"""Apply the API-side filters to the repo frame (T0.1, ROADMAP §8.1 subtasks
2-4, §23.1 rows 7-10, §23.3 stages 3-4).

Reads `data/frame/repos_raw.csv` (the merged SEART export, §23.3 stage 0-2)
and, for each repo, makes exactly two calls through `get_with_backoff()` —
the sole HTTP entry point (`src/harvest/ratelimit.py`) — to decide whether
the repo survives:

  1. `GET /repos/{o}/{r}/actions/runs` windowed to the last 90 days via
     `created=>={SINCE_DATE}` — CI-liveness (stage 3, §23.1 row 8, keep if
     >= CI_LIVENESS_THRESHOLD).
  2. `GET /repos/{o}/{r}/actions/workflows` — workflow triage (stage 4,
     §23.1 rows 9-10: keep if >=1 workflow matches test intent by name or
     path and does not match the exclude pattern).

This combines what ROADMAP §8.1 subtasks 2-3 name as two separate modules
(`liveness.py`, `workflow_triage.py`) into one file, per this task's explicit
instruction — flagging the consolidation here since the roadmap sketch says
otherwise.

Consumes ~7,300 requests for the full 3,671-repo frame, so every repo's
result is appended to `data/frame/repos.partial.csv` as soon as it's known
and a repo already present there is skipped on the next run — this WILL be
interrupted and must not re-fetch completed work.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from collections import Counter
from dataclasses import dataclass, fields
from pathlib import Path

from src.harvest.ratelimit import TokenPool, get_with_backoff

INPUT_PATH = Path("data/frame/repos_raw.csv")
PARTIAL_PATH = Path("data/frame/repos.partial.csv")
OUTPUT_PATH = Path("data/frame/repos.csv")
ATTRITION_PATH = Path("data/frame/attrition_stage.csv")

# 90-day floor for the CI-liveness window, resolved against "today"
# 2026-08-05 (data/frame/QUERY.md §4's convention). Given directly as ground
# truth by the task that specified this module, not recomputed here.
SINCE_DATE = "2026-05-07"

CI_LIVENESS_THRESHOLD = 100
DEFAULT_LIMIT = 20

INCLUDE_RE = re.compile(r"test|ci|build|pytest|mvn|gradle", re.IGNORECASE)
EXCLUDE_RE = re.compile(r"release|deploy|docker|publish|docs|dependabot|codeql|lint-only", re.IGNORECASE)

OUTPUT_COLUMNS = [
    "owner",
    "repo",
    "lang",
    "stars",
    "commits",
    "default_branch",
    "n_runs_90d",
    "test_workflow_ids",
    "license",
]

ATTRITION_COLUMNS = [
    "owner",
    "repo",
    "lang",
    "n_runs_90d",
    "n_workflows",
    "n_test_workflows",
    "verdict",
]


@dataclass
class RepoResult:
    owner: str
    repo: str
    lang: str
    stars: str
    commits: str
    default_branch: str
    license: str
    n_runs_90d: str
    n_workflows: str
    n_test_workflows: str
    test_workflow_ids: str
    verdict: str


PARTIAL_COLUMNS = [f.name for f in fields(RepoResult)]


def is_test_intent(workflow: dict) -> bool:
    haystack = f"{workflow.get('name', '')} {workflow.get('path', '')}"
    if EXCLUDE_RE.search(haystack):
        return False
    return bool(INCLUDE_RE.search(haystack))


def classify_workflows(workflows: list[dict]) -> list[int]:
    return [w["id"] for w in workflows if is_test_intent(w)]


def fetch_n_runs_90d(owner: str, repo: str, pool: TokenPool, since: str) -> int:
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
    response = get_with_backoff(url, params={"per_page": 1, "created": f">={since}"}, pool=pool)
    return response.json()["total_count"]


def fetch_workflows(owner: str, repo: str, pool: TokenPool) -> list[dict]:
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows"
    response = get_with_backoff(url, pool=pool)
    return response.json().get("workflows", [])


def process_repo(row: dict, pool: TokenPool, since: str) -> RepoResult:
    owner, repo = row["name"].split("/", 1)
    base = dict(
        owner=owner,
        repo=repo,
        lang=row["mainLanguage"],
        stars=row["stargazers"],
        commits=row["commits"],
        default_branch=row["defaultBranch"],
        license=row["license"],
    )

    try:
        n_runs_90d = fetch_n_runs_90d(owner, repo, pool, since)
    except Exception:
        return RepoResult(
            **base,
            n_runs_90d="",
            n_workflows="",
            n_test_workflows="",
            test_workflow_ids="",
            verdict="api_error",
        )

    try:
        workflows = fetch_workflows(owner, repo, pool)
    except Exception:
        return RepoResult(
            **base,
            n_runs_90d=str(n_runs_90d),
            n_workflows="",
            n_test_workflows="",
            test_workflow_ids="",
            verdict="api_error",
        )

    test_ids = classify_workflows(workflows)
    n_workflows = len(workflows)
    n_test_workflows = len(test_ids)
    test_workflow_ids = ";".join(str(i) for i in test_ids)

    if n_runs_90d < CI_LIVENESS_THRESHOLD:
        verdict = "no_ci"
    elif n_test_workflows == 0:
        verdict = "no_test_workflow"
    else:
        verdict = "kept"

    return RepoResult(
        **base,
        n_runs_90d=str(n_runs_90d),
        n_workflows=str(n_workflows),
        n_test_workflows=str(n_test_workflows),
        test_workflow_ids=test_workflow_ids,
        verdict=verdict,
    )


def _load_partial(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _append_partial(path: Path, result: RepoResult) -> None:
    write_header = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=PARTIAL_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow(vars(result))
        fh.flush()
        os.fsync(fh.fileno())


def _write_repos_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for row in rows:
            if row["verdict"] != "kept":
                continue
            writer.writerow({col: row[col] for col in OUTPUT_COLUMNS})


def _write_attrition_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=ATTRITION_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row[col] for col in ATTRITION_COLUMNS})


def run_frame(
    *,
    pool: TokenPool,
    input_path: Path = INPUT_PATH,
    partial_path: Path = PARTIAL_PATH,
    output_path: Path = OUTPUT_PATH,
    attrition_path: Path = ATTRITION_PATH,
    since: str = SINCE_DATE,
    limit: int = DEFAULT_LIMIT,
) -> dict:
    with input_path.open("r", newline="", encoding="utf-8") as fh:
        input_rows = list(csv.DictReader(fh))

    existing_rows = _load_partial(partial_path)
    done_keys = {(r["owner"], r["repo"]) for r in existing_rows}

    newly_processed = 0
    for row in input_rows:
        owner, repo = row["name"].split("/", 1)
        if (owner, repo) in done_keys:
            continue
        if newly_processed >= limit:
            break
        result = process_repo(row, pool, since)
        _append_partial(partial_path, result)
        newly_processed += 1

    all_rows = _load_partial(partial_path)
    _write_repos_csv(output_path, all_rows)
    _write_attrition_csv(attrition_path, all_rows)

    verdict_counts = dict(Counter(r["verdict"] for r in all_rows))
    return {
        "newly_processed": newly_processed,
        "total_recorded": len(all_rows),
        "verdict_counts": verdict_counts,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    pool = TokenPool.from_env()
    summary = run_frame(pool=pool, limit=args.limit)

    print(f"Newly processed this run: {summary['newly_processed']}")
    print(f"Total repos recorded so far: {summary['total_recorded']}")
    print(f"Verdict counts: {summary['verdict_counts']}")
    print(f"Wrote {OUTPUT_PATH} and {ATTRITION_PATH}")


if __name__ == "__main__":
    main()
