"""Ranking metrics against hand-computed examples."""

import math

import pytest

from src.eval import metrics as m

# 10 candidates a..j; failing files are c (rank 3) and h (rank 8).
RANKED = list("abcdefghij")
GT = {"c", "h"}


def test_recall_at_k() -> None:
    assert m.recall_at_k(RANKED, GT, 1) == 0.0
    assert m.recall_at_k(RANKED, GT, 3) == 0.5
    assert m.recall_at_k(RANKED, GT, 8) == 1.0
    assert m.recall_at_k(RANKED, set(), 5) == 0.0


def test_recall_at_fraction() -> None:
    assert m.recall_at_fraction(RANKED, GT, 0.1) == 0.0   # k = ceil(1.0) = 1
    assert m.recall_at_fraction(RANKED, GT, 0.2) == 0.0   # k = 2
    assert m.recall_at_fraction(RANKED, GT, 0.3) == 0.5   # k = 3
    assert m.recall_at_fraction(RANKED, GT, 0.75) == 1.0  # k = ceil(7.5) = 8


def test_precision_ap_rr() -> None:
    assert m.precision_at_k(RANKED, GT, 5) == pytest.approx(1 / 5)
    assert m.precision_at_k(RANKED, GT, 10) == pytest.approx(2 / 10)
    # AP = (1/3 + 2/8) / 2
    assert m.average_precision(RANKED, GT) == pytest.approx((1 / 3 + 2 / 8) / 2)
    assert m.reciprocal_rank(RANKED, GT) == pytest.approx(1 / 3)
    assert m.reciprocal_rank(RANKED, {"zzz"}) == 0.0


def test_apfd() -> None:
    # 1 - (3 + 8) / (10 * 2) + 1 / 20 = 1 - 0.55 + 0.05
    assert m.apfd(RANKED, GT) == pytest.approx(0.5)
    assert m.apfd(RANKED, {"a"}) == pytest.approx(1 - 1 / 10 + 1 / 20)
    assert m.apfd(RANKED, {"j"}) == pytest.approx(1 / 20)
    assert m.apfd(RANKED, {"missing"}) == 0.0


def test_first_fail_and_full_recall_fraction() -> None:
    assert m.first_fail_position(RANKED, GT) == 3
    assert m.first_fail_position(RANKED, {"q"}) is None
    assert m.suite_fraction_for_full_recall(RANKED, GT) == pytest.approx(0.8)
    assert m.suite_fraction_for_full_recall(RANKED, {"c", "q"}) is None


def test_ndcg() -> None:
    dcg = 1 / math.log2(4) + 1 / math.log2(9)
    ideal = 1 / math.log2(2) + 1 / math.log2(3)
    assert m.ndcg_at_k(RANKED, GT, 10) == pytest.approx(dcg / ideal)
    assert m.ndcg_at_k(RANKED, GT, 2) == 0.0


def test_baseline_rank_ties_by_path_and_bm25() -> None:
    import numpy as np

    from src.eval.baselines import bm25_scores, path_token_list, rank

    assert rank(["b", "a", "c"], np.array([1.0, 1.0, 2.0])) == ["c", "a", "b"]
    assert path_token_list("src/UserService_test.py") == ["src", "user", "service", "test", "py"]
    # corpus: d0=[a,b], d1=[b,c], d2=[c,c]; query [a]. N=3 df(a)=1 -> idf = ln(1 + 2.5/1.5); avgdl=2;
    # d0: tf=1, norm = 1.2 * (0.25 + 0.75 * 1) = 1.2 -> idf * 1 * 2.2 / 2.2 = idf
    s = bm25_scores([["a", "b"], ["b", "c"], ["c", "c"]], ["a"])
    assert s[0] == pytest.approx(math.log(1 + 2.5 / 1.5))
    assert s[1] == 0.0 and s[2] == 0.0
