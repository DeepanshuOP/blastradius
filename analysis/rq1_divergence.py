"""RQ1 divergence measurement: the co-change proxy on two axes, plus null baselines.

Every number this script prints regenerates without matplotlib, and everything
it prints as a result is also written to `paper/generated/rq1.md`. Figures are
optional: `write_figures` imports matplotlib lazily and skips with a warning if
it is absent, so `make tables` emits the full measurement on a fresh clone with
no plotting stack. Numbers are the paper; figures are a convenience.

Four predictors are compared at k in {5, 10, 20} on ONE common set of
instances (those where the all-partners co-change proxy fires), so their rows
are comparable:
  - co-change, all partner files;
  - co-change restricted to test files (`is_test_filename`, the pipeline's
    only file-level test predicate; restriction is applied BEFORE the top-k cut,
    so the k slots are spent on test files);
  - changeset baseline (the PR's changed files);
  - historical-frequency baseline (the k most frequently failing bound test
    files of the repo before the run).
"""

import os
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from analysis import paper_md
from src.parse.changeset import is_test_filename

K_VALS = [5, 10, 20]
METHODS = [
    ("co", "co-change, all partner files"),
    ("co_test", "co-change, restricted to test files"),
    ("b1", "changeset baseline"),
    ("b2", "historical-frequency baseline"),
]

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
    hist_all: pd.DataFrame
    language_of: dict
    n_strict_instances: int
    valid_runs: pd.DataFrame = field(default=None)


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
    for _, row in changesets.iterrows():
        key = (row['repo'], str(row['pr_number']))
        if key not in pr_to_changed:
            pr_to_changed[key] = set()
        pr_to_changed[key].add(row['filename'])

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

    all_outcomes = pd.merge(outcomes, instances[['run_id', 'repo', 'run_started_at']], on='run_id', how='inner')
    hist_all = all_outcomes.copy()
    hist_all['resolved_path'] = hist_all.apply(lambda r: bound.get((r['repo'], r['test_id'])), axis=1)
    hist_all = hist_all.dropna(subset=['resolved_path'])

    valid_runs = strict_labels.drop_duplicates(subset=['run_id'])
    language_of = instances.drop_duplicates('run_id').set_index('run_id')['language'].to_dict()
    return Rq1Data(strict_labels, bound, pr_to_changed, co_support_map, co_lookup, hist_all,
                   language_of, len(valid_runs), valid_runs)


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


def evaluate_k(data: Rq1Data, run_to_gt: dict, k: int) -> pd.DataFrame:
    """One row per instance on which the all-partners proxy fires at `k`.

    Args:
        data: Loaded inputs.
        run_to_gt: From :func:`ground_truth`.
        k: Partners kept per changed file.

    Returns:
        Columns repo, run_id, language, n_gt, and for each method in METHODS
        `<m>_p`, `<m>_r`, `<m>_j`, `<m>_size`, `<m>_hit`, `<m>_pred`.
    """
    rows = []
    for _, row in data.valid_runs.iterrows():
        repo, run_id, pr = row['repo'], row['run_id'], str(row['pr_number'])
        GT = run_to_gt.get((repo, run_id))
        if not GT:
            continue
        F = data.pr_to_changed.get((repo, pr))
        if not F:
            continue

        C_co, C_test = set(), set()
        for f in F:
            partners = data.co_lookup.get(repo, {}).get(f)
            if partners:
                C_co.update(partners[:k])
                C_test.update([b for b in partners if is_test_filename(b)][:k])
        C_co -= F
        C_test -= F
        if len(C_co) == 0:
            continue  # conditional on the proxy firing

        hist = data.hist_all[(data.hist_all['repo'] == repo) & (data.hist_all['run_started_at'] < row['run_started_at'])]
        C_b2 = set(hist['resolved_path'].value_counts().head(k).index.tolist()) if len(hist) > 0 else set()

        rec = {'repo': repo, 'run_id': run_id, 'language': data.language_of.get(run_id), 'n_gt': len(GT),
               'co_test_fires': len(C_test) > 0}
        for key, C in (('co', C_co), ('co_test', C_test), ('b1', F), ('b2', C_b2)):
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
    """The four method rows for one slice of instances."""
    return [_method_row(df, key, label) for key, label in METHODS]


def write_rq1_md(data: Rq1Data, run_to_gt: dict, per_k: dict[int, pd.DataFrame]) -> None:
    """Write `paper/generated/rq1.md`: denominators, then results overall and per language."""
    n_gt = sum(1 for (repo, rid) in run_to_gt if (repo, rid) in
               {(r['repo'], r['run_id']) for _, r in data.valid_runs.iterrows()})
    gt_files = [p for paths in run_to_gt.values() for p in paths]
    n_test_gt = sum(1 for p in gt_files if is_test_filename(p))
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
    text += ("\nAll four methods are scored on the SAME instances (those where the all-partners proxy "
             "fires), so n is identical across methods within a k. Mean P/R/J are macro means over "
             "instances; micro P and R pool hits over all instances.\n")
    text += ("\n## Test-file predicate\n\n`is_test_filename` (`src/parse/changeset.py`): `\"test\"` in the lowercased "
             "path. The binding step has no file-level predicate (it resolves ids to files by name), so this "
             "is the pipeline's only one. Coverage of the ground truth by the predicate: "
             f"{paper_md.rate(n_test_gt, len(gt_files))} ground-truth (instance, file) pairs pass it, so the restriction "
             "removes a ground-truth file only to the extent that this fraction is below 100%.\n")
    for k, df in per_k.items():
        text += f"\n## k = {k}\n\n### Overall\n\n" + paper_md.table(METHOD_COLS, summarize(df))
        fires = int(df['co_test_fires'].sum())
        text += (f"\nThe test-restricted co-change set is non-empty on {paper_md.rate(fires, len(df))} "
                 "of these instances (an empty set scores P=R=J=0 here).\n")
        for lang in sorted(df['language'].dropna().unique()):
            sub = df[df['language'] == lang]
            text += f"\n### {lang} (n={len(sub)})\n\n" + paper_md.table(METHOD_COLS, summarize(sub))
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
    all_changed_files = []
    instance_silent = []

    for _, row in valid_runs.iterrows():
        repo = row['repo']
        run_id = row['run_id']
        pr = str(row['pr_number'])
        if (repo, run_id) not in run_to_gt:
            continue

        F = pr_to_changed.get((repo, pr), set())

        instance_has_partner = False
        for f in F:
            supports = co_support_map.get((repo, f), [])
            partners_ge_3 = sum(1 for s in supports if s >= 3)
            partners_ge_2 = sum(1 for s in supports if s >= 2)
            partners_all = len(supports)
            all_changed_files.append({
                'repo': repo, 'file': f,
                'ge_3': partners_ge_3, 'ge_2': partners_ge_2, 'all': partners_all
            })
            if partners_all > 0:
                instance_has_partner = True
        instance_silent.append(not instance_has_partner)

    df_files = pd.DataFrame(all_changed_files)
    tot = len(df_files)
    ge3_cnt = len(df_files[df_files['ge_3'] > 0])
    ge2_cnt = len(df_files[df_files['ge_2'] > 0])
    print(f"Total changed files in instances with GT: {tot}")
    print(f">=1 partner at support >=3: {ge3_cnt} / {tot} ({ge3_cnt/tot:.1%})")
    print(f">=1 partner at support >=2: {ge2_cnt} / {tot} ({ge2_cnt/tot:.1%})")

    bins = [0, 1, 3, 6, 11, np.inf]
    labels = ['0', '1-2', '3-5', '6-10', '11+']
    dist = pd.cut(df_files['all'], bins=bins, labels=labels, right=False)
    print("Distribution of partners-per-changed-file (any support):")
    dist_counts = dist.value_counts().sort_index()
    print(dist_counts)

    silent_cnt = sum(instance_silent)
    tot_inst = len(instance_silent)
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
            for key, label in (("co", "Co-change"), ("co_test", "Co-change (test files only)"),
                               ("b1", "Baseline 1 (Changeset)"), ("b2", "Baseline 2 (Historical Top-k)")):
                print(f"{label}: Precision: {df[f'{key}_p'].mean():.3f}, Recall: {df[f'{key}_r'].mean():.3f}, "
                      f"Jaccard: {df[f'{key}_j'].mean():.3f} (Med size: {float(df[f'{key}_size'].median())})")
            co_perf.append((df['co_p'].mean(), df['co_r'].mean()))
            ct_perf.append((df['co_test_p'].mean(), df['co_test_r'].mean()))
            b1_perf.append((df['b1_p'].mean(), df['b1_r'].mean()))
            b2_perf.append((df['b2_p'].mean(), df['b2_r'].mean()))

    write_rq1_md(data, run_to_gt, per_k)
    print("\nWrote paper/generated/rq1.md")

    # --------------------------------------------------------------------------
    # FIGURES (optional — see write_figures)
    # --------------------------------------------------------------------------
    write_figures(dist_counts, K_VALS, co_perf, b1_perf, b2_perf, ct_perf)


if __name__ == '__main__':
    main()
