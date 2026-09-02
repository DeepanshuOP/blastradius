"""BlastRadius — Parser regression harness over the Phase 021B fixture corpus.

Per integrity invariant 5 and CLAUDE.md rule 3: every data-touching function is tested
against a REAL checked-in fixture with a hand-written expected value, never a mock. This
module pins the current, observed behaviour of the real parser dispatcher across all 47
rows of the Phase 021B corpus so that any parser fix is a *deliberate* change with a
visible diff, not a silent one.

What this is NOT: a precision measurement. `docs/phase/021B-blind-worksheet.md` records
that its HAND_EXPECTED values were filled by the coding agent, with all 47 parser outputs
in context. Agreement rows are self-agreement and carry no evidential weight. This corpus
is a regression fixture and yields no precision figure, ever.

Case derivation
---------------
Cases are derived by importing `analysis.expectation_diff` and calling its own parsers,
rather than by reimplementing them. That is what makes "the same way" literally true: the
`row_key` a case carries is recomputed from the raw bytes of the fixture name and the
evidence lines by `compute_row_key`, and `parse_worksheet` raises if a section's stored
header key disagrees with the key recomputed from that section's own evidence. No stored
key is trusted anywhere in this module.

Assertion shape
---------------
`dispatch_parse_log` returns a *list* of `TestOutcome` for a whole log, and `TestOutcome`
retains no reference to the raw line that produced it (see `src/parse/outcome.py`). A
worksheet row therefore cannot be matched to one element of that list — not by position,
and not by evidence line, because the evidence line is not carried. The assertion is
consequently set membership over the normalised ids emitted for the entire fixture:

- HAND_EXPECTED is an identifier  -> that identifier MUST appear in the fixture's
  normalised id set.
- HAND_EXPECTED begins with `NO_TEST` -> the identifier the parser is currently recorded
  as emitting for that evidence (the expectation table's NORMALIZED value) MUST NOT
  appear in that set.

Known defects (D2, D4, D-46) are marked `xfail(strict=True)`. Strict is the point: when a
defect is fixed the xfail becomes an unexpected pass and the suite goes red, forcing the
marker to be removed deliberately rather than leaving a fixed defect recorded as broken.
"""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE_DIR = Path("tests/fixtures/holdout_v4")
WORKSHEET_MD = Path("docs/phase/021B-blind-worksheet.md")
EXPECTATION_TABLE_MD = Path("docs/phase/021-expectation-table.md")

# `tests/fixtures/holdout_v4/` is untracked, and so are both Phase 021 documents. A fresh
# clone legitimately has none of them, and a hard dependency here would turn `make test`
# red for a new contributor — which is how a real failure gets ignored. Skip at module
# level, naming exactly what was absent, before any parametrisation is attempted.
_missing = [
    str(p)
    for p in (FIXTURE_DIR, WORKSHEET_MD, EXPECTATION_TABLE_MD)
    if not p.exists()
]
if _missing:
    pytest.skip(
        "Phase 021B regression corpus is not present in this checkout, missing: "
        + ", ".join(_missing),
        allow_module_level=True,
    )

from analysis.expectation_diff import (  # noqa: E402  (import follows the skip guard)
    parse_expectation_table,
    parse_worksheet,
)
from src.parse.dispatch import classify_log_format, dispatch_parse_log  # noqa: E402
from src.parse.log_gradle import parse_gradle_log_with_stats  # noqa: E402
from src.parse.log_maven import parse_maven_log_with_stats  # noqa: E402
from src.parse.log_pytest import parse_pytest_log_with_stats  # noqa: E402
from src.parse.test_ids import normalize_test_id  # noqa: E402


# Rows whose current parser output is a known, documented defect. Keyed by row_key so the
# marker survives any reshuffle of the worksheet; the reason names the defect so a reader
# of the xfail line does not have to go looking for what is broken.
KNOWN_DEFECTS: dict[str, str] = {}


def _build_cases() -> list:
    """Build the parametrisation, one case per worksheet row.

    Joins the worksheet against the expectation table on the content-derived `row_key`
    that both files' parsers recompute from raw bytes.

    Returns:
        A list of `pytest.param(row_key, fixture, hand_expected, normalized)`, carrying an
        `xfail(strict=True)` marker for each row named in `KNOWN_DEFECTS`.

    Raises:
        ValueError: if the two documents do not cover exactly the same set of row_keys, or
        if a row's HAND_EXPECTED is unfilled. Either is corpus corruption, not a test
        failure, and must not be silently skipped.
    """
    worksheet = parse_worksheet(WORKSHEET_MD)
    expectation = parse_expectation_table(EXPECTATION_TABLE_MD)

    if set(worksheet) != set(expectation):
        only_ws = sorted(set(worksheet) - set(expectation))
        only_et = sorted(set(expectation) - set(worksheet))
        raise ValueError(
            f"row_key sets differ: worksheet-only={only_ws}, expectation-table-only={only_et}"
        )

    cases = []
    for row_key in sorted(worksheet):
        row = worksheet[row_key]
        if not row.hand_expected:
            raise ValueError(f"row {row_key} ({row.fixture}) has an unfilled HAND_EXPECTED")
        marks = []
        if row_key in KNOWN_DEFECTS:
            marks.append(pytest.mark.xfail(strict=True, reason=KNOWN_DEFECTS[row_key]))
        cases.append(
            pytest.param(
                row_key,
                row.fixture,
                row.hand_expected,
                expectation[row_key].normalized,
                id=row_key,
                marks=marks,
            )
        )
    return cases


CASES = _build_cases()


@pytest.fixture(scope="session")
def parsed_fixtures() -> dict[str, tuple[set[str], object]]:
    """Session-scoped cache of (normalised_test_ids, parse_stats) by fixture filename.

    The 47 rows come from 26 distinct fixtures, several of them multi-megabyte. Parsing
    once per row instead of once per fixture would re-read and re-parse the same log up
    to five times.

    Returns:
        A mutable dict populated lazily by `_parse_fixture`.
    """
    return {}


def _parse_fixture(
    fixture: str, cache: dict[str, tuple[set[str], object]]
) -> tuple[set[str], object]:
    """Return the normalised test ids and framework stats for one fixture.

    Calls the real dispatcher / framework parser on the real fixture bytes and maps each
    emitted `test_id` through the real, unmodified `normalize_test_id`. Outcomes that
    normalise to `None` are dropped from the set, which is exactly what the expectation
    table records as `NONE`.

    Args:
        fixture: Filename inside `tests/fixtures/holdout_v4/`.
        cache: The session-scoped cache to read through.

    Returns:
        A tuple of (canonical_normalised_ids_set, parse_stats_object).
    """
    if fixture not in cache:
        body = (FIXTURE_DIR / fixture).read_text(encoding="utf-8", errors="replace")
        fmt = classify_log_format(body)
        if fmt == "maven":
            outcomes, stats = parse_maven_log_with_stats(body)
        elif fmt == "gradle":
            outcomes, stats = parse_gradle_log_with_stats(body)
        elif fmt == "pytest":
            outcomes, stats = parse_pytest_log_with_stats(body)
        else:
            outcomes = dispatch_parse_log(body)
            stats = None

        ids = set()
        for outcome in outcomes:
            normalized = normalize_test_id(outcome.test_id)
            if normalized is not None:
                ids.add(normalized.canonical)
        cache[fixture] = (ids, stats)
    return cache[fixture]


@pytest.mark.parametrize("row_key,fixture,hand_expected,normalized", CASES)
def test_parser_matches_hand_expected(
    row_key: str,
    fixture: str,
    hand_expected: str,
    normalized: str,
    parsed_fixtures: dict[str, tuple[set[str], object]],
) -> None:
    """The real dispatcher's output for a fixture must match the row's HAND_EXPECTED.

    Args:
        row_key: Content-derived key of the worksheet row under test.
        fixture: Fixture filename the row's evidence was taken from.
        hand_expected: The row's HAND_EXPECTED value — a canonical id, or `NO_TEST` prose.
        normalized: The expectation table's recorded NORMALIZED value for this row, i.e.
            the id the parser is currently observed to emit for this evidence.
        parsed_fixtures: Session-scoped parse cache.
    """
    emitted, stats = _parse_fixture(fixture, parsed_fixtures)

    if hand_expected.startswith("NO_TEST"):
        # The evidence names no test, so nothing derived from it may be emitted, and the
        # framework parser must record suppression of the class-level event per D-46.
        assert stats is not None and stats.class_level_events_suppressed >= 1, (
            f"{row_key} ({fixture}): expected class_level_events_suppressed >= 1"
        )
        assert normalized not in emitted, (
            f"{row_key} ({fixture}): {hand_expected}\n"
            f"but the parser emitted {normalized!r}"
        )
        return

    assert hand_expected in emitted, (
        f"{row_key} ({fixture}): expected {hand_expected!r} among the emitted ids, "
        f"parser currently records {normalized!r} for this evidence; "
        f"emitted set = {sorted(emitted)}"
    )
