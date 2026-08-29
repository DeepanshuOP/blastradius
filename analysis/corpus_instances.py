"""BlastRadius — Corpus Workflow Run Instances Extractor.

Per ROADMAP §9.3 (T1.3), §31, and DECISIONS.md (D-12, D-19, D-20).
Extracts workflow run instances across harvested PR and run payloads, links
pull request metadata (head_sha, base_sha, base_ref, bot status) and job
payloads (job_ids, n_matrix_legs), and streams instances into
data/interim/instances_raw.parquet with companion INSTANCES_PIN.json.

Memory & Execution Discipline:
- Decompresses one payload at a time; no multiprocessing.
- Batches Parquet writes at 5,000 rows.
- Emits heartbeat every 250 files and aborts if RSS exceeds 3.0 GB.
- Uses RawStore.read_records; catches TruncatedRecordError per file.
- Enforces strict --as-of ISO-8601 timestamp cutoff against cursor.db.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import json
import os
import resource
import sqlite3
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from src.harvest.rawstore import RawStore, TruncatedRecordError

DEFAULT_RAW_ROOT = Path("data/raw")
DEFAULT_DB_PATH = Path("data/state/cursor.db")
DEFAULT_FRAME_PATH = Path("data/frame/frame_v1.csv")
DEFAULT_OUTPUT_PARQUET = Path("data/interim/instances_raw.parquet")
DEFAULT_PIN_FILE = Path("data/interim/INSTANCES_PIN.json")

UNPOPULATED_FIELDS = [
    "base_run_id",
    "base_run_distance",
    "changed_files",
    "changed_symbols",
    "n_files_changed",
    "n_lines_changed",
    "touches_test_file",
    "touches_build_config",
    "touches_ci_config",
    "is_dependency_bump",
    "is_docs_only",
    "is_formatting_only",
    "frontier_truncated",
    "is_default_branch",
    "graph_sha",
    "parse_failure_rate",
    "frame_version",
    "actual_changed_files",
]

PARQUET_SCHEMA = pa.schema(
    [
        ("instance_id", pa.string()),
        ("repo", pa.string()),
        ("repo_full", pa.string()),
        ("language", pa.string()),
        ("pr_number", pa.int64()),
        ("head_sha", pa.string()),
        ("base_sha", pa.string()),
        ("base_ref", pa.string()),
        ("base_run_id", pa.int64()),
        ("run_id", pa.int64()),
        ("workflow_id", pa.int64()),
        ("workflow_name", pa.string()),
        ("run_started_at", pa.string()),
        ("created_at", pa.string()),
        ("run_conclusion", pa.string()),
        ("job_ids", pa.list_(pa.int64())),
        ("job_conclusions", pa.list_(pa.string())),
        ("n_matrix_legs", pa.int32()),
        ("is_bot_pr", pa.bool_()),
        ("bot_name", pa.string()),
        ("author_login", pa.string()),
        ("event_type", pa.string()),
    ],
    metadata={
        b"unpopulated_fields": ", ".join(UNPOPULATED_FIELDS).encode("utf-8"),
        b"generator": b"analysis/corpus_instances.py",
    },
)


def get_current_rss_mb() -> float:
    """Return current resident memory set size (RSS) in megabytes."""
    try:
        with open("/proc/self/status", encoding="utf-8") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024.0
    except Exception:
        pass
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def get_peak_rss_mb() -> float:
    """Return peak resident memory set size (ru_maxrss) in megabytes."""
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def get_git_head_sha() -> str:
    """Retrieve git HEAD commit sha."""
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
        return out.decode("ascii").strip()
    except Exception:
        return "unknown"


def load_frame(frame_path: Path) -> dict[str, str]:
    """Return mapping from repository name ('owner/repo' and 'owner__repo') to language."""
    mapping: dict[str, str] = {}
    if not frame_path.is_file():
        return mapping
    with open(frame_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            slash = f"{row['owner']}/{row['repo']}"
            under = f"{row['owner']}__{row['repo']}"
            lang = row.get("lang", "unknown")
            mapping[slash] = lang
            mapping[under] = lang
    return mapping


def load_cursor_units(
    db_path: Path, as_of_dt: datetime.datetime
) -> tuple[dict[str, dict[str, set[str]]], dict[str, int]]:
    """Return map of repo -> kind -> set of completed unit_keys <= as_of_dt, and total counts."""
    completed: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    counts: dict[str, int] = defaultdict(int)

    if not db_path.is_file():
        return completed, counts

    uri = f"file:{db_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    try:
        c = conn.cursor()
        c.execute(
            "SELECT repo, kind, unit_key, completed_at FROM capture_unit "
            "WHERE status = 'complete'"
        )
        for repo, kind, unit_key, completed_at in c.fetchall():
            if completed_at:
                try:
                    cat_dt = datetime.datetime.fromisoformat(completed_at)
                    if cat_dt <= as_of_dt:
                        completed[repo][kind].add(unit_key)
                        counts[kind] += 1
                except Exception:
                    pass
    finally:
        conn.close()

    return completed, counts


def classify_bot(author: str | None) -> tuple[bool, str | None]:
    """Classify if PR author is a bot per T0.6."""
    if not author:
        return False, None
    author_lower = author.lower()
    if "dependabot" in author_lower:
        return True, "dependabot"
    if "renovate" in author_lower:
        return True, "renovate"
    if "[bot]" in author_lower or author_lower.endswith("-bot") or author_lower.endswith("_bot"):
        return True, author
    return False, None


def format_duration(seconds: float) -> str:
    """Format seconds into readable human format."""
    if seconds < 0:
        return "0s"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m}m {s:02d}s"


def compute_instance_id(repo: str, head_sha: str, run_id: int) -> str:
    """Compute deterministic instance_id PK per SCHEMAS.md."""
    key = f"{repo}|{head_sha}|{run_id}".encode("utf-8")
    return hashlib.sha256(key).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="BlastRadius — Corpus Workflow Run Instances Extractor"
    )
    parser.add_argument(
        "--as-of",
        required=True,
        help="Mandatory ISO-8601 timestamp cutoff (e.g. 2026-08-28T21:36:57Z)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional maximum number of runs to extract",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output Parquet and pin file rather than skipping",
    )
    parser.add_argument(
        "--raw-root",
        type=Path,
        default=DEFAULT_RAW_ROOT,
        help=f"Raw data directory root (default: {DEFAULT_RAW_ROOT})",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=DEFAULT_OUTPUT_PARQUET,
        help=f"Output Parquet destination (default: {DEFAULT_OUTPUT_PARQUET})",
    )
    parser.add_argument(
        "--pin-file",
        type=Path,
        default=DEFAULT_PIN_FILE,
        help=f"Instances pin JSON destination (default: {DEFAULT_PIN_FILE})",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Cursor database path (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--frame-path",
        type=Path,
        default=DEFAULT_FRAME_PATH,
        help=f"Frame CSV path (default: {DEFAULT_FRAME_PATH})",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5000,
        help="Parquet batch write size in rows (default: 5000)",
    )
    parser.add_argument(
        "--heartbeat-interval",
        type=int,
        default=250,
        help="Files interval for heartbeat reports (default: 250)",
    )
    parser.add_argument(
        "--max-rss-gb",
        type=float,
        default=3.0,
        help="Maximum allowed RSS in GB before aborting (default: 3.0)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Parse and validate --as-of
    try:
        as_of_iso = args.as_of.strip()
        as_of_dt = datetime.datetime.fromisoformat(as_of_iso.replace("Z", "+00:00"))
    except Exception as exc:
        print(f"ERROR: Invalid --as-of ISO-8601 timestamp {args.as_of!r}: {exc}", file=sys.stderr)
        sys.exit(1)

    run_start_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    start_time = time.time()

    print("=" * 80)
    print("BlastRadius Corpus Instances Extractor")
    print(f"As-of Cutoff:      {as_of_iso}")
    print(f"Raw Root:          {args.raw_root}")
    print(f"Output Parquet:    {args.output}")
    print(f"Pin File:          {args.pin_file}")
    print(f"Cursor DB:         {args.db_path}")
    print(f"Frame CSV:         {args.frame_path}")
    print(f"Batch Size:        {args.batch_size}")
    print(f"Heartbeat:         Every {args.heartbeat_interval} files")
    print(f"Max RSS Limit:     {args.max_rss_gb} GB")
    print("=" * 80)

    # 1. Load frame and cursor.db completed units
    frame_map = load_frame(args.frame_path)
    cursor_units, cursor_counts = load_cursor_units(args.db_path, as_of_dt)
    print(f"Loaded {len(frame_map) // 2} frame repos.")
    print("Cursor completed units <= as_of:")
    for k in sorted(cursor_counts):
        print(f"  {k:<15s}: {cursor_counts[k]:,}")

    # 2. Setup output directories
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.pin_file.parent.mkdir(parents=True, exist_ok=True)

    if args.overwrite and args.output.is_file():
        print(f"Overwriting existing {args.output}...")
        args.output.unlink(missing_ok=True)

    # 3. Discover repos under raw root
    store = RawStore(args.raw_root)
    repo_dirs = sorted([d for d in args.raw_root.iterdir() if d.is_dir() and "__" in d.name])
    print(f"Discovered {len(repo_dirs)} repo directories under {args.raw_root}.")

    # 4. Initialize reader, writer, counters
    max_rss_mb = args.max_rss_gb * 1024.0

    writer: pq.ParquetWriter | None = None
    batch_rows: list[dict[str, Any]] = []

    files_scanned = 0
    files_skipped = 0
    skip_reasons: Counter[str] = Counter()

    total_instances_written = 0
    distinct_repos: set[str] = set()
    distinct_prs: set[int] = set()
    distinct_head_shas: set[str] = set()
    distinct_run_ids: set[int] = set()

    run_conclusion_counts: Counter[str] = Counter()
    non_null_base_sha_count = 0
    null_base_sha_count = 0
    is_bot_pr_true_count = 0
    is_bot_pr_false_count = 0
    matrix_leg_lengths: list[int] = []
    matrix_leg_null_count = 0

    seen_instance_keys: set[tuple[str, str, int]] = set()
    duplicate_instance_count = 0

    heartbeat_lines: list[str] = []

    print("-" * 80)
    print("Starting instance extraction loop...")
    print("-" * 80)

    try:
        for repo_dir in repo_dirs:
            owner, name = repo_dir.name.split("__", 1)
            repo_slash = f"{owner}/{name}"
            repo_lang = frame_map.get(repo_slash, "unknown")

            repo_cursor = cursor_units.get(repo_slash, {})
            eligible_pull_pages = repo_cursor.get("pulls", set())
            eligible_pull_commits = repo_cursor.get("pull_commits", set())
            eligible_runs_shas = repo_cursor.get("runs", set())
            eligible_jobs_runs = repo_cursor.get("jobs", set())

            # Step A: Load PR metadata from eligible pulls pages
            pr_metadata: dict[int, dict[str, Any]] = {}
            for page_str in sorted(eligible_pull_pages, key=int):
                files_scanned += 1
                page_num = int(page_str)
                try:
                    recs = store.read_records(repo_slash, "pulls", page_num)
                except TruncatedRecordError as exc:
                    files_skipped += 1
                    skip_reasons["truncated_pulls_record"] += 1
                    continue
                except Exception as exc:
                    files_skipped += 1
                    skip_reasons[f"read_error_pulls_{type(exc).__name__}"] += 1
                    continue

                if not recs or not recs[0].body:
                    continue

                try:
                    prs_list = json.loads(recs[0].body)
                except Exception:
                    continue

                for pr in prs_list:
                    pnum = pr.get("number")
                    if pnum is None:
                        continue
                    user_dict = pr.get("user") or {}
                    author = user_dict.get("login")
                    is_bot, bot_name = classify_bot(author)
                    head_dict = pr.get("head") or {}
                    base_dict = pr.get("base") or {}

                    pr_metadata[pnum] = {
                        "pr_number": pnum,
                        "head_sha": head_dict.get("sha"),
                        "base_sha": base_dict.get("sha"),
                        "base_ref": base_dict.get("ref"),
                        "author_login": author,
                        "is_bot_pr": is_bot,
                        "bot_name": bot_name,
                    }

            # Step B: Load commit SHA -> PR mapping from eligible pull_commits
            sha_to_pr_map: dict[str, int] = {}
            for pr_str in sorted(eligible_pull_commits, key=int):
                files_scanned += 1
                pnum = int(pr_str)
                try:
                    recs = store.read_records(repo_slash, "pull_commits", pnum)
                except TruncatedRecordError:
                    files_skipped += 1
                    skip_reasons["truncated_pull_commits_record"] += 1
                    continue
                except Exception as exc:
                    files_skipped += 1
                    skip_reasons[f"read_error_pull_commits_{type(exc).__name__}"] += 1
                    continue

                for rec in recs:
                    if not rec.body:
                        continue
                    try:
                        commits_list = json.loads(rec.body)
                    except Exception:
                        continue
                    for c in commits_list:
                        csha = c.get("sha")
                        if csha and csha not in sha_to_pr_map:
                            sha_to_pr_map[csha] = pnum

            # Ensure head_sha from PR metadata also maps to PR
            for pnum, pmeta in pr_metadata.items():
                hsha = pmeta.get("head_sha")
                if hsha and hsha not in sha_to_pr_map:
                    sha_to_pr_map[hsha] = pnum

            # Step C: Iterate eligible runs files
            for sha in sorted(eligible_runs_shas):
                files_scanned += 1

                # Heartbeat check
                if files_scanned % args.heartbeat_interval == 0:
                    elapsed = time.time() - start_time
                    rate = files_scanned / elapsed if elapsed > 0 else 0.0
                    curr_rss = get_current_rss_mb()
                    pk_rss = get_peak_rss_mb()
                    hb_line = (
                        f"[HEARTBEAT] files: {files_scanned:6d} | "
                        f"elapsed: {format_duration(elapsed):>9s} | "
                        f"rate: {rate:5.1f} files/s | "
                        f"instances: {total_instances_written:6d} | "
                        f"RSS: {curr_rss:6.1f} MB | peak: {pk_rss:6.1f} MB"
                    )
                    print(hb_line, flush=True)
                    heartbeat_lines.append(hb_line)

                    # RSS safety guard
                    if curr_rss > max_rss_mb:
                        print(
                            f"FATAL: RSS memory ({curr_rss:.1f} MB) exceeded safety limit ({max_rss_mb:.1f} MB). Aborting!",
                            file=sys.stderr,
                        )
                        sys.exit(2)

                try:
                    recs = store.read_records(repo_slash, "runs", sha)
                except TruncatedRecordError:
                    files_skipped += 1
                    skip_reasons["truncated_runs_record"] += 1
                    continue
                except Exception as exc:
                    files_skipped += 1
                    skip_reasons[f"read_error_runs_{type(exc).__name__}"] += 1
                    continue

                if not recs or not recs[0].body:
                    continue

                try:
                    runs_body = json.loads(recs[0].body)
                except Exception:
                    continue

                workflow_runs = runs_body.get("workflow_runs", [])
                for run in workflow_runs:
                    run_id = run.get("id")
                    if run_id is None:
                        continue

                    head_sha = run.get("head_sha") or sha
                    instance_key = (repo_slash, head_sha, run_id)
                    if instance_key in seen_instance_keys:
                        duplicate_instance_count += 1
                        continue
                    seen_instance_keys.add(instance_key)

                    # Link PR
                    pr_num = sha_to_pr_map.get(head_sha)
                    if pr_num is None and run.get("pull_requests"):
                        prs_in_run = run["pull_requests"]
                        if prs_in_run and isinstance(prs_in_run[0], dict):
                            pr_num = prs_in_run[0].get("number")

                    pr_info = pr_metadata.get(pr_num) if pr_num is not None else None

                    base_sha = pr_info.get("base_sha") if pr_info else None
                    base_ref = pr_info.get("base_ref") if pr_info else None
                    is_bot = pr_info.get("is_bot_pr") if pr_info else None
                    bot_name = pr_info.get("bot_name") if pr_info else None
                    author_login = pr_info.get("author_login") if pr_info else None

                    # If run had actor / triggering_actor and author_login is still None
                    if author_login is None:
                        actor = run.get("actor") or {}
                        author_login = actor.get("login")
                        if is_bot is None and author_login:
                            is_bot, bot_name = classify_bot(author_login)

                    # Step D: Read jobs for this run
                    job_ids: list[int] = []
                    job_conclusions: list[str] = []
                    n_matrix_legs: int | None = None

                    run_id_str = str(run_id)
                    if run_id_str in eligible_jobs_runs:
                        files_scanned += 1
                        try:
                            jrecs = store.read_records(repo_slash, "jobs", run_id)
                            if jrecs and jrecs[0].body:
                                jbody = json.loads(jrecs[0].body)
                                jobs_list = jbody.get("jobs", [])
                                for j in jobs_list:
                                    jid = j.get("id")
                                    if jid is not None:
                                        job_ids.append(int(jid))
                                        job_conclusions.append(str(j.get("conclusion") or "unknown"))
                                n_matrix_legs = len(jobs_list)
                        except TruncatedRecordError:
                            files_skipped += 1
                            skip_reasons["truncated_jobs_record"] += 1
                        except Exception as exc:
                            files_skipped += 1
                            skip_reasons[f"read_error_jobs_{type(exc).__name__}"] += 1

                    # Track metrics
                    distinct_repos.add(repo_slash)
                    if pr_num is not None:
                        distinct_prs.add(pr_num)
                    distinct_head_shas.add(head_sha)
                    distinct_run_ids.add(run_id)

                    run_conc = run.get("conclusion") or "unknown"
                    run_conclusion_counts[run_conc] += 1

                    if base_sha is not None:
                        non_null_base_sha_count += 1
                    else:
                        null_base_sha_count += 1

                    if is_bot is True:
                        is_bot_pr_true_count += 1
                    elif is_bot is False:
                        is_bot_pr_false_count += 1

                    if n_matrix_legs is not None:
                        matrix_leg_lengths.append(n_matrix_legs)
                    else:
                        matrix_leg_null_count += 1

                    inst_id = compute_instance_id(repo_slash, head_sha, run_id)
                    run_started = run.get("run_started_at") or run.get("created_at")

                    row = {
                        "instance_id": inst_id,
                        "repo": repo_slash,
                        "repo_full": repo_slash,
                        "language": repo_lang,
                        "pr_number": pr_num,
                        "head_sha": head_sha,
                        "base_sha": base_sha,
                        "base_ref": base_ref,
                        "base_run_id": None,
                        "run_id": run_id,
                        "workflow_id": run.get("workflow_id"),
                        "workflow_name": run.get("name"),
                        "run_started_at": run_started,
                        "created_at": run.get("created_at"),
                        "run_conclusion": run.get("conclusion"),
                        "job_ids": job_ids,
                        "job_conclusions": job_conclusions,
                        "n_matrix_legs": n_matrix_legs,
                        "is_bot_pr": is_bot,
                        "bot_name": bot_name,
                        "author_login": author_login,
                        "event_type": run.get("event"),
                    }
                    batch_rows.append(row)
                    total_instances_written += 1

                    if len(batch_rows) >= args.batch_size:
                        table = pa.Table.from_pylist(batch_rows, schema=PARQUET_SCHEMA)
                        if writer is None:
                            writer = pq.ParquetWriter(
                                args.output, schema=PARQUET_SCHEMA, compression="snappy"
                            )
                        writer.write_table(table)
                        batch_rows.clear()

                    if args.limit is not None and total_instances_written >= args.limit:
                        break

                if args.limit is not None and total_instances_written >= args.limit:
                    break

            if args.limit is not None and total_instances_written >= args.limit:
                break

    finally:
        # Flush remaining batch rows
        if batch_rows:
            table = pa.Table.from_pylist(batch_rows, schema=PARQUET_SCHEMA)
            if writer is None:
                writer = pq.ParquetWriter(
                    args.output, schema=PARQUET_SCHEMA, compression="snappy"
                )
            writer.write_table(table)
            batch_rows.clear()

        if writer is not None:
            writer.close()
        elif total_instances_written == 0:
            table = pa.Table.from_pylist([], schema=PARQUET_SCHEMA)
            writer = pq.ParquetWriter(
                args.output, schema=PARQUET_SCHEMA, compression="snappy"
            )
            writer.write_table(table)
            writer.close()

    total_wall_clock = time.time() - start_time
    run_end_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    peak_rss = get_peak_rss_mb()

    # 5. Write INSTANCES_PIN.json
    pin_data = {
        "as_of": as_of_iso,
        "per_kind_file_counts": dict(cursor_counts),
        "total_files_scanned": files_scanned,
        "total_files_skipped": files_skipped,
        "total_instances_written": total_instances_written,
        "git_head_sha": get_git_head_sha(),
        "run_start_utc": run_start_utc,
        "run_end_utc": run_end_utc,
        "unpopulated_fields": UNPOPULATED_FIELDS,
        "completed_at_resolved_via": "cursor.db capture_unit table lookup on (repo, kind, unit_key) with status='complete' and completed_at <= as_of",
    }
    with open(args.pin_file, "w", encoding="utf-8") as f:
        json.dump(pin_data, f, indent=2)

    # 6. Summary Report
    print()
    print("=" * 80)
    print("FINAL INSTANCES SUMMARY REPORT")
    print("=" * 80)
    print(f"Total Wall Clock Time:     {format_duration(total_wall_clock)} ({total_wall_clock:.2f} s)")
    print(f"Peak RSS Memory:           {peak_rss:.2f} MB")
    print(f"Parquet Dataset:           {args.output} ({args.output.stat().st_size:,} bytes)")
    print(f"Pin File:                  {args.pin_file}")
    print()

    print("1. FILE SCAN & SKIP BREAKDOWN:")
    print(f"  Files Scanned:           {files_scanned:,}")
    print(f"  Files Skipped:           {files_skipped:,}")
    if skip_reasons:
        print("  Skip Reasons Breakdown:")
        for reason, cnt in skip_reasons.most_common():
            print(f"    - {reason}: {cnt:,}")
    print(f"  Duplicate Instances:     {duplicate_instance_count:,}")
    print()

    print("2. INSTANCES & ENTITIES:")
    print(f"  Total Instance Rows:     {total_instances_written:,}")
    print(f"  Distinct Repos:          {len(distinct_repos):,}")
    print(f"  Distinct PRs:            {len(distinct_prs):,}")
    print(f"  Distinct Head SHAs:      {len(distinct_head_shas):,}")
    print(f"  Distinct Run IDs:        {len(distinct_run_ids):,}")
    print()

    print("3. RUN CONCLUSION BREAKDOWN:")
    for conc, cnt in run_conclusion_counts.most_common():
        pct = (cnt / total_instances_written * 100.0) if total_instances_written > 0 else 0.0
        print(f"  {conc:<20s}: {cnt:6,d} ({pct:5.2f}%)")
    print()

    print("4. BASE SHA COVERAGE:")
    print(f"  Non-null base_sha:       {non_null_base_sha_count:,} ({non_null_base_sha_count/max(1,total_instances_written)*100:.2f}%)")
    print(f"  Null base_sha:           {null_base_sha_count:,} ({null_base_sha_count/max(1,total_instances_written)*100:.2f}%)")
    print()

    print("5. BOT PR BREAKDOWN (T0.6):")
    print(f"  is_bot_pr True:          {is_bot_pr_true_count:,} ({is_bot_pr_true_count/max(1,total_instances_written)*100:.2f}%)")
    print(f"  is_bot_pr False:         {is_bot_pr_false_count:,} ({is_bot_pr_false_count/max(1,total_instances_written)*100:.2f}%)")
    null_bot = total_instances_written - is_bot_pr_true_count - is_bot_pr_false_count
    print(f"  is_bot_pr Null (no PR):  {null_bot:,} ({null_bot/max(1,total_instances_written)*100:.2f}%)")
    print()

    print("6. MATRIX LEGS DISTRIBUTION (D-12):")
    if matrix_leg_lengths:
        matrix_leg_lengths.sort()
        n = len(matrix_leg_lengths)
        med = matrix_leg_lengths[n // 2]
        print(f"  Count Measured:          {n:,}")
        print(f"  Min:                     {matrix_leg_lengths[0]:,}")
        print(f"  Median:                  {med:,}")
        print(f"  Max:                     {matrix_leg_lengths[-1]:,}")
        print(f"  Null / Unmeasured:       {matrix_leg_null_count:,}")
    else:
        print(f"  Null / Unmeasured:       {matrix_leg_null_count:,}")
    print()

    # 7. Join Test against outcomes Parquet if it exists
    outcomes_path_candidates = [
        Path("data/interim/outcomes_raw.parquet"),
        Path("data/interim/parsed_outcomes.parquet"),
    ]
    outcomes_found = None
    for cand in outcomes_path_candidates:
        if cand.is_file():
            outcomes_found = cand
            break

    print("7. JOIN TEST:")
    if outcomes_found is not None:
        try:
            outcomes_table = pq.read_table(outcomes_found, columns=["repo", "job_id"])
            outcomes_df = outcomes_table.to_pandas().dropna()
            outcomes_pairs = set(zip(outcomes_df["repo"], outcomes_df["job_id"].astype(int)))
            
            # Extract (repo, job_id) pairs from our instances
            instance_pairs: set[tuple[str, int]] = set()
            inst_table = pq.read_table(args.output, columns=["repo", "job_ids"])
            for row_repo, row_job_ids in zip(inst_table["repo"].to_pylist(), inst_table["job_ids"].to_pylist()):
                if row_job_ids:
                    for jid in row_job_ids:
                        instance_pairs.add((row_repo, int(jid)))

            common_pairs = outcomes_pairs.intersection(instance_pairs)
            print(f"  Outcomes file tested:    {outcomes_found}")
            print(f"  Outcomes distinct pairs: {len(outcomes_pairs):,}")
            print(f"  Instances distinct pairs:{len(instance_pairs):,}")
            print(f"  Joined distinct pairs:   {len(common_pairs):,} ({len(common_pairs)/max(1,len(outcomes_pairs))*100:.2f}% of outcomes)")
        except Exception as exc:
            print(f"  Error performing join test against {outcomes_found}: {exc}")
    else:
        print("  data/interim/outcomes_raw.parquet does not exist yet (skipped).")

    print("=" * 80)


if __name__ == "__main__":
    main()
