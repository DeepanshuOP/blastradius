"""E1 rankers measured with the metrics of the base paper (Machalica et al., "Predictive Test Selection", ICSE-SEIP 2019).

Offline, deterministic, no network, no LLM, no training. Unit = test FILE; the candidates of a change are all
test files of the repo at that commit, as in E1 (`analysis/build_e1_features.py`).

* TestRecall(s)       = sum over changes |selected & failing| / sum |failing|   (micro; macro mean also reported)
* ChangeRecall(s)     = share of changes with >= 1 failing file selected
* SelectionRate(s)    = sum |selected| / sum |candidates|
* TestRecallWithFlakes = TestRecall with failing = every file bound from the `all` outcome split
                        (strict + inherited + flaky), restricted to the change's candidates like the strict label.

Selecting at rate r takes the top ceil(r * |candidates|) files of each change, computed in exact rational
arithmetic. Reads the test-split ranked lists that `analysis/rq2_predictor.py` wrote to
`data/processed/e1_scores.parquet` (D-57 split, 148 instances; ours/B6/B7 over seeds 0-4, B0/B2/B4 deterministic)
and recomputes B1 over its 20 seeds with `src.eval.baselines.score_b1`; the macro/micro values of seeded methods
are the mean over seeds. Writes `paper/generated/pts_comparison.md`.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd

from analysis import paper_md
from src.eval import baselines as B

FEATURES = Path("data/processed/e1_features.parquet")
SCORES = Path("data/processed/e1_scores.parquet")
OUTCOMES = Path("data/interim/outcomes.parquet")
BINDING = Path("data/interim/binding.parquet")
INSTANCES = Path("data/interim/instances_raw.parquet")
EXPECTED_TEST_INSTANCES = 148
RATES = (Fraction("0.05"), Fraction("0.10"), Fraction("0.15"), Fraction("0.20"), Fraction("0.33"), Fraction("0.50"))
TOP_K = (1, 3, 5, 10, 20)
TARGET_TEST_RECALL = Fraction("0.95")
TARGET_CHANGE_RECALL = Fraction("0.999")
SEEDED = {"B1": tuple(B.RANDOM_SEEDS), "B6": (0, 1, 2, 3, 4), "B7": (0, 1, 2, 3, 4), "ours": (0, 1, 2, 3, 4)}
METHODS = ("ours", "B7", "B6", "B4", "B2", "B0", "B1")
NAMES = {"ours": "BlastRadius ranker", "B7": "B7 readily-available-info LTR", "B6": "B6 history-only LTR",
         "B4": "B4 failure history", "B2": "B2 changed test files", "B0": "B0 retest-all (alphabetical)",
         "B1": "B1 random (mean of 20 seeds)"}


@dataclass
class Change:
    """One change: candidates best-first and the set of files that failed (and, optionally, all that failed)."""

    ranked: list[str]
    failing: frozenset[str]
    failing_all: frozenset[str] | None = None
    _cum: dict = field(default_factory=dict, repr=False, compare=False)

    def hits(self, size: int, all_labels: bool = False) -> int:
        """Failing files among the top `size` candidates."""
        truth = self.failing_all if all_labels else self.failing
        assert truth is not None
        if all_labels not in self._cum:
            self._cum[all_labels] = np.cumsum([f in truth for f in self.ranked], dtype=np.int64)
        return int(self._cum[all_labels][size - 1]) if size > 0 else 0

    def n_fail(self, all_labels: bool = False) -> int:
        """Failing files that are among the candidates."""
        truth = self.failing_all if all_labels else self.failing
        assert truth is not None
        return len(truth)


def select_size(n_candidates: int, rate: Fraction) -> int:
    """`ceil(rate * n_candidates)`, exact (no float rounding: `0.07 * 100` is `7.000000000000001`)."""
    return -((-rate.numerator * n_candidates) // rate.denominator)


def failing_recall(changes: list[Change], rate: Fraction | None = None, k: int | None = None,
                all_labels: bool = False, macro: bool = False) -> float:
    """Micro (default) or macro TestRecall at a selection rate or a per-change top-`k`."""
    hit, fail, ratios = 0, 0, []
    for c in changes:
        size = min(k, len(c.ranked)) if k is not None else select_size(len(c.ranked), rate)
        h, f = c.hits(size, all_labels), c.n_fail(all_labels)
        hit, fail = hit + h, fail + f
        if f:
            ratios.append(h / f)
    if macro:
        return float(np.mean(ratios)) if ratios else float("nan")
    return hit / fail if fail else float("nan")


def change_recall(changes: list[Change], rate: Fraction | None = None, k: int | None = None) -> float:
    """Share of changes with at least one failing file selected."""
    ok = 0
    for c in changes:
        size = min(k, len(c.ranked)) if k is not None else select_size(len(c.ranked), rate)
        ok += c.hits(size) >= 1
    return ok / len(changes)


def selection_rate(changes: list[Change], rate: Fraction | None = None, k: int | None = None) -> float:
    """Sum of selected files over sum of candidates."""
    sel = sum(min(k, len(c.ranked)) if k is not None else select_size(len(c.ranked), rate) for c in changes)
    return sel / sum(len(c.ranked) for c in changes)


def mean_runs(runs: list[list[Change]], fn, **kw) -> float:
    """Mean of a metric over the runs (seeds) of a method."""
    return float(np.mean([fn(r, **kw) for r in runs]))


def min_rate(runs: list[list[Change]], fn, target: Fraction, **kw) -> Fraction | None:
    """Smallest rate (the same for every change) whose seed-mean metric is >= `target`; None if even 1.0 misses.

    The selection size `ceil(r * n)` is constant on each interval `(j / n, (j + 1) / n]`, so the metric is a
    non-decreasing step function that changes only just above a fraction `k / n`; the search runs over those
    fractions (binary search, exact) and returns the smallest `k / n` at which the target holds. Any rate
    above the previous fraction in that set selects the same files.
    """
    steps = sorted({Fraction(k, len(c.ranked)) for c in runs[0] for k in range(1, len(c.ranked) + 1)})
    ok = lambda r: Fraction(mean_runs(runs, fn, rate=r, **kw)).limit_denominator(10**9) >= target  # noqa: E731
    if not ok(steps[-1]):
        return None
    lo, hi = 0, len(steps) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        lo, hi = (lo, mid) if ok(steps[mid]) else (mid + 1, hi)
    return steps[lo]


def _fmt(x: float) -> str:
    return f"{x:.3f}"


def load_changes() -> tuple[dict[str, list[list[Change]]], dict]:
    """Test-split changes per method (one run per seed) with strict and all-split failing files."""
    feats = pd.read_parquet(FEATURES, columns=["repo", "run_id", "split", "label", "test_file"])
    feats = feats[feats["split"] == "test"].reset_index(drop=True)
    idx = feats.groupby(["repo", "run_id"], sort=False).indices
    keys = list(idx)
    assert len(keys) == EXPECTED_TEST_INSTANCES, f"{len(keys)} test instances, expected {EXPECTED_TEST_INSTANCES}"

    # strict failing files from the label column; all-split failing files from the `all` outcome split
    outcomes = pd.read_parquet(OUTCOMES)
    runs = pd.read_parquet(INSTANCES, columns=["run_id", "repo"]).drop_duplicates("run_id")
    binding = pd.read_parquet(BINDING)
    bound = binding[binding["status"] == "exact"].set_index(["repo", "test_id"])["resolved_path"].to_dict()
    out = outcomes.merge(runs, on="run_id", how="inner")
    out["path"] = [bound.get(k) for k in zip(out["repo"], out["test_id"])]
    out = out.dropna(subset=["path"])
    by_split = {s: g.groupby(["repo", "run_id"])["path"].agg(frozenset).to_dict() for s, g in out.groupby("split")}

    base: dict[tuple, tuple[list[str], frozenset, frozenset]] = {}
    lost = 0
    for k in keys:
        rows = feats.iloc[idx[k]]
        cands = set(rows["test_file"])
        strict = frozenset(rows.loc[rows["label"] == 1, "test_file"])
        everything = frozenset(by_split.get("all", {}).get(k, frozenset()) & cands)
        assert strict <= frozenset(by_split["strict"].get(k, frozenset())), f"label not in strict split: {k}"
        # the `all` split must contain the strict failures; a strict file missing from it is a data fault
        assert strict <= everything, f"strict failure absent from the all split: {k}"
        lost += len(by_split["all"].get(k, frozenset()) - cands)
        base[k] = (rows["test_file"].tolist(), strict, everything)

    scores = pd.read_parquet(SCORES, columns=["method", "seed", "repo", "run_id", "test_file", "rank", "split"])
    scores = scores[scores["split"] == "test"]
    result: dict[str, list[list[Change]]] = {}
    for m in METHODS:
        if m == "B1":
            result[m] = []
            for seed in SEEDED[m]:
                run = []
                for k in keys:
                    files = np.asarray(base[k][0], dtype=object)
                    s = np.random.default_rng([seed, int(k[1])]).random(len(files))
                    run.append(Change(files[np.argsort(-s, kind="stable")].tolist(), base[k][1], base[k][2]))
                result[m].append(run)
            continue
        sub = scores[scores["method"] == m]
        seeds = SEEDED.get(m, (None,))
        result[m] = []
        for seed in seeds:
            part = sub if seed is None else sub[sub["seed"] == seed]
            part = part.sort_values(["repo", "run_id", "rank"], kind="stable")
            files_by = part.groupby(["repo", "run_id"], sort=False)["test_file"].agg(list).to_dict()
            result[m].append([Change(files_by[k], base[k][1], base[k][2]) for k in keys])
    # the recomputed B1 seed 0 and the stored one must agree (guards a drifted score table)
    stored = scores[(scores["method"] == "B1")].sort_values(["repo", "run_id", "rank"], kind="stable") \
        .groupby(["repo", "run_id"], sort=False)["test_file"].agg(list).to_dict()
    assert all(stored[k] == c.ranked for k, c in zip(keys, result["B1"][0])), "B1 seed 0 differs from e1_scores"
    return result, {"keys": keys, "lost_all_files": lost}


def build_report(result: dict[str, list[list[Change]]], extra: dict) -> str:
    """The markdown document."""
    ours = result["ours"][0]
    n_cand = np.array([len(c.ranked) for c in ours])
    n_fail = np.array([c.n_fail() for c in ours])
    n_all = np.array([c.n_fail(True) for c in ours])
    text = paper_md.header("E1 rankers under the metrics of Predictive Test Selection (Machalica et al., ICSE-SEIP 2019)",
                           "analysis/pts_comparison.py")
    text += (f"\nTest split D-57 (chronological, {len(ours)} changes). Unit: test FILE; candidates: every test file of the "
             "repo at that commit, as in E1. Selecting at rate r takes the top ceil(r x candidates) files of each change "
             "(exact arithmetic). TestRecall is micro (sum of hits over sum of failing files) unless marked macro "
             "(mean of per-change ratios). Seeded methods (ours, B7, B6: seeds 0-4; B1: 20 seeds) report the mean over "
             "seeds. This measures rankers trained and evaluated on BR-Bench, a different corpus and unit than the "
             "base paper's industrial setting; the numbers are not comparable to theirs in absolute terms.\n")

    # (e) candidates
    text += "\n## Candidates per change (our analogue of |DependentTests|)\n\n" + paper_md.table(
        ["quantity", "mean", "median", "min", "max", "sum"],
        [["candidate test files", f"{n_cand.mean():.1f}", f"{np.median(n_cand):g}", n_cand.min(), n_cand.max(), n_cand.sum()],
         ["failing files (strict)", f"{n_fail.mean():.2f}", f"{np.median(n_fail):g}", n_fail.min(), n_fail.max(), n_fail.sum()],
         ["failing files (all splits, bound, in candidates)", f"{n_all.mean():.2f}", f"{np.median(n_all):g}",
          n_all.min(), n_all.max(), n_all.sum()]])
    text += (f"\nAll-split failing files that are not among the candidates (not counted anywhere): "
             f"{extra['lost_all_files']}.\n")

    # (a)
    sel = [f"{float(r):.0%}" for r in RATES]
    text += ("\n## (a) TestRecall and ChangeRecall by selection rate\n\n"
             "Actual selection rate (sum selected / sum candidates; the ceiling makes it slightly above the "
             "nominal rate, identically for every method): "
             + ", ".join(f"{s} -> {selection_rate(ours, rate=r):.3f}" for s, r in zip(sel, RATES)) + ".\n")
    for title, fn, kw in (("micro TestRecall", failing_recall, {}), ("macro TestRecall", failing_recall, {"macro": True}),
                          ("ChangeRecall", change_recall, {})):
        text += f"\n### {title}\n\n" + paper_md.table(
            ["method", *sel],
            [[NAMES[m], *[_fmt(mean_runs(result[m], fn, rate=r, **kw)) for r in RATES]] for m in METHODS])

    # (b)
    rows = []
    for m in METHODS:
        a = min_rate(result[m], failing_recall, TARGET_TEST_RECALL)
        b = min_rate(result[m], change_recall, TARGET_CHANGE_RECALL)
        rows.append([NAMES[m], "not reached" if a is None else f"{float(a):.3f}",
                     "not reached" if b is None else f"{float(b):.3f}"])
    text += ("\n## (b) Smallest per-change selection rate that reaches the target\n\n"
             "The same rate for every change; seed-mean metric for seeded methods. The rate is the smallest "
             "k/n (a whole number of files for some change) at which the target holds; any rate just above the "
             "previous such fraction selects the same files. With 148 changes, ChangeRecall >= 0.999 means every "
             "change has a failing file selected.\n\n"
             + paper_md.table(["method", "rate for micro TestRecall >= 0.95", "rate for ChangeRecall >= 0.999"], rows))

    # (c)
    text += ("\n## (c) Top-K view: ChangeRecall when selecting the K best files per change\n\n"
             + paper_md.table(["method", *[f"K={k}" for k in TOP_K]],
                              [[NAMES[m], *[_fmt(mean_runs(result[m], change_recall, k=k)) for k in TOP_K]]
                               for m in METHODS])
             + "\nSelection rate at that K (sum min(K, candidates) / sum candidates): "
             + ", ".join(f"K={k} -> {selection_rate(ours, k=k):.4f}" for k in TOP_K) + ".\n")

    # (d)
    text += ("\n## (d) TestRecall against TestRecallWithFlakes (ours)\n\n"
             "Failing = every bound file of the `all` outcome split, which includes strict, inherited and flaky "
             "failures; the ranker was trained on strict labels only.\n\n"
             + paper_md.table(
                 ["quantity", *sel],
                 [["micro TestRecall (strict)", *[_fmt(mean_runs(result["ours"], failing_recall, rate=r)) for r in RATES]],
                  ["micro TestRecallWithFlakes", *[_fmt(mean_runs(result["ours"], failing_recall, rate=r, all_labels=True))
                                                    for r in RATES]],
                  ["macro TestRecall (strict)", *[_fmt(mean_runs(result["ours"], failing_recall, rate=r, macro=True))
                                                   for r in RATES]],
                  ["macro TestRecallWithFlakes", *[_fmt(mean_runs(result["ours"], failing_recall, rate=r, macro=True,
                                                                  all_labels=True)) for r in RATES]]]))
    return text


def main() -> int:
    result, extra = load_changes()
    path = paper_md.write("pts_comparison.md", build_report(result, extra))
    print("wrote", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
