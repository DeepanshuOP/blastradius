"""Tests for src/parse/log_gradle.py against real committed log fixtures.

Per ROADMAP §9.1 (T1.1 Test-result parser suite) and AGENTS.md.
All tests run against real fixture files in tests/fixtures/logs/.
No mocks, no synthetic strings (except for explicit boundary threshold test).
"""

from __future__ import annotations

from pathlib import Path
import pytest

from src.parse.log_gradle import (
    CONFIDENCE_S1_MULTILINE,
    CONFIDENCE_S2_SINGLE_LINE,
    CONFIDENCE_S3_CHEVRON_2SEG,
    CONFIDENCE_S4_CHEVRON_3SEG,
    MAX_CLASS_HEADER_DISTANCE_LINES,
    classify_gradle_log,
    extract_gradle_failing_test_ids,
    parse_gradle_log,
    parse_gradle_log_with_stats,
)
from src.parse.outcome import TestOutcome

FIXTURES_DIR = Path("tests/fixtures/logs")


def _read_fixture(fname: str) -> str:
    fpath = FIXTURES_DIR / fname
    assert fpath.exists(), f"Fixture file does not exist: {fpath}"
    return fpath.read_text(encoding="utf-8", errors="replace")


def test_shape_s1_multiline_fineract():
    """Shape S1: Class header on preceding unindented line, indented test failure."""
    body = _read_fixture("apache__fineract__083161294301.txt")
    outcomes, stats = parse_gradle_log_with_stats(body)

    assert len(outcomes) == 1
    o = outcomes[0]
    assert o.test_id == "org.apache.fineract.integrationtests.cob.CobPartitioningTest#testLoanCOBPartitioningQuery()"
    assert o.status == "fail"
    assert o.duration_s == 3.1
    assert o.parser_confidence == CONFIDENCE_S1_MULTILINE
    assert stats.s1_count == 1
    assert stats.stale_guard_fired_count == 0


def test_shape_s1_spock_narrative_openremote():
    """Shape S1 Variant: Multi-line Spock narrative test names containing spaces."""
    body = _read_fixture("openremote__openremote__084103046129.txt")
    outcomes, stats = parse_gradle_log_with_stats(body)

    assert len(outcomes) == 1
    o = outcomes[0]
    assert (
        o.test_id
        == "org.openremote.test.assets.ApplyPredictedDataPointsServiceTest#Does not emit attribute events after asset deletion"
    )
    assert o.status == "fail"
    assert o.duration_s == 22.2
    assert o.parser_confidence == CONFIDENCE_S1_MULTILINE
    assert stats.s1_count == 1


def test_shape_s2_single_line_spotless_deduplication():
    """Shape S2: FQCN and method name on single line, deduplicated across task summary."""
    body = _read_fixture("diffplug__spotless__086063491051.txt")
    outcomes, stats = parse_gradle_log_with_stats(body)

    # Must find all 3 failures exactly once despite repetition in task summary
    assert len(outcomes) == 3
    test_ids = {o.test_id for o in outcomes}
    expected_ids = {
        "com.diffplug.spotless.rdf.RdfFormatterTest#testCoolRdfFormatter_2_0_0_DefaultStyle()",
        "com.diffplug.spotless.rdf.RdfFormatterTest#blankNodeOrderingIsNotStableInCoolRdfFormatter_2_0_0()",
        "com.diffplug.spotless.rdf.RdfFormatterTest#testCoolRdfFormatter_2_0_0_style01()",
    }
    assert test_ids == expected_ids
    for o in outcomes:
        assert o.status == "fail"
        assert o.parser_confidence == CONFIDENCE_S2_SINGLE_LINE


def test_shape_s3_single_line_sirix_kotlin():
    """Shape S3: Chevron single-line test failures with Kotlin space-separated names."""
    body = _read_fixture("sirixdb__sirix__079909436297.txt")
    outcomes, stats = parse_gradle_log_with_stats(body)

    assert len(outcomes) == 6
    test_ids = {o.test_id for o in outcomes}
    expected_ids = {
        "io.sirix.cli.NativeImageSmokeTest#FLWOR expression",
        "io.sirix.cli.NativeImageSmokeTest#Let expression with computation",
        "io.sirix.cli.NativeImageSmokeTest#String manipulation query",
        "io.sirix.cli.NativeImageSmokeTest#Conditional expression",
        "io.sirix.cli.NativeImageSmokeTest#Sequence operations",
        "io.sirix.cli.NativeImageSmokeTest#Basic arithmetic query",
    }
    assert test_ids == expected_ids
    for o in outcomes:
        assert o.status == "fail"
        assert o.parser_confidence == CONFIDENCE_S3_CHEVRON_2SEG


def test_shape_s3_standard_gradle_beam_and_servicetalk():
    """Shape S3: Standard single-line 'Class > method() FAILED' logs."""
    body_beam = _read_fixture("apache__beam__077630056646.txt")
    outcomes_beam = parse_gradle_log(body_beam)
    assert len(outcomes_beam) == 1
    assert outcomes_beam[0].test_id == "MemoryMonitorTest#detectGCThrashing"

    body_st = _read_fixture("apple__servicetalk__085939947321.txt")
    outcomes_st = parse_gradle_log(body_st)
    assert len(outcomes_st) == 1
    assert outcomes_st[0].test_id == "PublisherBufferConcurrencyTest#largeRun()"


def test_shape_s4_hierarchical_stirling_pdf():
    """Shape S4: Hierarchical 3-segment display names; intermediate segment dropped."""
    body = _read_fixture("Stirling-Tools__Stirling-PDF__085817860968.txt")
    outcomes, stats = parse_gradle_log_with_stats(body)

    assert len(outcomes) == 1
    o = outcomes[0]
    assert o.test_id == "WebMvcConfig#registers all five resource handler groups"
    assert o.status == "fail"
    assert o.parser_confidence == CONFIDENCE_S4_CHEVRON_3SEG
    assert stats.s4_count == 1


def test_stale_class_isolation_fineract():
    """Stale-Class Test: Ensure class header does not leak across subsequent classes."""
    body = _read_fixture("apache__fineract__083161294301.txt")
    outcomes = parse_gradle_log(body)

    # Only CobPartitioningTest failed; ExternalAssetOwnerTransferCancelTest passed clean.
    # The parser must NOT attach any method to ExternalAssetOwnerTransferCancelTest.
    assert len(outcomes) == 1
    assert "CobPartitioningTest" in outcomes[0].test_id
    assert "ExternalAssetOwnerTransferCancelTest" not in outcomes[0].test_id


def test_no_failure_fixtures_yield_empty():
    """No-Failure Test: Ensure clean builds and setup failures yield 0 outcomes."""
    clean_fixtures = [
        "apache__beam__077621011187.txt",
        "apache__beam__082575659629.txt",
        "apache__fineract__080132127199.txt",
        "diffplug__spotless__077697425370.txt",
        "grobidOrg__grobid__085264981989.txt",
        "Stirling-Tools__Stirling-PDF__077860967858.txt",
    ]
    for fname in clean_fixtures:
        body = _read_fixture(fname)
        outcomes = parse_gradle_log(body)
        assert len(outcomes) == 0, f"Expected 0 outcomes for clean fixture {fname}, got {outcomes}"


def test_stale_distance_guard_boundary():
    """Stale Guard Test: 50-line distance limit clears class header if no methods follow."""
    # Build a slice where a class header is followed by 55 indented log lines
    lines = ["org.example.StaleTest"]
    lines.extend([f"  log message line {i}" for i in range(MAX_CLASS_HEADER_DISTANCE_LINES + 5)])
    lines.append("  Test testLate() FAILED (1.0s)")
    body = "\n".join(lines)

    outcomes, stats = parse_gradle_log_with_stats(body)
    assert stats.stale_guard_fired_count == 1
    assert len(outcomes) == 1
    # Because stale guard cleared org.example.StaleTest, test_id is bare method without class prefix
    assert outcomes[0].test_id == "testLate()"
    assert "org.example.StaleTest" not in outcomes[0].test_id


def test_classify_gradle_log():
    """Verify classify_gradle_log contract returns correct status and set."""
    body_fail = _read_fixture("apache__fineract__083161294301.txt")
    status, f_ids, is_trunc = classify_gradle_log(body_fail)
    assert status == "TEST_FAILURE"
    assert len(f_ids) == 1
    assert not is_trunc

    body_clean = _read_fixture("apache__beam__077621011187.txt")
    status_c, f_ids_c, _ = classify_gradle_log(body_clean)
    assert status_c == "NO_TEST_OUTPUT"
    assert len(f_ids_c) == 0
