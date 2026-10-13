"""One model interface for repair and the Live Lab: Groq first, Amazon Bedrock as the fallback (D-69).

Bedrock is reached through its OpenAI-compatible chat-completions endpoint over plain ``requests``, the same request
shape as Groq (only the base URL, the bearer key and the model id differ; no boto3):

    POST https://bedrock-runtime.{region}.amazonaws.com/openai/v1/chat/completions
    Authorization: Bearer $AWS_BEARER_TOKEN_BEDROCK          model: openai.gpt-oss-120b-1:0

When Bedrock answers:

* only when Groq raises :class:`~src.agents.llm.RateLimited` (429) or
  :class:`~src.agents.llm.DailyQuotaReached`, or when ``BR_LLM_PROVIDER=bedrock`` forces it;
* never once the ledger ``logs/agent/bedrock_ledger.jsonl`` plus the next call's estimate passes the budget
  ``BR_BEDROCK_MAX_USD`` (alias ``BR_BEDROCK_BUDGET_USD``; default 5, clamped to the hard maximum 50);
* its reply may open with ``<reasoning>...</reasoning>``; that is stripped before patch parsing and kept only on
  :attr:`BedrockChatLLM.last_reasoning` (the decision log writes it to the gitignored per-run folder).

Cost is computed from the reply's ``usage`` block at the list price (``BEDROCK_PRICES``; override with
``BR_BEDROCK_PRICE_IN`` / ``BR_BEDROCK_PRICE_OUT``, USD per million tokens).

Each provider keeps its own cache file and the cache key carries provider and model, so a Groq recording is never
answered by Bedrock and the published E3 caches are untouched.
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import requests

from src.agents.llm import (NETWORK_ERRORS, TIMEOUT, ChatResult, DailyQuotaReached, LLMError, NetworkUnavailable,
                            RateLimited, extract_json, network_backoff)
from src.agents.llm_cache import CacheMiss, LLMCache, cache_key, model_slug

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "logs" / "agent" / "bedrock_ledger.jsonl"
DEFAULT_BUDGET_USD = 5.0
HARD_MAX_USD = 50.0
DEFAULT_REGION = "us-west-2"
#: Project model name -> Bedrock model id. The id was confirmed by the foundation-models listing in us-west-2.
BEDROCK_MODEL_IDS = {"openai/gpt-oss-120b": "openai.gpt-oss-120b-1:0"}
#: USD per million (input, output) tokens: Bedrock on-demand list price for gpt-oss-120b, standard regions.
BEDROCK_PRICES = {"openai.gpt-oss-120b-1:0": (0.15, 0.60)}
#: Extra completion tokens on Bedrock so a reasoning preamble cannot truncate the patch that follows it.
REASONING_HEADROOM = 4096
_REASONING = re.compile(r"<reasoning>.*?</reasoning>\s*", re.S)


def strip_reasoning(text: str) -> tuple[str, str]:
    """Split a reply into (answer, reasoning). An unterminated ``<reasoning>`` swallows the rest (no answer)."""
    found = _REASONING.findall(text)
    answer = _REASONING.sub("", text)
    if "<reasoning>" in answer:                       # opened and never closed: the budget ran out mid-reasoning
        i = answer.index("<reasoning>")
        found.append(answer[i:])
        answer = answer[:i]
    return answer.strip(), "".join(found).strip()


def budget_usd() -> float:
    """The Bedrock budget in USD: ``BR_BEDROCK_MAX_USD`` (or ``BR_BEDROCK_BUDGET_USD``), default 5, at most 50."""
    raw = os.environ.get("BR_BEDROCK_MAX_USD") or os.environ.get("BR_BEDROCK_BUDGET_USD") or ""
    try:
        val = float(raw) if raw.strip() else DEFAULT_BUDGET_USD
    except ValueError:
        val = DEFAULT_BUDGET_USD
    return max(0.0, min(val, HARD_MAX_USD))


def ledger_spend(ledger: Path = LEDGER) -> float:
    """Total USD recorded in the Bedrock ledger."""
    total = 0.0
    if Path(ledger).exists():
        for line in Path(ledger).read_text(encoding="utf-8").splitlines():
            if line.strip():
                total += float(json.loads(line).get("cost_usd") or 0.0)
    return total


class BudgetExhausted(LLMError):
    """The Bedrock ledger (plus the next call's estimate) has reached the budget; no request was sent."""


@dataclass
class BedrockChatLLM:
    """Bedrock's OpenAI-compatible chat completions with a USD ledger and a hard budget."""

    api_key: str
    model: str = BEDROCK_MODEL_IDS["openai/gpt-oss-120b"]
    region: str = DEFAULT_REGION
    cache: LLMCache | None = None
    ledger: Path = LEDGER
    max_usd: float = field(default_factory=budget_usd)
    price_in: float | None = None
    price_out: float | None = None
    name: str = "bedrock"
    clock: object = time.time
    sleeper: object = time.sleep
    max_retries: int = 2

    def __post_init__(self) -> None:
        self.max_usd = max(0.0, min(float(self.max_usd), HARD_MAX_USD))
        lp_in, lp_out = BEDROCK_PRICES.get(self.model, (None, None))
        env_in, env_out = os.environ.get("BR_BEDROCK_PRICE_IN"), os.environ.get("BR_BEDROCK_PRICE_OUT")
        self.price_in = self.price_in if self.price_in is not None else float(env_in) if env_in else lp_in
        self.price_out = self.price_out if self.price_out is not None else float(env_out) if env_out else lp_out
        self.last_reasoning: str = ""

    def available(self) -> bool:
        """True when a key is configured."""
        return bool(self.api_key)

    def url(self) -> str:
        """The chat-completions endpoint of the region."""
        return f"https://bedrock-runtime.{self.region}.amazonaws.com/openai/v1/chat/completions"

    def request_params(self, max_completion_tokens: int = 1500) -> dict:
        """Pinned sampling parameters; the completion budget includes the reasoning headroom."""
        return {"temperature": 0, "max_tokens": max_completion_tokens + REASONING_HEADROOM}

    def request_key(self, system: str, user: str, max_completion_tokens: int = 1500) -> str:
        """The cache key `chat` would use (provider and model are part of it)."""
        return cache_key(self.name, self.model, system, [{"role": "user", "content": user}],
                         self.request_params(max_completion_tokens))

    def cost(self, tokens_in: int, tokens_out: int) -> float:
        """USD at the list price.

        Raises:
            LLMError: When no price is known for the model.
        """
        if self.price_in is None or self.price_out is None:
            raise LLMError(f"no list price for {self.model}; set BR_BEDROCK_PRICE_IN and BR_BEDROCK_PRICE_OUT")
        return tokens_in * self.price_in / 1e6 + tokens_out * self.price_out / 1e6

    def spent(self) -> float:
        """USD recorded in the ledger so far."""
        return ledger_spend(self.ledger)

    def check_budget(self, system: str, user: str, max_completion_tokens: int) -> float:
        """The estimate of the next call; raises when it (or the spend so far) reaches the budget.

        Raises:
            BudgetExhausted: Ledger + estimate >= budget.
        """
        est = self.cost(int((len(system) + len(user)) / 3.5), max_completion_tokens + REASONING_HEADROOM)
        spent = self.spent()
        if spent >= self.max_usd or spent + est > self.max_usd:
            raise BudgetExhausted(f"Bedrock budget reached: ledger USD {spent:.4f} + next-call estimate USD {est:.4f} "
                                  f"> budget USD {self.max_usd:.2f}; no request sent")
        return est

    def _record(self, tokens_in: int, tokens_out: int, usd: float, request_id: str | None) -> None:
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": datetime.fromtimestamp(self.clock(), timezone.utc).isoformat(timespec="seconds"),
                                 "provider": "bedrock", "model": self.model, "region": self.region,
                                 "tokens_in": tokens_in, "tokens_out": tokens_out, "cost_usd": round(usd, 8),
                                 "price_in": self.price_in, "price_out": self.price_out,
                                 "request_id": request_id}) + "\n")

    def chat(self, system: str, user: str, max_completion_tokens: int = 1500) -> ChatResult:
        """One completion, from the cache when recorded. The returned text has the reasoning stripped.

        Raises:
            CacheMiss: Replay mode and not recorded.
            BudgetExhausted: The budget would be passed.
            NetworkUnavailable: Bedrock unreachable after the retries.
            LLMError: Any other non-200 answer.
        """
        params = self.request_params(max_completion_tokens)
        messages = [{"role": "user", "content": user}]
        key = cache_key(self.name, self.model, system, messages, params)
        self.last_reasoning = ""
        if self.cache is not None:
            rec = self.cache.get(key)
            if rec is not None:
                return ChatResult(rec["response_text"], rec.get("usage"), rec["model"], True, rec.get("provider_id"),
                                  rec.get("latency_s"), provider=self.name)
        self.check_budget(system, user, max_completion_tokens)
        body = {"model": self.model, "messages": [{"role": "system", "content": system}, *messages], **params}
        hdr = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        delay = 5.0
        for attempt in range(self.max_retries + 1):
            t0 = self.clock()
            try:
                resp = requests.post(self.url(), headers=hdr, json=body, timeout=TIMEOUT)
            except NETWORK_ERRORS as exc:
                if attempt == self.max_retries:
                    raise NetworkUnavailable(f"Bedrock unreachable after {self.max_retries} retries: "
                                             f"{type(exc).__name__}") from exc
                self.sleeper(network_backoff(attempt))
                continue
            if resp.status_code == 429:
                if attempt == self.max_retries:
                    raise RateLimited(f"Bedrock throttling persisted after {self.max_retries} retries")
                self.sleeper(float(resp.headers.get("retry-after", delay)))
                delay *= 2
                continue
            if resp.status_code != 200:
                raise LLMError(f"Bedrock {resp.status_code}: {resp.text[:300]}")
            return self._finish(resp, key, system, messages, params, t0)
        raise LLMError("unreachable")

    def _finish(self, resp, key: str, system: str, messages: list[dict], params: dict, t0: float) -> ChatResult:
        data = resp.json()
        raw = (data["choices"][0]["message"].get("content") or "")
        text, reasoning = strip_reasoning(raw)
        self.last_reasoning = reasoning
        u = data.get("usage") or {}
        tin, tout = int(u.get("prompt_tokens", 0)), int(u.get("completion_tokens", 0))
        usd = self.cost(tin, tout)
        rid = resp.headers.get("x-amzn-requestid") or data.get("id")
        self._record(tin, tout, usd, rid)
        usage = {"prompt_tokens": tin, "completion_tokens": tout, "total_tokens": int(u.get("total_tokens", tin + tout)),
                 "cost_usd": round(usd, 8)}
        lat = round(self.clock() - t0, 3)
        if self.cache is not None:                  # the cache keeps the answer only, never the reasoning
            self.cache.put(key, {"model": self.model, "system": system, "messages": messages, "params": params},
                           text, usage, data.get("model", self.model), rid, lat)
        return ChatResult(text, usage, data.get("model", self.model), False, rid, lat, provider=self.name)

    def complete_json(self, system: str, prompt: str, max_tokens: int = 4000) -> dict | None:
        """JSON-object completion for the agents that expect one."""
        return extract_json(self.chat(system + "\nReply with a single JSON object and nothing else.", prompt,
                                      max_tokens).text)


class FallbackLLM:
    """`chat()` on the primary (Groq); on a 429 / daily quota, or when forced, on Bedrock.

    Attributes:
        last_provider: Provider of the last answer ("groq" | "bedrock").
        fallback_reason: Why the last call went to Bedrock (None when it did not).
    """

    def __init__(self, primary, secondary=None, force_secondary: bool = False) -> None:
        if primary is None and secondary is None:
            raise ValueError("FallbackLLM needs at least one provider")
        self.primary, self.secondary, self.force = primary, secondary, force_secondary
        self.last_provider: str | None = None
        self.fallback_reason: str | None = None

    @property
    def active(self):
        """The provider the next call starts with."""
        return self.secondary if (self.force or self.primary is None) else self.primary

    @property
    def model(self) -> str:
        """The project model name (the primary's), so prompts and caches stay keyed as before."""
        return getattr(self.primary or self.secondary, "model", "model")

    @property
    def provider(self) -> str:
        """Provider of the last answer, else the one the next call starts with."""
        return self.last_provider or getattr(self.active, "name", "groq")

    @property
    def cache(self):
        return getattr(self.active, "cache", None)

    @property
    def last_reasoning(self) -> str:
        return getattr(self.secondary, "last_reasoning", "") if self.last_provider == "bedrock" else ""

    def request_key(self, system: str, user: str, max_completion_tokens: int = 1500) -> str:
        return self.active.request_key(system, user, max_completion_tokens)

    def request_params(self, max_completion_tokens: int = 1500) -> dict:
        return self.active.request_params(max_completion_tokens)

    def model_id(self, provider: str | None = None) -> str:
        """Provider-native model id of `provider` (default: the last answer's)."""
        p = provider or self.provider
        llm = self.secondary if p == "bedrock" else self.primary
        return getattr(llm, "model", self.model)

    def _secondary(self, system: str, user: str, n: int) -> ChatResult:
        res = self.secondary.chat(system, user, n)
        res.provider, self.last_provider = "bedrock", "bedrock"
        return res

    def chat(self, system: str, user: str, max_completion_tokens: int = 1500) -> ChatResult:
        """One completion. Errors other than a rate limit or quota propagate unchanged."""
        self.fallback_reason = None
        if self.active is self.secondary:
            self.fallback_reason = "BR_LLM_PROVIDER=bedrock" if self.force else "no primary provider configured"
            return self._secondary(system, user, max_completion_tokens)
        try:
            res = self.primary.chat(system, user, max_completion_tokens)
        except (RateLimited, DailyQuotaReached) as exc:
            if self.secondary is None:
                raise
            self.fallback_reason = f"{getattr(self.primary, 'name', 'primary')}: {type(exc).__name__}"
            return self._secondary(system, user, max_completion_tokens)
        except CacheMiss:
            # replay: the request may have been answered by the fallback when it was recorded
            sec_cache = getattr(self.secondary, "cache", None)
            if sec_cache is not None and self.secondary.request_key(system, user, max_completion_tokens) in sec_cache:
                self.fallback_reason = "replay: recorded from the fallback provider"
                return self._secondary(system, user, max_completion_tokens)
            raise
        res.provider = res.provider or getattr(self.primary, "name", "groq")
        self.last_provider = res.provider
        return res

    def complete_json(self, system: str, prompt: str, max_tokens: int = 4000) -> dict | None:
        return extract_json(self.chat(system + "\nReply with a single JSON object and nothing else.", prompt,
                                      max_tokens).text)


def bedrock_for(model: str, cache_path: Path | None = None, ledger: Path = LEDGER) -> BedrockChatLLM | None:
    """The Bedrock fallback for a project model name, or None (no key, or no Bedrock id for that model)."""
    key = os.environ.get("AWS_BEARER_TOKEN_BEDROCK", "")
    mid = BEDROCK_MODEL_IDS.get(model)
    if not key or not mid:
        return None
    region = os.environ.get("BR_BEDROCK_REGION") or os.environ.get("AWS_REGION") or DEFAULT_REGION
    if region == "ap-south-1":                  # answers 400 "Operation not allowed" for this account (13 Oct)
        region = DEFAULT_REGION
    return BedrockChatLLM(api_key=key, model=mid, region=region, ledger=ledger,
                          cache=LLMCache(cache_path) if cache_path else None)


def bedrock_cache_path(groq_cache: Path) -> Path:
    """Bedrock's cache file beside a Groq one: `<stem>.bedrock.jsonl` (a separate file, a separate key space)."""
    p = Path(groq_cache)
    return p.with_name(p.stem + ".bedrock.jsonl")


def with_fallback(primary, model: str, groq_cache: Path | None = None):
    """Wrap a Groq provider (may be None) with the Bedrock fallback when one is configured.

    Returns:
        A :class:`FallbackLLM`, the primary unchanged when no fallback exists, or None when neither exists.
    """
    force = (os.environ.get("BR_LLM_PROVIDER") or "").strip().lower() == "bedrock"
    sec = bedrock_for(model, bedrock_cache_path(groq_cache) if groq_cache else None)
    if sec is None:
        return primary
    return FallbackLLM(primary, sec, force_secondary=force)


def status(model: str, groq_ok: bool | None = None) -> dict:
    """What the model chip shows: which provider the next call would use, and why (no network, no secret).

    Args:
        model: Project model name.
        groq_ok: False when Groq's daily quota is known to be used up.
    """
    groq = bool(os.environ.get("GROQ_API_KEY"))
    mid = BEDROCK_MODEL_IDS.get(model)
    bed_key = bool(os.environ.get("AWS_BEARER_TOKEN_BEDROCK")) and mid is not None
    spent, cap = ledger_spend(), budget_usd()
    bed_ok = bed_key and spent < cap
    force = (os.environ.get("BR_LLM_PROVIDER") or "").strip().lower() == "bedrock"
    if force and bed_ok:
        prov, why = "bedrock", "BR_LLM_PROVIDER=bedrock"
    elif groq and groq_ok is not False:
        prov, why = "groq", "primary"
    elif bed_ok:
        prov, why = "bedrock", "Groq unavailable (no key or daily quota used up)"
    else:
        prov, why = None, "no provider available"
    return {"provider": prov, "why": why, "model": model, "slug": model_slug(model),
            "bedrock": {"configured": bed_key, "model_id": mid, "spent_usd": round(spent, 6), "budget_usd": cap,
                        "ok": bed_ok}}
