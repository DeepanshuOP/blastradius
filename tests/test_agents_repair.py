"""Repair agent (D-58), offline: strict patching, routing, full-suite acceptance, replay cache, limiter.

The HTTP transport is the only thing replaced (a recorded-shape Groq response); the repo under
repair is the real checked-in shopcart sample and the suites are real pytest runs.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

from src.agents.llm import DailyQuotaReached, GroqLLM, get_llm
from src.agents.llm_cache import CacheMiss, LLMCache, cache_key
from src.agents.repair import (Chunk, FailureReport, RepairAgent, apply_blocks, build_prompt, changed_line_ranges,
                               parse_blocks, route, select_chunks)
from src.eval.seeded.build import git, run_suite
from src.eval.seeded.validate import head_state, make_validator

SAMPLE = Path(__file__).resolve().parents[1] / "src" / "agents" / "demo" / "sample_repo"
FIXED = "return subtotal - (subtotal * percent) // 100"
BUG = "return subtotal + (subtotal * percent) // 100"


@pytest.fixture()
def repo(tmp_path):
    dst = tmp_path / "shopcart"
    shutil.copytree(SAMPLE, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    git(dst, "init", "-q")
    git(dst, "add", "-A")
    git(dst, "commit", "-q", "-m", "base")
    return dst


@pytest.fixture()
def bug_diff(repo):
    p = repo / "shopcart" / "pricing.py"
    p.write_text(p.read_text().replace(FIXED, BUG))
    d = git(repo, "diff", "--no-color")
    git(repo, "checkout", "--", ".")
    return d


def failing_report(bug_diff: str) -> FailureReport:
    return FailureReport(
        failing=[{"test_id": "tests.test_pricing::test_welcome10_takes_ten_percent",
                  "output": "assert 11000 == 9000\n where 11000 = apply_discount(10000, 'WELCOME10')"},
                 {"test_id": "tests.test_pricing::test_code_is_case_insensitive", "output": "assert 11500 == 8500"}],
        pr_diff=bug_diff, triage="mine", changed_files=["shopcart/pricing.py"])


# ---- strict patching -------------------------------------------------------------------------
def test_blocks_parse_through_code_fences() -> None:
    reply = "```\nshopcart/pricing.py\n<<<<<<< SEARCH\na = 1\n=======\na = 2\n>>>>>>> REPLACE\n```"
    assert parse_blocks(reply) == [("shopcart/pricing.py", "a = 1", "a = 2")]


def test_search_must_match_exactly_once(repo) -> None:
    ok = apply_blocks(repo, [("shopcart/pricing.py", "if not code:", "if code is None:")])
    assert "if code is None:" in ok["shopcart/pricing.py"]
    with pytest.raises(ValueError, match="0 times"):
        apply_blocks(repo, [("shopcart/pricing.py", "no such text", "x")])
    with pytest.raises(ValueError, match="2 times"):
        apply_blocks(repo, [("shopcart/pricing.py", "return subtotal\n", "x")])  # appears twice
    with pytest.raises(ValueError, match="not one of the files shown"):
        apply_blocks(repo, [("shopcart/cart.py", "x", "y")], allowed={"shopcart/pricing.py"})
    with pytest.raises(ValueError, match="no SEARCH"):
        apply_blocks(repo, [])


def test_two_blocks_in_one_file_compose(repo) -> None:
    out = apply_blocks(repo, [("shopcart/pricing.py", '"WELCOME10": 10', '"WELCOME10": 12'),
                              ("shopcart/pricing.py", '"STUDENT15": 15', '"STUDENT15": 17')])
    assert '"WELCOME10": 12' in out["shopcart/pricing.py"] and '"STUDENT15": 17' in out["shopcart/pricing.py"]


# ---- routing -----------------------------------------------------------------------------------
def test_routing_by_triage_class() -> None:
    assert route("mine") == "repair" and route("flaky") == "rerun" and route("inherited") == "ignore"


class NoCall:
    def chat(self, *a, **k):
        raise AssertionError("the model must not be called")


def test_only_mine_failures_reach_the_model(repo, bug_diff) -> None:
    for cls, action in (("flaky", "rerun"), ("inherited", "ignore")):
        rep = failing_report(bug_diff)
        rep.triage = cls
        res = RepairAgent(NoCall(), "R2").run(repo, ["shopcart/pricing.py"], rep, lambda f: (True, ""))
        assert res.action == action and not res.attempts and not res.accepted
    res = RepairAgent(NoCall(), "R0").run(repo, ["shopcart/pricing.py"], failing_report(bug_diff), lambda f: (True, ""))
    assert res.action == "notify"


# ---- retrieval ---------------------------------------------------------------------------------
def test_changed_line_ranges_from_a_diff(bug_diff) -> None:
    r = changed_line_ranges(bug_diff)
    assert list(r) == ["shopcart/pricing.py"] and r["shopcart/pricing.py"] == [20]


def test_r2_searches_only_touched_functions_r1_searches_everything(repo, bug_diff) -> None:
    files = ["shopcart/pricing.py", "shopcart/cart.py", "shopcart/tax.py", "shopcart/catalog.py"]
    with head_state(repo, bug_diff):
        rep = failing_report(bug_diff)
        r2 = select_chunks("R2", repo, files, rep)
        assert [(c.file, c.qualname) for c in r2] == [("shopcart/pricing.py", "apply_discount")]
        r1 = select_chunks("R1", repo, files, rep)
        assert len(r1) == 3 and r1[0].qualname == "apply_discount"
        prompt = build_prompt("R2", rep, r2, repo)
        assert "MINE" in prompt and "shopcart/pricing.py" in prompt and "SEARCH/REPLACE" in prompt
        assert "MINE" not in build_prompt("R1", rep, r1, repo)  # log-only arm never gets the change


# ---- validation: the full suite decides --------------------------------------------------------
def test_full_suite_accepts_the_real_fix_and_rejects_an_overfit_patch(repo, bug_diff) -> None:
    py = Path(sys.executable)
    with head_state(repo, bug_diff):
        base_fail = run_suite(repo, py).failing
        assert any("welcome10" in t for t in base_fail) and len(base_fail) == 3  # 2 pricing + 1 cart test
        validate = make_validator(repo, py, preexisting=set(), target_tests=list(base_fail))
        good = apply_blocks(repo, [("shopcart/pricing.py", BUG, FIXED)])
        assert validate(good)[0] is True
        # overfit: the three target tests pass, test_unknown_code_is_ignored (a green test) now fails
        overfit = apply_blocks(repo, [("shopcart/pricing.py",
                                       f"    if percent is None:\n        return subtotal\n    {BUG}",
                                       f"    if percent is None:\n        return 0\n    {FIXED}")])
        ok, out = validate(overfit)
        assert ok is False and "test_unknown_code_is_ignored" in out
        # the working tree is restored after every validation
        assert BUG in (repo / "shopcart" / "pricing.py").read_text()


def test_agent_end_to_end_from_a_recorded_reply_in_replay_mode(repo, bug_diff, tmp_path) -> None:
    """A recorded model reply is replayed through the real prompt, strict apply and full-suite validation."""
    files = ["shopcart/pricing.py", "shopcart/cart.py"]
    reply = f"shopcart/pricing.py\n<<<<<<< SEARCH\n{BUG}\n=======\n{FIXED}\n>>>>>>> REPLACE"
    cache_file = tmp_path / "cache.jsonl"
    with head_state(repo, bug_diff):
        rep = failing_report(bug_diff)
        chunks = select_chunks("R2", repo, files, rep)
        from src.agents.repair import SYSTEM
        prompt = build_prompt("R2", rep, chunks, repo)
        params = {"temperature": 0, "seed": 0, "reasoning_effort": "low", "include_reasoning": False,
                  "max_completion_tokens": 1500}
        key = cache_key("groq", "openai/gpt-oss-120b", SYSTEM, [{"role": "user", "content": prompt}], params)
        LLMCache(cache_file).put(key, {"x": 1}, reply, {"total_tokens": 900}, "openai/gpt-oss-120b")
        llm = GroqLLM(api_key="", cache=LLMCache(cache_file, replay=True), ledger=tmp_path / "usage.jsonl")
        py = Path(sys.executable)
        base_fail = run_suite(repo, py).failing
        res = RepairAgent(llm, "R2").run(repo, files, rep, make_validator(repo, py, set(), list(base_fail)))
    assert res.accepted and res.attempts[0].from_cache and res.attempts[0].usage == {"total_tokens": 900}
    assert not (tmp_path / "usage.jsonl").exists()  # a cache hit spends nothing


def test_replay_mode_cache_miss_raises_and_never_calls_the_network(tmp_path, monkeypatch) -> None:
    def boom(*a, **k):
        raise AssertionError("network call in replay mode")
    monkeypatch.setattr("src.agents.llm.requests.post", boom)
    llm = GroqLLM(api_key="k", cache=LLMCache(tmp_path / "c.jsonl", replay=True), ledger=tmp_path / "u.jsonl")
    with pytest.raises(CacheMiss):
        llm.chat("sys", "user")


# ---- Groq provider: limiter, quota, selection ---------------------------------------------------
class FakeResp:
    def __init__(self, status=200, body=None, headers=None, text=""):
        self.status_code, self._body, self.headers, self.text = status, body or {}, headers or {}, text

    def json(self):
        return self._body


OK = {"model": "openai/gpt-oss-120b", "choices": [{"message": {"content": "ok"}}],
      "usage": {"prompt_tokens": 76, "completion_tokens": 16, "total_tokens": 92}, "x_groq": {"id": "req_1"}}


def test_groq_retries_429_with_retry_after_and_records_usage(tmp_path, monkeypatch) -> None:
    calls = []
    seq = [FakeResp(429, headers={"retry-after": "7"}, text="rate limit"), FakeResp(200, OK)]
    monkeypatch.setattr("src.agents.llm.requests.post", lambda *a, **k: calls.append(k) or seq.pop(0))
    slept = []
    llm = GroqLLM(api_key="k", ledger=tmp_path / "u.jsonl", sleeper=slept.append, cache=LLMCache(tmp_path / "c.jsonl"))
    r = llm.chat("s", "u")
    assert r.text == "ok" and not r.from_cache and slept[0] == 7.0 and len(calls) == 2
    body = calls[-1]["json"]
    assert body["temperature"] == 0 and body["seed"] == 0 and body["reasoning_effort"] == "low"
    assert "n" not in body and "logprobs" not in body and "logit_bias" not in body
    assert json.loads((tmp_path / "u.jsonl").read_text())["tokens"] == 92
    assert llm.chat("s", "u").from_cache  # second identical call is free


def test_tool_call_reply_is_an_empty_cached_answer_not_a_crash(tmp_path, monkeypatch) -> None:
    n = []
    body = '{"error":{"message":"Tool choice is none, but model called a tool","code":"tool_use_failed"}}'
    monkeypatch.setattr("src.agents.llm.requests.post", lambda *a, **k: n.append(1) or FakeResp(400, text=body))
    llm = GroqLLM(api_key="k", ledger=tmp_path / "u.jsonl", sleeper=lambda s: None, cache=LLMCache(tmp_path / "c.jsonl"))
    r = llm.chat("s", "u")
    assert r.text == "" and not r.from_cache and len(n) == 1
    assert llm.chat("s", "u").from_cache and len(n) == 1


def test_other_4xx_is_not_retried(tmp_path, monkeypatch) -> None:
    n = []
    monkeypatch.setattr("src.agents.llm.requests.post", lambda *a, **k: n.append(1) or FakeResp(400, text="bad"))
    llm = GroqLLM(api_key="k", ledger=tmp_path / "u.jsonl", sleeper=lambda s: None)
    with pytest.raises(Exception, match="400"):
        llm.chat("s", "u")
    assert len(n) == 1


def test_daily_quota_stops_cleanly_before_the_call(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("src.agents.llm.requests.post", lambda *a, **k: (_ for _ in ()).throw(AssertionError()))
    ledger = tmp_path / "u.jsonl"
    now = 1_800_000_000.0
    from datetime import datetime, timezone
    ledger.write_text(json.dumps({"timestamp": datetime.fromtimestamp(now - 3600, timezone.utc).isoformat(),
                                 "model": "openai/gpt-oss-120b", "tokens": 199_000}) + "\n")
    llm = GroqLLM(api_key="k", ledger=ledger, clock=lambda: now, sleeper=lambda s: None, tpd=200_000)
    with pytest.raises(DailyQuotaReached, match="DAILY QUOTA REACHED"):
        llm.chat("s" * 100, "u" * 100)


def test_minute_limiter_waits_for_the_window(tmp_path, monkeypatch) -> None:
    t = [1000.0]
    slept = []

    def sleeper(s):
        slept.append(s)
        t[0] += s
    monkeypatch.setattr("src.agents.llm.requests.post", lambda *a, **k: FakeResp(200, {**OK, "usage": {"total_tokens": 7000}}))
    llm = GroqLLM(api_key="k", ledger=tmp_path / "u.jsonl", clock=lambda: t[0], sleeper=sleeper, tpm=8000)
    llm.chat("s", "u")          # 7000 tokens spent in this minute
    llm.chat("s", "u2")         # estimate ~1500 > 1000 left: must wait for the minute to roll over
    assert slept and sum(slept) >= 59


def test_provider_selection_order(monkeypatch) -> None:
    for k in ("BR_OFFLINE", "BR_AGENT_PROVIDER", "ANTHROPIC_API_KEY", "GROQ_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    assert get_llm().name == "offline"
    monkeypatch.setenv("GROQ_API_KEY", "g")
    assert get_llm().name == "groq"
    monkeypatch.setenv("ANTHROPIC_API_KEY", "a")
    assert get_llm().name == "anthropic"          # an Anthropic key alone keeps its old behaviour
    monkeypatch.setenv("BR_AGENT_PROVIDER", "groq")
    assert get_llm().name == "groq"
    monkeypatch.setenv("BR_OFFLINE", "1")
    assert get_llm().name == "offline"


def test_retry_feedback_is_deterministic(tmp_path) -> None:
    from src.agents.repair import clean_feedback

    raw = f"runner = <click.testing.CliRunner object at 0x75921a4a4390> in {tmp_path}/x.py"
    assert clean_feedback(raw, tmp_path) == "runner = <click.testing.CliRunner object at 0xADDR> in <repo>/x.py"
    assert clean_feedback(raw, tmp_path) == clean_feedback(raw.replace("0x75921a4a4390", "0x7b0546c12450"), tmp_path)
