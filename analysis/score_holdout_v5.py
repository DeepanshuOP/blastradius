"""Score Holdout v5 exactly once, from hand labels only.

Contract
--------
- **Refuses to run while any answer cell is empty.** A partially filled
  worksheet is not ground truth, and scoring one would burn the corpus for a
  measurement nobody can defend.
- **Refuses to run twice.** The first successful run writes a sealed marker
  (`SEAL_PATH`) recording the worksheet digest and the figures. Any later run
  exits non-zero. D-37: a holdout corpus is scored exactly once.
- **Never derives ground truth.** Expected Class is read from the worksheet as
  the operator wrote it. It is never inferred from the identifier list -- doing
  that is what voided the 2026-09-04 scoring under D-38.

The parser side is, of course, computed: the comparison is the operator's hand
labels against `src.parse.dispatch`. Precision is reported per parser as n/d and
never as a bare percentage.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from src.parse.dispatch import dispatch_parse_log_with_stats
from src.parse.test_ids import normalize_test_id

__all__ = ["HandLabel", "parse_worksheet", "score", "SEAL_PATH"]

WORKSHEET = Path("docs/phase/029-holdout-v5-worksheet.md")
SEAL_PATH = Path("docs/phase/029-holdout-v5-SEALED.json")
FIXTURE_DIR = Path("tests/fixtures/holdout_v5")

VALID_CLASSES = ("TEST_FAILURE", "NO_TEST_OUTPUT", "TEST_RAN_CLEAN")
ANSWER_FIELDS = (
    "Build Tool",
    "Expected Class",
    "Expected Identifier Count",
    "Expected Identifiers",
    "Confidence",
)

_SECTION_RE = re.compile(r"^## (\d+)\. `([^`]+)`\s*$", re.MULTILINE)


@dataclass
class HandLabel:
    """One fixture's hand-written ground truth.

    Attributes:
        index: 1-based worksheet section index.
        fixture: Fixture filename.
        build_tool: Harness, as the operator identified it.
        expected_class: One of VALID_CLASSES, as the operator judged it.
        expected_count: Identifier count the operator wrote.
        expected_ids: Canonical identifiers the operator listed.
        confidence: CERTAIN or UNCERTAIN.
    """

    index: int
    fixture: str
    build_tool: str
    expected_class: str
    expected_count: str
    expected_ids: list[str] = field(default_factory=list)
    confidence: str = ""


def _field_value(block: str, label: str) -> str:
    """Pull one answer field's text out of a section block.

    Args:
        block: The section's markdown.
        label: Field label, e.g. "Expected Class".

    Returns:
        The trimmed value, or "" when the field is empty or absent.
    """
    match = re.search(
        rf"^- \*\*{re.escape(label)}:\*\*(.*)$", block, re.MULTILINE
    )
    if match is None:
        return ""
    return match.group(1).strip().strip("`")


def parse_worksheet(path: Path) -> tuple[list[HandLabel], list[str]]:
    """Parse the worksheet into hand labels, reporting empty cells.

    Args:
        path: Worksheet markdown path.

    Returns:
        A pair of (labels parsed, human-readable complaints about empty or
        invalid cells). A non-empty complaint list means the worksheet is not
        ready and must not be scored.
    """
    text = path.read_text(encoding="utf-8")
    bounds = [(m.start(), int(m.group(1)), m.group(2)) for m in _SECTION_RE.finditer(text)]
    labels: list[HandLabel] = []
    problems: list[str] = []

    for position, (start, index, name) in enumerate(bounds):
        end = bounds[position + 1][0] if position + 1 < len(bounds) else len(text)
        block = text[start:end]

        values = {label: _field_value(block, label) for label in ANSWER_FIELDS}
        for label, value in values.items():
            if not value:
                problems.append(f"section {index} ({name}): '{label}' is empty")

        cls = values["Expected Class"].upper()
        if cls and cls not in VALID_CLASSES:
            problems.append(
                f"section {index} ({name}): Expected Class {cls!r} is not one of "
                f"{', '.join(VALID_CLASSES)}"
            )

        raw_ids = values["Expected Identifiers"]
        ids: list[str] = []
        if raw_ids and raw_ids.upper() != "NO_TEST_OUTCOMES":
            ids = [i.strip().strip("`") for i in raw_ids.split(",") if i.strip()]

        labels.append(
            HandLabel(
                index=index,
                fixture=name,
                build_tool=values["Build Tool"],
                expected_class=cls,
                expected_count=values["Expected Identifier Count"],
                expected_ids=ids,
                confidence=values["Confidence"].upper(),
            )
        )

    return labels, problems


def _emitted_ids(body: str, fixture: str) -> tuple[set[str], str]:
    """Run the dispatcher over a fixture and canonicalise what it emits.

    Args:
        body: Raw log text.
        fixture: Fixture filename, used as the job id for the records.

    Returns:
        A pair of (canonical ids emitted, format the dispatcher detected).
    """
    outcomes, stats = dispatch_parse_log_with_stats(
        body, run_id="holdout_v5", job_id=fixture, repo="holdout", head_sha=None
    )
    ids: set[str] = set()
    for outcome in outcomes:
        normalized = normalize_test_id(outcome.test_id)
        if normalized is not None:
            ids.add(normalized.canonical)
    return ids, stats.format_detected


def score(labels: list[HandLabel], fixture_dir: Path) -> dict:
    """Compare parser output with the hand labels, per parser.

    Args:
        labels: Hand labels from the worksheet.
        fixture_dir: Directory of checked-in fixtures.

    Returns:
        A results dict carrying per-parser precision numerators and
        denominators, plus per-parser classification agreement.
    """
    per_parser: dict[str, dict[str, int]] = {}

    for label in labels:
        path = fixture_dir / label.fixture
        emitted, detected = _emitted_ids(path.read_text(encoding="utf-8", errors="replace"), label.fixture)
        parser = label.build_tool.strip().lower() or "unknown"
        bucket = per_parser.setdefault(
            parser,
            {
                "true_positives": 0,
                "emitted": 0,
                "expected": 0,
                "fixtures": 0,
                "class_agree": 0,
            },
        )
        expected = set(label.expected_ids)
        bucket["true_positives"] += len(emitted & expected)
        bucket["emitted"] += len(emitted)
        bucket["expected"] += len(expected)
        bucket["fixtures"] += 1

        parser_class = "TEST_FAILURE" if emitted else detected_to_class(detected)
        if parser_class == label.expected_class:
            bucket["class_agree"] += 1

    return {"per_parser": per_parser}


def detected_to_class(detected: str) -> str:
    """Map a dispatcher format verdict to a classification bucket.

    This is the PARSER's side of the comparison, never the ground truth.

    Args:
        detected: Format string the dispatcher reported.

    Returns:
        `NO_TEST_OUTPUT` when nothing was detected, else `TEST_RAN_CLEAN`.
    """
    return "NO_TEST_OUTPUT" if detected in ("", "unknown", "none") else "TEST_RAN_CLEAN"


def main() -> None:
    """Score once, or refuse with a reason."""
    parser = argparse.ArgumentParser(description="Score Holdout v5 exactly once")
    parser.add_argument("--worksheet", type=Path, default=WORKSHEET)
    parser.add_argument("--fixture-dir", type=Path, default=FIXTURE_DIR)
    parser.add_argument("--seal", type=Path, default=SEAL_PATH)
    args = parser.parse_args()

    if args.seal.exists():
        seal = json.loads(args.seal.read_text())
        print(
            "REFUSING: Holdout v5 has already been scored.\n"
            f"  sealed at: {seal.get('sealed_at')}\n"
            f"  worksheet digest: {seal.get('worksheet_sha256')}\n"
            f"  seal: {args.seal}\n"
            "D-37: a holdout corpus is scored exactly once. Superseding this "
            "figure requires a NEW corpus under a new seed.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    labels, problems = parse_worksheet(args.worksheet)
    if problems:
        print(
            f"REFUSING: the worksheet is not fully filled "
            f"({len(problems)} problems across {len(labels)} sections).\n"
            "Scoring a partial worksheet would consume the corpus for a figure "
            "nobody can defend (D-37).\n",
            file=sys.stderr,
        )
        for problem in problems[:20]:
            print(f"  - {problem}", file=sys.stderr)
        if len(problems) > 20:
            print(f"  ... and {len(problems) - 20} more", file=sys.stderr)
        raise SystemExit(1)

    results = score(labels, args.fixture_dir)

    print("Holdout v5 precision, per parser (n/d, never a bare percentage):")
    for name in sorted(results["per_parser"]):
        bucket = results["per_parser"][name]
        print(
            f"  {name}: precision {bucket['true_positives']}/{bucket['emitted']}"
            f"   recall {bucket['true_positives']}/{bucket['expected']}"
            f"   class agreement {bucket['class_agree']}/{bucket['fixtures']}"
        )

    digest = hashlib.sha256(args.worksheet.read_bytes()).hexdigest()
    args.seal.write_text(
        json.dumps(
            {
                "sealed_at": datetime.now(timezone.utc).isoformat(),
                "worksheet": args.worksheet.as_posix(),
                "worksheet_sha256": digest,
                "sections": len(labels),
                "results": results,
                "governing": "D-37 (scored once), D-38 (hand labels only)",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\nSealed: {args.seal}. Holdout v5 is now closed and cannot be re-scored.")


if __name__ == "__main__":
    main()
