import argparse
import datetime
import time
from pathlib import Path
import numpy as np
import pandas as pd

from src.harvest.ratelimit import TokenPool, get_with_backoff
from src.harvest.rawstore import RawStore
from src.label.base_resolve import build_commit_graph, parse_iso


def run(
    limit: int | None = None,
    sample_100: bool = False,
    python_first: bool = True,
    as_of: str | None = None,
    out_parquet: str | None = None,
    pool: TokenPool | None = None,
    store: RawStore | None = None,
) -> pd.DataFrame:
    print("Loading base resolution and instance data...")
    df_res = pd.read_parquet('data/interim/base_resolution_new.parquet')
    df_inst = pd.read_parquet('data/interim/instances_raw.parquet')

    df_no_base = df_res[df_res['status'] == 'no_base']
    df = pd.merge(df_no_base[['run_id', 'repo']], df_inst, on=['run_id', 'repo'], how='inner').drop_duplicates('run_id')

    if python_first:
        # Sort groups: Python first (by group size desc), then other languages (by group size desc)
        group_sizes = df.groupby(['repo', 'workflow_id', 'base_ref', 'language']).size().reset_index(name='size')
        py_groups = group_sizes[group_sizes['language'] == 'Python'].sort_values('size', ascending=False)
        other_groups = group_sizes[group_sizes['language'] != 'Python'].sort_values('size', ascending=False)
        ordered_groups = pd.concat([py_groups, other_groups], ignore_index=True)
    else:
        group_sizes = df.groupby(['repo', 'workflow_id', 'base_ref', 'language']).size().reset_index(name='size')
        ordered_groups = group_sizes.sort_values('size', ascending=False)

    if sample_100:
        indices = np.linspace(0, len(ordered_groups) - 1, 100, dtype=int)
        sampled_groups = ordered_groups.iloc[indices]
        group_keys = set(zip(sampled_groups['repo'], sampled_groups['workflow_id'], sampled_groups['base_ref']))
        df = df[df.apply(lambda r: (r['repo'], r['workflow_id'], r['base_ref']) in group_keys, axis=1)].copy()
        print(f"Sampled 100 groups covering {len(df)} instances.")

    if limit is not None:
        df = df.head(limit).copy()
        print(f"Limiting to first {limit} instances.")

    print(f"Total instances to resolve: {len(df)}")
    if df.empty:
        return pd.DataFrame(columns=['run_id', 'repo', 'status', 'base_sha', 'base_run_id', 'base_run_distance'])

    if store is None:
        store = RawStore()
    if pool is None:
        try:
            pool = TokenPool.from_env()
        except ValueError:
            pool = TokenPool(["dummy_pat_for_test"])

    results = []
    start_time = time.time()
    req_count = 0
    group_count = 0

    # Iterate over unique groups in ordered order
    unique_groups = df[['repo', 'workflow_id', 'base_ref', 'language']].drop_duplicates()
    if python_first:
        py_g = unique_groups[unique_groups['language'] == 'Python']
        oth_g = unique_groups[unique_groups['language'] != 'Python']
        unique_groups = pd.concat([py_g, oth_g], ignore_index=True)

    total_groups = len(unique_groups)

    # Cache commit graphs per repo
    commit_graphs = {}

    for _, group_row in unique_groups.iterrows():
        repo = group_row['repo']
        wf_id = group_row['workflow_id']
        branch = group_row['base_ref']

        group_df = df[(df['repo'] == repo) & (df['workflow_id'] == wf_id) & (df['base_ref'] == branch)]
        if group_df.empty:
            continue

        if repo not in commit_graphs:
            commit_graphs[repo] = build_commit_graph(repo, store=store)
        commit_graph = commit_graphs[repo]

        latest_ts = group_df['run_started_at'].max()
        if not latest_ts:
            for _, row in group_df.iterrows():
                results.append({
                    'run_id': row['run_id'], 'repo': repo, 'status': 'no_base',
                    'base_sha': row.get('base_sha'), 'base_run_id': None, 'base_run_distance': None
                })
            continue

        latest_dt = datetime.datetime.fromtimestamp(parse_iso(latest_ts), tz=datetime.timezone.utc)
        day_str = latest_dt.strftime('%Y-%m-%d')

        url = f"https://api.github.com/repos/{repo}/actions/workflows/{wf_id}/runs"
        params = {"branch": branch, "created": f"<={day_str}", "per_page": 100}

        unresolved = group_df.copy()
        instance_ancestors = {}
        for _, row in unresolved.iterrows():
            base_sha = row['base_sha']
            ancestors = [base_sha] if base_sha else []
            curr = base_sha
            for _ in range(10):
                if not curr:
                    break
                parents = commit_graph.get(curr, [])
                if not parents:
                    break
                curr = parents[0]
                ancestors.append(curr)
            instance_ancestors[row['run_id']] = ancestors

        fetched_runs = []
        pages_fetched = 0

        while url and not unresolved.empty:
            # First request uses params; subsequent pages from Link header already contain query params
            try:
                res = get_with_backoff(url, params=params, pool=pool)
            except Exception:
                break
            req_count += 1
            if res.status_code != 200:
                break

            runs = res.json().get("workflow_runs", [])
            if not runs:
                break
            fetched_runs.extend(runs)
            pages_fetched += 1

            # Check unresolved instances against fetched_runs
            resolved_idx = []
            for idx, row in unresolved.iterrows():
                head_ts = parse_iso(row['run_started_at'])
                ancs = instance_ancestors[row['run_id']]
                if not ancs:
                    continue
                best_run = None
                best_dist = None

                for run_obj in fetched_runs:
                    run_ts_str = run_obj.get("run_started_at") or run_obj.get("created_at")
                    if not run_ts_str:
                        continue
                    run_ts = parse_iso(run_ts_str)
                    if run_ts >= head_ts:
                        continue
                    if run_obj.get("id") == row["run_id"]:
                        continue

                    run_head = run_obj.get("head_sha")
                    if run_head in ancs:
                        best_run = run_obj
                        best_dist = ancs.index(run_head)
                        break

                if best_run:
                    status = "exact" if best_dist == 0 else "ancestor"
                    if best_run.get("conclusion") == "success":
                        status = "exact_green"
                    results.append({
                        'run_id': row['run_id'],
                        'repo': repo,
                        'status': status,
                        'base_sha': best_run['head_sha'],
                        'base_run_id': best_run['id'],
                        'base_run_distance': best_dist,
                    })
                    resolved_idx.append(idx)

            unresolved = unresolved.drop(resolved_idx)

            if pages_fetched >= 34:  # ~1000 items ceiling per query window
                break

            url = None
            params = None  # Link header already encodes query parameters
            if "Link" in res.headers:
                for link in res.headers["Link"].split(","):
                    if 'rel="next"' in link:
                        url = link[link.index('<') + 1:link.index('>')]
                        break

        # Any remaining unresolved instances get no_base
        for _, row in unresolved.iterrows():
            results.append({
                'run_id': row['run_id'],
                'repo': repo,
                'status': 'no_base',
                'base_sha': row.get('base_sha'),
                'base_run_id': None,
                'base_run_distance': None,
            })

        group_count += 1
        if group_count % 10 == 0 or group_count == total_groups:
            elapsed = time.time() - start_time
            rpm = (req_count / elapsed) * 60 if elapsed > 0 else 0
            print(f"Group {group_count}/{total_groups} done ({group_row['language']} {repo}). Reqs: {req_count}, Elapsed: {elapsed:.1f}s, RPM: {rpm:.1f}")

    end_time = time.time()
    res_df = pd.DataFrame(results)
    print(f"\nCompleted in {end_time - start_time:.2f}s. Total requests: {req_count}")
    if not res_df.empty:
        print("\nStatus distribution:")
        print(res_df['status'].value_counts(normalize=True).mul(100).round(2).astype(str) + '% (' + res_df['status'].value_counts().astype(str) + ')')
        if 'base_run_distance' in res_df and res_df['base_run_distance'].notna().any():
            print("\nDistance distribution:")
            print(res_df['base_run_distance'].value_counts())

    if out_parquet:
        res_df.to_parquet(out_parquet)
    return res_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-100", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--python-first", action="store_true", default=True)
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()
    run(sample_100=args.sample_100, limit=args.limit, python_first=args.python_first, out_parquet=args.out)
