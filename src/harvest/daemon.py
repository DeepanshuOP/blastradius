"""The rolling harvester daemon — stages 1-3 (T0.3, ROADMAP §8.3).

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

Stage 3 (endpoints 6-7), check-run + annotation capture — the label source
that survives log expiry (§35 T0.3c: "priority: persists >90d"):

  6. GET /repos/{o}/{r}/commits/{sha}/check-runs      (kind 'checkruns', key = sha)
  7. GET /repos/{o}/{r}/check-runs/{id}/annotations   (kind 'annotations', key = check_run_id)

Unlike Stages 1-2, Stage 3 is NOT processed repo-by-repo: SHAs are ordered
oldest-discovered-run-first across the WHOLE invocation (`capture_checkruns()`),
because that ordering — capturing annotations for the runs closest to losing
their logs first — is the entire reason this stage is sequenced before log
capture. `annotations` is paginated with the same MAX_PR_PAGES bound as
Stage 1's PR-scoped kinds; a cap hit marks the unit `failed` and writes
nothing, same all-or-nothing contract. `parent_run_id` is left NULL on every
`annotations` unit — the check-run object carries no documented, resolvable
field back to an Actions workflow run id (see the report this stage shipped
with for the evidence); D-20 reserves the column for exactly this kind, but
inventing a linkage from an undocumented URL shape is worse than leaving it
unset.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.harvest.cursor import CursorStore, DEFAULT_DB_PATH
# Reused, not reinvented (frame.py's terminal/transient split, unmodified —
# CONSECUTIVE_TRANSIENT_LIMIT is public there, so imported rather than
# redefined, per the same D-09 lesson D-19/D-20 keep citing).
from src.harvest.frame import AbortRun, CONSECUTIVE_TRANSIENT_LIMIT, TransientGovernor, _classify_failure
from src.harvest.ratelimit import AllTokensDead, TokenPool, get_with_backoff
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
    except AllTokensDead:
        raise
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
) -> tuple[str, str | None, int | None]:
    """Fetch one capture unit for a PR, following `per_page=100` pagination
    until a short page (FIX for silent truncation on PRs with >100
    commits/files). Returns (status, detail, status_code): status is one of
    the PR_UNIT_* constants; detail is the "{status} {exception_class}"
    string (same convention as the `reason` written to cursor) for FAILED and
    TRANSIENT, else None. status_code is the real HTTP status as an int on a
    fresh terminal/transient failure, else None (success, dedup/skip with no
    fresh request, MAX_PR_PAGES exhaustion with no HTTP failure of its own,
    or an exception that carried no HTTP response).

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
        return PR_UNIT_SKIPPED_ALREADY_DONE, None, None  # already resolved — no request

    cursor.mark_unit_started(repo_full, kind, pr_number)
    url = f"https://api.github.com/repos/{owner}/{repo}/{path_suffix}"

    records: list[RawRecord] = []
    for page in range(1, MAX_PR_PAGES + 1):
        try:
            response = get_with_backoff(
                url, params={"per_page": PULLS_PER_PAGE, "page": page}, pool=pool
            )
        except AllTokensDead:
            raise
        except Exception as exc:
            bucket, status, exception_class = _classify_failure(exc)
            detail = f"{status} {exception_class}"
            status_code = int(status) if status else None
            if bucket == "terminal":
                cursor.mark_unit_failed(repo_full, kind, pr_number, detail)
                return PR_UNIT_FAILED, detail, status_code
            return PR_UNIT_TRANSIENT, detail, status_code  # nothing written — a rerun retries page 1

        page_body = response.json()
        records.append(_record_from_response(response))
        if len(page_body) < PULLS_PER_PAGE:
            break
    else:
        detail = f"exceeded MAX_PR_PAGES={MAX_PR_PAGES} without a short page"
        cursor.mark_unit_failed(repo_full, kind, pr_number, detail)
        return PR_UNIT_FAILED, detail, None

    store.write_records(repo_full, kind, pr_number, records)
    cursor.mark_unit_complete(repo_full, kind, pr_number)
    return PR_UNIT_COMPLETE, None, None


def _capture_pr(
    owner: str,
    repo: str,
    pr_number: int,
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    repo_full: str,
) -> tuple[str, str | None, int | None]:
    """Capture both of a PR's units (independent: one failing must not skip
    the other) and aggregate to a single (status, detail, status_code),
    worst-first: transient > failed > complete > skipped_already_done.
    "complete" beats "skipped_already_done" so a PR with at least one
    freshly-captured unit this run reads as active work, not a no-op."""
    files_status, files_detail, files_status_code = _capture_pr_unit(
        owner, repo, pr_number, "pull_files", f"pulls/{pr_number}/files",
        pool=pool, store=store, cursor=cursor, repo_full=repo_full,
    )
    commits_status, commits_detail, commits_status_code = _capture_pr_unit(
        owner, repo, pr_number, "pull_commits", f"pulls/{pr_number}/commits",
        pool=pool, store=store, cursor=cursor, repo_full=repo_full,
    )

    # Both units can fail transiently; files is captured first, so on a
    # double transient failure its status_code (the first one encountered)
    # is what's reported.
    if files_status == PR_UNIT_TRANSIENT:
        return PR_UNIT_TRANSIENT, files_detail, files_status_code
    if commits_status == PR_UNIT_TRANSIENT:
        return PR_UNIT_TRANSIENT, commits_detail, commits_status_code
    if files_status == PR_UNIT_FAILED:
        return PR_UNIT_FAILED, files_detail, files_status_code
    if commits_status == PR_UNIT_FAILED:
        return PR_UNIT_FAILED, commits_detail, commits_status_code
    if files_status == PR_UNIT_SKIPPED_ALREADY_DONE and commits_status == PR_UNIT_SKIPPED_ALREADY_DONE:
        return PR_UNIT_SKIPPED_ALREADY_DONE, None, None
    return PR_UNIT_COMPLETE, None, None


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


def _collect_repo_shas(
    repo_full: str, store: RawStore, cursor: CursorStore
) -> tuple[set[str], int, int, int]:
    """Derive the repo's distinct head-SHA set from every PR the persisted
    `pulls` pages list, splitting the PRs that contribute no SHAs by *why*:

      - out-of-window: no `pull_commits` capture_unit row at all. This is
        `sweep_repo()`'s own window filter — `_capture_pr()` is only ever
        called for PRs with `updated_at >= cutoff`, so a PR outside that
        window never got `mark_unit_started()` and never will; the row's
        absence isn't a hole, it's the intended "never attempted" state.
      - not-complete: a row exists (in_flight/failed/skipped/expired) — a
        PR the sweep DID attempt but that hasn't (or couldn't) resolve to
        real commit data. This is the genuine incompleteness case; the two
        must stay separate; a PR out of window silently inflating an
        "incomplete units" count was the bug (see report).

    Shared by Stage 2 (discover_repo) and Stage 3 (capture_checkruns) so
    both count PRs the same way."""
    pr_numbers = _iter_captured_pr_numbers(repo_full, store, cursor)
    n_prs_out_of_window = 0
    n_prs_pull_commits_not_complete = 0
    shas: set[str] = set()
    for pr_number in pr_numbers:
        unit = cursor.get_capture_unit(repo_full, "pull_commits", pr_number)
        if unit is None:
            n_prs_out_of_window += 1
            continue
        if unit.status != "complete":
            n_prs_pull_commits_not_complete += 1
            continue
        for commit in _read_paginated_json(store, repo_full, "pull_commits", pr_number):
            shas.add(commit["sha"])
    return shas, len(pr_numbers), n_prs_out_of_window, n_prs_pull_commits_not_complete


def _run_started_at(run: dict) -> str:
    return run.get("run_started_at") or run["created_at"]


def _read_run_ages_for_sha(
    store: RawStore, cursor: CursorStore, repo_full: str, sha: str, now: datetime
) -> list[float]:
    """Ages (days) of every run already discovered for this sha, read back
    from Stage 2's persisted `runs` unit — never re-fetched here (Stage 3
    owns endpoints 6-7 only, not endpoint 4). Empty if the unit doesn't
    exist, isn't `complete`, or genuinely discovered zero runs — Stage 3's
    ordering treats all three the same (see report: no age signal to order
    by, so these sort after every SHA that does have one)."""
    unit = cursor.get_capture_unit(repo_full, "runs", sha)
    if unit is None or unit.status != "complete":
        return []
    records = store.read_records(repo_full, "runs", sha)
    body = json.loads(records[0].body) if records else {}
    workflow_runs = body.get("workflow_runs", [])
    return [
        (now - _parse_github_ts(_run_started_at(run))).total_seconds() / 86400
        for run in workflow_runs
    ]


def _fetch_runs_for_sha(
    owner: str,
    repo: str,
    sha: str,
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    repo_full: str,
) -> tuple[str, list[dict] | None, int | None]:
    """Endpoint 4. Returns (status, workflow_runs, status_code): workflow_runs
    is the list of run dicts when real data is available (freshly fetched, or
    read back from an already-`complete` unit — G4 dedup, zero requests
    either way), else None (failed/transient/skipped/expired with nothing to
    read). status_code is the real HTTP status as an int on a fresh
    terminal/transient failure, else None (success, dedup/skip reads with no
    fresh request, or an exception that carried no HTTP response)."""
    existing = cursor.get_capture_unit(repo_full, "runs", sha)
    if existing is not None and existing.status != "in_flight":
        if existing.status == "complete":
            records = store.read_records(repo_full, "runs", sha)
            body = json.loads(records[0].body) if records else {}
            return PR_UNIT_SKIPPED_ALREADY_DONE, body.get("workflow_runs", []), None
        return PR_UNIT_SKIPPED_ALREADY_DONE, None, None  # already resolved failed/skipped/expired

    cursor.mark_unit_started(repo_full, "runs", sha)
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
    try:
        response = get_with_backoff(url, params={"head_sha": sha, "per_page": 100}, pool=pool)
    except AllTokensDead:
        raise
    except Exception as exc:
        bucket, status, exception_class = _classify_failure(exc)
        detail = f"{status} {exception_class}"
        status_code = int(status) if status else None
        if bucket == "terminal":
            cursor.mark_unit_failed(repo_full, "runs", sha, detail)
            return PR_UNIT_FAILED, None, status_code
        return PR_UNIT_TRANSIENT, None, status_code

    body = response.json()
    store.write_records(repo_full, "runs", sha, [_record_from_response(response)])
    cursor.mark_unit_complete(repo_full, "runs", sha)
    return PR_UNIT_COMPLETE, body.get("workflow_runs", []), None


def _fetch_jobs_for_run(
    owner: str,
    repo: str,
    run_id: int,
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    repo_full: str,
) -> tuple[str, list[dict] | None, int | None]:
    """Endpoint 5. Same (status, jobs, status_code) shape as
    `_fetch_runs_for_sha`."""
    existing = cursor.get_capture_unit(repo_full, "jobs", run_id)
    if existing is not None and existing.status != "in_flight":
        if existing.status == "complete":
            records = store.read_records(repo_full, "jobs", run_id)
            body = json.loads(records[0].body) if records else {}
            return PR_UNIT_SKIPPED_ALREADY_DONE, body.get("jobs", []), None
        return PR_UNIT_SKIPPED_ALREADY_DONE, None, None

    cursor.mark_unit_started(repo_full, "jobs", run_id)
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
    try:
        response = get_with_backoff(url, params={"per_page": 100}, pool=pool)
    except AllTokensDead:
        raise
    except Exception as exc:
        bucket, status, exception_class = _classify_failure(exc)
        detail = f"{status} {exception_class}"
        status_code = int(status) if status else None
        if bucket == "terminal":
            cursor.mark_unit_failed(repo_full, "jobs", run_id, detail)
            return PR_UNIT_FAILED, None, status_code
        return PR_UNIT_TRANSIENT, None, status_code

    body = response.json()
    store.write_records(repo_full, "jobs", run_id, [_record_from_response(response)])
    cursor.mark_unit_complete(repo_full, "jobs", run_id)
    return PR_UNIT_COMPLETE, body.get("jobs", []), None


def discover_repo(
    owner: str,
    repo: str,
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    now: datetime | None = None,
    governor: TransientGovernor | None = None,
) -> dict:
    """Stage 2: run discovery for one repo, per distinct head SHA drawn from
    every PR whose `pull_commits` unit is `complete` (D-20/G4). Mirrors
    sweep_repo()'s AbortRun-after-CONSECUTIVE_TRANSIENT_LIMIT pattern, one
    shared counter across both the 'runs' and 'jobs' fetches.

    Returns a raw stats dict (per-repo); `_summarize_repo_stats()` turns it
    into the RUN_AGES.json shape."""
    repo_full = f"{owner}/{repo}"
    now = now or datetime.now(timezone.utc)
    governor = governor if governor is not None else TransientGovernor(pool)

    shas, n_prs_seen, n_prs_out_of_window, n_prs_pull_commits_not_complete = _collect_repo_shas(
        repo_full, store, cursor
    )

    stats = {
        "n_prs_seen": n_prs_seen,
        "n_prs_out_of_window": n_prs_out_of_window,
        "n_prs_pull_commits_not_complete": n_prs_pull_commits_not_complete,
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

    for sha in sorted(shas):
        status, workflow_runs, status_code = _fetch_runs_for_sha(
            owner, repo, sha, pool=pool, store=store, cursor=cursor, repo_full=repo_full
        )

        if status == PR_UNIT_TRANSIENT:
            stats["n_transient_runs"] += 1
            governor.record_transient(status=status_code, token_idx=None)
            continue
        governor.record_success()

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

            j_status, jobs, j_status_code = _fetch_jobs_for_run(
                owner, repo, run_id, pool=pool, store=store, cursor=cursor, repo_full=repo_full
            )
            if j_status == PR_UNIT_TRANSIENT:
                stats["n_transient_jobs"] += 1
                governor.record_transient(status=j_status_code, token_idx=None)
                continue
            governor.record_success()

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


def _fetch_checkruns_for_sha(
    owner: str,
    repo: str,
    sha: str,
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    repo_full: str,
) -> tuple[str, list[dict] | None, int | None]:
    """Endpoint 6, paginated (wrapped-object body, unlike pull_commits/
    pull_files/annotations) with the same MAX_PR_PAGES bound and
    all-or-nothing write as `_fetch_annotations_for_checkrun`: a cap hit
    marks the unit `failed` and writes nothing, never a partial `complete`
    — a truncated check-run list silently marked complete is the same
    failure class as the 100-commit truncation. Same (status, check_runs,
    status_code) shape as `_fetch_runs_for_sha`."""
    existing = cursor.get_capture_unit(repo_full, "checkruns", sha)
    if existing is not None and existing.status != "in_flight":
        if existing.status == "complete":
            check_runs: list[dict] = []
            for record in store.read_records(repo_full, "checkruns", sha):
                check_runs.extend(json.loads(record.body).get("check_runs", []))
            return PR_UNIT_SKIPPED_ALREADY_DONE, check_runs, None
        return PR_UNIT_SKIPPED_ALREADY_DONE, None, None

    cursor.mark_unit_started(repo_full, "checkruns", sha)
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}/check-runs"

    records: list[RawRecord] = []
    check_runs = []
    for page in range(1, MAX_PR_PAGES + 1):
        try:
            response = get_with_backoff(
                url, params={"per_page": PULLS_PER_PAGE, "page": page}, pool=pool
            )
        except AllTokensDead:
            raise
        except Exception as exc:
            bucket, status, exception_class = _classify_failure(exc)
            detail = f"{status} {exception_class}"
            status_code = int(status) if status else None
            if bucket == "terminal":
                cursor.mark_unit_failed(repo_full, "checkruns", sha, detail)
                return PR_UNIT_FAILED, None, status_code
            return PR_UNIT_TRANSIENT, None, status_code

        page_body = response.json()
        page_check_runs = page_body.get("check_runs", [])
        records.append(_record_from_response(response))
        check_runs.extend(page_check_runs)
        if len(page_check_runs) < PULLS_PER_PAGE:
            break
    else:
        detail = f"exceeded MAX_PR_PAGES={MAX_PR_PAGES} without a short page"
        cursor.mark_unit_failed(repo_full, "checkruns", sha, detail)
        return PR_UNIT_FAILED, None, None

    store.write_records(repo_full, "checkruns", sha, records)
    cursor.mark_unit_complete(repo_full, "checkruns", sha)
    return PR_UNIT_COMPLETE, check_runs, None


def _fetch_annotations_for_checkrun(
    owner: str,
    repo: str,
    check_run_id: int,
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    repo_full: str,
) -> tuple[str, list[dict] | None, int | None]:
    """Endpoint 7, paginated (unwrapped JSON array, like pull_commits/
    pull_files) with the same MAX_PR_PAGES bound and all-or-nothing write:
    a cap hit marks the unit `failed` and writes nothing, never a partial
    `complete` — a truncated annotation set silently marked complete is
    exactly the FIX 1 bug repeated at a different endpoint. Third element is
    the (status, items, status_code) shape shared with `_fetch_runs_for_sha`;
    the MAX_PR_PAGES-exhausted branch carries no HTTP failure of its own, so
    its status_code is None.

    parent_run_id is always NULL here (see report): the check-run object
    carries no documented, resolvable field back to the Actions workflow
    run id, so D-20's parent_run_id column — reserved for job/checkrun-
    scoped kinds precisely so `logs`/`annotations` expiry is attributable
    to a run — is left unset rather than invented from an undocumented URL
    shape."""
    existing = cursor.get_capture_unit(repo_full, "annotations", check_run_id)
    if existing is not None and existing.status != "in_flight":
        if existing.status == "complete":
            items: list[dict] = []
            for record in store.read_records(repo_full, "annotations", check_run_id):
                items.extend(json.loads(record.body))
            return PR_UNIT_SKIPPED_ALREADY_DONE, items, None
        return PR_UNIT_SKIPPED_ALREADY_DONE, None, None

    cursor.mark_unit_started(repo_full, "annotations", check_run_id, parent_run_id=None)
    url = f"https://api.github.com/repos/{owner}/{repo}/check-runs/{check_run_id}/annotations"

    records: list[RawRecord] = []
    items: list[dict] = []
    for page in range(1, MAX_PR_PAGES + 1):
        try:
            response = get_with_backoff(
                url, params={"per_page": PULLS_PER_PAGE, "page": page}, pool=pool
            )
        except AllTokensDead:
            raise
        except Exception as exc:
            bucket, status, exception_class = _classify_failure(exc)
            detail = f"{status} {exception_class}"
            status_code = int(status) if status else None
            if bucket == "terminal":
                cursor.mark_unit_failed(repo_full, "annotations", check_run_id, detail)
                return PR_UNIT_FAILED, None, status_code
            return PR_UNIT_TRANSIENT, None, status_code

        page_body = response.json()
        records.append(_record_from_response(response))
        items.extend(page_body)
        if len(page_body) < PULLS_PER_PAGE:
            break
    else:
        detail = f"exceeded MAX_PR_PAGES={MAX_PR_PAGES} without a short page"
        cursor.mark_unit_failed(repo_full, "annotations", check_run_id, detail)
        return PR_UNIT_FAILED, None, None

    store.write_records(repo_full, "annotations", check_run_id, records)
    cursor.mark_unit_complete(repo_full, "annotations", check_run_id)
    return PR_UNIT_COMPLETE, items, None


def _fetch_job_log(
    owner: str,
    repo: str,
    job_id: int,
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    repo_full: str,
    parent_run_id: int,
) -> tuple[str, int | None, int | None]:
    """Endpoint 9, a SINGLE request — not paginated. The endpoint returns the
    whole log in one response (a 302 from api.github.com to a blob host, which
    `get_with_backoff` already follows with Authorization stripped on the
    redirected leg), so there is no `per_page` and no page loop to copy from
    `_fetch_annotations_for_checkrun`.

    The body is plain text, not JSON, and is never decoded, parsed, or
    ANSI-stripped here — §8.3's principle is capture wide, parse narrow, and
    parsing belongs to T1.1. `_record_from_response` stores `response.content`
    verbatim; rawstore's `_encode_body` falls back to base64 when those bytes
    are not valid UTF-8.

    Middle element is the SIZE IN BYTES of the log fetched THIS invocation,
    not the body — a caller must never be handed a ~1.5 MB payload it does not
    need (a live probe measured one log at 1,497,943 bytes). It is None on
    every path that did not fetch, INCLUDING a successful dedup skip: sizing an
    already-captured log would mean gunzipping it off disk for a number nobody
    uses, and the compressed on-disk size is a different quantity that must not
    travel through the same field. The orchestrator counts dedup skips
    separately.

    parent_run_id is REQUIRED and is populated from the job's own `run_id`
    field, unlike every other helper: `logs` has scope `job`, which
    `_validate_parent_run_id` permits, and D-20 reserved the column precisely
    so this 90-day-expiring kind's expiry is attributable to a run. Per D-23
    it costs nothing, because the job object already carries `run_id`.

    A 404 or 410 means the log has EXPIRED. Both are in `TERMINAL_STATUSES`,
    so `_classify_failure` buckets them terminal and the unit is marked
    `failed` — correct, and deliberately not given a retry or a status of its
    own. The orchestrator distinguishes expiry from the returned status_code.
    """
    existing = cursor.get_capture_unit(repo_full, "logs", job_id)
    if existing is not None and existing.status != "in_flight":
        return PR_UNIT_SKIPPED_ALREADY_DONE, None, None

    cursor.mark_unit_started(repo_full, "logs", job_id, parent_run_id=parent_run_id)
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/jobs/{job_id}/logs"

    try:
        response = get_with_backoff(url, pool=pool)
    except AllTokensDead:
        raise
    except Exception as exc:
        bucket, status, exception_class = _classify_failure(exc)
        detail = f"{status} {exception_class}"
        status_code = int(status) if status else None
        if bucket == "terminal":
            cursor.mark_unit_failed(repo_full, "logs", job_id, detail)
            return PR_UNIT_FAILED, None, status_code
        return PR_UNIT_TRANSIENT, None, status_code

    store.write_records(repo_full, "logs", job_id, [_record_from_response(response)])
    cursor.mark_unit_complete(repo_full, "logs", job_id)
    return PR_UNIT_COMPLETE, len(response.content), None


def capture_checkruns(
    repos: list[tuple[str, str]],
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    now: datetime | None = None,
    governor: TransientGovernor | None = None,
) -> dict:
    """Stage 3: check-run + annotation capture (endpoints 6-7), oldest-
    discovered-run-first across the WHOLE invocation, not repo-by-repo and
    not in discovery order — this ordering is the entire point of the
    stage (see report: expired_90d_rate=0.110, median run age 61d, p90 93d
    — job logs for those runs are already gone; annotations, captured now,
    are not).

    Ordering key: for every distinct head SHA (same derivation as Stage 2,
    `_collect_repo_shas`), the age in days of its OLDEST already-discovered
    run, read back from Stage 2's persisted 'runs' units — never
    re-fetched (Stage 3 owns endpoints 6-7 only). SHAs with no age signal
    (no 'runs' unit, an incomplete one, or one that completed with zero
    runs — all three are indistinguishable from "nothing to prioritise
    by") sort after every SHA that has one, in a deterministic (repo, sha)
    order among themselves — see report for why zero-run and missing-data
    SHAs are treated identically here.

    Mirrors sweep_repo()/discover_repo()'s AbortRun-after-
    CONSECUTIVE_TRANSIENT_LIMIT pattern, one counter shared across both the
    'checkruns' and 'annotations' fetches, but as a single counter across
    the whole ordered sequence (not reset per repo) since the sequence
    itself spans every repo."""
    now = now or datetime.now(timezone.utc)
    governor = governor if governor is not None else TransientGovernor(pool)

    entries: list[tuple[str, str, str, str, list[float]]] = []  # (repo_full, owner, repo, sha, run_ages)
    n_prs_out_of_window_total = 0
    n_prs_pull_commits_not_complete_total = 0
    for owner, repo in repos:
        repo_full = f"{owner}/{repo}"
        shas, _n_seen, n_out, n_not_complete = _collect_repo_shas(repo_full, store, cursor)
        n_prs_out_of_window_total += n_out
        n_prs_pull_commits_not_complete_total += n_not_complete
        for sha in sorted(shas):
            run_ages = _read_run_ages_for_sha(store, cursor, repo_full, sha, now)
            entries.append((repo_full, owner, repo, sha, run_ages))

    # Stable sort: deterministic (repo, sha) tie-break first, then oldest-
    # run-age-first: known ages sort before unknown ones (None), and among
    # known ages, larger age (older run) sorts first.
    entries.sort(key=lambda e: (e[0], e[3]))
    entries.sort(key=lambda e: (0, -max(e[4])) if e[4] else (1, 0.0))

    stats = {
        "n_prs_out_of_window": n_prs_out_of_window_total,
        "n_prs_pull_commits_not_complete": n_prs_pull_commits_not_complete_total,
        "n_shas_total": len(entries),
        "n_checkruns_dedup_skipped": 0,
        "n_checkruns_fetched_fresh": 0,
        "n_checkruns_failed_terminal": 0,
        "n_transient_checkruns": 0,
        "n_checkruns_discovered": 0,
        "n_annotations_dedup_skipped": 0,
        "n_annotations_fetched_fresh": 0,
        "n_annotations_failed_terminal": 0,
        "n_transient_annotations": 0,
        "annotations_per_checkrun_counts": [],
        "n_checkruns_zero_annotations": 0,
        "n_annotations_skipped_zero_count": 0,
        "n_checkruns_seen": 0,
        "n_annotations_skipped_prior_failure": 0,
        "n_checkruns_unaccounted": 0,
        # "runs" here means: every discovered run whose head sha ended up
        # with >=1 captured annotation this (or a prior) invocation. Runs
        # are attributed by head_sha, not by run_id — parent_run_id is
        # NULL (see report), so a run-level join isn't possible; SHAs
        # shared by multiple runs (reruns/matrix legs) count every one of
        # those runs as recovered together.
        "recovered_runs_over_90d": 0,
    }

    for repo_full, owner, repo, sha, run_ages in entries:
        cr_status, check_runs, cr_status_code = _fetch_checkruns_for_sha(
            owner, repo, sha, pool=pool, store=store, cursor=cursor, repo_full=repo_full
        )

        if cr_status == PR_UNIT_TRANSIENT:
            stats["n_transient_checkruns"] += 1
            governor.record_transient(status=cr_status_code, token_idx=None)
            continue
        governor.record_success()

        if cr_status == PR_UNIT_FAILED:
            stats["n_checkruns_failed_terminal"] += 1
            continue
        if check_runs is None:
            continue  # already-terminal non-complete unit from an earlier run — no data
        if cr_status == PR_UNIT_SKIPPED_ALREADY_DONE:
            stats["n_checkruns_dedup_skipped"] += 1
        else:
            stats["n_checkruns_fetched_fresh"] += 1
        stats["n_checkruns_discovered"] += len(check_runs)

        sha_got_annotation = False
        for check_run in check_runs:
            stats["n_checkruns_seen"] += 1
            check_run_id = check_run["id"]

            output = check_run.get("output") or {}
            annotations_count = output.get("annotations_count")
            if annotations_count == 0:
                stats["n_checkruns_zero_annotations"] += 1
                stats["annotations_per_checkrun_counts"].append(0)
                stats["n_annotations_skipped_zero_count"] += 1
                continue

            an_status, annotations, an_status_code = _fetch_annotations_for_checkrun(
                owner, repo, check_run_id, pool=pool, store=store, cursor=cursor, repo_full=repo_full
            )
            if an_status == PR_UNIT_TRANSIENT:
                stats["n_transient_annotations"] += 1
                governor.record_transient(status=an_status_code, token_idx=None)
                continue
            governor.record_success()

            if an_status == PR_UNIT_FAILED:
                stats["n_annotations_failed_terminal"] += 1
                continue
            if annotations is None:
                stats["n_annotations_skipped_prior_failure"] += 1
                continue
            if an_status == PR_UNIT_SKIPPED_ALREADY_DONE:
                stats["n_annotations_dedup_skipped"] += 1
            else:
                stats["n_annotations_fetched_fresh"] += 1

            stats["annotations_per_checkrun_counts"].append(len(annotations))
            if len(annotations) == 0:
                stats["n_checkruns_zero_annotations"] += 1
            else:
                sha_got_annotation = True

        if sha_got_annotation:
            stats["recovered_runs_over_90d"] += sum(1 for a in run_ages if a > LOG_RETENTION_DAYS)

    accounted = (
        stats["n_annotations_skipped_zero_count"]
        + stats["n_transient_annotations"]
        + stats["n_annotations_failed_terminal"]
        + stats["n_annotations_skipped_prior_failure"]
        + stats["n_annotations_dedup_skipped"]
        + stats["n_annotations_fetched_fresh"]
    )
    stats["n_checkruns_unaccounted"] = stats["n_checkruns_seen"] - accounted
    if stats["n_checkruns_unaccounted"] != 0:
        print(
            f"capture_checkruns: conservation check failed — "
            f"n_checkruns_seen={stats['n_checkruns_seen']} accounted={accounted} "
            f"n_checkruns_unaccounted={stats['n_checkruns_unaccounted']}",
            file=sys.stderr,
        )

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
    governor: TransientGovernor | None = None,
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
    governor = governor if governor is not None else TransientGovernor(pool)
    cursor.start_sweep(repo_full)
    rc = cursor.get_repo_cursor(repo_full)
    page = rc.pr_page if rc is not None else 1
    newest_updated_at = (rc.last_pr_updated_at if rc is not None and rc.last_pr_updated_at else "")

    pages_fetched = 0
    n_prs_captured = 0
    n_prs_failed_terminal = 0
    n_transient = 0

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
            status, detail, status_code = _capture_pr(
                owner, repo, pr["number"], pool=pool, store=store, cursor=cursor, repo_full=repo_full
            )

            if status == PR_UNIT_TRANSIENT:
                n_transient += 1
                governor.record_transient(status=status_code, token_idx=None)
                continue

            governor.record_success()
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
        "n_prs_out_of_window": stats["n_prs_out_of_window"],
        "n_prs_pull_commits_not_complete": stats["n_prs_pull_commits_not_complete"],
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


def _load_existing_run_ages(path: Path = RUN_AGES_PATH) -> dict | None:
    """Lets `--stage 3` run standalone (no Stage 2 this invocation) and
    still augment a RUN_AGES.json a prior invocation already wrote,
    instead of clobbering Stage 2's numbers with an empty shell."""
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _empty_run_ages_report() -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "log_retention_days": LOG_RETENTION_DAYS,
        "per_repo": {},
        "overall": {},
    }


def _apply_stage3_to_report(report: dict, stage3_stats: dict) -> dict:
    """Add Stage 3's fields to the `overall` block in place. `runs` in
    `n_runs_over_90d_recovered_via_annotations` means "runs whose head sha
    got >=1 captured annotation" — a sha-level join, not a run-level one,
    because parent_run_id is NULL (see report: the check-run object has no
    resolvable run id)."""
    overall = report.setdefault("overall", {})
    overall["annotations_per_checkrun"] = _dist_mean(stage3_stats["annotations_per_checkrun_counts"])
    overall["n_checkruns_discovered"] = stage3_stats["n_checkruns_discovered"]
    overall["n_checkruns_zero_annotations"] = stage3_stats["n_checkruns_zero_annotations"]
    overall["n_runs_over_90d_recovered_via_annotations"] = stage3_stats["recovered_runs_over_90d"]
    return report


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
    """Run Stage 1 (PR sweep), Stage 2 (run discovery), and/or Stage 3
    (check-run + annotation capture) for each repo in turn, printing a
    one-line summary per repo and a total at the end. Propagates AbortRun
    uncaught (same as frame.py's run_frame); main() handles it.

    Stages 1-2 are per-repo (unchanged: 'both' means 1+2, same as before
    this stage existed). Stage 3 is NOT per-repo — oldest-run-first
    ordering is cross-repo by design (see capture_checkruns()), so it runs
    once over the whole `repos` list after the per-repo loop. Whichever of
    Stage 2 / Stage 3 ran this invocation writes/augments
    data/raw/RUN_AGES.json; Stage 3 running standalone (`--stage 3`, no
    Stage 2 this invocation) augments a prior invocation's file instead of
    clobbering it."""
    repos = _load_repos(repos_path, limit)
    run_stage1 = stage in ("1", "both", "all")
    run_stage2 = stage in ("2", "both", "all")
    run_stage3 = stage in ("3", "all")
    governor = TransientGovernor(pool)

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
        "n_checkruns_discovered": 0,
        "n_annotations_captured": 0,
        "n_transient_stage3": 0,
    }
    stage2_raw: dict[str, dict] = {}

    for owner, repo in repos:
        repo_full = f"{owner}/{repo}"
        total["repos_processed"] += 1
        if run_stage1:
            result = sweep_repo(
                owner, repo, pool=pool, store=store, cursor=cursor, cutoff=cutoff, governor=governor
            )
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

        if run_stage2:
            stats = discover_repo(owner, repo, pool=pool, store=store, cursor=cursor, governor=governor)
            stage2_raw[repo_full] = stats
            print(
                f"[{repo_full}] stage2 shas={stats['n_shas_total']} "
                f"out_of_window={stats['n_prs_out_of_window']} "
                f"pull_commits_not_complete={stats['n_prs_pull_commits_not_complete']} "
                f"runs_discovered={len(stats['run_age_days'])} "
                f"failed_terminal={stats['n_shas_failed_terminal'] + stats['n_jobs_failed_terminal']} "
                f"transient={stats['n_transient_runs'] + stats['n_transient_jobs']}"
            )
            total["n_shas_total"] += stats["n_shas_total"]
            total["n_runs_discovered"] += len(stats["run_age_days"])
            total["n_transient_discovery"] += stats["n_transient_runs"] + stats["n_transient_jobs"]

    stage2_report = None
    if run_stage2 and stage2_raw:
        stage2_report = build_run_ages_report(stage2_raw)

    stage3_stats = None
    if run_stage3:
        stage3_stats = capture_checkruns(repos, pool=pool, store=store, cursor=cursor, governor=governor)
        print(
            f"STAGE3: shas={stage3_stats['n_shas_total']} "
            f"out_of_window={stage3_stats['n_prs_out_of_window']} "
            f"pull_commits_not_complete={stage3_stats['n_prs_pull_commits_not_complete']} "
            f"checkruns_discovered={stage3_stats['n_checkruns_discovered']} "
            f"annotations_per_checkrun(mean/median/p90/max)="
            f"{_dist_mean(stage3_stats['annotations_per_checkrun_counts'])} "
            f"zero_annotation_checkruns={stage3_stats['n_checkruns_zero_annotations']} "
            f"recovered_runs_over_90d={stage3_stats['recovered_runs_over_90d']} "
            f"failed_terminal={stage3_stats['n_checkruns_failed_terminal'] + stage3_stats['n_annotations_failed_terminal']} "
            f"transient={stage3_stats['n_transient_checkruns'] + stage3_stats['n_transient_annotations']}"
        )
        total["n_checkruns_discovered"] += stage3_stats["n_checkruns_discovered"]
        total["n_annotations_captured"] += sum(stage3_stats["annotations_per_checkrun_counts"])
        total["n_transient_stage3"] += (
            stage3_stats["n_transient_checkruns"] + stage3_stats["n_transient_annotations"]
        )

    if stage2_report is not None or stage3_stats is not None:
        if stage2_report is not None:
            report = stage2_report
        else:
            report = _load_existing_run_ages() or _empty_run_ages_report()
        if stage3_stats is not None:
            _apply_stage3_to_report(report, stage3_stats)
        _write_run_ages_json(report)

        overall = report["overall"]
        if "n_runs_discovered" in overall:
            print(
                f"RUN_AGES: n_runs={overall['n_runs_discovered']} "
                f"runs_per_sha(mean/median/p90/max)={overall['runs_per_sha']} "
                f"jobs_per_run(mean/median/p90/max)={overall['jobs_per_run']} "
                f"run_age_days(min/median/p90/max)={overall['run_age_days']} "
                f"expired_90d={overall['n_runs_expired_90d']} "
                f"(rate={overall['expired_90d_rate']}) "
                f"extrapolation_300_repos={overall['extrapolation']}"
            )
        if stage3_stats is not None:
            print(
                f"RUN_AGES: annotations_per_checkrun={overall['annotations_per_checkrun']} "
                f"zero_annotation_checkruns={overall['n_checkruns_zero_annotations']} "
                f"n_runs_over_90d_recovered_via_annotations="
                f"{overall['n_runs_over_90d_recovered_via_annotations']}"
            )

    print(
        f"TOTAL: repos={total['repos_processed']} pages={total['pages_fetched']} "
        f"captured={total['n_prs_captured']} failed_terminal={total['n_prs_failed_terminal']} "
        f"transient={total['n_transient']} window_stops={total['window_stops']} "
        f"shas={total['n_shas_total']} runs_discovered={total['n_runs_discovered']} "
        f"transient_discovery={total['n_transient_discovery']} "
        f"checkruns_discovered={total['n_checkruns_discovered']} "
        f"annotations_captured={total['n_annotations_captured']} "
        f"transient_stage3={total['n_transient_stage3']}"
    )
    return total


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repos", type=Path, default=DEFAULT_REPOS_PATH)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stage", choices=("1", "2", "3", "both", "all"), default=DEFAULT_STAGE)
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
    except AllTokensDead as exc:
        print("ABORTED: dead credentials — every token evicted, check .env", file=sys.stderr)
        raise SystemExit(1) from exc
    finally:
        cursor.close()


if __name__ == "__main__":
    main()
