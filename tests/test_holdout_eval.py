"""Tests for analysis/holdout_eval.py union evaluator against held-out fixture corpus.

Per ROADMAP §25.3, §34.4, §37.1 and AGENTS.md.
Asserts that the dispatcher-free union scorer reproduces known-by-hand results
on representative holdout fixtures (pytest, Maven, Gradle, non-test output) and
asserts overall evaluation consistency.
"""

from __future__ import annotations

from pathlib import Path
import pytest

from analysis.holdout_eval import (
    evaluate_holdout,
    normalize_comparison_id,
    parse_holdout_expected,
    union_classify,
    union_extract,
)

HOLDOUT_DIR = Path("tests/fixtures/holdout")


def _read_holdout_fixture(fname: str) -> str:
    fpath = HOLDOUT_DIR / fname
    assert fpath.exists(), f"Holdout fixture not found: {fpath}"
    return fpath.read_text(encoding="utf-8", errors="replace")


def test_holdout_fixture_2_pytest_exact_match():
    """Fixture 2 (apache__beam__077874374405.txt): All 4 pytest failures extracted without cross-firing."""
    body = _read_holdout_fixture("apache__beam__077874374405.txt")
    union_ids, per_parser_ids = union_extract(body)
    actual_class, _, _, _ = union_classify(body)

    assert actual_class == "TEST_FAILURE"
    assert len(per_parser_ids["pytest"]) == 4
    assert len(per_parser_ids["gradle"]) == 0
    assert len(per_parser_ids["maven"]) == 0

    norm_extracted = {normalize_comparison_id(x) for x in union_ids}
    expected_ids = {
        "apache_beam/yaml/integration_tests.py::Assign_TimestampsTest::test_only",
        "apache_beam/yaml/integration_tests.py::CreateTest::test_only",
        "apache_beam/yaml/integration_tests.py::Ml_TransformTest::test_only",
        "apache_beam/yaml/integration_tests.py::Validate_With_SchemaTest::test_only",
    }
    assert norm_extracted == expected_ids


def test_holdout_fixture_4_maven_exact_match():
    """Fixture 4 (unicode-org__cldr__083663566205.txt): Maven failure extracted without cross-firing."""
    body = _read_holdout_fixture("unicode-org__cldr__083663566205.txt")
    union_ids, per_parser_ids = union_extract(body)
    actual_class, _, _, _ = union_classify(body)

    assert actual_class == "TEST_FAILURE"
    assert len(per_parser_ids["maven"]) == 1
    assert len(per_parser_ids["gradle"]) == 0
    assert len(per_parser_ids["pytest"]) == 0

    norm_extracted = {normalize_comparison_id(x) for x in union_ids}
    expected_ids = {"org.unicode.cldr.surveydriver.AppTest::shouldDrive"}
    assert norm_extracted == expected_ids


def test_holdout_fixture_10_gradle_exact_match():
    """Fixture 10 (diffplug__spotless__079141262640.txt): Gradle failure extracted without cross-firing."""
    body = _read_holdout_fixture("diffplug__spotless__079141262640.txt")
    union_ids, per_parser_ids = union_extract(body)
    actual_class, _, _, _ = union_classify(body)

    assert actual_class == "TEST_FAILURE"
    assert len(per_parser_ids["gradle"]) == 1
    assert len(per_parser_ids["maven"]) == 0
    assert len(per_parser_ids["pytest"]) == 0

    norm_extracted = {normalize_comparison_id(x) for x in union_ids}
    expected_ids = {
        "com.diffplug.gradle.spotless.AsciidocExtensionTest::spotlessCheckFailsOnUnformattedThenPassesAfterApply"
    }
    assert norm_extracted == expected_ids


def test_holdout_fixture_17_no_test_output():
    """Fixture 17 (apache__dolphinscheduler__082710858610.txt): Non-test log correctly classified as NO_TEST_OUTPUT."""
    body = _read_holdout_fixture("apache__dolphinscheduler__082710858610.txt")
    union_ids, per_parser_ids = union_extract(body)
    actual_class, _, _, _ = union_classify(body)

    assert actual_class == "NO_TEST_OUTPUT"
    assert len(union_ids) == 0
    assert len(per_parser_ids["gradle"]) == 0
    assert len(per_parser_ids["maven"]) == 0
    assert len(per_parser_ids["pytest"]) == 0


def test_holdout_fixture_14_gradle_bare_class_match():
    """Fixture 14 (gurkenlabs__litiengine__079032771640.txt): Bare class Gradle failure matches without fabrication."""
    body = _read_holdout_fixture("gurkenlabs__litiengine__079032771640.txt")
    union_ids, per_parser_ids = union_extract(body)
    actual_class, _, _, _ = union_classify(body)

    assert actual_class == "TEST_FAILURE"
    assert len(per_parser_ids["gradle"]) == 2
    assert len(per_parser_ids["maven"]) == 0
    assert len(per_parser_ids["pytest"]) == 0

    norm_extracted = {normalize_comparison_id(x) for x in union_ids}
    expected_ids = {
        "AlignTests::getClampedLocation_InPoint",
        "AlignTests::getClampedLocation_OffPoint",
    }
    assert norm_extracted == expected_ids


def test_holdout_fixture_15_gradle_bare_class_match():
    """Fixture 15 (mcreator__mcreator__081715271356.txt): Bare class Gradle failure matches without fabrication."""
    body = _read_holdout_fixture("mcreator__mcreator__081715271356.txt")
    union_ids, per_parser_ids = union_extract(body)
    actual_class, _, _, _ = union_classify(body)

    assert actual_class == "TEST_FAILURE"
    assert len(per_parser_ids["gradle"]) == 4
    assert len(per_parser_ids["maven"]) == 0
    assert len(per_parser_ids["pytest"]) == 0

    norm_extracted = {normalize_comparison_id(x) for x in union_ids}
    expected_ids = {
        "ReferencesFinderTest::testModElementUsagesSearch",
        "ReferencesFinderTest::testModelUsagesSearch",
        "ReferencesFinderTest::testStructureUsagesSearch",
        "ReferencesFinderTest::testTextureUsagesSearch",
    }
    assert norm_extracted == expected_ids


def test_evaluate_holdout_aggregate_metrics():
    """Holdout evaluation report satisfies regression floors with zero cross-firing.

    Measured values as of this commit:
      TP: 30, FP: 0, FN: 0, class_matches: 20, precision: 1.0000, recall: 1.0000, F1: 1.0000.

    These figures are FITTED, not held-out: this corpus drove four consecutive parser
    fixes and now functions as a development set. A third quarantined corpus is required
    before any generalisation claim reaches the paper.
    """
    report = evaluate_holdout()

    assert report.total_fixtures == 20
    assert report.total_expected == 30
    assert report.true_positives >= 30
    assert report.false_positives <= 0
    assert report.false_negatives <= 0
    assert report.class_matches >= 20
    assert report.precision >= 1.0
    assert report.recall >= 1.0
    assert report.cross_firing_count == 0

    # Per-harness counts
    assert report.harness_breakdown["pytest"].fixtures_count == 2
    assert report.harness_breakdown["Maven"].fixtures_count == 7
    assert report.harness_breakdown["Gradle"].fixtures_count == 7
    assert report.harness_breakdown["Other"].fixtures_count == 4
