"""Co-change evidence available at a point in time (leakage-free, per instance).

`analysis/cochange_mine.py` mines ONE table over a window ending at the corpus
pin (`as_of`), so an instance whose run started earlier is scored with commits
that landed after it ran. This module mines the same statistic from the commit
log restricted to commits strictly before an instance's `run_started_at`, over
the same trailing window, support threshold and oversize rule:

  - non-merge commits only; commits touching more than `max_files` files, or no
    file, are skipped (as `cochange_mine.parse_git_log_commits` /
    `mine_repo_cochange` do);
  - `support(f, g)`    = commits in the window touching both;
  - `confidence(f->g)` = support / commits in the window touching f;
  - a pair is kept only at support >= `min_support`.

`git log --no-renames` is used because the clones are blobless and rename detection reads
blobs (it fails offline, `GIT_NO_LAZY_FETCH=1`); the miner ran with lazy fetch on, so a renamed file
appears here under both its old and new path. Commit time is the COMMITTER time (`%ct`), the same clock `git log --since` /
`--until` use in the miner. The window is `[cutoff - window_days, cutoff)`.
Ranking is confidence desc, support desc, path asc (deterministic; the static
table's order among ties was not).
"""

from __future__ import annotations

import datetime
import os
import subprocess
from bisect import bisect_left
from dataclasses import dataclass
from pathlib import Path

from analysis.cochange_mine import DEFAULT_MAX_FILES_PER_COMMIT, DEFAULT_WINDOW_DAYS

SECONDS_PER_DAY = 86400
_SEP = "@@@COMMIT:"


@dataclass(frozen=True)
class Commit:
    """One mined commit."""

    sha: str
    ts: int  # committer time, epoch seconds
    files: tuple[str, ...]  # sorted, de-duplicated


def read_history(clone: Path, rev: str, since_ts: int, until_ts: int,
                 max_files: int = DEFAULT_MAX_FILES_PER_COMMIT) -> list[Commit]:
    """Mined commits of `rev` with `since_ts <= committer time <= until_ts`.

    Args:
        clone: Path of the git clone.
        rev: Commit-ish to walk back from (a pinned sha, never live HEAD).
        since_ts: Earliest committer time, epoch seconds (inclusive).
        until_ts: Latest committer time, epoch seconds (inclusive).
        max_files: Commits touching more files than this are skipped.

    Returns:
        Commits sorted by `(ts, sha)`.
    """
    def iso(ts: int) -> str:
        return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    out = subprocess.run(
        ["git", "-C", str(clone), "log", rev, "--no-merges", "--no-renames", f"--since={iso(since_ts)}",
         f"--until={iso(until_ts)}", f"--pretty=format:{_SEP}%H %ct", "--name-only"],
        capture_output=True, text=True, check=True, encoding="utf-8", errors="replace",
        env={**os.environ, "GIT_NO_LAZY_FETCH": "1"},
    ).stdout
    commits: list[Commit] = []
    sha, ts, files = None, 0, []

    def flush() -> None:
        uniq = tuple(sorted(set(files)))
        if sha is not None and 0 < len(uniq) <= max_files:
            commits.append(Commit(sha, ts, uniq))

    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(_SEP):
            flush()
            sha_s, ts_s = line[len(_SEP):].split(" ")
            sha, ts, files = sha_s, int(ts_s), []
        else:
            files.append(line)
    flush()
    commits.sort(key=lambda c: (c.ts, c.sha))
    return commits


@dataclass(frozen=True)
class Partner:
    """A co-change partner of a file, with the statistics that ranked it."""

    path: str
    support: int
    confidence: float


class RepoHistory:
    """Commit log of one repository, queryable as of any cutoff time."""

    def __init__(self, commits: list[Commit], window_days: int = DEFAULT_WINDOW_DAYS,
                 min_support: int = 2) -> None:
        self.commits = sorted(commits, key=lambda c: (c.ts, c.sha))
        self.window_days = window_days
        self.min_support = min_support
        self._ts = [c.ts for c in self.commits]
        self._by_file: dict[str, list[int]] = {}
        for i, c in enumerate(self.commits):
            for f in c.files:
                self._by_file.setdefault(f, []).append(i)

    def _window(self, cutoff_ts: int) -> tuple[int, int]:
        """Index range `[lo, hi)` of commits with `cutoff - window <= ts < cutoff`."""
        return (bisect_left(self._ts, cutoff_ts - self.window_days * SECONDS_PER_DAY),
                bisect_left(self._ts, cutoff_ts))

    def commits_touching(self, path: str, cutoff_ts: int, exclude_sha: str | None = None) -> list[Commit]:
        """Commits in the window ending strictly before `cutoff_ts` that touch `path`."""
        lo, hi = self._window(cutoff_ts)
        return [self.commits[i] for i in self._by_file.get(path, ()) if lo <= i < hi
                and self.commits[i].sha != exclude_sha]

    def partners(self, path: str, cutoff_ts: int, exclude_sha: str | None = None,
                 both_directions: bool = False) -> list[Partner]:
        """Ranked co-change partners of `path` using only commits before `cutoff_ts`.

        Args:
            path: The changed file.
            cutoff_ts: Instance start, epoch seconds; commits at or after it are invisible.
            exclude_sha: A commit to ignore even if dated before the cutoff (the instance's own head).
            both_directions: False reproduces the static table's reach, which stores each pair once
                as `file_a < file_b` and was looked up by `file_a` only, so a file's partners are
                only the lexicographically LATER paths. True returns every partner.

        Returns:
            Partners with support >= `min_support`, best first.
        """
        touching = self.commits_touching(path, cutoff_ts, exclude_sha)
        n = len(touching)
        counts: dict[str, int] = {}
        for c in touching:
            for g in c.files:
                if g != path and (both_directions or g > path):
                    counts[g] = counts.get(g, 0) + 1
        ranked = [Partner(g, s, s / n) for g, s in counts.items() if s >= self.min_support]
        ranked.sort(key=lambda p: (-p.confidence, -p.support, p.path))
        return ranked
