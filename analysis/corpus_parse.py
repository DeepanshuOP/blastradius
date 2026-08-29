"""BlastRadius — Full Corpus Log Parser & Test Outcome Extractor.

Per ROADMAP §9.1, §37.1 (Gate 1.5 readiness), and DECISIONS.md (D-25, D-27).
Parses gzipped raw GitHub Actions build logs using RawStore, normalizes test
identifiers through normalize_test_id, evaluates FQCN qualification rates, and
streams extracted test outcomes into a canonical Parquet dataset.

Memory Discipline:
- Decompresses one log at a time; no multiprocessing.
- Enforces a 64 MB ISIZE skip guard on compressed logs.
- Batches Parquet writes at 5,000 rows to keep memory usage low.
- Emits heartbeat every 250 logs and aborts if RSS exceeds 3.0 GB.
"""

from __future__ import annotations

import argparse
import csv
import datetime
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
from src.parse.dispatch import classify_dispatch_log, dispatch_parse_log_with_stats
from src.parse.log_gradle import classify_gradle_log
from src.parse.log_maven import classify_maven_log
from src.parse.log_pytest import classify_pytest_log
from src.parse.test_ids import normalize_test_id

DEFAULT_RAW_ROOT = Path("data/raw")
DEFAULT_DB_PATH = Path("data/state/cursor.db")
DEFAULT_FRAME_PATH = Path("data/frame/frame_v1.csv")
DEFAULT_OUTPUT_PARQUET = Path("data/interim/parsed_outcomes.parquet")
DEFAULT_PIN_FILE = Path("data/interim/CORPUS_PIN.json")

PARQUET_SCHEMA = pa.schema(
    [
        ("test_id", pa.string()),
        ("parser_confidence", pa.float32()),
        ("run_id", pa.int64()),
        ("job_id", pa.int64()),
        ("repo", pa.string()),
        ("head_sha", pa.string()),
        ("test_file", pa.string()),
        ("status", pa.string()),
        ("duration_s", pa.float32()),
        ("failure_message", pa.string()),
        ("label_source", pa.string()),
        ("harness", pa.string()),
        ("is_fqcn_qualified", pa.bool_()),
        ("params", pa.string()),
    ]
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


def get_gzip_isize(path: Path) -> int:
    """Read the uncompressed size modulo 2^32 from the gzip footer (last 4 bytes)."""
    try:
        size = path.stat().st_size
        if size < 4:
            return 0
        with open(path, "rb") as f:
            f.seek(-4, os.SEEK_END)
            return int.from_bytes(f.read(4), "little")
    except Exception:
        return 0


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


def load_cursor_db(
    db_path: Path,
) -> dict[tuple[str, str], tuple[int | None, str, datetime.datetime | None]]:
    """Return map of (repo_slash, unit_key) -> (parent_run_id, completed_at_str, completed_at_dt)."""
    mapping: dict[tuple[str, str], tuple[int | None, str, datetime.datetime | None]] = {}
    if not db_path.is_file():
        return mapping
    uri = f"file:{db_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    try:
        c = conn.cursor()
        c.execute(
            "SELECT repo, unit_key, parent_run_id, completed_at "
            "FROM capture_unit WHERE kind='logs' AND status='complete'"
        )
        for repo, unit_key, parent_run_id, completed_at in c.fetchall():
            dt = None
            if completed_at:
                try:
                    dt = datetime.datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                except Exception:
                    dt = None
            mapping[(repo, unit_key)] = (parent_run_id, completed_at, dt)
    finally:
        conn.close()
    return mapping


def format_duration(seconds: float) -> str:
    """Format seconds into readable human format."""
    if seconds < 0:
        return "0s"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m}m {s:02d}s"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="BlastRadius — Full Corpus Log Parser & Test Outcome Extractor"
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
        help="Optional maximum number of logs to parse",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output Parquet and pin file rather than resuming",
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
        help=f"Corpus pin JSON destination (default: {DEFAULT_PIN_FILE})",
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
        help="Logs interval for heartbeat reports (default: 250)",
    )
    parser.add_argument(
        "--max-isize-mb",
        type=float,
        default=64.0,
        help="Maximum gzip ISIZE uncompressed size in MB (default: 64.0)",
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
    print("BlastRadius Corpus Log Parser & Outcome Extractor")
    print(f"As-of Cutoff:      {as_of_iso}")
    print(f"Raw Root:          {args.raw_root}")
    print(f"Output Parquet:    {args.output}")
    print(f"Pin File:          {args.pin_file}")
    print(f"Cursor DB:         {args.db_path}")
    print(f"Frame CSV:         {args.frame_path}")
    print(f"Batch Size:        {args.batch_size}")
    print(f"Heartbeat:         Every {args.heartbeat_interval} logs")
    print(f"ISIZE Limit:       {args.max_isize_mb} MB")
    print(f"Max RSS Limit:     {args.max_rss_gb} GB")
    print("=" * 80)

    # 1. Load frame and cursor.db
    frame_map = load_frame(args.frame_path)
    cursor_map = load_cursor_db(args.db_path)
    print(f"Loaded {len(frame_map) // 2} frame repos and {len(cursor_map)} completed logs in cursor.db.")

    # 2. Discover and filter log files
    print("Discovering logs matching */job/*/*/logs.jsonl.gz...")
    candidate_paths = list(args.raw_root.glob("*/job/*/*/logs.jsonl.gz"))
    total_globbed = len(candidate_paths)
    print(f"Discovered {total_globbed} log files on disk.")

    worklist: list[dict[str, Any]] = []
    pre_skip_reasons: Counter[str] = Counter()

    for p in candidate_paths:
        parts = p.parts
        repo_under = parts[-5]
        repo_slash = repo_under.replace("__", "/", 1)
        job_id_int = int(parts[-2])
        unit_key = str(job_id_int)

        db_entry = cursor_map.get((repo_slash, unit_key))
        if db_entry is None:
            pre_skip_reasons["not_in_cursor_db_complete"] += 1
            continue

        parent_run_id, completed_at_str, completed_at_dt = db_entry
        if completed_at_dt is None or completed_at_dt > as_of_dt:
            pre_skip_reasons["completed_after_as_of"] += 1
            continue

        worklist.append(
            {
                "path": p,
                "repo": repo_slash,
                "job_id": job_id_int,
                "unit_key": unit_key,
                "parent_run_id": parent_run_id,
                "completed_at": completed_at_str,
            }
        )

    # Sort deterministically
    worklist.sort(key=lambda x: (x["repo"], x["job_id"]))

    if args.limit is not None and args.limit > 0:
        print(f"Applying limit: {args.limit} of {len(worklist)} eligible logs.")
        worklist = worklist[: args.limit]

    total_logs_to_process = len(worklist)
    print(f"Eligible logs to parse: {total_logs_to_process} (Pre-filtered out: {dict(pre_skip_reasons)})")

    # 3. Setup output directories
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.pin_file.parent.mkdir(parents=True, exist_ok=True)

    if args.overwrite and args.output.is_file():
        print(f"Overwriting existing {args.output}...")
        args.output.unlink(missing_ok=True)

    # 4. Initialize reader, writer, counters
    store = RawStore(args.raw_root)
    max_isize_bytes = int(args.max_isize_mb * 1024 * 1024)
    max_rss_mb = args.max_rss_gb * 1024.0

    writer: pq.ParquetWriter | None = None
    batch_rows: list[dict[str, Any]] = []

    logs_scanned = 0
    logs_skipped = 0
    logs_parsed = 0

    skip_reasons: Counter[str] = Counter()
    skip_reasons.update(pre_skip_reasons)

    classification_counts: Counter[str] = Counter()
    unnormalizable_count = 0
    unnormalizable_examples: list[str] = []

    total_outcomes_written = 0
    distinct_test_ids: set[str] = set()
    distinct_test_ids_by_harness: dict[str, set[str]] = defaultdict(set)
    distinct_test_ids_by_lang: dict[str, set[str]] = defaultdict(set)
    repo_distinct_ids: dict[str, set[str]] = defaultdict(set)

    fqcn_outcome_true_count = 0
    fqcn_outcome_false_count = 0
    fqcn_distinct_true_ids: set[str] = set()
    fqcn_distinct_false_ids: set[str] = set()

    heartbeat_lines: list[str] = []

    print("-" * 80)
    print("Starting log parse loop...")
    print("-" * 80)

    try:
        for idx, item in enumerate(worklist, start=1):
            logs_scanned += 1

            # Heartbeat check
            if idx % args.heartbeat_interval == 0 or idx == total_logs_to_process:
                elapsed = time.time() - start_time
                rate = idx / elapsed if elapsed > 0 else 0.0
                pct = (idx / total_logs_to_process) * 100.0 if total_logs_to_process > 0 else 0.0
                curr_rss = get_current_rss_mb()
                pk_rss = get_peak_rss_mb()
                hb_line = (
                    f"[HEARTBEAT] processed: {idx:5d}/{total_logs_to_process} ({pct:5.1f}%) | "
                    f"elapsed: {format_duration(elapsed):>9s} | "
                    f"rate: {rate:5.1f} logs/s | "
                    f"outcomes: {total_outcomes_written:6d} | "
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

            # Gzip ISIZE guard
            isize = get_gzip_isize(item["path"])
            if isize > max_isize_bytes:
                logs_skipped += 1
                skip_reasons[f"oversize (isize {isize / (1024*1024):.1f}MB > {args.max_isize_mb}MB)"] += 1
                continue

            # Read records via RawStore
            try:
                records = store.read_records(item["repo"], "logs", item["job_id"])
            except TruncatedRecordError as exc:
                logs_skipped += 1
                msg = str(exc).split(":")[0] if ":" in str(exc) else str(exc)
                skip_reasons[f"truncated ({msg})"] += 1
                continue
            except Exception as exc:
                logs_skipped += 1
                skip_reasons[f"read_error ({type(exc).__name__})"] += 1
                continue

            if not records or not records[0].body:
                logs_parsed += 1
                classification_counts["NO_TEST_OUTPUT"] += 1
                continue

            body_text = records[0].body.decode("utf-8", errors="replace")

            # Parse log text via dispatch
            try:
                outcomes, stats = dispatch_parse_log_with_stats(
                    body_text,
                    run_id=item["parent_run_id"],
                    job_id=item["job_id"],
                    repo=item["repo"],
                    head_sha=None,
                )
            except Exception as exc:
                logs_skipped += 1
                skip_reasons[f"parse_error ({type(exc).__name__})"] += 1
                continue

            logs_parsed += 1
            harness = stats.format_detected

            if outcomes:
                valid_items: list[tuple[Any, Any]] = []
                for o in outcomes:
                    tid = normalize_test_id(o.test_id)
                    if tid is None:
                        unnormalizable_count += 1
                        if len(unnormalizable_examples) < 20:
                            unnormalizable_examples.append(o.test_id)
                        continue
                    valid_items.append((o, tid))

                if valid_items:
                    classification_counts["TEST_FAILURE"] += 1
                    for o, tid in valid_items:
                        canonical_id = tid.canonical
                        params = tid.params

                        # Determine is_fqcn_qualified per Amendment 2
                        if "#" in canonical_id:
                            cls_part = canonical_id.split("#", 1)[0]
                            is_fqcn = "." in cls_part
                        elif "::" in canonical_id:
                            is_fqcn = True
                        else:
                            is_fqcn = False

                        # Resolve harness to maven / gradle / pytest
                        if stats.format_detected in ("maven", "gradle", "pytest"):
                            row_harness = stats.format_detected
                        elif tid.lang == "python":
                            row_harness = "pytest"
                        elif "> Task :" in body_text or ":test" in body_text:
                            row_harness = "gradle"
                        else:
                            row_harness = "maven"

                        row = {
                            "test_id": canonical_id,
                            "parser_confidence": float(o.parser_confidence),
                            "run_id": item["parent_run_id"],
                            "job_id": item["job_id"],
                            "repo": item["repo"],
                            "head_sha": None,
                            "test_file": o.test_file,
                            "status": o.status,
                            "duration_s": float(o.duration_s) if o.duration_s is not None else None,
                            "failure_message": o.failure_message,
                            "label_source": o.label_source or "log",
                            "harness": row_harness,
                            "is_fqcn_qualified": bool(is_fqcn),
                            "params": params,
                        }
                        batch_rows.append(row)
                        total_outcomes_written += 1

                        # Tracking aggregates
                        distinct_test_ids.add(canonical_id)
                        distinct_test_ids_by_harness[row_harness].add(canonical_id)

                        repo_lang = frame_map.get(item["repo"], "unknown")
                        distinct_test_ids_by_lang[repo_lang].add(canonical_id)
                        repo_distinct_ids[item["repo"]].add(canonical_id)

                        if is_fqcn:
                            fqcn_outcome_true_count += 1
                            fqcn_distinct_true_ids.add(canonical_id)
                        else:
                            fqcn_outcome_false_count += 1
                            fqcn_distinct_false_ids.add(canonical_id)

                        if len(batch_rows) >= args.batch_size:
                            table = pa.Table.from_pylist(batch_rows, schema=PARQUET_SCHEMA)
                            if writer is None:
                                writer = pq.ParquetWriter(
                                    args.output, schema=PARQUET_SCHEMA, compression="snappy"
                                )
                            writer.write_table(table)
                            batch_rows.clear()
                else:
                    # All candidate outcomes were unnormalizable
                    cls, _, _ = classify_dispatch_log(body_text)
                    if cls == "TEST_FAILURE":
                        cls = "NO_TEST_OUTPUT"
                    classification_counts[cls] += 1
            else:
                # 0 outcomes: classify clean test run vs no test output
                cls, _, _ = classify_dispatch_log(body_text)
                if cls == "TEST_FAILURE":
                    cls = "NO_TEST_OUTPUT"
                classification_counts[cls] += 1

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
        elif total_outcomes_written == 0:
            # Emit empty parquet file with schema
            table = pa.Table.from_pylist([], schema=PARQUET_SCHEMA)
            writer = pq.ParquetWriter(
                args.output, schema=PARQUET_SCHEMA, compression="snappy"
            )
            writer.write_table(table)
            writer.close()

    total_wall_clock = time.time() - start_time
    run_end_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    peak_rss = get_peak_rss_mb()

    # 5. Write CORPUS_PIN.json
    pin_data = {
        "as_of": as_of_iso,
        "file_count": total_logs_to_process,
        "git_head_sha": get_git_head_sha(),
        "run_start_utc": run_start_utc,
        "run_end_utc": run_end_utc,
        "completed_at_resolved_via": "cursor.db capture_unit table lookup on (repo, 'logs', unit_key)",
    }
    with open(args.pin_file, "w", encoding="utf-8") as f:
        json.dump(pin_data, f, indent=2)

    # 6. Comprehensive Summary & Metrics Output
    print()
    print("=" * 80)
    print("FINAL SUMMARY REPORT")
    print("=" * 80)
    print(f"Total Wall Clock Time:     {format_duration(total_wall_clock)} ({total_wall_clock:.2f} s)")
    print(f"Peak RSS Memory:           {peak_rss:.2f} MB")
    print(f"Parquet Dataset:           {args.output} ({args.output.stat().st_size:,} bytes)")
    print(f"Pin File:                  {args.pin_file}")
    print()

    print("1. LOG SCAN & SKIP BREAKDOWN:")
    print(f"  Logs Scanned:            {logs_scanned:,}")
    print(f"  Logs Parsed:             {logs_parsed:,} ({logs_parsed/logs_scanned*100:.2f}%)" if logs_scanned else "  Logs Parsed: 0")
    print(f"  Logs Skipped:            {logs_skipped:,} ({logs_skipped/logs_scanned*100:.2f}%)" if logs_scanned else "  Logs Skipped: 0")
    if skip_reasons:
        print("  Skip Reasons Breakdown:")
        for reason, cnt in skip_reasons.most_common():
            print(f"    - {reason}: {cnt:,}")
    if unnormalizable_count:
        print(f"  Unnormalizable Raw IDs:  {unnormalizable_count:,} (excluded from dataset)")
        if unnormalizable_examples:
            print("    Sample unnormalizable IDs:")
            for ex in unnormalizable_examples[:5]:
                print(f"      * {ex!r}")
    print()

    print("2. LOG CLASSIFICATION BREAKDOWN:")
    for cls_name in ["TEST_FAILURE", "TEST_RAN_CLEAN", "NO_TEST_OUTPUT"]:
        cnt = classification_counts[cls_name]
        pct = (cnt / logs_parsed * 100.0) if logs_parsed > 0 else 0.0
        print(f"  {cls_name:<20s}: {cnt:6,d} ({pct:5.2f}%)")
    print()

    print("3. OUTCOMES & IDENTIFIERS:")
    print(f"  Total Outcome Rows:      {total_outcomes_written:,}")
    print(f"  Distinct Canonical IDs:  {len(distinct_test_ids):,}")
    print()

    print("4. DISTINCT TEST_ID PER HARNESS:")
    for h in sorted(distinct_test_ids_by_harness):
        cnt = len(distinct_test_ids_by_harness[h])
        print(f"  {h:<15s}: {cnt:6,d} distinct test IDs")
    print()

    print("5. DISTINCT TEST_ID PER LANGUAGE (via frame_v1.csv):")
    for lang in sorted(distinct_test_ids_by_lang):
        cnt = len(distinct_test_ids_by_lang[lang])
        print(f"  {lang:<15s}: {cnt:6,d} distinct test IDs")
    py_count = len(distinct_test_ids_by_lang.get("Python", set()))
    print(f"  --> Python-classified repos yielded {py_count:,} distinct test IDs.")
    print()

    print("6. IS_FQCN_QUALIFIED (Gate 1.5 Readiness Headline):")
    total_fqcn_outcomes = fqcn_outcome_true_count + fqcn_outcome_false_count
    outcome_pct = (fqcn_outcome_true_count / total_fqcn_outcomes * 100.0) if total_fqcn_outcomes > 0 else 0.0
    print(f"  Outcome Rows True:       {fqcn_outcome_true_count:,}")
    print(f"  Outcome Rows False:      {fqcn_outcome_false_count:,}")
    print(f"  Outcome Qualification:   {outcome_pct:.2f}%")
    total_fqcn_distinct = len(fqcn_distinct_true_ids) + len(fqcn_distinct_false_ids)
    distinct_pct = (len(fqcn_distinct_true_ids) / total_fqcn_distinct * 100.0) if total_fqcn_distinct > 0 else 0.0
    print(f"  Distinct IDs True:       {len(fqcn_distinct_true_ids):,}")
    print(f"  Distinct IDs False:      {len(fqcn_distinct_false_ids):,}")
    print(f"  Distinct Qualification:  {distinct_pct:.2f}%")
    print()

    print("7. REPOSITORY YIELD:")
    # Top 15 repos by distinct test_id
    sorted_repos = sorted(repo_distinct_ids.items(), key=lambda x: len(x[1]), reverse=True)
    print("  Top 15 Repositories by Distinct Test IDs:")
    for rank, (repo, ids) in enumerate(sorted_repos[:15], start=1):
        print(f"    {rank:2d}. {repo:<40s}: {len(ids):5,d} distinct test IDs")

    # Count repos in corpus yielding 0 test IDs
    all_corpus_repos = {item["repo"] for item in worklist}
    zero_yield_repos = [r for r in all_corpus_repos if len(repo_distinct_ids[r]) == 0]
    print(f"  Repos in corpus with 0 test failure outcomes: {len(zero_yield_repos):,}/{len(all_corpus_repos):,}")
    print("=" * 80)


if __name__ == "__main__":
    main()
