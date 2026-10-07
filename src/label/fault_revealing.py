import pandas as pd
import numpy as np

def compute_labels(res_df, instances_df, head_parsed, base_parsed):
    # Filter head_parsed and base_parsed to only those in res_df
    
    # 1. T_head_fail
    head_fail = head_parsed.groupby(['run_id', 'test_id']).size().reset_index(name='n_legs_head')
    
    # 2. T_base_fail
    base_fail = base_parsed.groupby(['run_id', 'test_id']).size().reset_index(name='n_legs_base')
    
    runs_with_base_outcomes = set(base_parsed['run_id'].unique())

    # Inclusion criterion: the HEAD run must have executed tests. A run that
    # parsed to NO_TEST_OUTPUT cannot yield a fault-revealing label, so it is
    # excluded from the corpus rather than labelled. This is a corpus-inclusion
    # rule, distinct from invariant 6, which governs the BASE side.
    runs_with_head_outcomes = set(head_parsed['run_id'].unique())

    valid_runs = []
    no_output_count = 0
    head_no_tests_count = 0

    # Invariant 6: status == 'no_base' -> emit NO labels.

    for _, row in res_df.iterrows():
        r_id = row['run_id']
        status = row['status']
        if status == 'no_base':
            continue
        if r_id not in runs_with_head_outcomes:
            head_no_tests_count += 1
            continue
        elif status == 'exact_green':
            valid_runs.append(r_id)
        elif status in ['exact', 'ancestor', 'branch_prior']:
            if r_id in runs_with_base_outcomes:
                valid_runs.append(r_id)
            else:
                no_output_count += 1
                
    valid_runs_set = set(valid_runs)
    
    # Assert Invariant 6: no run with status 'no_base' is in valid_runs
    no_base_runs = set(res_df[res_df['status'] == 'no_base']['run_id'])
    assert len(no_base_runs.intersection(valid_runs_set)) == 0, "Invariant 6 violated: no_base run in valid_runs"
    
    head_labels = head_fail[head_fail['run_id'].isin(valid_runs_set)].copy()
    
    # Split: ALL
    all_labels = head_labels[['run_id', 'test_id']].copy()
    all_labels['split'] = 'all'
    
    # Split: RELAXED
    base_fail_set = set(zip(base_fail['run_id'], base_fail['test_id']))
    
    if len(head_labels) > 0:
        head_labels['in_base'] = head_labels.apply(lambda x: (x['run_id'], x['test_id']) in base_fail_set, axis=1)
    else:
        head_labels['in_base'] = False

    relaxed_labels = head_labels[~head_labels['in_base']][['run_id', 'test_id']].copy()
    relaxed_labels['split'] = 'relaxed'
    
    # Flaky detection
    # df with head_sha
    df = pd.merge(res_df, instances_df[['run_id', 'head_sha', 'workflow_id']], on='run_id', how='left')
    runs_per_sha = df.groupby(['head_sha', 'workflow_id'])['run_id'].nunique().reset_index(name='n_runs_for_sha')
    head_fail_with_sha = pd.merge(head_fail, df[['run_id', 'head_sha', 'workflow_id']], on='run_id', how='inner')
    fails_per_sha_test = head_fail_with_sha.groupby(['head_sha', 'workflow_id', 'test_id'])['run_id'].nunique().reset_index(name='n_fail_runs')
    flips = pd.merge(fails_per_sha_test, runs_per_sha, on=['head_sha', 'workflow_id'])
    flips['is_flip'] = flips['n_fail_runs'] < flips['n_runs_for_sha']
    
    flip_count = flips['is_flip'].sum()
    flip_rate = flip_count / len(flips) if len(flips) > 0 else 0
    
    flaky_pairs = set(zip(flips[flips['is_flip']]['head_sha'], flips[flips['is_flip']]['test_id']))
    
    # Split: STRICT
    def is_flaky(row):
        run_id = row['run_id']
        test_id = row['test_id']
        # get head_sha for this run
        shas = df[df['run_id'] == run_id]['head_sha']
        if len(shas) == 0: return False
        return (shas.iloc[0], test_id) in flaky_pairs

    if len(relaxed_labels) > 0:
        strict_mask = ~relaxed_labels.apply(is_flaky, axis=1)
        strict_labels = relaxed_labels[strict_mask][['run_id', 'test_id']].copy()
    else:
        strict_labels = relaxed_labels.copy()
    strict_labels['split'] = 'strict'
    
    outcomes = pd.concat([all_labels, relaxed_labels, strict_labels])
    
    return outcomes, {
        "head_no_tests_count": head_no_tests_count,
        "no_output_count": no_output_count,
        "flip_count": flip_count,
        "flip_rate": flip_rate,
        "n_sha_test_pairs": len(flips),
        "n_matrix_legs_handled": head_parsed['run_id'].duplicated(keep=False).sum() # approximate
    }

GATE1_THRESHOLD = 5000


def write_flakiness_md(outcomes: pd.DataFrame, stats: dict, out_dir=None) -> None:
    """Write `paper/generated/flakiness.md` (same-SHA flips and what they remove).

    Args:
        outcomes: The `outcomes` frame.
        stats: The stats dict returned by :func:`compute_labels`.
        out_dir: Output directory (default `paper/generated`).
    """
    from analysis import paper_md

    relaxed = int((outcomes['split'] == 'relaxed').sum())
    strict = int((outcomes['split'] == 'strict').sum())
    flips, pairs = int(stats['flip_count']), int(stats['n_sha_test_pairs'])
    text = paper_md.header(
        "Flakiness: same-SHA flips", "src/label/fault_revealing.py",
        "A (head SHA, workflow, test) is a flip when it fails in some but not all runs of that "
        "workflow on that SHA. Strict labels are the relaxed labels minus flips.")
    text += "\n" + paper_md.table(
        ["measure", "n/d"],
        [["same-SHA flips over (head SHA, workflow, test) groups with a failure", paper_md.rate(flips, pairs)],
         ["relaxed labels removed as flaky (relaxed -> strict)", paper_md.rate(relaxed - strict, relaxed)]])
    paper_md.write("flakiness.md", text, *([out_dir] if out_dir else []))




def gate1_lines(outcomes: pd.DataFrame) -> list[str]:
    """Gate 1 report lines: labels (D-44, primary) then instances, both vs 5,000.

    Args:
        outcomes: The `outcomes` frame (columns run_id, test_id, split).

    Returns:
        Two printable lines.
    """
    strict = outcomes[outcomes['split'] == 'strict']
    labels, instances = len(strict), strict['run_id'].nunique()

    def met(n: int) -> str:
        return 'Yes' if n >= GATE1_THRESHOLD else 'No'

    return [
        f"Gate 1 (D-44, primary) labels: {labels} / {GATE1_THRESHOLD} (Met? {met(labels)})",
        f"Gate 1 (secondary) instances: {instances} / {GATE1_THRESHOLD} (Met? {met(instances)})",
    ]


if __name__ == '__main__':
    res = pd.read_parquet('data/interim/base_resolution_new.parquet')
    instances = pd.read_parquet('data/interim/instances_raw.parquet')
    head_parsed = pd.read_parquet('data/interim/parsed_outcomes.parquet')
    base_parsed = pd.read_parquet('data/interim/base_outcomes.parquet')
    
    outcomes, stats = compute_labels(res, instances, head_parsed, base_parsed)
    outcomes.to_parquet('data/interim/outcomes.parquet')
    
    print("Done writing data/interim/outcomes.parquet")
    print(f"NO_TEST_OUTPUT base runs omitted: {stats['no_output_count']}")
    print(f"Matrix leg rows unioned: {stats['n_matrix_legs_handled']}")
    print(f"Same-SHA flips detected: {stats['flip_count']}/{stats['n_sha_test_pairs']} (Rate: {stats['flip_rate']:.2%})")
    
    for split in ['all', 'relaxed', 'strict']:
        split_df = outcomes[outcomes['split'] == split]
        instances_cnt = split_df['run_id'].nunique()
        labels_cnt = len(split_df)
        distinct_tests = split_df['test_id'].nunique()
        print(f"Split {split}: {instances_cnt} instances, {labels_cnt} labels, {distinct_tests} distinct tests")
        
    for line in gate1_lines(outcomes):
        print(line)

    write_flakiness_md(outcomes, stats)
