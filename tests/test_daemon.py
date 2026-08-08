"""Tests for src.harvest.daemon — the T0.3 PR-sweep stage (endpoints 1-3).

No network: all GitHub calls go through get_with_backoff and are intercepted
with `responses` at the transport layer, same convention as test_frame.py.
No mocks of our own modules — real RawStore/CursorStore against tmp_path.
"""

import csv
from datetime import datetime, timedelta, timezone

import pytest
import responses
from responses import matchers

from src.harvest import daemon
from src.harvest.cursor import CursorStore
from src.harvest.rawstore import RawStore
from src.harvest.ratelimit import TokenPool

RECENT = "2026-08-01T00:00:00Z"
OLD = "2026-04-01T00:00:00Z"  # well over 90 days before "now" below
NOW = datetime(2026, 8, 7, tzinfo=timezone.utc)


def _pool():
    return TokenPool(["tok_a"])


def _cutoff():
    return NOW - timedelta(days=daemon.WINDOW_DAYS)


def _pulls_url(owner, repo):
    return f"https://api.github.com/repos/{owner}/{repo}/pulls"


def _files_url(owner, repo, n):
    return f"https://api.github.com/repos/{owner}/{repo}/pulls/{n}/files"


def _commits_url(owner, repo, n):
    return f"https://api.github.com/repos/{owner}/{repo}/pulls/{n}/commits"


def _pr(number, updated_at):
    return {"number": number, "updated_at": updated_at}


def _mock_pulls_page(owner, repo, page, body):
    responses.add(
        responses.GET,
        _pulls_url(owner, repo),
        json=body,
        status=200,
        match=[
            matchers.query_param_matcher(
                {
                    "state": "all",
                    "sort": "updated",
                    "direction": "desc",
                    "per_page": "100",
                    "page": str(page),
                }
            )
        ],
    )


def _seed_pr_already_captured(cursor, repo, number):
    for kind in ("pull_files", "pull_commits"):
        cursor.mark_unit_started(repo, kind, number)
        cursor.mark_unit_complete(repo, kind, number)


@responses.activate
def test_two_page_sweep_records_two_pulls_units_and_stops_at_short_page(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    page1 = [_pr(i, RECENT) for i in range(1, 101)]
    page2 = [_pr(101, RECENT)]
    for pr in page1 + page2:
        _seed_pr_already_captured(cursor, "owner/repo", pr["number"])

    _mock_pulls_page("owner", "repo", 1, page1)
    _mock_pulls_page("owner", "repo", 2, page2)

    daemon.sweep_repo("owner", "repo", pool=pool, store=store, cursor=cursor, cutoff=_cutoff())

    assert cursor.get_capture_unit("owner/repo", "pulls", 1).status == "complete"
    assert cursor.get_capture_unit("owner/repo", "pulls", 2).status == "complete"
    assert cursor.get_capture_unit("owner/repo", "pulls", 3) is None
    assert cursor.get_repo_cursor("owner/repo").sweep_status == "idle"

    cursor.close()


@responses.activate
def test_each_pr_produces_one_pull_files_and_one_pull_commits_unit(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    page1 = [_pr(1, RECENT), _pr(2, RECENT)]
    _mock_pulls_page("owner", "repo", 1, page1)
    for n in (1, 2):
        responses.add(responses.GET, _files_url("owner", "repo", n), json=[{"filename": f"f{n}.py"}], status=200)
        responses.add(responses.GET, _commits_url("owner", "repo", n), json=[{"sha": f"s{n}"}], status=200)

    daemon.sweep_repo("owner", "repo", pool=pool, store=store, cursor=cursor, cutoff=_cutoff())

    for n in (1, 2):
        files_unit = cursor.get_capture_unit("owner/repo", "pull_files", n)
        commits_unit = cursor.get_capture_unit("owner/repo", "pull_commits", n)
        assert files_unit.status == "complete"
        assert commits_unit.status == "complete"
        assert store.read_records("owner/repo", "pull_files", n)[0].body == f'[{{"filename": "f{n}.py"}}]'.encode()
        assert store.read_records("owner/repo", "pull_commits", n)[0].body == f'[{{"sha": "s{n}"}}]'.encode()

    cursor.close()


@responses.activate
def test_rerunning_after_complete_sweep_issues_zero_requests(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    page1 = [_pr(1, RECENT)]
    _mock_pulls_page("owner", "repo", 1, page1)
    responses.add(responses.GET, _files_url("owner", "repo", 1), json=[], status=200)
    responses.add(responses.GET, _commits_url("owner", "repo", 1), json=[], status=200)

    daemon.sweep_repo("owner", "repo", pool=pool, store=store, cursor=cursor, cutoff=_cutoff())
    n_calls_after_first_run = len(responses.calls)

    # No new mocks registered: any further HTTP attempt raises inside `responses`.
    daemon.sweep_repo("owner", "repo", pool=pool, store=store, cursor=cursor, cutoff=_cutoff())

    assert len(responses.calls) == n_calls_after_first_run

    cursor.close()


@responses.activate
def test_in_flight_unit_is_refetched_on_rerun_and_file_overwritten(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    # Simulate a crash: a stale write already on disk, and the unit left
    # in_flight (mark_unit_started called, mark_unit_complete never was).
    from src.harvest.rawstore import RawRecord

    store.write_records(
        "owner/repo", "pulls", 1,
        [RawRecord(url="stale", status=200, fetched_at="2020-01-01T00:00:00+00:00", etag=None, body=b'[{"stale": true}]')],
    )
    cursor.mark_unit_started("owner/repo", "pulls", 1)

    page1 = [_pr(1, RECENT)]  # short page -> clean finish
    _mock_pulls_page("owner", "repo", 1, page1)
    responses.add(responses.GET, _files_url("owner", "repo", 1), json=[], status=200)
    responses.add(responses.GET, _commits_url("owner", "repo", 1), json=[], status=200)

    daemon.sweep_repo("owner", "repo", pool=pool, store=store, cursor=cursor, cutoff=_cutoff())

    unit = cursor.get_capture_unit("owner/repo", "pulls", 1)
    assert unit.status == "complete"
    body = store.read_records("owner/repo", "pulls", 1)[0].body
    assert body != b'[{"stale": true}]'
    assert b"stale" not in body

    cursor.close()


@responses.activate
def test_404_on_pull_files_marks_failed_and_sweep_continues_to_next_pr(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    page1 = [_pr(1, RECENT), _pr(2, RECENT)]
    _mock_pulls_page("owner", "repo", 1, page1)
    responses.add(responses.GET, _files_url("owner", "repo", 1), status=404)
    responses.add(responses.GET, _commits_url("owner", "repo", 1), json=[], status=200)
    responses.add(responses.GET, _files_url("owner", "repo", 2), json=[], status=200)
    responses.add(responses.GET, _commits_url("owner", "repo", 2), json=[], status=200)

    daemon.sweep_repo("owner", "repo", pool=pool, store=store, cursor=cursor, cutoff=_cutoff())

    pr1_files = cursor.get_capture_unit("owner/repo", "pull_files", 1)
    pr1_commits = cursor.get_capture_unit("owner/repo", "pull_commits", 1)
    pr2_files = cursor.get_capture_unit("owner/repo", "pull_files", 2)
    pr2_commits = cursor.get_capture_unit("owner/repo", "pull_commits", 2)

    assert pr1_files.status == "failed"
    assert "404" in pr1_files.reason
    assert pr1_commits.status == "complete"
    assert pr2_files.status == "complete"
    assert pr2_commits.status == "complete"

    # A terminal failure is a recorded outcome, not a hole: the sweep still
    # completes cleanly (no transient failures occurred).
    assert cursor.get_repo_cursor("owner/repo").sweep_status == "idle"

    cursor.close()


@responses.activate
def test_transient_pr_failure_blocks_complete_sweep_until_resolved(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    page1 = [_pr(1, RECENT)]
    _mock_pulls_page("owner", "repo", 1, page1)
    for _ in range(6):  # MAX_ATTEMPTS in ratelimit.py
        responses.add(responses.GET, _files_url("owner", "repo", 1), status=503)
    responses.add(responses.GET, _commits_url("owner", "repo", 1), json=[], status=200)

    result = daemon.sweep_repo("owner", "repo", pool=pool, store=store, cursor=cursor, cutoff=_cutoff())

    assert cursor.get_capture_unit("owner/repo", "pull_files", 1).status == "in_flight"
    assert cursor.get_capture_unit("owner/repo", "pull_commits", 1).status == "complete"
    # The bug: a hole inside the repo must not read as a clean sweep.
    assert cursor.get_repo_cursor("owner/repo").sweep_status == "in_progress"
    assert result["n_transient"] == 1

    # Re-run: pull_files now succeeds. The pulls-listing page and
    # pull_commits are already 'complete', so no new request is made for
    # either — only the still-in_flight pull_files unit is retried.
    responses.add(responses.GET, _files_url("owner", "repo", 1), json=[{"filename": "f1.py"}], status=200)

    result2 = daemon.sweep_repo("owner", "repo", pool=pool, store=store, cursor=cursor, cutoff=_cutoff())

    assert cursor.get_capture_unit("owner/repo", "pull_files", 1).status == "complete"
    assert cursor.get_repo_cursor("owner/repo").sweep_status == "idle"
    assert result2["n_transient"] == 0
    assert result2["n_prs_captured"] == 1

    cursor.close()


@responses.activate
def test_summary_dict_reports_hand_computable_counts(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    # PR 1: fully captured. PR 2: terminal 404 on pull_files, pull_commits
    # succeeds. PR 3: fully captured. No transient failures in this fixture.
    page1 = [_pr(1, RECENT), _pr(2, RECENT), _pr(3, RECENT)]
    _mock_pulls_page("owner", "repo", 1, page1)

    responses.add(responses.GET, _files_url("owner", "repo", 1), json=[], status=200)
    responses.add(responses.GET, _commits_url("owner", "repo", 1), json=[], status=200)
    responses.add(responses.GET, _files_url("owner", "repo", 2), status=404)
    responses.add(responses.GET, _commits_url("owner", "repo", 2), json=[], status=200)
    responses.add(responses.GET, _files_url("owner", "repo", 3), json=[], status=200)
    responses.add(responses.GET, _commits_url("owner", "repo", 3), json=[], status=200)

    result = daemon.sweep_repo("owner", "repo", pool=pool, store=store, cursor=cursor, cutoff=_cutoff())

    assert result["n_prs_captured"] == 2
    assert result["n_prs_failed_terminal"] == 1
    assert result["n_transient"] == 0
    assert result["pages_fetched"] == 1

    cursor.close()


@responses.activate
def test_five_consecutive_transient_pr_failures_abort_run(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    prs = [_pr(n, RECENT) for n in range(1, 6)]
    _mock_pulls_page("owner", "repo", 1, prs)

    for n in range(1, 6):
        for _ in range(6):  # MAX_ATTEMPTS in ratelimit.py
            responses.add(responses.GET, _files_url("owner", "repo", n), status=503)
        # pull_commits is attempted independently of pull_files for every
        # PR (that's the whole point of the independent-units fix), so it
        # needs a mock even though this test is only about pull_files.
        responses.add(responses.GET, _commits_url("owner", "repo", n), json=[], status=200)

    with pytest.raises(daemon.AbortRun, match="5 consecutive"):
        daemon.sweep_repo("owner", "repo", pool=pool, store=store, cursor=cursor, cutoff=_cutoff())

    cursor.close()


@responses.activate
def test_pr_120_days_old_not_fetched_pagination_stops_at_that_page(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    # Sorted updated desc: PR 1 recent, PR 2 (last on the page) 120 days old.
    page1 = [_pr(1, RECENT), _pr(2, OLD)]
    _mock_pulls_page("owner", "repo", 1, page1)
    responses.add(responses.GET, _files_url("owner", "repo", 1), json=[], status=200)
    responses.add(responses.GET, _commits_url("owner", "repo", 1), json=[], status=200)
    # Deliberately no mocks for PR 2 or for page 2 — either being requested
    # is a bug, and `responses` will raise a connection error if attempted.

    daemon.sweep_repo("owner", "repo", pool=pool, store=store, cursor=cursor, cutoff=_cutoff())

    assert cursor.get_capture_unit("owner/repo", "pull_files", 1).status == "complete"
    assert cursor.get_capture_unit("owner/repo", "pull_files", 2) is None
    assert cursor.get_capture_unit("owner/repo", "pull_commits", 2) is None
    assert cursor.get_capture_unit("owner/repo", "pulls", 2) is None
    assert cursor.get_repo_cursor("owner/repo").sweep_status == "idle"

    cursor.close()


@responses.activate
def test_dry_run_issues_zero_requests_and_prints_a_count(tmp_path, capsys):
    repos_csv = tmp_path / "repos.csv"
    with repos_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["owner", "repo"])
        writer.writerow(["ownerA", "repoA"])
        writer.writerow(["ownerB", "repoB"])

    # No responses registered at all: any HTTP attempt would raise here.
    daemon.main(["--dry-run", "--repos", str(repos_csv), "--limit", "2"])

    out = capsys.readouterr().out
    assert "2" in out
    assert len(responses.calls) == 0
