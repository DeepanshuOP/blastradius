"""Tests for the Holdout v5 worksheet generator and its single-shot scorer.

The fixtures are real: the two worksheet files under
`tests/fixtures/holdout_v5_scorer/` are hand-written with hand-chosen expected
values, and they name real logs from `tests/fixtures/holdout_v5/`. Nothing here
is a mock (CLAUDE.md rule 3).

What matters most is the pair of refusals. The scorer guards a corpus that can
only be measured once (D-37), so "refuses a partial worksheet" and "refuses a
second run" are the behaviours under test, not incidental error handling.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from analysis.build_holdout_v5_worksheet import EXCERPT_LINES, section_for
from analysis.score_holdout_v5 import ANSWER_FIELDS, parse_worksheet

FIXTURES = Path(__file__).parent / "fixtures" / "holdout_v5_scorer"
FILLED = FIXTURES / "filled.md"
PARTIAL = FIXTURES / "partial.md"
WORKSHEET = Path("docs/phase/029-holdout-v5-worksheet.md")
FILLED_SPACES = FIXTURES / "filled_spaces.md"
V5_DIR = Path("tests/fixtures/holdout_v5")


def test_generated_worksheet_has_every_answer_field_empty():
    """The shipped worksheet must carry no pre-filled value (D-38)."""
    text = WORKSHEET.read_text(encoding="utf-8")
    for field in ANSWER_FIELDS:
        filled = [
            line
            for line in text.splitlines()
            if line.startswith(f"- **{field}:**") and line.split(":**", 1)[1].strip()
        ]
        assert not filled, f"{field} is pre-filled on {len(filled)} lines: {filled[:3]}"


def test_generated_worksheet_covers_every_fixture():
    """One section per checked-in v5 fixture, no more and no fewer."""
    text = WORKSHEET.read_text(encoding="utf-8")
    fixtures = sorted(p.name for p in V5_DIR.glob("*.txt"))
    assert fixtures, "no v5 fixtures on disk"
    for name in fixtures:
        assert f"`{name}`" in text, f"{name} missing from the worksheet"


def test_excerpt_is_the_content_blind_tail(tmp_path):
    """The excerpt is the final N lines, chosen without reading content.

    If this ever became a content search (grep for FAILED, say), the worksheet
    would be machine-assisted and the scoring void under D-38.
    """
    log = tmp_path / "repo__owner__1.txt"
    body = "\n".join(f"line {i}" for i in range(1, EXCERPT_LINES + 51))
    log.write_text(body, encoding="utf-8")

    section = section_for(1, log)

    assert f"line {EXCERPT_LINES + 50}" in section
    assert "line 50" not in section.split("```text", 1)[1].split("```", 1)[0]


def test_parse_worksheet_reports_every_empty_cell():
    """A blank worksheet yields one complaint per empty field per section."""
    labels, problems = parse_worksheet(WORKSHEET)
    assert len(labels) == len(sorted(V5_DIR.glob("*.txt")))
    assert len(problems) == len(labels) * len(ANSWER_FIELDS)


def test_parse_worksheet_accepts_a_fully_filled_sheet():
    """The hand-filled fixture parses with no complaints."""
    labels, problems = parse_worksheet(FILLED)

    assert problems == []
    assert len(labels) == 2
    first, second = labels
    assert first.build_tool == "gradle"
    assert first.expected_class == "TEST_FAILURE"
    assert first.expected_ids == [
        "com.example.AlphaTest#one",
        "com.example.BetaTest#two",
    ]
    assert second.expected_class == "NO_TEST_OUTPUT"
    assert second.expected_ids == []
    assert second.confidence == "CERTAIN"


def test_identifiers_split_on_commas_only_so_spaces_survive():
    """JUnit display names contain spaces; only commas separate identifiers."""
    labels, problems = parse_worksheet(FILLED_SPACES)

    assert problems == []
    assert labels[0].expected_ids == [
        "com.example.AlphaTest#rejects an empty file",
        "com.example.BetaTest#two",
        "com.example.GammaTest#handles two words",
    ]


def test_one_empty_cell_is_enough_to_refuse():
    """A single blank field blocks scoring."""
    labels, problems = parse_worksheet(PARTIAL)

    assert len(labels) == 2
    assert len(problems) == 1
    assert "Confidence" in problems[0]


def test_expected_class_is_read_not_derived():
    """Ground truth comes from the sheet even when it contradicts the count.

    D-38 voided the previous scoring precisely because Expected Class was
    derived from the identifier list. A sheet claiming TEST_RAN_CLEAN while
    listing two identifiers must be reported as the operator wrote it.
    """
    sheet = FIXTURES / "contradictory.md"
    sheet.write_text(
        FILLED.read_text(encoding="utf-8").replace(
            "- **Expected Class:** TEST_FAILURE",
            "- **Expected Class:** TEST_RAN_CLEAN",
            1,
        ),
        encoding="utf-8",
    )
    try:
        labels, problems = parse_worksheet(sheet)
        assert problems == []
        assert labels[0].expected_class == "TEST_RAN_CLEAN"
        assert len(labels[0].expected_ids) == 2
    finally:
        sheet.unlink()


def test_scorer_refuses_the_blank_shipped_worksheet_and_writes_no_seal(tmp_path):
    """End to end: the real blank worksheet is refused, nothing is sealed."""
    seal = tmp_path / "seal.json"
    result = subprocess.run(
        [
            sys.executable,
            "analysis/score_holdout_v5.py",
            "--worksheet",
            str(WORKSHEET),
            "--seal",
            str(seal),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "REFUSING" in result.stderr
    assert not seal.exists(), "a refused run must not seal the corpus"


def test_scorer_refuses_a_second_run(tmp_path):
    """An existing seal blocks scoring, whatever the worksheet says."""
    seal = tmp_path / "seal.json"
    seal.write_text(
        json.dumps({"sealed_at": "2026-10-03T00:00:00+00:00", "worksheet_sha256": "x"}),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "analysis/score_holdout_v5.py",
            "--worksheet",
            str(FILLED),
            "--seal",
            str(seal),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "already been scored" in result.stderr
    assert "D-37" in result.stderr
