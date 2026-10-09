"""Thin, explicit git helpers used by every agent (subprocess, no library)."""

from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterator


class GitError(RuntimeError):
    """A git command exited non-zero."""


def git(repo: Path | str, *args: str, check: bool = True) -> str:
    """Run ``git -C repo args`` and return stripped stdout.

    Raises:
        GitError: When ``check`` and the command fails.
    """
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    proc = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, env=env
    )
    if check and proc.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed: {proc.stderr.strip() or proc.stdout.strip()}")
    return proc.stdout.strip()


def head_sha(repo: Path | str, rev: str = "HEAD") -> str:
    """Full SHA of ``rev``."""
    return git(repo, "rev-parse", rev)


def current_branch(repo: Path | str) -> str:
    """Name of the checked-out branch."""
    return git(repo, "rev-parse", "--abbrev-ref", "HEAD")


def is_clean(repo: Path | str) -> bool:
    """True when no tracked file is modified or staged (untracked files are ignored)."""
    return git(repo, "status", "--porcelain", "--untracked-files=no") == ""


def tracked_files(repo: Path | str) -> list[str]:
    """Paths tracked at HEAD, POSIX-style, sorted."""
    out = git(repo, "ls-files")
    return sorted(p for p in out.splitlines() if p)


def changed_files(repo: Path | str, base: str, head: str) -> list[str]:
    """Files changed between the merge base of ``base`` and ``head``, and ``head``."""
    out = git(repo, "diff", "--name-only", f"{base}...{head}")
    return sorted(p for p in out.splitlines() if p)


def diff_text(repo: Path | str, base: str, head: str, max_chars: int = 60000) -> str:
    """Unified diff ``base...head``, truncated to ``max_chars``."""
    return git(repo, "diff", f"{base}...{head}")[:max_chars]


def exclude_state_dir(repo: Path | str, name: str = ".blastradius/") -> None:
    """Add the agents' state directory to ``.git/info/exclude`` (idempotent)."""
    git_dir = Path(git(repo, "rev-parse", "--absolute-git-dir"))
    exclude = git_dir / "info" / "exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    lines = exclude.read_text(encoding="utf-8").splitlines() if exclude.exists() else []
    if name not in lines:
        exclude.write_text("\n".join([*lines, name]) + "\n", encoding="utf-8")


def is_ancestor(repo: Path | str, commit: str, branch: str) -> bool:
    """True when ``commit`` is reachable from ``branch``."""
    return subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", commit, branch],
        capture_output=True,
    ).returncode == 0


@contextlib.contextmanager
def worktree(repo: Path | str, rev: str) -> Iterator[Path]:
    """Detached, throw-away worktree of ``rev``; removed on exit."""
    tmp = Path(tempfile.mkdtemp(prefix="br-agent-wt-"))
    path = tmp / "tree"
    git(repo, "worktree", "add", "--detach", str(path), rev)
    try:
        yield path
    finally:
        git(repo, "worktree", "remove", "--force", str(path), check=False)
        shutil.rmtree(tmp, ignore_errors=True)
