"""BlastRadius — Deterministic Stratified Holdout Fixture Selection (v3).

Per ROADMAP §25.3, §26.1, DECISIONS.md (D-27, D-29, D-31), and AGENTS.md.
Constructs a third quarantined evaluation corpus (holdout_v3) partitioned into:
1. Core Partition (25 logs):
   - 18 failure-bearing logs (10 Maven, 8 Gradle)
   - 7 non-failing logs (5 NO_SUMMARY, 2 Maven Clean)
   - 0 repository overlap with tests/fixtures/logs/ (Dev) AND tests/fixtures/holdout/ (v2)
   - Max 2 logs per repository
   - 14 distinct unseen repositories
   - All logs <= 8 MB uncompressed size (via ISIZE trailer check)
2. Pytest Supplement Partition (5 logs):
   - 5 failure-bearing Pytest logs from apache/beam
   - 0 overlap at the LOG level against dev and v2
   - Distinctly marked partition with explicit repo-overlap caveat

Deterministic PRNG seeded with constant SEED (20260828).
Selected via two-stage draw: initial draw at seed 20260828, followed by replacement
of two oversize fixtures (> 8 MB uncompressed) with next eligible candidates in the
same seeded permutation.
"""

from __future__ import annotations

import csv
import gzip
import json
import pathlib
import random
import struct
from collections import Counter

from analysis.expected_audit import extract_harness_count

SEED = 20260828
MAX_COMPRESSED_BYTES = 5 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 8 * 1024 * 1024
MAX_FAILURES_PER_LOG = 6

CORE_TARGET_FAILING_MAVEN = 10
CORE_TARGET_FAILING_GRADLE = 8
CORE_TARGET_CLEAN = 7
CORE_MAX_PER_REPO = 2

SUPPLEMENT_TARGET_PYTEST = 5

HOLDOUT_V3_DIR = pathlib.Path("tests/fixtures/holdout_v3")
DEV_DIR = pathlib.Path("tests/fixtures/logs")
HOLDOUT_V2_DIR = pathlib.Path("tests/fixtures/holdout")
RAW_DIR = pathlib.Path("data/raw")
FRAME_PATH = pathlib.Path("data/frame/frame_v1.csv")
MANIFEST_PATH = pathlib.Path(__file__).parent / "holdout_v3_manifest.json"


def get_gzip_isize(p: pathlib.Path) -> int:
    """Read the uncompressed size (ISIZE) from the 8-byte gzip trailer."""
    with open(p, "rb") as f:
        f.seek(-4, 2)
        return struct.unpack("<I", f.read(4))[0]


def _get_existing_metadata() -> tuple[set[str], set[str]]:
    """Retrieve all previously sampled repository names and job IDs from dev and v2."""
    used_repos: set[str] = set()
    used_jobs: set[str] = set()
    for d in (DEV_DIR, HOLDOUT_V2_DIR):
        if d.exists():
            for p in d.glob("*.txt"):
                parts = p.stem.split("__")
                if len(parts) >= 3:
                    used_repos.add(f"{parts[0]}/{parts[1]}")
                    used_jobs.add(parts[2])
    return used_repos, used_jobs


def _get_java_frame_repos() -> set[str]:
    """Retrieve all Java repositories from frame_v1.csv."""
    java_repos: set[str] = set()
    if FRAME_PATH.exists():
        with open(FRAME_PATH, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("lang") == "Java":
                    java_repos.add(f"{row['owner']}/{row['repo']}")
    return java_repos


def _inspect_candidate(path_str: str) -> dict:
    """Inspect a single raw archive and extract harness summary metadata sequentially."""
    p = pathlib.Path(path_str)
    try:
        sz = p.stat().st_size
        if sz > MAX_COMPRESSED_BYTES:
            return {"status": "oversize", "compressed_size": sz, "path": path_str}

        isize = get_gzip_isize(p)
        jid = p.parent.name
        repo = p.parts[2].replace("__", "/")

        with gzip.open(p, "rt", encoding="utf-8", errors="replace") as gz:
            line = gz.readline()
            if not line:
                return {"status": "empty", "path": path_str}
            data = json.loads(line)
            body = data.get("body", "")

        cnt, h_type, evid = extract_harness_count(body)
        nlines = len(body.splitlines())
        del body
        del data

        return {
            "status": "ok",
            "path": path_str,
            "repo": repo,
            "job_id": jid,
            "harness_count": cnt,
            "harness_type": h_type,
            "evidence": evid,
            "compressed_size": sz,
            "uncompressed_size": isize,
            "lines": nlines,
        }
    except Exception as e:
        return {"status": "error", "path": path_str, "err": str(e)}


def load_or_scan_manifest(manifest_path: pathlib.Path = MANIFEST_PATH) -> list[dict]:
    """Load candidate manifest from disk, or scan raw Java logs sequentially to generate it."""
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            candidates = json.load(f)
        return candidates

    java_repos = _get_java_frame_repos()
    raw_files = [
        str(p)
        for p in sorted(list(RAW_DIR.glob("*/job/*/*/logs.jsonl.gz")))
        if p.parts[2].replace("__", "/") in java_repos
    ]

    inspected = []
    for fpath in raw_files:
        res = _inspect_candidate(fpath)
        if res.get("status") == "ok":
            inspected.append(res)

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(inspected, f, indent=2)

    return inspected


def select_holdout_v3(
    seed: int = SEED,
    manifest_path: pathlib.Path = MANIFEST_PATH,
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """Select the 25 core logs and 5 pytest supplement logs via two-stage deterministic selection.

    Returns: (final_core, supplement_selected, oversize_core, replacements)
    """
    used_repos, used_jobs = _get_existing_metadata()
    ok_logs = load_or_scan_manifest(manifest_path)

    # 1. CORE PARTITION SELECTION (Stage 1 Initial Draw at Seed 20260828)
    rng_core = random.Random(seed)
    core_candidates = [
        c for c in ok_logs
        if c["repo"] not in used_repos and c["job_id"] not in used_jobs
    ]

    fb_maven = [
        c for c in core_candidates
        if c["harness_count"] is not None
        and 1 <= c["harness_count"] <= MAX_FAILURES_PER_LOG
        and "Maven" in c["harness_type"]
    ]
    fb_gradle = [
        c for c in core_candidates
        if c["harness_count"] is not None
        and 1 <= c["harness_count"] <= MAX_FAILURES_PER_LOG
        and c["harness_type"] == "Gradle"
    ]
    clean_candidates = [
        c for c in core_candidates
        if c["harness_count"] == 0 or c["harness_count"] is None
    ]

    for pool in (fb_maven, fb_gradle, clean_candidates):
        pool.sort(key=lambda x: (x["repo"], x["job_id"]))
        rng_core.shuffle(pool)

    initial_core: list[dict] = []
    repo_counts = Counter()

    def try_add_core(cand: dict) -> bool:
        r = cand["repo"]
        if repo_counts[r] < CORE_MAX_PER_REPO:
            initial_core.append(cand)
            repo_counts[r] += 1
            return True
        return False

    for c in fb_maven:
        if len([x for x in initial_core if "Maven" in x["harness_type"]]) >= CORE_TARGET_FAILING_MAVEN:
            break
        try_add_core(c)

    for c in fb_gradle:
        if len([x for x in initial_core if x["harness_type"] == "Gradle"]) >= CORE_TARGET_FAILING_GRADLE:
            break
        try_add_core(c)

    for c in clean_candidates:
        if len([x for x in initial_core if x["harness_count"] == 0 or x["harness_count"] is None]) >= CORE_TARGET_CLEAN:
            break
        try_add_core(c)

    assert len(initial_core) == 25, f"Expected 25 initial core logs, got {len(initial_core)}"
    assert not (set(repo_counts.keys()) & used_repos), "Core partition has repo overlap!"

    # 2. SUPPLEMENT PARTITION SELECTION (apache/beam pytest logs, 0 log-level overlap)
    rng_supp = random.Random(seed)
    selected_core_jobs = set(x["job_id"] for x in initial_core)
    beam_pytest_candidates = [
        c for c in ok_logs
        if c["repo"] == "apache/beam"
        and c["harness_type"] == "Pytest"
        and c["harness_count"] is not None
        and 1 <= c["harness_count"] <= MAX_FAILURES_PER_LOG
        and c["job_id"] not in used_jobs
        and c["job_id"] not in selected_core_jobs
    ]
    beam_pytest_candidates.sort(key=lambda x: (x["repo"], x["job_id"]))
    rng_supp.shuffle(beam_pytest_candidates)

    supplement_selected = beam_pytest_candidates[:SUPPLEMENT_TARGET_PYTEST]
    assert len(supplement_selected) == 5, f"Expected 5 supplement logs, got {len(supplement_selected)}"

    # 3. STAGE 2: TWO-FIXTURE REPLACEMENT (8 MB UNCOMPRESSED CAP)
    oversize_core = [c for c in initial_core if c["uncompressed_size"] > MAX_UNCOMPRESSED_BYTES]
    oversize_job_ids = set(c["job_id"] for c in oversize_core)

    kept_core = [c for c in initial_core if c["job_id"] not in oversize_job_ids]
    kept_repo_counts = Counter(c["repo"] for c in kept_core)
    kept_job_ids = set(c["job_id"] for c in kept_core)

    replacements: list[dict] = []
    for c in fb_maven:
        jid = c["job_id"]
        r = c["repo"]
        if jid in kept_job_ids or jid in oversize_job_ids:
            continue
        if c["uncompressed_size"] > MAX_UNCOMPRESSED_BYTES:
            continue
        if kept_repo_counts[r] >= CORE_MAX_PER_REPO:
            continue
        replacements.append(c)
        kept_repo_counts[r] += 1
        if len(replacements) == len(oversize_core):
            break

    assert len(replacements) == len(oversize_core), f"Could not find {len(oversize_core)} replacements"

    final_core: list[dict] = []
    repl_idx = 0
    for c in initial_core:
        if c["job_id"] in oversize_job_ids:
            final_core.append(replacements[repl_idx])
            repl_idx += 1
        else:
            final_core.append(c)

    assert len(final_core) == 25, f"Expected 25 final core logs, got {len(final_core)}"
    assert not (set(kept_repo_counts.keys()) & used_repos), "Final core partition has repo overlap!"

    return final_core, supplement_selected, oversize_core, replacements


def export_fixtures(
    core_selected: list[dict],
    supplement_selected: list[dict],
    out_dir: pathlib.Path = HOLDOUT_V3_DIR,
) -> list[pathlib.Path]:
    """Decompress and write selected fixtures to target directory, removing obsolete fixtures."""
    out_dir.mkdir(parents=True, exist_ok=True)
    all_selected = core_selected + supplement_selected
    exported: list[pathlib.Path] = []
    valid_filenames = set()

    for item in all_selected:
        p = pathlib.Path(item["path"])
        repo_owner_name = p.parts[2]
        job_id = p.parent.name
        out_filename = f"{repo_owner_name}__{job_id}.txt"
        valid_filenames.add(out_filename)
        out_path = out_dir / out_filename

        with gzip.open(p, "rt", encoding="utf-8", errors="replace") as gz:
            line = gz.readline()
            data = json.loads(line)
            body = data.get("body", "")

        out_path.write_text(body, encoding="utf-8")
        del body
        del data
        exported.append(out_path)

    # Remove any stale fixture .txt files in holdout_v3
    for existing_file in out_dir.glob("*.txt"):
        if existing_file.name not in valid_filenames:
            existing_file.unlink()

    return exported


def main() -> None:
    print(f"=== BlastRadius Holdout v3 Construction (Seed {SEED}) ===")
    final_core, supplement_selected, oversize_core, replacements = select_holdout_v3(
        SEED, MANIFEST_PATH
    )
    exported = export_fixtures(final_core, supplement_selected)

    print(f"\nSuccessfully exported {len(exported)} fixtures to {HOLDOUT_V3_DIR}/")
    print(f"\n--- STAGE 2 REPLACEMENTS ({len(oversize_core)} oversize fixtures replaced) ---")
    for orig, repl in zip(oversize_core, replacements):
        orig_p = pathlib.Path(orig["path"])
        repl_p = pathlib.Path(repl["path"])
        orig_fn = f"{orig_p.parts[2]}__{orig['job_id']}.txt"
        repl_fn = f"{repl_p.parts[2]}__{repl['job_id']}.txt"
        print(f"  Replaced: {orig_fn:<45} ({orig['uncompressed_size']/(1024*1024):6.2f} MB)")
        print(f"      With: {repl_fn:<45} ({repl['uncompressed_size']/(1024*1024):6.2f} MB, fail:{repl['harness_count']})")

    print(f"\n--- PARTITION A: Core Fixtures ({len(final_core)} logs, 0 repo overlap) ---")
    for i, s in enumerate(final_core, 1):
        p = pathlib.Path(s["path"])
        fname = f"{p.parts[2]}__{s['job_id']}.txt"
        cnt = s["harness_count"] if s["harness_count"] is not None else 0
        uncomp_mb = s["uncompressed_size"] / (1024 * 1024)
        print(f"  {i:>2}. {fname:<55} | {s['repo']:<28} | {s['harness_type']:<17} | fail:{cnt:>2} | {uncomp_mb:>5.2f} MB")

    print(f"\n--- PARTITION B: Pytest Supplement ({len(supplement_selected)} logs, 0 log overlap) ---")
    for i, s in enumerate(supplement_selected, 26):
        p = pathlib.Path(s["path"])
        fname = f"{p.parts[2]}__{s['job_id']}.txt"
        cnt = s["harness_count"] if s["harness_count"] is not None else 0
        uncomp_mb = s["uncompressed_size"] / (1024 * 1024)
        print(f"  {i:>2}. {fname:<55} | {s['repo']:<28} | {s['harness_type']:<17} | fail:{cnt:>2} | {uncomp_mb:>5.2f} MB")


if __name__ == "__main__":
    main()
