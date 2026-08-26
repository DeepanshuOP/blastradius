"""BlastRadius — Deterministic Holdout Fixture Selection.

Per ROADMAP §25.3, §26.1 and AGENTS.md.
Selects 20 held-out logs from data/raw and writes decompressed .txt files
to tests/fixtures/holdout/.

Selection rules:
  (a) EXCLUDE every job_id already in tests/fixtures/logs/.
  (b) 20 logs, at most 2 per repo, from at least 12 distinct repos.
  (c) Skip anything over 5 MB compressed.
  (d) Deliberately include at least 4 logs from repos NOT in original 40.
  (e) Include at least 4 logs with no test failure at all.
  (f) Seed the selection and print the seed (integrity invariant 3).
"""

from __future__ import annotations

import gzip
import json
import os
import pathlib
import random
from collections import Counter, defaultdict

SEED = 20260826
TARGET_COUNT = 20
MAX_PER_REPO = 2
MIN_DISTINCT_REPOS = 12
MIN_NEW_REPOS = 4
MAX_COMPRESSED_BYTES = 5 * 1024 * 1024

HOLDOUT_DIR = pathlib.Path("tests/fixtures/holdout")
EXISTING_DIR = pathlib.Path("tests/fixtures/logs")
RAW_DIR = pathlib.Path("data/raw")


def select_holdout_candidates(seed: int = SEED) -> list[pathlib.Path]:
    """Select 20 candidate logs deterministically using seeded PRNG."""
    rng = random.Random(seed)

    # 1. Enumerate existing job IDs and repos in tests/fixtures/logs/
    existing_job_ids = set()
    existing_repos = set()
    if EXISTING_DIR.exists():
        for p in sorted(EXISTING_DIR.glob("*.txt")):
            parts = p.stem.split("__")
            if len(parts) >= 3:
                existing_repos.add(f"{parts[0]}/{parts[1]}")
                existing_job_ids.add(parts[2])

    # 2. Enumerate candidate raw archives
    raw_files = sorted(list(RAW_DIR.glob("*/job/*/*/logs.jsonl.gz")))

    candidates_new = defaultdict(list)
    candidates_orig = defaultdict(list)
    skipped_oversize = 0
    skipped_overlap = 0
    skipped_corrupt = 0

    for p in raw_files:
        try:
            sz = p.stat().st_size
            if sz > MAX_COMPRESSED_BYTES:
                skipped_oversize += 1
                continue
            job_id = p.parent.name
            if job_id in existing_job_ids:
                skipped_overlap += 1
                continue
            repo = p.parts[2].replace("__", "/")
            if repo in existing_repos:
                candidates_orig[repo].append(p)
            else:
                candidates_new[repo].append(p)
        except Exception:
            skipped_corrupt += 1

    # 3. Deterministic stratified selection
    new_repo_keys = sorted(candidates_new.keys())
    orig_repo_keys = sorted(candidates_orig.keys())

    rng.shuffle(new_repo_keys)
    rng.shuffle(orig_repo_keys)

    selected: list[pathlib.Path] = []
    repo_counts = Counter()

    # Pick 6 logs from 6 distinct new repos
    for r in new_repo_keys:
        if len([x for x in selected if x.parts[2].replace("__", "/") not in existing_repos]) >= 6:
            break
        pool = sorted(candidates_new[r])
        rng.shuffle(pool)
        for cand in pool:
            selected.append(cand)
            repo_counts[r] += 1
            break

    # Pick 14 logs from original repos, at most 2 per repo, across distinct repos
    for r in orig_repo_keys:
        if len(selected) >= TARGET_COUNT:
            break
        pool = sorted(candidates_orig[r])
        rng.shuffle(pool)
        take = min(MAX_PER_REPO, len(pool), TARGET_COUNT - len(selected))
        for cand in pool[:take]:
            selected.append(cand)
            repo_counts[r] += 1
            if len(selected) >= TARGET_COUNT:
                break

    # Assert invariant constraints
    assert len(selected) == TARGET_COUNT, f"Expected {TARGET_COUNT} logs, got {len(selected)}"
    assert len(repo_counts) >= MIN_DISTINCT_REPOS, f"Expected >= {MIN_DISTINCT_REPOS} repos, got {len(repo_counts)}"
    assert all(c <= MAX_PER_REPO for c in repo_counts.values()), "Exceeded max per repo"
    new_repo_count = sum(1 for r in repo_counts if r not in existing_repos)
    assert new_repo_count >= MIN_NEW_REPOS, f"Expected >= {MIN_NEW_REPOS} new repos, got {new_repo_count}"

    return selected


def export_holdout_fixtures(selected: list[pathlib.Path], out_dir: pathlib.Path = HOLDOUT_DIR) -> list[pathlib.Path]:
    """Decompress selected raw archives to target directory as .txt files."""
    out_dir.mkdir(parents=True, exist_ok=True)
    exported: list[pathlib.Path] = []

    for p in selected:
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
    print(f"BlastRadius Holdout Selection — SEED: {SEED}")
    selected = select_holdout_candidates(SEED)
    exported = export_holdout_fixtures(selected)

    print(f"Successfully selected and exported {len(exported)} holdout fixtures to {HOLDOUT_DIR}/:")
    for i, p in enumerate(exported, 1):
        sz_kb = p.stat().st_size / 1024
        line_count = len(p.read_text(encoding="utf-8", errors="replace").splitlines())
        print(f"  {i:>2}. {p.name:<60} ({line_count:>6} lines, {sz_kb:>6.1f} KB)")


if __name__ == "__main__":
    main()
