"""RQ5 analysis arithmetic (exploratory): scoring, the gap reading, Holm over the paired tests. Hand-computed."""

from __future__ import annotations

import analysis.rq5_retrieval as rq5


def task() -> dict:
    return {"task_id": "t", "repo": "r", "operator": "ARITH_SWAP", "gt_file": "a.py", "gt_function": "f",
            "distractor_files": ["d.py"], "hard_distractors": [{"file": "a.py", "function": "g"}]}


def test_score_task_ranks_hits_and_distractors() -> None:
    rank = {"L1": [("x.py", "h"), ("a.py", "f"), ("d.py", "k"), ("a.py", "g")],     # ground truth at rank 2
            "L4": [("a.py", "f"), ("a.py", "g"), ("d.py", "k")],                    # rank 1, two distractors in the top 3
            "L5": [("z.py", "q")]}                                                  # not retrieved
    rec = rq5.score_task(task(), rank)
    assert rec["L1"] == {"hit1": False, "hit3": True, "rr": 0.5, "distractor": 1, "n": 3}
    assert rec["L4"] == {"hit1": True, "hit3": True, "rr": 1.0, "distractor": 2, "n": 3}
    assert rec["L5"] == {"hit1": False, "hit3": False, "rr": 0.0, "distractor": 0, "n": 1}


def recs(hits: dict[str, list[bool]]) -> list[dict]:
    n = len(next(iter(hits.values())))
    return [{m: {"hit1": h[i], "hit3": h[i], "rr": float(h[i]), "distractor": 0, "n": 3} for m, h in hits.items()}
            for i in range(n)]


def test_gap_reading_when_smarter_retrieval_helps_and_when_it_does_not() -> None:
    # 10 tasks: L1 hits 4, L4 hits 8, L3 hits 6 -> L3 recovers 2 of the 4 (50%): "most"
    helps = recs({"L1": [True] * 4 + [False] * 6, "L2": [False] * 10, "L3": [True] * 6 + [False] * 4,
                  "L4": [True] * 8 + [False] * 2, "L5": [True] * 9 + [False]})
    s = rq5.gap_sentence("standard", helps)
    assert "L3 recovers 2 of the 4 tasks" in s and "(50%)" in s and "closes most of" in s
    worse = recs({"L1": [True] * 6 + [False] * 4, "L2": [False] * 10, "L3": [True] * 3 + [False] * 7,
                  "L4": [True] * 9 + [False], "L5": [True] * 9 + [False]})
    s = rq5.gap_sentence("hard", worse)
    assert "does not close the gap: L3 is 3 task(s) below L1, while knowing the change (L4) is 3 above it" in s


def test_paired_tests_use_exact_mcnemar_and_holm_over_all_four() -> None:
    std = recs({"L1": [False] * 8 + [True] * 2, "L3": [True] * 8 + [False] * 2, "L4": [True] * 10, "L5": [True] * 10,
                "L2": [False] * 10})
    text, tests = rq5.paired_tests({"standard": std, "hard": std})
    # L3 vs L1: 8 first-only, 2 second-only -> two-sided exact p = 2 * P(X <= 2 | n = 10) = 0.109375
    first, second, holm = tests[("standard", "L3", "L1")]
    assert (first, second) == (8, 2) and abs(holm - 0.4375) < 1e-9        # x4: Holm smallest p
    assert tests[("standard", "L5", "L4")][:2] == (0, 0)
    assert "Holm-adjusted (family of 4)" in text
