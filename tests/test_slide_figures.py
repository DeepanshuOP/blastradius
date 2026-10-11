"""Slide-figure helpers: Wilson interval against hand-computed values, and the rq5 table parser on a hand-written excerpt."""

from __future__ import annotations

import pytest

from analysis.slide_figures import arm_counts, parse_hit3, title_n, wilson

MD = """# RQ5

## Localization: is the seeded function among the top 3 chunks?

### Standard variant (n = 70)

| mode | hit@1 | hit@3 | MRR | top-3 chunks that are distractors |
|---|---|---|---|---|
| L1 BM25, whole repo (= R1) | 32/70 (45.71%) | 46/70 (65.71%) | 0.581 | 48/210 (22.86%) |
| L4 BM25, functions touched by the diff (= R2) | 63/70 (90.00%) | 69/70 (98.57%) | 0.940 | 47/117 (40.17%) |

### Hard variant (n = 70)

| mode | hit@1 | hit@3 | MRR | top-3 chunks that are distractors |
|---|---|---|---|---|
| L1 BM25, whole repo (= R1) | 32/70 (45.71%) | 46/70 (65.71%) | 0.581 | 75/210 (35.71%) |
| L5 hybrid (RRF), functions touched by the diff | 30/70 (42.86%) | 58/70 (82.86%) | 0.637 | 151/210 (71.90%) |

## Failure-history retrieval

| retriever | hit@1 | hit@5 | MRR |
|---|---|---|---|
| BM25 | 55/90 (61.11%) | 69/90 (76.67%) | 0.672 |
"""


def test_wilson_matches_hand_computed_values() -> None:
    lo, hi = wilson(37, 47)       # 37/47 = 0.78723: centre 0.7657, half 0.1146 (z = 1.96)
    assert lo == pytest.approx(0.6511, abs=1e-3)
    assert hi == pytest.approx(0.8803, abs=1e-3)
    assert wilson(0, 10)[0] == 0.0 and wilson(10, 10)[1] == pytest.approx(1.0)
    assert wilson(0, 0) == (0.0, 1.0)


def test_parse_hit3_reads_hit3_not_hit1_and_stops_at_the_next_section() -> None:
    assert parse_hit3(MD) == {"standard": {"L1": (46, 70), "L4": (69, 70)},
                              "hard": {"L1": (46, 70), "L5": (58, 70)}}


def test_arm_counts_and_title_n() -> None:
    recs = [{"R1": {"accepted": True}, "R2": {"accepted": True}, "R3": {"accepted": True}},
            {"R1": {"accepted": False}, "R2": {"accepted": True}, "R3": {"accepted": True}}]
    counts = {"openai/gpt-oss-120b": arm_counts(recs), "openai/gpt-oss-20b": arm_counts(recs[:1])}
    assert counts["openai/gpt-oss-120b"] == {"R1": (1, 2), "R2": (2, 2), "R3": (2, 2)}
    assert title_n(counts) == "n = 2 (120b), 1 (20b)"
    assert title_n({"a/b": counts["openai/gpt-oss-120b"]}) == "n = 2 per model"
