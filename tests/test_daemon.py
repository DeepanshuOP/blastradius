"""Tests for src.harvest.daemon — the T0.3 PR-sweep (stage 1, endpoints 1-3),
run-discovery (stage 2, endpoints 4-5), and check-run/annotation capture
(stage 3, endpoints 6-7) stages.

No network: all GitHub calls go through get_with_backoff and are intercepted
with `responses` at the transport layer, same convention as test_frame.py.
No mocks of our own modules — real RawStore/CursorStore against tmp_path.
"""

import csv
import json
from datetime import datetime, timedelta, timezone

import pytest
import requests
import responses
from responses import matchers

from src.harvest import daemon
from src.harvest.cursor import CursorStore
from src.harvest.rawstore import RawRecord, RawStore
from src.harvest.ratelimit import TokenPool

RECENT = "2026-08-01T00:00:00Z"
OLD = "2026-04-01T00:00:00Z"  # well over 90 days before "now" below
NOW = datetime(2026, 8, 7, tzinfo=timezone.utc)

SHA_A = "a" * 40
SHA_B = "b" * 40
SHA_C = "c" * 40


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
def test_transient_pr_failures_abort_after_ladder_exhausted(tmp_path):
    """Supersedes test_five_consecutive_transient_pr_failures_abort_run: that
    test asserted the pre-governor contract of an immediate abort on the 5th
    consecutive transient failure. The approved pause-and-probe design
    deliberately replaced that with escalating through every ladder rung
    first, so the abort (frame.py's single unified AbortRun) now only fires
    once the probe has failed at every rung."""
    from src.harvest.frame import AbortRun, TransientGovernor

    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    sleeps: list[float] = []
    fake_now = [0.0]

    def fake_sleep(seconds):
        sleeps.append(seconds)
        fake_now[0] += seconds

    def fake_monotonic():
        return fake_now[0]

    governor = TransientGovernor(pool, sleep=fake_sleep, monotonic=fake_monotonic)

    prs = [_pr(n, RECENT) for n in range(1, 6)]
    _mock_pulls_page("owner", "repo", 1, prs)

    for n in range(1, 6):
        for _ in range(6):  # MAX_ATTEMPTS in ratelimit.py
            responses.add(responses.GET, _files_url("owner", "repo", n), status=503)
        # pull_commits is attempted independently of pull_files for every
        # PR (that's the whole point of the independent-units fix), so it
        # needs a mock even though this test is only about pull_files.
        responses.add(responses.GET, _commits_url("owner", "repo", n), json=[], status=200)

    for _ in range(3):  # every rung of DEFAULT_PAUSE_LADDER probed, and fails
        responses.add(responses.GET, "https://api.github.com/rate_limit", status=503)

    with pytest.raises(AbortRun):
        daemon.sweep_repo(
            "owner", "repo", pool=pool, store=store, cursor=cursor, cutoff=_cutoff(), governor=governor
        )

    assert sum(sleeps) == 1260.0  # 60.0 + 300.0 + 900.0, every rung exhausted

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


# -- FIX 1: pull_commits/pull_files pagination -------------------------------


@responses.activate
def test_two_page_pull_commits_captures_all_commits_from_both_pages(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    page1 = [_pr(1, RECENT)]
    _mock_pulls_page("owner", "repo", 1, page1)
    responses.add(responses.GET, _files_url("owner", "repo", 1), json=[], status=200)

    commits_page1 = [{"sha": f"{i:040d}"} for i in range(100)]
    commits_page2 = [{"sha": f"{100:040d}"}]
    responses.add(
        responses.GET, _commits_url("owner", "repo", 1), json=commits_page1, status=200,
        match=[matchers.query_param_matcher({"per_page": "100", "page": "1"})],
    )
    responses.add(
        responses.GET, _commits_url("owner", "repo", 1), json=commits_page2, status=200,
        match=[matchers.query_param_matcher({"per_page": "100", "page": "2"})],
    )

    daemon.sweep_repo("owner", "repo", pool=pool, store=store, cursor=cursor, cutoff=_cutoff())

    unit = cursor.get_capture_unit("owner/repo", "pull_commits", 1)
    assert unit.status == "complete"

    records = store.read_records("owner/repo", "pull_commits", 1)
    assert len(records) == 2  # one RawRecord per page, same (repo, kind, pr_number) unit
    all_commits = daemon._read_paginated_json(store, "owner/repo", "pull_commits", 1)
    assert len(all_commits) == 101

    cursor.close()


@responses.activate
def test_endpoint_returning_full_pages_forever_stops_at_max_pr_pages(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    full_page = [{"sha": f"{i:040d}"} for i in range(100)]
    # No query matcher: the same registered response is returned for every
    # page request, simulating an endpoint that never returns a short page.
    responses.add(responses.GET, _commits_url("owner", "repo", 1), json=full_page, status=200)

    status, detail, status_code = daemon._capture_pr_unit(
        "owner", "repo", 1, "pull_commits", "pulls/1/commits",
        pool=pool, store=store, cursor=cursor, repo_full="owner/repo",
    )

    assert status == daemon.PR_UNIT_FAILED
    assert str(daemon.MAX_PR_PAGES) in detail
    assert len(responses.calls) == daemon.MAX_PR_PAGES

    unit = cursor.get_capture_unit("owner/repo", "pull_commits", 1)
    assert unit.status == "failed"
    assert str(daemon.MAX_PR_PAGES) in unit.reason

    assert not store.exists("owner/repo", "pull_commits", 1)

    cursor.close()


@responses.activate
def test_three_page_pull_commits_completes_normally_under_the_cap(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    page1 = [{"sha": f"{i:040d}"} for i in range(100)]
    page2 = [{"sha": f"{i:040d}"} for i in range(100, 200)]
    page3 = [{"sha": f"{200:040d}"}]
    responses.add(
        responses.GET, _commits_url("owner", "repo", 1), json=page1, status=200,
        match=[matchers.query_param_matcher({"per_page": "100", "page": "1"})],
    )
    responses.add(
        responses.GET, _commits_url("owner", "repo", 1), json=page2, status=200,
        match=[matchers.query_param_matcher({"per_page": "100", "page": "2"})],
    )
    responses.add(
        responses.GET, _commits_url("owner", "repo", 1), json=page3, status=200,
        match=[matchers.query_param_matcher({"per_page": "100", "page": "3"})],
    )

    status, detail, status_code = daemon._capture_pr_unit(
        "owner", "repo", 1, "pull_commits", "pulls/1/commits",
        pool=pool, store=store, cursor=cursor, repo_full="owner/repo",
    )

    assert status == daemon.PR_UNIT_COMPLETE
    assert cursor.get_capture_unit("owner/repo", "pull_commits", 1).status == "complete"
    all_commits = daemon._read_paginated_json(store, "owner/repo", "pull_commits", 1)
    assert len(all_commits) == 201

    cursor.close()


# -- Stage 2: run discovery ---------------------------------------------------


def _runs_url(owner, repo):
    return f"https://api.github.com/repos/{owner}/{repo}/actions/runs"


def _jobs_url(owner, repo, run_id):
    return f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"


def _seed_pulls_page(store, cursor, repo, page, prs):
    cursor.mark_unit_started(repo, "pulls", page)
    store.write_records(
        repo, "pulls", page,
        [RawRecord(url="seed", status=200, fetched_at="2020-01-01T00:00:00+00:00", etag=None,
                    body=json.dumps(prs).encode())],
    )
    cursor.mark_unit_complete(repo, "pulls", page)


def _seed_pull_commits(store, cursor, repo, pr_number, shas):
    cursor.mark_unit_started(repo, "pull_commits", pr_number)
    body = [{"sha": s} for s in shas]
    store.write_records(
        repo, "pull_commits", pr_number,
        [RawRecord(url="seed", status=200, fetched_at="2020-01-01T00:00:00+00:00", etag=None,
                    body=json.dumps(body).encode())],
    )
    cursor.mark_unit_complete(repo, "pull_commits", pr_number)


def _run_obj(run_id, started_at):
    return {"id": run_id, "run_started_at": started_at, "created_at": started_at}


@responses.activate
def test_two_prs_sharing_head_sha_produce_one_runs_request(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT), _pr(2, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])
    _seed_pull_commits(store, cursor, "owner/repo", 2, [SHA_A])  # same head sha as PR 1

    responses.add(
        responses.GET, _runs_url("owner", "repo"), json={"workflow_runs": []}, status=200,
        match=[matchers.query_param_matcher({"head_sha": SHA_A, "per_page": "100"})],
    )

    stats = daemon.discover_repo("owner", "repo", pool=pool, store=store, cursor=cursor, now=NOW)

    assert stats["n_shas_total"] == 1  # deduped at the sha-set level before any request
    assert len(responses.calls) == 1
    assert cursor.get_capture_unit("owner/repo", "runs", SHA_A).status == "complete"

    cursor.close()


@responses.activate
def test_sha_with_terminal_runs_unit_is_not_refetched_on_rerun(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])

    cursor.mark_unit_started("owner/repo", "runs", SHA_A)
    store.write_records(
        "owner/repo", "runs", SHA_A,
        [RawRecord(url="seed", status=200, fetched_at="2020-01-01T00:00:00+00:00", etag=None,
                    body=json.dumps({"workflow_runs": []}).encode())],
    )
    cursor.mark_unit_complete("owner/repo", "runs", SHA_A)

    # No responses registered at all: any HTTP attempt would raise here.
    stats = daemon.discover_repo("owner", "repo", pool=pool, store=store, cursor=cursor, now=NOW)

    assert len(responses.calls) == 0
    assert stats["n_shas_dedup_skipped"] == 1
    assert stats["n_shas_fetched_fresh"] == 0

    cursor.close()


@responses.activate
def test_each_run_produces_one_jobs_unit_keyed_by_run_id(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])

    workflow_runs = [_run_obj(101, RECENT), _run_obj(202, RECENT)]
    responses.add(responses.GET, _runs_url("owner", "repo"), json={"workflow_runs": workflow_runs}, status=200)
    responses.add(responses.GET, _jobs_url("owner", "repo", 101), json={"jobs": [{"id": 1}]}, status=200)
    responses.add(responses.GET, _jobs_url("owner", "repo", 202), json={"jobs": [{"id": 2}, {"id": 3}]}, status=200)

    stats = daemon.discover_repo("owner", "repo", pool=pool, store=store, cursor=cursor, now=NOW)

    assert cursor.get_capture_unit("owner/repo", "jobs", 101).status == "complete"
    assert cursor.get_capture_unit("owner/repo", "jobs", 202).status == "complete"
    assert store.read_records("owner/repo", "jobs", 101)[0].body == json.dumps({"jobs": [{"id": 1}]}).encode()
    assert stats["jobs_per_run_counts"] == [1, 2]

    cursor.close()


@responses.activate
def test_pr_with_in_flight_pull_commits_contributes_zero_shas_and_is_counted_skipped(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    cursor.mark_unit_started("owner/repo", "pull_commits", 1)  # left in_flight, never completed

    # No responses registered at all: any HTTP attempt would raise here.
    stats = daemon.discover_repo("owner", "repo", pool=pool, store=store, cursor=cursor, now=NOW)

    assert len(responses.calls) == 0
    # A row exists (in_flight) — attempted but not complete, distinct from
    # out-of-window (no row at all, see test_out_of_window_and_not_complete_counters_are_distinct).
    assert stats["n_prs_pull_commits_not_complete"] == 1
    assert stats["n_prs_out_of_window"] == 0
    assert stats["n_shas_total"] == 0

    cursor.close()


@responses.activate
def test_404_on_jobs_marks_unit_failed_and_discovery_continues(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])

    workflow_runs = [_run_obj(1, RECENT), _run_obj(2, RECENT)]
    responses.add(responses.GET, _runs_url("owner", "repo"), json={"workflow_runs": workflow_runs}, status=200)
    responses.add(responses.GET, _jobs_url("owner", "repo", 1), status=404)
    responses.add(responses.GET, _jobs_url("owner", "repo", 2), json={"jobs": [{"id": 9}]}, status=200)

    stats = daemon.discover_repo("owner", "repo", pool=pool, store=store, cursor=cursor, now=NOW)

    job1 = cursor.get_capture_unit("owner/repo", "jobs", 1)
    job2 = cursor.get_capture_unit("owner/repo", "jobs", 2)
    assert job1.status == "failed"
    assert "404" in job1.reason
    assert job2.status == "complete"
    assert stats["n_jobs_failed_terminal"] == 1
    assert stats["jobs_per_run_counts"] == [1]  # only run 2's jobs counted — run 1's data is unknown, not zero

    cursor.close()


@responses.activate
def test_run_age_report_counts_100_day_old_run_as_already_expired(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])

    old_started_at = (NOW - timedelta(days=100)).strftime("%Y-%m-%dT%H:%M:%SZ")
    workflow_runs = [_run_obj(1, old_started_at)]
    responses.add(responses.GET, _runs_url("owner", "repo"), json={"workflow_runs": workflow_runs}, status=200)
    responses.add(responses.GET, _jobs_url("owner", "repo", 1), json={"jobs": []}, status=200)

    stats = daemon.discover_repo("owner", "repo", pool=pool, store=store, cursor=cursor, now=NOW)

    assert stats["run_age_days"] == [pytest.approx(100.0, abs=0.01)]

    report = daemon.build_run_ages_report({"owner/repo": stats})
    assert report["overall"]["n_runs_expired_90d"] == 1
    assert report["overall"]["expired_90d_rate"] == 1.0
    assert report["per_repo"]["owner/repo"]["n_runs_expired_90d"] == 1

    cursor.close()


# -- Stage 3: check-run + annotation capture ----------------------------------


def _checkruns_url(owner, repo, sha):
    return f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}/check-runs"


def _annotations_url(owner, repo, check_run_id):
    return f"https://api.github.com/repos/{owner}/{repo}/check-runs/{check_run_id}/annotations"


def _seed_runs_unit(store, cursor, repo, sha, workflow_runs):
    cursor.mark_unit_started(repo, "runs", sha)
    store.write_records(
        repo, "runs", sha,
        [RawRecord(url="seed", status=200, fetched_at="2020-01-01T00:00:00+00:00", etag=None,
                    body=json.dumps({"workflow_runs": workflow_runs}).encode())],
    )
    cursor.mark_unit_complete(repo, "runs", sha)


@responses.activate
def test_shas_processed_oldest_run_first(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT), _pr(2, RECENT), _pr(3, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])
    _seed_pull_commits(store, cursor, "owner/repo", 2, [SHA_B])
    _seed_pull_commits(store, cursor, "owner/repo", 3, [SHA_C])

    oldest = (NOW - timedelta(days=200)).strftime("%Y-%m-%dT%H:%M:%SZ")
    middle = (NOW - timedelta(days=50)).strftime("%Y-%m-%dT%H:%M:%SZ")
    newest = (NOW - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
    # Seeded out of age order deliberately — sha-set iteration/dict order
    # must not be what determines request order.
    _seed_runs_unit(store, cursor, "owner/repo", SHA_C, [_run_obj(3, newest)])
    _seed_runs_unit(store, cursor, "owner/repo", SHA_A, [_run_obj(1, oldest)])
    _seed_runs_unit(store, cursor, "owner/repo", SHA_B, [_run_obj(2, middle)])

    for sha in (SHA_A, SHA_B, SHA_C):
        responses.add(responses.GET, _checkruns_url("owner", "repo", sha), json={"check_runs": []}, status=200)

    daemon.capture_checkruns([("owner", "repo")], pool=pool, store=store, cursor=cursor, now=NOW)

    called_shas = []
    for call in responses.calls:
        for sha in (SHA_A, SHA_B, SHA_C):
            if sha in call.request.url:
                called_shas.append(sha)
    assert called_shas == [SHA_A, SHA_B, SHA_C]  # oldest (200d) -> middle (50d) -> newest (5d)

    cursor.close()


@responses.activate
def test_sha_with_terminal_checkruns_unit_is_not_refetched(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])

    cursor.mark_unit_started("owner/repo", "checkruns", SHA_A)
    store.write_records(
        "owner/repo", "checkruns", SHA_A,
        [RawRecord(url="seed", status=200, fetched_at="2020-01-01T00:00:00+00:00", etag=None,
                    body=json.dumps({"check_runs": []}).encode())],
    )
    cursor.mark_unit_complete("owner/repo", "checkruns", SHA_A)

    # No responses registered at all: any HTTP attempt would raise here.
    stats = daemon.capture_checkruns([("owner", "repo")], pool=pool, store=store, cursor=cursor, now=NOW)

    assert len(responses.calls) == 0
    assert stats["n_checkruns_dedup_skipped"] == 1
    assert stats["n_checkruns_fetched_fresh"] == 0

    cursor.close()


@responses.activate
def test_each_checkrun_produces_one_annotations_unit_keyed_by_check_run_id(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])

    check_runs = [{"id": 11, "head_sha": SHA_A}, {"id": 22, "head_sha": SHA_A}]
    responses.add(responses.GET, _checkruns_url("owner", "repo", SHA_A), json={"check_runs": check_runs}, status=200)
    responses.add(responses.GET, _annotations_url("owner", "repo", 11), json=[{"message": "m1"}], status=200)
    responses.add(
        responses.GET, _annotations_url("owner", "repo", 22),
        json=[{"message": "m2"}, {"message": "m3"}], status=200,
    )

    stats = daemon.capture_checkruns([("owner", "repo")], pool=pool, store=store, cursor=cursor, now=NOW)

    unit11 = cursor.get_capture_unit("owner/repo", "annotations", 11)
    unit22 = cursor.get_capture_unit("owner/repo", "annotations", 22)
    assert unit11.status == "complete"
    assert unit22.status == "complete"
    assert store.read_records("owner/repo", "annotations", 11)[0].body == json.dumps([{"message": "m1"}]).encode()
    assert stats["annotations_per_checkrun_counts"] == [1, 2]
    # parent_run_id is not resolvable from the check-run object (see report) — always NULL.
    assert unit11.parent_run_id is None
    assert unit22.parent_run_id is None

    cursor.close()


@responses.activate
def test_checkrun_with_zero_annotations_records_complete_not_failure(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])

    responses.add(
        responses.GET, _checkruns_url("owner", "repo", SHA_A),
        json={"check_runs": [{"id": 11, "head_sha": SHA_A}]}, status=200,
    )
    responses.add(responses.GET, _annotations_url("owner", "repo", 11), json=[], status=200)

    stats = daemon.capture_checkruns([("owner", "repo")], pool=pool, store=store, cursor=cursor, now=NOW)

    unit = cursor.get_capture_unit("owner/repo", "annotations", 11)
    assert unit.status == "complete"
    assert stats["n_checkruns_zero_annotations"] == 1
    assert stats["annotations_per_checkrun_counts"] == [0]

    cursor.close()


@responses.activate
def test_404_on_annotations_marks_unit_failed_and_processing_continues(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])

    check_runs = [{"id": 11, "head_sha": SHA_A}, {"id": 22, "head_sha": SHA_A}]
    responses.add(responses.GET, _checkruns_url("owner", "repo", SHA_A), json={"check_runs": check_runs}, status=200)
    responses.add(responses.GET, _annotations_url("owner", "repo", 11), status=404)
    responses.add(responses.GET, _annotations_url("owner", "repo", 22), json=[{"message": "m"}], status=200)

    stats = daemon.capture_checkruns([("owner", "repo")], pool=pool, store=store, cursor=cursor, now=NOW)

    unit11 = cursor.get_capture_unit("owner/repo", "annotations", 11)
    unit22 = cursor.get_capture_unit("owner/repo", "annotations", 22)
    assert unit11.status == "failed"
    assert "404" in unit11.reason
    assert unit22.status == "complete"
    assert stats["n_annotations_failed_terminal"] == 1
    assert stats["annotations_per_checkrun_counts"] == [1]  # only run 22's — run 11's is unknown, not zero

    cursor.close()


@responses.activate
def test_annotations_pagination_past_cap_marks_failed_and_writes_nothing(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])

    responses.add(
        responses.GET, _checkruns_url("owner", "repo", SHA_A),
        json={"check_runs": [{"id": 11, "head_sha": SHA_A}]}, status=200,
    )
    full_page = [{"message": f"m{i}"} for i in range(100)]
    # No query matcher: the same registered response is returned for every
    # page request, simulating an endpoint that never returns a short page.
    responses.add(responses.GET, _annotations_url("owner", "repo", 11), json=full_page, status=200)

    stats = daemon.capture_checkruns([("owner", "repo")], pool=pool, store=store, cursor=cursor, now=NOW)

    unit = cursor.get_capture_unit("owner/repo", "annotations", 11)
    assert unit.status == "failed"
    assert str(daemon.MAX_PR_PAGES) in unit.reason
    assert not store.exists("owner/repo", "annotations", 11)
    assert stats["n_annotations_failed_terminal"] == 1
    # 1 checkruns request + MAX_PR_PAGES annotation-page requests.
    assert len(responses.calls) == 1 + daemon.MAX_PR_PAGES

    cursor.close()


@responses.activate
def test_out_of_window_and_not_complete_counters_are_distinct(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    # PR 1: listed on the pulls page but pull_commits was never attempted
    # (out of window — sweep_repo's window filter never called _capture_pr,
    # so no capture_unit row exists at all).
    # PR 2: pull_commits attempted but left in_flight (not complete).
    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, OLD), _pr(2, RECENT)])
    cursor.mark_unit_started("owner/repo", "pull_commits", 2)

    # No responses registered: neither PR contributes a sha, so zero requests.
    stats = daemon.discover_repo("owner", "repo", pool=pool, store=store, cursor=cursor, now=NOW)

    assert len(responses.calls) == 0
    assert stats["n_prs_out_of_window"] == 1
    assert stats["n_prs_pull_commits_not_complete"] == 1

    cursor.close()


# -- TransientGovernor wiring -------------------------------------------------


@responses.activate
def test_shared_governor_carries_sticky_rung_across_repo_boundary(tmp_path):
    """One governor passed into two successive sweep_repo() calls must not
    reset its rung index at the repo boundary: 5 transient PR failures in
    repo A pause at rung 0 (60s) and the probe succeeds; 5 more in repo B
    must pause at the now-advanced rung 1 (300s), not repeat rung 0."""
    from src.harvest.frame import TransientGovernor

    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    sleeps: list[float] = []
    fake_now = [0.0]

    def fake_sleep(seconds):
        sleeps.append(seconds)
        fake_now[0] += seconds

    def fake_monotonic():
        return fake_now[0]

    governor = TransientGovernor(pool, sleep=fake_sleep, monotonic=fake_monotonic)

    for repo in ("repoA", "repoB"):
        prs = [_pr(n, RECENT) for n in range(1, 6)]
        _mock_pulls_page("owner", repo, 1, prs)
        for n in range(1, 6):
            for _ in range(6):  # MAX_ATTEMPTS in ratelimit.py
                responses.add(responses.GET, _files_url("owner", repo, n), status=503)
            responses.add(responses.GET, _commits_url("owner", repo, n), json=[], status=200)
        responses.add(responses.GET, "https://api.github.com/rate_limit", json={}, status=200)

        daemon.sweep_repo(
            "owner", repo, pool=pool, store=store, cursor=cursor, cutoff=_cutoff(), governor=governor
        )

    assert sleeps == [60.0, 300.0]

    cursor.close()


@responses.activate
def test_discover_repo_ladder_exhausted_raises_and_leaves_units_in_flight(tmp_path):
    """A probe that fails at every rung during discover_repo's run-fetch
    escalates through the whole ladder inside a single record_transient()
    call and raises frame.AbortRun. The SHA capture units that never
    resolved stay in_flight, and since sweep_repo() was never invoked for
    this repo, complete_sweep() never fired (no repo_cursor row exists)."""
    from src.harvest.frame import AbortRun as FrameAbortRun
    from src.harvest.frame import TransientGovernor

    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    shas = [str(n) * 40 for n in range(1, 6)]
    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(n, RECENT) for n in range(1, 6)])
    for n, sha in enumerate(shas, start=1):
        _seed_pull_commits(store, cursor, "owner/repo", n, [sha])

    for _ in shas:
        for _ in range(6):  # MAX_ATTEMPTS in ratelimit.py
            responses.add(responses.GET, _runs_url("owner", "repo"), status=503)
    for _ in range(3):  # every rung of DEFAULT_PAUSE_LADDER probed, and fails
        responses.add(responses.GET, "https://api.github.com/rate_limit", status=503)

    governor = TransientGovernor(pool, sleep=lambda seconds: None, monotonic=lambda: 0.0)

    with pytest.raises(FrameAbortRun):
        daemon.discover_repo("owner", "repo", pool=pool, store=store, cursor=cursor, now=NOW, governor=governor)

    assert len(cursor.incomplete_units("owner/repo", "runs")) == 5
    assert cursor.get_repo_cursor("owner/repo") is None  # sweep_repo() never ran

    cursor.close()


class _SpyGovernor:
    """Records the exact value each record_transient()/record_success() call
    receives instead of acting on it — lets a test assert what daemon.py
    passes through without exercising TransientGovernor's real pause-and-
    probe ladder."""

    def __init__(self):
        self.transient_calls: list[int | None] = []
        self.success_calls = 0

    def record_transient(self, *, status, token_idx):
        self.transient_calls.append(status)

    def record_success(self):
        self.success_calls += 1


@responses.activate
def test_503_on_checkruns_reaches_governor_as_int_not_string(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])

    for _ in range(6):  # MAX_ATTEMPTS in ratelimit.py
        responses.add(responses.GET, _checkruns_url("owner", "repo", SHA_A), status=503)

    governor = _SpyGovernor()
    daemon.capture_checkruns(
        [("owner", "repo")], pool=pool, store=store, cursor=cursor, now=NOW, governor=governor
    )

    assert governor.transient_calls == [503]
    assert type(governor.transient_calls[0]) is int  # not "503", not "transient"

    cursor.close()


@responses.activate
def test_connection_error_on_checkruns_reaches_governor_as_none(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])

    for _ in range(6):  # MAX_ATTEMPTS in ratelimit.py
        responses.add(
            responses.GET, _checkruns_url("owner", "repo", SHA_A),
            body=requests.exceptions.ConnectionError(),
        )

    governor = _SpyGovernor()
    daemon.capture_checkruns(
        [("owner", "repo")], pool=pool, store=store, cursor=cursor, now=NOW, governor=governor
    )

    assert governor.transient_calls == [None]


@responses.activate
def test_503_on_pull_files_reaches_sweep_repo_governor_as_int_not_string(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    _mock_pulls_page("owner", "repo", 1, [_pr(1, RECENT)])
    for _ in range(6):  # MAX_ATTEMPTS in ratelimit.py
        responses.add(responses.GET, _files_url("owner", "repo", 1), status=503)
    responses.add(responses.GET, _commits_url("owner", "repo", 1), json=[], status=200)

    governor = _SpyGovernor()
    daemon.sweep_repo(
        "owner", "repo", pool=pool, store=store, cursor=cursor, cutoff=_cutoff(), governor=governor
    )

    assert governor.transient_calls == [503]
    assert type(governor.transient_calls[0]) is int  # not "503", not "503 HTTPError"

    cursor.close()


@responses.activate
def test_connection_error_on_pull_files_reaches_sweep_repo_governor_as_none(tmp_path):
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()

    _mock_pulls_page("owner", "repo", 1, [_pr(1, RECENT)])
    for _ in range(6):  # MAX_ATTEMPTS in ratelimit.py
        responses.add(
            responses.GET, _files_url("owner", "repo", 1),
            body=requests.exceptions.ConnectionError(),
        )
    responses.add(responses.GET, _commits_url("owner", "repo", 1), json=[], status=200)

    governor = _SpyGovernor()
    daemon.sweep_repo(
        "owner", "repo", pool=pool, store=store, cursor=cursor, cutoff=_cutoff(), governor=governor
    )

    assert governor.transient_calls == [None]

    cursor.close()

    cursor.close()
