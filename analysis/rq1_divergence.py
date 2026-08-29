# UNVALIDATED: never successfully run to completion as of this commit
import pandas as pd

def compute_metrics(C, F):
    overlap = C & F
    precision = len(overlap) / len(C) if C else 0.0
    recall = len(overlap) / len(F) if F else 0.0
    jaccard = len(overlap) / len(C | F) if (C or F) else 0.0
    return precision, recall, jaccard

def evaluate_k(k, resolved, run_to_failing_files, pr_to_changed_files, co_lookup):
    results = []
    
    for _, row in resolved.iterrows():
        repo = row['repo']
        run_id = row['run_id']
        pr = str(row['pr_number'])
        
        # Ground truth F
        F = run_to_failing_files.get((repo, run_id))
        if not F:
            continue
            
        # Changed files
        changed_files = pr_to_changed_files.get((repo, pr))
        if not changed_files:
            continue
            
        # Co-change impact set C
        C = set()
        if repo in co_lookup:
            for f in changed_files:
                # Top k for this file_a
                if f in co_lookup[repo]:
                    top_k = co_lookup[repo][f][:k]
                    C.update(top_k)
                    
        p, r, j = compute_metrics(C, F)
        results.append({
            'repo': repo,
            'precision': p,
            'recall': r,
            'jaccard': j
        })
        
    res_df = pd.DataFrame(results)
    return res_df

def main():
    print("Loading datasets...")
    base_res = pd.read_parquet('data/interim/base_resolution.parquet')
    outcomes = pd.read_parquet('data/interim/parsed_outcomes.parquet')
    binding = pd.read_parquet('data/interim/binding.parquet')
    cochange = pd.read_parquet('data/interim/cochange.parquet')
    changesets = pd.read_parquet('data/interim/changesets.parquet')
    
    # We only use instances where a base run resolved
    resolved = base_res[base_res['status'].isin(['exact', 'ancestor'])]
    
    # Need to join with instances_raw to get pr_number
    instances = pd.read_parquet('data/interim/instances_raw.parquet')
    resolved = resolved.merge(instances[['run_id', 'pr_number']], on='run_id', how='left')
    
    # Filter binding for only resolved paths
    bound = binding[binding['status'] == 'exact'].set_index(['repo', 'test_id'])['resolved_path'].to_dict()
    
    # Actually failing tests mapping (head-side failures, not fault-revealing)
    fails = outcomes[outcomes['status'].isin(['fail', 'error'])]
    run_to_failing_files = {}
    for _, row in fails.iterrows():
        key = (row['repo'], row['run_id'])
        tid = row['test_id']
        path = bound.get((row['repo'], tid))
        if path:
            if key not in run_to_failing_files:
                run_to_failing_files[key] = set()
            run_to_failing_files[key].add(path)
            
    # Changed files from changesets.parquet (HONESTY REQUIREMENT)
    pr_to_changed_files = {}
    for _, row in changesets.iterrows():
        key = (row['repo'], str(row['pr_number']))
        if key not in pr_to_changed_files:
            pr_to_changed_files[key] = set()
        pr_to_changed_files[key].add(row['filename'])
        
    # Process cochange into a lookup: repo -> file_a -> top k file_b
    # Sort by conf_a_to_b globally for each group
    co_lookup = {}
    for repo, group in cochange.groupby('repo_full'):
        repo_lookup = {}
        for file_a, a_group in group.groupby('file_a'):
            # sort and keep max 20 so we can slice for k=5,10,20
            top = a_group.sort_values('conf_a_to_b', ascending=False).head(20)
            repo_lookup[file_a] = top['file_b'].tolist()
        co_lookup[repo] = repo_lookup
        
    print("Evaluating RQ1 metrics...")
    # NOTE: The "tests that actually failed" set is head-side only 
    # and is NOT yet the fault-revealing set of 21.1.
    
    for k in [5, 10, 20]:
        df = evaluate_k(k, resolved, run_to_failing_files, pr_to_changed_files, co_lookup)
        
        n = len(df)
        print(f"\n=== k={k} (n={n}) [head-side failures, not fault-revealing] ===")
        if n == 0:
            print("No valid instances found.")
            continue
            
        print("\nPer-repo overlap statistics:")
        for repo, group in df.groupby('repo'):
            print(f"  {repo} (n={len(group)}):")
            print(f"    Precision: {group['precision'].mean():.4f}")
            print(f"    Recall:    {group['recall'].mean():.4f}")
            print(f"    Jaccard:   {group['jaccard'].mean():.4f}")
            
        print(f"\nPooled statistics (n={n}):")
        print(f"  Precision: {df['precision'].mean():.4f}")
        print(f"  Recall:    {df['recall'].mean():.4f}")
        print(f"  Jaccard:   {df['jaccard'].mean():.4f}")

if __name__ == "__main__":
    main()
