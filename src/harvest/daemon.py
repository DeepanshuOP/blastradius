"""The rolling harvester daemon — stage 1: the PR sweep (T0.3, ROADMAP §8.3).

Captures exactly the first three of §8.3's nine endpoints, in order, per
repo:

  1. GET /repos/{o}/{r}/pulls?state=all&sort=updated&direction=desc  (kind
     'pulls', key = page number) — paginated, `per_page=100`, followed
     until a page returns fewer than `per_page` items.
  2. GET /repos/{o}/{r}/pulls/{n}/files    (kind 'pull_files',   key = PR #)
  3. GET /repos/{o}/{r}/pulls/{n}/commits  (kind 'pull_commits', key = PR #)

Run discovery (endpoint 4 onward), logs, and artifacts are explicitly out
of scope for this stage — see ROADMAP §8.3 subtasks 2+.

WINDOW: only PRs `updated_at` within the last `WINDOW_DAYS` (90) days are
captured. The listing is sorted `updated` desc, so once a page's oldest
(last) item falls outside the window, everything on every later page would
too — pagination stops there, same as a naturally short page. Both are
"clean finish" conditions and both call `cursor.complete_sweep()`.

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
status and cause and the sweep moves on. A transient failure (anything
else, including exhausting all of `get_with_backoff`'s retries) writes
nothing — the unit stays `in_flight` for a future rerun to retry.

Resume: before issuing any request for a unit, its current capture_unit row
is checked. Anything not `in_flight` (i.e. already resolved, in any of
`complete`/`skipped`/`expired`/`failed`) is skipped without a request; a
`pulls` page already `complete` is instead re-read back from rawstore so
pagination can continue without re-fetching it.
"""

from __future__ import annotations

import argparse
import csv
import json
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

PULLS_PER_PAGE = 100
WINDOW_DAYS = 90

# Four terminal-ish outcomes a single capture unit (or a PR's pair of them)
# can land in for one sweep_repo() call.
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
    """Fetch one capture unit for a PR. Returns (status, detail): status is
    one of the PR_UNIT_* constants; detail is the "{status} {exception_class}"
    string (same convention as the `reason` written to cursor) for FAILED
    and TRANSIENT, else None."""
    existing = cursor.get_capture_unit(repo_full, kind, pr_number)
    if existing is not None and existing.status != "in_flight":
        return PR_UNIT_SKIPPED_ALREADY_DONE, None  # already resolved — no request

    cursor.mark_unit_started(repo_full, kind, pr_number)
    url = f"https://api.github.com/repos/{owner}/{repo}/{path_suffix}"
    try:
        response = get_with_backoff(url, params={"per_page": 100}, pool=pool)
    except Exception as exc:
        bucket, status, exception_class = _classify_failure(exc)
        detail = f"{status} {exception_class}"
        if bucket == "terminal":
            cursor.mark_unit_failed(repo_full, kind, pr_number, detail)
            return PR_UNIT_FAILED, detail
        return PR_UNIT_TRANSIENT, detail  # left in_flight — a rerun retries it

    store.write_records(repo_full, kind, pr_number, [_record_from_response(response)])
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


def run(
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    repos_path: Path,
    limit: int,
    cutoff: datetime,
) -> dict:
    """Sweep each repo in turn, printing a one-line summary per repo and a
    total at the end — a sweep that captured nothing must be visibly
    different in this output from one that captured everything. Propagates
    AbortRun uncaught (same as frame.py's run_frame); main() handles it."""
    repos = _load_repos(repos_path, limit)
    total = {
        "repos_processed": 0,
        "pages_fetched": 0,
        "window_stops": 0,
        "n_prs_captured": 0,
        "n_prs_failed_terminal": 0,
        "n_transient": 0,
    }
    for owner, repo in repos:
        result = sweep_repo(owner, repo, pool=pool, store=store, cursor=cursor, cutoff=cutoff)
        print(
            f"[{owner}/{repo}] pages={result['pages_fetched']} "
            f"captured={result['n_prs_captured']} "
            f"failed_terminal={result['n_prs_failed_terminal']} "
            f"transient={result['n_transient']} "
            f"window_stopped={result['window_stopped']}"
        )
        total["repos_processed"] += 1
        total["pages_fetched"] += result["pages_fetched"]
        total["window_stops"] += 1 if result["window_stopped"] else 0
        total["n_prs_captured"] += result["n_prs_captured"]
        total["n_prs_failed_terminal"] += result["n_prs_failed_terminal"]
        total["n_transient"] += result["n_transient"]

    print(
        f"TOTAL: repos={total['repos_processed']} pages={total['pages_fetched']} "
        f"captured={total['n_prs_captured']} failed_terminal={total['n_prs_failed_terminal']} "
        f"transient={total['n_transient']} window_stops={total['window_stops']}"
    )
    return total


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repos", type=Path, default=DEFAULT_REPOS_PATH)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--dry-run", action="store_true")
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
        )
    except AbortRun as exc:
        print(f"ABORTED: {exc}")
        raise SystemExit(1) from exc
    finally:
        cursor.close()


if __name__ == "__main__":
    main()
