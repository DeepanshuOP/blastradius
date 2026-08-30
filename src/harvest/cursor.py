"""Resumable per-repo harvest cursor (T0.3a, ROADMAP §8.2, §8.3).

Persists two things the daemon in T0.3 needs to survive a crash without
re-fetching completed work or silently skipping in-flight work:

  * `repo_cursor`  — one row per repo: where the PR-listing sweep is
    (`pr_page`) and the watermark to resume from (`last_pr_updated_at`),
    which only advances when a sweep completes cleanly.
  * `capture_unit` — one row per (repo, kind, key) actually captured — the
    exact same triple `rawstore.path_for()` uses (D-19) — so completion is
    tracked per raw-capture unit, never per run. A run is "complete" only
    when every kind it owns by run_id (`jobs`, `artifacts`) has reached a
    terminal status; PR-scoped kinds (`pull_files`, `pull_commits`) and
    sha-scoped kinds (`runs`, `checkruns`) get exactly the same per-unit
    tracking, so a commit sha shared by two different PRs is captured once
    (G4 dedup: `get_capture_unit` returns the same row regardless of which
    PR asks). See D-20.

  `capture_unit.unit_key` is stored as the UNPADDED `str(key)` — e.g. run
  id `7` is stored as `"7"`, never rawstore's zero-padded `"000000000007"`
  path segment. cursor.py tracks capture *status*, not filesystem layout;
  nobody should ever try to join a cursor row against a raw file path by
  string-matching `unit_key`.

  `capture_unit.parent_run_id` links job-scoped (`logs`) and checkrun-scoped
  (`annotations`) units back to the run_id the daemon was iterating when it
  fetched them; NULL for every other kind. `logs` is the 90-day-expiring
  kind (§8.3), so its expiry must be attributable to a run for the per-run
  and per-repo attrition numbers in §23.3 to mean anything. See D-20(a).

CONTRACT this module assumes of `src/harvest/daemon.py` (T0.3, not yet
written — this is a requirement ON it, not a claim about it): redoing an
`in_flight` unit means daemon.py will re-fetch and overwrite that unit's
raw output. For that to be safe, daemon.py's raw writes MUST be
overwrite-safe (write to a temp path, then atomic rename) — never appended
to in place. rawstore.py's `write_records()` already satisfies this.
cursor.py has no way to enforce that daemon.py actually calls it; it is
flagged here so it isn't forgotten when daemon.py is built.

Terminal per-kind states (full argument in D-20):
  * `complete` — rawstore.write_records() succeeded; real data is on disk.
  * `skipped`  — deliberately never fetched, by policy (§8.3 subtask 3: a
    success run's logs — low value per byte, and we are storage-bound).
  * `expired`  — attempted (or eligible) after GitHub's retention window
    had already closed (90d for `logs`); unrecoverable, must be counted
    (§23.3) — the expiry rate `stats()` reports is a paper number.
  * `failed`   — a permanent API failure unrelated to retention (404/410 —
    frame.py's TERMINAL_STATUSES), e.g. a deleted PR or a repo gone
    private. `reason` carries the status code and cause, the same
    convention frame.py's `_classify_failure` already uses.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.harvest.rawstore import ALLOWED_KINDS, KIND_SCOPE

DEFAULT_DB_PATH = Path("data/state/cursor.db")

# The only two D-19 scopes a parent_run_id can attach to: a job belongs to
# exactly one run, and a check-run is looked up by the same sha a run is,
# but annotations are fetched per check-run within the loop's per-run pass.
_PARENT_RUN_SCOPES = frozenset({"job", "checkrun"})

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

CREATE TABLE IF NOT EXISTS capture_unit (
    repo          TEXT NOT NULL,
    kind          TEXT NOT NULL CHECK (kind IN (
                      'pulls', 'pull_files', 'pull_commits', 'runs',
                      'jobs', 'checkruns', 'annotations', 'artifacts', 'logs',
                      'branch_runs'
                  )),
    unit_key      TEXT NOT NULL,
    status        TEXT NOT NULL CHECK (status IN (
                      'in_flight', 'complete', 'skipped', 'expired', 'failed'
                  )),
    parent_run_id INTEGER,
    started_at    TEXT NOT NULL,
    completed_at  TEXT,
    reason        TEXT,
    PRIMARY KEY (repo, kind, unit_key)
);
CREATE INDEX IF NOT EXISTS idx_capture_unit_repo_kind_status
    ON capture_unit (repo, kind, status);
CREATE INDEX IF NOT EXISTS idx_capture_unit_repo_parent_run
    ON capture_unit (repo, parent_run_id);
"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_kind(kind: str) -> None:
    if kind not in ALLOWED_KINDS:
        raise ValueError(f"unknown capture kind {kind!r}; must be one of {sorted(ALLOWED_KINDS)}")


def _validate_parent_run_id(kind: str, parent_run_id: int | None) -> None:
    if parent_run_id is None:
        return
    scope = KIND_SCOPE[kind]
    if scope not in _PARENT_RUN_SCOPES:
        raise ValueError(
            f"parent_run_id is only valid for job/checkrun-scoped kinds "
            f"(logs, annotations); kind {kind!r} has scope {scope!r}"
        )


@dataclass
class RepoCursor:
    repo: str
    last_pr_updated_at: str | None
    pr_page: int
    sweep_status: str
    updated_at: str
    last_complete_sweep_at: str | None


@dataclass
class CaptureUnit:
    repo: str
    kind: str
    unit_key: str
    status: str
    parent_run_id: int | None
    started_at: str
    completed_at: str | None
    reason: str | None


_CAPTURE_UNIT_COLUMNS = "repo, kind, unit_key, status, parent_run_id, started_at, completed_at, reason"


class CursorStore:
    """SQLite-backed resumable cursor over `repo_cursor` and `capture_unit`.

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

    # -- capture_unit: per-unit idempotency (G1/G3/G4) -----------------------

    def mark_unit_started(
        self, repo: str, kind: str, key: int | str, parent_run_id: int | None = None
    ) -> None:
        _validate_kind(kind)
        _validate_parent_run_id(kind, parent_run_id)
        self._conn.execute(
            f"""
            INSERT INTO capture_unit ({_CAPTURE_UNIT_COLUMNS})
            VALUES (?, ?, ?, 'in_flight', ?, ?, NULL, NULL)
            ON CONFLICT(repo, kind, unit_key) DO UPDATE SET
                status = 'in_flight',
                parent_run_id = excluded.parent_run_id,
                started_at = excluded.started_at,
                completed_at = NULL,
                reason = NULL
            """,
            (repo, kind, str(key), parent_run_id, _now_iso()),
        )
        self._conn.commit()

    def mark_unit_complete(self, repo: str, kind: str, key: int | str) -> None:
        _validate_kind(kind)
        self._conn.execute(
            """
            UPDATE capture_unit SET status = 'complete', completed_at = ?, reason = NULL
            WHERE repo = ? AND kind = ? AND unit_key = ?
            """,
            (_now_iso(), repo, kind, str(key)),
        )
        self._conn.commit()

    def mark_unit_skipped(self, repo: str, kind: str, key: int | str, reason: str) -> None:
        self._mark_unit_terminal(repo, kind, key, "skipped", reason)

    def mark_unit_expired(self, repo: str, kind: str, key: int | str, reason: str) -> None:
        self._mark_unit_terminal(repo, kind, key, "expired", reason)

    def mark_unit_failed(self, repo: str, kind: str, key: int | str, reason: str) -> None:
        self._mark_unit_terminal(repo, kind, key, "failed", reason)

    def _mark_unit_terminal(
        self, repo: str, kind: str, key: int | str, status: str, reason: str
    ) -> None:
        _validate_kind(kind)
        self._conn.execute(
            """
            UPDATE capture_unit SET status = ?, completed_at = ?, reason = ?
            WHERE repo = ? AND kind = ? AND unit_key = ?
            """,
            (status, _now_iso(), reason, repo, kind, str(key)),
        )
        self._conn.commit()

    def get_capture_unit(self, repo: str, kind: str, key: int | str) -> CaptureUnit | None:
        _validate_kind(kind)
        row = self._conn.execute(
            f"SELECT {_CAPTURE_UNIT_COLUMNS} FROM capture_unit "
            "WHERE repo = ? AND kind = ? AND unit_key = ?",
            (repo, kind, str(key)),
        ).fetchone()
        if row is None:
            return None
        return CaptureUnit(*row)

    def is_captured(self, repo: str, kind: str, key: int | str) -> bool:
        _validate_kind(kind)
        row = self._conn.execute(
            "SELECT 1 FROM capture_unit "
            "WHERE repo = ? AND kind = ? AND unit_key = ? AND status = 'complete'",
            (repo, kind, str(key)),
        ).fetchone()
        return row is not None

    def incomplete_units(self, repo: str, kind: str | None = None) -> list[CaptureUnit]:
        if kind is not None:
            _validate_kind(kind)
            rows = self._conn.execute(
                f"SELECT {_CAPTURE_UNIT_COLUMNS} FROM capture_unit "
                "WHERE repo = ? AND kind = ? AND status = 'in_flight' ORDER BY kind, unit_key",
                (repo, kind),
            ).fetchall()
        else:
            rows = self._conn.execute(
                f"SELECT {_CAPTURE_UNIT_COLUMNS} FROM capture_unit "
                "WHERE repo = ? AND status = 'in_flight' ORDER BY kind, unit_key",
                (repo,),
            ).fetchall()
        return [CaptureUnit(*row) for row in rows]

    def units_for_run(self, repo: str, run_id: int) -> list[CaptureUnit]:
        rows = self._conn.execute(
            f"SELECT {_CAPTURE_UNIT_COLUMNS} FROM capture_unit "
            "WHERE repo = ? AND parent_run_id = ? ORDER BY kind, unit_key",
            (repo, run_id),
        ).fetchall()
        return [CaptureUnit(*row) for row in rows]

    # -- run-level convenience, derived from capture_unit ---------------------

    def run_is_complete(self, repo: str, run_id: int) -> bool:
        run_key = str(run_id)
        row = self._conn.execute(
            """
            SELECT
                EXISTS (SELECT 1 FROM capture_unit
                        WHERE repo = ? AND kind = 'jobs' AND unit_key = ?)
                AND EXISTS (SELECT 1 FROM capture_unit
                            WHERE repo = ? AND kind = 'artifacts' AND unit_key = ?)
                AND NOT EXISTS (
                    SELECT 1 FROM capture_unit
                    WHERE repo = ? AND kind IN ('jobs', 'artifacts')
                      AND unit_key = ? AND status = 'in_flight'
                )
            """,
            (repo, run_key, repo, run_key, repo, run_key),
        ).fetchone()
        return bool(row[0])

    def incomplete_runs(self, repo: str) -> list[int]:
        rows = self._conn.execute(
            """
            SELECT unit_key FROM capture_unit
            WHERE repo = ? AND kind IN ('jobs', 'artifacts')
            EXCEPT
            SELECT unit_key FROM (
                SELECT unit_key FROM capture_unit
                WHERE repo = ? AND kind IN ('jobs', 'artifacts') AND status != 'in_flight'
                GROUP BY unit_key
                HAVING COUNT(DISTINCT kind) = 2
            )
            """,
            (repo, repo),
        ).fetchall()
        return sorted(int(r[0]) for r in rows)

    def newest_complete_run(self, repo: str) -> int | None:
        row = self._conn.execute(
            """
            SELECT MAX(CAST(unit_key AS INTEGER)) FROM (
                SELECT unit_key FROM capture_unit
                WHERE repo = ? AND kind IN ('jobs', 'artifacts') AND status = 'complete'
                GROUP BY unit_key
                HAVING COUNT(DISTINCT kind) = 2
            )
            """,
            (repo,),
        ).fetchone()
        return row[0] if row is not None and row[0] is not None else None

    # -- dashboard (T0.5a) ----------------------------------------------------

    def stats(self) -> dict:
        n_repos = self._conn.execute("SELECT COUNT(*) FROM repo_cursor").fetchone()[0]
        n_repos_never_swept = self._conn.execute(
            "SELECT COUNT(*) FROM repo_cursor WHERE last_complete_sweep_at IS NULL"
        ).fetchone()[0]

        by_kind_status: dict[str, dict[str, int]] = {kind: {} for kind in sorted(ALLOWED_KINDS)}
        for kind, status, count in self._conn.execute(
            "SELECT kind, status, COUNT(*) FROM capture_unit GROUP BY kind, status"
        ).fetchall():
            by_kind_status[kind][status] = count

        n_units_total = self._conn.execute("SELECT COUNT(*) FROM capture_unit").fetchone()[0]
        # Denominator is terminal (resolved) units only — in_flight units
        # haven't reached an outcome yet and would understate/skew the true
        # rate as more of them resolve over the course of harvesting.
        n_units_terminal = self._conn.execute(
            "SELECT COUNT(*) FROM capture_unit WHERE status != 'in_flight'"
        ).fetchone()[0]
        n_units_expired = self._conn.execute(
            "SELECT COUNT(*) FROM capture_unit WHERE status = 'expired'"
        ).fetchone()[0]
        expired_rate = (n_units_expired / n_units_terminal) if n_units_terminal else 0.0

        return {
            "n_repos": n_repos,
            "n_repos_never_swept": n_repos_never_swept,
            "by_kind_status": by_kind_status,
            "n_units_total": n_units_total,
            "n_units_terminal": n_units_terminal,
            "n_units_expired": n_units_expired,
            "expired_rate": expired_rate,
        }
