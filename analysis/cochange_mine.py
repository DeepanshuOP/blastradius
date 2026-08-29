"""BlastRadius — Git Commit Co-Change Mining (T1.4).

Per ROADMAP §9.4, §31, and DECISIONS.md.
Mines historical file co-change relationships over a trailing window (default 365 days)
ending at the corpus pin (default 2026-08-29T14:13:00Z).

Computes association metrics for all co-occurring file pairs:
  - support          = count(A and B modified together in same commit)
  - confidence(A->B) = support / count(A)
  - confidence(B->A) = support / count(B)
  - lift             = confidence(A->B) / (count(B) / n_commits)
                     = (support * n_commits) / (count(A) * count(B))

Prunes pairs with support < support_threshold (default 3) per repository to bound
memory consumption. Emits data/interim/cochange.parquet and data/interim/COCHANGE_PIN.json.
"""

from __future__ import annotations

import argparse
import datetime
import itertools
import json
import os
import resource
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterator

import pyarrow as pa
import pyarrow.parquet as pq

DEFAULT_AS_OF = "2026-08-29T14:13:00Z"
DEFAULT_WINDOW_DAYS = 365
DEFAULT_SUPPORT_THRESHOLD = 3
DEFAULT_MAX_FILES_PER_COMMIT = 50
DEFAULT_CLONES_DIR = Path("data/clones")
DEFAULT_OUTPUT_PARQUET = Path("data/interim/cochange.parquet")
DEFAULT_PIN_FILE = Path("data/interim/COCHANGE_PIN.json")

RSS_LIMIT_MB = 3072.0  # 3 GB hard memory guard

COCHANGE_SCHEMA = pa.schema(
    [
        ("repo_full", pa.string()),
        ("file_a", pa.string()),
        ("file_b", pa.string()),
        ("support", pa.int64()),
        ("conf_a_to_b", pa.float64()),
        ("conf_b_to_a", pa.float64()),
        ("lift", pa.float64()),
        ("n_commits_a", pa.int64()),
        ("n_commits_b", pa.int64()),
        ("n_commits_total", pa.int64()),
        ("window_days", pa.int32()),
        ("as_of", pa.string()),
    ],
    metadata={
        b"generator": b"analysis/cochange_mine.py",
        b"description": b"Mined file-level git commit co-change association metrics",
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


def get_git_head_sha(repo_dir: Path | str = ".") -> str:
    """Retrieve git HEAD commit sha for a repo directory."""
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode("ascii").strip()
    except Exception:
        return "unknown"


def parse_iso_datetime(dt_str: str) -> datetime.datetime:
    """Parse ISO-8601 string to timezone-aware UTC datetime."""
    cleaned = dt_str.replace("Z", "+00:00")
    dt = datetime.datetime.fromisoformat(cleaned)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


def format_iso_datetime(dt: datetime.datetime) -> str:
    """Format UTC datetime as standard ISO-8601 with trailing Z."""
    utc_dt = dt.astimezone(datetime.timezone.utc)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def discover_cloned_repos(clones_dir: Path) -> list[tuple[str, Path]]:
    """Discover cloned repositories in clones_dir returning (repo_full, repo_path) pairs."""
    if not clones_dir.is_dir():
        return []
    repos = []
    for entry in sorted(clones_dir.iterdir()):
        if entry.is_dir() and ((entry / ".git").exists() or (entry / "objects").exists()):
            name = entry.name
            if "__" in name:
                repo_full = name.replace("__", "/", 1)
            else:
                repo_full = name
            repos.append((repo_full, entry))
    return repos


def parse_git_log_commits(
    repo_path: Path,
    since_str: str,
    until_str: str,
) -> Iterator[tuple[str, list[str]]]:
    """Stream (commit_sha, files) for non-merge commits in window using git log --name-only."""
    separator = "@@@COMMIT:"
    cmd = [
        "git",
        "-C",
        str(repo_path),
        "log",
        f"--since={since_str}",
        f"--until={until_str}",
        "--no-merges",
        f"--pretty=format:{separator}%H",
        "--name-only",
    ]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=65536,
    )

    current_sha: str | None = None
    current_files: list[str] = []

    try:
        assert proc.stdout is not None
        for line in proc.stdout:
            line_str = line.strip()
            if not line_str:
                continue
            if line_str.startswith(separator):
                if current_sha is not None:
                    yield current_sha, current_files
                current_sha = line_str[len(separator) :]
                current_files = []
            else:
                if current_sha is not None:
                    current_files.append(line_str)
        if current_sha is not None:
            yield current_sha, current_files
    finally:
        if proc.stdout:
            proc.stdout.close()
        if proc.stderr:
            proc.stderr.close()
        proc.wait()


def mine_repo_cochange(
    repo_full: str,
    repo_path: Path,
    as_of: str,
    window_days: int,
    support_threshold: int = DEFAULT_SUPPORT_THRESHOLD,
    max_files_per_commit: int = DEFAULT_MAX_FILES_PER_COMMIT,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Mine co-change pairs and metrics for a single cloned repository.

    Returns:
        (retained_rows, repo_stats_dict)
    """
    as_of_dt = parse_iso_datetime(as_of)
    since_dt = as_of_dt - datetime.timedelta(days=window_days)
    since_str = format_iso_datetime(since_dt)
    until_str = format_iso_datetime(as_of_dt)

    # Get merge commit count and total commits count in window
    try:
        merges_out = subprocess.check_output(
            [
                "git",
                "-C",
                str(repo_path),
                "rev-list",
                "--count",
                "--merges",
                f"--since={since_str}",
                f"--until={until_str}",
                "HEAD",
            ],
            stderr=subprocess.DEVNULL,
        )
        merges_skipped = int(merges_out.decode("ascii").strip())
    except Exception:
        merges_skipped = 0

    try:
        total_commits_out = subprocess.check_output(
            [
                "git",
                "-C",
                str(repo_path),
                "rev-list",
                "--count",
                f"--since={since_str}",
                f"--until={until_str}",
                "HEAD",
            ],
            stderr=subprocess.DEVNULL,
        )
        total_commits_in_window = int(total_commits_out.decode("ascii").strip())
    except Exception:
        total_commits_in_window = 0

    repo_head_sha = get_git_head_sha(repo_path)

    file_commit_counts: dict[str, int] = defaultdict(int)
    pair_counts: dict[tuple[str, str], int] = defaultdict(int)

    commits_processed = 0
    mined_commits = 0
    oversize_commits_skipped = 0
    empty_commits_skipped = 0

    for sha, raw_files in parse_git_log_commits(repo_path, since_str, until_str):
        commits_processed += 1
        # Deduplicate and sort files in this commit
        unique_files = sorted(set(f for f in raw_files if f))

        if len(unique_files) > max_files_per_commit:
            oversize_commits_skipped += 1
            continue
        if len(unique_files) == 0:
            empty_commits_skipped += 1
            continue

        mined_commits += 1

        for f in unique_files:
            file_commit_counts[f] += 1

        if len(unique_files) >= 2:
            for f_a, f_b in itertools.combinations(unique_files, 2):
                pair_counts[(f_a, f_b)] += 1

        if commits_processed % 500 == 0:
            rss_mb = get_current_rss_mb()
            print(
                f"[HEARTBEAT] {repo_full:30s} | commits: {commits_processed:5d} "
                f"| pairs held: {len(pair_counts):7d} | RSS: {rss_mb:6.1f} MB",
                flush=True,
            )
            if rss_mb > RSS_LIMIT_MB:
                print(
                    f"\n[HARD ABORT] Memory guard tripped! Current RSS {rss_mb:.1f} MB "
                    f"exceeds limit {RSS_LIMIT_MB:.1f} MB.",
                    file=sys.stderr,
                    flush=True,
                )
                sys.exit(1)

    # Prune pairs with support < support_threshold
    pairs_held_before_pruning = len(pair_counts)
    pairs_pruned = 0
    pairs_retained = 0
    retained_rows: list[dict[str, Any]] = []

    n_commits_total = mined_commits

    for (f_a, f_b), support in pair_counts.items():
        if support < support_threshold:
            pairs_pruned += 1
            continue

        pairs_retained += 1
        n_a = file_commit_counts[f_a]
        n_b = file_commit_counts[f_b]

        conf_a_to_b = support / n_a if n_a > 0 else 0.0
        conf_b_to_a = support / n_b if n_b > 0 else 0.0

        # lift = P(A & B) / (P(A) * P(B)) = (support * n_commits_total) / (n_a * n_b)
        if n_a > 0 and n_b > 0 and n_commits_total > 0:
            lift = (support * n_commits_total) / (n_a * n_b)
        else:
            lift = 0.0

        retained_rows.append(
            {
                "repo_full": repo_full,
                "file_a": f_a,
                "file_b": f_b,
                "support": int(support),
                "conf_a_to_b": float(conf_a_to_b),
                "conf_b_to_a": float(conf_b_to_a),
                "lift": float(lift),
                "n_commits_a": int(n_a),
                "n_commits_b": int(n_b),
                "n_commits_total": int(n_commits_total),
                "window_days": int(window_days),
                "as_of": as_of,
            }
        )

    # Sort deterministically
    retained_rows.sort(
        key=lambda r: (
            r["repo_full"],
            -r["support"],
            -r["lift"],
            r["file_a"],
            r["file_b"],
        )
    )

    stats = {
        "repo_full": repo_full,
        "repo_path": str(repo_path),
        "git_head_sha": repo_head_sha,
        "total_commits_in_window": total_commits_in_window,
        "merges_skipped": merges_skipped,
        "oversize_commits_skipped": oversize_commits_skipped,
        "empty_commits_skipped": empty_commits_skipped,
        "mined_commits": mined_commits,
        "distinct_files_touched": len(file_commit_counts),
        "pairs_held_before_pruning": pairs_held_before_pruning,
        "pairs_retained": pairs_retained,
        "pairs_pruned": pairs_pruned,
    }

    return retained_rows, stats


def rows_to_arrow_table(rows: list[dict[str, Any]]) -> pa.Table:
    """Convert list of row dictionaries to pyarrow.Table conforming to COCHANGE_SCHEMA."""
    if not rows:
        return pa.Table.from_batches([], schema=COCHANGE_SCHEMA)

    pydict = {
        "repo_full": [r["repo_full"] for r in rows],
        "file_a": [r["file_a"] for r in rows],
        "file_b": [r["file_b"] for r in rows],
        "support": [r["support"] for r in rows],
        "conf_a_to_b": [r["conf_a_to_b"] for r in rows],
        "conf_b_to_a": [r["conf_b_to_a"] for r in rows],
        "lift": [r["lift"] for r in rows],
        "n_commits_a": [r["n_commits_a"] for r in rows],
        "n_commits_b": [r["n_commits_b"] for r in rows],
        "n_commits_total": [r["n_commits_total"] for r in rows],
        "window_days": [r["window_days"] for r in rows],
        "as_of": [r["as_of"] for r in rows],
    }
    return pa.Table.from_pydict(pydict, schema=COCHANGE_SCHEMA)


def mine_all_repos(
    clones_dir: Path = DEFAULT_CLONES_DIR,
    repo_filter: list[str] | None = None,
    as_of: str = DEFAULT_AS_OF,
    window_days: int = DEFAULT_WINDOW_DAYS,
    support_threshold: int = DEFAULT_SUPPORT_THRESHOLD,
    max_files_per_commit: int = DEFAULT_MAX_FILES_PER_COMMIT,
    output_parquet: Path = DEFAULT_OUTPUT_PARQUET,
    pin_file: Path = DEFAULT_PIN_FILE,
) -> tuple[int, list[dict[str, Any]]]:
    """Execute mining across all cloned repositories and write outputs."""
    t_start = time.perf_counter()
    start_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

    discovered = discover_cloned_repos(clones_dir)
    if repo_filter:
        filter_set = set(repo_filter)
        discovered = [d for d in discovered if d[0] in filter_set or d[1].name in filter_set]

    if not discovered:
        print(f"No cloned repositories found in {clones_dir}.", file=sys.stderr)
        return 0, []

    print(f"Starting co-change mining across {len(discovered)} repositories...")
    print(f"  as_of:                {as_of}")
    print(f"  window_days:          {window_days}")
    print(f"  support_threshold:    {support_threshold}")
    print(f"  max_files_per_commit: {max_files_per_commit}")
    print(f"  output_parquet:       {output_parquet}")
    print(f"  pin_file:             {pin_file}")

    output_parquet.parent.mkdir(parents=True, exist_ok=True)
    pin_file.parent.mkdir(parents=True, exist_ok=True)

    all_stats: list[dict[str, Any]] = []
    total_pairs_retained = 0
    total_pairs_pruned = 0

    writer = pq.ParquetWriter(
        str(output_parquet),
        COCHANGE_SCHEMA,
        compression="zstd",
    )

    try:
        for idx, (repo_full, repo_path) in enumerate(discovered, 1):
            print(f"\n--- [{idx}/{len(discovered)}] Mining {repo_full} ---", flush=True)
            repo_rows, repo_stats = mine_repo_cochange(
                repo_full=repo_full,
                repo_path=repo_path,
                as_of=as_of,
                window_days=window_days,
                support_threshold=support_threshold,
                max_files_per_commit=max_files_per_commit,
            )

            all_stats.append(repo_stats)
            total_pairs_retained += repo_stats["pairs_retained"]
            total_pairs_pruned += repo_stats["pairs_pruned"]

            if repo_rows:
                table = rows_to_arrow_table(repo_rows)
                writer.write_table(table)

            print(
                f"Completed {repo_full}: commits={repo_stats['mined_commits']} "
                f"| oversize_skipped={repo_stats['oversize_commits_skipped']} "
                f"| merges_skipped={repo_stats['merges_skipped']} "
                f"| distinct_files={repo_stats['distinct_files_touched']} "
                f"| retained_pairs={repo_stats['pairs_retained']} "
                f"| pruned_pairs={repo_stats['pairs_pruned']}",
                flush=True,
            )
    finally:
        writer.close()

    end_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    t_elapsed = time.perf_counter() - t_start

    pin_data = {
        "as_of": as_of,
        "window_days": window_days,
        "window_start": format_iso_datetime(parse_iso_datetime(as_of) - datetime.timedelta(days=window_days)),
        "support_threshold": support_threshold,
        "max_files_per_commit": max_files_per_commit,
        "git_head_sha": get_git_head_sha("."),
        "total_repos": len(all_stats),
        "total_pairs_retained": total_pairs_retained,
        "total_pairs_pruned": total_pairs_pruned,
        "total_mined_commits": sum(s["mined_commits"] for s in all_stats),
        "total_merges_skipped": sum(s["merges_skipped"] for s in all_stats),
        "total_oversize_commits_skipped": sum(s["oversize_commits_skipped"] for s in all_stats),
        "wall_clock_seconds": round(t_elapsed, 2),
        "peak_rss_mb": round(get_peak_rss_mb(), 2),
        "run_start_utc": start_utc,
        "run_end_utc": end_utc,
        "repos": all_stats,
    }

    with open(pin_file, "w", encoding="utf-8") as f:
        json.dump(pin_data, f, indent=2)

    print(f"\nSaved {total_pairs_retained} pairs to {output_parquet}")
    print(f"Saved pin metadata to {pin_file}")
    return total_pairs_retained, all_stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Mine git commit co-change association metrics.")
    parser.add_argument("--as-of", default=DEFAULT_AS_OF, help="Corpus pin timestamp (ISO-8601 UTC)")
    parser.add_argument("--window-days", type=int, default=DEFAULT_WINDOW_DAYS, help="Trailing window days")
    parser.add_argument("--support-threshold", type=int, default=DEFAULT_SUPPORT_THRESHOLD, help="Minimum support")
    parser.add_argument("--max-files-per-commit", type=int, default=DEFAULT_MAX_FILES_PER_COMMIT, help="Max files per commit")
    parser.add_argument("--clones-dir", type=Path, default=DEFAULT_CLONES_DIR, help="Path to clones directory")
    parser.add_argument("--repos", nargs="*", default=None, help="Explicit repository list to process")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PARQUET, help="Output parquet path")
    parser.add_argument("--pin-file", type=Path, default=DEFAULT_PIN_FILE, help="Output pin JSON path")

    args = parser.parse_args()

    mine_all_repos(
        clones_dir=args.clones_dir,
        repo_filter=args.repos,
        as_of=args.as_of,
        window_days=args.window_days,
        support_threshold=args.support_threshold,
        max_files_per_commit=args.max_files_per_commit,
        output_parquet=args.output,
        pin_file=args.pin_file,
    )


if __name__ == "__main__":
    main()
