"""E3 replay guarantees (phase 034): cached replies never consume quota, prompts are byte-deterministic,
chunks are rendered from the text they were indexed from, and reasoning parameters follow the model.

Repos are real git working trees (the checked-in shopcart sample or a hand-written module); the only thing
replaced is the HTTP transport, and where a test replaces it, it fails the test if it is ever called.
"""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import analysis.rq4_repair as rq4
from src.agents import repair
from src.agents.llm import DailyQuotaReached, GroqLLM, LLMError, groq_reasoning_params
from src.agents.llm_cache import LLMCache
from src.agents.repair import SYSTEM, Chunk, FailureReport, RepairAgent, build_prompt, render_chunk, select_chunks
from src.eval.seeded.build import git, run_suite, source_files
from src.eval.seeded.validate import head_state, make_validator

SAMPLE = Path(__file__).resolve().parents[1] / "src" / "agents" / "demo" / "sample_repo"
FIXED = "return subtotal - (subtotal * percent) // 100"
BUG = "return subtotal + (subtotal * percent) // 100"
FILES = ["shopcart/pricing.py", "shopcart/cart.py"]
REPLY = f"shopcart/pricing.py\n<<<<<<< SEARCH\n{BUG}\n=======\n{FIXED}\n>>>>>>> REPLACE"


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


def report(bug_diff: str) -> FailureReport:
    return FailureReport(
        failing=[{"test_id": "tests.test_pricing::test_welcome10_takes_ten_percent",
                  "output": "assert 11000 == 9000\n where 11000 = apply_discount(10000, 'WELCOME10')"}],
        pr_diff=bug_diff, triage="mine", changed_files=["shopcart/pricing.py"])


def no_network(monkeypatch) -> None:
    def boom(*a, **k):
        raise AssertionError("network call")
    monkeypatch.setattr("src.agents.llm.requests.post", boom)


# ---- Rule 2: cached replies never consume quota ---------------------------------------------------
def test_a_fully_cached_task_runs_with_a_zero_daily_budget(repo, bug_diff, tmp_path, monkeypatch) -> None:
    no_network(monkeypatch)
    monkeypatch.setenv("BR_GROQ_TPD", "0")
    ledger = tmp_path / "usage.jsonl"
    from datetime import datetime, timezone
    ledger.write_text(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "model": "openai/gpt-oss-120b",
                                  "tokens": 10**9}) + "\n")
    cache = LLMCache(tmp_path / "c.jsonl")
    llm = GroqLLM(api_key="k", cache=cache, ledger=ledger)
    assert llm.tpd == 0
    rep = report(bug_diff)
    with head_state(repo, bug_diff):
        for arm, sel in (("R1", "R1"), ("R2", "R2")):
            prompt = build_prompt(arm, rep, select_chunks(sel, repo, FILES, rep), repo)
            cache.put(llm.request_key(SYSTEM, prompt, 1500), {"x": 1}, REPLY, {"total_tokens": 900}, llm.model)
        py = Path(sys.executable)
        failing = list(run_suite(repo, py).failing)
        for arm in ("R1", "R2", "R3"):
            res = RepairAgent(llm, arm).run(repo, FILES, rep, make_validator(repo, py, set(), failing))
            assert res.accepted and all(a.from_cache for a in res.attempts), arm
    # a request that is NOT cached is the only thing the budget stops
    with pytest.raises(DailyQuotaReached):
        llm.chat("another system prompt", "never recorded")


def test_estimate_counts_only_the_uncached_remainder(repo, bug_diff, tmp_path, monkeypatch) -> None:
    seeded = tmp_path / "seeded"
    (seeded / "repos").mkdir(parents=True)
    shutil.move(str(repo), str(seeded / "repos" / "shopcart"))
    monkeypatch.setattr(rq4, "SEEDED", seeded)
    repo = seeded / "repos" / "shopcart"
    task = {"task_id": "shopcart-X-00", "repo": "shopcart", "pr_diff": bug_diff, "failing_tests": report(bug_diff).failing}
    pins = {"shopcart": {"src_dirs": ["shopcart"]}}
    cache = LLMCache(tmp_path / "c.jsonl")
    llm = GroqLLM(api_key="k", cache=cache, ledger=tmp_path / "u.jsonl")
    cold = rq4.estimate_run([task], pins, llm)
    assert (cold.calls_live, cold.calls_cached, cold.tasks_live) == (2, 0, 1)
    assert cold.tout == 1500 * (1 + 3) and cold.tin > 0          # R1 once, R2 first call + two retries
    with head_state(repo, bug_diff):
        rep = report(bug_diff)
        srcs = source_files(repo, {"src_dirs": ["shopcart"]})
        tie = rq4.e1_priority(repo, ["shopcart/pricing.py"], 2)
        prompts = {arm: build_prompt(arm, rep, select_chunks(arm, repo, srcs, rep, tie if arm == "R2" else None), repo)
                   for arm in ("R1", "R2")}
        r2_prompt = prompts["R2"]
        for arm in ("R1", "R2"):
            p = prompts[arm]
            cache.put(llm.request_key(SYSTEM, p, 1500), {"messages": [{"role": "user", "content": p}]}, "", None,
                      llm.model)
        retry = r2_prompt[:-len("\n\nReply with SEARCH/REPLACE blocks only.")] + "\n\nYour previous patch did not make the whole suite pass."
        cache.put(llm.request_key(SYSTEM, retry, 1500), {"messages": [{"role": "user", "content": retry}]}, "", None,
                  llm.model)
    warm = rq4.estimate_run([task], pins, llm)
    assert (warm.calls_live, warm.calls_cached, warm.tasks_live, warm.retries_cached) == (0, 2, 0, 1)
    assert warm.tin == 0 and warm.tout == 0


# ---- Rule 3: deterministic prompts ----------------------------------------------------------------
_PROMPT_SCRIPT = """
import hashlib, sys
from pathlib import Path
from src.agents.repair import FailureReport, build_prompt, select_chunks
from src.eval.seeded.validate import head_state
repo, diff = Path(sys.argv[1]), Path(sys.argv[2]).read_text()
rep = FailureReport(failing=[{"test_id": "tests.test_pricing::test_welcome10_takes_ten_percent",
                              "output": "assert 11000 == 9000 in apply_discount percent subtotal code"}],
                    pr_diff=diff, triage="mine", changed_files=["shopcart/pricing.py", "shopcart/cart.py"])
h = hashlib.sha256()
with head_state(repo, diff):
    for arm in ("R1", "R2"):
        ch = select_chunks(arm, repo, ["shopcart/pricing.py", "shopcart/cart.py", "shopcart/catalog.py"], rep)
        h.update(build_prompt(arm, rep, ch, repo).encode())
print(h.hexdigest())
"""


def test_the_same_prompt_has_identical_bytes_in_fresh_processes(repo, bug_diff, tmp_path) -> None:
    diff = tmp_path / "bug.diff"
    diff.write_text(bug_diff)
    root = Path(__file__).resolve().parents[1]
    digests = set()
    for seed in ("0", "1", "2", "random"):
        out = subprocess.run([sys.executable, "-c", _PROMPT_SCRIPT, str(repo), str(diff)], cwd=root, check=True,
                             capture_output=True, text=True, env={**__import__("os").environ, "PYTHONHASHSEED": seed})
        digests.add(out.stdout.strip())
    assert len(digests) == 1 and len(next(iter(digests))) == 64


def test_repair_bm25_matches_the_baseline_formula() -> None:
    from src.eval.baselines import bm25_scores

    docs = [["cart", "add", "qty", "cart"], ["price", "discount", "percent"], ["cart", "total", "price", "tax"]]
    query = ["cart", "price", "tax", "zzz", "cart"]
    assert repair.bm25_scores(docs, query) == pytest.approx(list(bm25_scores(docs, query)), abs=1e-12)
    assert repair.bm25_scores([], query) == [] and repair.bm25_scores(docs, []) == [0.0, 0.0, 0.0]


# ---- Part B: chunks come from the text they were indexed from -------------------------------------
MODULE = '''def helper(a):
    return a + 1


def target(x):
    if x > 0:
        return x
    return 0
'''


def test_a_distractor_above_the_target_does_not_shift_the_rendered_chunk(tmp_path) -> None:
    r = tmp_path / "m"
    r.mkdir()
    (r / "m.py").write_text(MODULE)
    git(r, "init", "-q")
    git(r, "add", "-A")
    git(r, "commit", "-q", "-m", "base")
    edited = MODULE.replace("def helper(a):\n", "def helper(a):\n    # reviewed: no functional change intended\n")
    edited = edited.replace("if x > 0:", "if x >= 0:")      # the mutant, now one line further down
    (r / "m.py").write_text(edited)
    diff = git(r, "diff", "--no-color")
    git(r, "checkout", "--", ".")
    rep = FailureReport(failing=[{"test_id": "tests.test_m::test_target", "output": "target x 0"}], pr_diff=diff,
                        triage="mine", changed_files=["m.py"])
    with head_state(r, diff):
        chunks = select_chunks("R2", r, ["m.py"], rep)
        assert {c.qualname for c in chunks} == {"helper", "target"}
        text = build_prompt("R2", rep, chunks, r)
        want = (r / "m.py").read_text().splitlines().index("def target(x):") + 1
    assert f"{want:>5}| def target(x):" in text
    assert repair.CLAMPED == []


def test_render_uses_the_indexed_text_not_a_second_read_of_the_file(tmp_path) -> None:
    (tmp_path / "m.py").write_text(MODULE)
    (c,) = [c for c in repair.index_functions(tmp_path, ["m.py"]) if c.qualname == "target"]
    before = render_chunk(c, tmp_path)
    (tmp_path / "m.py").write_text("x = 1\n")     # the tree changes under the chunk: formerly an IndexError
    assert render_chunk(c, tmp_path) == before and "def target(x):" in before


def test_a_focus_outside_the_function_is_clamped_and_logged_as_a_bug(tmp_path, caplog) -> None:
    (tmp_path / "m.py").write_text(MODULE)
    (c,) = [c for c in repair.index_functions(tmp_path, ["m.py"]) if c.qualname == "target"]
    stale = Chunk(c.file, c.qualname, c.start, c.end, c.focus + 50, 0.0, c.text)
    repair.CLAMPED.clear()
    with caplog.at_level(logging.ERROR, logger="src.agents.repair"):
        out = render_chunk(stale, tmp_path)
    assert "def target(x):" in out and len(repair.CLAMPED) == 1 and "BUG" in caplog.text
    repair.CLAMPED.clear()


_LOCK_SCRIPT = '''
import sys
from pathlib import Path
from src.eval.seeded.validate import head_state
with head_state(Path(sys.argv[1]), Path(sys.argv[2]).read_text()):
    print("entered", flush=True)
'''


def test_a_second_process_waits_for_the_repo_lock(repo, bug_diff, tmp_path) -> None:
    """Two runs must not rewrite one working tree at once (the cause of ranges from one tree, text from another)."""
    from src.eval.seeded.validate import repo_lock

    diff = tmp_path / "bug.diff"
    diff.write_text(bug_diff)
    root = Path(__file__).resolve().parents[1]
    cmd = [sys.executable, "-c", _LOCK_SCRIPT, str(repo), str(diff)]
    with repo_lock(repo):
        with pytest.raises(subprocess.TimeoutExpired):
            subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=4)
    done = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=60)
    assert done.returncode == 0 and "entered" in done.stdout


# ---- Part C: reasoning parameters follow the model ------------------------------------------------
def test_reasoning_parameters_are_sent_only_to_models_known_to_take_them(tmp_path) -> None:
    assert groq_reasoning_params("openai/gpt-oss-120b") == {"reasoning_effort": "low", "include_reasoning": False}
    assert groq_reasoning_params("qwen/qwen3.8-27b") == {}
    q = GroqLLM(api_key="k", model="qwen/qwen3.8-27b", ledger=tmp_path / "u.jsonl")
    assert set(q.request_params(1500)) == {"temperature", "seed", "max_completion_tokens"}
    g = GroqLLM(api_key="k", model="openai/gpt-oss-120b", ledger=tmp_path / "u.jsonl")
    assert g.request_params(1500) == {"temperature": 0, "seed": 0, "reasoning_effort": "low", "include_reasoning": False,
                                      "max_completion_tokens": 1500}


class Resp:
    def __init__(self, status, text="", body=None):
        self.status_code, self.text, self._b, self.headers = status, text, body or {}, {}

    def json(self):
        return self._b


OK = {"model": "m", "choices": [{"message": {"content": "reply"}}], "usage": {"total_tokens": 10}}


def test_a_400_that_names_a_reasoning_parameter_drops_exactly_that_one(tmp_path, monkeypatch) -> None:
    sent = []

    def post(url, headers=None, json=None, timeout=None):
        sent.append(dict(json))
        if "include_reasoning" in json:
            return Resp(400, '{"error":{"message":"`include_reasoning` is not supported with this model"}}')
        return Resp(200, body=OK)

    monkeypatch.setattr("src.agents.llm.requests.post", post)
    cache = LLMCache(tmp_path / "c.jsonl")
    llm = GroqLLM(api_key="k", model="openai/gpt-oss-20b", cache=cache, ledger=tmp_path / "u.jsonl",
                  sleeper=lambda s: None)
    assert llm.chat("s", "u").text == "reply"
    assert "include_reasoning" in sent[0] and "include_reasoning" not in sent[1]
    assert sent[1]["reasoning_effort"] == "low" and sent[1]["temperature"] == 0 and sent[1]["seed"] == 0
    # a fresh process finds the reply under the parameters that were accepted, without asking again
    no_network(monkeypatch)
    again = GroqLLM(api_key="k", model="openai/gpt-oss-20b", cache=LLMCache(tmp_path / "c.jsonl"),
                    ledger=tmp_path / "u.jsonl")
    assert again.chat("s", "u").from_cache


def test_a_400_about_temperature_is_never_worked_around(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("src.agents.llm.requests.post",
                        lambda *a, **k: Resp(400, '{"error":{"message":"temperature must be above 0"}}'))
    llm = GroqLLM(api_key="k", model="qwen/qwen3.8-27b", ledger=tmp_path / "u.jsonl", sleeper=lambda s: None)
    with pytest.raises(LLMError, match="400"):
        llm.chat("s", "u")
