"""BlastRadius — Held-Out Fixture Integrity Guard Tests.

Per ROADMAP §25.3, §26.1 and AGENTS.md.
Guarantees:
- tests/fixtures/holdout/ contains exactly 20 .txt files plus EXPECTED.md.
- EXPECTED.md parses to exactly 4 hand-labelled test identifiers.
- ZERO job_id overlap between holdout and tests/fixtures/logs/.
- Deterministic seed constant in analysis/select_holdout.py is unchanged.

CRITICAL: Never score parsers against holdout fixtures in any test suite.
"""

from __future__ import annotations

from pathlib import Path

from analysis.expected_audit import parse_expected_counts
from analysis.select_holdout import SEED

HOLDOUT_DIR = Path("tests/fixtures/holdout")
LOGS_DIR = Path("tests/fixtures/logs")
EXPECTED_TEST_IDENTIFIER_COUNT = 30
EXPECTED_TXT_FILE_COUNT = 20
EXPECTED_SEED = 20260826


def test_holdout_file_counts() -> None:
    """Holdout directory must contain exactly 20 .txt logs plus EXPECTED.md."""
    assert HOLDOUT_DIR.exists(), f"Holdout directory {HOLDOUT_DIR} does not exist"

    txt_files = sorted(HOLDOUT_DIR.glob("*.txt"))
    assert len(txt_files) == EXPECTED_TXT_FILE_COUNT, (
        f"Expected {EXPECTED_TXT_FILE_COUNT} .txt files in {HOLDOUT_DIR}, found {len(txt_files)}"
    )

    all_files = sorted([p.name for p in HOLDOUT_DIR.iterdir() if p.is_file()])
    expected_filenames = sorted([p.name for p in txt_files] + ["EXPECTED.md"])
    assert all_files == expected_filenames, (
        f"Unexpected file inventory in {HOLDOUT_DIR}: {set(all_files) ^ set(expected_filenames)}"
    )


def test_holdout_expected_identifier_count() -> None:
    """Holdout EXPECTED.md must parse to the literal hand-labelled identifier count (4)."""
    expected_md = HOLDOUT_DIR / "EXPECTED.md"
    assert expected_md.exists(), f"{expected_md} does not exist"

    counts = parse_expected_counts(expected_md)
    assert len(counts) == EXPECTED_TXT_FILE_COUNT, (
        f"Expected {EXPECTED_TXT_FILE_COUNT} fixture entries in EXPECTED.md, got {len(counts)}"
    )

    total_identifiers = sum(meta["expected_count"] for meta in counts.values())
    assert total_identifiers == EXPECTED_TEST_IDENTIFIER_COUNT, (
        f"Expected exactly {EXPECTED_TEST_IDENTIFIER_COUNT} hand-labelled test identifiers, "
        f"got {total_identifiers}. Any silent edits to EXPECTED.md break this guard."
    )


def test_holdout_zero_overlap_with_original_corpus() -> None:
    """ZERO job_id overlap between tests/fixtures/holdout/ and tests/fixtures/logs/."""
    holdout_job_ids = {p.stem.split("__")[2] for p in HOLDOUT_DIR.glob("*.txt")}
    logs_job_ids = {p.stem.split("__")[2] for p in LOGS_DIR.glob("*.txt")}

    overlap = holdout_job_ids & logs_job_ids
    assert not overlap, f"Forbidden job_id overlap detected between holdout and logs: {overlap}"


def test_holdout_seed_constant_unchanged() -> None:
    """The selection seed constant in select_holdout.py must be unchanged."""
    assert SEED == EXPECTED_SEED, f"SEED constant in select_holdout.py changed: {SEED} != {EXPECTED_SEED}"
