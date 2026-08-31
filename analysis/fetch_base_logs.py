import argparse
import pandas as pd
import time
import datetime
import traceback
import sys
from src.harvest.rawstore import RawStore, RawRecord
from src.harvest.ratelimit import TokenPool, get_with_backoff

def run(as_of: str = None, limit: int = None):
    df = pd.read_parquet('data/interim/base_resolution_new.parquet')
    target_df = df[df['status'].isin(['exact', 'ancestor', 'branch_prior'])]
    base_runs_to_fetch = target_df['base_run_id'].dropna().astype(int).unique()
    
    if limit is not None:
        base_runs_to_fetch = base_runs_to_fetch[:limit]
        
    print(f"Base runs targeted: {len(base_runs_to_fetch)}")
    
    pool = TokenPool.from_env()
    store = RawStore()
    
    run_to_repo = target_df.dropna(subset=['base_run_id']).set_index('base_run_id')['repo'].to_dict()
    
    df_inst = pd.read_parquet('data/interim/instances_raw.parquet')
    df = df.merge(df_inst[['run_id', 'repo', 'run_started_at']], on=['run_id', 'repo'], how='left')
    
    # Calculate base run age in days relative to now
    import datetime
    now = datetime.datetime.now(datetime.timezone.utc)
    df['base_age_days'] = df.apply(lambda row: (now - pd.to_datetime(row['run_started_at'], utc=True)).total_seconds() / 86400 if pd.notnull(row['run_started_at']) else 0, axis=1)
    
    age_map = dict(zip(df['base_run_id'].dropna().astype(int), df['base_age_days']))
    
    stats = {
        'requests': 0,
        'jobs_fetched': 0,
        'logs_fetched': 0,
        '404': 0,
        '410': 0,
        '429': 0,
        'err': 0,
        '410_ages': []
    }

    
    start = time.time()
    
    for i, run_id in enumerate(base_runs_to_fetch):
        repo = run_to_repo.get(run_id)
        if not repo:
            continue
            
        jobs_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs"
        try:
            resp = get_with_backoff(jobs_url, params={"per_page": 100}, pool=pool)
            stats['requests'] += 1
            if resp.status_code == 404: stats['404'] += 1; continue
            elif resp.status_code == 410: stats['410'] += 1; stats['410_ages'].append(age_map.get(int(run_id), 0)); continue
            elif resp.status_code == 429: stats['429'] += 1; continue
            
            jobs = resp.json().get("jobs", [])
            stats['jobs_fetched'] += len(jobs)

            if not store.exists(repo, "jobs", int(run_id)):
                rr_jobs = RawRecord(
                    url=jobs_url,
                    status=resp.status_code,
                    fetched_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    etag=resp.headers.get("etag"),
                    body=resp.content
                )
                store.write_records(repo, "jobs", int(run_id), [rr_jobs])

            for job in jobs:
                if job.get("conclusion") != "failure":
                    continue
                    
                job_id = job["id"]
                if store.exists(repo, "logs", int(job_id)):
                    stats['logs_fetched'] += 1
                    continue
                
                log_url = f"https://api.github.com/repos/{repo}/actions/jobs/{job_id}/logs"
                log_resp = get_with_backoff(log_url, pool=pool)
                stats['requests'] += 1
                
                if log_resp.status_code == 404: stats['404'] += 1
                elif log_resp.status_code == 410: stats['410'] += 1; stats['410_ages'].append(age_map.get(int(run_id), 0))
                elif log_resp.status_code == 429: stats['429'] += 1
                elif log_resp.status_code == 200:
                    rr = RawRecord(
                        url=log_url,
                        status=log_resp.status_code,
                        fetched_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        etag=log_resp.headers.get("etag"),
                        body=log_resp.content
                    )
                    store.write_records(repo, "logs", int(job_id), [rr])
                    stats['logs_fetched'] += 1
                    
        except Exception as e:
            stats['err'] += 1
            print(f"Error on run {run_id}: {e}")
            
        if (i + 1) % 100 == 0:
            elapsed = time.time() - start
            print(f"Heartbeat: {i+1}/{len(base_runs_to_fetch)} | Req/m: {stats['requests']/(elapsed/60):.1f} | 410: {stats['410']} | err: {stats['err']}")

    print("\n--- FETCH RESULTS ---")
    print(stats)
    return stats
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", type=str, help="As of date")
    parser.add_argument("--limit", type=int, help="Limit number of runs")
    args = parser.parse_args()
    run(as_of=args.as_of, limit=args.limit)

    if stats["410_ages"]:
        ages = pd.Series(stats["410_ages"])
        print("\\n410 Ages:")
        print(f"min: {ages.min():.1f}d")
        print(f"median: {ages.median():.1f}d")
        print(f"max: {ages.max():.1f}d")
        print("Buckets:")
        print(pd.cut(ages, bins=[0, 30, 60, 90, 120, 365, 1000]).value_counts().sort_index())

