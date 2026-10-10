"""Paired statistics for the E1/E2 comparisons (ROADMAP §32): Cliff's delta, Holm, bootstrap CI."""

from __future__ import annotations

import numpy as np

__all__ = ["cliffs_delta", "cliffs_label", "holm_adjust", "bootstrap_ci", "wilcoxon_p"]


def cliffs_delta(x, y) -> float:
    """Cliff's delta: `(#(x_i > y_j) - #(x_i < y_j)) / (n_x * n_y)` over all pairs.

    Positive when `x` tends to be larger than `y`; in [-1, 1].
    """
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if x.size == 0 or y.size == 0:
        return 0.0
    diff = x[:, None] - y[None, :]
    return float(((diff > 0).sum() - (diff < 0).sum()) / (x.size * y.size))


def cliffs_label(delta: float) -> str:
    """Romano et al. magnitude: |d| < 0.147 negligible, < 0.33 small, < 0.474 medium, else large."""
    a = abs(delta)
    return "negligible" if a < 0.147 else "small" if a < 0.33 else "medium" if a < 0.474 else "large"


def holm_adjust(pvalues: list[float]) -> list[float]:
    """Holm-Bonferroni adjusted p-values, returned in the input order.

    Step-down: sort ascending, `adj_(i) = max over j <= i of min(1, (m - j + 1) * p_(j))`.
    """
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvalues[i]))
        adj[i] = running
    return adj


def bootstrap_ci(values, n_boot: int = 10_000, seed: int = 0, alpha: float = 0.05) -> tuple[float, float]:
    """Percentile bootstrap CI of the mean (resampling instances with replacement)."""
    v = np.asarray(values, dtype=float)
    if v.size == 0:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    means = v[rng.integers(0, v.size, size=(n_boot, v.size))].mean(axis=1)
    return (float(np.quantile(means, alpha / 2)), float(np.quantile(means, 1 - alpha / 2)))


def wilcoxon_p(x, y) -> float:
    """Two-sided Wilcoxon signed-rank p on paired samples (`zero_method="zsplit"`); 1.0 if all pairs tie."""
    from scipy.stats import wilcoxon

    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if np.all(x == y):
        return 1.0
    return float(wilcoxon(x, y, zero_method="zsplit", alternative="two-sided").pvalue)
