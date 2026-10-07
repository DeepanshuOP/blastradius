"""Composition, base resolution, binding and gate tables for the paper.

Writes four files under `paper/generated/` (each headed with this script and
the git sha, every row `n/d`): `composition.md`, `base_resolution.md`,
`binding.md`, `gates.md`. Reads only `data/interim/*.parquet`; no network.
Flakiness (`flakiness.md`) is written by `src/label/fault_revealing.py`, which
holds the flip statistics.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from analysis import paper_md
from analysis.paper_md import rate
from src.label.fault_revealing import GATE1_THRESHOLD

GATE15_THRESHOLD = 0.70
SPLITS = ("all", "relaxed", "strict")
HIST_MAX = 10


def _slice(df: pd.DataFrame) -> list:
    """repos, instances, labels, distinct tests for one slice of labelled rows."""
    return [int(df["repo"].nunique()), int(df["run_id"].nunique()), len(df), int(df["test_id"].nunique())]


def composition(outcomes: pd.DataFrame, instances: pd.DataFrame) -> str:
    """`composition.md`: per split, and per language within each split.

    Args:
        outcomes: Columns run_id, test_id, split.
        instances: Columns run_id, repo, language (duplicates by run_id ignored).

    Returns:
        The markdown document.
    """
    inst = instances.drop_duplicates("run_id")[["run_id", "repo", "language"]]
    df = outcomes.merge(inst, on="run_id", how="left")
    totals = {s: df[df["split"] == s] for s in SPLITS}
    all_inst, all_labels = totals["all"]["run_id"].nunique(), len(totals["all"])

    rows = []
    for s in SPLITS:
        d = totals[s]
        repos, n_inst, n_lab, n_tests = _slice(d)
        langs = sorted(d["language"].dropna().unique())
        rows.append([s, repos, f"{len(langs)} ({', '.join(langs)})", rate(n_inst, all_inst),
                     rate(n_lab, all_labels), f"{n_tests:,}"])
    text = paper_md.header("Corpus composition", "analysis/paper_numbers.py",
                           "Instances and labels are shown as a share of the `all` split. Distinct tests "
                           "count distinct `test_id` values (the figure `fault_revealing.py` prints).")
    text += "\n## Per split\n\n" + paper_md.table(
        ["split", "repos", "languages", "instances (n/d of all)", "labels (n/d of all)", "distinct tests"], rows)
    for s in SPLITS:
        d = totals[s]
        rows = []
        for lg in sorted(d["language"].dropna().unique()):
            sub = d[d["language"] == lg]
            repos, n_inst, n_lab, n_tests = _slice(sub)
            rows.append([lg, repos, rate(n_inst, d["run_id"].nunique()), rate(n_lab, len(d)), f"{n_tests:,}"])
        text += f"\n## Per language: {s} split\n\n" + paper_md.table(
            ["language", "repos", f"instances (n/d of {s})", f"labels (n/d of {s})", "distinct tests"], rows)
    return text


def base_resolution(res: pd.DataFrame) -> str:
    """`base_resolution.md`: status mix, no_base rate and base-run distance distribution.

    Args:
        res: `base_resolution_new` (status, base_run_distance).

    Returns:
        The markdown document.
    """
    n = len(res)
    text = paper_md.header("Base resolution", "analysis/paper_numbers.py",
                           f"Population: the {n:,} failed-run instances in `base_resolution_new.parquet`.")
    counts = res["status"].value_counts().to_dict()
    order = sorted(counts, key=lambda k: (-counts[k], k))
    text += "\n## Status mix\n\n" + paper_md.table(
        ["status", "instances (n/d)"], [[s, rate(int(counts[s]), n)] for s in order])
    text += f"\n**no_base rate: {rate(int(counts.get('no_base', 0)), n)}**\n"

    resolved = res[res["status"] != "no_base"]
    dist = resolved["base_run_distance"].dropna()
    with_d = res[res["base_run_distance"].notna()].groupby("status").size().to_dict()
    text += ("\n## Base-run distance\n\n"
             f"Population: resolved instances (status != no_base) with a distance recorded: "
             f"{rate(len(dist), len(resolved))}. Distance is recorded for: "
             + ", ".join(f"{k} {rate(int(v), int((res['status'] == k).sum()))}" for k, v in sorted(with_d.items()))
             + ".\n\n")
    if len(dist):
        text += paper_md.table(
            ["statistic", "value"],
            [["median", f"{float(np.median(dist)):g}"],
             ["p90 (linear interpolation)", f"{float(np.percentile(dist, 90)):g}"],
             ["p99 (linear interpolation)", f"{float(np.percentile(dist, 99)):g}"],
             ["max", f"{float(dist.max()):g}"]])
        vals = dist.astype(int)
        rows = [[i, rate(int((vals == i).sum()), len(dist))] for i in range(HIST_MAX + 1)]
        rows.append([f"> {HIST_MAX}", rate(int((vals > HIST_MAX).sum()), len(dist))])
        text += "\n### Histogram (commits between base run and head)\n\n" + paper_md.table(
            ["distance", "instances (n/d)"], rows)
    return text


def binding(b: pd.DataFrame) -> str:
    """`binding.md`: combined and full-confidence binding, plus the residual statuses.

    Args:
        b: `binding.parquet` (status, is_fqcn_qualified).

    Returns:
        The markdown document.
    """
    n = len(b)
    exact = b["status"] == "exact"
    fq = b["is_fqcn_qualified"].astype(bool)
    rows = [
        ["combined (exact)", rate(int(exact.sum()), n)],
        ["full confidence (exact, fully-qualified class name)", rate(int((exact & fq).sum()), n)],
        ["basename-only, 0.5 confidence (exact, bare class name)", rate(int((exact & ~fq).sum()), n)],
        ["ambiguous", rate(int((b["status"] == "ambiguous").sum()), n)],
        ["not_found", rate(int((b["status"] == "not_found").sum()), n)],
        ["unqualified", rate(int((b["status"] == "unqualified").sum()), n)],
    ]
    text = paper_md.header("Test-to-file binding (D-47, D-50)", "analysis/paper_numbers.py",
                           f"Denominator: {n:,} distinct (repo, test_id) pairs, bound against the pinned "
                           "clone commits in `docs/CLONE_PINS.json`. Both binding figures appear together (D-47).")
    text += "\n" + paper_md.table(["measure", "n/d"], rows)
    return text


def gates(outcomes: pd.DataFrame, b: pd.DataFrame) -> str:
    """`gates.md`: Gate 1 (labels, instances) and Gate 1.5 (both binding figures).

    Args:
        outcomes: `outcomes.parquet`.
        b: `binding.parquet`.

    Returns:
        The markdown document.
    """
    strict = outcomes[outcomes["split"] == "strict"]
    labels, insts = len(strict), strict["run_id"].nunique()
    n = len(b)
    exact = b["status"] == "exact"
    comb, full = int(exact.sum()), int((exact & b["is_fqcn_qualified"].astype(bool)).sum())

    def verdict(met: bool) -> str:
        return "MET" if met else "NOT MET"

    rows = [
        ["Gate 1 (D-44, primary): strict labels", rate(labels, GATE1_THRESHOLD), f">= {GATE1_THRESHOLD:,}",
         verdict(labels >= GATE1_THRESHOLD)],
        ["Gate 1 (secondary): strict instances", rate(insts, GATE1_THRESHOLD), f">= {GATE1_THRESHOLD:,}",
         verdict(insts >= GATE1_THRESHOLD)],
        ["Gate 1.5: combined binding", rate(comb, n), f">= {GATE15_THRESHOLD:.0%}",
         verdict(comb / n >= GATE15_THRESHOLD)],
        ["Gate 1.5: full-confidence binding", rate(full, n), f">= {GATE15_THRESHOLD:.0%}",
         verdict(full / n >= GATE15_THRESHOLD)],
    ]
    text = paper_md.header("Gates", "analysis/paper_numbers.py",
                           "Gate 1 reads against the label count (D-44). Gate 1.5 is read on both binding "
                           "figures (D-47) at the pinned clones (D-50).")
    text += "\n" + paper_md.table(["gate", "measured (n/d)", "threshold", "verdict"], rows)
    return text


def main() -> None:
    outcomes = pd.read_parquet("data/interim/outcomes.parquet")
    instances = pd.read_parquet("data/interim/instances_raw.parquet", columns=["run_id", "repo", "language"])
    res = pd.read_parquet("data/interim/base_resolution_new.parquet")
    b = pd.read_parquet("data/interim/binding.parquet")
    for name, text in (("composition.md", composition(outcomes, instances)),
                       ("base_resolution.md", base_resolution(res)),
                       ("binding.md", binding(b)),
                       ("gates.md", gates(outcomes, b))):
        print(f"Wrote {paper_md.write(name, text)}")


if __name__ == "__main__":
    main()
