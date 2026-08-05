"""Resumable per-repo harvest cursor (T0.3a, ROADMAP §8.2, §8.3).

Persists two things the daemon in T0.3 needs to survive a crash without
re-fetching completed work or silently skipping in-flight work:

  * `repo_cursor`  — one row per repo: where the PR-listing sweep is
    (`pr_page`) and the watermark to resume from (`last_pr_updated_at`),
    which only advances when a sweep completes cleanly.
  * `run_capture`  — one row per (repo, run_id) actually captured, so a
    crash mid-run leaves that run's status at 'in_flight' forever until
    something calls `mark_run_complete` — never silently marked done.

CONTRACT this module assumes of `src/harvest/daemon.py` (T0.3, not yet
written — this is a requirement ON it, not a claim about it): redoing an
`in_flight` run means daemon.py will re-fetch and overwrite that run's raw
output. For that to be safe, daemon.py's raw writes MUST be overwrite-safe
(write to a temp path, then atomic rename) — never appended to in place.
cursor.py has no way to enforce this; it is flagged here so it isn't
forgotten when daemon.py is built.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_DB_PATH = Path("data/state/cursor.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS repo_cursor (
    repo                   TEXT PRIMARY KEY,
    last_pr_updated_at     TEXT,
    pr_page                INTEGER NOT NULL DEFAULT 1,
    sweep_status           TEXT NOT NULL DEFAULT 'idle'
                           CHECK (sweep_status IN ('idle', 'in_progress')),
    updated_at             TEXT NOT NULL,
    last_complete_sweep_at TEXT
);

CREATE TABLE IF NOT EXISTS run_capture (
    repo         TEXT NOT NULL,
    run_id       INTEGER NOT NULL,
    status       TEXT NOT NULL CHECK (status IN ('in_flight', 'complete')),
    started_at   TEXT NOT NULL,
    completed_at TEXT,
    PRIMARY KEY (repo, run_id)
);
CREATE INDEX IF NOT EXISTS idx_run_capture_repo_status
    ON run_capture (repo, status);
"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RepoCursor:
    repo: str
    last_pr_updated_at: str | None
    pr_page: int
    sweep_status: str
    updated_at: str
    last_complete_sweep_at: str | None


class CursorStore:
    """SQLite-backed resumable cursor over `repo_cursor` and `run_capture`.

    One connection per instance, WAL journal mode so T0.5a's dashboard can
    read the db concurrently with the daemon writing it. Not thread-safe —
    T0.3's daemon is single-process, single-writer.
    """

    def __init__(self, db_path: Path | str) -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._db_path))
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "CursorStore":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def journal_mode(self) -> str:
        return self._conn.execute("PRAGMA journal_mode").fetchone()[0]

    # -- repo-level PR sweep -------------------------------------------------

    def get_repo_cursor(self, repo: str) -> RepoCursor | None:
        row = self._conn.execute(
            """
            SELECT repo, last_pr_updated_at, pr_page, sweep_status,
                   updated_at, last_complete_sweep_at
            FROM repo_cursor WHERE repo = ?
            """,
            (repo,),
        ).fetchone()
        if row is None:
            return None
        return RepoCursor(*row)

    def start_sweep(self, repo: str) -> None:
        now = _now_iso()
        self._conn.execute(
            """
            INSERT INTO repo_cursor
                (repo, last_pr_updated_at, pr_page, sweep_status,
                 updated_at, last_complete_sweep_at)
            VALUES (?, NULL, 1, 'in_progress', ?, NULL)
            ON CONFLICT(repo) DO UPDATE SET
                pr_page = CASE WHEN sweep_status = 'in_progress'
                               THEN pr_page ELSE 1 END,
                sweep_status = 'in_progress',
                updated_at = excluded.updated_at
            """,
            (repo, now),
        )
        self._conn.commit()

    def advance_page(self, repo: str, page: int) -> None:
        self._conn.execute(
            "UPDATE repo_cursor SET pr_page = ?, updated_at = ? WHERE repo = ?",
            (page, _now_iso(), repo),
        )
        self._conn.commit()

    def complete_sweep(self, repo: str, newest_pr_updated_at: str) -> None:
        now = _now_iso()
        self._conn.execute(
            """
            INSERT INTO repo_cursor
                (repo, last_pr_updated_at, pr_page, sweep_status,
                 updated_at, last_complete_sweep_at)
            VALUES (?, ?, 1, 'idle', ?, ?)
            ON CONFLICT(repo) DO UPDATE SET
                last_pr_updated_at = excluded.last_pr_updated_at,
                pr_page = 1,
                sweep_status = 'idle',
                updated_at = excluded.updated_at,
                last_complete_sweep_at = excluded.last_complete_sweep_at
            """,
            (repo, newest_pr_updated_at, now, now),
        )
        self._conn.commit()

    def stale_sweeps(self, older_than_hours: float) -> list[str]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=older_than_hours)
        rows = self._conn.execute(
            "SELECT repo, last_complete_sweep_at FROM repo_cursor"
        ).fetchall()
        stale = []
        for repo, last_complete_sweep_at in rows:
            if last_complete_sweep_at is None:
                stale.append(repo)
            elif datetime.fromisoformat(last_complete_sweep_at) < cutoff:
                stale.append(repo)
        return stale

    # -- run-level idempotency -----------------------------------------------

    def mark_run_started(self, repo: str, run_id: int) -> None:
        self._conn.execute(
            """
            INSERT INTO run_capture (repo, run_id, status, started_at, completed_at)
            VALUES (?, ?, 'in_flight', ?, NULL)
            ON CONFLICT(repo, run_id) DO UPDATE SET
                status = 'in_flight',
                started_at = excluded.started_at,
                completed_at = NULL
            """,
            (repo, run_id, _now_iso()),
        )
        self._conn.commit()

    def mark_run_complete(self, repo: str, run_id: int) -> None:
        self._conn.execute(
            "UPDATE run_capture SET status = 'complete', completed_at = ? "
            "WHERE repo = ? AND run_id = ?",
            (_now_iso(), repo, run_id),
        )
        self._conn.commit()

    def is_run_complete(self, repo: str, run_id: int) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM run_capture WHERE repo = ? AND run_id = ? AND status = 'complete'",
            (repo, run_id),
        ).fetchone()
        return row is not None

    def incomplete_runs(self, repo: str) -> list[int]:
        rows = self._conn.execute(
            "SELECT run_id FROM run_capture WHERE repo = ? AND status = 'in_flight' "
            "ORDER BY run_id",
            (repo,),
        ).fetchall()
        return [r[0] for r in rows]

    def newest_complete_run(self, repo: str) -> int | None:
        row = self._conn.execute(
            "SELECT MAX(run_id) FROM run_capture WHERE repo = ? AND status = 'complete'",
            (repo,),
        ).fetchone()
        return row[0] if row is not None else None

    # -- dashboard (T0.5a) ----------------------------------------------------

    def stats(self) -> dict:
        n_repos = self._conn.execute("SELECT COUNT(*) FROM repo_cursor").fetchone()[0]
        n_repos_never_swept = self._conn.execute(
            "SELECT COUNT(*) FROM repo_cursor WHERE last_complete_sweep_at IS NULL"
        ).fetchone()[0]
        n_runs_complete = self._conn.execute(
            "SELECT COUNT(*) FROM run_capture WHERE status = 'complete'"
        ).fetchone()[0]
        n_runs_in_flight = self._conn.execute(
            "SELECT COUNT(*) FROM run_capture WHERE status = 'in_flight'"
        ).fetchone()[0]
        return {
            "n_repos": n_repos,
            "n_repos_never_swept": n_repos_never_swept,
            "n_runs_complete": n_runs_complete,
            "n_runs_in_flight": n_runs_in_flight,
        }
