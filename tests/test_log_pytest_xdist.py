"""BlastRadius — Pytest-xdist Multi-Worker Log Parser Tests.

Per ROADMAP §9.1 (T1.1d), DECISIONS.md (D-09, D-25), and amendment rulings:
- Tests extraction of pytest test outcomes from inverted pytest-xdist progress lines:
    [gw<N>] [<pct>%] (FAILED|ERROR) <node_id>
- Tests status mapping: FAILED -> "fail", ERROR -> "error" (Amendment 2).
- Tests XFAIL/XPASS produce no failure outcomes (Amendment 3).
- Tests parser confidence constants and dedup enrichment (Amendment 4).
- Tests full fixture contracts on real regression fixture logs.
"""

from pathlib import Path
import pytest

from src.parse.dispatch import (
    classify_dispatch_log,
    dispatch_parse_log,
    dispatch_parse_log_with_stats,
)
from src.parse.log_pytest import (
    CONFIDENCE_PYTEST_PROGRESS,
    CONFIDENCE_PYTEST_SUMMARY,
    classify_pytest_log,
    extract_pytest_failing_test_ids,
    parse_pytest_log,
    parse_pytest_log_with_stats,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "regression" / "pytest_xdist"


def test_xdist_fixture_081645128008_seventeen_error_identifiers() -> None:
    """Verify 17 setup/collection ERROR outcomes from real beam xdist log 081645128008."""
    log_path = FIXTURES_DIR / "apache__beam__081645128008.txt"
    body = log_path.read_text(encoding="utf-8")

    expected_ids = {
        "apache_beam/ml/rag/enrichment/milvus_search_it_test.py::TestMilvusSearchEnrichment::test_invalid_query_on_non_existent_collection",
        "apache_beam/ml/rag/enrichment/milvus_search_it_test.py::TestMilvusSearchEnrichment::test_invalid_query_on_non_existent_field",
        "apache_beam/ml/rag/ingestion/milvus_search_it_test.py::TestMilvusVectorWriterConfig::test_invalid_write_on_non_existent_partition",
        "apache_beam/ml/rag/ingestion/milvus_search_it_test.py::TestMilvusVectorWriterConfig::test_write_on_auto_id_primary_key",
        "apache_beam/ml/rag/ingestion/milvus_search_it_test.py::TestMilvusVectorWriterConfig::test_write_on_existent_collection_with_default_schema",
        "apache_beam/ml/rag/ingestion/milvus_search_it_test.py::TestMilvusVectorWriterConfig::test_write_with_batching",
        "apache_beam/ml/rag/ingestion/milvus_search_it_test.py::TestMilvusVectorWriterConfig::test_write_with_custom_column_specifications",
        "apache_beam/ml/rag/enrichment/milvus_search_it_test.py::TestMilvusSearchEnrichment::test_vector_search_with_inner_product_similarity",
        "apache_beam/ml/rag/enrichment/milvus_search_it_test.py::TestMilvusSearchEnrichment::test_empty_input_chunks",
        "apache_beam/ml/rag/enrichment/milvus_search_it_test.py::TestMilvusSearchEnrichment::test_filtered_search_with_cosine_similarity_and_batching",
        "apache_beam/ml/rag/ingestion/milvus_search_it_test.py::TestMilvusVectorWriterConfig::test_invalid_write_on_missing_primary_key_in_entity",
        "apache_beam/ml/rag/enrichment/milvus_search_it_test.py::TestMilvusSearchEnrichment::test_keyword_search_with_inner_product_sparse_embedding",
        "apache_beam/ml/rag/ingestion/milvus_search_it_test.py::TestMilvusVectorWriterConfig::test_invalid_write_on_non_existent_collection",
        "apache_beam/ml/rag/enrichment/milvus_search_it_test.py::TestMilvusSearchEnrichment::test_vector_search_with_euclidean_distance",
        "apache_beam/ml/rag/enrichment/milvus_search_it_test.py::TestMilvusSearchEnrichment::test_filtered_search_with_bm25_full_text_and_batching",
        "apache_beam/ml/rag/enrichment/milvus_search_it_test.py::TestMilvusSearchEnrichment::test_hybrid_search",
        "apache_beam/ml/rag/ingestion/milvus_search_it_test.py::TestMilvusVectorWriterConfig::test_idempotent_write",
    }

    # 1. Test parse_pytest_log_with_stats
    outcomes, stats = parse_pytest_log_with_stats(body, repo="apache/beam", job_id=81645128008)
    assert len(outcomes) == 17
    assert stats.total_outcomes == 17
    assert stats.progress_error_count == 17
    assert stats.progress_fail_count == 0

    extracted_ids = {o.test_id for o in outcomes}
    assert extracted_ids == expected_ids

    for o in outcomes:
        assert o.status == "error"
        assert o.parser_confidence == CONFIDENCE_PYTEST_PROGRESS
        assert o.repo == "apache/beam"
        assert o.job_id == 81645128008

    # 2. Test classify_pytest_log
    status, fids, is_trunc = classify_pytest_log(body)
    assert status == "TEST_FAILURE"
    assert fids == expected_ids
    assert is_trunc is False

    # 3. Test dispatcher
    disp_outcomes, disp_stats = dispatch_parse_log_with_stats(body, repo="apache/beam", job_id=81645128008)
    assert len(disp_outcomes) == 17
    assert {o.test_id for o in disp_outcomes} == expected_ids

    d_status, d_fids, d_trunc = classify_dispatch_log(body)
    assert d_status == "TEST_FAILURE"
    assert d_fids == expected_ids


def test_xdist_fixture_077952110001_single_failed_identifier() -> None:
    """Verify single test assertion FAILED outcome from real beam xdist log 077952110001."""
    log_path = FIXTURES_DIR / "apache__beam__077952110001.txt"
    body = log_path.read_text(encoding="utf-8")

    expected_id = (
        "apache_beam/runners/dataflow/internal/apiclient_test.py::UtilTest::test_environment_packages_with_hash"
    )

    outcomes, stats = parse_pytest_log_with_stats(body, repo="apache/beam", job_id=77952110001)
    assert len(outcomes) == 1
    assert stats.total_outcomes == 1
    assert stats.progress_fail_count == 1
    assert stats.progress_error_count == 0

    outcome = outcomes[0]
    assert outcome.test_id == expected_id
    assert outcome.status == "fail"
    assert outcome.parser_confidence == CONFIDENCE_PYTEST_PROGRESS

    status, fids, is_trunc = classify_pytest_log(body)
    assert status == "TEST_FAILURE"
    assert fids == {expected_id}

    d_status, d_fids, d_trunc = classify_dispatch_log(body)
    assert d_status == "TEST_FAILURE"
    assert d_fids == {expected_id}


def test_synthetic_xdist_status_mapping_and_confidence() -> None:
    """Verify exact status mapping (FAILED->fail, ERROR->error) and confidence under xdist."""
    log_text = """
[gw0] [ 10%] FAILED tests/test_calc.py::test_add
[gw1] [ 20%] ERROR tests/test_service.py::test_init
[gw2] [ 30%] PASSED tests/test_ok.py::test_pass
[gw3] [ 40%] SKIPPED tests/test_skip.py::test_skip
==== 1 failed, 1 error, 1 passed, 1 skipped in 2.0s ====
"""
    outcomes, stats = parse_pytest_log_with_stats(log_text)
    assert len(outcomes) == 2
    assert stats.progress_fail_count == 1
    assert stats.progress_error_count == 1

    by_id = {o.test_id: o for o in outcomes}
    assert by_id["tests/test_calc.py::test_add"].status == "fail"
    assert by_id["tests/test_calc.py::test_add"].parser_confidence == CONFIDENCE_PYTEST_PROGRESS

    assert by_id["tests/test_service.py::test_init"].status == "error"
    assert by_id["tests/test_service.py::test_init"].parser_confidence == CONFIDENCE_PYTEST_PROGRESS


def test_synthetic_xdist_xfail_xpass_produce_no_failures() -> None:
    """Verify Amendment 3: XFAIL and XPASS produce no failure outcomes."""
    log_text = """
[gw0] [ 50%] XFAIL tests/test_feature.py::test_known_defect
[gw1] [ 60%] XPASS tests/test_feature.py::test_unexpected_fix
[gw2] [100%] PASSED tests/test_feature.py::test_regular
=========================== short test summary info ============================
XFAIL tests/test_feature.py::test_known_defect - reason: known defect
XPASS tests/test_feature.py::test_unexpected_fix - reason: fix landed
==== 1 passed, 1 xfailed in 1.5s ====
"""
    outcomes, stats = parse_pytest_log_with_stats(log_text)
    assert outcomes == []
    assert stats.total_outcomes == 0

    failing_ids = extract_pytest_failing_test_ids(log_text)
    assert failing_ids == set()

    # Verify classify_pytest_log classifies clean execution when passed/xfailed footer is present
    status, fids, _ = classify_pytest_log(log_text)
    assert status == "TEST_RAN_CLEAN"
    assert fids == set()


def test_synthetic_xdist_progress_dedup_merge_enrichment() -> None:
    """Verify xdist progress failure enriched by summary block elevates confidence and message."""
    log_text = """
[gw0] [ 50%] FAILED tests/test_unit.py::test_sample
=========================== short test summary info ============================
FAILED tests/test_unit.py::test_sample - AssertionError: assert False is True
==== 1 failed in 0.5s ====
"""
    outcomes, stats = parse_pytest_log_with_stats(log_text)
    assert len(outcomes) == 1
    assert stats.dedup_merged_count == 1
    assert stats.summary_fail_count == 1
    assert stats.progress_fail_count == 1

    outcome = outcomes[0]
    assert outcome.test_id == "tests/test_unit.py::test_sample"
    assert outcome.status == "fail"
    assert outcome.parser_confidence == CONFIDENCE_PYTEST_SUMMARY
    assert outcome.failure_message == "AssertionError: assert False is True"


def test_synthetic_xdist_negative_cases_and_clean_execution() -> None:
    """Verify non-pytest lines and Gradle/Maven task failures are rejected."""
    gradle_log = """
> Task :sdks:python:testPy314 FAILED
BUILD FAILED in 10s
"""
    outcomes, stats = parse_pytest_log_with_stats(gradle_log)
    assert outcomes == []

    maven_log = """
[ERROR] COMPILATION ERROR :
[ERROR] /path/to/Foo.java:[10,5] cannot find symbol
[INFO] BUILD FAILURE
"""
    outcomes_mvn, _ = parse_pytest_log_with_stats(maven_log)
    assert outcomes_mvn == []
