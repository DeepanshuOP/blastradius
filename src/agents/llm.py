"""Pluggable LLM access for the agents (D-55: outside the reproducible pipeline).

Three providers:

* ``offline`` returns ``None`` for every request. Each agent has a deterministic
  fallback, so the whole workflow runs with no key and no network.
* ``anthropic`` calls the Anthropic Messages API over plain ``requests`` (already a
  project dependency, so no new package). Key: ``ANTHROPIC_API_KEY``. Model:
  ``BR_AGENT_MODEL``.

* ``groq`` calls Groq's OpenAI-compatible endpoint over plain ``requests`` (no SDK), on
  the free tier (D-58). Key: ``GROQ_API_KEY``. Model: ``BR_AGENT_MODEL`` (default
  ``openai/gpt-oss-120b``). A client-side limiter keeps to ``BR_GROQ_RPM`` /
  ``BR_GROQ_TPM`` / ``BR_GROQ_TPD`` and every answer can be cached and replayed
  (``src/agents/llm_cache.py``).

Selection: ``BR_OFFLINE=1`` always forces ``offline``; else ``BR_AGENT_PROVIDER`` if set
(``groq`` | ``anthropic`` | ``offline``); else ``anthropic`` when ``ANTHROPIC_API_KEY`` is
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


class LLMError(RuntimeError):
    """The provider answered, but not with usable JSON."""


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


@dataclass
class ChatResult:
    """One chat completion (live or replayed)."""

    text: str
    usage: dict | None
    model: str
    from_cache: bool
    provider_id: str | None = None
    latency_s: float | None = None


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
    def chat(self, system: str, user: str, max_completion_tokens: int = 1500) -> ChatResult:
        """One chat completion, from the cache when recorded.

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
        """
        params = {"temperature": 0, "seed": 0, "reasoning_effort": "low", "include_reasoning": False,
                  "max_completion_tokens": max_completion_tokens}
        messages = [{"role": "user", "content": user}]
        key = cache_key(self.name, self.model, system, messages, params)
        if self.cache is not None:
            rec = self.cache.get(key)
            if rec is not None:
                return ChatResult(rec["response_text"], rec.get("usage"), rec["model"], True, rec.get("provider_id"),
                                  rec.get("latency_s"))
        need = self.estimate_tokens(system, user, max_completion_tokens)
        used, oldest = self._day_total()
        if used + need > self.tpd:
            resume = datetime.fromtimestamp((oldest or self.clock()) + 86400, timezone.utc)
            raise DailyQuotaReached(resume.isoformat(timespec="minutes"))
        body = {"model": self.model, "messages": [{"role": "system", "content": system}, *messages], **params}
        for attempt in range(self.max_retries + 1):
            self._wait_for_minute(need)
            t0 = self.clock()
            resp = requests.post(GROQ_URL, headers={"Authorization": f"Bearer {self.api_key}"}, json=body,
                                 timeout=TIMEOUT)
            if resp.status_code == 429:
                msg = resp.text.lower()
                if "per day" in msg or "tpd" in msg or "requests per day" in msg:
                    raise DailyQuotaReached((datetime.fromtimestamp(self.clock(), timezone.utc)
                                             + timedelta(hours=24)).isoformat(timespec="minutes"))
                if attempt == self.max_retries:
                    raise LLMError(f"Groq rate limit persisted after {self.max_retries} retries")
                self.sleeper(float(resp.headers.get("retry-after", 20)))
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


def get_llm(provider: str | None = None) -> OfflineLLM | AnthropicLLM | GroqLLM:
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
    raise LLMError(f"unknown provider {choice!r} (use 'offline', 'anthropic' or 'groq')")
