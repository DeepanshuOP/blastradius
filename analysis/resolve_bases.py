import argparse
import pandas as pd
import numpy as np
import time
from src.harvest.rawstore import RawStore
from src.label.base_resolve import resolve_base_run, build_commit_graph, build_run_index, parse_iso
import pyarrow.parquet as pq

def run(as_of: str = None, limit: int = None):
    print("Loading data...")
    # as_of would filter runs if needed, but here we just take the parquet
    df_res = pd.read_parquet('data/interim/base_resolution.parquet')
    df_inst = pd.read_parquet('data/interim/instances_raw.parquet')
    
    df = pd.merge(df_res[['run_id', 'repo']], df_inst[['run_id', 'repo', 'head_sha', 'base_sha', 'workflow_id', 'run_started_at']], on=['run_id', 'repo'], how='inner')
    
    if limit is not None:
        df = df.head(limit)
        
    print(f"Total runs to resolve: {len(df)}")
    
    store = RawStore()
    
    repos = df['repo'].unique()
    results = []
    
    start_time = time.time()
    
    for repo in repos:
        repo_df = df[df['repo'] == repo]
        
        run_index = build_run_index(repo, store=store)
        commit_graph = build_commit_graph(repo, store=store)
        runs_cache = {}
        
        branch_runs = []
        for sha, runs in run_index.items():
            for r in runs:
                ts_str = r.get("run_started_at") or r.get("created_at")
                if ts_str:
                    r["_ts"] = parse_iso(ts_str)
                    r["head_sha"] = sha
                    branch_runs.append(r)
        
        branch_runs.sort(key=lambda x: x["_ts"])
        branch_prior_index = {repo: branch_runs}
        
        for _, row in repo_df.iterrows():
            res = resolve_base_run(
                repo=repo,
                head_sha=row['head_sha'],
                run_id=row['run_id'],
                workflow_id=row['workflow_id'],
                base_sha=row['base_sha'],
                store=store,
                commit_graph=commit_graph,
                run_index=run_index,
                runs_cache=runs_cache,
                branch_prior_index=branch_prior_index
            )
            results.append({
                'run_id': row['run_id'],
                'repo': repo,
                'status': res.status,
                'base_sha': res.base_sha,
                'base_run_id': res.base_run_id,
                'base_run_distance': res.base_run_distance,
                'base_time_gap_seconds': res.base_time_gap_seconds
            })
            
    end_time = time.time()
    print(f"Resolution completed in {end_time - start_time:.2f} seconds")
    
    res_df = pd.DataFrame(results)
    
    # Print summary
    print("New distribution:")
    print(res_df['status'].value_counts(normalize=True).mul(100).round(2).astype(str) + '% (' + res_df['status'].value_counts().astype(str) + ')')
    
    gaps = res_df[res_df['status'] == 'branch_prior']['base_time_gap_seconds']
    if len(gaps) > 0:
        print("base_time_gap_seconds distribution:")
        print(f"min: {gaps.min():.2f}")
        print(f"median: {gaps.median():.2f}")
        print(f"p90: {gaps.quantile(0.9):.2f}")
        print(f"max: {gaps.max():.2f}")
        
    res_df.to_parquet('data/interim/base_resolution_new.parquet')
    return res_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", type=str, help="As of date")
    parser.add_argument("--limit", type=int, help="Limit number of runs")
    args = parser.parse_args()
    run(as_of=args.as_of, limit=args.limit)
