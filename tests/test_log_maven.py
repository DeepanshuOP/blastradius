"""Tests for src/parse/log_maven.py against real committed log fixtures.

Per ROADMAP §9.1 (T1.1 Test-result parser suite) and AGENTS.md.
All tests run against real fixture files in tests/fixtures/logs/.
No mocks, no synthetic strings (except for explicit class-drop unit assertion).
"""

from __future__ import annotations

from pathlib import Path
import pytest

from src.parse.log_maven import (
    CONFIDENCE_FORM_A_FQCN,
    CONFIDENCE_FORM_C_BARE,
    CONFIDENCE_FORM_C_JOINED,
    CONFIDENCE_FORM_D_BARE,
    CONFIDENCE_FORM_D_JOINED,
    MavenParseStats,
    classify_maven_log,
    extract_maven_failing_test_ids,
    parse_maven_log,
    parse_maven_log_with_stats,
)
from src.parse.outcome import TestOutcome

FIXTURES_DIR = Path("tests/fixtures/logs")


def _read_fixture(fname: str) -> str:
    fpath = FIXTURES_DIR / fname
    assert fpath.exists(), f"Fixture file does not exist: {fpath}"
    return fpath.read_text(encoding="utf-8", errors="replace")


def test_shape_form_a_self_contained_zeppelin():
    """FORM A: Self-contained FQCN and method on a single line with duration."""
    body = _read_fixture("apache__zeppelin__084837475646.txt")
    outcomes, stats = parse_maven_log_with_stats(body)

    assert len(outcomes) == 1
    o = outcomes[0]
    assert (
        o.test_id
        == "org.apache.zeppelin.integration.AuthenticationIT#testSimpleAuthentication"
    )
    assert o.status == "fail"
    assert o.duration_s == 46.44
    assert o.parser_confidence == CONFIDENCE_FORM_A_FQCN
    assert stats.form_a_count == 1
    assert stats.form_b_count == 1
    assert stats.form_c_count == 1
    assert stats.dropped_class_only_count == 0
    assert stats.ambiguous_join_count == 0


def test_shape_form_b_dropped_class_only_instrumentation():
    """FORM B: Unattached class-only failure header is dropped and counted (Amendment 1)."""
    body = (
        "[ERROR] Tests run: 5, Failures: 1, Errors: 0, Skipped: 0, "
        "Time elapsed: 1.23 s <<< FAILURE! -- in org.example.ClassLevelSetupTest\n"
    )
    outcomes, stats = parse_maven_log_with_stats(body)

    # Class-level failure without test method must NOT enter outcome list
    assert len(outcomes) == 0
    assert stats.form_b_count == 1
    assert stats.dropped_class_only_count == 1
    assert stats.total_outcomes == 0


def test_shape_form_c_summary_only_opentripplanner():
    """FORM C: Surefire 3.x summary failure lines with no preceding FQCN header."""
    body = _read_fixture("opentripplanner__opentripplanner__077865124037.txt")
    outcomes, stats = parse_maven_log_with_stats(body)

    assert len(outcomes) == 4
    test_ids = {o.test_id for o in outcomes}
    expected_ids = {
        "ScooterRentalGeofencingTest#arriveByAdjacentNoDropOffZonesDropsOutsideBothZones",
        "ScooterRentalGeofencingTest#arriveBySearchBlocksRidingIntoNoTraversalZone",
        "ScooterRentalGeofencingTest#arriveBySearchDropsOffOutsideNoDropOffZone",
        "ScooterRentalGeofencingTest#forwardAndArriveByBothFindPath",
    }
    assert test_ids == expected_ids
    for o in outcomes:
        assert o.status == "fail"
        assert o.parser_confidence == CONFIDENCE_FORM_C_BARE
        assert o.failure_message is not None
        assert "IllegalArgument" in o.failure_message
    assert stats.form_c_count == 4
    assert stats.form_a_count == 0
    assert stats.form_b_count == 0
    assert stats.dropped_class_only_count == 0


def test_shape_form_d_bare_method_dolphinscheduler():
    """FORM D: Bare method failure line reconciled with FORM B enclosing class header."""
    body = _read_fixture("apache__dolphinscheduler__083801509824.txt")
    outcomes, stats = parse_maven_log_with_stats(body)

    assert len(outcomes) == 1
    o = outcomes[0]
    assert (
        o.test_id
        == "org.apache.dolphinscheduler.api.test.cases.tasks.EmrServerlessTaskAPITest#testEmrServerlessSuccessWorkflowInstance"
    )
    assert o.status == "fail"
    assert o.duration_s == 0.345
    assert stats.form_d_count == 1
    assert stats.form_b_count == 1
    assert stats.form_c_count == 1
    assert stats.dropped_class_only_count == 0


def test_fixture_10_two_identifiers_flink():
    """Fixture 10: Doubled date prefix and multiple FQCN test failures (SavepointITCase + IPv6HostnamesITCase)."""
    body = _read_fixture("apache__flink__079848838447.txt")
    outcomes, stats = parse_maven_log_with_stats(body)

    assert len(outcomes) == 2
    test_ids = {o.test_id for o in outcomes}
    expected_ids = {
        "org.apache.flink.test.checkpointing.SavepointITCase#testStopWithSavepointFailsOverToSavepoint",
        "org.apache.flink.test.runtime.IPv6HostnamesITCase#testClusterWithIPv6host",
    }
    assert test_ids == expected_ids
    for o in outcomes:
        assert o.status == "fail"
        assert o.parser_confidence == CONFIDENCE_FORM_A_FQCN
        assert o.duration_s is not None
    assert stats.form_a_count == 2
    assert stats.form_b_count == 2
    assert stats.form_c_count == 2


def test_fixture_18_parameterised_index_collapse_airlift():
    """Fixture 18: Parameterised test indices [1] and [2] collapse to single test ID."""
    body = _read_fixture("airlift__airlift__084082609180.txt")
    outcomes, stats = parse_maven_log_with_stats(body)

    assert len(outcomes) == 1
    o = outcomes[0]
    assert (
        o.test_id
        == "io.airlift.api.maven.tests.OpenApiGenerationTest#testApiIdSupportsLookupSucceeds"
    )
    assert o.status == "fail"
    assert stats.form_a_count == 2
    assert stats.form_b_count == 1


def test_fixture_36_multi_method_multi_class_join_saiku():
    """Fixture 36: Multi-class (3 classes), multi-method (8 failures) Surefire execution."""
    body = _read_fixture("spiculedata__saiku__082534301666.txt")
    outcomes, stats = parse_maven_log_with_stats(body)

    assert len(outcomes) == 8
    test_ids = {o.test_id for o in outcomes}
    expected_ids = {
        "org.saiku.service.olap.ai.ask.AiAskServiceTest#degradesWhenProviderEmitsInvalidJson",
        "org.saiku.service.olap.ai.ask.AnthropicNlAskProviderTest#requestAlwaysCarriesRefusalToolAndForcesToolChoice",
        "org.saiku.service.olap.ai.ask.AnthropicNlAskProviderTest#requestBodyBindsSchemaAsToolInputSchema",
        "org.saiku.service.olap.ai.ask.AnthropicNlAskProviderTest#systemPromptKeepsGuardrailWordingVerbatim",
        "org.saiku.service.olap.ai.ask.OpenAINlAskProviderTest#requestBodyBindsFunctionParametersAndForcesToolChoice",
        "org.saiku.service.olap.ai.ask.OpenAINlAskProviderTest#requestAlwaysCarriesRefusalFunctionAndForcesToolChoice",
        "org.saiku.service.olap.ai.ask.OpenAINlAskProviderTest#systemPromptKeepsGuardrailWordingVerbatim",
        "org.saiku.service.olap.ai.ask.OpenAINlAskProviderTest#parseToolResponseDegradesWhenToolCallsExcludeEmitQuery",
    }
    assert test_ids == expected_ids
    assert stats.form_a_count == 8
    assert stats.form_b_count == 3
    assert stats.form_c_count == 8
    assert stats.dropped_class_only_count == 0


def test_fixture_26_floci_ec2():
    """Fixture 26: Floci EC2 container manager test failure extraction."""
    body = _read_fixture("floci-io__floci__084479785666.txt")
    outcomes, stats = parse_maven_log_with_stats(body)

    assert len(outcomes) == 1
    assert (
        outcomes[0].test_id
        == "io.github.hectorvent.floci.services.ec2.Ec2ContainerManagerTest#launchInstanceUserDataStreamToCloudWatch"
    )
    assert outcomes[0].parser_confidence == CONFIDENCE_FORM_A_FQCN


def test_fixture_40_thealgorithms_parameterised():
    """Fixture 40: Parameterised test with argument types and index (String, String)[1]."""
    body = _read_fixture("thealgorithms__java__080494921200.txt")
    outcomes, stats = parse_maven_log_with_stats(body)

    assert len(outcomes) == 1
    assert (
        outcomes[0].test_id
        == "com.thealgorithms.dynamicprogramming.LongestPalindromicSubsequenceTest#testLpsKnownCases"
    )


def test_no_failure_fixtures_yield_empty():
    """No-Failure Test: Ensure clean builds, dependency errors, and setup failures yield 0 outcomes."""
    clean_fixtures = [
        "apache__beam__077621011187.txt",
        "apache__flink__079221420559.txt",
        "apache__hbase__078892029185.txt",
        "apache__zeppelin__079328560137.txt",
        "airlift__airlift__081878478589.txt",
        "floci-io__floci__081814559712.txt",
        "opentripplanner__opentripplanner__077860984374.txt",
        "spiculedata__saiku__080014373865.txt",
    ]
    for fname in clean_fixtures:
        body = _read_fixture(fname)
        outcomes = parse_maven_log(body)
        assert (
            len(outcomes) == 0
        ), f"Expected 0 outcomes for clean fixture {fname}, got {outcomes}"


def test_fixture_4_pytest_boundary_yields_empty():
    """Boundary Test: Fixture 4 (pytest) is out-of-scope for Maven parser and must yield 0 outcomes."""
    body = _read_fixture("apache__beam__082592431584.txt")
    failing_ids = extract_maven_failing_test_ids(body)
    assert len(failing_ids) == 0
    outcomes = parse_maven_log(body)
    assert len(outcomes) == 0


def test_classify_maven_log_contracts():
    """Verify classify_maven_log contract returns correct status and set."""
    body_fail = _read_fixture("apache__flink__079848838447.txt")
    status, f_ids, is_trunc = classify_maven_log(body_fail)
    assert status == "TEST_FAILURE"
    assert len(f_ids) == 2
    assert not is_trunc

    body_clean = _read_fixture("spiculedata__saiku__080014373865.txt")
    status_c, f_ids_c, _ = classify_maven_log(body_clean)
    assert status_c == "TEST_RAN_CLEAN"
    assert len(f_ids_c) == 0

    body_setup = _read_fixture("apache__flink__079221420559.txt")
    status_s, f_ids_s, _ = classify_maven_log(body_setup)
    assert status_s == "NO_TEST_OUTPUT"
    assert len(f_ids_s) == 0


def test_shape_junit4_with_preceding_suite_header():
    """JUnit 4 shape with FORM B suite header: all test IDs carry true FQCN, suite not in any test_id."""
    log_text = (
        "[ERROR] Tests run: 788, Failures: 0, Errors: 3, Skipped: 41, Time elapsed: 685.124 s <<< FAILURE! - in org.apache.hugegraph.core.CoreTestSuite\n"
        "[ERROR] testValidateUserByToken(org.apache.hugegraph.core.AuthTest)  Time elapsed: 0.929 s  <<< ERROR!\n"
        "[ERROR] testLogin(org.apache.hugegraph.core.AuthTest)  Time elapsed: 0.397 s  <<< ERROR!\n"
        "[ERROR] testLogout(org.apache.hugegraph.core.AuthTest)  Time elapsed: 0.48 s  <<< ERROR!\n"
    )
    outcomes, stats = parse_maven_log_with_stats(log_text)
    assert len(outcomes) == 3
    test_ids = {o.test_id for o in outcomes}
    expected_ids = {
        "org.apache.hugegraph.core.AuthTest#testValidateUserByToken",
        "org.apache.hugegraph.core.AuthTest#testLogin",
        "org.apache.hugegraph.core.AuthTest#testLogout",
    }
    assert test_ids == expected_ids
    assert not any("CoreTestSuite" in o.test_id for o in outcomes)
    for o in outcomes:
        assert o.status == "fail"
        assert o.parser_confidence == CONFIDENCE_FORM_A_FQCN
        assert o.duration_s is not None
    assert stats.form_junit4_count == 3
    assert stats.form_b_count == 1
    assert stats.form_d_count == 0
    assert stats.dropped_class_only_count == 1


def test_shape_junit4_with_form_c_summary_dedup():
    """JUnit 4 failure line + FORM C summary line deduplicate to 1 outcome with FQCN and merged message."""
    log_text = (
        "[ERROR] Tests run: 788, Failures: 0, Errors: 3, Skipped: 41, Time elapsed: 685.124 s <<< FAILURE! - in org.apache.hugegraph.core.CoreTestSuite\n"
        "[ERROR] testLogin(org.apache.hugegraph.core.AuthTest)  Time elapsed: 0.397 s  <<< ERROR!\n"
        "[ERROR] Failures:\n"
        "[ERROR]   AuthTest.testLogin:1425 » NoSuchMethod 'void com.fasterxml.jackson.core.util.B...\n"
    )
    outcomes, stats = parse_maven_log_with_stats(log_text)
    assert len(outcomes) == 1
    o = outcomes[0]
    assert o.test_id == "org.apache.hugegraph.core.AuthTest#testLogin"
    assert o.status == "fail"
    assert o.duration_s == 0.397
    assert o.parser_confidence == CONFIDENCE_FORM_A_FQCN
    assert o.failure_message is not None
    assert "NoSuchMethod" in o.failure_message
    assert stats.form_junit4_count == 1
    assert stats.form_c_count == 1


def test_shape_form_d_regression_without_parenthesised_class():
    """Genuine FORM D shape (bare methodName with no class in parens) still reconciles with FORM B suite header."""
    log_text = (
        "[ERROR] Tests run: 1, Failures: 1, Errors: 0, Skipped: 0, Time elapsed: 0.345 s <<< FAILURE! - in org.apache.dolphinscheduler.api.test.cases.tasks.EmrServerlessTaskAPITest\n"
        "[ERROR] testEmrServerlessSuccessWorkflowInstance  Time elapsed: 0.345 s  <<< FAILURE!\n"
    )
    outcomes, stats = parse_maven_log_with_stats(log_text)
    assert len(outcomes) == 1
    o = outcomes[0]
    assert (
        o.test_id
        == "org.apache.dolphinscheduler.api.test.cases.tasks.EmrServerlessTaskAPITest#testEmrServerlessSuccessWorkflowInstance"
    )
    assert o.status == "fail"
    assert o.duration_s == 0.345
    assert o.parser_confidence == CONFIDENCE_FORM_D_JOINED
    assert stats.form_d_count == 1
    assert stats.form_junit4_count == 0


def test_shape_junit4_multi_class_form_c_reconciliation():
    """Two distinct classes in JUnit 4 lines: FORM C suffix-join binds each to the correct FQCN."""
    log_text = (
        "[ERROR] Tests run: 781, Failures: 3, Errors: 0, Skipped: 42, Time elapsed: 670.883 s <<< FAILURE! - in org.apache.hugegraph.core.CoreTestSuite\n"
        "[ERROR] testTask(org.apache.hugegraph.core.TaskCoreTest)  Time elapsed: 19.582 s  <<< FAILURE!\n"
        "[ERROR] testTaskWithoutResult(org.apache.hugegraph.core.TaskCoreTest)  Time elapsed: 1.77 s  <<< FAILURE!\n"
        "[ERROR] testDistributedDeleteKeepsTaskResultRecoverable(org.apache.hugegraph.task.TaskAndResultSchedulerTest)  Time elapsed: 0.321 s  <<< FAILURE!\n"
        "[INFO] Results:\n"
        "[ERROR] Failures:\n"
        "[ERROR]   TaskCoreTest.testTask:96 expected:<DELETING> but was:<NEW>\n"
        "[ERROR]   TaskCoreTest.testTaskWithoutResult:185 expected:<\"metadata-result\"> but was:<null>\n"
        "[ERROR]   TaskAndResultSchedulerTest.testDistributedDeleteKeepsTaskResultRecoverable:122 expected:<DELETING> but was:<SUCCESS>\n"
    )
    outcomes, stats = parse_maven_log_with_stats(log_text)
    assert len(outcomes) == 3
    test_ids = {o.test_id for o in outcomes}
    expected_ids = {
        "org.apache.hugegraph.core.TaskCoreTest#testTask",
        "org.apache.hugegraph.core.TaskCoreTest#testTaskWithoutResult",
        "org.apache.hugegraph.task.TaskAndResultSchedulerTest#testDistributedDeleteKeepsTaskResultRecoverable",
    }
    assert test_ids == expected_ids
    assert not any("CoreTestSuite" in o.test_id for o in outcomes)
    for o in outcomes:
        assert o.status == "fail"
        assert o.parser_confidence == CONFIDENCE_FORM_A_FQCN
        assert o.failure_message is not None
    assert stats.form_junit4_count == 3
    assert stats.form_c_count == 3
    assert stats.form_d_count == 0
    assert stats.dropped_class_only_count == 1


def test_d4_class_level_event_suppressed_increments_counter():
    """D4/D-46: Class-level FORM A failure line naming only a class emits nothing and increments counter."""
    log_text = "[ERROR] org.apache.hugegraph.core.CoreTestSuite  Time elapsed: 2.946 s  <<< ERROR!\n"
    outcomes, stats = parse_maven_log_with_stats(log_text)
    assert len(outcomes) == 0
    assert stats.form_a_count == 0
    assert stats.class_level_events_suppressed == 1
    assert stats.total_outcomes == 0


def test_cldr_pascal_case_method_emitted_and_not_suppressed():
    """PascalCase test method with separator (e.g. TestShim.TestAll) is emitted and not suppressed."""
    log_text = "[ERROR] org.unicode.cldr.unittest.TestShim.TestAll -- Time elapsed: 1484 s <<< FAILURE!\n"
    outcomes, stats = parse_maven_log_with_stats(log_text)
    assert len(outcomes) == 1
    assert outcomes[0].test_id == "org.unicode.cldr.unittest.TestShim#TestAll"
    assert outcomes[0].status == "fail"
    assert stats.form_a_count == 1
    assert stats.class_level_events_suppressed == 0
    assert stats.total_outcomes == 1


def test_at_frame_corroboration_prevents_suppression_without_separator():
    """Stack frame 'at <class>.<method>(' corroborates real method even if separator is absent."""
    log_text = (
        "[ERROR] org.example.MyClass.TestMethod  Time elapsed: 1.23 s  <<< ERROR!\n"
        "\tat org.example.MyClass.TestMethod(MyClass.java:42)\n"
    )
    outcomes, stats = parse_maven_log_with_stats(log_text)
    assert len(outcomes) == 1
    assert outcomes[0].test_id == "org.example.MyClass#TestMethod"
    assert stats.form_a_count == 1
    assert stats.class_level_events_suppressed == 0


