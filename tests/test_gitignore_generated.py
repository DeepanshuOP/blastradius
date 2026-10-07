"""`paper/generated/*.md` and `*.pdf` are tracked; other files there are not."""

from __future__ import annotations

import subprocess

import pytest


def ignored(path: str) -> bool:
    return subprocess.run(["git", "check-ignore", "-q", path]).returncode == 0


@pytest.mark.parametrize("path", ["paper/generated/rq1.md", "paper/generated/leakage_audit.md",
                                  "paper/generated/fig1_applicability.pdf"])
def test_generated_markdown_and_pdf_are_not_ignored(path: str) -> None:
    assert not ignored(path)


@pytest.mark.parametrize("path", ["paper/generated/scratch.csv", "paper/generated/table.parquet",
                                  "paper/generated/notes.txt"])
def test_other_generated_files_stay_ignored(path: str) -> None:
    assert ignored(path)
