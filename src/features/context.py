"""The change and the history it is judged against, one interface for two worlds.

`featurize` (``src/features/test_features.py``) never reads a parquet or a git
repo itself. It asks a :class:`HistoryView`, so the SAME feature code scores a
BR-Bench instance offline (:class:`BrBenchHistory`) and a live repository in the
agents (:class:`LocalGitHistory`).

Time-safety is a property of the interface: every method takes a timestamp
`ts` and may only return information strictly BEFORE it.

Failure *events*: one event per (run, test_id) failure. Several test ids of one
file failing in one run are several events, which is exactly how the RQ1
historical-frequency baseline counts them (D-52), so the B4 baseline and the
`hist_` features agree with the published numbers.
"""

from __future__ import annotations

import json
import os
import subprocess
from bisect import bisect_left
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

SECONDS_PER_DAY = 86400


@dataclass(frozen=True)
class ChangeContext:
    """What is known about a change at the moment a prediction is asked for.

    Attributes:
        repo: `owner/name`.
        instance_key: `(repo, run_id)` offline; any hashable label online.
        ts: Epoch seconds of `run_started_at`; the prediction cutoff.
        changed_files: Repo-relative paths in the change, sorted.
        n_lines_changed: Additions plus deletions.
        touches_test_file: Any changed path contains "test" (`is_test_filename`).
        touches_build_config: A build file changed.
        touches_ci_config: A CI workflow changed.
        is_docs_only: Every changed file is documentation.
        head_sha: The change's own head commit; its commit is never evidence.
    """

    repo: str
    instance_key: tuple
    ts: int
    changed_files: tuple[str, ...]
    n_lines_changed: int = 0
    touches_test_file: bool = False
    touches_build_config: bool = False
    touches_ci_config: bool = False
    is_docs_only: bool = False
    head_sha: str | None = None


class HistoryView(Protocol):
    """Everything `featurize` may ask about the past of one repository."""

    def failures_before(self, test_file: str, ts: int) -> list[tuple[int, object]]:
        """Strict fault-revealing failure events of `test_file` with time `< ts`, oldest first."""

    def head_failures_before(self, test_file: str, ts: int) -> list[int]:
        """Failure times of `test_file` at the head of any run (any split) `< ts`, oldest first."""

    def cochange_stats(self, changed_file: str, test_file: str, ts: int,
                       exclude_sha: str | None = None) -> tuple[int, float]:
        """`(support, confidence)` of the trailing co-change of the pair, `(0, 0.0)` if below threshold."""

    def cochange_partners(self, changed_file: str, ts: int,
                          exclude_sha: str | None = None) -> dict[str, tuple[int, float]]:
        """Every trailing co-change partner of `changed_file` as `{path: (support, confidence)}`."""

    def cofailure_count(self, changed_file: str, test_file: str, ts: int) -> int:
        """Earlier strict instances where `test_file` was a label and `changed_file` was in the change."""


def _epoch(iso: str) -> int:
    """Epoch seconds of an ISO-8601 stamp (UTC when no offset is present)."""
    dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


class BrBenchHistory:
    """History of the BR-Bench corpus, read from the RQ1 loader's tables.

    Built from `analysis.rq1_divergence.Rq1Data` so co-change, strict labels and
    the binding are exactly the ones RQ1 publishes; nothing is re-derived.
    """

    def __init__(self, data) -> None:
        """Index the strict labels, head failures and co-failures of `data`.

        Args:
            data: `analysis.rq1_divergence.Rq1Data` from `load_data()`.
        """
        from analysis.rq1_divergence import ground_truth, run_ts  # lazy: research-side helpers

        self._data = data
        self._strict: dict[tuple[str, str], list[tuple[int, int]]] = {}
        for r in data.hist_all.itertuples():
            self._strict.setdefault((r.repo, r.resolved_path), []).append((run_ts(r.run_started_at), int(r.run_id)))
        for v in self._strict.values():
            v.sort()
        self._strict_ts = {k: [t for t, _ in v] for k, v in self._strict.items()}

        head = data.hist_legacy
        head = head[head["split"] == "all"].drop_duplicates(subset=["run_id", "test_id"])
        self._head: dict[tuple[str, str], list[int]] = {}
        for r in head.itertuples():
            self._head.setdefault((r.repo, r.resolved_path), []).append(run_ts(r.run_started_at))
        for v in self._head.values():
            v.sort()

        self._cofail: dict[tuple[str, str, str], list[int]] = {}
        started = {(r["repo"], r["run_id"]): run_ts(r["run_started_at"]) for _, r in data.valid_runs.iterrows()}
        pr_of = {(r["repo"], r["run_id"]): str(r["pr_number"]) for _, r in data.valid_runs.iterrows()}
        for key, files in ground_truth(data).items():
            if key not in started:
                continue
            changed = data.pr_to_changed.get((key[0], pr_of[key]), set())
            for cf in changed:
                for tf in files:
                    self._cofail.setdefault((key[0], cf, tf), []).append(started[key])
        for v in self._cofail.values():
            v.sort()
        self._partners: dict[tuple, dict[str, tuple[int, float]]] = {}

    def failures_before(self, test_file: str, ts: int, repo: str | None = None) -> list[tuple[int, object]]:
        """See :class:`HistoryView`. `repo` is required: BR-Bench holds many repos."""
        key = (repo, test_file)
        n = bisect_left(self._strict_ts.get(key, []), ts)
        return list(self._strict.get(key, [])[:n])

    def head_failures_before(self, test_file: str, ts: int, repo: str | None = None) -> list[int]:
        """See :class:`HistoryView`."""
        lst = self._head.get((repo, test_file), [])
        return lst[:bisect_left(lst, ts)]

    def cochange_partners(self, changed_file: str, ts: int, exclude_sha: str | None = None,
                          repo: str | None = None) -> dict[str, tuple[int, float]]:
        """See :class:`HistoryView`."""
        key = (repo, changed_file, ts, exclude_sha)
        if key not in self._partners:
            rh = self._data.history.get(repo)
            ps = rh.partners(changed_file, ts, exclude_sha=exclude_sha) if rh is not None else []
            self._partners[key] = {p.path: (p.support, p.confidence) for p in ps}
        return self._partners[key]

    def cochange_stats(self, changed_file: str, test_file: str, ts: int, exclude_sha: str | None = None,
                       repo: str | None = None) -> tuple[int, float]:
        """See :class:`HistoryView`."""
        return self.cochange_partners(changed_file, ts, exclude_sha, repo).get(test_file, (0, 0.0))

    def cofailure_count(self, changed_file: str, test_file: str, ts: int, repo: str | None = None) -> int:
        """See :class:`HistoryView`."""
        return bisect_left(self._cofail.get((repo, changed_file, test_file), []), ts)

    def for_repo(self, repo: str) -> "RepoBound":
        """A view fixed to one repo, satisfying :class:`HistoryView` exactly."""
        return RepoBound(self, repo)


class RepoBound:
    """`BrBenchHistory` restricted to one repo (the `HistoryView` signature has no repo)."""

    def __init__(self, hist: BrBenchHistory, repo: str) -> None:
        self._h, self.repo = hist, repo

    def failures_before(self, test_file: str, ts: int) -> list[tuple[int, object]]:
        return self._h.failures_before(test_file, ts, self.repo)

    def head_failures_before(self, test_file: str, ts: int) -> list[int]:
        return self._h.head_failures_before(test_file, ts, self.repo)

    def cochange_partners(self, changed_file: str, ts: int, exclude_sha: str | None = None):
        return self._h.cochange_partners(changed_file, ts, exclude_sha, self.repo)

    def cochange_stats(self, changed_file: str, test_file: str, ts: int, exclude_sha: str | None = None):
        return self._h.cochange_stats(changed_file, test_file, ts, exclude_sha, self.repo)

    def cofailure_count(self, changed_file: str, test_file: str, ts: int) -> int:
        return self._h.cofailure_count(changed_file, test_file, ts, self.repo)


class LocalGitHistory:
    """History of a live repository: `git log` for co-change, the Regression agent's outcomes for failures.

    Failures come from `<state>/history/test_outcomes.jsonl`
    (`{"ts", "commit", "test_id", "outcome"}` per line). A `test_id` such as
    `tests/test_a.py::test_x` belongs to the file before `::`. There is no split
    notion online, so strict and head failures are the same events, and a failure
    is co-attributed to the files of the commit it was recorded at.
    """

    def __init__(self, repo_path: Path | str, outcomes_path: Path | str | None = None, rev: str = "HEAD",
                 window_days: int = 365, min_support: int = 2, max_files: int = 50) -> None:
        """Read the commit log and outcome history once.

        Args:
            repo_path: The working repository.
            outcomes_path: The jsonl history; default `<repo>/.blastradius/history/test_outcomes.jsonl`.
            rev: Commit-ish to walk the log back from.
            window_days: Trailing co-change window.
            min_support: Co-change support threshold.
            max_files: Commits touching more files than this are skipped.
        """
        from analysis.cochange_trailing import RepoHistory, read_history

        self.repo_path = Path(repo_path)
        commits = read_history(self.repo_path, rev, 0, 2**31 - 1, max_files)
        self._hist = RepoHistory(commits, window_days, min_support)
        path = Path(outcomes_path) if outcomes_path else self.repo_path / ".blastradius" / "history" / "test_outcomes.jsonl"
        self._events: dict[str, list[tuple[int, str]]] = {}  # file -> [(ts, commit)]
        self._commit_files: dict[str, set[str]] = {}
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                r = json.loads(line)
                if r.get("outcome") not in ("failed", "error"):
                    continue
                f = str(r["test_id"]).split("::")[0]
                self._events.setdefault(f, []).append((_epoch(r["ts"]), str(r.get("commit", ""))))
        for v in self._events.values():
            v.sort()

    def failures_before(self, test_file: str, ts: int) -> list[tuple[int, object]]:
        """See :class:`HistoryView`."""
        return [(t, c) for t, c in self._events.get(test_file, []) if t < ts]

    def head_failures_before(self, test_file: str, ts: int) -> list[int]:
        """See :class:`HistoryView`: same events as `failures_before`."""
        return [t for t, _ in self.failures_before(test_file, ts)]

    def cochange_partners(self, changed_file: str, ts: int, exclude_sha: str | None = None):
        """See :class:`HistoryView`."""
        return {p.path: (p.support, p.confidence) for p in self._hist.partners(changed_file, ts, exclude_sha)}

    def cochange_stats(self, changed_file: str, test_file: str, ts: int, exclude_sha: str | None = None):
        """See :class:`HistoryView`."""
        return self.cochange_partners(changed_file, ts, exclude_sha).get(test_file, (0, 0.0))

    def _files_of(self, commit: str) -> set[str]:
        if commit not in self._commit_files:
            out = subprocess.run(["git", "-C", str(self.repo_path), "show", "--no-renames", "--name-only",
                                  "--format=", commit], capture_output=True, text=True, check=False,
                                 env={**os.environ, "GIT_NO_LAZY_FETCH": "1"}).stdout
            self._commit_files[commit] = {ln.strip() for ln in out.splitlines() if ln.strip()}
        return self._commit_files[commit]

    def cofailure_count(self, changed_file: str, test_file: str, ts: int) -> int:
        """See :class:`HistoryView`."""
        return sum(1 for t, c in self._events.get(test_file, []) if t < ts and c and changed_file in self._files_of(c))
