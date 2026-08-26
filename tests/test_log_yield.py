"""Contract and regression tests for analysis/log_yield.py extraction.

Tests real committed log fixtures from tests/fixtures/logs/ (no mocks or inline synthetic logs).
"""

from __future__ import annotations

from pathlib import Path
import pytest

from analysis.log_yield import extract_failing_test_ids, classify_log

FIXTURES_DIR = Path("tests/fixtures/logs")


def _read_fixture(fname: str) -> str:
    path = FIXTURES_DIR / fname
    if not path.exists():
        pytest.skip(f"Fixture file {fname} not found")
    return path.read_text(encoding="utf-8", errors="replace")


def test_opentripplanner_surefire_3x_form_c() -> None:
    """Fixture 32 (OTP): Maven Surefire 3.x summary form without FQN detail lines."""
    body = _read_fixture("opentripplanner__opentripplanner__077865124037.txt")
    extracted = extract_failing_test_ids(body)
    expected = {
        "ScooterRentalGeofencingTest::arriveByAdjacentNoDropOffZonesDropsOutsideBothZones",
        "ScooterRentalGeofencingTest::arriveBySearchBlocksRidingIntoNoTraversalZone",
        "ScooterRentalGeofencingTest::arriveBySearchDropsOffOutsideNoDropOffZone",
        "ScooterRentalGeofencingTest::forwardAndArriveByBothFindPath",
    }
    assert extracted == expected


def test_saiku_join_multi_method() -> None:
    """Fixture 36 (Saiku): 3 FQN classes in FORM B join 8 methods across FORM A and FORM C."""
    body = _read_fixture("spiculedata__saiku__082534301666.txt")
    extracted = extract_failing_test_ids(body)
    expected = {
        "org.saiku.service.olap.ai.ask.AiAskServiceTest::degradesWhenProviderEmitsInvalidJson",
        "org.saiku.service.olap.ai.ask.AnthropicNlAskProviderTest::requestAlwaysCarriesRefusalToolAndForcesToolChoice",
        "org.saiku.service.olap.ai.ask.AnthropicNlAskProviderTest::requestBodyBindsSchemaAsToolInputSchema",
        "org.saiku.service.olap.ai.ask.AnthropicNlAskProviderTest::systemPromptKeepsGuardrailWordingVerbatim",
        "org.saiku.service.olap.ai.ask.OpenAINlAskProviderTest::parseToolResponseDegradesWhenToolCallsExcludeEmitQuery",
        "org.saiku.service.olap.ai.ask.OpenAINlAskProviderTest::requestAlwaysCarriesRefusalFunctionAndForcesToolChoice",
        "org.saiku.service.olap.ai.ask.OpenAINlAskProviderTest::requestBodyBindsFunctionParametersAndForcesToolChoice",
        "org.saiku.service.olap.ai.ask.OpenAINlAskProviderTest::systemPromptKeepsGuardrailWordingVerbatim",
    }
    assert extracted == expected


def test_airlift_parameterized_index_collapse() -> None:
    """Fixture 18 (Airlift): Parameterized test indices [1] and [2] collapse to one method ID."""
    body = _read_fixture("airlift__airlift__084082609180.txt")
    extracted = extract_failing_test_ids(body)
    assert extracted == {
        "io.airlift.api.maven.tests.OpenApiGenerationTest::testApiIdSupportsLookupSucceeds"
    }


def test_mybatis_plus_ex_phantom_gradle() -> None:
    """Fixture 20 (MyBatis-Plus): Gradle test extracts test method without phantom task name."""
    body = _read_fixture("baomidou__mybatis-plus__085831964676.txt")
    extracted = extract_failing_test_ids(body)
    assert extracted == {"GeneratePomTest > test()"}


def test_dolphinscheduler_form_d_join() -> None:
    """Fixture 6 (DolphinScheduler): Bare method in FORM D and summary in FORM C join FQN class."""
    body = _read_fixture("apache__dolphinscheduler__083801509824.txt")
    extracted = extract_failing_test_ids(body)
    assert extracted == {
        "org.apache.dolphinscheduler.api.test.cases.tasks.EmrServerlessTaskAPITest::testEmrServerlessSuccessWorkflowInstance"
    }


def test_no_failure_fixtures_yield_empty() -> None:
    """Fixtures 1 and 11 (Beam & HBase): No test outcomes yield empty set of identifiers."""
    beam_body = _read_fixture("apache__beam__077621011187.txt")
    assert extract_failing_test_ids(beam_body) == set()

    hbase_body = _read_fixture("apache__hbase__078892029185.txt")
    assert extract_failing_test_ids(hbase_body) == set()


def test_ansi_heavy_log_clean_extraction() -> None:
    """Fixture 32: Heavy ANSI logs (2800+ lines) extract clean identifiers with no escape codes."""
    body = _read_fixture("opentripplanner__opentripplanner__077865124037.txt")
    extracted = extract_failing_test_ids(body)
    assert len(extracted) == 4
    for item in extracted:
        assert "\x1b" not in item
        assert "[" not in item
