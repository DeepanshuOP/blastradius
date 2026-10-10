"""Statistics helpers against hand-computed values."""

import pytest

from src.eval import stats as s


def test_cliffs_delta_hand_computed() -> None:
    # x = [3, 4], y = [1, 4, 5]: pairs (3,1)+ (3,4)- (3,5)- (4,1)+ (4,4)0 (4,5)-  -> (2 - 3) / 6
    assert s.cliffs_delta([3, 4], [1, 4, 5]) == pytest.approx(-1 / 6)
    assert s.cliffs_delta([5, 6], [1, 2]) == 1.0
    assert s.cliffs_delta([1, 1], [1, 1]) == 0.0


def test_cliffs_labels() -> None:
    assert [s.cliffs_label(d) for d in (0.1, 0.2, 0.4, 0.5, -0.5)] == ["negligible", "small", "medium", "large", "large"]
    assert s.cliffs_label(0.147) == "small"  # the threshold itself is not negligible


def test_holm() -> None:
    # sorted 0.01, 0.02, 0.04 with m=3: 0.03, max(0.03, 0.04)=0.04, max(0.04, 0.04)=0.04
    assert s.holm_adjust([0.04, 0.01, 0.02]) == pytest.approx([0.04, 0.03, 0.04])
    assert s.holm_adjust([0.5, 0.6]) == pytest.approx([1.0, 1.0])


def test_bootstrap_is_seeded_and_brackets_mean() -> None:
    v = [0.0, 1.0] * 10
    lo, hi = s.bootstrap_ci(v, n_boot=2000, seed=0)
    assert (lo, hi) == s.bootstrap_ci(v, n_boot=2000, seed=0)
    assert lo < 0.5 < hi


def test_wilcoxon_all_ties_is_one() -> None:
    assert s.wilcoxon_p([1, 2, 3], [1, 2, 3]) == 1.0
    assert s.wilcoxon_p([1, 2, 3, 4, 5, 6], [0, 0, 0, 0, 0, 0]) < 0.05
