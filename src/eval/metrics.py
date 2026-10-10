"""Ranking metrics at test-file level for one change.

Every function takes `ranked` (candidate test files, best first) and `gt` (the
set of files that really failed). Ground-truth files absent from `ranked` count
as never retrieved; E1 candidates always contain them (`build_e1_features.py`
asserts 100%). All values are floats in [0, 1] unless stated.
"""

from __future__ import annotations

import math
from typing import Sequence

__all__ = ["recall_at_k", "recall_at_fraction", "precision_at_k", "average_precision", "reciprocal_rank",
           "apfd", "first_fail_position", "suite_fraction_for_full_recall", "ndcg_at_k", "positions"]


def positions(ranked: Sequence[str], gt: set[str]) -> list[int]:
    """1-based ranks of the ground-truth files found in `ranked`, ascending."""
    return [i for i, f in enumerate(ranked, 1) if f in gt]


def recall_at_k(ranked: Sequence[str], gt: set[str], k: int) -> float:
    """`|top-k & gt| / |gt|`. 0.0 for an empty `gt`."""
    return len(set(ranked[:k]) & gt) / len(gt) if gt else 0.0


def recall_at_fraction(ranked: Sequence[str], gt: set[str], frac: float) -> float:
    """Recall after running `ceil(frac * n)` tests (at least one) of the `n` candidates."""
    k = max(1, math.ceil(frac * len(ranked))) if ranked else 0
    return recall_at_k(ranked, gt, k)


def precision_at_k(ranked: Sequence[str], gt: set[str], k: int) -> float:
    """`|top-k & gt| / min(k, n)`. 0.0 when `ranked` is empty."""
    top = ranked[:k]
    return len(set(top) & gt) / len(top) if top else 0.0


def average_precision(ranked: Sequence[str], gt: set[str]) -> float:
    """`(1 / |gt|) * sum over hits of precision@position`. Missing ground truth contributes 0."""
    if not gt:
        return 0.0
    hits, total = 0, 0.0
    for i, f in enumerate(ranked, 1):
        if f in gt:
            hits += 1
            total += hits / i
    return total / len(gt)


def reciprocal_rank(ranked: Sequence[str], gt: set[str]) -> float:
    """`1 / position of the first ground-truth file`; 0.0 if none is ranked."""
    pos = positions(ranked, gt)
    return 1.0 / pos[0] if pos else 0.0


def first_fail_position(ranked: Sequence[str], gt: set[str]) -> int | None:
    """1-based position of the first failing test file, or None."""
    pos = positions(ranked, gt)
    return pos[0] if pos else None


def apfd(ranked: Sequence[str], gt: set[str]) -> float:
    """Average Percentage of Faults Detected over the ranked list.

    `APFD = 1 - sum(TF_i) / (n * m) + 1 / (2n)` with `n` candidates, `m` failing
    files and `TF_i` the position of the i-th failing file. Here a "fault" is a
    failing test file. 1.0 means every failing file is first; for `m = 1` and the
    failing file last it is `1/(2n)`.

    Returns:
        The APFD, or 0.0 if `ranked` is empty, `gt` is empty, or a ground-truth
        file is missing from `ranked` (not defined; E1 candidates always contain them).
    """
    n, pos = len(ranked), positions(ranked, gt)
    m = len(gt)
    if n == 0 or m == 0 or len(pos) != m:
        return 0.0
    return 1.0 - sum(pos) / (n * m) + 1.0 / (2 * n)


def suite_fraction_for_full_recall(ranked: Sequence[str], gt: set[str]) -> float | None:
    """Fraction of the candidate list that must run to catch every failing file: `max position / n`.

    Returns:
        None if some ground-truth file is not in `ranked`.
    """
    pos = positions(ranked, gt)
    if not ranked or not gt or len(pos) != len(gt):
        return None
    return pos[-1] / len(ranked)


def ndcg_at_k(ranked: Sequence[str], gt: set[str], k: int = 10) -> float:
    """Binary-gain NDCG@k: `DCG / IDCG` with `DCG = sum 1/log2(pos+1)` over hits in the top k."""
    dcg = sum(1.0 / math.log2(i + 1) for i, f in enumerate(ranked[:k], 1) if f in gt)
    ideal = sum(1.0 / math.log2(i + 1) for i in range(1, min(len(gt), k) + 1))
    return dcg / ideal if ideal else 0.0
