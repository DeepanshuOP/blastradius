"""Pluggable LLM access for the agents (D-55: outside the reproducible pipeline).

Three providers:

* ``offline`` returns ``None`` for every request. Each agent has a deterministic
  fallback, so the whole workflow runs with no key and no network.
* ``anthropic`` calls the Anthropic Messages API over plain ``requests`` (already a
  project dependency, so no new package). Key: ``ANTHROPIC_API_KEY``. Model:
  ``BR_AGENT_MODEL``.

* ``bedrock`` calls Amazon Bedrock's Converse API over plain ``requests`` (D-60), paid from the
  operator's AWS credits with a hard project cap (``BR_BEDROCK_MAX_USD``). Key:
  ``AWS_BEARER_TOKEN_BEDROCK``; region ``BR_BEDROCK_REGION``; prices ``BR_PRICE_IN`` /
  ``BR_PRICE_OUT`` (USD per million tokens, required). E3 replication only.
* ``groq`` calls Groq's OpenAI-compatible endpoint over plain ``requests`` (no SDK), on
  the free tier (D-58). Key: ``GROQ_API_KEY``. Model: ``BR_AGENT_MODEL`` (default
  ``openai/gpt-oss-120b``). A client-side limiter keeps to ``BR_GROQ_RPM`` /
  ``BR_GROQ_TPM`` / ``BR_GROQ_TPD`` and every answer can be cached and replayed
  (``src/agents/llm_cache.py``).

Selection: ``BR_OFFLINE=1`` always forces ``offline``; else ``BR_AGENT_PROVIDER`` if set
(``groq`` | ``bedrock`` | ``anthropic`` | ``offline``); else ``anthropic`` when ``ANTHROPIC_API_KEY`` is
set; else ``groq`` when ``GROQ_API_KEY`` is set; else ``offline``.
"""

from __future__ import annotations

import json
import os
import re
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

from src.agents.llm_cache import LLMCache, cache_key

DEFAULT_MODEL = "claude-sonnet-5-5"
API_URL = "https://api.anthropic.com/v1/messages"
TIMEOUT = (10, 180)


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_DEFAULT_MODEL = "openai/gpt-oss-120b"
USAGE_LEDGER = Path("eval/llm_cache/usage.jsonl")


# Sampling parameters sent besides the pinned temperature / seed / completion budget, by model-name prefix.
# The gpt-oss family takes both (they were sent on every recorded request, so the cache keys depend on them).
# qwen/qwen3.8-27b takes only reasoning_effort="none" (Groq docs: none/default apply to Qwen 3.8 27B), so its
# thinking does not eat the completion budget (D-62). Other models get neither: an unsupported parameter is a
# Groq 400, and `chat` drops a parameter the 400 message names and retries (see `_unsupported_param`).
GROQ_REASONING_PARAMS: dict[str, dict] = {
    "openai/gpt-oss": {"reasoning_effort": "low", "include_reasoning": False},
    "qwen/qwen3.8-27b": {"reasoning_effort": "none"},
}


def groq_reasoning_params(model: str) -> dict:
    """Reasoning-control parameters sent for `model` (empty for models not known to accept them)."""
    for prefix, params in GROQ_REASONING_PARAMS.items():
        if model.startswith(prefix):
            return dict(params)
    return {}


_DROPPABLE = ("reasoning_effort", "include_reasoning")   # never temperature, seed or the completion budget


def _unsupported_param(body: str, params: dict) -> str | None:
    """The droppable parameter a Groq 400 message names, if it is one of `params` (read from the message)."""
    low = body.lower()
    for name in _DROPPABLE:
        if name in params and name in low:
            return name
    return None


def _param_variants(params: dict) -> list[dict]:
    """`params` first, then every copy with some droppable parameters removed (what a refused-and-retried
    request was recorded under), so a cache written after a 400 is found without asking the API again."""
    names = [n for n in _DROPPABLE if n in params]
    out = [params]
    for mask in range(1, 1 << len(names)):
        drop = {n for i, n in enumerate(names) if mask >> i & 1}
        out.append({k: v for k, v in params.items() if k not in drop})
    return out


class LLMError(RuntimeError):
    """The provider answered, but not with usable JSON."""


class RateLimited(LLMError):
    """The provider answered 429 (per-minute limit) and the retries are spent; a fallback provider may take over."""


class DailyQuotaReached(RuntimeError):
    """The free tier's daily token budget (client-side or reported by the provider) is spent."""

    def __init__(self, resume_after: str) -> None:
        super().__init__(f"DAILY QUOTA REACHED, resume after {resume_after}")
        self.resume_after = resume_after


@dataclass
class OfflineLLM:
    """Provider that never answers; agents fall back to deterministic logic."""

    name: str = "offline"

    def available(self) -> bool:
        """Offline never answers."""
        return False

    def complete_json(self, system: str, prompt: str, max_tokens: int = 4000) -> dict | None:
        """Always ``None``."""
        return None


@dataclass
class AnthropicLLM:
    """Anthropic Messages API provider."""

    api_key: str
    model: str = DEFAULT_MODEL
    name: str = "anthropic"

    def available(self) -> bool:
        """True when a key is configured."""
        return bool(self.api_key)

    def complete_json(self, system: str, prompt: str, max_tokens: int = 4000) -> dict | None:
        """Ask for a JSON object and parse the first one in the reply.

        Raises:
            LLMError: On an HTTP error or a reply with no parseable JSON object.
        """
        resp = requests.post(
            API_URL,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": max_tokens,
                "system": system + "\nReply with a single JSON object and nothing else.",
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=TIMEOUT,
        )
        if resp.status_code != 200:
            raise LLMError(f"Anthropic API returned {resp.status_code}: {resp.text[:300]}")
        text = "".join(b.get("text", "") for b in resp.json().get("content", []) if b.get("type") == "text")
        return extract_json(text)


class NetworkUnavailable(RuntimeError):
    """The provider could not be reached (DNS, connection or timeout) after the retries; nothing was recorded."""


NETWORK_ERRORS = (requests.exceptions.ConnectionError, requests.exceptions.Timeout)


def network_backoff(attempt: int) -> float:
    """Seconds to wait after the `attempt`-th (0-based) network failure: 5, 10, 20, 40, 80, then 120."""
    return float(min(5 * 2 ** attempt, 120))


class CostCapReached(RuntimeError):
    """The next Bedrock call's estimated cost would push the ledger past ``BR_BEDROCK_MAX_USD``."""


@dataclass
class ChatResult:
    """One chat completion (live or replayed)."""

    text: str
    usage: dict | None
    model: str
    from_cache: bool
    provider_id: str | None = None
    latency_s: float | None = None
    provider: str | None = None          # which provider answered ("groq" | "bedrock"); set by llm_provider


@dataclass
class GroqLLM:
    """Groq free-tier chat provider with a client-side rate limiter and an optional cache.

    Sampling is pinned: temperature 0, seed 0, reasoning_effort low, reasoning not
    returned. `n`, `logprobs` and `logit_bias` are never sent (Groq rejects them).
    """

    api_key: str
    model: str = GROQ_DEFAULT_MODEL
    name: str = "groq"
    cache: LLMCache | None = None
    rpm: int = field(default_factory=lambda: int(os.environ.get("BR_GROQ_RPM") or 30))
    tpm: int = field(default_factory=lambda: int(os.environ.get("BR_GROQ_TPM") or 8000))
    tpd: int = field(default_factory=lambda: int(os.environ.get("BR_GROQ_TPD") or 200000))
    ledger: Path = USAGE_LEDGER
    clock: object = time.time
    sleeper: object = time.sleep
    max_retries: int = 5

    def __post_init__(self) -> None:
        self._window: deque[tuple[float, int]] = deque()  # (time, tokens) of calls in the last minute
        self._dropped: set[str] = set()                   # parameters a 400 told us this model does not accept

    def available(self) -> bool:
        """True when a key is configured."""
        return bool(self.api_key)

    # -- limiter ----------------------------------------------------------------------------
    @staticmethod
    def estimate_tokens(system: str, user: str, max_completion_tokens: int) -> int:
        """Request estimate: characters / 3.5 plus the completion budget."""
        return int((len(system) + len(user)) / 3.5) + max_completion_tokens

    def _day_total(self) -> tuple[int, float | None]:
        """Tokens of this model in the rolling 24 h, and the time the oldest of them expires."""
        if not self.ledger.exists():
            return 0, None
        cut = self.clock() - 86400
        total, oldest = 0, None
        for line in self.ledger.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            t = datetime.fromisoformat(r["timestamp"]).timestamp()
            if r.get("model") == self.model and t >= cut:
                total += int(r["tokens"])
                oldest = t if oldest is None else min(oldest, t)
        return total, oldest

    def _wait_for_minute(self, need: int) -> None:
        while True:
            now = self.clock()
            while self._window and self._window[0][0] <= now - 60:
                self._window.popleft()
            used = sum(t for _, t in self._window)
            if len(self._window) < self.rpm and used + need <= self.tpm:
                return
            wake = self._window[0][0] + 60 - now if self._window else 1.0
            self.sleeper(max(wake, 0.5))

    def _record_usage(self, tokens: int) -> None:
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"timestamp": datetime.fromtimestamp(self.clock(), timezone.utc)
                                 .isoformat(timespec="seconds"), "model": self.model, "tokens": tokens}) + "\n")

    # -- calls ------------------------------------------------------------------------------
    def request_params(self, max_completion_tokens: int = 1500) -> dict:
        """The sampling parameters of a request: pinned base plus the model's reasoning controls."""
        extra = {k: v for k, v in groq_reasoning_params(self.model).items() if k not in self._dropped}
        return {"temperature": 0, "seed": 0, **extra, "max_completion_tokens": max_completion_tokens}

    def request_key(self, system: str, user: str, max_completion_tokens: int = 1500) -> str:
        """The cache key `chat` would use for this request (no I/O)."""
        return cache_key(self.name, self.model, system, [{"role": "user", "content": user}],
                         self.request_params(max_completion_tokens))

    def chat(self, system: str, user: str, max_completion_tokens: int = 1500) -> ChatResult:
        """One chat completion, from the cache when recorded.

        The cache is consulted first and a hit returns before any quota arithmetic, so a replayed request never
        consumes (or is blocked by) the day's token budget.

        Args:
            system: System prompt.
            user: User message.
            max_completion_tokens: Completion budget.

        Returns:
            The result. `from_cache` is True when no network call was made.

        Raises:
            CacheMiss: In replay mode, for an unrecorded request.
            DailyQuotaReached: When the day's token budget cannot cover the next call.
            LLMError: On a non-retryable HTTP error or after the retries are spent.
            NetworkUnavailable: When the provider cannot be reached after the retries (no record is written).
        """
        params = self.request_params(max_completion_tokens)
        messages = [{"role": "user", "content": user}]
        key = cache_key(self.name, self.model, system, messages, params)
        if self.cache is not None:
            for alt in _param_variants(params):
                alt_key = key if alt is params else cache_key(self.name, self.model, system, messages, alt)
                if alt_key in self.cache:
                    rec = self.cache.get(alt_key)
                    return ChatResult(rec["response_text"], rec.get("usage"), rec["model"], True,
                                      rec.get("provider_id"), rec.get("latency_s"))
            self.cache.get(key)   # replay mode: a miss raises CacheMiss here, before any quota check
        need = self.estimate_tokens(system, user, max_completion_tokens)
        used, oldest = self._day_total()
        if used + need > self.tpd:
            resume = datetime.fromtimestamp((oldest or self.clock()) + 86400, timezone.utc)
            raise DailyQuotaReached(resume.isoformat(timespec="minutes"))
        body = {"model": self.model, "messages": [{"role": "system", "content": system}, *messages], **params}
        for attempt in range(self.max_retries + 1):
            self._wait_for_minute(need)
            t0 = self.clock()
            try:
                resp = requests.post(GROQ_URL, headers={"Authorization": f"Bearer {self.api_key}"}, json=body,
                                     timeout=TIMEOUT)
            except NETWORK_ERRORS as exc:
                if attempt == self.max_retries:
                    raise NetworkUnavailable(f"Groq unreachable after {self.max_retries} retries: "
                                             f"{type(exc).__name__}") from exc
                self.sleeper(network_backoff(attempt))
                continue
            if resp.status_code == 429:
                msg = resp.text.lower()
                if "per day" in msg or "tpd" in msg or "requests per day" in msg:
                    raise DailyQuotaReached((datetime.fromtimestamp(self.clock(), timezone.utc)
                                             + timedelta(hours=24)).isoformat(timespec="minutes"))
                if attempt == self.max_retries:
                    raise RateLimited(f"Groq rate limit persisted after {self.max_retries} retries")
                self.sleeper(float(resp.headers.get("retry-after", 20)))
                continue
            if resp.status_code == 400 and "tool_use_failed" in resp.text:
                # the model tried to call a tool we never offered: an unusable reply, recorded as an empty one so
                # the attempt counts as failed (and replays identically) instead of aborting a whole run
                self._window.append((self.clock(), need))
                self._record_usage(need)
                if self.cache is not None:
                    self.cache.put(key, {"model": self.model, "system": system, "messages": messages,
                                         "params": params}, "", None, self.model, None,
                                   round(self.clock() - t0, 3))
                return ChatResult("", None, self.model, False, None, round(self.clock() - t0, 3))
            if resp.status_code == 400 and (bad := _unsupported_param(resp.text, params)) and attempt < self.max_retries:
                # the 400 names a parameter this model does not accept: drop exactly that one and ask again; the
                # request that is cached (and keyed) is the one that was actually accepted
                params = {k: v for k, v in params.items() if k != bad}
                self._dropped.add(bad)
                body = {"model": self.model, "messages": [{"role": "system", "content": system}, *messages], **params}
                key = cache_key(self.name, self.model, system, messages, params)
                continue
            if resp.status_code != 200:
                low = resp.text.lower()
                if "billing" in low or "payment" in low:
                    raise LLMError("Groq reports a billing/paid-tier condition: stopping (no step may spend money)")
                raise LLMError(f"Groq API returned {resp.status_code}: {resp.text[:300]}")
            data = resp.json()
            text = data["choices"][0]["message"].get("content") or ""
            usage = data.get("usage") or {}
            self._window.append((self.clock(), int(usage.get("total_tokens", need))))
            self._record_usage(int(usage.get("total_tokens", need)))
            pid = (data.get("x_groq") or {}).get("id")
            if self.cache is not None:
                self.cache.put(key, {"model": self.model, "system": system, "messages": messages, "params": params},
                               text, usage, data.get("model", self.model), pid, round(self.clock() - t0, 3))
            return ChatResult(text, usage, data.get("model", self.model), False, pid, round(self.clock() - t0, 3))
        raise LLMError("unreachable")

    def complete_json(self, system: str, prompt: str, max_tokens: int = 4000) -> dict | None:
        """JSON-object completion for the agents that expect one."""
        res = self.chat(system + "\nReply with a single JSON object and nothing else.", prompt, max_tokens)
        return extract_json(res.text)


def bedrock_spend(ledger: Path = USAGE_LEDGER) -> float:
    """Total USD recorded for Bedrock calls in the usage ledger (the project-wide figure)."""
    total = 0.0
    if Path(ledger).exists():
        for line in Path(ledger).read_text(encoding="utf-8").splitlines():
            if line.strip():
                total += float(json.loads(line).get("usd") or 0.0)
    return total


@dataclass
class BedrockLLM:
    """Amazon Bedrock Converse provider with a cost ledger and a hard USD cap.

    ``POST https://bedrock-runtime.{region}.amazonaws.com/model/{model_id}/converse`` with a bearer key and
    ``inferenceConfig {maxTokens, temperature: 0}``. Converse has no seed, so runs are not bit-reproducible:
    the cache is the record, and replay mode never calls the network.
    """

    api_key: str
    model: str
    region: str = "ap-south-1"
    price_in: float | None = None     # USD per million input tokens
    price_out: float | None = None    # USD per million output tokens
    max_usd: float = 10.0
    name: str = "bedrock"
    cache: LLMCache | None = None
    ledger: Path = USAGE_LEDGER
    clock: object = time.time
    sleeper: object = time.sleep
    max_retries: int = 5

    def available(self) -> bool:
        """True when a key is configured."""
        return bool(self.api_key)

    @staticmethod
    def usd(input_tokens: int, output_tokens: int, price_in: float, price_out: float) -> float:
        """`input * price_in / 1e6 + output * price_out / 1e6`."""
        return input_tokens * price_in / 1e6 + output_tokens * price_out / 1e6

    def estimate_usd(self, system: str, user: str, max_tokens: int) -> float:
        """Upper-bound estimate of one call: input at 3.5 chars/token, output at the full completion budget."""
        if self.price_in is None or self.price_out is None:
            raise LLMError("BR_PRICE_IN and BR_PRICE_OUT must be set (USD per million tokens); refusing to run")
        return self.usd(int((len(system) + len(user)) / 3.5), max_tokens, self.price_in, self.price_out)

    def check_budget(self, planned_usd: float) -> None:
        """Raise :class:`CostCapReached` if `planned_usd` on top of the ledger would pass the cap."""
        spent = bedrock_spend(self.ledger)
        if spent + planned_usd > self.max_usd:
            raise CostCapReached(f"estimated USD {planned_usd:.4f} + ledger USD {spent:.4f} exceeds "
                                 f"BR_BEDROCK_MAX_USD {self.max_usd:.2f}")

    def request_key(self, system: str, user: str, max_completion_tokens: int = 1500) -> str:
        """The cache key `chat` would use for this request (no I/O)."""
        return cache_key(self.name, self.model, system, [{"role": "user", "content": user}],
                         {"temperature": 0, "maxTokens": max_completion_tokens})

    def url(self) -> str:
        from urllib.parse import quote

        return f"https://bedrock-runtime.{self.region}.amazonaws.com/model/{quote(self.model, safe='')}/converse"

    def body(self, system: str, user: str, max_tokens: int) -> dict:
        return {"messages": [{"role": "user", "content": [{"text": user}]}], "system": [{"text": system}],
                "inferenceConfig": {"maxTokens": max_tokens, "temperature": 0}}

    def _record(self, in_t: int, out_t: int, usd: float | None) -> None:
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"timestamp": datetime.fromtimestamp(self.clock(), timezone.utc)
                                 .isoformat(timespec="seconds"), "model": self.model, "provider": "bedrock",
                                 "tokens": in_t + out_t, "input_tokens": in_t, "output_tokens": out_t,
                                 "usd": usd}) + "\n")

    def chat(self, system: str, user: str, max_completion_tokens: int = 1500, probe: bool = False) -> ChatResult:
        """One Converse call, from the cache when recorded.

        Args:
            system: System prompt.
            user: User message.
            max_completion_tokens: Completion budget (`maxTokens`).
            probe: Allow a call with unset prices (model probe only; the cost is recorded as unknown).

        Raises:
            CacheMiss: In replay mode, for an unrecorded request.
            CostCapReached: If the estimated cost would exceed the project cap.
            LLMError: Unset prices, a non-retryable error, or retries exhausted.
        """
        params = {"temperature": 0, "maxTokens": max_completion_tokens}
        messages = [{"role": "user", "content": user}]
        key = cache_key(self.name, self.model, system, messages, params)
        if self.cache is not None:
            rec = self.cache.get(key)
            if rec is not None:
                return ChatResult(rec["response_text"], rec.get("usage"), rec["model"], True, rec.get("provider_id"),
                                  rec.get("latency_s"))
        if not probe:
            self.check_budget(self.estimate_usd(system, user, max_completion_tokens))
        delay = 10.0
        for attempt in range(self.max_retries + 1):
            t0 = self.clock()
            try:
                resp = requests.post(self.url(), headers={"Authorization": f"Bearer {self.api_key}",
                                                          "Content-Type": "application/json"},
                                     json=self.body(system, user, max_completion_tokens), timeout=TIMEOUT)
            except NETWORK_ERRORS as exc:
                if attempt == self.max_retries:
                    raise NetworkUnavailable(f"Bedrock unreachable after {self.max_retries} retries: "
                                             f"{type(exc).__name__}") from exc
                self.sleeper(network_backoff(attempt))
                continue
            low = resp.text.lower()
            if resp.status_code == 429 or "throttlingexception" in low:
                if attempt == self.max_retries:
                    raise LLMError(f"Bedrock throttling persisted after {self.max_retries} retries")
                self.sleeper(float(resp.headers.get("retry-after", delay)))
                delay *= 2
                continue
            if resp.status_code != 200:
                raise LLMError(f"Bedrock {resp.status_code}: {resp.text[:300]}")
            data = resp.json()
            blocks = ((data.get("output") or {}).get("message") or {}).get("content") or []
            text = "".join(b.get("text", "") for b in blocks if "text" in b)
            usage = data.get("usage") or {}
            in_t, out_t = int(usage.get("inputTokens", 0)), int(usage.get("outputTokens", 0))
            usd = (self.usd(in_t, out_t, self.price_in, self.price_out)
                   if self.price_in is not None and self.price_out is not None else None)
            self._record(in_t, out_t, usd)
            lat = round(self.clock() - t0, 3)
            if self.cache is not None:
                self.cache.put(key, {"model": self.model, "system": system, "messages": messages, "params": params},
                               text, {**usage, "usd": usd}, self.model, resp.headers.get("x-amzn-requestid"), lat)
            return ChatResult(text, {**usage, "usd": usd, "total_tokens": in_t + out_t}, self.model, False,
                              resp.headers.get("x-amzn-requestid"), lat)
        raise LLMError("unreachable")

    def complete_json(self, system: str, prompt: str, max_tokens: int = 4000) -> dict | None:
        """JSON-object completion for the agents that expect one."""
        res = self.chat(system + "\nReply with a single JSON object and nothing else.", prompt, max_tokens)
        return extract_json(res.text)


def extract_json(text: str) -> dict:
    """Parse the first JSON object in ``text`` (tolerates ```json fences).

    Raises:
        LLMError: When no JSON object can be parsed.
    """
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    candidate = fenced.group(1) if fenced else text[text.find("{"): text.rfind("}") + 1]
    try:
        value = json.loads(candidate)
    except (json.JSONDecodeError, ValueError) as exc:
        raise LLMError(f"no JSON object in model reply: {text[:200]!r}") from exc
    if not isinstance(value, dict):
        raise LLMError("model reply JSON is not an object")
    return value


def get_llm(provider: str | None = None) -> OfflineLLM | AnthropicLLM | GroqLLM | BedrockLLM:
    """Return the configured provider (see module docstring)."""
    if os.environ.get("BR_OFFLINE") == "1":
        return OfflineLLM()
    choice = (provider or os.environ.get("BR_AGENT_PROVIDER") or "").strip().lower()
    a_key = os.environ.get("ANTHROPIC_API_KEY", "")
    g_key = os.environ.get("GROQ_API_KEY", "")
    if not choice:
        choice = "anthropic" if a_key else "groq" if g_key else "offline"
    if choice == "offline":
        return OfflineLLM()
    if choice == "anthropic":
        if not a_key:
            raise LLMError("BR_AGENT_PROVIDER=anthropic but ANTHROPIC_API_KEY is not set")
        return AnthropicLLM(api_key=a_key, model=os.environ.get("BR_AGENT_MODEL") or DEFAULT_MODEL)
    if choice == "groq":
        if not g_key:
            raise LLMError("BR_AGENT_PROVIDER=groq but GROQ_API_KEY is not set")
        return GroqLLM(api_key=g_key, model=os.environ.get("BR_AGENT_MODEL") or GROQ_DEFAULT_MODEL)
    if choice == "bedrock":
        key = os.environ.get("AWS_BEARER_TOKEN_BEDROCK", "")
        model = os.environ.get("BR_BEDROCK_MODEL", "")
        if not key or not model:
            raise LLMError("BR_AGENT_PROVIDER=bedrock needs AWS_BEARER_TOKEN_BEDROCK and BR_BEDROCK_MODEL")
        pi, po = os.environ.get("BR_PRICE_IN"), os.environ.get("BR_PRICE_OUT")
        return BedrockLLM(api_key=key, model=model, region=os.environ.get("BR_BEDROCK_REGION") or "ap-south-1",
                          price_in=float(pi) if pi else None, price_out=float(po) if po else None,
                          max_usd=float(os.environ.get("BR_BEDROCK_MAX_USD") or 10))
    raise LLMError(f"unknown provider {choice!r} (use 'offline', 'anthropic', 'groq' or 'bedrock')")


# ---- Bedrock model probe ---------------------------------------------------------------------
_UNUSABLE = ("invalid_payment_instrument", "aws marketplace", "subscription", "accessdenied", "access denied",
             "not authorized", "marketplace")
_FAMILIES = [("claude-sonnet", "newest Anthropic Claude Sonnet"), ("qwen3-coder", "newest Qwen3 Coder"),
             ("deepseek", "newest DeepSeek"), ("nova-pro", "newest Amazon Nova Pro")]


def _version_key(model_id: str) -> tuple:
    return tuple(int(x) for x in re.findall(r"\d+", model_id))


def list_bedrock_ids(key: str, region: str) -> tuple[list[str], list[str], str]:
    """Foundation-model ids and inference-profile ids visible to the key (control-plane GETs).

    Returns:
        `(model_ids, profile_ids, note)`; empty lists and a note if listing is not permitted.
    """
    hdr = {"Authorization": f"Bearer {key}"}
    base = f"https://bedrock.{region}.amazonaws.com"
    models: list[str] = []
    profiles: list[str] = []
    notes = []
    r = requests.get(f"{base}/foundation-models", headers=hdr, timeout=TIMEOUT)
    if r.status_code == 200:
        models = [m["modelId"] for m in r.json().get("modelSummaries", [])]
    else:
        notes.append(f"foundation-models {r.status_code}: {r.text[:120]}")
    token = None
    while True:
        r = requests.get(f"{base}/inference-profiles", headers=hdr, timeout=TIMEOUT,
                         params={"maxResults": 1000, **({"nextToken": token} if token else {})})
        if r.status_code != 200:
            notes.append(f"inference-profiles {r.status_code}: {r.text[:120]}")
            break
        d = r.json()
        profiles += [p["inferenceProfileId"] for p in d.get("inferenceProfileSummaries", [])]
        token = d.get("nextToken")
        if not token:
            break
    return models, profiles, "; ".join(notes)


def probe_bedrock(out: Path = Path("eval/llm_cache/bedrock_probe.json")) -> dict:
    """One 16-token call per candidate model; record which are usable on this account. No other Bedrock call."""
    key = os.environ.get("AWS_BEARER_TOKEN_BEDROCK", "")
    region = os.environ.get("BR_BEDROCK_REGION") or "ap-south-1"
    if not key:
        raise SystemExit("AWS_BEARER_TOKEN_BEDROCK is not set")
    explicit = [c.strip() for c in os.environ.get("BR_BEDROCK_CANDIDATES", "").split(",") if c.strip()]
    models, profiles, note = ([], [], "BR_BEDROCK_CANDIDATES given; listing skipped") if explicit else list_bedrock_ids(key, region)
    cands: list[tuple[str, str]] = [(c, "from BR_BEDROCK_CANDIDATES") for c in explicit]
    if not explicit:
        pool = profiles + models
        for frag, label in _FAMILIES:
            hits = [m for m in pool if frag in m.lower()]
            # prefer a cross-region profile (apac. / global.) over a bare model id of the same model
            hits.sort(key=lambda m: (_version_key(m), m.startswith(("apac.", "global.")), m), reverse=True)
            if hits:
                cands.append((hits[0], label))
    results = []
    for mid, label in cands:
        llm = BedrockLLM(api_key=key, model=mid, region=region, max_retries=1)
        rec: dict = {"candidate": label, "model_id": mid}
        try:
            r = llm.chat("Reply with one word.", "Reply with the word ok", 16, probe=True)
            rec.update(status=200, usable=True, reply=r.text.strip()[:40], usage=r.usage)
        except Exception as exc:  # recorded, never raised: the next candidate is tried
            msg = str(exc)
            rec.update(status=int(re.search(r"Bedrock (\d{3})", msg).group(1)) if re.search(r"Bedrock (\d{3})", msg) else None,
                       usable=False, error=msg[:300],
                       marketplace_or_access=any(t in msg.lower() for t in _UNUSABLE))
        results.append(rec)
        print(json.dumps(rec, ensure_ascii=False))
    doc = {"region": region, "listing_note": note, "n_models_listed": len(models), "n_profiles_listed": len(profiles),
           "candidates": results}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


if __name__ == "__main__":
    import sys

    if "--probe-bedrock" in sys.argv:
        probe_bedrock()
    else:
        print(__doc__)
