"""Tests for src.harvest.cursor — CursorStore against a real temp sqlite file.

No mocks: every test opens an actual sqlite3 database under tmp_path.
"""

from datetime import datetime, timedelta, timezone

from src.harvest.cursor import CursorStore


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


def test_in_flight_run_never_completed_is_returned_by_incomplete_runs(tmp_path):
    store = CursorStore(tmp_path / "cursor.db")
    store.mark_run_started("owner/repo", 101)
    store.mark_run_started("owner/repo", 102)
    store.mark_run_complete("owner/repo", 101)

    incomplete = store.incomplete_runs("owner/repo")

    assert incomplete == [102]
    assert store.is_run_complete("owner/repo", 101) is True
    assert store.is_run_complete("owner/repo", 102) is False

    store.close()


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
