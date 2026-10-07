"""Smoke and unit tests for `analysis/demo_walkthrough.py`.

The pure helpers run against a real checked-in dev log (never a holdout log).
The end-to-end smoke test runs the real script against `data/interim` and is
skipped where that data is absent; it asserts the demo is deterministic,
offline-safe and read-only, not any particular instance.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from analysis.demo_walkthrough import (
    holdout_job_ids,
    log_excerpt,
    mini_corpus_repos,
    short_name,
)

ROOT = Path(__file__).resolve().parent.parent
DEV_LOG = ROOT / "tests/fixtures/logs/apache__dolphinscheduler__083801509824.txt"
TEST_ID = (
    "org.apache.dolphinscheduler.api.test.cases.tasks.EmrServerlessTaskAPITest"
    "#testEmrServerlessSuccessWorkflowInstance"
)


def test_short_name_strips_class_and_params() -> None:
    assert short_name(TEST_ID) == "testEmrServerlessSuccessWorkflowInstance"
    assert short_name("tests/ops/test_x.py::test_chunk[a-1]") == "test_chunk"


def test_log_excerpt_leads_with_the_failure_line_and_is_capped() -> None:
    lines = log_excerpt(DEV_LOG.read_text(encoding="utf-8", errors="replace"), TEST_ID)
    assert 1 <= len(lines) <= 10
    assert "<<< FAILURE" in lines[0]
    assert all("testEmrServerlessSuccessWorkflowInstance" in ln for ln in lines)
    assert all(len(ln) <= 200 for ln in lines)


def test_mini_corpus_repos_come_from_the_doc() -> None:
    assert mini_corpus_repos() == [
        "Stirling-Tools/Stirling-PDF",
        "fla-org/flash-linear-attention",
        "spiculedata/saiku",
    ]


def test_holdout_ids_cover_v5_and_exclude_dev_fixtures() -> None:
    ids, _ = holdout_job_ids()
    v5 = {
        int(p.stem.rsplit("__", 1)[1]) for p in (ROOT / "tests/fixtures/holdout_v5").glob("*.txt")
    }
    dev = {int(p.stem.rsplit("__", 1)[1]) for p in (ROOT / "tests/fixtures/logs").glob("*.txt")}
    assert v5 and v5 <= ids
    assert not dev & ids


@pytest.mark.skipif(
    not (ROOT / "data/interim/outcomes.parquet").exists(), reason="needs data/interim"
)
def test_demo_is_deterministic_and_read_only() -> None:
    watched = sorted((ROOT / "data/interim").glob("*.parquet"))
    before = [p.stat().st_mtime_ns for p in watched]

    def run() -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "analysis/demo_walkthrough.py"],
            capture_output=True, text=True, cwd=ROOT, timeout=60,
        )

    first, second = run(), run()
    assert first.returncode in (0, 2), first.stderr
    assert first.returncode == second.returncode
    assert first.stdout == second.stdout
    assert "SELECTION" in first.stdout
    assert "failure-message classification" in first.stdout
    if first.returncode == 0:
        assert "preference code-level > unknown > timeout > environment" in first.stdout
    if first.returncode == 2:
        assert "NO QUALIFYING INSTANCE" in first.stdout
    assert [p.stat().st_mtime_ns for p in watched] == before
