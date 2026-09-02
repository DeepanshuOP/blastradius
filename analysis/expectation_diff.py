"""BlastRadius — Blind Ground-Truth vs. Parser-Emitted Expectation Diff.

Per docs/phase/021B-blind-worksheet.md and the D-38 blind-scoring ruling (ground truth
must be filled without visibility into the extractor's output, or it anchors to the
extractor's own answer). Joins the blind worksheet (docs/phase/021B-blind-worksheet.md)
against the machine-derived expectation table (docs/phase/021-expectation-table.md) on a
content-derived `row_key` (sha256 of fixture + raw evidence, not a sequential number — the
prior sequential-number join was abandoned after the operator read the diff output for an
unfilled worksheet and saw every NORMALIZED answer next to its row number). This is a
regression fixture, not a scored holdout set — it yields no precision/recall figure, ever.

Leak-proofing (per docs/phase/021C-REPORT.md): for any row whose HAND_EXPECTED is empty,
this script prints ONLY row_key, fixture, and verdict=UNFILLED. NORMALIZED is never
referenced, formatted, or printed on that code path, under any flag.
"""

from __future__ import annotations

import ast
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

WORKSHEET_MD = Path("docs/phase/021B-blind-worksheet.md")
EXPECTATION_TABLE_MD = Path("docs/phase/021-expectation-table.md")

_ROW_HEADER_RE = re.compile(r"^##\s+Row\s+([0-9a-f]{12})\s+—\s+(.+?)\s*$", re.MULTILINE)
_HAND_EXPECTED_RE = re.compile(r"HAND_EXPECTED:(.*)\Z", re.DOTALL)
_TABLE_ROW_RE = re.compile(r"^\|\s*\d+\s*\|.*\|\s*$", re.MULTILINE)
_UNESCAPED_PIPE_RE = re.compile(r"(?<!\\)\|")
_TABLE_CELL_LITERAL_RE = re.compile(
    r"L\d+:\s*((?:'(?:\\.|[^'\\])*')|(?:\"(?:\\.|[^\"\\])*\"))"
)
_FENCED_BLOCK_RE = re.compile(r"```\n(.*?)\n```", re.DOTALL)

_CONTESTED_METHOD_NAMES = {"classMethod", "run", "TestAll", "setup", "init"}


def compute_row_key(fixture: str, lines: list[str]) -> str:
    """First 12 hex chars of sha256(fixture + "\\n" + raw evidence lines joined by "\\n").

    Hashes the RAW bytes of the fixture name and evidence lines, never any display
    transform (e.g. the repr() used to render RAW_LINE cells) of them.
    """
    payload = fixture + "\n" + "\n".join(lines)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


@dataclass
class WorksheetRow:
    """One row of the blind ground-truth worksheet."""

    row_key: str
    fixture: str
    hand_expected: str


@dataclass
class ExpectationRow:
    """One row of the machine-derived expectation table."""

    row_key: str
    fixture: str
    normalized: str


def parse_worksheet(path: Path = WORKSHEET_MD) -> dict[str, WorksheetRow]:
    """Parse docs/phase/021B-blind-worksheet.md into row_key -> WorksheetRow.

    The section's own `row_key` header is cross-checked against a row_key recomputed
    from that section's own displayed evidence (un-repr()'d back to raw bytes); a
    mismatch is treated as corruption, not trusted silently.
    """
    content = path.read_text(encoding="utf-8", errors="replace")
    sections = _ROW_HEADER_RE.split(content)[1:]

    rows: dict[str, WorksheetRow] = {}
    for i in range(0, len(sections), 3):
        header_key = sections[i]
        fixture = sections[i + 1].strip()
        body = sections[i + 2]

        blocks = _FENCED_BLOCK_RE.findall(body)
        lines = [ast.literal_eval(block.strip()) for block in blocks]
        recomputed_key = compute_row_key(fixture, lines)
        if recomputed_key != header_key:
            raise ValueError(
                f"row_key mismatch in worksheet section {header_key!r}: "
                f"header says {header_key!r}, recomputed from its own evidence is "
                f"{recomputed_key!r} (fixture={fixture!r})"
            )

        m = _HAND_EXPECTED_RE.search(body)
        raw = m.group(1).rstrip() if m else ""
        if raw.endswith("---"):
            raw = raw[: -len("---")].rstrip()
        hand_expected = raw.strip()

        rows[header_key] = WorksheetRow(row_key=header_key, fixture=fixture, hand_expected=hand_expected)
    return rows


def parse_expectation_table(path: Path = EXPECTATION_TABLE_MD) -> dict[str, ExpectationRow]:
    """Parse docs/phase/021-expectation-table.md's markdown table into row_key -> ExpectationRow.

    row_key is recomputed from each row's own RAW_LINE cell (un-repr()'d back to raw
    bytes) and fixture, never trusted from a stored value — the table has no row_key
    column, and even if it did, this function would not read it.
    """
    content = path.read_text(encoding="utf-8", errors="replace")

    rows: dict[str, ExpectationRow] = {}
    for line in content.splitlines():
        if not _TABLE_ROW_RE.match(line):
            continue
        cells = [
            c.replace("\\|", "|").strip()
            for c in _UNESCAPED_PIPE_RE.split(line.strip().strip("|"))
        ]
        # Columns: # | fixture | RAW_LINE | PARSER_EMITTED | NORMALIZED | HAND_EXPECTED
        if len(cells) < 6:
            continue
        row_num_str = cells[0].strip()
        if not row_num_str.isdigit():
            continue

        fixture = _strip_backticks(cells[1])
        raw_line_cell = cells[2]
        normalized = _strip_backticks(cells[4])

        literals = _TABLE_CELL_LITERAL_RE.findall(raw_line_cell)
        lines = [ast.literal_eval(lit) for lit in literals]
        row_key = compute_row_key(fixture, lines)

        rows[row_key] = ExpectationRow(row_key=row_key, fixture=fixture, normalized=normalized)
    return rows


def _strip_backticks(cell: str) -> str:
    cell = cell.strip()
    if len(cell) >= 2 and cell.startswith("`") and cell.endswith("`"):
        cell = cell[1:-1]
    return cell


def is_contested(normalized: str) -> bool:
    """Flag NORMALIZED shapes where agreement is weak evidence.

    Contested: a NONE value, a Java class segment with no "." (the D3 bare-class
    defect signature), or a method segment that is a common/generic name likely to
    collide across unrelated classes (classMethod, run, TestAll, setup, init).
    """
    if normalized == "NONE":
        return True
    if "#" in normalized:
        cls_part, method_part = normalized.split("#", 1)
        if "." not in cls_part:
            return True
        return method_part in _CONTESTED_METHOD_NAMES
    if "::" in normalized:
        method_part = normalized.rsplit("::", 1)[-1]
        return method_part in _CONTESTED_METHOD_NAMES
    return False


def main() -> None:
    """Print the per-row join and totals to stdout."""
    worksheet = parse_worksheet()
    expectation = parse_expectation_table()

    all_keys = sorted(set(worksheet) | set(expectation))

    total = 0
    unfilled = 0
    agree = 0
    disagree = 0
    agree_on_contested = 0

    for row_key in all_keys:
        w = worksheet.get(row_key)
        e = expectation.get(row_key)
        fixture = (w.fixture if w else None) or (e.fixture if e else "UNKNOWN")
        hand_expected = w.hand_expected if w else ""

        total += 1

        if not hand_expected:
            # Leak-proof path: NORMALIZED is never read, formatted, or printed here.
            unfilled += 1
            print(f"row_key={row_key} fixture={fixture} verdict=UNFILLED")
            continue

        normalized = e.normalized if e else ""
        verdict = "AGREE" if hand_expected == normalized else "DISAGREE"
        contested = is_contested(normalized)

        if verdict == "AGREE":
            agree += 1
            if contested:
                agree_on_contested += 1
        else:
            disagree += 1

        marker = " CONTESTED" if contested else ""
        print(
            f"row_key={row_key} fixture={fixture} HAND_EXPECTED={hand_expected!r} "
            f"NORMALIZED={normalized!r} verdict={verdict}{marker}"
        )

    print()
    print(f"UNFILLED: {unfilled} / {total}")
    print(f"AGREE:    {agree} / {total}")
    print(f"DISAGREE: {disagree} / {total}")
    print(f"AGREE-ON-CONTESTED: {agree_on_contested} / {total}")


if __name__ == "__main__":
    sys.exit(main())
