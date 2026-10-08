"""RQ1 divergence measurement: the co-change proxy on two axes, plus null baselines.

Every number this script prints regenerates without matplotlib, and everything
it prints as a result is also written to `paper/generated/rq1.md`. Figures are
optional: `write_figures` imports matplotlib lazily and skips with a warning if
it is absent, so `make tables` emits the full measurement on a fresh clone with
no plotting stack. Numbers are the paper; figures are a convenience.

Five predictors are compared at k in {5, 10, 20} on ONE common set of
instances (those where the all-partners co-change proxy fires), so their rows
are comparable:
  - co-change, all partner files;
  - co-change restricted to conventional test files
    (`is_conventional_test_file`; PRIMARY test-only variant). The restriction is
    applied BEFORE the top-k cut, so the k slots are spent on test files;
  - the same restricted to `is_test_filename` (`"test"` in the path; sensitivity);
  - changeset baseline (the PR's changed files);
  - historical-frequency baseline (the k most frequently failing bound test
    files of the repo, from STRICT labels of instances that started strictly
    earlier, each (test, instance) failure counted once).

Leakage: co-change is mined per instance from the commits strictly before that
instance's `run_started_at` (`analysis/cochange_trailing.py`), not read from the
static table whose window ends at the corpus pin. The legacy variants
(`cochange="static"`, `hist="legacy"`) are kept only so `analysis/leakage_audit.py`
and the old -> new comparison can regenerate the numbers they replace.
"""

import datetime
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from analysis import paper_md
from analysis.cochange_trailing import RepoHistory, read_history
from src.parse.changeset import is_conventional_test_file, is_test_filename

K_VALS = [5, 10, 20]
METHODS = [
    ("co", "co-change, all partner files"),
    ("co_test", "co-change, restricted to conventional test files"),
    ("co_test_loose", "co-change, restricted to files with \"test\" in the path (sensitivity)"),
    ("b1", "changeset baseline"),
    ("b2", "historical-frequency baseline"),
]
COCHANGE_MODES = ("trailing", "trailing_oneside", "static")
HIST_MODES = ("strict", "legacy")
SIZE_STRATA = [("1", 1, 1), ("2-5", 2, 5), ("6-20", 6, 20), (">20", 21, 10**9)]
CLONES_DIR = Path("data/clones")
CLONE_PINS = Path("docs/CLONE_PINS.json")
COCHANGE_PIN = Path("data/interim/COCHANGE_PIN.json")

def write_figures(dist_counts, k_vals, co_perf, b1_perf, b2_perf, co_test_perf=None):
    """Write the two RQ1 figures, or skip if matplotlib is not installed.

    Args:
        dist_counts: Partners-per-changed-file distribution (Axis 1).
        k_vals: The k values evaluated, in order.
        co_perf: Per-k (precision, recall) for co-change.
        b1_perf: Per-k (precision, recall) for the changeset baseline.
        b2_perf: Per-k (precision, recall) for the historical top-k baseline.
        co_test_perf: Per-k (precision, recall) for test-restricted co-change, if computed.

    Returns:
        True if the figures were written, False if matplotlib was unavailable.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print(
            "\nWARNING: matplotlib is not installed; skipping "
            "paper/generated/fig1_applicability.pdf and fig2_accuracy.pdf. "
            "Every number above was produced without it."
        )
        return False

    os.makedirs('paper/generated', exist_ok=True)

    # Fig 1
    plt.figure(figsize=(8, 5))
    dist_counts.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('Applicability: Distribution of Partners-per-Changed-File')
    plt.xlabel('Number of Co-change Partners')
    plt.ylabel('Number of Changed Files')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('paper/generated/fig1_applicability.pdf', metadata={'CreationDate': None})
    plt.close()

    # Fig 2
    if len(co_perf) > 0:
        plt.figure(figsize=(8, 5))
        ks = [str(k) for k in k_vals]

        # Plot recall
        plt.plot(ks, [x[1] for x in co_perf], marker='o', label='Co-change Recall')
        if co_test_perf:
            plt.plot(ks, [x[1] for x in co_test_perf], marker='D', label='Co-change (test files only) Recall')
        plt.plot(ks, [x[1] for x in b1_perf], marker='s', linestyle='--', label='Baseline 1 (Changeset) Recall')
        plt.plot(ks, [x[1] for x in b2_perf], marker='^', linestyle=':', label='Baseline 2 (Hist Top-k) Recall')

        plt.title('Accuracy vs k (Conditional on Proxy Firing)')
        plt.xlabel('k (Top-k recommendations)')
        plt.ylabel('Recall')
        plt.ylim(0, 1.0)
        plt.legend()
        plt.tight_layout()
        plt.savefig('paper/generated/fig2_accuracy.pdf', metadata={'CreationDate': None})
        plt.close()
        print("\nGenerated paper/generated/fig1_applicability.pdf and paper/generated/fig2_accuracy.pdf")
    return True

def compute_metrics(C, GT):
    if not isinstance(C, set): C = set(C)
    if not isinstance(GT, set): GT = set(GT)
    overlap = C & GT
    precision = len(overlap) / len(C) if C else 0.0
    recall = len(overlap) / len(GT) if GT else 0.0
    jaccard = len(overlap) / len(C | GT) if (C or GT) else 0.0
    return precision, recall, jaccard


@dataclass
class Rq1Data:
    """Everything the RQ1 evaluation reads, loaded once."""

    strict_labels: pd.DataFrame
    bound: dict
    pr_to_changed: dict
    co_support_map: dict
    co_lookup: dict
    hist_all: pd.DataFrame  # strict labels only, one row per (run_id, test_id)
    language_of: dict
    n_strict_instances: int
    valid_runs: pd.DataFrame = field(default=None)
    history: dict = field(default_factory=dict)  # repo -> RepoHistory (trailing co-change)
    head_sha_of: dict = field(default_factory=dict)  # run_id -> head sha
    hist_legacy: pd.DataFrame | None = None  # all splits, as the baseline used to read them
    cache: dict = field(default_factory=dict)  # (mode, repo, file, ts, sha) -> ranked partner paths


def run_ts(started_at: str) -> int:
    """Epoch seconds of an ISO-8601 `run_started_at` (UTC when no offset is given)."""
    dt = datetime.datetime.fromisoformat(str(started_at).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return int(dt.timestamp())


def load_history(repos_ts: dict[str, tuple[int, int]], window_days: int, min_support: int,
                 until_ts: int) -> dict[str, RepoHistory]:
    """Read each repo's commit log at its pinned commit, back to the earliest window it needs.

    Args:
        repos_ts: `{repo: (earliest cutoff, latest cutoff)}` over the instances scored.
        window_days: Trailing window of the co-change statistic.
        min_support: Support threshold of the statistic.
        until_ts: Newest commit time to read (the corpus pin, so the legacy window is covered).

    Returns:
        `{repo: RepoHistory}`.

    Raises:
        SystemExit: If a repo has no pinned commit or no clone (no silent fallback to HEAD).
    """
    pins = json.loads(CLONE_PINS.read_text())["pins"]
    out = {}
    for repo, (lo, _hi) in sorted(repos_ts.items()):
        clone = CLONES_DIR / repo.replace("/", "__")
        if repo not in pins or not clone.is_dir():
            raise SystemExit(f"BLOCKED: no pinned clone for {repo}")
        commits = read_history(clone, pins[repo], lo - window_days * 86400, until_ts)
        out[repo] = RepoHistory(commits, window_days, min_support)
    return out


def load_data() -> Rq1Data:
    """Load the parquet inputs and build the lookups the evaluation uses."""
    outcomes = pd.read_parquet('data/interim/outcomes.parquet')
    binding = pd.read_parquet('data/interim/binding.parquet')
    changesets = pd.read_parquet('data/interim/changesets.parquet')
    cochange = pd.read_parquet('data/interim/cochange.parquet')
    instances = pd.read_parquet('data/interim/instances_raw.parquet')

    strict_labels = outcomes[outcomes['split'] == 'strict'].copy()
    strict_labels = pd.merge(strict_labels, instances[['run_id', 'repo', 'pr_number', 'run_started_at']], on=['run_id'], how='inner')

    bound = binding[binding['status'] == 'exact'].set_index(['repo', 'test_id'])['resolved_path'].to_dict()

    pr_to_changed = {}
    for repo, pr, filename in zip(changesets['repo'], changesets['pr_number'].astype(str), changesets['filename']):
        pr_to_changed.setdefault((repo, pr), set()).add(filename)

    cochange['support'] = cochange['support'].astype(int)
    co_support_map = {}
    for row in cochange.itertuples():
        co_support_map.setdefault((row.repo_full, row.file_a), []).append(row.support)

    cochange_sorted = cochange.sort_values(by=['repo_full', 'file_a', 'conf_a_to_b'], ascending=[True, True, False])
    co_lookup = {}
    for repo, grp in cochange_sorted.groupby('repo_full'):
        co_lookup[repo] = {}
        for fa, subgrp in grp.groupby('file_a'):
            co_lookup[repo][fa] = subgrp['file_b'].tolist()

    # Legacy baseline evidence: every split, so a strict label was counted up to three times.
    all_outcomes = pd.merge(outcomes, instances[['run_id', 'repo', 'run_started_at']], on='run_id', how='inner')
    hist_legacy = all_outcomes.copy()
    hist_legacy['resolved_path'] = [bound.get(k) for k in zip(hist_legacy['repo'], hist_legacy['test_id'])]
    hist_legacy = hist_legacy.dropna(subset=['resolved_path'])

    # Current baseline evidence: the strict split only, each (run_id, test_id) once.
    hist_all = strict_labels.drop_duplicates(subset=['run_id', 'test_id']).copy()
    hist_all['resolved_path'] = [bound.get(k) for k in zip(hist_all['repo'], hist_all['test_id'])]
    hist_all = hist_all.dropna(subset=['resolved_path'])

    valid_runs = strict_labels.drop_duplicates(subset=['run_id'])
    language_of = instances.drop_duplicates('run_id').set_index('run_id')['language'].to_dict()
    head_sha_of = instances.drop_duplicates('run_id').set_index('run_id')['head_sha'].to_dict()

    pin = json.loads(COCHANGE_PIN.read_text())
    spans = {}
    for r in valid_runs.itertuples():
        ts = run_ts(r.run_started_at)
        lo, hi = spans.get(r.repo, (ts, ts))
        spans[r.repo] = (min(lo, ts), max(hi, ts))
    history = load_history(spans, pin['window_days'], pin['support_threshold'], run_ts(pin['as_of']))
    return Rq1Data(strict_labels, bound, pr_to_changed, co_support_map, co_lookup, hist_all,
                   language_of, len(valid_runs), valid_runs, history, head_sha_of, hist_legacy)


def ground_truth(data: Rq1Data, exclude: set | None = None) -> dict:
    """Bound test files of each strict instance: `{(repo, run_id): {path}}`.

    Args:
        data: Loaded inputs.
        exclude: `(run_id, test_id)` labels to drop first (sensitivity analyses).

    Returns:
        Instances whose remaining labels bind to at least one file.
    """
    run_to_gt: dict = {}
    for _, row in data.strict_labels.iterrows():
        if exclude and (row['run_id'], row['test_id']) in exclude:
            continue
        path = data.bound.get((row['repo'], row['test_id']))
        if path:
            run_to_gt.setdefault((row['repo'], row['run_id']), set()).add(path)
    return run_to_gt


def partner_stats(data: Rq1Data, repo: str, path: str, row, mode: str = "trailing") -> list:
    """Ranked co-change partners of `path` for one instance, with support and confidence.

    Args:
        data: Loaded inputs.
        repo: Repository.
        path: A changed file.
        row: The instance row (needs `run_id`, `run_started_at`).
        mode: `trailing` (only commits strictly before the run; partners looked up in both
            directions, D-52) or `trailing_oneside` (same, but only lexicographically later
            partners, the old static table's reach; sensitivity only).

    Returns:
        `Partner` records, best first.
    """
    cutoff, head = run_ts(row['run_started_at']), data.head_sha_of.get(row['run_id'])
    key = (mode, repo, path, cutoff, head)
    if key not in data.cache:
        data.cache[key] = data.history[repo].partners(path, cutoff, exclude_sha=head,
                                                      both_directions=(mode != "trailing_oneside"))
    return data.cache[key]


def cochange_partners(data: Rq1Data, repo: str, path: str, row, mode: str = "trailing") -> list[str]:
    """Ranked co-change partner paths of `path` for one instance.

    Args:
        data: Loaded inputs.
        repo: Repository.
        path: A changed file.
        row: The instance row (needs `run_id`, `run_started_at`).
        mode: As :func:`partner_stats`, or `static` (legacy: the table mined to the corpus
            pin, whose window ends after most runs started; it LEAKS).

    Returns:
        Partner paths, best first.
    """
    if mode == "static":
        return data.co_lookup.get(repo, {}).get(path, [])
    return [p.path for p in partner_stats(data, repo, path, row, mode)]


def historical_evidence(data: Rq1Data, repo: str, row, hist: str = "strict") -> pd.DataFrame:
    """The rows the historical-frequency baseline may read for one instance.

    Args:
        data: Loaded inputs.
        repo: Repository.
        row: The instance row (needs `run_started_at`).
        hist: `strict` (strict labels once each) or `legacy` (all splits).

    Returns:
        Rows of the same repo with `run_started_at` strictly before the instance's.
    """
    frame = data.hist_legacy if hist == "legacy" else data.hist_all
    return frame[(frame['repo'] == repo) & (frame['run_started_at'] < row['run_started_at'])]


def evaluate_k(data: Rq1Data, run_to_gt: dict, k: int, cochange: str = "trailing", hist: str = "strict") -> pd.DataFrame:
    """One row per instance on which the all-partners proxy fires at `k`.

    Args:
        data: Loaded inputs.
        run_to_gt: From :func:`ground_truth`.
        k: Partners kept per changed file.
        cochange: See :func:`cochange_partners`.
        hist: See :func:`historical_evidence`.

    Returns:
        Columns repo, run_id, language, n_gt, n_files and for each method in METHODS
        `<m>_p`, `<m>_r`, `<m>_j`, `<m>_size`, `<m>_hit`.
    """
    if cochange not in COCHANGE_MODES or hist not in HIST_MODES:
        raise ValueError(f"unknown mode: cochange={cochange!r}, hist={hist!r}")
    rows = []
    for _, row in data.valid_runs.iterrows():
        repo, run_id, pr = row['repo'], row['run_id'], str(row['pr_number'])
        GT = run_to_gt.get((repo, run_id))
        if not GT:
            continue
        F = data.pr_to_changed.get((repo, pr))
        if not F:
            continue

        C_co, C_test, C_loose = set(), set(), set()
        for f in sorted(F):
            partners = cochange_partners(data, repo, f, row, cochange)
            if partners:
                C_co.update(partners[:k])
                C_test.update([b for b in partners if is_conventional_test_file(b)][:k])
                C_loose.update([b for b in partners if is_test_filename(b)][:k])
        C_co -= F
        C_test -= F
        C_loose -= F
        if len(C_co) == 0:
            continue  # conditional on the proxy firing

        h = historical_evidence(data, repo, row, hist)
        C_b2 = set(h['resolved_path'].value_counts().head(k).index.tolist()) if len(h) > 0 else set()

        rec = {'repo': repo, 'run_id': run_id, 'language': data.language_of.get(run_id), 'n_gt': len(GT),
               'n_files': len(F), 'co_test_fires': len(C_test) > 0}
        for key, C in (('co', C_co), ('co_test', C_test), ('co_test_loose', C_loose), ('b1', F), ('b2', C_b2)):
            p, r, j = compute_metrics(C, GT)
            rec.update({f'{key}_p': p, f'{key}_r': r, f'{key}_j': j, f'{key}_size': len(C),
                        f'{key}_hit': len(C & GT)})
        rows.append(rec)
    return pd.DataFrame(rows)


def _method_row(df: pd.DataFrame, key: str, label: str) -> list:
    hits, pred, act = int(df[f'{key}_hit'].sum()), int(df[f'{key}_size'].sum()), int(df['n_gt'].sum())
    return [label, len(df), f"{df[f'{key}_p'].mean():.3f}", f"{df[f'{key}_r'].mean():.3f}",
            f"{df[f'{key}_j'].mean():.3f}", paper_md.rate(hits, pred), paper_md.rate(hits, act),
            f"{df[f'{key}_size'].median():g}"]


METHOD_COLS = ["method", "n", "mean P", "mean R", "mean J", "micro P (hits/predicted)",
               "micro R (hits/actual)", "median size"]


def summarize(df: pd.DataFrame) -> list[list]:
    """The method rows for one slice of instances."""
    return [_method_row(df, key, label) for key, label in METHODS]


def size_strata(df: pd.DataFrame) -> list[tuple[str, pd.DataFrame]]:
    """Split instances by number of changed files: 1, 2-5, 6-20, >20."""
    return [(name, df[(df['n_files'] >= lo) & (df['n_files'] <= hi)]) for name, lo, hi in SIZE_STRATA]


def applicability(data: Rq1Data, run_to_gt: dict, mode: str = "trailing") -> dict:
    """Axis 1: how many changed files have a co-change partner at all (per instance, as of its start).

    Args:
        data: Loaded inputs.
        run_to_gt: From :func:`ground_truth`; only instances with ground truth are counted.
        mode: `trailing` / `trailing_oneside` / `static` as in :func:`cochange_partners`.

    Returns:
        `tot` changed files, `ge3` / `ge2` of them with a partner of support >= 3 / >= 2,
        `dist` partners-per-file histogram, `instances` counted, `silent` instances
        with no partner on any changed file.
    """
    files, silent = [], []
    for _, row in data.valid_runs.iterrows():
        repo = row['repo']
        if (repo, row['run_id']) not in run_to_gt:
            continue
        F = data.pr_to_changed.get((repo, str(row['pr_number'])), set())
        has_partner = False
        for f in sorted(F):
            if mode == "static":
                supports = data.co_support_map.get((repo, f), [])
            else:
                supports = [p.support for p in partner_stats(data, repo, f, row, mode)]
            files.append({'ge_3': sum(1 for s in supports if s >= 3), 'ge_2': sum(1 for s in supports if s >= 2),
                          'all': len(supports)})
            has_partner = has_partner or len(supports) > 0
        silent.append(not has_partner)
    df = pd.DataFrame(files)
    dist = pd.cut(df['all'], bins=[0, 1, 3, 6, 11, np.inf], labels=['0', '1-2', '3-5', '6-10', '11+'], right=False)
    return {'tot': len(df), 'ge3': int((df['ge_3'] > 0).sum()), 'ge2': int((df['ge_2'] > 0).sum()),
            'dist': dist.value_counts().sort_index(), 'instances': len(silent), 'silent': int(sum(silent))}


def write_rq1_md(data: Rq1Data, run_to_gt: dict, per_k: dict[int, pd.DataFrame], app: dict | None = None) -> None:
    """Write `paper/generated/rq1.md`: denominators, applicability, then results overall, per language and by change size."""
    n_gt = sum(1 for (repo, rid) in run_to_gt if (repo, rid) in
               {(r['repo'], r['run_id']) for _, r in data.valid_runs.iterrows()})
    gt_files = [p for paths in run_to_gt.values() for p in paths]
    n_conv = sum(1 for p in gt_files if is_conventional_test_file(p))
    n_loose = sum(1 for p in gt_files if is_test_filename(p))
    text = paper_md.header("RQ1: co-change divergence and baselines", "analysis/rq1_divergence.py")
    text += "\n## Denominators\n\n"
    rows = [["strict instances (distinct run_ids with a strict label)", data.n_strict_instances,
             paper_md.rate(data.n_strict_instances, data.n_strict_instances)],
            ["with ground truth (>= 1 strict label bound to a test file)", n_gt,
             paper_md.rate(n_gt, data.n_strict_instances)]]
    for k, df in per_k.items():
        rows.append([f"proxy fires at k={k} (non-empty co-change set after removing changed files; also needs a changeset)",
                     len(df), paper_md.rate(len(df), n_gt)])
    text += paper_md.table(["denominator", "n", "share of its parent (strict instances for GT; GT instances for fires)"],
                           rows)
    text += ("\nAll methods are scored on the SAME instances (those where the all-partners proxy "
             "fires), so n is identical across methods within a k. Mean P/R/J are macro means over "
             "instances; micro P and R pool hits over all instances.\n")
    if app:
        text += "\n## Applicability (Axis 1)\n\n" + paper_md.table(["measure", "n/d"], [
            ["changed files with >= 1 partner at support >= 3", paper_md.rate(app['ge3'], app['tot'])],
            ["changed files with >= 1 partner at support >= 2", paper_md.rate(app['ge2'], app['tot'])],
            ["instances where the proxy is entirely silent", paper_md.rate(app['silent'], app['instances'])]])
        text += "\nPartners-per-changed-file distribution (any support):\n\n" + paper_md.table(
            ["partners", "changed files"], [[k, paper_md.rate(int(v), app['tot'])] for k, v in app['dist'].items()])
    text += ("\n## Leakage control\n\nCo-change partners are mined per instance from commits with committer time "
             "strictly before that instance's `run_started_at` (trailing 365 days, support >= 2, commits over 50 "
             "files skipped; `analysis/cochange_trailing.py`). The historical-frequency baseline reads strict "
             "labels of instances that started strictly earlier, each (test, instance) failure once. "
             "`leakage_audit.md` asserts both per instance.\n")
    text += ("\n## Test-file predicates\n\nPrimary test-only variant: `is_conventional_test_file` "
             "(`src/parse/changeset.py`): Java/Kotlin/Groovy under `src/test/` or named `*Test`, `*Tests`, `Test*`, `*IT`; "
             "Python `test_*.py`, `*_test.py`, or `.py` under a `tests/` or `test/` directory. It accepts "
             f"{paper_md.rate(n_conv, len(gt_files))} ground-truth (instance, file) pairs. "
             "Sensitivity row: `is_test_filename` (`\"test\"` in the lowercased path), which accepts "
             f"{paper_md.rate(n_loose, len(gt_files))}. A pair a predicate rejects can never be recalled by that variant.\n")
    for k, df in per_k.items():
        text += f"\n## k = {k}\n\n### Overall\n\n" + paper_md.table(METHOD_COLS, summarize(df))
        fires = int(df['co_test_fires'].sum())
        text += (f"\nThe conventional-test-restricted co-change set is non-empty on {paper_md.rate(fires, len(df))} "
                 "of these instances (an empty set scores P=R=J=0 here).\n")
        for lang in sorted(df['language'].dropna().unique()):
            sub = df[df['language'] == lang]
            text += f"\n### {lang} (n={len(sub)})\n\n" + paper_md.table(METHOD_COLS, summarize(sub))
    if 10 in per_k:
        df = per_k[10]
        text += ("\n## Change size (k = 10)\n\nStrata by number of changed files in the PR; "
                 f"the strata partition the {len(df)} scored instances.\n")
        for name, sub in size_strata(df):
            text += f"\n### {name} changed files (n={len(sub)})\n\n"
            if len(sub):
                text += paper_md.table(METHOD_COLS, summarize(sub))
            else:
                text += "No instances in this stratum.\n"
    paper_md.write("rq1.md", text)


def main():
    print("Loading data...")
    data = load_data()
    strict_labels, valid_runs = data.strict_labels, data.valid_runs
    bound, pr_to_changed = data.bound, data.pr_to_changed
    co_support_map = data.co_support_map
    run_to_gt = ground_truth(data)

    # --------------------------------------------------------------------------
    # AXIS 1: APPLICABILITY
    # --------------------------------------------------------------------------
    print("\nAXIS 1 - APPLICABILITY")
    app = applicability(data, run_to_gt)
    tot, ge3_cnt, ge2_cnt = app['tot'], app['ge3'], app['ge2']
    print(f"Total changed files in instances with GT: {tot}")
    print(f">=1 partner at support >=3: {ge3_cnt} / {tot} ({ge3_cnt/tot:.1%})")
    print(f">=1 partner at support >=2: {ge2_cnt} / {tot} ({ge2_cnt/tot:.1%})")
    print("Distribution of partners-per-changed-file (any support):")
    dist_counts = app['dist']
    print(dist_counts)
    silent_cnt, tot_inst = app['silent'], app['instances']
    print(f"Instances with at least one changed file with any partner: {tot_inst - silent_cnt} / {tot_inst} ({(tot_inst - silent_cnt)/tot_inst:.1%})")
    print(f"Proxy is entirely silent on {silent_cnt} / {tot_inst} ({silent_cnt/tot_inst:.1%}) of instances.")

    # --------------------------------------------------------------------------
    # AXIS 2: ACCURACY & BASELINES
    # --------------------------------------------------------------------------
    print("\nAXIS 2 - ACCURACY & NULL BASELINES (conditional on proxy firing)")
    co_perf, ct_perf, b1_perf, b2_perf = [], [], [], []
    per_k = {}
    for k in K_VALS:
        df = evaluate_k(data, run_to_gt, k)
        per_k[k] = df
        n = len(df)
        print(f"\n=== k={k} (n={n}) ===")
        if n > 0:
            for key, label in (("co", "Co-change"), ("co_test", "Co-change (conventional test files only)"),
                               ("co_test_loose", "Co-change ('test' in path; sensitivity)"),
                               ("b1", "Baseline 1 (Changeset)"), ("b2", "Baseline 2 (Historical Top-k)")):
                print(f"{label}: Precision: {df[f'{key}_p'].mean():.3f}, Recall: {df[f'{key}_r'].mean():.3f}, "
                      f"Jaccard: {df[f'{key}_j'].mean():.3f} (Med size: {float(df[f'{key}_size'].median())})")
            co_perf.append((df['co_p'].mean(), df['co_r'].mean()))
            ct_perf.append((df['co_test_p'].mean(), df['co_test_r'].mean()))
            b1_perf.append((df['b1_p'].mean(), df['b1_r'].mean()))
            b2_perf.append((df['b2_p'].mean(), df['b2_r'].mean()))

    write_rq1_md(data, run_to_gt, per_k, app)
    print("\nWrote paper/generated/rq1.md")

    # --------------------------------------------------------------------------
    # FIGURES (optional — see write_figures)
    # --------------------------------------------------------------------------
    write_figures(dist_counts, K_VALS, co_perf, b1_perf, b2_perf, ct_perf)


if __name__ == '__main__':
    main()
