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


def test_multi_failure_block_timestamped_fineract():
    """Shape S1 Multi-Failure: All failures under a timestamped class header retain FQCN."""
    log_chunk = """2026-06-13T18:02:33.4136711Z org.apache.fineract.portfolio.savings.service.SavingsAccountWritePlatformServiceJpaRepositoryImplTest
2026-06-13T18:02:33.4137512Z 
2026-06-13T18:02:33.4138401Z   Test validateTransactionsForTransfer_transactionDateEqualsTransferDate_throwsGeneralPlatformDomainRuleException() PASSED (1.4s)
2026-06-13T18:02:33.6147199Z   Test payCharge_shouldReturnTransactionIdInResult() FAILED
2026-06-13T18:02:33.6178954Z 
2026-06-13T18:02:33.6201776Z   java.lang.NullPointerException: Cannot invoke "org.apache.fineract.organisation.office.domain.Office.getHierarchy()" because the return value of "org.apache.fineract.portfolio.savings.domain.SavingsAccount.office()" is null
2026-06-13T18:02:33.6237019Z       at org.apache.fineract.portfolio.savings.service.SavingsAccountWritePlatformServiceJpaRepositoryImplTest.payCharge_shouldReturnTransactionIdInResult(SavingsAccountWritePlatformServiceJpaRepositoryImplTest.java:452)
2026-06-13T18:02:33.6265734Z 
2026-06-13T18:02:33.6266862Z   Test validateTransactionsForTransfer_nullTransferDate_doesNotThrowNullPointerException() PASSED
2026-06-13T18:02:33.7143887Z   Test releaseAmount_shouldThrowNotFoundWhenTransactionDoesNotBelongToSavingsAccount() PASSED
2026-06-13T18:02:33.7176368Z   Test holdAmount_shouldUpdateTransactionExternalId() FAILED
2026-06-13T18:02:33.7200315Z 
2026-06-13T18:02:33.7224757Z   java.lang.NullPointerException: Cannot invoke "org.apache.fineract.organisation.office.domain.Office.getHierarchy()" because the return value of "org.apache.fineract.portfolio.savings.domain.SavingsAccount.office()" is null
2026-06-13T18:02:33.7256582Z       at org.apache.fineract.portfolio.savings.service.SavingsAccountWritePlatformServiceJpaRepositoryImplTest.holdAmount_shouldUpdateTransactionExternalId(SavingsAccountWritePlatformServiceJpaRepositoryImplTest.java:282)
2026-06-13T18:02:33.7273887Z 
2026-06-13T18:02:33.8147105Z   Test validateTransactionsForTransfer_transactionDateBeforeTransferDate_doesNotThrow() PASSED
2026-06-13T18:02:33.8166784Z   Test validateTransactionsForTransfer_transactionDateAfterTransferDate_throwsGeneralPlatformDomainRuleException() PASSED
2026-06-13T18:02:33.8191017Z   Test postInterest_shouldValidateRequestAndUpdateManualInterestPostingExternalId() FAILED
2026-06-13T18:02:33.8215386Z 
2026-06-13T18:02:33.8217138Z   java.lang.NullPointerException: Cannot invoke "org.apache.fineract.organisation.office.domain.Office.getHierarchy()" because the return value of "org.apache.fineract.portfolio.savings.domain.SavingsAccount.office()" is null
2026-06-13T18:02:33.8220913Z       at org.apache.fineract.portfolio.savings.service.SavingsAccountWritePlatformServiceJpaRepositoryImplTest.postInterest_shouldValidateRequestAndUpdateManualInterestPostingExternalId(SavingsAccountWritePlatformServiceJpaRepositoryImplTest.java:390)
2026-06-13T18:02:33.8232363Z 
2026-06-13T18:02:33.8239377Z   Test validateTransactionsForTransfer_transactionWithNullDate_doesNotThrow() PASSED
2026-06-13T18:02:33.8246218Z   Test releaseAmount_shouldUpdateTransactionExternalId() FAILED
2026-06-13T18:02:33.8274419Z 
2026-06-13T18:02:33.8306933Z   java.lang.NullPointerException: Cannot invoke "org.apache.fineract.organisation.office.domain.Office.getHierarchy()" because the return value of "org.apache.fineract.portfolio.savings.domain.SavingsAccount.office()" is null
2026-06-13T18:02:33.8317051Z       at org.apache.fineract.portfolio.savings.service.SavingsAccountWritePlatformServiceJpaRepositoryImplTest.releaseAmount_shouldUpdateTransactionExternalId(SavingsAccountWritePlatformServiceJpaRepositoryImplTest.java:322)
"""
    outcomes, stats = parse_gradle_log_with_stats(log_chunk)
    assert len(outcomes) == 4
    expected_ids = {
        "org.apache.fineract.portfolio.savings.service.SavingsAccountWritePlatformServiceJpaRepositoryImplTest#payCharge_shouldReturnTransactionIdInResult()",
        "org.apache.fineract.portfolio.savings.service.SavingsAccountWritePlatformServiceJpaRepositoryImplTest#holdAmount_shouldUpdateTransactionExternalId()",
        "org.apache.fineract.portfolio.savings.service.SavingsAccountWritePlatformServiceJpaRepositoryImplTest#postInterest_shouldValidateRequestAndUpdateManualInterestPostingExternalId()",
        "org.apache.fineract.portfolio.savings.service.SavingsAccountWritePlatformServiceJpaRepositoryImplTest#releaseAmount_shouldUpdateTransactionExternalId()",
    }
    extracted_ids = {o.test_id for o in outcomes}
    assert extracted_ids == expected_ids
    for o in outcomes:
        assert o.status == "fail"
        assert o.parser_confidence == CONFIDENCE_S1_MULTILINE


def test_unindented_non_stacktrace_resets_class_context():
    """Regression: Genuinely column-0 non-stacktrace line resets current_class via section 7 elif."""
    log_chunk = """org.example.FirstTest
  Test testA() FAILED (1.0s)
Some non-stacktrace text at column 0
  Test testB() FAILED (1.0s)
"""
    outcomes = parse_gradle_log(log_chunk)
    assert len(outcomes) == 2
    assert outcomes[0].test_id == "org.example.FirstTest#testA()"
    assert outcomes[1].test_id == "testB()"
    assert "org.example.FirstTest" not in outcomes[1].test_id


def test_multi_failure_block_untimestamped():
    """Shape S1 Multi-Failure (Untimestamped): Class context retained across multi-failure block without timestamps."""
    log_chunk = """org.example.CalculatorTest
  Test testAdd() FAILED (0.5s)
  java.lang.AssertionError: expected:<4> but was:<5>
      at org.example.CalculatorTest.testAdd(CalculatorTest.java:20)
  Test testSubtract() FAILED (0.2s)
  java.lang.AssertionError: expected:<1> but was:<0>
      at org.example.CalculatorTest.testSubtract(CalculatorTest.java:30)
"""
    outcomes = parse_gradle_log(log_chunk)
    assert len(outcomes) == 2
    assert outcomes[0].test_id == "org.example.CalculatorTest#testAdd()"
    assert outcomes[1].test_id == "org.example.CalculatorTest#testSubtract()"


def test_s1_bare_s3_qualified_deduplication_grobid_real_lines():
    """(a) S1 bare + S3 class-qualified for the same method in one block emits exactly ONE identifier carrying FQCN."""
    log_chunk = """2026-06-22T18:21:52.5235288Z org.grobid.core.data.BiblioItemTest
2026-06-22T18:21:55.1254418Z > Task :grobid-core:test
2026-06-22T18:21:55.1255540Z   Test setNormalizedPublicationDate_populatesYearMonthDay_issue15 FAILED
2026-06-22T18:21:55.1258298Z       at org.grobid.core.data.BiblioItemTest.setNormalizedPublicationDate_populatesYearMonthDay_issue15(BiblioItemTest.kt:920)
2026-06-22T18:21:55.1259942Z BiblioItemTest > setNormalizedPublicationDate_populatesYearMonthDay_issue15 FAILED
"""
    outcomes, stats = parse_gradle_log_with_stats(log_chunk)
    assert len(outcomes) == 1
    assert (
        outcomes[0].test_id
        == "org.grobid.core.data.BiblioItemTest#setNormalizedPublicationDate_populatesYearMonthDay_issue15"
    )
    assert stats.s1_count == 1
    assert stats.s3_count == 1
    assert stats.total_outcomes == 1


def test_stack_frame_suffix_join_nats_real_lines():
    """(b) Simple class name joins to the FQCN when an 'at' frame matches class AND method."""
    log_chunk = """2026-07-13T15:07:34.8167072Z KeyValueConfigurationTests > testInstanceMirrorAndSources() FAILED
2026-07-13T15:07:34.8167932Z     java.lang.RuntimeException: java.lang.NullPointerException
2026-07-13T15:07:34.8170995Z         at io.nats.client.api.KeyValueConfigurationTests.testInstanceMirrorAndSources(KeyValueConfigurationTests.java:116)
"""
    outcomes, stats = parse_gradle_log_with_stats(log_chunk)
    assert len(outcomes) == 1
    assert (
        outcomes[0].test_id
        == "io.nats.client.api.KeyValueConfigurationTests#testInstanceMirrorAndSources()"
    )
    assert stats.ambiguous_join_count == 0


def test_stack_frame_suffix_join_negative_different_method():
    """(c) NEGATIVE: join must NOT fire when an 'at' frame matches the class but a DIFFERENT method."""
    log_chunk = """KeyValueConfigurationTests > testMethodA() FAILED
    java.lang.RuntimeException: assertion failed
        at io.nats.client.api.KeyValueConfigurationTests.testMethodB(KeyValueConfigurationTests.java:200)
"""
    outcomes, stats = parse_gradle_log_with_stats(log_chunk)
    assert len(outcomes) == 1
    assert outcomes[0].test_id == "KeyValueConfigurationTests#testMethodA()"
    assert stats.ambiguous_join_count == 0


def test_stack_frame_suffix_join_negative_ambiguous_candidates():
    """(d) NEGATIVE: two candidate FQCNs with same simple class name and method leave identifier unjoined and increment counter."""
    log_chunk = """KeyValueConfigurationTests > testDuplicate() FAILED
    java.lang.RuntimeException: fail
        at com.foo.api.KeyValueConfigurationTests.testDuplicate(KeyValueConfigurationTests.java:50)
        at com.bar.api.KeyValueConfigurationTests.testDuplicate(KeyValueConfigurationTests.java:80)
"""
    outcomes, stats = parse_gradle_log_with_stats(log_chunk)
    assert len(outcomes) == 1
    assert outcomes[0].test_id == "KeyValueConfigurationTests#testDuplicate()"
    assert stats.ambiguous_join_count == 1


def test_stack_frame_suffix_join_ignores_framework_frames():
    """(e) Framework frames (org.junit.Assert, org.hamcrest.MatcherAssert) present in trace do not pollute the join."""
    log_chunk = """2026-06-22T18:21:55.1259942Z BiblioItemTest > setNormalizedPublicationDate_populatesYearMonthDay_issue15 FAILED
2026-06-22T18:21:55.1260488Z     java.lang.AssertionError: 
2026-06-22T18:21:55.1261557Z         at org.hamcrest.MatcherAssert.assertThat(MatcherAssert.java:20)
2026-06-22T18:21:55.1262067Z         at org.junit.Assert.assertThat(Assert.java:964)
2026-06-22T18:21:55.1263591Z         at org.grobid.core.data.BiblioItemTest.setNormalizedPublicationDate_populatesYearMonthDay_issue15(BiblioItemTest.kt:920)
"""
    outcomes, stats = parse_gradle_log_with_stats(log_chunk)
    assert len(outcomes) == 1
    assert (
        outcomes[0].test_id
        == "org.grobid.core.data.BiblioItemTest#setNormalizedPublicationDate_populatesYearMonthDay_issue15"
    )
    assert stats.ambiguous_join_count == 0

