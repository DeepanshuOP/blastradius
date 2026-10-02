"""Shared fixtures for the graph-layer tests.

Every graph test runs against the real checked-in tree at
`tests/fixtures/graph/minirepo/` — real Java and Python sources with a real
syntax error, a real build-output directory and a real vendored directory — not
against mocks. The only thing constructed at test time is the git history, which
cannot be checked in as a nested repository.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

MINIREPO = Path(__file__).resolve().parents[1] / "fixtures" / "graph" / "minirepo"

_GIT_ENV = {
    "GIT_AUTHOR_NAME": "BlastRadius Fixture",
    "GIT_AUTHOR_EMAIL": "fixture@blastradius.invalid",
    "GIT_COMMITTER_NAME": "BlastRadius Fixture",
    "GIT_COMMITTER_EMAIL": "fixture@blastradius.invalid",
    # Fixed timestamps keep the commit SHAs identical on every run, so a failure
    # message naming a SHA means the same thing on every machine.
    "GIT_AUTHOR_DATE": "2026-01-01T00:00:00+00:00",
    "GIT_COMMITTER_DATE": "2026-01-01T00:00:00+00:00",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_SYSTEM": "/dev/null",
    "GIT_TERMINAL_PROMPT": "0",
}


def git(repo: Path, *args: str) -> str:
    """Run git in `repo` with a pinned identity and return stdout.

    Args:
        repo: Repository directory.
        *args: Arguments after `git`.

    Returns:
        Captured stdout.
    """
    import os

    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, **_GIT_ENV},
    )
    return proc.stdout


@pytest.fixture
def minirepo_clone(tmp_path: Path) -> Path:
    """A git repo whose single commit is the checked-in minirepo fixture.

    Returns:
        The repository root. `git("rev-parse", "HEAD")` gives the commit.
    """
    repo = tmp_path / "clone"
    shutil.copytree(MINIREPO, repo)
    git(repo, "init", "--quiet", "--initial-branch=main")
    git(repo, "add", "--all")
    git(repo, "commit", "--quiet", "-m", "fixture")
    return repo


@pytest.fixture
def minirepo_sha(minirepo_clone: Path) -> str:
    """The commit SHA of `minirepo_clone`'s single commit."""
    return git(minirepo_clone, "rev-parse", "HEAD").strip()
