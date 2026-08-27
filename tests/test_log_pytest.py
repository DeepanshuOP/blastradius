"""Tests for src/parse/log_pytest.py against real committed log fixtures and minimal synthetic cases.

Per ROADMAP §9.1 (T1.1 Test-result parser suite) and AGENTS.md.
Real fixture tests run against tests/fixtures/logs/ (QUARANTINE: holdout is never touched).
Synthetic tests are minimal and explicitly marked [SYNTHETIC] in their docstrings.
"""

from __future__ import annotations

from pathlib import Path
import pytest

from src.parse.log_pytest import (
    CONFIDENCE_PYTEST_PROGRESS,
    CONFIDENCE_PYTEST_SUMMARY,
    PytestParseStats,
    classify_pytest_log,
    extract_pytest_failing_test_ids,
    parse_pytest_log,
    parse_pytest_log_with_stats,
)
from src.parse.outcome import TestOutcome

FIXTURES_DIR = Path("tests/fixtures/logs")


def _read_fixture(fname: str) -> str:
    fpath = FIXTURES_DIR / fname
    assert fpath.exists(), f"Fixture file does not exist: {fpath}"
    return fpath.read_text(encoding="utf-8", errors="replace")


def test_fixture_4_eight_identifiers():
    """Real Fixture 4 (apache__beam__082592431584.txt): All 8 pytest failures extracted."""
    body = _read_fixture("apache__beam__082592431584.txt")
    outcomes, stats = parse_pytest_log_with_stats(body)

    assert len(outcomes) == 8
    assert stats.total_outcomes == 8
    assert stats.progress_fail_count == 8
    assert stats.summary_fail_count == 8
    assert stats.dedup_merged_count == 8
    assert stats.progress_error_count == 0
    assert stats.summary_error_count == 0

    extracted_ids = {o.test_id for o in outcomes}
    expected_ids = {
        "apache_beam/yaml/integration_tests.py::FlattenTest::test_Flatten_ExternalJavaProvider_2",
        "apache_beam/yaml/integration_tests.py::DatadogTest::test_only",
        "apache_beam/yaml/integration_tests.py::Iceberg_Add_FilesTest::test_WriteToJson_ExternalJavaProvider_1",
        "apache_beam/yaml/integration_tests.py::Iceberg_Add_FilesTest::test_WriteToJson_InlineProvider_0",
        "apache_beam/yaml/integration_tests.py::DeltaTest::test_only",
        "apache_beam/yaml/integration_tests.py::IcebergTest::test_only",
        "apache_beam/yaml/integration_tests.py::MongodbTest::test_WriteToMongoDB_ExternalJavaProvider_1",
        "apache_beam/yaml/integration_tests.py::Iceberg_Add_Files_BatchTest::test_only",
    }
    assert extracted_ids == expected_ids

    for o in outcomes:
        assert o.status == "fail"
        assert o.parser_confidence == CONFIDENCE_PYTEST_SUMMARY
        assert o.failure_message is not None


def test_fixture_4_dedup_merge_enrichment():
    """Real Fixture 4: Summary line enriches progress record with failure message and raises confidence."""
    body = _read_fixture("apache__beam__082592431584.txt")
    outcomes, stats = parse_pytest_log_with_stats(body)

    by_id = {o.test_id: o for o in outcomes}
    datadog = by_id["apache_beam/yaml/integration_tests.py::DatadogTest::test_only"]
    assert datadog.parser_confidence == CONFIDENCE_PYTEST_SUMMARY
    assert datadog.failure_message == "AssertionError: Mismatch in recorded Datadog events!"

    delta = by_id["apache_beam/yaml/integration_tests.py::DeltaTest::test_only"]
    assert delta.parser_confidence == CONFIDENCE_PYTEST_SUMMARY
    assert delta.failure_message == "NameError: name 'tempfile' is not defined"


def test_fixture_2_boundary_yields_empty():
    """Boundary Test: Fixture 2 (apache__beam__077630056646.txt, Gradle Java) yields empty from pytest parser."""
    body = _read_fixture("apache__beam__077630056646.txt")
    failing_ids = extract_pytest_failing_test_ids(body)
    assert len(failing_ids) == 0
    outcomes = parse_pytest_log(body)
    assert len(outcomes) == 0


def test_fixture_5_boundary_yields_empty():
    """Boundary Test: Fixture 5 (apache__beam__086455350919.txt, Gradle Groovy) yields empty from pytest parser."""
    body = _read_fixture("apache__beam__086455350919.txt")
    failing_ids = extract_pytest_failing_test_ids(body)
    assert len(failing_ids) == 0
    outcomes = parse_pytest_log(body)
    assert len(outcomes) == 0


def test_no_failure_fixtures_yield_empty():
    """Real Clean/Setup Fixtures: Non-pytest and clean builds yield 0 outcomes."""
    clean_fixtures = [
        "apache__beam__077621011187.txt",
        "apache__beam__082575659629.txt",
        "spiculedata__saiku__080014373865.txt",
        "crimera__piko__083277376521.txt",
    ]
    for fname in clean_fixtures:
        body = _read_fixture(fname)
        outcomes = parse_pytest_log(body)
        assert len(outcomes) == 0, f"Expected 0 outcomes for {fname}, got {outcomes}"


def test_synthetic_module_level_failure():
    """[SYNTHETIC] Module-level collection or execution failure with no class or method."""
    body = (
        "2026-08-27T10:00:00.000Z tests/test_module.py FAILED [100%]\n"
        "=========================== short test summary info ============================\n"
        "2026-08-27T10:00:01.000Z FAILED tests/test_module.py - SyntaxError: invalid syntax\n"
    )
    outcomes, stats = parse_pytest_log_with_stats(body)

    assert len(outcomes) == 1
    o = outcomes[0]
    assert o.test_id == "tests/test_module.py"
    assert o.status == "fail"
    assert o.parser_confidence == CONFIDENCE_PYTEST_SUMMARY
    assert o.failure_message == "SyntaxError: invalid syntax"
    assert stats.total_outcomes == 1
    assert stats.progress_fail_count == 1
    assert stats.summary_fail_count == 1
    assert stats.dedup_merged_count == 1


def test_synthetic_error_fixture_setup():
    """[SYNTHETIC] Fixture setup failure reporting ERROR status tag."""
    body = (
        "2026-08-27T10:00:00.000Z tests/test_service.py::test_init ERROR [ 10%]\n"
        "=========================== short test summary info ============================\n"
        "2026-08-27T10:00:01.000Z ERROR tests/test_service.py::test_init (setup) - RuntimeError: DB connection failed\n"
    )
    outcomes, stats = parse_pytest_log_with_stats(body)

    assert len(outcomes) == 1
    o = outcomes[0]
    assert o.test_id == "tests/test_service.py::test_init"
    assert o.status == "error"
    assert o.parser_confidence == CONFIDENCE_PYTEST_SUMMARY
    assert o.failure_message == "RuntimeError: DB connection failed"
    assert stats.progress_error_count == 1
    assert stats.summary_error_count == 1
    assert stats.dedup_merged_count == 1


def test_synthetic_parameterised_brackets_preserved():
    """[SYNTHETIC] Parameterised test ID keeps brackets intact and does not collapse index."""
    body = (
        "2026-08-27T10:00:00.000Z tests/test_calc.py::test_add[2-3-5] FAILED [ 50%]\n"
        "=========================== short test summary info ============================\n"
        "2026-08-27T10:00:01.000Z FAILED tests/test_calc.py::test_add[2-3-5] - AssertionError: assert 5 == 6\n"
    )
    outcomes, stats = parse_pytest_log_with_stats(body)

    assert len(outcomes) == 1
    o = outcomes[0]
    assert o.test_id == "tests/test_calc.py::test_add[2-3-5]"
    assert o.status == "fail"
    assert o.failure_message == "AssertionError: assert 5 == 6"


def test_synthetic_parameterised_complex_brackets():
    """[SYNTHETIC] Parameterised test with :: characters inside parameter brackets does not split."""
    body = (
        "2026-08-27T10:00:00.000Z tests/test_calc.py::test_eval[a::b-c] FAILED [ 50%]\n"
        "=========================== short test summary info ============================\n"
        "2026-08-27T10:00:01.000Z FAILED tests/test_calc.py::test_eval[a::b-c] - ValueError: parse error\n"
    )
    outcomes, stats = parse_pytest_log_with_stats(body)

    assert len(outcomes) == 1
    assert outcomes[0].test_id == "tests/test_calc.py::test_eval[a::b-c]"
    assert outcomes[0].failure_message == "ValueError: parse error"


def test_synthetic_doctest_failure():
    """[SYNTHETIC] Python doctest failure extraction."""
    body = (
        "2026-08-27T10:00:00.000Z src/pkg/util.py::src.pkg.util.format_text (doctest) FAILED [ 80%]\n"
        "=========================== short test summary info ============================\n"
        "2026-08-27T10:00:01.000Z FAILED src/pkg/util.py::src.pkg.util.format_text - Failed example: format_text('a')\n"
    )
    outcomes, stats = parse_pytest_log_with_stats(body)

    assert len(outcomes) >= 1
    extracted_ids = {o.test_id for o in outcomes}
    assert any("src/pkg/util.py" in tid for tid in extracted_ids)


def test_synthetic_xfail_xpass_unsupported():
    """[SYNTHETIC] XFAIL and XPASS outcomes are not emitted per strict unsupported policy."""
    body = (
        "2026-08-27T10:00:00.000Z tests/test_foo.py::test_expected_fail XFAIL [ 50%]\n"
        "2026-08-27T10:00:00.000Z tests/test_foo.py::test_unexpected_pass XPASS [100%]\n"
        "=========================== short test summary info ============================\n"
        "2026-08-27T10:00:01.000Z XFAIL tests/test_foo.py::test_expected_fail - reason: known issue\n"
        "2026-08-27T10:00:01.000Z XPASS tests/test_foo.py::test_unexpected_pass - reason: fixed but marked xfail\n"
    )
    outcomes, stats = parse_pytest_log_with_stats(body)
    assert len(outcomes) == 0
    assert stats.total_outcomes == 0


def test_classify_pytest_log_contracts():
    """Verify classify_pytest_log contract returns correct status and set."""
    body_fail = _read_fixture("apache__beam__082592431584.txt")
    status_f, f_ids, is_trunc = classify_pytest_log(body_fail)
    assert status_f == "TEST_FAILURE"
    assert len(f_ids) == 8
    assert not is_trunc

    body_none = _read_fixture("apache__beam__077621011187.txt")
    status_n, f_ids_n, _ = classify_pytest_log(body_none)
    assert status_n == "NO_TEST_OUTPUT"
    assert len(f_ids_n) == 0

    body_clean = "====== 10 passed, 1 skipped in 1.23s ======"
    status_c, f_ids_c, _ = classify_pytest_log(body_clean)
    assert status_c == "TEST_RAN_CLEAN"
    assert len(f_ids_c) == 0
