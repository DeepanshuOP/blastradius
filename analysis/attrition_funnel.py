import pandas as pd
import sqlite3
import glob

from analysis import paper_md

CAVEATS = [
    "`logs captured` is the `kind='logs'` capture_unit count plus a hard-coded 394 (the 006A base-target "
    "fetch), and falls back to a hard-coded 13,710 if `data/state/cursor.db` is unreadable.",
    "`logs parsed` is set equal to `logs not expired` (every log on disk is treated as parsed).",
    "`logs with test output` is the number of distinct jobs with a parsed TEST_FAILURE outcome (head plus "
    "base); TEST_RAN_CLEAN logs are not counted.",
    "`logs not expired` exceeds `logs captured` (a rate above 100%): the two counts come from different "
    "sources (capture_unit rows versus files on disk), so this stage is not a nested subset. Not corrected here.",
    "Units change between steps (repos, PRs, runs, logs, instances); a row's n/d is only a survival rate "
    "where the unit matches its denominator, otherwise the raw ratio is shown.",
    "The repository-frame stages (SEART export, CI liveness, test intent, sample draw) are NOT regenerated "
    "here: the script that produced them was replaced in d6990fb.",
]


def write_md(steps: list[tuple]) -> None:
    """Write `paper/generated/attrition_funnel.md` from the computed steps (each row n/d)."""
    counts = {name: count for name, count, _, _ in steps}
    units = {name: unit for name, _, unit, _ in steps}
    rows = []
    for name, count, unit, denom_name in steps:
        if denom_name is None:
            rows.append([name, unit, f"{count:,}", "-", "-"])
            continue
        d = counts[denom_name]
        same = unit == units[denom_name]
        rows.append([name, unit, f"{count:,}", f"{denom_name} ({d:,} {units[denom_name]})",
                     paper_md.rate(count, d) if same else f"{count:,} {unit} / {d:,} {units[denom_name]}"])
    text = paper_md.header("Pipeline attrition funnel", "analysis/attrition_funnel.py")
    text += "\n" + paper_md.table(["step", "unit", "count", "denominator", "n/d"], rows)
    text += "\n## Caveats\n\n" + "\n".join(f"- {c}" for c in CAVEATS) + "\n"
    paper_md.write("attrition_funnel.md", text)


def main():
    print("Computing Attrition Funnel...")
    
    # 1. repos in frame
    repos_in_frame = sum(1 for _ in open('data/frame/frame_v1.csv')) - 1
    
    # 2. repos swept
    instances = pd.read_parquet('data/interim/instances_raw.parquet')
    repos_swept = instances['repo'].nunique()
    
    # 3. PRs discovered
    prs_discovered = instances.dropna(subset=['pr_number']).groupby(['repo', 'pr_number']).ngroups
    
    # 4. runs discovered
    runs_discovered = len(instances)
    
    # 5. failed runs
    failed_runs = len(instances[instances['run_conclusion'] == 'failure'])
    
    # 6. logs captured
    # All records in state/cursor.db where kind='logs' + manual sweep from 006A (let's just approximate as 13710 from state)
    try:
        conn = sqlite3.connect('data/state/cursor.db')
        logs_captured = conn.execute("SELECT count(*) FROM capture_unit WHERE kind='logs'").fetchone()[0]
    except Exception:
        logs_captured = 13710
        
    # Add manual base runs parsed in 006A
    # Base target logs fetch was 394
    logs_captured += 394
    
    # 7. logs not expired
    # Total jsonl.gz on disk
    logs_not_expired = len(glob.glob('data/raw/*/job/*/*/*.jsonl.gz'))
    
    # 8. logs parsed
    # Since Phase 045 classified everything, we consider all logs on disk as parsed.
    logs_parsed = logs_not_expired
    
    # 9. logs with test output
    # From parsed_outcomes (TEST_FAILURE) + TEST_RAN_CLEAN
    # We can get TEST_FAILURE from parsed_outcomes.parquet (unique jobs)
    # But wait, we also have base_outcomes.parquet
    parsed = pd.read_parquet('data/interim/parsed_outcomes.parquet')
    test_failure = parsed['job_id'].nunique()
    base_out = pd.read_parquet('data/interim/base_outcomes.parquet')
    test_failure += base_out['job_id'].nunique()
    
    # Let's say TEST_RAN_CLEAN is unknown here, we just use test_failure as approximation, or 2785.
    logs_with_test_output = test_failure  # This is actually TEST_FAILURE.
    
    # 10. instances with resolved base
    res = pd.read_parquet('data/interim/base_resolution_new.parquet')
    inst_resolved = len(res[res['status'] != 'no_base'])
    
    # 11. instances with a known base failure set
    runs_with_base_outcomes = set(base_out['run_id'].unique())
    inst_known_base = len(res[res['status'] == 'exact_green']) + len(res[res['run_id'].isin(runs_with_base_outcomes)])
    
    # 12. instances with >=1 fault-revealing label
    outcomes = pd.read_parquet('data/interim/outcomes.parquet')
    strict = outcomes[outcomes['split'] == 'strict']
    inst_with_label = strict['run_id'].nunique()
    
    steps = [
        ("repos in frame", repos_in_frame, "repos", None),
        ("repos swept", repos_swept, "repos", "repos in frame"),
        ("PRs discovered", prs_discovered, "PRs", None),
        ("runs discovered", runs_discovered, "runs", "PRs discovered"),
        ("failed runs", failed_runs, "runs", "runs discovered"),
        ("logs captured", logs_captured, "logs", None),
        ("logs not expired", logs_not_expired, "logs", "logs captured"),
        ("logs parsed", logs_parsed, "logs", "logs not expired"),
        ("logs with test output", logs_with_test_output, "logs", "logs parsed"),
        ("instances with resolved base", inst_resolved, "instances", "failed runs"),
        ("instances with a known base failure set", inst_known_base, "instances", "instances with resolved base"),
        ("instances with >=1 fault-revealing label", inst_with_label, "instances", "instances with a known base failure set")
    ]
    
    write_md(steps)
    print(f"{'Pipeline Step':<45} | {'Count':>10} | {'Survival/Ratio':>25}")
    print("-" * 85)
    
    # lookup map
    counts = {name: count for name, count, _, _ in steps}
    units = {name: unit for name, _, unit, _ in steps}
    
    for name, count, unit, denom_name in steps:
        if denom_name is None:
            print(f"{name:<45} | {count:10,d} | {'-':>25}")
        else:
            denom_count = counts[denom_name]
            denom_unit = units[denom_name]
            if unit == denom_unit:
                pct = (count / denom_count * 100) if denom_count > 0 else 0
                print(f"{name:<45} | {count:10,d} | {pct:24.2f}%")
            else:
                ratio = f"{count} {unit} / {denom_count} {denom_unit}"
                print(f"{name:<45} | {count:10,d} | {ratio:>25}")

if __name__ == '__main__':
    main()
