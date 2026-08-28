"""Tests for analysis/fixture_score.py scorecard evaluation on dev corpus.

Per ROADMAP §25.3, §34.4, §37.1, AGENTS.md, and Amendments 1 & 2.
Evaluates standalone default dispatch scoring (46 TP / 0 FP / 0 FN), explicit
single-harness injection, and split-check injection decoupling.
"""

from __future__ import annotations

from pathlib import Path
import pytest

from analysis.fixture_score import score_corpus
from src.parse.dispatch import extract_dispatch_failing_test_ids
from src.parse.log_maven import (
    classify_maven_log,
    extract_maven_failing_test_ids,
)


def test_score_corpus_standalone_default() -> None:
    """(a) Standalone default uses parser dispatch and scores 46 TP / 0 FP / 0 FN (100% precision & recall)."""
    report = score_corpus()

    assert report.total_fixtures == 40
    assert report.total_expected == 46
    assert report.total_extracted == 46
    assert report.true_positives == 46
    assert report.false_positives == 0
    assert report.false_negatives == 0
    assert report.precision == 1.0
    assert report.recall == 1.0
    assert report.f1 == 1.0
    assert report.class_matches == 40
    assert report.classification_accuracy == 1.0
    assert report.no_failure_fps == 0


def test_score_corpus_explicit_single_harness_maven_injection() -> None:
    """(b) Explicit single-harness injection still works and reports Maven-only numbers."""
    report = score_corpus(
        classify_fn=classify_maven_log,
        extract_fn=extract_maven_failing_test_ids,
    )

    assert report.total_fixtures == 40
    assert report.total_expected == 46
    assert report.total_extracted == 19
    assert report.true_positives == 19
    assert report.false_positives == 0
    assert report.false_negatives == 27
    assert report.precision == 1.0
    assert report.class_matches == 28
    assert report.classification_accuracy == 0.70


def test_score_corpus_split_check_extract_fn_only() -> None:
    """(c) THE SPLIT-CHECK CASE: inject extract_fn ONLY, leaving classify_fn None.

    The classifier must default to dispatch's classify_dispatch_log, NOT log_yield's
    coupled fallback (which would collapse clean logs to NO_TEST_OUTPUT).
    Proves Amendment 1 landed.
    """
    report = score_corpus(extract_fn=extract_dispatch_failing_test_ids)

    assert report.total_fixtures == 40
    assert report.total_expected == 46
    assert report.total_extracted == 46
    assert report.true_positives == 46
    assert report.false_positives == 0
    assert report.false_negatives == 0
    assert report.class_matches == 40
    assert report.classification_accuracy == 1.0

    # Specifically verify fixture 35 (clean run) was classified as TEST_RAN_CLEAN by dispatch
    s35 = next(s for s in report.scores if s.index == 35)
    assert s35.expected_class == "TEST_RAN_CLEAN"
    assert s35.actual_class == "TEST_RAN_CLEAN"
    assert s35.class_correct is True
