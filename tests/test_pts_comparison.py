"""Base-paper metrics (TestRecall, ChangeRecall, SelectionRate) against values computed by hand.

Three changes, candidates ranked best-first:
  C1: a1..a10, failing {a2, a9};            all-split failing {a2, a9, a5}
  C2: b1..b4,  failing {b1};                all-split failing {b1, b3}
  C3: c1..c20, failing {c3, c4, c20};       all-split failing {c3, c4, c20, c7}
"""

from fractions import Fraction

import pytest

from analysis.pts_comparison import (Change, change_recall, failing_recall, mean_runs, min_rate, select_size,
                                     selection_rate)


def changes() -> list[Change]:
    return [
        Change([f"a{i}" for i in range(1, 11)], frozenset({"a2", "a9"}), frozenset({"a2", "a9", "a5"})),
        Change([f"b{i}" for i in range(1, 5)], frozenset({"b1"}), frozenset({"b1", "b3"})),
        Change([f"c{i}" for i in range(1, 21)], frozenset({"c3", "c4", "c20"}), frozenset({"c3", "c4", "c20", "c7"})),
    ]


def test_select_size_is_exact() -> None:
    assert select_size(10, Fraction("0.2")) == 2          # 2.0, not 3
    assert select_size(4, Fraction("0.2")) == 1           # ceil(0.8)
    assert select_size(100, Fraction("0.07")) == 7        # the float product is 7.000000000000001
    assert select_size(20, Fraction("0.1")) == 2


def test_rate_020() -> None:
    # sizes 2, 1, 4 -> hits 1 (a2), 1 (b1), 2 (c3, c4) of 2, 1, 3 failing
    r, cs = Fraction("0.2"), changes()
    assert failing_recall(cs, rate=r) == pytest.approx(4 / 6)
    assert failing_recall(cs, rate=r, macro=True) == pytest.approx((1 / 2 + 1 + 2 / 3) / 3)
    assert change_recall(cs, rate=r) == pytest.approx(1.0)
    assert selection_rate(cs, rate=r) == pytest.approx(7 / 34)


def test_rate_010() -> None:
    # sizes 1, 1, 2 -> hits 0, 1, 0
    r, cs = Fraction("0.1"), changes()
    assert failing_recall(cs, rate=r) == pytest.approx(1 / 6)
    assert failing_recall(cs, rate=r, macro=True) == pytest.approx(1 / 3)
    assert change_recall(cs, rate=r) == pytest.approx(1 / 3)
    assert selection_rate(cs, rate=r) == pytest.approx(4 / 34)


def test_rate_050() -> None:
    # sizes 5, 2, 10 -> hits 1 (a2), 1 (b1), 2 (c3, c4)
    r, cs = Fraction("0.5"), changes()
    assert failing_recall(cs, rate=r) == pytest.approx(4 / 6)
    assert selection_rate(cs, rate=r) == pytest.approx(0.5)


def test_with_flakes() -> None:
    # rate 0.2 selects a1 a2 / b1 / c1..c4: all-split hits 1 (a2), 1 (b1), 2 (c3, c4) of 3, 2, 4 failing
    r, cs = Fraction("0.2"), changes()
    assert failing_recall(cs, rate=r, all_labels=True) == pytest.approx(4 / 9)
    assert failing_recall(cs, rate=r, all_labels=True, macro=True) == pytest.approx((1 / 3 + 1 / 2 + 2 / 4) / 3)


def test_top_k() -> None:
    cs = changes()
    assert change_recall(cs, k=1) == pytest.approx(1 / 3)  # only b1 is first
    assert change_recall(cs, k=3) == pytest.approx(1.0)    # a2, b1, c3 are within the top 3
    assert selection_rate(cs, k=3) == pytest.approx(9 / 34)
    assert selection_rate(cs, k=10) == pytest.approx(24 / 34)  # 10 + 4 (C2 has only 4 candidates) + 10


def test_min_rate() -> None:
    cs = [changes()]
    # all six failing files need a9 (size 9 of 10 -> rate 0.9) and c20 (size 20 of 20 -> rate 1); 5/6 < 0.95
    assert min_rate(cs, failing_recall, Fraction("0.95")) == Fraction(1)
    # one failing file per change: a2 needs size 2 of 10 (any rate > 0.1), b1 size 1 of 4, c3 size 3 of 20
    # (any rate > 0.1). At exactly 0.1 the sizes are 1, 1, 2 (C1 misses), so the smallest whole-file rate k/n
    # that works is 3/20 = 0.15 (sizes 2, 1, 3).
    assert min_rate(cs, change_recall, Fraction("0.999")) == Fraction(3, 20)
    # 4 of 6 hit at rate 0.2 (checked above), and 3 of 6 at 0.15 -> sizes 2, 1, 3: a2, b1, c3 only
    assert min_rate(cs, failing_recall, Fraction("0.6")) == Fraction(1, 5)


def test_mean_over_runs() -> None:
    worse = [Change(list(reversed(c.ranked)), c.failing, c.failing_all) for c in changes()]
    r = Fraction("0.2")
    # reversed ranking at rate 0.2: C1 selects a10 a9 -> 1 hit; C2 selects b4 -> 0; C3 selects c20..c17 -> 1 hit
    assert failing_recall(worse, rate=r) == pytest.approx(2 / 6)
    assert mean_runs([changes(), worse], failing_recall, rate=r) == pytest.approx((4 / 6 + 2 / 6) / 2)
