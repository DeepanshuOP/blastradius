"""Ask BlastRadius (exploratory, D-61): question routing, citation checking, time-safe retrieval, replay.

The failure-history source is built by the real loader from small parquet tables written to `tmp_path`
(`parsed_outcomes`, `instances_raw`, `outcomes`); only the vectors are absent (BM25 retrieval).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.agents.ask import (NOT_IN_CONTEXT, SYSTEM, AskAgent, build_user, check_citations, classify_question,
                            parse_citations, score_answers)
from src.agents.llm import GroqLLM
from src.agents.llm_cache import CacheMiss, LLMCache
from src.features.online import RankedTest
from src.rag.knowledge import Knowledge, code_docs, doc_sections, load_failure_docs, load_repo_docs

SAMPLE = Path(__file__).resolve().parents[1] / "src" / "agents" / "demo" / "sample_repo"


# ---- routing ------------------------------------------------------------------------------------
@pytest.mark.parametrize("q,want", [
    ("Why is test_welcome10_takes_ten_percent failing?", "test-failure"),
    ("Has this failure happened before?", "history"),
    ("What is at risk if I change pricing.py?", "impact"),
    ("How do I run the suite locally?", "general"),
    ("Has test_code_is_case_insensitive failed previously?", "history"),
    ("Which tests would break if I edit shopcart/cart.py?", "impact"),
    ("test_total raised an AssertionError", "test-failure"),
])
def test_question_routing(q, want) -> None:
    assert classify_question(q) == want


# ---- citations ----------------------------------------------------------------------------------
def test_citation_parser_and_faithfulness_check() -> None:
    ans = "Discount is applied first [S1], then tax [S3]. See also [S1] and [S12]."
    assert parse_citations(ans) == [1, 3, 12]
    assert check_citations(ans, 8) == ([1, 3, 12], False)          # S12 was never retrieved
    assert check_citations("Applied first [S1][S2].", 2) == ([1, 2], True)
    assert check_citations(NOT_IN_CONTEXT, 8) == ([], True)         # an abstention cites nothing and invents nothing
    assert check_citations("[S0] is not a context item", 8)[1] is False


# ---- knowledge sources --------------------------------------------------------------------------
@pytest.fixture()
def interim(tmp_path) -> Path:
    d = tmp_path / "interim"
    d.mkdir()
    pd.DataFrame({
        "run_id": [1, 2, 3, 4, 4], "job_id": [10, 20, 30, 40, 41],
        "test_id": ["tests.test_a::test_x", "tests.test_a::test_x", "tests.test_b::test_y", "tests.test_a::test_x",
                    "tests.test_a::test_z"],
        "repo": ["org__r"] * 5, "status": ["fail", "fail", "error", "fail", "pass"],
        "failure_message": ["AssertionError: 1 != 2", "AssertionError: 3 != 4", "TimeoutError: connection timed out",
                            "AssertionError: 5 != 6", None],
    }).to_parquet(d / "parsed_outcomes.parquet")
    pd.DataFrame({
        "run_id": [1, 2, 3, 4], "run_started_at": ["2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z",
                                                  "2026-01-03T00:00:00Z", "2026-01-04T00:00:00Z"],
    }).to_parquet(d / "instances_raw.parquet")
    pd.DataFrame({"run_id": [1, 1, 2, 2, 3, 3], "test_id": ["tests.test_a::test_x"] * 2 + ["tests.test_a::test_x"] * 2
                  + ["tests.test_b::test_y"] * 2, "split": ["strict", "all", "all", "relaxed", "all", "relaxed"]}) \
        .to_parquet(d / "outcomes.parquet")
    return d


def test_failure_docs_have_message_date_repo_and_label(interim) -> None:
    docs = load_failure_docs(interim)
    assert [(d.meta["run_id"], d.meta["test_id"], d.meta["label"], d.meta["date"]) for d in docs] == [
        (1, "tests.test_a::test_x", "mine", "2026-01-01"),        # strict
        (2, "tests.test_a::test_x", "flaky", "2026-01-02"),       # relaxed minus strict
        (3, "tests.test_b::test_y", "flaky", "2026-01-03"),
        (4, "tests.test_a::test_x", "unknown", "2026-01-04"),     # base outcome not known
    ]
    assert all(d.source == "failure" and d.ts is not None for d in docs)       # the pass row and the empty message are out
    assert docs[0].text.startswith("tests.test_a::test_x | org__r | 2026-01-01 | mine\nAssertionError: 1 != 2")


def test_retrieval_is_time_safe_strictly_before_the_query(interim) -> None:
    kb = Knowledge(load_failure_docs(interim), dense=False)
    docs = {d.meta["run_id"]: d for d in kb.docs}
    t3 = docs[3].ts
    hits = kb.search("AssertionError", k=8, per_source=8, before_ts=t3)
    assert {h.meta["run_id"] for h in hits} == {1, 2}                      # run 3 is AT the query time: excluded
    assert all(h.ts < t3 for h in hits)
    assert kb.search("AssertionError", k=8, per_source=8, before_ts=docs[1].ts) == []   # nothing earlier than the first
    # unrestricted, run 4 comes back too
    assert {h.meta["run_id"] for h in kb.search("AssertionError", k=8, per_source=8)} == {1, 2, 4}


def test_per_source_cap_and_source_filter(interim) -> None:
    docs = load_failure_docs(interim) + code_docs(SAMPLE) + load_repo_docs(SAMPLE)
    kb = Knowledge(docs, dense=False)
    hits = kb.search("discount percent tax AssertionError", k=8, per_source=2)
    counts = {s: sum(1 for h in hits if h.source == s) for s in ("code", "failure", "doc")}
    assert max(counts.values()) <= 2 and len(hits) <= 6
    only = kb.search("discount percent", k=8, per_source=4, sources=["code"])
    assert only and {h.source for h in only} == {"code"} and only[0].qualname == "apply_discount"


def test_doc_sections_split_at_headings() -> None:
    text = "# Title\nintro\n\n## Setup\nrun it\n\n## Use\nuse it\n"
    got = [(d.qualname, d.start, d.end) for d in doc_sections(text, "README.md")]
    assert got == [("Title", 1, 3), ("Setup", 4, 6), ("Use", 7, 8)]


# ---- the agent ----------------------------------------------------------------------------------
class Offline:
    """No `chat`: the agent must degrade to retrieval only."""


def _kb(interim) -> Knowledge:
    return Knowledge(load_failure_docs(interim) + code_docs(SAMPLE) + load_repo_docs(SAMPLE), dense=False)


def test_no_model_returns_retrieval_only_with_citations(interim) -> None:
    res = AskAgent(_kb(interim), SAMPLE, Offline()).ask("Why is test_x failing with AssertionError?")
    assert res.qtype == "test-failure" and res.answer is None and res.faithful is None
    assert 1 <= len(res.citations) <= 8 and res.citations[0].id == "S1"
    assert {c.source for c in res.citations} <= {"code", "failure", "doc"}
    assert "no model configured: retrieval only" in res.notes


def test_impact_question_adds_the_e1_block_as_the_last_item(interim) -> None:
    seen = {}

    def ranker(repo, changed, n_lines, explain_top=3):
        seen["changed"] = changed
        return [RankedTest(f"tests/test_{i}.py", 1.0 - i / 10, [f"hist_fail={i} (+0.{i})"]) for i in range(7)]

    res = AskAgent(_kb(interim), SAMPLE, Offline(), ranker).ask("What is at risk if I change pricing.py?")
    assert res.qtype == "impact" and seen["changed"] == ["shopcart/pricing.py"]
    last = res.context[-1]
    assert last["source"] == "e1" and res.citations[-1].source == "e1" and len(res.context) <= 8
    assert last["text"].count("\n") == 5 and "1. tests/test_0.py score 1.000 because hist_fail=0 (+0.0)" in last["text"]
    assert "5. tests/test_4.py" in last["text"] and "tests/test_5.py" not in last["text"]   # top 5 only


def test_impact_without_a_named_file_says_why_no_ranker_block(interim) -> None:
    res = AskAgent(_kb(interim), SAMPLE, Offline()).ask("What is at risk if I change something?")
    assert res.qtype == "impact" and all(c.source != "e1" for c in res.citations)
    assert any("no tracked source file named" in n for n in res.notes)


def test_replay_of_a_recorded_answer(interim, tmp_path) -> None:
    kb = _kb(interim)
    q = "Why is test_welcome10_takes_ten_percent failing?"
    probe = AskAgent(kb, SAMPLE, None).ask(q)
    user = build_user(q, probe.context)
    cache_path = tmp_path / "ask.jsonl"
    llm = GroqLLM(api_key="replay", model="openai/gpt-oss-20b", cache=LLMCache(cache_path), ledger=tmp_path / "u.jsonl")
    key = llm.request_key(SYSTEM, user, 800)
    LLMCache(cache_path).put(key, {"system": SYSTEM, "messages": [{"role": "user", "content": user}],
                                   "params": llm.request_params(800), "model": "openai/gpt-oss-20b"},
                             "The discount is applied in apply_discount [S1]; the failure is an assertion [S2].",
                             {"total_tokens": 321}, "openai/gpt-oss-20b")
    replay = GroqLLM(api_key="replay", model="openai/gpt-oss-20b", cache=LLMCache(cache_path, replay=True),
                     ledger=tmp_path / "u2.jsonl")
    res = AskAgent(kb, SAMPLE, replay).ask(q)
    assert res.answer.startswith("The discount is applied") and res.from_cache and res.tokens == 321
    assert res.cited == [1, 2] and res.faithful is True
    assert score_answers([res]) == {"answered": 1, "all_citations_real": 1, "all_citations_real_or_none": 1,
                                    "cites_at_least_one": 1, "abstained": 0}
    # a different question is a miss in replay mode, never a network call
    with pytest.raises(CacheMiss):
        AskAgent(kb, SAMPLE, replay).ask("Why is test_other failing?")


def test_history_questions_search_failure_history_only(interim) -> None:
    res = AskAgent(_kb(interim), SAMPLE, Offline()).ask("Has a connection timed out before in tests.test_b::test_y?")
    assert res.qtype == "history"
    assert res.citations and {c.source for c in res.citations} == {"failure"}
    # BM25 keeps only documents that share a token with the question; the only such failure is run 3's timeout
    assert [c.ref for c in res.citations] == ["run 3 (org__r, 2026-01-03)"]
