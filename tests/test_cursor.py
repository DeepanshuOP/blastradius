"""Tests for src.harvest.cursor — CursorStore against a real temp sqlite file.

No mocks: every test opens an actual sqlite3 database under tmp_path.
"""

from datetime import datetime, timedelta, timezone

import pytest

from src.harvest.cursor import CursorStore


# -- repo-level PR sweep (unchanged by the capture_unit redesign) -----------


def test_fresh_db_returns_no_cursor_for_unseen_repo(tmp_path):
    store = CursorStore(tmp_path / "cursor.db")

    assert store.get_repo_cursor("owner/repo") is None

    store.close()


def test_mark_complete_then_reopen_cursor_survives(tmp_path):
    db_path = tmp_path / "cursor.db"
    store = CursorStore(db_path)
    store.start_sweep("owner/repo")
    store.complete_sweep("owner/repo", "2026-08-01T00:00:00+00:00")
    store.close()

    reopened = CursorStore(db_path)
    cursor = reopened.get_repo_cursor("owner/repo")

    assert cursor is not None
    assert cursor.last_pr_updated_at == "2026-08-01T00:00:00+00:00"
    assert cursor.sweep_status == "idle"
    assert cursor.pr_page == 1
    assert cursor.last_complete_sweep_at is not None

    reopened.close()


def test_two_sequential_writes_to_same_repo_create_no_duplicate_rows(tmp_path):
    store = CursorStore(tmp_path / "cursor.db")
    store.start_sweep("owner/repo")
    store.complete_sweep("owner/repo", "2026-08-01T00:00:00+00:00")
    store.start_sweep("owner/repo")
    store.complete_sweep("owner/repo", "2026-08-02T00:00:00+00:00")

    count = store._conn.execute(
        "SELECT COUNT(*) FROM repo_cursor WHERE repo = ?", ("owner/repo",)
    ).fetchone()[0]

    assert count == 1

    store.close()


def test_journal_mode_is_wal_after_reopen(tmp_path):
    db_path = tmp_path / "cursor.db"
    store = CursorStore(db_path)
    store.close()

    reopened = CursorStore(db_path)

    assert reopened.journal_mode() == "wal"

    reopened.close()


def test_stale_sweeps_returns_stale_repo_and_not_fresh(tmp_path):
    store = CursorStore(tmp_path / "cursor.db")
    store.start_sweep("owner/stale-repo")
    store.complete_sweep("owner/stale-repo", "2026-08-01T00:00:00+00:00")
    store.start_sweep("owner/fresh-repo")
    store.complete_sweep("owner/fresh-repo", "2026-08-01T00:00:00+00:00")

    old_ts = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
    store._conn.execute(
        "UPDATE repo_cursor SET last_complete_sweep_at = ? WHERE repo = ?",
        (old_ts, "owner/stale-repo"),
    )
    store._conn.commit()

    stale = store.stale_sweeps(older_than_hours=1.0)

    assert stale == ["owner/stale-repo"]

    store.close()


def test_start_sweep_on_in_progress_repo_resumes_at_stored_page(tmp_path):
    store = CursorStore(tmp_path / "cursor.db")
    store.start_sweep("owner/repo")
    store.advance_page("owner/repo", 7)

    store.start_sweep("owner/repo")

    cursor = store.get_repo_cursor("owner/repo")
    assert cursor.pr_page == 7
    assert cursor.sweep_status == "in_progress"

    store.close()


# -- capture_unit: per-kind completion (G1) ----------------------------------


def test_run_with_jobs_complete_artifacts_in_flight_is_not_complete(tmp_path):
    store = CursorStore(tmp_path / "cursor.db")
    store.mark_unit_started("owner/repo", "jobs", 501)
    store.mark_unit_complete("owner/repo", "jobs", 501)
    store.mark_unit_started("owner/repo", "artifacts", 501)

    assert store.run_is_complete("owner/repo", 501) is False

    store.close()


def test_run_with_jobs_complete_artifacts_skipped_is_complete(tmp_path):
    store = CursorStore(tmp_path / "cursor.db")
    store.mark_unit_started("owner/repo", "jobs", 502)
    store.mark_unit_complete("owner/repo", "jobs", 502)
    store.mark_unit_started("owner/repo", "artifacts", 502)
    store.mark_unit_skipped("owner/repo", "artifacts", 502, "no artifacts matched name filter")

    assert store.run_is_complete("owner/repo", 502) is True

    store.close()


# -- capture_unit: sha dedup (G4) --------------------------------------------


def test_same_sha_recorded_once_returns_same_row_for_two_prs(tmp_path):
    store = CursorStore(tmp_path / "cursor.db")
    sha = "a" * 40
    store.mark_unit_started("owner/repo", "runs", sha)
    store.mark_unit_complete("owner/repo", "runs", sha)

    # Two different PRs sharing this head sha both look it up the same way —
    # there is no PR identity in the lookup at all, which is the point.
    unit_seen_by_pr_a = store.get_capture_unit("owner/repo", "runs", sha)
    unit_seen_by_pr_b = store.get_capture_unit("owner/repo", "runs", sha)

    assert unit_seen_by_pr_a == unit_seen_by_pr_b
    assert unit_seen_by_pr_a.status == "complete"

    store.close()


# -- capture_unit: terminal states round-trip with reason -------------------


def test_each_terminal_state_round_trips_with_reason(tmp_path):
    store = CursorStore(tmp_path / "cursor.db")

    store.mark_unit_started("owner/repo", "jobs", 1)
    store.mark_unit_complete("owner/repo", "jobs", 1)
    complete_unit = store.get_capture_unit("owner/repo", "jobs", 1)
    assert complete_unit.status == "complete"
    assert complete_unit.reason is None

    store.mark_unit_started("owner/repo", "artifacts", 2)
    store.mark_unit_skipped("owner/repo", "artifacts", 2, "no artifacts matched name filter")
    skipped_unit = store.get_capture_unit("owner/repo", "artifacts", 2)
    assert skipped_unit.status == "skipped"
    assert skipped_unit.reason == "no artifacts matched name filter"

    store.mark_unit_started("owner/repo", "logs", 3)
    store.mark_unit_expired("owner/repo", "logs", 3, "90-day retention window closed")
    expired_unit = store.get_capture_unit("owner/repo", "logs", 3)
    assert expired_unit.status == "expired"
    assert expired_unit.reason == "90-day retention window closed"

    store.mark_unit_started("owner/repo", "pull_files", 4)
    store.mark_unit_failed("owner/repo", "pull_files", 4, "404 HTTPError")
    failed_unit = store.get_capture_unit("owner/repo", "pull_files", 4)
    assert failed_unit.status == "failed"
    assert failed_unit.reason == "404 HTTPError"

    store.close()


# -- capture_unit: parent_run_id (A1) ----------------------------------------


def test_expired_logs_unit_with_parent_run_id_retrievable_by_run(tmp_path):
    store = CursorStore(tmp_path / "cursor.db")
    store.mark_unit_started("owner/repo", "logs", 9001, parent_run_id=555)
    store.mark_unit_expired("owner/repo", "logs", 9001, "90-day retention window closed")

    units = store.units_for_run("owner/repo", 555)

    assert len(units) == 1
    assert units[0].kind == "logs"
    assert units[0].unit_key == "9001"
    assert units[0].status == "expired"
    assert units[0].parent_run_id == 555

    store.close()


def test_parent_run_id_for_sha_scoped_kind_raises(tmp_path):
    store = CursorStore(tmp_path / "cursor.db")

    with pytest.raises(ValueError):
        store.mark_unit_started("owner/repo", "runs", "a" * 40, parent_run_id=1)

    count = store._conn.execute("SELECT COUNT(*) FROM capture_unit").fetchone()[0]
    assert count == 0

    store.close()


# -- capture_unit: kind validation (A3) --------------------------------------


def test_unknown_kind_raises_value_error_not_sqlite_error(tmp_path):
    store = CursorStore(tmp_path / "cursor.db")

    with pytest.raises(ValueError):
        store.mark_unit_started("owner/repo", "not_a_real_kind", 1)

    # never reached SQL, so no row (and no sqlite3.IntegrityError) either
    count = store._conn.execute("SELECT COUNT(*) FROM capture_unit").fetchone()[0]
    assert count == 0

    store.close()


def test_unknown_kind_raises_on_read_methods_too(tmp_path):
    store = CursorStore(tmp_path / "cursor.db")

    with pytest.raises(ValueError):
        store.get_capture_unit("owner/repo", "not_a_real_kind", 1)
    with pytest.raises(ValueError):
        store.is_captured("owner/repo", "not_a_real_kind", 1)

    store.close()


# -- capture_unit: incidental coverage of the remaining new public methods --


def test_is_captured_true_only_for_complete_status(tmp_path):
    store = CursorStore(tmp_path / "cursor.db")
    store.mark_unit_started("owner/repo", "jobs", 1)

    assert store.is_captured("owner/repo", "jobs", 1) is False

    store.mark_unit_complete("owner/repo", "jobs", 1)

    assert store.is_captured("owner/repo", "jobs", 1) is True

    store.close()


def test_incomplete_units_filters_by_kind_and_status(tmp_path):
    store = CursorStore(tmp_path / "cursor.db")
    store.mark_unit_started("owner/repo", "jobs", 1)
    store.mark_unit_started("owner/repo", "jobs", 2)
    store.mark_unit_complete("owner/repo", "jobs", 2)
    store.mark_unit_started("owner/repo", "artifacts", 1)

    jobs_incomplete = store.incomplete_units("owner/repo", "jobs")
    all_incomplete = store.incomplete_units("owner/repo")

    assert [u.unit_key for u in jobs_incomplete] == ["1"]
    assert {(u.kind, u.unit_key) for u in all_incomplete} == {("jobs", "1"), ("artifacts", "1")}

    store.close()


def test_incomplete_runs_and_newest_complete_run(tmp_path):
    store = CursorStore(tmp_path / "cursor.db")

    store.mark_unit_started("owner/repo", "jobs", 10)
    store.mark_unit_complete("owner/repo", "jobs", 10)
    store.mark_unit_started("owner/repo", "artifacts", 10)
    store.mark_unit_complete("owner/repo", "artifacts", 10)

    store.mark_unit_started("owner/repo", "jobs", 20)
    store.mark_unit_complete("owner/repo", "jobs", 20)
    store.mark_unit_started("owner/repo", "artifacts", 20)  # left in_flight

    assert store.incomplete_runs("owner/repo") == [20]
    assert store.newest_complete_run("owner/repo") == 10

    store.close()


# -- stats() (§23.3 / G2 expiry rate) ----------------------------------------


def test_stats_reports_correct_expired_rate_on_known_mix(tmp_path):
    store = CursorStore(tmp_path / "cursor.db")

    store.mark_unit_started("owner/repo", "jobs", 1)
    store.mark_unit_complete("owner/repo", "jobs", 1)
    store.mark_unit_started("owner/repo", "jobs", 2)
    store.mark_unit_complete("owner/repo", "jobs", 2)
    store.mark_unit_started("owner/repo", "jobs", 3)  # left in_flight

    store.mark_unit_started("owner/repo", "artifacts", 1)
    store.mark_unit_complete("owner/repo", "artifacts", 1)
    store.mark_unit_started("owner/repo", "artifacts", 2)
    store.mark_unit_skipped("owner/repo", "artifacts", 2, "no artifacts matched name filter")

    store.mark_unit_started("owner/repo", "logs", 10, parent_run_id=1)
    store.mark_unit_expired("owner/repo", "logs", 10, "90-day retention window closed")
    store.mark_unit_started("owner/repo", "logs", 11, parent_run_id=2)
    store.mark_unit_failed("owner/repo", "logs", 11, "404 HTTPError")

    stats = store.stats()

    assert stats["n_units_total"] == 7
    assert stats["n_units_terminal"] == 6
    assert stats["n_units_expired"] == 1
    assert stats["expired_rate"] == pytest.approx(1 / 6)
    assert stats["by_kind_status"]["jobs"] == {"complete": 2, "in_flight": 1}
    assert stats["by_kind_status"]["artifacts"] == {"complete": 1, "skipped": 1}
    assert stats["by_kind_status"]["logs"] == {"expired": 1, "failed": 1}

    store.close()
