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

FAILURE HANDLING (added after a dead-credential cascade produced 20
api_error verdicts with no recorded cause, ROADMAP §8.2, §34.1 Rule 6):
TERMINAL failures (404/410/451 — the repo itself is gone) get a
permanent `api_error` row naming the failing call, status, and exception
class. TRANSIENT failures (everything else: 401/403/429/5xx, timeouts,
connection errors — a credential or infrastructure problem, not a fact
about the repo) are never written to repos.partial.csv at all, so the repo
is simply retried on the next invocation — no special resume flag needed,
since "not yet done" is already the natural state for a repo nothing was
ever written for. Five consecutive transient failures abort the run rather
than silently grinding through the rest of the frame producing nothing.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from collections import Counter
from dataclasses import dataclass, fields
from pathlib import Path

import requests

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

# A real, permanent fact about the repo — not evidence of a broken
# credential or a flaky backend. Everything else (401/403/429/5xx,
# timeouts, connection errors, and anything with no status code at all)
# is transient: we cannot prove the repo is gone, so we don't treat it
# as gone. 401 in particular means the credential is broken, not that
# the repo doesn't exist — see the dead-token cascade this fixes.
TERMINAL_STATUSES = frozenset({404, 410, 451})

# Five in a row is long enough to absorb an isolated flaky 403/5xx without
# aborting a healthy run, and short enough to fail fast rather than grind
# through the rest of a 3,671-repo frame on a dead credential — the exact
# failure mode this replaces (20 wasted repos, and at full scale it would
# have been ~2,900). Matches get_with_backoff's own MAX_ATTEMPTS=6 order of
# magnitude for "how much retrying is reasonable before assuming systemic
# failure."
CONSECUTIVE_TRANSIENT_LIMIT = 5

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
    "failing_call",
    "status",
    "exception_class",
]


class AbortRun(RuntimeError):
    """Raised to stop a run outright rather than let it keep writing
    nothing useful — startup token validation failures and runs of
    consecutive transient failures both raise this."""


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
    failing_call: str = ""
    status: str = ""
    exception_class: str = ""


@dataclass
class TransientFailure:
    """Sentinel returned by process_repo for a transient failure: nothing
    gets written for this repo, so it's retried on the next invocation."""

    exc: Exception


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


def _classify_failure(exc: Exception) -> tuple[str, str, str]:
    """Returns (bucket, status_str, exception_class_name). bucket is
    'terminal' (404/410/451 — write it and stay) or 'transient' (anything
    else, including no status code at all — retry next run)."""
    response = getattr(exc, "response", None)
    status = getattr(response, "status_code", None)
    status_str = str(status) if status is not None else ""
    exception_class = type(exc).__name__
    bucket = "terminal" if status in TERMINAL_STATUSES else "transient"
    return bucket, status_str, exception_class


def process_repo(row: dict, pool: TokenPool, since: str) -> RepoResult | TransientFailure:
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
    except Exception as exc:
        bucket, status, exception_class = _classify_failure(exc)
        if bucket == "transient":
            return TransientFailure(exc)
        return RepoResult(
            **base,
            n_runs_90d="",
            n_workflows="",
            n_test_workflows="",
            test_workflow_ids="",
            verdict="api_error",
            failing_call="runs",
            status=status,
            exception_class=exception_class,
        )

    try:
        workflows = fetch_workflows(owner, repo, pool)
    except Exception as exc:
        bucket, status, exception_class = _classify_failure(exc)
        if bucket == "transient":
            return TransientFailure(exc)
        return RepoResult(
            **base,
            n_runs_90d=str(n_runs_90d),
            n_workflows="",
            n_test_workflows="",
            test_workflow_ids="",
            verdict="api_error",
            failing_call="workflows",
            status=status,
            exception_class=exception_class,
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


def validate_tokens(pool: TokenPool) -> None:
    """One free GET /rate_limit per token before any repo is processed.
    /rate_limit doesn't count against quota but still checks auth, so a
    dead credential is caught here — one wasted request per token beats
    thousands of api_error rows from a pool that silently round-robins
    onto it. Relies on TokenPool.acquire()'s round-robin tie-break: every
    token starts at the same default quota, so len(pool) consecutive
    acquires visit each token index exactly once."""
    for _ in range(len(pool)):
        try:
            get_with_backoff("https://api.github.com/rate_limit", pool=pool)
        except requests.HTTPError as exc:
            token_idx = getattr(exc, "token_idx", "unknown")
            response = getattr(exc, "response", None)
            status = response.status_code if response is not None else "unknown"
            raise AbortRun(
                f"token validation failed: token_idx={token_idx} returned "
                f"status={status} on GET /rate_limit"
            ) from exc


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
            writer.writerow({col: row.get(col, "") for col in ATTRITION_COLUMNS})


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
    validate_tokens(pool)

    with input_path.open("r", newline="", encoding="utf-8") as fh:
        input_rows = list(csv.DictReader(fh))

    existing_rows = _load_partial(partial_path)
    done_keys = {(r["owner"], r["repo"]) for r in existing_rows}

    newly_processed = 0
    consecutive_transient = 0
    last_status: str | None = None
    last_token_idx: object = None

    for row in input_rows:
        owner, repo = row["name"].split("/", 1)
        if (owner, repo) in done_keys:
            continue
        if newly_processed >= limit:
            break

        result = process_repo(row, pool, since)

        if isinstance(result, TransientFailure):
            consecutive_transient += 1
            response = getattr(result.exc, "response", None)
            last_status = getattr(response, "status_code", None)
            last_token_idx = getattr(result.exc, "token_idx", None)
            if consecutive_transient >= CONSECUTIVE_TRANSIENT_LIMIT:
                raise AbortRun(
                    f"aborting after {consecutive_transient} consecutive transient "
                    f"failures; last status={last_status}, last token_idx={last_token_idx}"
                )
            continue

        consecutive_transient = 0
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
    try:
        summary = run_frame(pool=pool, limit=args.limit)
    except AbortRun as exc:
        print(f"ABORTED: {exc}")
        raise SystemExit(1) from exc

    print(f"Newly processed this run: {summary['newly_processed']}")
    print(f"Total repos recorded so far: {summary['total_recorded']}")
    print(f"Verdict counts: {summary['verdict_counts']}")
    print(f"Wrote {OUTPUT_PATH} and {ATTRITION_PATH}")


if __name__ == "__main__":
    main()
