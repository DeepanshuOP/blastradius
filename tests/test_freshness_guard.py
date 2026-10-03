"""Tests for the interim-artifact freshness guard.

Per CLAUDE.md rule 3 the pair under test is a REAL checked-in fixture pair --
`tests/fixtures/sample_frame_repos.csv` and
`tests/fixtures/sample_frame_attrition_stage.csv`, both real pipeline CSVs --
copied into `tmp_path` so the test can set their mtimes without mutating
anything checked in. The guard reads mtimes only, so real content is what makes
the fixture real; no file here is fabricated or empty.

Regression target: DECISIONS.md D-49. `outcomes.parquet` predated
`parsed_outcomes.parquet`, one of its own inputs, and nothing complained.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil

import pytest

from analysis.check_freshness import (
    DERIVATIONS,
    find_stale,
    format_report,
)

REAL_FIXTURES = Path(__file__).parent / "fixtures"
REAL_INPUT = REAL_FIXTURES / "sample_frame_repos.csv"
REAL_ARTIFACT = REAL_FIXTURES / "sample_frame_attrition_stage.csv"

ARTIFACT = "derived.csv"
INPUT = "source.csv"
PAIR: dict[str, tuple[str, ...]] = {ARTIFACT: (INPUT,)}


def _build_pair(root: Path, artifact_mtime: float, input_mtime: float) -> None:
    """Copy the real fixture pair into `root` and set both mtimes.

    Args:
        root: Directory to place the pair in.
        artifact_mtime: Epoch seconds to stamp on the derived artifact.
        input_mtime: Epoch seconds to stamp on the input.
    """
    shutil.copyfile(REAL_ARTIFACT, root / ARTIFACT)
    shutil.copyfile(REAL_INPUT, root / INPUT)
    os.utime(root / ARTIFACT, (artifact_mtime, artifact_mtime))
    os.utime(root / INPUT, (input_mtime, input_mtime))


def test_the_real_fixture_pair_exists_and_is_non_empty():
    """Guard the guard: the fixtures this module relies on are real files."""
    for path in (REAL_INPUT, REAL_ARTIFACT):
        assert path.is_file(), path
        assert path.stat().st_size > 0, path


def test_artifact_older_than_its_input_is_stale(tmp_path):
    """The D-49 shape: derived artifact behind its input is reported."""
    _build_pair(tmp_path, artifact_mtime=1_000_000.0, input_mtime=1_000_600.0)

    findings, skipped = find_stale(tmp_path, PAIR)

    assert not skipped
    assert len(findings) == 1
    finding = findings[0]
    assert finding.artifact == ARTIFACT
    assert finding.input_name == INPUT
    assert finding.lag_seconds == pytest.approx(600.0)


def test_artifact_newer_than_its_input_is_fresh(tmp_path):
    """The correct dependency order reports nothing."""
    _build_pair(tmp_path, artifact_mtime=1_000_600.0, input_mtime=1_000_000.0)

    findings, skipped = find_stale(tmp_path, PAIR)

    assert findings == []
    assert not skipped


def test_equal_mtimes_are_fresh(tmp_path):
    """Equal timestamps mean unresolvable gap, not a stale artifact."""
    _build_pair(tmp_path, artifact_mtime=1_000_000.0, input_mtime=1_000_000.0)

    findings, _ = find_stale(tmp_path, PAIR)

    assert findings == []


def test_absent_paths_are_skipped_not_reported_stale(tmp_path):
    """A missing artifact or input is skipped, with the reason named."""
    findings, skipped = find_stale(tmp_path, PAIR)
    assert findings == []
    assert skipped == [f"{ARTIFACT} (artifact absent)"]

    shutil.copyfile(REAL_ARTIFACT, tmp_path / ARTIFACT)
    findings, skipped = find_stale(tmp_path, PAIR)
    assert findings == []
    assert skipped == [f"{ARTIFACT} <- {INPUT} (input absent)"]


def test_report_names_both_paths_and_the_decision(tmp_path):
    """The error an operator sees names the files, the lag and the fix."""
    _build_pair(tmp_path, artifact_mtime=1_000_000.0, input_mtime=1_000_600.0)
    findings, _ = find_stale(tmp_path, PAIR)

    report = format_report(findings, tmp_path)

    assert str(tmp_path / ARTIFACT) in report
    assert str(tmp_path / INPUT) in report
    assert "D-49" in report
    assert "600.0 s" in report
    assert "corpus_parse.py" in report
    assert "fault_revealing.py" in report


def test_shipped_derivations_match_the_pipeline_source():
    """The guarded edges are the ones the pipeline actually reads.

    Pinned so that adding a `pd.read_parquet` to the labels step without
    extending the guard shows up here as a deliberate choice.
    """
    assert DERIVATIONS == {
        "base_outcomes.parquet": ("base_resolution_new.parquet",),
        "outcomes.parquet": (
            "base_resolution_new.parquet",
            "instances_raw.parquet",
            "parsed_outcomes.parquet",
            "base_outcomes.parquet",
        ),
    }


def test_labels_step_reads_exactly_the_guarded_inputs():
    """`src/label/fault_revealing.py` reads no interim parquet the guard omits."""
    import re

    source = Path("src/label/fault_revealing.py").read_text()
    read = set(re.findall(r"read_parquet\('data/interim/([^']+)'\)", source))

    assert read == set(DERIVATIONS["outcomes.parquet"]), (
        "labels-step inputs drifted from DERIVATIONS['outcomes.parquet']; "
        f"source reads {sorted(read)}"
    )
