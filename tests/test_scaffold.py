"""Smoke test asserting the repository skeleton matches ROADMAP §33."""

import sys
from pathlib import Path

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


def test_no_env_file() -> None:
    assert (REPO_ROOT / ".env").exists() is False
