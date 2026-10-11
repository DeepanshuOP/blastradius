"""Arm R4 (exploratory, D-61): prompt assembly and trimming, and proof that R0-R3 prompts did not move.

The hashes below were recorded from `repair.build_prompt` at commit 5807f36 (before arm R4 existed) on the
checked-in shopcart sample with the bug of `tests/test_agents_repair.py`. If one changes, a pre-registered
prompt changed and the replay cache no longer hits: stop and look.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
import pytest

from src.agents import repair
from src.agents.llm_cache import LLMCache
from src.agents.repair import (ALL_ARMS, ARMS, SYSTEM, FailureReport, RepairAgent, build_prompt, build_prompt_r4,
                               select_chunks)
from src.eval.seeded.build import git, source_files
from src.rag.context import RagContext

SAMPLE = Path(__file__).resolve().parents[1] / "src" / "agents" / "demo" / "sample_repo"
FIXED = "return subtotal - (subtotal * percent) // 100"
BUG = "return subtotal + (subtotal * percent) // 100"
H = {"SYSTEM": "cfff271d45dc02486494826111f55db88ac4643cb33447380bed11b4c0c5cb58",
     "R1": "c3fce8e402b0d686239274ec29c4b7a52b4c2cfd4860213df9a2a5afd8036e03",
     "R1_retry": "0922003dfdc1ee0d3e4d5d044f51236b3f4c551939dad32eeffe2d17f45235e2",
     "R2": "a1b17f500a6d47ebedb75d36724ce57c4cd3ea5208013c4db8edddbe63c7863e",
     "R2_retry": "a317b151e002a3d0bb136f4f6b3e00d5b4612143b6db57782bdb217b425b696a"}


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


@pytest.fixture()
def repo(tmp_path):
    dst = tmp_path / "shopcart"
    shutil.copytree(SAMPLE, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    git(dst, "init", "-q")
    git(dst, "add", "-A")
    git(dst, "commit", "-q", "-m", "base")
    p = dst / "shopcart" / "pricing.py"
    p.write_text(p.read_text().replace(FIXED, BUG))
    return dst


@pytest.fixture()
def report(repo) -> FailureReport:
    return FailureReport(
        failing=[{"test_id": "tests.test_pricing::test_welcome10_takes_ten_percent",
                  "output": "assert 11000 == 9000\n where 11000 = apply_discount(10000, 'WELCOME10')"},
                 {"test_id": "tests.test_pricing::test_code_is_case_insensitive", "output": "assert 11500 == 8500"}],
        pr_diff=git(repo, "diff", "--no-color"), triage="mine", changed_files=["shopcart/pricing.py"])


@pytest.fixture()
def srcs(repo):
    return source_files(repo, {"src_dirs": ["shopcart"]})


class KeywordEmbedder:
    """Hand-checkable vectors: counts of four keywords in the lower-cased text."""

    name = "keywords"
    WORDS = ("discount", "tax", "subtotal", "percent")

    def embed(self, texts):
        return np.array([[t.lower().count(w) for w in self.WORDS] for t in texts], dtype=np.float32)


# ---- R0-R3 are untouched -----------------------------------------------------------------------
def test_r0_to_r3_prompts_and_system_are_byte_identical_to_the_recorded_hashes(repo, report, srcs) -> None:
    assert ARMS == ("R0", "R1", "R2", "R3") and ALL_ARMS == ARMS + ("R4",)
    assert sha(SYSTEM) == H["SYSTEM"]
    r1 = select_chunks("R1", repo, srcs, report)
    r2 = select_chunks("R2", repo, srcs, report)
    assert sha(build_prompt("R1", report, r1, repo)) == H["R1"]
    assert sha(build_prompt("R1", report, r1, repo, "FAILED test_x: boom")) == H["R1_retry"]
    for arm in ("R2", "R3"):
        assert sha(build_prompt(arm, report, r2, repo)) == H["R2"]
        assert sha(build_prompt(arm, report, r2, repo, "FAILED test_x: boom")) == H["R2_retry"]


def test_r4_needs_a_context_provider_and_unknown_arms_still_fail() -> None:
    with pytest.raises(ValueError):
        RepairAgent(None, "R4")
    with pytest.raises(ValueError):
        RepairAgent(None, "R9")


# ---- R4 context ---------------------------------------------------------------------------------
def fake_history(repo, rev, file, qualname, n=2):
    class Item:
        def __init__(self, i):
            self.i = i

        def render(self):
            return f"commit {'abcdef0123'}: earlier change {self.i} to {qualname}\n@@ -1 +1 @@\n-old {self.i}\n+new {self.i}"

    return [Item(1), Item(2)]


def test_select_is_the_change_aware_hybrid_top_chunk(repo, report, srcs, tmp_path) -> None:
    ctx = RagContext(KeywordEmbedder(), "HEAD", tmp_path / "rag", fake_history)
    chunks = ctx.select(repo, srcs, report)
    # only apply_discount is touched by the diff (pricing.py line 20), so it is the only candidate, focus on the bug line
    assert [(c.file, c.qualname, c.start, c.end, c.focus) for c in chunks] == [("shopcart/pricing.py", "apply_discount", 10, 20, 20)]
    hist, sim = ctx.extras(repo, chunks, srcs)
    assert len(hist) == 2 and hist[0].startswith("commit abcdef0123: earlier change 1 to apply_discount")
    # similar code: dense neighbours of apply_discount's text over every function, itself excluded
    # keyword counts (discount, tax, subtotal, percent): query (3,0,7,3); Cart.subtotal (0,0,2,0) cos 0.855;
    # Cart.total (6,2,1,0) cos 0.477; compute_tax (0,4,0,1) cos 0.089
    assert [c.qualname for c in sim] == ["Cart.subtotal", "Cart.total"]
    assert all(c.qualname != "apply_discount" for c in sim)


def test_r4_prompt_has_the_r2_sections_then_history_then_similar_in_that_order(repo, report, srcs, tmp_path) -> None:
    ctx = RagContext(KeywordEmbedder(), "HEAD", tmp_path / "rag", fake_history)
    chunks = ctx.select(repo, srcs, report)
    hist, sim = ctx.extras(repo, chunks, srcs)
    prompt, info = build_prompt_r4(report, chunks, repo, hist, sim)
    order = ["Failing tests:", "Test output (truncated):", "Triage: this failure is MINE", "Candidate code:",
             "Earlier commits that changed apply_discount", "Similar code elsewhere in this repository",
             "Reply with SEARCH/REPLACE blocks only."]
    pos = [prompt.index(h) for h in order]
    assert pos == sorted(pos) and len(set(pos)) == len(order)
    assert info["history"] == 2 and info["similar"] == 2
    # the R2 part is a prefix of the R4 prompt up to the history section
    r2 = build_prompt("R2", report, chunks, repo)
    assert prompt.startswith(r2[:r2.index("Reply with SEARCH/REPLACE blocks only.")].rstrip())
    assert "### shopcart/cart.py :: Cart.subtotal" in prompt and "### shopcart/cart.py :: Cart.total" in prompt
    assert info["tokens"] <= repair.R4_INPUT_TOKENS


def test_trimming_drops_history_first_then_similar_and_never_the_target(repo, report, srcs, tmp_path) -> None:
    ctx = RagContext(KeywordEmbedder(), "HEAD", tmp_path / "rag", fake_history)
    chunks = ctx.select(repo, srcs, report)
    hist, sim = ctx.extras(repo, chunks, srcs)
    full, i_full = build_prompt_r4(report, chunks, repo, hist, sim)
    base = repair.estimate_tokens(SYSTEM) + repair.estimate_tokens(build_prompt_r4(report, chunks, repo, [], [])[0])

    def with_cap(cap):
        return build_prompt_r4(report, chunks, repo, hist, sim, cap=cap)

    # a cap that fits everything but the last history item: the second history item goes first
    p, i = with_cap(i_full["tokens"] - 1)
    assert (i["history"], i["similar"]) == (1, 2) and "earlier change 2" not in p and "earlier change 1" in p
    # a cap that fits the target plus one history item and no similar code beyond one chunk
    p, i = with_cap(base + 1)
    assert (i["history"], i["similar"]) == (0, 0)                   # nothing but the target fits
    # in between: history is exhausted before any similar chunk is dropped
    tok_no_hist = build_prompt_r4(report, chunks, repo, [], sim)[1]["tokens"]
    p, i = with_cap(tok_no_hist - 1)
    assert i["history"] == 0 and i["similar"] == 1 and "Cart.subtotal" in p and "Cart.total" not in p
    # the target chunk survives even an impossible cap
    p, i = with_cap(1)
    assert "### shopcart/pricing.py :: apply_discount" in p and (i["history"], i["similar"]) == (0, 0)


class Scripted:
    """Stand-in model: returns the same reply and records prompts (the HTTP layer is the only thing replaced)."""

    def __init__(self, reply):
        self.reply, self.prompts = reply, []

    def chat(self, system, user, max_completion_tokens=1500):
        from src.agents.llm import ChatResult
        self.prompts.append(user)
        return ChatResult(self.reply, {"total_tokens": 10}, "scripted", False)


def test_r4_agent_makes_one_call_with_the_r4_prompt_and_validates_the_patch(repo, report, srcs, tmp_path) -> None:
    reply = f"shopcart/pricing.py\n<<<<<<< SEARCH\n{BUG}\n=======\n{FIXED}\n>>>>>>> REPLACE"
    llm = Scripted(reply)
    ctx = RagContext(KeywordEmbedder(), "HEAD", tmp_path / "rag", fake_history)
    res = RepairAgent(llm, "R4", rag=ctx).run(repo, srcs, report, lambda files: (True, ""))
    assert res.accepted and res.action == "repair" and len(llm.prompts) == 1
    assert "Earlier commits that changed apply_discount" in llm.prompts[0]
    assert res.attempts[0].files["shopcart/pricing.py"].count(FIXED) == 1


# ---- exploratory reporting ----------------------------------------------------------------------
def _arm(ok: bool) -> dict:
    return {"accepted": ok, "edited_gt_file": ok, "edited_gt_function": ok, "exact_restore": ok, "overfit": False,
            "patch_in_distractor": False, "total_tokens": 4000, "attempts": 1}


def test_exploratory_section_has_r4_beside_r2_and_the_third_model_outside_the_family() -> None:
    import analysis.rq4_repair as rq4

    # 10 tasks: R2 fixes 6; R4 fixes 8 (R4 only: 3, R2 only: 1)
    r2 = [True] * 5 + [True] + [False] * 4
    r4 = [True] * 5 + [False] + [True] * 3 + [False]
    recs = [{"task_id": f"t{i}", "R1": _arm(False), "R2": _arm(r2[i]), "R3": _arm(r2[i]), "R4": _arm(r4[i]),
             "operator": "A", "repo": "r"} for i in range(10)]
    qwen = [{"task_id": f"t{i}", "R1": _arm(i < 2), "R2": _arm(i < 5), "R3": _arm(i < 5), "operator": "A", "repo": "r"}
            for i in range(5)]
    runs = {("openai/gpt-oss-20b", "standard"): recs, (rq4.THIRD_MODEL, "standard"): qwen}
    text = rq4.exploratory_section(runs, {(rq4.THIRD_MODEL, "standard"): "5 of 70 tasks done"}, {"standard": 70})
    assert "Exploratory (not pre-registered)" in text
    assert f"Third model {rq4.THIRD_MODEL}, standard variant (n = 5 of 70 tasks" in text and "5 of 70 tasks done" in text
    assert "Paired R2 vs R1: R2 only 3, R1 only 0" in text
    assert "R4 (R2 + retrieved fix history and similar code), openai/gpt-oss-20b, standard variant (n = 10" in text
    assert "Paired R4 vs R2: R4 only 3, R2 only 1" in text
    assert "| R4 | 10 | 8/10 (80.00%)" in text and "| R2 | 10 | 6/10 (60.00%)" in text
    # no exploratory cache at all: say so rather than print an empty section
    assert "nothing to report" in rq4.exploratory_section({}, {}, {})
