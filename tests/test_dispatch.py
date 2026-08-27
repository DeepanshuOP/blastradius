"""BlastRadius — Unit tests for Parser Dispatcher (src/parse/dispatch.py).

Per ROADMAP §9.1 (T1.1 Test-result parser suite), DECISIONS.md (D-09, D-25, D-27),
and Amendments 1 & 2.
"""

from pathlib import Path
import pytest

from src.parse.dispatch import (
    DispatchStats,
    classify_dispatch_log,
    classify_log_format,
    dispatch_parse_log,
    dispatch_parse_log_with_stats,
    extract_dispatch_failing_test_ids,
)
from src.parse.log_gradle import parse_gradle_log_with_stats
from src.parse.log_pytest import parse_pytest_log_with_stats

FIXTURE_4_PATH = Path("tests/fixtures/logs/apache__beam__082592431584.txt")


def test_classify_maven_format_scanning():
    log = "[INFO] Scanning for projects...\n[INFO] Building my-project 1.0"
    assert classify_log_format(log) == "maven"


def test_classify_maven_format_plugin_error():
    log = "Some log line\n[ERROR] --- maven-surefire-plugin:3.0.0:test (default-test) @ core ---"
    assert classify_log_format(log) == "maven"


def test_classify_gradle_format():
    log = "Starting Build\n> Task :core:compileJava\n> Task :core:test\nBUILD SUCCESSFUL"
    assert classify_log_format(log) == "gradle"


def test_classify_pytest_format_rootdir():
    log = "============================= test session starts ==============================\nrootdir: /home/runner/work/repo\ncollected 10 items"
    assert classify_log_format(log) == "pytest"


def test_classify_pytest_format_bare_node_id():
    log = "tests/test_core.py::test_function FAILED [100%]\nFAILED tests/test_core.py::test_function - AssertionError: 1 != 2"
    assert classify_log_format(log) == "pytest"


def test_classify_ambiguous_format():
    log = "> Task :python:test\nrootdir: /repo\ntests/test_foo.py::test_bar FAILED"
    assert classify_log_format(log) == "ambiguous"


def test_classify_unknown_format():
    log = "npm ERR! Missing script: test\nError: Process completed with exit code 1."
    assert classify_log_format(log) == "unknown"


def test_dispatch_maven_single_route():
    log = """[INFO] Scanning for projects...
[ERROR] org.apache.flink.test.MyITCase.testSavepoint -- Time elapsed: 1.2 s <<< FAILURE!
[INFO] BUILD FAILURE
"""
    outcomes, stats = dispatch_parse_log_with_stats(log)
    assert stats.format_detected == "maven"
    assert stats.routed_single == 1
    assert stats.routed_ambiguous == 0
    assert stats.unknown == 0
    assert stats.duplicate_collisions == 0
    assert len(outcomes) == 1
    assert outcomes[0].test_id == "org.apache.flink.test.MyITCase#testSavepoint"


def test_dispatch_gradle_single_route():
    log = """> Task :core:test
com.diffplug.spotless.FormatterTest testFormatting() FAILED (1.2s)
> Task :core:test FAILED
"""
    outcomes, stats = dispatch_parse_log_with_stats(log)
    assert stats.format_detected == "gradle"
    assert stats.routed_single == 1
    assert stats.routed_ambiguous == 0
    assert stats.unknown == 0
    assert stats.duplicate_collisions == 0
    assert len(outcomes) == 1
    assert outcomes[0].test_id == "com.diffplug.spotless.FormatterTest#testFormatting()"


def test_dispatch_pytest_single_route():
    log = """rootdir: /home/runner/work/repo
tests/test_calc.py::test_addition FAILED [ 50%]
FAILED tests/test_calc.py::test_addition - AssertionError: 4 != 5
"""
    outcomes, stats = dispatch_parse_log_with_stats(log)
    assert stats.format_detected == "pytest"
    assert stats.routed_single == 1
    assert stats.routed_ambiguous == 0
    assert stats.unknown == 0
    assert stats.duplicate_collisions == 0
    assert len(outcomes) == 1
    assert outcomes[0].test_id == "tests/test_calc.py::test_addition"


def test_dispatch_fixture_4_ambiguous_zero_extraction_not_collision():
    """Amendment 2 Acceptance Test:
    In Fixture 4, Gradle's lifecycle signature fires (> Task :), but Gradle yields 0 outcomes,
    while Pytest yields 8 outcomes. This zero-extraction by Gradle must NOT be treated as a
    collision, error, or ambiguity resolution failure.
    """
    assert FIXTURE_4_PATH.exists(), f"Fixture 4 missing at {FIXTURE_4_PATH}"
    body = FIXTURE_4_PATH.read_text(encoding="utf-8", errors="replace")

    # Confirm individual parser behavior on this fixture
    g_outcomes, g_stats = parse_gradle_log_with_stats(body)
    p_outcomes, p_stats = parse_pytest_log_with_stats(body)
    assert len(g_outcomes) == 0, "Gradle parser should extract 0 outcomes from pytest-under-gradle log"
    assert len(p_outcomes) == 8, "Pytest parser should extract 8 outcomes from fixture 4"

    # Confirm dispatcher behavior
    outcomes, stats = dispatch_parse_log_with_stats(body)
    assert stats.format_detected == "ambiguous"
    assert stats.routed_ambiguous == 1
    assert stats.routed_single == 0
    assert stats.unknown == 0
    assert stats.duplicate_collisions == 0
    assert len(outcomes) == 8
    assert stats.total_outcomes == 8

    # Extract failing test IDs convenience function
    failing_ids = extract_dispatch_failing_test_ids(body)
    assert len(failing_ids) == 8


def test_dispatch_ambiguous_with_actual_duplicate_collision():
    """Amendment 1 Acceptance Test:
    When two parsers match an ambiguous log and both extract the same logical test entity
    using different format separators, normalized identifier comparison detects the collision
    and preserves the higher confidence record without duplicate emission.
    """
    synthetic_ambiguous_log = """> Task :core:test
[INFO] Scanning for projects...
com.example.FooTest testBar() FAILED (0.5s)
[ERROR] com.example.FooTest.testBar -- Time elapsed: 0.1 s <<< FAILURE!
"""
    outcomes, stats = dispatch_parse_log_with_stats(synthetic_ambiguous_log)
    assert stats.format_detected == "ambiguous"
    assert stats.routed_ambiguous == 1
    assert stats.duplicate_collisions == 1
    assert len(outcomes) == 1
    # Maven has confidence 0.90, Gradle has 0.85 -> Maven record is preferred
    assert outcomes[0].parser_confidence == 0.90
    assert outcomes[0].test_id == "com.example.FooTest#testBar"



def test_dispatch_unknown_returns_empty_and_increments_unknown():
    log = """Step 1/5 : FROM ubuntu:22.04
 ---> 123456789abc
Step 2/5 : RUN cargo build --release
error: could not compile `my-crate` due to previous error
"""
    outcomes, stats = dispatch_parse_log_with_stats(log)
    assert stats.format_detected == "unknown"
    assert stats.unknown == 1
    assert stats.routed_single == 0
    assert stats.routed_ambiguous == 0
    assert stats.duplicate_collisions == 0
    assert outcomes == []
    assert stats.total_outcomes == 0

    # classify_dispatch_log on unknown should report NO_TEST_OUTPUT
    cls, ids, trunc = classify_dispatch_log(log)
    assert cls == "NO_TEST_OUTPUT"
    assert ids == set()
    assert trunc is False


def test_classify_dispatch_log_clean_maven():
    log = """[INFO] Scanning for projects...
[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.example.AppTest
[INFO] Tests run: 5, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.2 s -- in com.example.AppTest
[INFO] BUILD SUCCESS
"""
    cls, ids, trunc = classify_dispatch_log(log)
    assert cls == "TEST_RAN_CLEAN"
    assert ids == set()
    assert trunc is False
