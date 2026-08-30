import pandas as pd
import numpy as np

def compute_metrics(C, GT):
    overlap = C & GT
    precision = len(overlap) / len(C) if C else 0.0
    recall = len(overlap) / len(GT) if GT else 0.0
    jaccard = len(overlap) / len(C | GT) if (C or GT) else 0.0
    return precision, recall, jaccard

def main():
    # Load data
    outcomes = pd.read_parquet('data/interim/outcomes.parquet')
    binding = pd.read_parquet('data/interim/binding.parquet')
    changesets = pd.read_parquet('data/interim/changesets.parquet')
    cochange = pd.read_parquet('data/interim/cochange.parquet')
    instances = pd.read_parquet('data/interim/instances_raw.parquet')
    
    # 4b. Ground truth = source files of FAULT-REVEALING tests from strict split
    strict_labels = outcomes[outcomes['split'] == 'strict'].copy()
    
    # join with instances to get pr_number
    strict_labels = pd.merge(strict_labels, instances[['run_id', 'repo', 'pr_number']], on=['run_id'], how='inner')
    
    # join with binding to get resolved_path
    bound = binding[binding['status'] == 'exact'].set_index(['repo', 'test_id'])['resolved_path'].to_dict()
    
    run_to_gt = {}
    for _, row in strict_labels.iterrows():
        key = (row['repo'], row['run_id'])
        tid = row['test_id']
        path = bound.get((row['repo'], tid))
        if path:
            if key not in run_to_gt:
                run_to_gt[key] = set()
            run_to_gt[key].add(path)
            
    # pr_to_changed_files
    pr_to_changed = {}
    for _, row in changesets.iterrows():
        key = (row['repo'], str(row['pr_number']))
        if key not in pr_to_changed:
            pr_to_changed[key] = set()
        pr_to_changed[key].add(row['filename'])
        
    # Build co_lookup
    # Sort by repo, file_a, confidence descending
    cochange = cochange.sort_values(by=['repo_full', 'file_a', 'conf_a_to_b'], ascending=[True, True, False])
    co_lookup = {}
    for repo, grp in cochange.groupby('repo_full'):
        co_lookup[repo] = {}
        for fa, subgrp in grp.groupby('file_a'):
            co_lookup[repo][fa] = subgrp['file_b'].tolist()
            
    # Calculate denominators for 4d
    total_strict_instances = strict_labels['run_id'].nunique()
    # "what fraction of all labelled instances have co-change data ... and what fraction have binding"
    # Actually, "labelled instances" = strict split instances (144).
    # How many have binding? (i.e. at least one test is in bound)
    runs_with_binding = len(run_to_gt)
    # How many have cochange data?
    repos_with_cochange = set(co_lookup.keys())
    strict_runs_with_cochange = strict_labels[strict_labels['repo'].isin(repos_with_cochange)]['run_id'].nunique()
    
    print(f"Strict labelled instances (n): {total_strict_instances}")
    print(f"Fraction with binding: {runs_with_binding}/{total_strict_instances} ({runs_with_binding/total_strict_instances:.1%})")
    print(f"Fraction with co-change data: {strict_runs_with_cochange}/{total_strict_instances} ({strict_runs_with_cochange/total_strict_instances:.1%})")
    
    def evaluate_k(k):
        results = []
        # We only evaluate runs that have BOTH binding and cochange data and a PR
        valid_runs = strict_labels.drop_duplicates(subset=['run_id'])
        
        for _, row in valid_runs.iterrows():
            repo = row['repo']
            run_id = row['run_id']
            pr = str(row['pr_number'])
            
            # F = ground truth
            GT = run_to_gt.get((repo, run_id))
            if not GT: continue
            
            if repo not in co_lookup: continue
            
            F = pr_to_changed.get((repo, pr))
            if not F: continue
            
            # C = union over f in F of { top-k co-change partners of f by confidence } deduplicated, excluding F itself.
            C = set()
            for f in F:
                if f in co_lookup[repo]:
                    C.update(co_lookup[repo][f][:k])
            
            C = C - F
            
            p, r, j = compute_metrics(C, GT)
            results.append({
                'repo': repo,
                'precision': p,
                'recall': r,
                'jaccard': j,
                'predicted_size': len(C)
            })
            
        return pd.DataFrame(results)

    for k in [5, 10, 20]:
        df = evaluate_k(k)
        n = len(df)
        print(f"\n=== k={k} (n={n}) ===")
        if n < 30:
            print("WARNING: n < 30. This is a PRELIMINARY finding!")
        
        if n > 0:
            p_mean = df['precision'].mean()
            r_mean = df['recall'].mean()
            j_mean = df['jaccard'].mean()
            med_size = df['predicted_size'].median()
            
            print(f"Pooled: Precision: {p_mean:.3f}, Recall: {r_mean:.3f}, Jaccard: {j_mean:.3f}")
            print(f"Median |predicted|: {med_size}")
            
            print("\nPer-repo:")
            repo_grp = df.groupby('repo').agg(
                n=('repo', 'count'),
                precision=('precision', 'mean'),
                recall=('recall', 'mean'),
                jaccard=('jaccard', 'mean'),
                med_size=('predicted_size', 'median')
            )
            print(repo_grp.to_string())

if __name__ == '__main__':
    main()
