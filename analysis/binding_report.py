import pandas as pd
import subprocess
from pathlib import Path
from src.parse.test_ids import normalize_test_id
from src.parse.test_files import resolve_test_file, _get_git_tree

def main():
    print("Loading parsed outcomes...")
    df = pd.read_parquet('data/interim/parsed_outcomes.parquet')
    
    # We only care about distinct test_ids whose repo is cloned.
    # Group by (repo, test_id)
    distinct_tests = df[['repo', 'test_id', 'harness', 'is_fqcn_qualified']].drop_duplicates()
    
    clones_dir = Path('data/clones')
    cloned_repos = [d.name.replace('__', '/') for d in clones_dir.iterdir() if d.is_dir()]
    
    df_cloned = distinct_tests[distinct_tests['repo'].isin(cloned_repos)].copy()
    print(f"Total distinct test_ids in cloned repos: {len(df_cloned)}")
    
    trees = {}
    for repo in cloned_repos:
        repo_root = clones_dir / repo.replace('/', '__')
        try:
            tree_paths = _get_git_tree(repo_root)
        except subprocess.CalledProcessError:
            tree_paths = set()
        tree_idx = {}
        for p in tree_paths:
            basename = p.split("/")[-1]
            if basename not in tree_idx:
                tree_idx[basename] = []
            tree_idx[basename].append(p)
        trees[repo] = tree_idx
            
    paths = []
    statuses = []
    candidates_considered = []
    
    ambiguous_samples = []
    for idx, row in df_cloned.iterrows():
        repo = row['repo']
        tid_raw = row['test_id']
        repo_root = clones_dir / repo.replace('/', '__')
        
        tid = normalize_test_id(tid_raw)
        if not tid:
            paths.append(None)
            statuses.append("unqualified")
            candidates_considered.append(0)
            continue
            
        res = resolve_test_file(tid, repo_root, _tree_cache=trees[repo])
        paths.append(res.path)
        statuses.append(res.status)
        candidates_considered.append(res.candidates_considered)
        
    df_cloned['resolved_path'] = paths
    df_cloned['status'] = statuses
    df_cloned['candidates_considered'] = candidates_considered
    
    df_cloned.to_parquet('data/interim/binding.parquet', index=False)
    print("Wrote data/interim/binding.parquet")

    # Overall binding rate
    exact_count = (df_cloned['status'] == 'exact').sum()
    total = len(df_cloned)
    print(f"\nOverall binding rate: {exact_count} / {total} ({(exact_count/total)*100:.2f}%)")
    
    # Status breakdown
    print("\nStatus breakdown:")
    counts = df_cloned['status'].value_counts()
    for status, count in counts.items():
        print(f"  {status}: {count} ({(count/total)*100:.2f}%)")
        
    # Binding rate per (repo, harness)
    print("\nBinding rate per (repo, harness):")
    grouped = df_cloned.groupby(['repo', 'harness'])
    repo_rates = {}
    for (repo, harness), group in grouped:
        g_exact = (group['status'] == 'exact').sum()
        g_total = len(group)
        rate = g_exact / g_total
        repo_rates[repo] = rate
        print(f"  {repo} [{harness}]: {g_exact} / {g_total} ({rate*100:.2f}%)")
        
    # How many repos fall below 70%
    below_70 = sum(1 for r in repo_rates.values() if r < 0.70)
    print(f"\nRepos below 70% gate: {below_70} / {len(repo_rates)}")
    
    # Binding rate by is_fqcn_qualified
    print("\nBinding rate by is_fqcn_qualified:")
    for fqcn_val, group in df_cloned.groupby('is_fqcn_qualified'):
        g_exact = (group['status'] == 'exact').sum()
        g_total = len(group)
        print(f"  {fqcn_val}: {g_exact} / {g_total} ({(g_exact/g_total)*100:.2f}%)")
        
    # 20 sampled UNBOUND test_ids printed verbatim with their status
    print("\n20 sampled UNBOUND test_ids:")
    unbound = df_cloned[df_cloned['status'] != 'exact'].sample(n=min(20, (df_cloned['status'] != 'exact').sum()), random_state=42)
    for _, row in unbound.iterrows():
        print(f"  Repo: {row['repo']} | Status: {row['status']} | ID: {row['test_id']}")

if __name__ == "__main__":
    main()
