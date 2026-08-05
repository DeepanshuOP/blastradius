"""Smoke test asserting the repository skeleton matches ROADMAP §33."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

EXPECTED_DIRS = [
    "src/harvest",
    "src/parse",
    "src/label",
    "src/graph",
    "src/features",
    "src/models",
    "src/eval",
    "src/gold",
    "src/api",
    "analysis",
    "tests/fixtures",
    "data/raw",
    "data/interim",
    "data/processed",
    "data/gold",
    "data/graphs",
    "docker",
    "paper",
    "vendor",
]


def test_python_version() -> None:
    assert sys.version_info[:2] == (3, 11)


def test_layout_exists() -> None:
    for rel_dir in EXPECTED_DIRS:
        assert (REPO_ROOT / rel_dir).is_dir(), f"missing directory: {rel_dir}"


def test_env_file_is_gitignored_and_untracked() -> None:
    """`.env` legitimately exists on disk and holds a real credential
    (GITHUB_PAT_1) — the guarantee that actually matters is that git never
    tracks it, not that the file itself is absent. Shells out to the real
    `git check-ignore` / `git ls-files` rather than hand-parsing
    `.gitignore`: gitignore pattern semantics (negation, anchoring,
    directory-only patterns) are exactly what git itself implements, and
    reimplementing that matching logic in Python risks silently drifting
    from what git actually does. If git isn't available, skip explicitly —
    a passing test here must mean git was actually asked, not that the
    check was quietly bypassed.
    """
    if shutil.which("git") is None:
        pytest.skip("git not available on PATH; cannot verify .env is ignored")

    ignore_result = subprocess.run(
        ["git", "check-ignore", ".env"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert ignore_result.returncode == 0, (
        ".env is not matched by .gitignore "
        f"(git check-ignore exit {ignore_result.returncode}): {ignore_result.stderr}"
    )

    tracked_result = subprocess.run(
        ["git", "ls-files", ".env"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert tracked_result.stdout.strip() == "", ".env is tracked by git"
