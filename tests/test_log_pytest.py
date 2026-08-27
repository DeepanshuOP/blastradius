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


def test_pytest_timeout_interleaved_thread_dump_recovery():
    """[SYNTHETIC] Pytest-timeout splits node ID and standalone FAILED marker across 52 lines of thread dump."""
    body = (
        "2026-05-27T14:20:00.5862110Z apache_beam/yaml/examples/testing/examples_test.py::MLTest::test_ml_preprocessing_yaml +++++++++++++++++++++++++++++++++++ Timeout ++++++++++++++++++++++++++++++++++++\n"
        "2026-05-27T14:20:00.5864494Z ~~~~~~~~~~~~~~~~~ Stack of Thread-42 (_run) (134578480072384) ~~~~~~~~~~~~~~~~~~\n"
        "2026-05-27T14:20:00.5866027Z   File \"/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/threading.py\", line 973, in _bootstrap\n"
        "2026-05-27T14:20:00.5878960Z     self._bootstrap_inner()\n"
        "2026-05-27T14:20:00.5880416Z   File \"/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/threading.py\", line 1016, in _bootstrap_inner\n"
        "2026-05-27T14:20:00.5881298Z     self.run()\n"
        "2026-05-27T14:20:00.5882021Z   File \"/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/threading.py\", line 953, in run\n"
        "2026-05-27T14:20:00.5882833Z     self._target(*self._args, **self._kwargs)\n"
        "2026-05-27T14:20:00.5884209Z   File \"/runner/_work/beam/beam/sdks/python/test-suites/tox/py310/build/srcs/sdks/python/target/.tox-py310/py310/lib/python3.10/site-packages/grpc/_channel.py\", line 1905, in _poll_connectivity\n"
        "2026-05-27T14:20:00.5885616Z     event = channel.watch_connectivity_state(\n"
        "2026-05-27T14:20:00.5886254Z ~~~~~~~~~~~~~~ Stack of Thread-41 (log_stdout) (134579321349824) ~~~~~~~~~~~~~~~\n"
        "2026-05-27T14:20:00.5897831Z   File \"/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/threading.py\", line 973, in _bootstrap\n"
        "2026-05-27T14:20:00.5898952Z     self._bootstrap_inner()\n"
        "2026-05-27T14:20:00.5900031Z   File \"/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/threading.py\", line 1016, in _bootstrap_inner\n"
        "2026-05-27T14:20:00.5901159Z     self.run()\n"
        "2026-05-27T14:20:00.5901993Z   File \"/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/threading.py\", line 953, in run\n"
        "2026-05-27T14:20:00.5902945Z     self._target(*self._args, **self._kwargs)\n"
        "2026-05-27T14:20:00.5904706Z   File \"/runner/_work/beam/beam/sdks/python/test-suites/tox/py310/build/srcs/sdks/python/target/.tox-py310/py310/lib/python3.10/site-packages/apache_beam/utils/subprocess_server.py\", line 257, in log_stdout\n"
        "2026-05-27T14:20:00.5906169Z     line = process.stdout.readline()\n"
        "2026-05-27T14:20:00.5917720Z ~~~~~~~~~~~~~~~~~~~~~ Stack of Thread-30 (134578236815040) ~~~~~~~~~~~~~~~~~~~~~\n"
        "2026-05-27T14:20:00.5918888Z   File \"/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/threading.py\", line 973, in _bootstrap\n"
        "2026-05-27T14:20:00.5919716Z     self._bootstrap_inner()\n"
        "2026-05-27T14:20:00.5920519Z   File \"/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/threading.py\", line 1016, in _bootstrap_inner\n"
        "2026-05-27T14:20:00.5921323Z     self.run()\n"
        "2026-05-27T14:20:00.5925704Z   File \"/runner/_work/beam/beam/sdks/python/test-suites/tox/py310/build/srcs/sdks/python/target/.tox-py310/py310/lib/python3.10/site-packages/apache_beam/utils/thread_pool_executor.py\", line 57, in run\n"
        "2026-05-27T14:20:00.5927506Z     self._wake_semaphore.acquire()\n"
        "2026-05-27T14:20:00.5938050Z   File \"/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/threading.py\", line 467, in acquire\n"
        "2026-05-27T14:20:00.5938982Z     self._cond.wait(timeout)\n"
        "2026-05-27T14:20:00.5939801Z   File \"/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/threading.py\", line 320, in wait\n"
        "2026-05-27T14:20:00.5940584Z     waiter.acquire()\n"
        "2026-05-27T14:20:00.5941095Z ~~~~~~~~~~~~~~~~~~~~~ Stack of Thread-29 (134578337461952) ~~~~~~~~~~~~~~~~~~~~~\n"
        "2026-05-27T14:20:00.5942101Z   File \"/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/threading.py\", line 973, in _bootstrap\n"
        "2026-05-27T14:20:00.5942969Z     self._bootstrap_inner()\n"
        "2026-05-27T14:20:00.5943788Z   File \"/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/threading.py\", line 1016, in _bootstrap_inner\n"
        "2026-05-27T14:20:00.5944575Z     self.run()\n"
        "2026-05-27T14:20:00.5946632Z   File \"/runner/_work/beam/beam/sdks/python/test-suites/tox/py310/build/srcs/sdks/python/target/.tox-py310/py310/lib/python3.10/site-packages/apache_beam/utils/thread_pool_executor.py\", line 57, in run\n"
        "2026-05-27T14:20:00.5959324Z     self._wake_semaphore.acquire()\n"
        "2026-05-27T14:20:00.5960322Z   File \"/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/threading.py\", line 467, in acquire\n"
        "2026-05-27T14:20:00.5961837Z     self._cond.wait(timeout)\n"
        "2026-05-27T14:20:00.5962980Z   File \"/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/threading.py\", line 320, in wait\n"
        "2026-05-27T14:20:00.5963864Z     waiter.acquire()\n"
        "2026-05-27T14:20:00.5964817Z ~~~~~~~~~~~~~~~~~~~~~ Stack of Thread-20 (134578329069248) ~~~~~~~~~~~~~~~~~~~~~\n"
        "2026-05-27T14:20:00.5965827Z   File \"/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/threading.py\", line 973, in _bootstrap\n"
        "2026-05-27T14:20:00.5966714Z     self._bootstrap_inner()\n"
        "2026-05-27T14:20:00.5988109Z   File \"/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/threading.py\", line 1016, in _bootstrap_inner\n"
        "2026-05-27T14:20:00.5989092Z     self.run()\n"
        "2026-05-27T14:20:00.5990546Z   File \"/runner/_work/beam/beam/sdks/python/test-suites/tox/py310/build/srcs/sdks/python/target/.tox-py310/py310/lib/python3.10/site-packages/apache_beam/utils/thread_pool_executor.py\", line 57, in run\n"
        "2026-05-27T14:20:00.5992153Z     self._wake_semaphore.acquire()\n"
        "2026-05-27T14:20:00.5993125Z   File \"/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/threading.py\", line 467, in acquire\n"
        "2026-05-27T14:20:00.5994096Z     self._cond.wait(timeout)\n"
        "2026-05-27T14:20:00.5994943Z   File \"/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/threading.py\", line 320, in wait\n"
        "2026-05-27T14:20:00.5995792Z     waiter.acquire()\n"
        "2026-05-27T14:20:00.5996457Z +++++++++++++++++++++++++++++++++++ Timeout ++++++++++++++++++++++++++++++++++++\n"
        "2026-05-27T14:20:00.5997495Z FAILED                                                                   [ 99%]\n"
        "2026-05-27T14:20:47.3858297Z apache_beam/yaml/examples/testing/examples_test.py::MLTest::test_streaming_sentiment_analysis_yaml PASSED [100%]\n"
    )
    outcomes, stats = parse_pytest_log_with_stats(body)
    assert len(outcomes) == 1
    o = outcomes[0]
    assert o.test_id == "apache_beam/yaml/examples/testing/examples_test.py::MLTest::test_ml_preprocessing_yaml"
    assert o.status == "fail"
    assert o.parser_confidence == CONFIDENCE_PYTEST_PROGRESS
    assert stats.total_outcomes == 1
    assert stats.progress_fail_count == 1


def test_negative_unrelated_node_id_above_standalone_marker():
    """[NEGATIVE] Valid node ID 50 lines above standalone FAILED without Timeout banner must NOT be bound."""
    lines = ["tests/test_foo.py::test_bar PASSED [ 10%]"]
    for i in range(50):
        lines.append(f"some log output line {i}")
    lines.append("FAILED                                                                   [ 99%]")
    body = "\n".join(lines)

    outcomes, stats = parse_pytest_log_with_stats(body)
    assert len(outcomes) == 0
    assert stats.total_outcomes == 0
    assert stats.progress_fail_count == 0


def test_disarm_pending_timeout_on_intervening_progress_line():
    """[DISARM] Timeout banner arms state, but normal progress line appears before standalone marker."""
    body = (
        "tests/test_first.py::test_timeout +++++++++++++++++++++++++++++++++++ Timeout ++++++++++++++++++++++++++++++++++++\n"
        "some stack dump line 1\n"
        "tests/test_second.py::test_normal PASSED [ 50%]\n"
        "some stack dump line 2\n"
        "FAILED                                                                   [ 99%]\n"
    )
    outcomes, stats = parse_pytest_log_with_stats(body)
    assert len(outcomes) == 0
    assert stats.total_outcomes == 0
    assert stats.progress_fail_count == 0


def test_closing_timeout_banner_neither_arms_nor_disarms():
    """[SYNTHETIC] Standalone closing +++ Timeout +++ banner line neither arms nor disarms."""
    # Sub-case 1: Closing banner alone before standalone marker does not arm
    body_unarmed = (
        "+++++++++++++++++++++++++++++++++++ Timeout ++++++++++++++++++++++++++++++++++++\n"
        "FAILED                                                                   [ 99%]\n"
    )
    outcomes_unarmed, _ = parse_pytest_log_with_stats(body_unarmed)
    assert len(outcomes_unarmed) == 0

    # Sub-case 2: Closing banner between armed node ID and standalone marker does not disarm
    body_armed = (
        "tests/test_timed.py::test_fn +++++++++++++++++++++++++++++++++++ Timeout ++++++++++++++++++++++++++++++++++++\n"
        "stack trace line\n"
        "+++++++++++++++++++++++++++++++++++ Timeout ++++++++++++++++++++++++++++++++++++\n"
        "FAILED                                                                   [ 99%]\n"
    )
    outcomes_armed, _ = parse_pytest_log_with_stats(body_armed)
    assert len(outcomes_armed) == 1
    assert outcomes_armed[0].test_id == "tests/test_timed.py::test_fn"
    assert outcomes_armed[0].status == "fail"
