import argparse
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
import json
from src.harvest.rawstore import RawStore
from src.parse.dispatch import dispatch_parse_log_with_stats
from src.parse.test_ids import normalize_test_id

def run(as_of: str = None, limit: int = None):
    df = pd.read_parquet('data/interim/base_resolution_new.parquet')
    target_df = df[df['status'].isin(['exact', 'ancestor', 'branch_prior'])].dropna(subset=['base_run_id'])
    
    if limit is not None:
        target_df = target_df.head(limit)
        
    base_run_to_head_runs = {}
    base_run_to_repo = {}
    
    for _, row in target_df.iterrows():
        b_id = int(row['base_run_id'])
        h_id = int(row['run_id'])
        repo = row['repo']
        base_run_to_head_runs.setdefault(b_id, []).append(h_id)
        base_run_to_repo[b_id] = repo
        
    store = RawStore()
    outcomes = []
    
    logs_parsed = 0
    classification_counts = {"TEST_FAILURE": 0, "TEST_RAN_CLEAN": 0, "NO_TEST_OUTPUT": 0, "UNREADABLE": 0}
    
    base_run_yielded_identifiers = {b_id: False for b_id in base_run_to_repo.keys()}
    distinct_test_ids = set()
    
    for b_id, repo in base_run_to_repo.items():
        try:
            jobs_recs = store.read_records(repo, "jobs", b_id)
            if not jobs_recs or not jobs_recs[0].body:
                continue
            jobs = json.loads(jobs_recs[0].body.decode("utf-8")).get("jobs", [])
        except Exception:
            continue
            
        for job in jobs:
            if job.get("conclusion") != "failure":
                continue
            job_id = job["id"]
            
            try:
                log_recs = store.read_records(repo, "logs", job_id)
                if not log_recs or not log_recs[0].body:
                    classification_counts["NO_TEST_OUTPUT"] += 1
                    continue
                body_text = log_recs[0].body.decode("utf-8", errors="replace")
            except Exception:
                continue
                
            try:
                parsed_outcomes, stats = dispatch_parse_log_with_stats(
                    body_text,
                    run_id=b_id,
                    job_id=job_id,
                    repo=repo,
                    head_sha=None,
                )
            except Exception:
                classification_counts["UNREADABLE"] += 1
                continue
                
            logs_parsed += 1
            if parsed_outcomes:
                base_run_yielded_identifiers[b_id] = True
                for o in parsed_outcomes:
                    canonical_id = normalize_test_id(o.test_id, None)
                    if not canonical_id:
                        continue
                    distinct_test_ids.add(canonical_id.canonical)
                    
                    for h_id in base_run_to_head_runs[b_id]:
                        outcomes.append({
                            "test_id": canonical_id.canonical,
                            "parser_confidence": float(o.parser_confidence),
                            "run_id": h_id,
                            "base_run_id": b_id,
                            "job_id": job_id,
                            "repo": repo,
                            "head_sha": None,
                            "test_file": o.test_file,
                        })
                        
    zero_identifiers = sum(1 for v in base_run_yielded_identifiers.values() if not v)
    
    print(f"Logs parsed: {logs_parsed}")
    print(f"Classification breakdown: {classification_counts}")
    print(f"Total outcome rows: {len(outcomes)}")
    print(f"Distinct test_ids: {len(distinct_test_ids)}")
    print(f"Base runs yielding zero identifiers: {zero_identifiers} out of {len(base_run_to_repo)}")
    
    exact_green_instances = len(df[df['status'] == 'exact_green'])
    instances_with_yield = 0
    for b_id, yielded in base_run_yielded_identifiers.items():
        if yielded:
            instances_with_yield += len(base_run_to_head_runs[b_id])
            
    real_size = exact_green_instances + instances_with_yield
    print(f"Instances with BOTH head and base failure sets (real size of BR-Bench): {real_size}")
    
    if outcomes:
        df_out = pd.DataFrame(outcomes)
        schema = pa.schema([
            ("test_id", pa.string()),
            ("parser_confidence", pa.float32()),
            ("run_id", pa.int64()),
            ("job_id", pa.int64()),
            ("repo", pa.string()),
            ("head_sha", pa.string()),
            ("test_file", pa.string()),
            ("base_run_id", pa.int64())
        ])
        table = pa.Table.from_pandas(df_out, schema=schema)
        pq.write_table(table, "data/interim/base_outcomes.parquet")
    else:
        print("No outcomes found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", type=str, help="As of date")
    parser.add_argument("--limit", type=int, help="Limit number of runs")
    args = parser.parse_args()
    run(as_of=args.as_of, limit=args.limit)
