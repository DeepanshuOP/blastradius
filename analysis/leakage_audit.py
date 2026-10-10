"""Leakage audit of the two RQ1 evidence sources, per strict instance.

For EVERY strict instance this asserts that the evidence each method reads comes
only from before the instance's `run_started_at`, and that the instance's own
run, labels and head commit are excluded:

  (a) historical-frequency baseline: the rows it ranks (`historical_evidence`)
      must all start strictly earlier than the instance, none may be the
      instance's own run, all must be strict-split rows, and no
      (run_id, test_id) may appear twice;
  (b) co-change: every commit behind a partner (`RepoHistory.commits_touching`,
      re-read independently from git with `git log --no-walk`) must have a
      committer time strictly before `run_started_at` and inside the trailing
      window, and the instance's own head commit must not be among them.

The same checks are run on the LEGACY variants (the static co-change table and
the all-splits baseline) so the report shows what the fix removed. Writes
`paper/generated/leakage_audit.md` and exits non-zero if a CURRENT method
violates anything.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from analysis import paper_md
from analysis.rq1_divergence import (CLONES_DIR, COCHANGE_PIN, K_VALS, METHODS, Rq1Data, evaluate_k, ground_truth,
                                     historical_evidence, load_data, run_ts)

E1_FEATURES = Path("data/processed/e1_features.parquet")
E1_CELLS = 200
DAY = 86400
WINDOW_NOTE = "committer time, `[run_started_at - 365 d, run_started_at)`"


def audit_historical(data: Rq1Data, hist: str) -> dict:
    """Per-instance checks of the historical-frequency baseline's evidence.

    Args:
        data: Loaded inputs.
        hist: `strict` (current) or `legacy` (all splits).

    Returns:
        Counts of instances (each over `audited`): `with_evidence`, `not_before`
        (some evidence row starts at or after the instance), `own_run` (the instance's own run
        is in the evidence), `non_strict` (a non-strict row is in the evidence), `duplicated`
        ((run_id, test_id) appears more than once), plus `same_head_sha` (evidence from another
        run of the same head commit: allowed, reported as an observation), `rows` and
        `distinct_labels` in the evidence summed over instances.
    """
    c = dict(audited=0, with_evidence=0, not_before=0, own_run=0, non_strict=0, duplicated=0, same_head_sha=0,
             rows=0, distinct_labels=0)
    for _, row in data.valid_runs.iterrows():
        ev = historical_evidence(data, row['repo'], row, hist)
        c['audited'] += 1
        if len(ev) == 0:
            continue
        c['with_evidence'] += 1
        cutoff = run_ts(row['run_started_at'])
        c['not_before'] += int((ev['run_started_at'].map(run_ts) >= cutoff).any())
        c['own_run'] += int((ev['run_id'] == row['run_id']).any())
        c['non_strict'] += int((ev['split'] != 'strict').any())
        pairs = ev[['run_id', 'test_id']]
        c['duplicated'] += int(pairs.duplicated().any())
        c['rows'] += len(ev)
        c['distinct_labels'] += len(pairs.drop_duplicates())
        head = data.head_sha_of.get(row['run_id'])
        c['same_head_sha'] += int(any(data.head_sha_of.get(r) == head for r in ev['run_id'].unique()))
    return c


def commit_times(repo: str, shas: set[str]) -> dict[str, int]:
    """Committer times read straight from git (independent of the cached history)."""
    clone = CLONES_DIR / repo.replace("/", "__")
    out = subprocess.run(["git", "-C", str(clone), "log", "--no-walk=unsorted", "--stdin", "--format=%H %ct"],
                         input="\n".join(sorted(shas)) + "\n", capture_output=True, text=True, check=True,
                         env={**os.environ, "GIT_NO_LAZY_FETCH": "1"}).stdout
    return {line.split()[0]: int(line.split()[1]) for line in out.splitlines() if line.strip()}


def audit_cochange(data: Rq1Data, as_of_ts: int) -> tuple[dict, dict]:
    """Per-instance checks of the trailing co-change evidence, and what the static table exposed.

    Args:
        data: Loaded inputs.
        as_of_ts: End of the static table's window (corpus pin), epoch seconds.

    Returns:
        `(current, legacy)` count dicts. `current` (over `audited` instances): `with_evidence`,
        `not_before` (a commit behind a partner is at/after the run), `outside_window`,
        `own_head` (the instance's own head commit is used), `not_in_git` (a used sha git cannot
        time). `legacy`: `exposed` (the static window ends after the run started), `future_commit`
        (at least one mined commit dated in `[run_started_at, as_of]` touches a changed file).
    """
    cur = dict(audited=0, with_evidence=0, not_before=0, outside_window=0, own_head=0, not_in_git=0, commits=0)
    leg = dict(audited=0, exposed=0, future_commit=0)
    window = data.history[next(iter(data.history))].window_days * 86400
    used: dict[str, set] = {}  # repo -> shas behind any instance's evidence
    per_instance = []
    for _, row in data.valid_runs.iterrows():
        repo = row['repo']
        F = data.pr_to_changed.get((repo, str(row['pr_number'])))
        if not F:
            continue
        cutoff, head = run_ts(row['run_started_at']), data.head_sha_of.get(row['run_id'])
        hist = data.history[repo]
        shas, future = set(), False
        for f in sorted(F):
            shas.update(c.sha for c in hist.commits_touching(f, cutoff, exclude_sha=head))
            future = future or any(cutoff <= hist.commits[i].ts <= as_of_ts for i in hist._by_file.get(f, ()))
        per_instance.append((repo, cutoff, head, shas))
        used.setdefault(repo, set()).update(shas)
        leg['audited'] += 1
        leg['exposed'] += int(cutoff < as_of_ts)
        leg['future_commit'] += int(future)
    times = {repo: commit_times(repo, shas) for repo, shas in used.items() if shas}
    for repo, cutoff, head, shas in per_instance:
        cur['audited'] += 1
        if not shas:
            continue
        cur['with_evidence'] += 1
        cur['commits'] += len(shas)
        t = times[repo]
        cur['not_in_git'] += int(any(s not in t for s in shas))
        cur['not_before'] += int(any(t.get(s, -1) >= cutoff for s in shas))
        cur['outside_window'] += int(any(0 <= t.get(s, -1) < cutoff - window for s in shas))
        cur['own_head'] += int(head in shas)
    return cur, leg


def _own_commits(repo: str, until_ts: int) -> list[tuple[int, str, frozenset]]:
    """Commits of the pinned clone read by this module's own `git log` parse (independent of `RepoHistory`).

    Non-merge, no renames, committer time, commits touching 0 or more than 50 files dropped (D-52).
    """
    pins = json.loads(Path("docs/CLONE_PINS.json").read_text())["pins"]
    clone = CLONES_DIR / repo.replace("/", "__")
    out = subprocess.run(["git", "-C", str(clone), "log", pins[repo], "--no-merges", "--no-renames",
                          "--format=@@@%H %ct", "--name-only"], capture_output=True, text=True, check=True,
                         encoding="utf-8", errors="replace", env={**os.environ, "GIT_NO_LAZY_FETCH": "1"}).stdout
    commits, cur = [], None
    for line in out.splitlines():
        if line.startswith("@@@"):
            if cur and 0 < len(cur[2]) <= 50 and cur[0] <= until_ts:
                commits.append((cur[0], cur[1], frozenset(cur[2])))
            sha, ts = line[3:].split()
            cur = (int(ts), sha, set())
        elif line.strip() and cur is not None:
            cur[2].add(line.strip())
    if cur and 0 < len(cur[2]) <= 50 and cur[0] <= until_ts:
        commits.append((cur[0], cur[1], frozenset(cur[2])))
    return commits


def audit_e1(data: Rq1Data, feats: pd.DataFrame, n_cells: int = E1_CELLS, seed: int = 0) -> dict:
    """Recompute a random sample of E1 feature cells from raw rows and check time-safety.

    For each sampled (instance, candidate, feature) cell the value is recomputed from the
    raw tables with this module's own code (strict labels and head failures from the RQ1
    frames, co-change from a fresh `git log` parse, co-failures from the ground truth), using
    only source rows with time strictly before `run_started_at`. A cell is a violation if the
    stored value differs, which is what any use of a row at or after the cutoff would cause.

    Args:
        data: Loaded RQ1 inputs.
        feats: `e1_features.parquet`.
        n_cells: Number of (row, feature) cells.
        seed: Sampling seed.

    Returns:
        `{"cells": [...], "by_family": {...}, "violations": n, "max_source_gap_s": ...}`.
    """
    from analysis.rq1_divergence import ground_truth
    from src.features.test_features import FAMILIES, FEATURE_COLS

    fam_of = {c: f for f, cs in FAMILIES.items() for c in cs}
    rng = np.random.default_rng(seed)
    # half uniform, half from rows where history exists (labels, prior failures, co-failures), so the
    # audit has power on the time-dependent families instead of sampling mostly all-zero rows
    active = np.flatnonzero(((feats["label"] == 1) | (feats["hist_fail_count"] > 0) | (feats["hist_head_fail_count"] > 0)
                             | (feats["cofail_max"] > 0)).to_numpy())
    half = n_cells // 2
    rows = np.concatenate([rng.integers(0, len(feats), n_cells - half),
                           active[rng.integers(0, len(active), half)] if len(active) else
                           rng.integers(0, len(feats), half)])
    cols = rng.integers(0, len(FEATURE_COLS), n_cells)
    pr_of = {(r["repo"], r["run_id"]): str(r["pr_number"]) for _, r in data.valid_runs.iterrows()}
    started = {(r["repo"], r["run_id"]): run_ts(r["run_started_at"]) for _, r in data.valid_runs.iterrows()}
    gt = ground_truth(data)
    head_all = data.hist_legacy[data.hist_legacy["split"] == "all"].drop_duplicates(subset=["run_id", "test_id"])
    commit_cache: dict[str, list] = {}
    by_family: dict[str, dict] = {}
    violations = 0
    min_gap = None
    for ri, ci in zip(rows, cols):
        r, col = feats.iloc[int(ri)], FEATURE_COLS[int(ci)]
        fam, repo, rid, tf, cutoff = fam_of[col], r["repo"], int(r["run_id"]), r["test_file"], int(r["ts"])
        key = (repo, rid)
        changed = sorted(data.pr_to_changed.get((repo, pr_of[key]), set()))
        stat = by_family.setdefault(fam, {"cells": 0, "had_later_rows": 0, "mismatch": 0, "no_time_source": 0})
        stat["cells"] += 1
        expected = None
        if fam == "hist_":
            ev = data.hist_all[(data.hist_all["repo"] == repo) & (data.hist_all["resolved_path"] == tf)]
            hv = head_all[(head_all["repo"] == repo) & (head_all["resolved_path"] == tf)]
            t_ev = ev["run_started_at"].map(run_ts).to_numpy()
            t_hd = hv["run_started_at"].map(run_ts).to_numpy()
            before = t_ev[t_ev < cutoff]
            stat["had_later_rows"] += int(bool((t_ev >= cutoff).any() or (t_hd >= cutoff).any()))
            if before.size:
                min_gap = cutoff - int(before.max()) if min_gap is None else min(min_gap, cutoff - int(before.max()))
            if col == "hist_fail_count":
                expected = before.size
            elif col == "hist_fail_30d":
                expected = int((before >= cutoff - 30 * DAY).sum())
            elif col == "hist_fail_90d":
                expected = int((before >= cutoff - 90 * DAY).sum())
            elif col == "hist_days_since_last":
                expected = (cutoff - before.max()) / DAY if before.size else float("nan")
            elif col == "hist_head_fail_count":
                expected = int((t_hd < cutoff).sum())
            else:  # hist_repo_rank: recount every candidate of the instance from the raw frame
                cand = feats[(feats["repo"] == repo) & (feats["run_id"] == rid)]["test_file"]
                evr = data.hist_all[data.hist_all["repo"] == repo]
                evr = evr[evr["run_started_at"].map(run_ts) < cutoff]
                counts = evr["resolved_path"].value_counts().to_dict()
                order = sorted(cand, key=lambda f: (-counts.get(f, 0), f))
                expected = order.index(tf) + 1
        elif fam == "cochg_":
            if repo not in commit_cache:
                commit_cache[repo] = _own_commits(repo, 2**40)
            head = data.head_sha_of.get(rid)
            lo = cutoff - 365 * DAY
            sup_l, conf_l, with_partner = [], [], 0
            for f in changed:
                touching = [c for c in commit_cache[repo] if f in c[2] and lo <= c[0] < cutoff and c[1] != head]
                stat["had_later_rows"] += int(any(f in c[2] and c[0] >= cutoff for c in commit_cache[repo]))
                counts: dict[str, int] = {}
                for c in touching:
                    for g in c[2]:
                        if g != f:
                            counts[g] = counts.get(g, 0) + 1
                kept = {g: n for g, n in counts.items() if n >= 2}
                with_partner += int(bool(kept))
                if tf in kept:
                    sup_l.append(kept[tf])
                    conf_l.append(kept[tf] / len(touching))
                    gap = cutoff - max(c[0] for c in touching)
                    min_gap = gap if min_gap is None else min(min_gap, gap)
            expected = {"cochg_max_support": max(sup_l, default=0), "cochg_sum_support": sum(sup_l),
                        "cochg_max_conf": max(conf_l, default=0.0), "cochg_sum_conf": sum(conf_l),
                        "cochg_n_files_with_partner": with_partner}[col]
        elif fam == "cofail_":
            vals = []
            for f in changed:
                n = 0
                for k2, files in gt.items():
                    if k2[0] != repo or k2 not in started or tf not in files:
                        continue
                    if f in data.pr_to_changed.get((repo, pr_of[k2]), set()):
                        if started[k2] < cutoff:
                            n += 1
                        else:
                            stat["had_later_rows"] += 1
                vals.append(n)
            expected = max(vals, default=0) if col == "cofail_max" else sum(vals)
        else:
            stat["no_time_source"] += 1
            continue
        got = r[col]
        ok = (np.isnan(got) and np.isnan(expected)) or abs(float(got) - float(expected)) < 1e-9
        if not ok:
            stat["mismatch"] += 1
            violations += 1
    return {"by_family": by_family, "violations": violations, "min_gap_s": min_gap, "cells": n_cells}


def stage_table(data: Rq1Data) -> list[list]:
    """RQ1 at k=5/10/20 under each combination of fixes, so each effect is visible."""
    stages = (
        ("0 old: static co-change table, all-splits baseline", "static", "legacy"),
        ("1 baseline de-duplicated to strict, once per (test, instance) only", "static", "strict"),
        ("2 co-change trailing, one-sided lookup, legacy baseline (leak fix only)", "trailing_oneside", "legacy"),
        ("3 co-change trailing, one-sided lookup, strict baseline (Round 4)", "trailing_oneside", "strict"),
        ("4 symmetric lookup, strict baseline (current, D-52)", "trailing", "strict"),
    )
    gt = ground_truth(data)
    rows = []
    for k in K_VALS:
        for name, cochange, hist in stages:
            df = evaluate_k(data, gt, k, cochange=cochange, hist=hist)
            for key, label in METHODS:
                rows.append([k, name, label, len(df), f"{df[f'{key}_p'].mean():.3f}",
                             f"{df[f'{key}_r'].mean():.3f}", f"{df[f'{key}_j'].mean():.3f}"])
    return rows


def main() -> int:
    data = load_data()
    n = data.n_strict_instances
    pin = json.loads(COCHANGE_PIN.read_text())
    cur_h, leg_h = audit_historical(data, "strict"), audit_historical(data, "legacy")
    cur_c, leg_c = audit_cochange(data, run_ts(pin['as_of']))

    def r(num: int, den: int) -> str:
        return paper_md.rate(num, den)

    text = paper_md.header(
        "Leakage audit: evidence available to the RQ1 methods", "analysis/leakage_audit.py",
        f"Every one of the {n:,} strict instances is checked. 'Before' means strictly before the "
        f"instance's `run_started_at`; commit time is {WINDOW_NOTE}. Violations are instances (n/d).")
    text += "\n## Historical-frequency baseline\n\n" + paper_md.table(
        ["check (instances violating)", "current: strict labels, once each", "legacy: all splits"],
        [["instances audited", r(cur_h['audited'], n), r(leg_h['audited'], n)],
         ["instances with any evidence", r(cur_h['with_evidence'], cur_h['audited']), r(leg_h['with_evidence'], leg_h['audited'])],
         ["evidence from a run starting at or after the instance", r(cur_h['not_before'], cur_h['audited']), r(leg_h['not_before'], leg_h['audited'])],
         ["instance's own run in the evidence", r(cur_h['own_run'], cur_h['audited']), r(leg_h['own_run'], leg_h['audited'])],
         ["non-strict rows in the evidence", r(cur_h['non_strict'], cur_h['audited']), r(leg_h['non_strict'], leg_h['audited'])],
         ["a (run, test) counted more than once", r(cur_h['duplicated'], cur_h['audited']), r(leg_h['duplicated'], leg_h['audited'])],
         ["evidence rows / distinct (run, test) labels, summed over instances",
          f"{cur_h['rows']:,} / {cur_h['distinct_labels']:,}", f"{leg_h['rows']:,} / {leg_h['distinct_labels']:,}"],
         ["observation (not a violation): evidence includes another run of the same head commit",
          r(cur_h['same_head_sha'], cur_h['audited']), r(leg_h['same_head_sha'], leg_h['audited'])]])
    text += ("\nThe baseline orders runs by start time, not by completion time: an earlier-started run that was "
             "still executing when the instance started would be visible here but not in deployment. "
             "`instances_raw` carries no completion time, so this cannot be checked from local data.\n")
    text += "\n## Co-change\n\n" + paper_md.table(
        ["check (instances violating)", "current: per-instance trailing history"],
        [["instances audited (strict, with a changeset)", r(cur_c['audited'], n)],
         ["instances with any co-change evidence", r(cur_c['with_evidence'], cur_c['audited'])],
         ["a commit at or after `run_started_at` behind a partner (times re-read from git)", r(cur_c['not_before'], cur_c['audited'])],
         ["a used commit git cannot time", r(cur_c['not_in_git'], cur_c['audited'])],
         ["a commit older than the trailing window", r(cur_c['outside_window'], cur_c['audited'])],
         ["the instance's own head commit used", r(cur_c['own_head'], cur_c['audited'])],
         ["commits behind the evidence, summed over instances", f"{cur_c['commits']:,}"]])
    text += ("\nCo-change reads commit file lists only, never outcomes, so no instance's labels can enter it.\n")
    text += "\n### Legacy static table (`data/interim/cochange.parquet`)\n\n" + paper_md.table(
        ["check (instances violating)", "legacy"],
        [["window ends (" + pin['as_of'] + ") after the instance started", r(leg_c['exposed'], leg_c['audited'])],
         ["a mined commit dated in `[run_started_at, as_of]` touches a changed file of the instance",
          r(leg_c['future_commit'], leg_c['audited'])]])
    text += "\n## RQ1 under each fix (mean P / R / J, n instances where the all-partners proxy fires)\n\n"
    text += ("Stage 1 isolates the baseline de-duplication, stage 2 the co-change leak fix, stage 3 both, stage 4 adds the symmetric lookup. "
             "`co-change, restricted to files with \"test\" in the path` is the old test-only row. The static table "
             "stores each pair once as `file_a < file_b` and was looked up by `file_a` only, so only "
             "lexicographically later paths were ever candidates; stages 0-3 inherit that, stage 4 reads both directions.\n\n")
    text += paper_md.table(["k", "stage", "method", "n", "mean P", "mean R", "mean J"], stage_table(data))
    e1 = None
    if E1_FEATURES.exists():
        e1 = audit_e1(data, pd.read_parquet(E1_FEATURES))
        text += ("\n## E1 feature table (`data/processed/e1_features.parquet`)\n\n"
                 f"A seeded sample of {e1['cells']} (candidate row, feature) cells (half uniform, half from rows with history) is recomputed from raw rows "
                 "by this script's own code (strict labels and head failures from the RQ1 frames, co-change from a "
                 "fresh `git log` parse of the pinned clone, co-failures from the ground truth), using only source "
                 "rows strictly before the instance's `run_started_at`. A violation is a stored value that differs "
                 "from that recomputation. 'Cells with later rows' counts cells where rows at or after the cutoff "
                 "exist for the same keys, i.e. where a leak would have changed the value (the audit's power). "
                 "`prox_` and `chg_` read only the change itself and have no time-dependent source.\n\n")
        text += paper_md.table(
            ["family", "cells audited", "cells with later rows (power)", "violations", "no time-dependent source"],
            [[f, v["cells"], v["had_later_rows"], v["mismatch"], v["no_time_source"]]
             for f, v in sorted(e1["by_family"].items())])
        gap = e1["min_gap_s"]
        text += ("\nSmallest gap between the cutoff and the newest source row used: "
                 + (f"{gap:,} s" if gap is not None else "n/a") + ".\n")
    path = paper_md.write("leakage_audit.md", text)

    bad = {"historical": [k for k in ("not_before", "own_run", "non_strict", "duplicated") if cur_h[k]],
           "cochange": [k for k in ("not_before", "not_in_git", "own_head") if cur_c[k]]}
    print(f"Wrote {path}")
    for name, ks in bad.items():
        print(f"{name}: {'VIOLATIONS ' + ', '.join(ks) if ks else 'no violations'}")
    if e1 is not None:
        print(f"e1 features: {e1['violations']} violations in {e1['cells']} sampled cells")
        if e1["violations"]:
            return 1
    return 1 if any(bad.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
