"""The rolling harvester daemon — stages 1-2 (T0.3, ROADMAP §8.3).

Stage 1 (endpoints 1-3), per repo:

  1. GET /repos/{o}/{r}/pulls?state=all&sort=updated&direction=desc  (kind
     'pulls', key = page number) — paginated, `per_page=100`, followed
     until a page returns fewer than `per_page` items.
  2. GET /repos/{o}/{r}/pulls/{n}/files    (kind 'pull_files',   key = PR #)
  3. GET /repos/{o}/{r}/pulls/{n}/commits  (kind 'pull_commits', key = PR #)

`pull_files`/`pull_commits` are themselves paginated `per_page=100`
following pages until a short page (FIX for the truncation defect Part A's
measurement surfaced: a PR with >100 commits/files silently lost SHAs under
the old single-page fetch). Per D-19, a paginated PR-scoped kind does NOT
get a compound `(pr_number, page)` key — `rawstore.write_records()` already
accepts a list of records for one unit, so all pages of one PR's commits
are buffered in memory and written together as multiple `RawRecord`s under
the same existing `(repo, kind, pr_number)` key, only after the full
sequence completes cleanly. A crash mid-pagination leaves the unit
`in_flight` and a rerun restarts from page 1 of that PR — same atomic-unit
contract every other capture unit already has, just now spanning >1 HTTP
response.

Stage 2 (endpoints 4-5), run discovery per distinct head SHA, over every PR
whose `pull_commits` unit is `complete` (PRs whose commits were never
captured contribute zero SHAs and are counted, never silently treated as
0):

  4. GET /repos/{o}/{r}/actions/runs?head_sha={sha}       (kind 'runs', key = sha)
  5. GET /repos/{o}/{r}/actions/runs/{id}/jobs             (kind 'jobs', key = run_id)

A SHA whose `runs` unit is already terminal (G4 dedup — the same SHA is
reachable from multiple PRs) is skipped with zero requests. Stage 2 derives
its PR list from the already-persisted `pulls` pages (`_iter_captured_pr_numbers`)
rather than a new cursor.py query, so `--stage 2` can run standalone against
state a prior `--stage 1` invocation wrote.

WINDOW: only PRs `updated_at` within the last `WINDOW_DAYS` (90) days are
captured (stage 1 only). The listing is sorted `updated` desc, so once a
page's oldest (last) item falls outside the window, everything on every
later page would too — pagination stops there, same as a naturally short
page. Both are "clean finish" conditions and both call
`cursor.complete_sweep()`.

All HTTP goes through `ratelimit.get_with_backoff()` — the sole entry point
(§34.4 C.1). Every raw response is written through `rawstore.RawStore.
write_records()` — nothing under data/raw is ever opened directly. Every
capture unit is `cursor.mark_unit_started()` before the request and marked
terminal only *after* `write_records()` returns, in that order, so a crash
between the two leaves the unit `in_flight` (never `complete`) and a rerun
re-fetches and overwrites it — exactly cursor.py's documented contract.

Terminal vs. transient HTTP failure is not reinvented here: `_classify_failure`
and `TERMINAL_STATUSES` are imported straight from `frame.py`, unmodified.
A terminal failure (404/410/451) calls `cursor.mark_unit_failed()` with the
status and cause and the sweep/discovery moves on. A transient failure
(anything else, including exhausting all of `get_with_backoff`'s retries)
writes nothing — the unit stays `in_flight` for a future rerun to retry.

Resume: before issuing any request for a unit, its current capture_unit row
is checked. Anything not `in_flight` (i.e. already resolved, in any of
`complete`/`skipped`/`expired`/`failed`) is skipped without a request; a
`pulls` page already `complete` is instead re-read back from rawstore so
pagination can continue without re-fetching it.

Stage 2 also emits `data/raw/RUN_AGES.json` — the run-age distribution and
90-day-expiry count Stage 3 needs to prioritise oldest-run-first before its
job logs disappear (§23.3).
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.harvest.cursor import CursorStore, DEFAULT_DB_PATH
# Reused, not reinvented (frame.py's terminal/transient split, unmodified —
# CONSECUTIVE_TRANSIENT_LIMIT is public there, so imported rather than
# redefined, per the same D-09 lesson D-19/D-20 keep citing).
from src.harvest.frame import CONSECUTIVE_TRANSIENT_LIMIT, _classify_failure
from src.harvest.ratelimit import TokenPool, get_with_backoff
from src.harvest.rawstore import DEFAULT_ROOT, RawRecord, RawStore

DEFAULT_REPOS_PATH = Path("data/frame/frame_v1.csv")
DEFAULT_LIMIT = 2
DEFAULT_STAGE = "both"
RUN_AGES_PATH = Path("data/raw/RUN_AGES.json")

PULLS_PER_PAGE = 100
WINDOW_DAYS = 90

# GitHub caps /pulls/{n}/commits at 250 commits and /pulls/{n}/files at 3000
# files — 10 pages of 100 is well past any legitimate response for either.
# Bounded loops are the house style (§8.2's MAX_ATTEMPTS=6 for retries); a
# misbehaving endpoint that never returns a short page must not spin
# forever burning all three tokens.
MAX_PR_PAGES = 10

# GitHub's retention window for job logs (§8.3, §23.3). A run older than
# this has already lost its logs — Stage 3 needs to know how many before it
# spends requests fetching logs that no longer exist.
LOG_RETENTION_DAYS = 90

# Four terminal-ish outcomes a single capture unit (or a PR's pair of them)
# can land in for one sweep_repo() call. Reused as-is for Stage 2's per-SHA
# and per-run units — same four outcomes, same meaning.
PR_UNIT_COMPLETE = "complete"
PR_UNIT_FAILED = "failed"
PR_UNIT_SKIPPED_ALREADY_DONE = "skipped_already_done"
PR_UNIT_TRANSIENT = "transient"


class AbortRun(RuntimeError):
    """Raised to stop a run outright rather than let it keep producing
    holes. Mirrors frame.py's AbortRun/CONSECUTIVE_TRANSIENT_LIMIT pattern
    at the PR level: five consecutive transient failures in a row means a
    systemic problem (dead credential, network outage), not bad luck."""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _cutoff(now: datetime | None = None) -> datetime:
    return (now or datetime.now(timezone.utc)) - timedelta(days=WINDOW_DAYS)


def _parse_github_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _load_repos(path: Path, limit: int) -> list[tuple[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return [(r["owner"], r["repo"]) for r in rows[:limit]]


def _record_from_response(response) -> RawRecord:
    return RawRecord(
        url=response.url,
        status=response.status_code,
        fetched_at=_now_iso(),
        etag=response.headers.get("ETag"),
        body=response.content,
    )


def _fetch_pulls_page(
    owner: str,
    repo: str,
    page: int,
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    repo_full: str,
) -> list[dict] | None:
    """Return the page body (list of PR dicts), or None if this page could
    not be produced this run (terminal failure, transient failure, or a
    previously-recorded non-complete terminal state with nothing to read
    back)."""
    existing = cursor.get_capture_unit(repo_full, "pulls", page)
    if existing is not None and existing.status != "in_flight":
        if existing.status == "complete":
            records = store.read_records(repo_full, "pulls", page)
            return json.loads(records[0].body) if records else []
        return None

    cursor.mark_unit_started(repo_full, "pulls", page)
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    params = {
        "state": "all",
        "sort": "updated",
        "direction": "desc",
        "per_page": PULLS_PER_PAGE,
        "page": page,
    }
    try:
        response = get_with_backoff(url, params=params, pool=pool)
    except Exception as exc:
        bucket, status, exception_class = _classify_failure(exc)
        if bucket == "terminal":
            cursor.mark_unit_failed(repo_full, "pulls", page, f"{status} {exception_class}")
        return None

    body = response.json()
    store.write_records(repo_full, "pulls", page, [_record_from_response(response)])
    cursor.mark_unit_complete(repo_full, "pulls", page)
    return body


def _capture_pr_unit(
    owner: str,
    repo: str,
    pr_number: int,
    kind: str,
    path_suffix: str,
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    repo_full: str,
) -> tuple[str, str | None]:
    """Fetch one capture unit for a PR, following `per_page=100` pagination
    until a short page (FIX for silent truncation on PRs with >100
    commits/files). Returns (status, detail): status is one of the
    PR_UNIT_* constants; detail is the "{status} {exception_class}" string
    (same convention as the `reason` written to cursor) for FAILED and
    TRANSIENT, else None.

    All pages are buffered in memory and written as one `write_records()`
    call under the single existing (repo, kind, pr_number) key — no compound
    key (D-19): a failure on any page leaves nothing written and the unit
    `in_flight`, so a rerun restarts pagination from page 1, same atomic-unit
    contract every other capture unit already has.

    Bounded at MAX_PR_PAGES: an endpoint that never returns a short page
    marks the unit `failed` (not left `in_flight`, not silently marked
    `complete` on a truncated read) and writes nothing — a recorded failure
    beats invisible data loss."""
    existing = cursor.get_capture_unit(repo_full, kind, pr_number)
    if existing is not None and existing.status != "in_flight":
        return PR_UNIT_SKIPPED_ALREADY_DONE, None  # already resolved — no request

    cursor.mark_unit_started(repo_full, kind, pr_number)
    url = f"https://api.github.com/repos/{owner}/{repo}/{path_suffix}"

    records: list[RawRecord] = []
    for page in range(1, MAX_PR_PAGES + 1):
        try:
            response = get_with_backoff(
                url, params={"per_page": PULLS_PER_PAGE, "page": page}, pool=pool
            )
        except Exception as exc:
            bucket, status, exception_class = _classify_failure(exc)
            detail = f"{status} {exception_class}"
            if bucket == "terminal":
                cursor.mark_unit_failed(repo_full, kind, pr_number, detail)
                return PR_UNIT_FAILED, detail
            return PR_UNIT_TRANSIENT, detail  # nothing written — a rerun retries page 1

        page_body = response.json()
        records.append(_record_from_response(response))
        if len(page_body) < PULLS_PER_PAGE:
            break
    else:
        detail = f"exceeded MAX_PR_PAGES={MAX_PR_PAGES} without a short page"
        cursor.mark_unit_failed(repo_full, kind, pr_number, detail)
        return PR_UNIT_FAILED, detail

    store.write_records(repo_full, kind, pr_number, records)
    cursor.mark_unit_complete(repo_full, kind, pr_number)
    return PR_UNIT_COMPLETE, None


def _capture_pr(
    owner: str,
    repo: str,
    pr_number: int,
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    repo_full: str,
) -> tuple[str, str | None]:
    """Capture both of a PR's units (independent: one failing must not skip
    the other) and aggregate to a single (status, detail), worst-first:
    transient > failed > complete > skipped_already_done. "complete" beats
    "skipped_already_done" so a PR with at least one freshly-captured unit
    this run reads as active work, not a no-op."""
    files_status, files_detail = _capture_pr_unit(
        owner, repo, pr_number, "pull_files", f"pulls/{pr_number}/files",
        pool=pool, store=store, cursor=cursor, repo_full=repo_full,
    )
    commits_status, commits_detail = _capture_pr_unit(
        owner, repo, pr_number, "pull_commits", f"pulls/{pr_number}/commits",
        pool=pool, store=store, cursor=cursor, repo_full=repo_full,
    )

    if files_status == PR_UNIT_TRANSIENT:
        return PR_UNIT_TRANSIENT, files_detail
    if commits_status == PR_UNIT_TRANSIENT:
        return PR_UNIT_TRANSIENT, commits_detail
    if files_status == PR_UNIT_FAILED:
        return PR_UNIT_FAILED, files_detail
    if commits_status == PR_UNIT_FAILED:
        return PR_UNIT_FAILED, commits_detail
    if files_status == PR_UNIT_SKIPPED_ALREADY_DONE and commits_status == PR_UNIT_SKIPPED_ALREADY_DONE:
        return PR_UNIT_SKIPPED_ALREADY_DONE, None
    return PR_UNIT_COMPLETE, None


def _read_paginated_json(store: RawStore, repo_full: str, kind: str, key: int) -> list[dict]:
    """Flatten every page's JSON array back into one list, in page order —
    the read-side counterpart of `_capture_pr_unit`'s multi-record write."""
    items: list[dict] = []
    for record in store.read_records(repo_full, kind, key):
        items.extend(json.loads(record.body))
    return items


def _iter_captured_pr_numbers(repo_full: str, store: RawStore, cursor: CursorStore) -> list[int]:
    """Re-derive the PR numbers already captured for this repo from the
    persisted `pulls` listing pages, using the same short-page boundary
    sweep_repo() itself uses. Lets Stage 2 run standalone against state a
    prior Stage 1 invocation wrote, without a new cursor.py query."""
    pr_numbers: list[int] = []
    page = 1
    while True:
        unit = cursor.get_capture_unit(repo_full, "pulls", page)
        if unit is None or unit.status != "complete":
            break
        records = store.read_records(repo_full, "pulls", page)
        body = json.loads(records[0].body) if records else []
        pr_numbers.extend(pr["number"] for pr in body)
        if len(body) < PULLS_PER_PAGE:
            break
        page += 1
    return pr_numbers


def _run_started_at(run: dict) -> str:
    return run.get("run_started_at") or run["created_at"]


def _fetch_runs_for_sha(
    owner: str,
    repo: str,
    sha: str,
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    repo_full: str,
) -> tuple[str, list[dict] | None]:
    """Endpoint 4. Returns (status, workflow_runs): workflow_runs is the
    list of run dicts when real data is available (freshly fetched, or read
    back from an already-`complete` unit — G4 dedup, zero requests either
    way), else None (failed/transient/skipped/expired with nothing to read)."""
    existing = cursor.get_capture_unit(repo_full, "runs", sha)
    if existing is not None and existing.status != "in_flight":
        if existing.status == "complete":
            records = store.read_records(repo_full, "runs", sha)
            body = json.loads(records[0].body) if records else {}
            return PR_UNIT_SKIPPED_ALREADY_DONE, body.get("workflow_runs", [])
        return PR_UNIT_SKIPPED_ALREADY_DONE, None  # already resolved failed/skipped/expired

    cursor.mark_unit_started(repo_full, "runs", sha)
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
    try:
        response = get_with_backoff(url, params={"head_sha": sha, "per_page": 100}, pool=pool)
    except Exception as exc:
        bucket, status, exception_class = _classify_failure(exc)
        detail = f"{status} {exception_class}"
        if bucket == "terminal":
            cursor.mark_unit_failed(repo_full, "runs", sha, detail)
            return PR_UNIT_FAILED, None
        return PR_UNIT_TRANSIENT, None

    body = response.json()
    store.write_records(repo_full, "runs", sha, [_record_from_response(response)])
    cursor.mark_unit_complete(repo_full, "runs", sha)
    return PR_UNIT_COMPLETE, body.get("workflow_runs", [])


def _fetch_jobs_for_run(
    owner: str,
    repo: str,
    run_id: int,
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    repo_full: str,
) -> tuple[str, list[dict] | None]:
    """Endpoint 5. Same (status, jobs) shape as `_fetch_runs_for_sha`."""
    existing = cursor.get_capture_unit(repo_full, "jobs", run_id)
    if existing is not None and existing.status != "in_flight":
        if existing.status == "complete":
            records = store.read_records(repo_full, "jobs", run_id)
            body = json.loads(records[0].body) if records else {}
            return PR_UNIT_SKIPPED_ALREADY_DONE, body.get("jobs", [])
        return PR_UNIT_SKIPPED_ALREADY_DONE, None

    cursor.mark_unit_started(repo_full, "jobs", run_id)
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
    try:
        response = get_with_backoff(url, params={"per_page": 100}, pool=pool)
    except Exception as exc:
        bucket, status, exception_class = _classify_failure(exc)
        detail = f"{status} {exception_class}"
        if bucket == "terminal":
            cursor.mark_unit_failed(repo_full, "jobs", run_id, detail)
            return PR_UNIT_FAILED, None
        return PR_UNIT_TRANSIENT, None

    body = response.json()
    store.write_records(repo_full, "jobs", run_id, [_record_from_response(response)])
    cursor.mark_unit_complete(repo_full, "jobs", run_id)
    return PR_UNIT_COMPLETE, body.get("jobs", [])


def discover_repo(
    owner: str,
    repo: str,
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    now: datetime | None = None,
) -> dict:
    """Stage 2: run discovery for one repo, per distinct head SHA drawn from
    every PR whose `pull_commits` unit is `complete` (D-20/G4). Mirrors
    sweep_repo()'s AbortRun-after-CONSECUTIVE_TRANSIENT_LIMIT pattern, one
    shared counter across both the 'runs' and 'jobs' fetches.

    Returns a raw stats dict (per-repo); `_summarize_repo_stats()` turns it
    into the RUN_AGES.json shape."""
    repo_full = f"{owner}/{repo}"
    now = now or datetime.now(timezone.utc)

    pr_numbers = _iter_captured_pr_numbers(repo_full, store, cursor)
    n_prs_skipped_commits_not_complete = 0
    shas: set[str] = set()
    for pr_number in pr_numbers:
        unit = cursor.get_capture_unit(repo_full, "pull_commits", pr_number)
        if unit is None or unit.status != "complete":
            n_prs_skipped_commits_not_complete += 1
            continue
        for commit in _read_paginated_json(store, repo_full, "pull_commits", pr_number):
            shas.add(commit["sha"])

    stats = {
        "n_prs_seen": len(pr_numbers),
        "n_prs_skipped_commits_not_complete": n_prs_skipped_commits_not_complete,
        "n_shas_total": len(shas),
        "n_shas_dedup_skipped": 0,
        "n_shas_fetched_fresh": 0,
        "n_shas_failed_terminal": 0,
        "n_transient_runs": 0,
        "n_jobs_dedup_skipped": 0,
        "n_jobs_fetched_fresh": 0,
        "n_jobs_failed_terminal": 0,
        "n_transient_jobs": 0,
        "runs_per_sha_counts": [],
        "jobs_per_run_counts": [],
        "run_age_days": [],
    }

    consecutive_transient = 0
    for sha in sorted(shas):
        status, workflow_runs = _fetch_runs_for_sha(
            owner, repo, sha, pool=pool, store=store, cursor=cursor, repo_full=repo_full
        )

        if status == PR_UNIT_TRANSIENT:
            stats["n_transient_runs"] += 1
            consecutive_transient += 1
            if consecutive_transient >= CONSECUTIVE_TRANSIENT_LIMIT:
                raise AbortRun(
                    f"aborting after {consecutive_transient} consecutive transient "
                    f"discovery failures in {repo_full}"
                )
            continue
        consecutive_transient = 0

        if status == PR_UNIT_FAILED:
            stats["n_shas_failed_terminal"] += 1
            continue
        if workflow_runs is None:
            continue  # already-terminal non-complete unit from an earlier run — no data
        if status == PR_UNIT_SKIPPED_ALREADY_DONE:
            stats["n_shas_dedup_skipped"] += 1
        else:
            stats["n_shas_fetched_fresh"] += 1

        stats["runs_per_sha_counts"].append(len(workflow_runs))

        for run in workflow_runs:
            run_id = run["id"]
            age_days = (now - _parse_github_ts(_run_started_at(run))).total_seconds() / 86400
            stats["run_age_days"].append(age_days)

            j_status, jobs = _fetch_jobs_for_run(
                owner, repo, run_id, pool=pool, store=store, cursor=cursor, repo_full=repo_full
            )
            if j_status == PR_UNIT_TRANSIENT:
                stats["n_transient_jobs"] += 1
                consecutive_transient += 1
                if consecutive_transient >= CONSECUTIVE_TRANSIENT_LIMIT:
                    raise AbortRun(
                        f"aborting after {consecutive_transient} consecutive transient "
                        f"discovery failures in {repo_full}"
                    )
                continue
            consecutive_transient = 0

            if j_status == PR_UNIT_FAILED:
                stats["n_jobs_failed_terminal"] += 1
                continue
            if jobs is None:
                continue
            if j_status == PR_UNIT_SKIPPED_ALREADY_DONE:
                stats["n_jobs_dedup_skipped"] += 1
            else:
                stats["n_jobs_fetched_fresh"] += 1
            stats["jobs_per_run_counts"].append(len(jobs))

    return stats


def _summary(pages_fetched, window_stopped, n_prs_captured, n_prs_failed_terminal, n_transient) -> dict:
    return {
        "pages_fetched": pages_fetched,
        "window_stopped": window_stopped,
        "n_prs_captured": n_prs_captured,
        "n_prs_failed_terminal": n_prs_failed_terminal,
        "n_transient": n_transient,
    }


def sweep_repo(
    owner: str,
    repo: str,
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    cutoff: datetime,
) -> dict:
    """Run (or resume) the PR sweep for one repo. `complete_sweep()` is
    called only when the sweep reaches a clean stopping point (a short page
    or the 90-day window) AND zero PRs failed transiently — a transient
    hole inside an otherwise-finished repo must never read as fully swept
    (that was the bug: leave sweep_status='in_progress' so a rerun resumes
    it, same as an in_flight unit would). Raises AbortRun after
    CONSECUTIVE_TRANSIENT_LIMIT consecutive transient PR failures, mirroring
    frame.py's repo-level abort at the PR level."""
    repo_full = f"{owner}/{repo}"
    cursor.start_sweep(repo_full)
    rc = cursor.get_repo_cursor(repo_full)
    page = rc.pr_page if rc is not None else 1
    newest_updated_at = (rc.last_pr_updated_at if rc is not None and rc.last_pr_updated_at else "")

    pages_fetched = 0
    n_prs_captured = 0
    n_prs_failed_terminal = 0
    n_transient = 0
    consecutive_transient = 0

    while True:
        page_body = _fetch_pulls_page(
            owner, repo, page, pool=pool, store=store, cursor=cursor, repo_full=repo_full
        )
        if page_body is None:
            # Terminal or transient failure on the listing itself, or a
            # previously-recorded non-complete unit with nothing to read
            # back: nothing more can be done for this repo this run.
            return _summary(pages_fetched, False, n_prs_captured, n_prs_failed_terminal, n_transient)

        pages_fetched += 1
        if page == 1 and page_body and not newest_updated_at:
            newest_updated_at = page_body[0]["updated_at"]

        in_window = [pr for pr in page_body if _parse_github_ts(pr["updated_at"]) >= cutoff]
        for pr in in_window:
            status, detail = _capture_pr(
                owner, repo, pr["number"], pool=pool, store=store, cursor=cursor, repo_full=repo_full
            )

            if status == PR_UNIT_TRANSIENT:
                n_transient += 1
                consecutive_transient += 1
                if consecutive_transient >= CONSECUTIVE_TRANSIENT_LIMIT:
                    raise AbortRun(
                        f"aborting after {consecutive_transient} consecutive transient "
                        f"PR failures in {repo_full}; last status={detail}"
                    )
                continue

            consecutive_transient = 0
            if status == PR_UNIT_FAILED:
                n_prs_failed_terminal += 1
            else:  # complete or skipped_already_done
                n_prs_captured += 1

        page_short = len(page_body) < PULLS_PER_PAGE
        window_exhausted = bool(page_body) and _parse_github_ts(page_body[-1]["updated_at"]) < cutoff

        if page_short or window_exhausted:
            window_stopped = window_exhausted and not page_short
            if n_transient == 0:
                cursor.complete_sweep(repo_full, newest_updated_at)
            return _summary(pages_fetched, window_stopped, n_prs_captured, n_prs_failed_terminal, n_transient)

        page += 1
        cursor.advance_page(repo_full, page)


def dry_run_estimate(repos_path: Path, limit: int) -> int:
    """A request-count floor, not a full estimate: one pulls-listing page
    per repo is guaranteed; the true total also depends on further pulls
    pages plus 2 requests per in-window PR, neither knowable without
    actually querying — which --dry-run exists specifically to avoid."""
    return len(_load_repos(repos_path, limit))


def _p90(sorted_values: list[float]) -> float:
    idx = min(len(sorted_values) - 1, round(0.9 * (len(sorted_values) - 1)))
    return sorted_values[idx]


def _dist_mean(values: list[float]) -> dict:
    if not values:
        return {"mean": None, "median": None, "p90": None, "max": None}
    s = sorted(values)
    return {
        "mean": statistics.mean(s),
        "median": statistics.median(s),
        "p90": _p90(s),
        "max": s[-1],
    }


def _dist_min(values: list[float]) -> dict:
    if not values:
        return {"min": None, "median": None, "p90": None, "max": None}
    s = sorted(values)
    return {
        "min": s[0],
        "median": statistics.median(s),
        "p90": _p90(s),
        "max": s[-1],
    }


def _summarize_repo_stats(stats: dict) -> dict:
    """Turn discover_repo()'s raw counters/lists into RUN_AGES.json's
    per-repo shape: distributions computed, raw lists dropped."""
    run_ages = stats["run_age_days"]
    n_expired = sum(1 for a in run_ages if a > LOG_RETENTION_DAYS)
    return {
        "n_prs_seen": stats["n_prs_seen"],
        "n_prs_skipped_commits_not_complete": stats["n_prs_skipped_commits_not_complete"],
        "n_shas_total": stats["n_shas_total"],
        "n_shas_dedup_skipped": stats["n_shas_dedup_skipped"],
        "n_shas_fetched_fresh": stats["n_shas_fetched_fresh"],
        "n_shas_failed_terminal": stats["n_shas_failed_terminal"],
        "n_transient_runs": stats["n_transient_runs"],
        "n_runs_discovered": len(run_ages),
        "runs_per_sha": _dist_mean(stats["runs_per_sha_counts"]),
        "n_jobs_dedup_skipped": stats["n_jobs_dedup_skipped"],
        "n_jobs_fetched_fresh": stats["n_jobs_fetched_fresh"],
        "n_jobs_failed_terminal": stats["n_jobs_failed_terminal"],
        "n_transient_jobs": stats["n_transient_jobs"],
        "jobs_per_run": _dist_mean(stats["jobs_per_run_counts"]),
        "run_age_days": _dist_min(run_ages),
        "n_runs_expired_90d": n_expired,
        "expired_90d_rate": (n_expired / len(run_ages)) if run_ages else None,
    }


def build_run_ages_report(per_repo_raw: dict[str, dict], *, n_target_repos: int = 300) -> dict:
    """Pool every repo's raw stats into the overall block and extrapolate to
    `n_target_repos`. `per_repo_raw` is {repo_full: discover_repo() stats}."""
    now = datetime.now(timezone.utc).isoformat()
    per_repo = {repo: _summarize_repo_stats(s) for repo, s in per_repo_raw.items()}

    all_runs_per_sha: list[float] = []
    all_jobs_per_run: list[float] = []
    all_run_ages: list[float] = []
    n_distinct_shas_total = 0
    n_repos = len(per_repo_raw)
    for s in per_repo_raw.values():
        all_runs_per_sha.extend(s["runs_per_sha_counts"])
        all_jobs_per_run.extend(s["jobs_per_run_counts"])
        all_run_ages.extend(s["run_age_days"])
        n_distinct_shas_total += s["n_shas_total"]

    n_expired = sum(1 for a in all_run_ages if a > LOG_RETENTION_DAYS)
    overall = {
        "n_repos": n_repos,
        "n_shas_total": n_distinct_shas_total,
        "n_runs_discovered": len(all_run_ages),
        "runs_per_sha": _dist_mean(all_runs_per_sha),
        "jobs_per_run": _dist_mean(all_jobs_per_run),
        "run_age_days": _dist_min(all_run_ages),
        "n_runs_expired_90d": n_expired,
        "expired_90d_rate": (n_expired / len(all_run_ages)) if all_run_ages else None,
    }

    avg_shas_per_repo = (n_distinct_shas_total / n_repos) if n_repos else 0.0
    avg_runs_per_sha = statistics.mean(all_runs_per_sha) if all_runs_per_sha else 0.0
    est_runs_requests = avg_shas_per_repo * n_target_repos
    est_jobs_requests = est_runs_requests * avg_runs_per_sha
    est_total_requests = est_runs_requests + est_jobs_requests
    overall["extrapolation"] = {
        "n_target_repos": n_target_repos,
        "distinct_shas_per_repo_avg": avg_shas_per_repo,
        "estimated_runs_requests": est_runs_requests,
        "estimated_jobs_requests": est_jobs_requests,
        "estimated_total_requests": est_total_requests,
        "estimated_hours_at_15000_per_hr": est_total_requests / 15000,
    }

    return {
        "generated_at": now,
        "log_retention_days": LOG_RETENTION_DAYS,
        "per_repo": per_repo,
        "overall": overall,
    }


def _write_run_ages_json(report: dict, path: Path = RUN_AGES_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def run(
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    repos_path: Path,
    limit: int,
    cutoff: datetime,
    stage: str = DEFAULT_STAGE,
) -> dict:
    """Run Stage 1 (PR sweep) and/or Stage 2 (run discovery) for each repo
    in turn, printing a one-line summary per repo and a total at the end.
    Propagates AbortRun uncaught (same as frame.py's run_frame); main()
    handles it. Stage 2, if run, writes data/raw/RUN_AGES.json once at the
    end over every repo processed this invocation."""
    repos = _load_repos(repos_path, limit)
    total = {
        "repos_processed": 0,
        "pages_fetched": 0,
        "window_stops": 0,
        "n_prs_captured": 0,
        "n_prs_failed_terminal": 0,
        "n_transient": 0,
        "n_shas_total": 0,
        "n_runs_discovered": 0,
        "n_transient_discovery": 0,
    }
    stage2_raw: dict[str, dict] = {}

    for owner, repo in repos:
        repo_full = f"{owner}/{repo}"
        total["repos_processed"] += 1
        if stage in ("1", "both"):
            result = sweep_repo(owner, repo, pool=pool, store=store, cursor=cursor, cutoff=cutoff)
            print(
                f"[{repo_full}] stage1 pages={result['pages_fetched']} "
                f"captured={result['n_prs_captured']} "
                f"failed_terminal={result['n_prs_failed_terminal']} "
                f"transient={result['n_transient']} "
                f"window_stopped={result['window_stopped']}"
            )
            total["pages_fetched"] += result["pages_fetched"]
            total["window_stops"] += 1 if result["window_stopped"] else 0
            total["n_prs_captured"] += result["n_prs_captured"]
            total["n_prs_failed_terminal"] += result["n_prs_failed_terminal"]
            total["n_transient"] += result["n_transient"]

        if stage in ("2", "both"):
            stats = discover_repo(owner, repo, pool=pool, store=store, cursor=cursor)
            stage2_raw[repo_full] = stats
            print(
                f"[{repo_full}] stage2 shas={stats['n_shas_total']} "
                f"prs_skipped_commits_not_complete={stats['n_prs_skipped_commits_not_complete']} "
                f"runs_discovered={len(stats['run_age_days'])} "
                f"failed_terminal={stats['n_shas_failed_terminal'] + stats['n_jobs_failed_terminal']} "
                f"transient={stats['n_transient_runs'] + stats['n_transient_jobs']}"
            )
            total["n_shas_total"] += stats["n_shas_total"]
            total["n_runs_discovered"] += len(stats["run_age_days"])
            total["n_transient_discovery"] += stats["n_transient_runs"] + stats["n_transient_jobs"]

    if stage in ("2", "both") and stage2_raw:
        report = build_run_ages_report(stage2_raw)
        _write_run_ages_json(report)
        overall = report["overall"]
        print(
            f"RUN_AGES: n_runs={overall['n_runs_discovered']} "
            f"runs_per_sha(mean/median/p90/max)={overall['runs_per_sha']} "
            f"jobs_per_run(mean/median/p90/max)={overall['jobs_per_run']} "
            f"run_age_days(min/median/p90/max)={overall['run_age_days']} "
            f"expired_90d={overall['n_runs_expired_90d']} "
            f"(rate={overall['expired_90d_rate']}) "
            f"extrapolation_300_repos={overall['extrapolation']}"
        )

    print(
        f"TOTAL: repos={total['repos_processed']} pages={total['pages_fetched']} "
        f"captured={total['n_prs_captured']} failed_terminal={total['n_prs_failed_terminal']} "
        f"transient={total['n_transient']} window_stops={total['window_stops']} "
        f"shas={total['n_shas_total']} runs_discovered={total['n_runs_discovered']} "
        f"transient_discovery={total['n_transient_discovery']}"
    )
    return total


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repos", type=Path, default=DEFAULT_REPOS_PATH)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stage", choices=("1", "2", "both"), default=DEFAULT_STAGE)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    if args.dry_run:
        estimate = dry_run_estimate(args.repos, args.limit)
        print(
            f"[dry-run] {estimate} repo(s) selected from {args.repos} (--limit {args.limit}); "
            f"at least {estimate} request(s) required (1 pulls-listing page per repo, minimum). "
            "Actual total also includes further pulls pages plus 2 requests per in-window PR — "
            "unknown without querying, which --dry-run does not do."
        )
        return

    pool = TokenPool.from_env()
    store = RawStore(DEFAULT_ROOT)
    cursor = CursorStore(DEFAULT_DB_PATH)
    try:
        run(
            pool=pool,
            store=store,
            cursor=cursor,
            repos_path=args.repos,
            limit=args.limit,
            cutoff=_cutoff(),
            stage=args.stage,
        )
    except AbortRun as exc:
        print(f"ABORTED: {exc}")
        raise SystemExit(1) from exc
    finally:
        cursor.close()


if __name__ == "__main__":
    main()
