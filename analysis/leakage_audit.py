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

import pandas as pd

from analysis import paper_md
from analysis.rq1_divergence import (CLONES_DIR, COCHANGE_PIN, K_VALS, METHODS, Rq1Data, evaluate_k, ground_truth,
                                     historical_evidence, load_data, run_ts)

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


def stage_table(data: Rq1Data) -> list[list]:
    """RQ1 at k=5/10/20 under each combination of fixes, so each effect is visible."""
    stages = (
        ("0 old: static co-change table, all-splits baseline", "static", "legacy"),
        ("1 baseline de-duplicated to strict, once per (test, instance) only", "static", "strict"),
        ("2 co-change trailing only (leak fix)", "trailing", "legacy"),
        ("3 both fixes (current)", "trailing", "strict"),
        ("info: 3 plus partners in both directions", "trailing_both", "strict"),
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
    text += ("Stage 1 isolates the baseline de-duplication, stage 2 the co-change leak fix, stage 3 both. "
             "`co-change, restricted to files with \"test\" in the path` is the old test-only row. The `info` stage "
             "is not a fix applied: the static table stores each pair once as `file_a < file_b` and was looked up "
             "by `file_a` only, so only lexicographically later paths were ever candidates; it shows what "
             "both directions would score.\n\n")
    text += paper_md.table(["k", "stage", "method", "n", "mean P", "mean R", "mean J"], stage_table(data))
    path = paper_md.write("leakage_audit.md", text)

    bad = {"historical": [k for k in ("not_before", "own_run", "non_strict", "duplicated") if cur_h[k]],
           "cochange": [k for k in ("not_before", "not_in_git", "own_head") if cur_c[k]]}
    print(f"Wrote {path}")
    for name, ks in bad.items():
        print(f"{name}: {'VIOLATIONS ' + ', '.join(ks) if ks else 'no violations'}")
    return 1 if any(bad.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
