import argparse
import pandas as pd
import numpy as np
import time
import datetime
from src.harvest.rawstore import RawStore
from src.label.base_resolve import resolve_base_run, build_commit_graph, build_run_index, parse_iso
from src.harvest.ratelimit import TokenPool, get_with_backoff

def run(sample_100: bool = False):
    print("Loading data...")
    df_res = pd.read_parquet('data/interim/base_resolution_new.parquet')
    df_inst = pd.read_parquet('data/interim/instances_raw.parquet')
    
    df_no_base = df_res[df_res['status'] == 'no_base']
    df = pd.merge(df_no_base[['run_id', 'repo']], df_inst, on=['run_id', 'repo'], how='inner')
    
    groups = df.groupby(['repo', 'workflow_id', 'base_ref']).size().sort_values(ascending=False)
    
    if sample_100:
        indices = np.linspace(0, len(groups) - 1, 100, dtype=int)
        sampled_groups = groups.iloc[indices]
        group_keys = sampled_groups.index.tolist()
        df = df[df.set_index(['repo', 'workflow_id', 'base_ref']).index.isin(group_keys)].copy()
        print(f"Sampled 100 groups covering {len(df)} instances.")
    
    store = RawStore()
    pool = TokenPool.from_env()
    
    repos = df['repo'].unique()
    results = []
    
    start_time = time.time()
    req_count = 0
    group_count = 0
    
    for repo in repos:
        repo_df = df[df['repo'] == repo]
        commit_graph = build_commit_graph(repo, store=store)
        
        for (wf_id, branch), group_df in repo_df.groupby(['workflow_id', 'base_ref']):
            latest_ts = group_df['run_started_at'].max()
            if not latest_ts: continue
            
            latest_dt = datetime.datetime.fromtimestamp(parse_iso(latest_ts), tz=datetime.timezone.utc)
            day_str = latest_dt.strftime('%Y-%m-%d')
            
            url = f"https://api.github.com/repos/{repo}/actions/workflows/{wf_id}/runs"
            params = {"branch": branch, "created": f"<={day_str}", "per_page": 100}
            
            unresolved = group_df.copy()
            # precompute ancestors
            instance_ancestors = {}
            for _, row in unresolved.iterrows():
                base_sha = row['base_sha']
                ancestors = [base_sha]
                curr = base_sha
                for _ in range(10):
                    parents = commit_graph.get(curr, [])
                    if not parents: break
                    curr = parents[0]
                    ancestors.append(curr)
                instance_ancestors[row['run_id']] = ancestors
                
            fetched_runs = []
            pages_fetched = 0
            
            while url and not unresolved.empty:
                res = get_with_backoff(url, params=params if 'created' in url else None, pool=pool)
                req_count += 1
                if res.status_code != 200: break
                
                runs = res.json().get("workflow_runs", [])
                if not runs: break
                fetched_runs.extend(runs)
                pages_fetched += 1
                
                # Check unresolved instances against fetched_runs
                resolved_idx = []
                for idx, row in unresolved.iterrows():
                    head_ts = parse_iso(row['run_started_at'])
                    ancs = instance_ancestors[row['run_id']]
                    best_run = None
                    best_dist = None
                    
                    for run_obj in fetched_runs:
                        run_ts_str = run_obj.get("run_started_at") or run_obj.get("created_at")
                        if not run_ts_str: continue
                        run_ts = parse_iso(run_ts_str)
                        if run_ts >= head_ts: continue
                        if run_obj.get("id") == row["run_id"]: continue
                        
                        run_head = run_obj.get("head_sha")
                        if run_head in ancs:
                            best_run = run_obj
                            best_dist = ancs.index(run_head)
                            break
                            
                    if best_run:
                        status = "exact" if best_dist == 0 else "ancestor"
                        results.append({
                            'run_id': row['run_id'], 'repo': repo, 'status': status,
                            'base_sha': best_run['head_sha'], 'base_run_id': best_run['id'],
                            'base_run_distance': best_dist
                        })
                        resolved_idx.append(idx)
                        
                unresolved = unresolved.drop(resolved_idx)
                
                if pages_fetched >= 34: # ~1000 items
                    break
                    
                url = None
                if "Link" in res.headers:
                    for link in res.headers["Link"].split(","):
                        if 'rel="next"' in link:
                            url = link[link.index('<')+1:link.index('>')]
                            params = None
                            break

            # Any remaining unresolved instances get no_base
            for _, row in unresolved.iterrows():
                results.append({
                    'run_id': row['run_id'], 'repo': repo, 'status': 'no_base',
                    'base_sha': row['base_sha'], 'base_run_id': None, 'base_run_distance': None
                })
                
            group_count += 1
            if group_count % 10 == 0 or group_count == 100:
                elapsed = time.time() - start_time
                rpm = (req_count / elapsed) * 60 if elapsed > 0 else 0
                print(f"Group {group_count}/100 done. Reqs: {req_count}, Elapsed: {elapsed:.1f}s, RPM: {rpm:.1f}")

    end_time = time.time()
    res_df = pd.DataFrame(results)
    print(f"\nCompleted in {end_time - start_time:.2f}s. Total requests: {req_count}")
    print("\nNew distribution:")
    print(res_df['status'].value_counts(normalize=True).mul(100).round(2).astype(str) + '% (' + res_df['status'].value_counts().astype(str) + ')')
    print("\nDistance distribution:")
    print(res_df['base_run_distance'].value_counts())
    res_df.to_parquet('data/interim/base_resolution_new_sampled.parquet')
    return res_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-100", action="store_true")
    args = parser.parse_args()
    run(sample_100=args.sample_100)
