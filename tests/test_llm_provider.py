"""D-69: Groq -> Bedrock fallback, the Bedrock budget, reasoning stripping and cache separation (no network)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.agents.llm import DailyQuotaReached, GroqLLM, RateLimited
from src.agents.llm_cache import LLMCache
from src.agents.llm_provider import (BedrockChatLLM, BudgetExhausted, FallbackLLM, budget_usd, ledger_spend,
                                     strip_reasoning, with_fallback)

FIX = Path(__file__).parent / "fixtures" / "agent"


class Recorded:
    """A recorded HTTP response (status, headers, body) as `requests` would return it."""

    def __init__(self, name: str) -> None:
        d = json.loads((FIX / name).read_text(encoding="utf-8"))
        self.status_code, self.headers, self._body = d["status"], d["headers"], d["body"]
        self.text = json.dumps(self._body)

    def json(self):
        return self._body


def _route(monkeypatch, calls: list, answers: dict[str, str]) -> None:
    def post(url, **kw):
        calls.append(url)
        host = "groq" if "groq.com" in url else "bedrock"
        return Recorded(answers[host])
    monkeypatch.setattr("src.agents.llm.requests.post", post)
    monkeypatch.setattr("src.agents.llm_provider.requests.post", post)


def _pair(tmp_path: Path, **bed):
    groq = GroqLLM(api_key="g", cache=LLMCache(tmp_path / "groq.jsonl"), ledger=tmp_path / "usage.jsonl",
                   max_retries=0, sleeper=lambda s: None)
    bedrock = BedrockChatLLM(api_key="b", cache=LLMCache(tmp_path / "groq.bedrock.jsonl"),
                             ledger=tmp_path / "bedrock_ledger.jsonl", sleeper=lambda s: None, **bed)
    return groq, bedrock


def test_recorded_429_falls_back_to_bedrock_and_strips_reasoning(tmp_path, monkeypatch) -> None:
    calls: list = []
    _route(monkeypatch, calls, {"groq": "groq_429_rate_limit.json", "bedrock": "bedrock_reply_reasoning.json"})
    groq, bedrock = _pair(tmp_path)
    llm = FallbackLLM(groq, bedrock)
    res = llm.chat("sys", "fix it")
    assert [("groq" in u) for u in calls] == [True, False]
    assert calls[1] == "https://bedrock-runtime.us-west-2.amazonaws.com/openai/v1/chat/completions"
    assert res.provider == "bedrock" and llm.last_provider == "bedrock"
    assert llm.fallback_reason == "groq: RateLimited"
    assert "<reasoning>" not in res.text and res.text.startswith("src/m.py\n<<<<<<< SEARCH")
    assert "comparison must be age > max_age" in llm.last_reasoning
    # cost at list price from the usage block: 1012 * 0.15/1e6 + 388 * 0.60/1e6
    assert res.usage["cost_usd"] == pytest.approx(1012 * 0.15e-6 + 388 * 0.60e-6)
    row = json.loads((tmp_path / "bedrock_ledger.jsonl").read_text().splitlines()[0])
    assert row["tokens_in"] == 1012 and row["tokens_out"] == 388 and row["model"] == "openai.gpt-oss-120b-1:0"
    # the cache holds the answer, never the reasoning
    cached = (tmp_path / "groq.bedrock.jsonl").read_text()
    assert "comparison must be age" not in cached and "REPLACE" in cached


def test_recorded_daily_429_falls_back(tmp_path, monkeypatch) -> None:
    calls: list = []
    _route(monkeypatch, calls, {"groq": "groq_429_daily.json", "bedrock": "bedrock_reply_reasoning.json"})
    groq, bedrock = _pair(tmp_path)
    llm = FallbackLLM(groq, bedrock)
    assert llm.chat("sys", "u").provider == "bedrock"
    assert llm.fallback_reason == "groq: DailyQuotaReached"


def test_no_fallback_configured_reraises_429(tmp_path, monkeypatch) -> None:
    _route(monkeypatch, [], {"groq": "groq_429_rate_limit.json"})
    groq, _ = _pair(tmp_path)
    with pytest.raises(RateLimited):
        FallbackLLM(groq, None).chat("sys", "u")
    _route(monkeypatch, [], {"groq": "groq_429_daily.json"})
    with pytest.raises(DailyQuotaReached):
        FallbackLLM(groq, None).chat("sys", "u")


def test_forced_bedrock_never_calls_groq(tmp_path, monkeypatch) -> None:
    calls: list = []
    _route(monkeypatch, calls, {"bedrock": "bedrock_reply_reasoning.json"})
    groq, bedrock = _pair(tmp_path)
    res = FallbackLLM(groq, bedrock, force_secondary=True).chat("sys", "u")
    assert res.provider == "bedrock" and all("groq" not in u for u in calls)


def test_budget_refusal_sends_no_request(tmp_path, monkeypatch) -> None:
    calls: list = []
    _route(monkeypatch, calls, {"bedrock": "bedrock_reply_reasoning.json"})
    _, bedrock = _pair(tmp_path, max_usd=0.01)
    (tmp_path / "bedrock_ledger.jsonl").write_text(json.dumps({"cost_usd": 0.01}) + "\n")
    with pytest.raises(BudgetExhausted):
        bedrock.chat("sys", "u")
    assert calls == []
    assert ledger_spend(tmp_path / "bedrock_ledger.jsonl") == pytest.approx(0.01)


def test_budget_is_clamped_to_hard_max(monkeypatch) -> None:
    monkeypatch.setenv("BR_BEDROCK_MAX_USD", "500")
    assert budget_usd() == 50.0
    monkeypatch.delenv("BR_BEDROCK_MAX_USD")
    monkeypatch.setenv("BR_BEDROCK_BUDGET_USD", "3")
    assert budget_usd() == 3.0
    monkeypatch.delenv("BR_BEDROCK_BUDGET_USD")
    assert budget_usd() == 5.0
    assert BedrockChatLLM(api_key="x", max_usd=99).max_usd == 50.0


def test_cache_keys_separate_provider_and_model(tmp_path) -> None:
    groq, bedrock = _pair(tmp_path)
    kg, kb = groq.request_key("s", "u", 1500), bedrock.request_key("s", "u", 1500)
    assert kg != kb
    # a Groq recording replays through the fallback wrapper with Groq's key, untouched by Bedrock
    groq.cache.put(kg, {"x": 1}, "groq answer", {"total_tokens": 5}, groq.model)
    llm = FallbackLLM(groq, bedrock)
    res = llm.chat("s", "u", 1500)
    assert res.from_cache and res.text == "groq answer" and res.provider == "groq"
    assert not (tmp_path / "groq.bedrock.jsonl").exists()


def test_replay_finds_answer_recorded_from_fallback(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("src.agents.llm.requests.post", lambda *a, **k: (_ for _ in ()).throw(AssertionError("net")))
    monkeypatch.setattr("src.agents.llm_provider.requests.post", lambda *a, **k: (_ for _ in ()).throw(AssertionError("net")))
    groq = GroqLLM(api_key="g", cache=LLMCache(tmp_path / "g.jsonl", replay=True), ledger=tmp_path / "u.jsonl")
    bedrock = BedrockChatLLM(api_key="b", cache=LLMCache(tmp_path / "b.jsonl", replay=True), ledger=tmp_path / "l.jsonl")
    bedrock.cache.put(bedrock.request_key("s", "u"), {"x": 1}, "bedrock answer", {"total_tokens": 1}, bedrock.model)
    res = FallbackLLM(groq, bedrock).chat("s", "u")
    assert res.text == "bedrock answer" and res.provider == "bedrock" and res.from_cache


def test_strip_reasoning_shapes() -> None:
    assert strip_reasoning("<reasoning>a</reasoning>ans") == ("ans", "<reasoning>a</reasoning>")
    assert strip_reasoning("plain") == ("plain", "")
    assert strip_reasoning("<reasoning>never closed") == ("", "<reasoning>never closed")


def test_with_fallback_needs_a_key(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("AWS_BEARER_TOKEN_BEDROCK", raising=False)
    groq, _ = _pair(tmp_path)
    assert with_fallback(groq, "openai/gpt-oss-120b", tmp_path / "g.jsonl") is groq
    monkeypatch.setenv("AWS_BEARER_TOKEN_BEDROCK", "k")
    monkeypatch.setenv("BR_BEDROCK_REGION", "ap-south-1")
    w = with_fallback(groq, "openai/gpt-oss-120b", tmp_path / "g.jsonl")
    assert isinstance(w, FallbackLLM) and w.secondary.region == "us-west-2"   # ap-south-1 is never used
    assert with_fallback(groq, "openai/gpt-oss-20b", tmp_path / "g.jsonl") is groq  # no Bedrock id for 20b
