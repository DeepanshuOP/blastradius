"""BlastRadius — Deterministic Stratified Holdout Fixture Selection (v2).

Per ROADMAP §25.3, §26.1 and AGENTS.md.
Selects 20 held-out logs from data/raw with failure stratification:
- 15 failure-bearing logs (mix of Maven, Gradle, and Pytest harnesses)
- 5 non-failing logs (NO_SUMMARY or zero failures)
- Zero overlap with tests/fixtures/logs/ AND v1 tests/fixtures/holdout/
- At most 2 logs per repository
- At least 12 distinct repositories
- At least 4 repositories absent from tests/fixtures/logs/
- Max compressed size <= 5 MB
- Deterministic PRNG seeded with constant SEED (20260826)
"""

from __future__ import annotations

import gzip
import json
import multiprocessing
import os
import pathlib
import random
from collections import Counter, defaultdict

from analysis.expected_audit import extract_harness_count

SEED = 20260826
TARGET_COUNT = 20
TARGET_FAILING_COUNT = 15
TARGET_NON_FAILING_COUNT = 5
MAX_PER_REPO = 2
MIN_DISTINCT_REPOS = 12
MIN_NEW_REPOS = 4
MAX_COMPRESSED_BYTES = 5 * 1024 * 1024
MAX_FAILURES_PER_LOG = 6

HOLDOUT_DIR = pathlib.Path("tests/fixtures/holdout")
EXISTING_DIR = pathlib.Path("tests/fixtures/logs")
RAW_DIR = pathlib.Path("data/raw")


def _inspect_candidate(path_str: str) -> dict:
    """Inspect a raw archive and extract harness summary metadata."""
    p = pathlib.Path(path_str)
    try:
        sz = p.stat().st_size
        if sz > MAX_COMPRESSED_BYTES:
            return {"status": "oversize", "size": sz, "path": path_str}
        jid = p.parent.name
        repo = p.parts[2].replace("__", "/")
        with gzip.open(p, "rt", encoding="utf-8", errors="replace") as gz:
            line = gz.readline()
            if not line:
                return {"status": "empty", "path": path_str}
            data = json.loads(line)
            body = data.get("body", "")

        cnt, h_type, evid = extract_harness_count(body)
        return {
            "status": "ok",
            "path": path_str,
            "repo": repo,
            "job_id": jid,
            "harness_count": cnt,
            "harness_type": h_type,
            "evidence": evid,
            "compressed_size": sz,
            "lines": len(body.splitlines()),
        }
    except Exception as e:
        return {"status": "error", "path": path_str, "err": str(e)}


def scan_and_measure_pool() -> tuple[list[dict], dict]:
    """Scan all raw archives in data/raw and return inspected candidate metadata."""
    raw_files = [str(p) for p in sorted(list(RAW_DIR.glob("*/job/*/*/logs.jsonl.gz")))]
    cpu_cores = os.cpu_count() or 4
    with multiprocessing.Pool(processes=cpu_cores) as pool:
        inspected = pool.map(_inspect_candidate, raw_files, chunksize=50)

    existing_logs_ids = set()
    if EXISTING_DIR.exists():
        for p in EXISTING_DIR.glob("*.txt"):
            parts = p.stem.split("__")
            if len(parts) >= 3:
                existing_logs_ids.add(parts[2])

    v1_holdout_ids = {
        "078093909304", "079375717291", "078459457993", "079332762566",
        "078050195307", "084107680035", "083114718053", "082913156708",
        "081674712291", "081853656807", "081451893643", "081577143906",
        "078003756269", "080017889012", "086150295955", "085859996738",
        "078736649370", "083289143209", "084724355515", "083974499807",
    }

    pool_stats = Counter()
    harness_types = Counter()
    valid_candidates = []

    for item in inspected:
        st = item["status"]
        if st == "oversize":
            pool_stats["oversize"] += 1
        elif st == "error":
            pool_stats["corrupt"] += 1
        elif st == "empty":
            pool_stats["empty"] += 1
        elif st == "ok":
            cnt = item["harness_count"]
            ht = item["harness_type"]
            jid = item["job_id"]
            if cnt is not None and cnt > 0:
                pool_stats["failure_bearing"] += 1
                harness_types[ht] += 1
            elif cnt == 0:
                pool_stats["zero_failures"] += 1
                harness_types[ht] += 1
            else:
                pool_stats["no_summary"] += 1
                harness_types["NO_SUMMARY"] += 1

            if jid not in existing_logs_ids and jid not in v1_holdout_ids:
                valid_candidates.append(item)

    summary = {
        "total_files": len(raw_files),
        "oversize": pool_stats["oversize"],
        "corrupt": pool_stats["corrupt"],
        "failure_bearing_total": pool_stats["failure_bearing"],
        "zero_failures_total": pool_stats["zero_failures"],
        "no_summary_total": pool_stats["no_summary"],
        "harness_types": dict(harness_types),
    }
    return valid_candidates, summary


def select_stratified_holdout(seed: int = SEED) -> list[dict]:
    """Select 20 candidate logs deterministically with failure stratification."""
    rng = random.Random(seed)
    candidates, _ = scan_and_measure_pool()

    existing_repos = set()
    if EXISTING_DIR.exists():
        for p in EXISTING_DIR.glob("*.txt"):
            parts = p.stem.split("__")
            if len(parts) >= 3:
                existing_repos.add(f"{parts[0]}/{parts[1]}")

    failing_maven = [
        c for c in candidates
        if c["harness_count"] is not None
        and 1 <= c["harness_count"] <= MAX_FAILURES_PER_LOG
        and "Maven" in c["harness_type"]
    ]
    failing_gradle = [
        c for c in candidates
        if c["harness_count"] is not None
        and 1 <= c["harness_count"] <= MAX_FAILURES_PER_LOG
        and c["harness_type"] == "Gradle"
    ]
    failing_pytest = [
        c for c in candidates
        if c["harness_count"] is not None
        and 1 <= c["harness_count"] <= MAX_FAILURES_PER_LOG
        and c["harness_type"] == "Pytest"
    ]
    non_failing = [
        c for c in candidates
        if c["harness_count"] is None or c["harness_count"] == 0
    ]

    for pool in [failing_maven, failing_gradle, failing_pytest, non_failing]:
        pool.sort(key=lambda x: (x["repo"], x["job_id"]))
        rng.shuffle(pool)

    selected: list[dict] = []
    repo_counts = Counter()

    def try_add(cand: dict) -> bool:
        r = cand["repo"]
        if repo_counts[r] < MAX_PER_REPO:
            selected.append(cand)
            repo_counts[r] += 1
            return True
        return False

    # 1. 2 Pytest logs
    for c in failing_pytest:
        if len([x for x in selected if x["harness_type"] == "Pytest"]) >= 2:
            break
        try_add(c)

    # 2. 6 Maven logs
    for c in failing_maven:
        if len([x for x in selected if "Maven" in x["harness_type"]]) >= 6:
            break
        try_add(c)

    # 3. 7 Gradle logs
    for c in failing_gradle:
        if len([x for x in selected if x["harness_type"] == "Gradle"]) >= 7:
            break
        try_add(c)

    # 4. Fill failing to 15 if needed
    all_failing = failing_pytest + failing_maven + failing_gradle
    for c in all_failing:
        if len([x for x in selected if x["harness_count"] is not None and x["harness_count"] > 0]) >= TARGET_FAILING_COUNT:
            break
        if c not in selected:
            try_add(c)

    # 5. Pick 5 non-failing logs
    for c in non_failing:
        if len(selected) >= TARGET_COUNT:
            break
        if c not in selected:
            try_add(c)

    assert len(selected) == TARGET_COUNT, f"Expected {TARGET_COUNT}, got {len(selected)}"
    failing_selected = [x for x in selected if x["harness_count"] is not None and x["harness_count"] > 0]
    assert len(failing_selected) == TARGET_FAILING_COUNT, f"Expected {TARGET_FAILING_COUNT} failing, got {len(failing_selected)}"
    assert len(repo_counts) >= MIN_DISTINCT_REPOS, f"Expected >= {MIN_DISTINCT_REPOS} repos, got {len(repo_counts)}"
    new_repos_count = sum(1 for r in repo_counts if r not in existing_repos)
    assert new_repos_count >= MIN_NEW_REPOS, f"Expected >= {MIN_NEW_REPOS} new repos, got {new_repos_count}"

    return selected


def export_holdout_fixtures(selected: list[dict], out_dir: pathlib.Path = HOLDOUT_DIR) -> list[pathlib.Path]:
    """Decompress selected raw archives to target directory as .txt files."""
    out_dir.mkdir(parents=True, exist_ok=True)
    exported: list[pathlib.Path] = []

    for item in selected:
        p = pathlib.Path(item["path"])
        repo_owner_name = p.parts[2]
        job_id = p.parent.name
        out_filename = f"{repo_owner_name}__{job_id}.txt"
        out_path = out_dir / out_filename

        with gzip.open(p, "rt", encoding="utf-8", errors="replace") as gz:
            line = gz.readline()
            data = json.loads(line)
            body = data.get("body", "")

        out_path.write_text(body, encoding="utf-8")
        exported.append(out_path)

    return exported


def main() -> None:
    print(f"BlastRadius Stratified Holdout Selection — SEED: {SEED}")
    _, summary = scan_and_measure_pool()
    print("=== TOTAL POOL MEASUREMENT ===")
    print(f"Total logs on disk: {summary['total_files']}")
    print(f"Oversize (>5MB compressed): {summary['oversize']}")
    print(f"Corrupt / mid-write: {summary['corrupt']}")
    print(f"Failure-bearing logs (all): {summary['failure_bearing_total']}")
    print(f"Zero-failure summary logs: {summary['zero_failures_total']}")
    print(f"No-summary logs: {summary['no_summary_total']}")
    print("Harness type breakdown (all logs):")
    for ht, c in sorted(summary["harness_types"].items(), key=lambda x: -x[1]):
        print(f"  {ht:<25}: {c}")

    selected = select_stratified_holdout(SEED)
    exported = export_holdout_fixtures(selected)

    print(f"\nSuccessfully selected and exported {len(exported)} holdout fixtures to {HOLDOUT_DIR}/:")
    for i, s in enumerate(selected, 1):
        p = pathlib.Path(s["path"])
        fname = f"{p.parts[2]}__{s['job_id']}.txt"
        cnt = s["harness_count"] if s["harness_count"] is not None else 0
        print(f"  {i:>2}. {fname:<55} | {s['repo']:<30} | {s['harness_type']:<17} | fail:{cnt:>2} | lines:{s['lines']:>5}")


if __name__ == "__main__":
    main()
