"""Trailing co-change on a REAL git repository built in tmp_path with fixed committer dates."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from analysis.cochange_trailing import RepoHistory, read_history

DAY = 86400
T0 = 1_700_000_000  # an arbitrary fixed epoch second


def _git(repo: Path, *args: str, ts: int | None = None) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.org",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.org"}
    if ts is not None:
        env["GIT_COMMITTER_DATE"] = env["GIT_AUTHOR_DATE"] = f"{ts} +0000"
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True, env=env).stdout


def _commit(repo: Path, files: list[str], ts: int) -> str:
    for f in files:
        p = repo / f
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(p.read_text() + "x\n" if p.exists() else "x\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "c", ts=ts)
    return _git(repo, "rev-parse", "HEAD").strip()


def make_repo(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    """Commits (day offsets from T0): A+B on day 1, 2 and 3; A+C on day 2; A+B on day 10 (the 'future')."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    sha = {
        "d1": _commit(repo, ["src/A.py", "src/B.py"], T0 + 1 * DAY),
        "d2": _commit(repo, ["src/A.py", "src/B.py"], T0 + 2 * DAY),
        "d2c": _commit(repo, ["src/A.py", "src/C.py"], T0 + 2 * DAY + 60),
        "d3": _commit(repo, ["src/A.py", "src/B.py"], T0 + 3 * DAY),
        "d10": _commit(repo, ["src/A.py", "src/B.py"], T0 + 10 * DAY),
    }
    return repo, sha


def history(tmp_path: Path, **kw) -> tuple[RepoHistory, dict[str, str]]:
    repo, sha = make_repo(tmp_path)
    commits = read_history(repo, "HEAD", T0, T0 + 30 * DAY)
    return RepoHistory(commits, **kw), sha


def test_read_history_returns_commits_sorted_with_their_files(tmp_path) -> None:
    h, sha = history(tmp_path)
    assert [c.sha for c in h.commits] == [sha[k] for k in ("d1", "d2", "d2c", "d3", "d10")]
    assert h.commits[2].files == ("src/A.py", "src/C.py")
    assert h.commits[0].ts == T0 + DAY


def test_partners_use_only_commits_strictly_before_the_cutoff(tmp_path) -> None:
    h, _ = history(tmp_path)
    # cutoff = day 4: commits d1,d2,d2c,d3 are visible; d10 is not.
    # A: 4 commits. B: support 3 (conf 3/4 = 0.75), C: support 1 (< min_support 2, dropped).
    [b] = h.partners("src/A.py", T0 + 4 * DAY)
    assert (b.path, b.support, b.confidence) == ("src/B.py", 3, 0.75)
    # cutoff after d10 sees it: support 4 of 5.
    [b] = h.partners("src/A.py", T0 + 11 * DAY)
    assert (b.support, b.confidence) == (4, 0.8)


def test_a_commit_exactly_at_the_cutoff_is_invisible(tmp_path) -> None:
    h, sha = history(tmp_path)
    assert [c.sha for c in h.commits_touching("src/A.py", T0 + 3 * DAY)] == [sha["d1"], sha["d2"], sha["d2c"]]
    assert sha["d3"] in [c.sha for c in h.commits_touching("src/A.py", T0 + 3 * DAY + 1)]


def test_the_instances_own_head_commit_can_be_excluded(tmp_path) -> None:
    h, sha = history(tmp_path)
    [b] = h.partners("src/A.py", T0 + 4 * DAY, exclude_sha=sha["d3"])
    assert (b.support, b.confidence) == (2, 2 / 3)  # A is in 3 remaining commits; B in 2
    assert sha["d3"] not in [c.sha for c in h.commits_touching("src/A.py", T0 + 4 * DAY, exclude_sha=sha["d3"])]


def test_window_drops_commits_older_than_window_days(tmp_path) -> None:
    h, _ = history(tmp_path, window_days=2)
    # cutoff day 4, window [day 2, day 4): d2, d2c, d3 -> A=3, B support 2 (d2, d3)
    [b] = h.partners("src/A.py", T0 + 4 * DAY)
    assert (b.support, b.confidence) == (2, 2 / 3)


def test_pairs_are_one_sided_unless_both_directions_is_requested(tmp_path) -> None:
    h, _ = history(tmp_path)
    # B < ... : B's later-sorting partners: none (A and C sort earlier... "src/A.py" < "src/B.py")
    assert h.partners("src/B.py", T0 + 4 * DAY) == []
    [a] = h.partners("src/B.py", T0 + 4 * DAY, both_directions=True)
    assert (a.path, a.support, a.confidence) == ("src/A.py", 3, 1.0)


def test_ranking_is_confidence_then_support_then_path(tmp_path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    for i in range(2):
        _commit(repo, ["a.py", "b.py", "c.py"], T0 + (i + 1) * DAY)
    _commit(repo, ["a.py", "c.py", "d.py"], T0 + 3 * DAY)
    _commit(repo, ["a.py", "d.py"], T0 + 4 * DAY)
    h = RepoHistory(read_history(repo, "HEAD", T0, T0 + 30 * DAY))
    got = [(p.path, p.support, p.confidence) for p in h.partners("a.py", T0 + 9 * DAY)]
    # a in 4 commits: b 2/4, c 3/4, d 2/4 -> c first, then b before d on the path tie-break
    assert got == [("c.py", 3, 0.75), ("b.py", 2, 0.5), ("d.py", 2, 0.5)]


def test_oversize_and_merge_commits_are_skipped(tmp_path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _commit(repo, ["a.py", "b.py"], T0 + DAY)
    big = _commit(repo, [f"bulk/f{i}.py" for i in range(51)] + ["a.py"], T0 + 2 * DAY)
    _git(repo, "checkout", "-q", "-b", "side")
    _commit(repo, ["a.py", "b.py"], T0 + 3 * DAY)
    _git(repo, "checkout", "-q", "main")
    _commit(repo, ["m.py"], T0 + 4 * DAY)
    _git(repo, "merge", "-q", "--no-ff", "-m", "merge", "side", ts=T0 + 5 * DAY)
    merge = _git(repo, "rev-parse", "HEAD").strip()
    shas = [c.sha for c in read_history(repo, "HEAD", T0, T0 + 30 * DAY)]
    assert big not in shas and merge not in shas
    assert len(shas) == 3  # the first commit, the side commit, m.py
