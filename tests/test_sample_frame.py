"""Tests for scripts.sample_frame — seeded, language-stratified frame sampling.

No network. Real fixture CSVs in tests/fixtures/ (sample_frame_repos.csv,
sample_frame_repos_small_java.csv, sample_frame_attrition_stage.csv) —
synthetic but real files, never mocks, never the live 3,671-row export.
"""

from pathlib import Path

import pytest

from scripts.sample_frame import (
    SAMPLE_PER_LANGUAGE,
    SEED,
    build_attrition,
    draw_sample,
    read_csv,
)

FIXTURES = Path(__file__).parent / "fixtures"
REPOS_FIXTURE = FIXTURES / "sample_frame_repos.csv"
SMALL_JAVA_FIXTURE = FIXTURES / "sample_frame_repos_small_java.csv"
ATTRITION_FIXTURE = FIXTURES / "sample_frame_attrition_stage.csv"


def _kept_rows():
    _, rows = read_csv(REPOS_FIXTURE)
    return rows


def test_determinism_same_seed_produces_identical_output():
    rows = _kept_rows()

    sample_a, reserve_a = draw_sample(rows, seed=SEED)
    sample_b, reserve_b = draw_sample(rows, seed=SEED)

    assert sample_a == sample_b
    assert reserve_a == reserve_b


def test_different_seed_produces_a_different_set():
    rows = _kept_rows()

    sample_a, _ = draw_sample(rows, seed=SEED)
    sample_b, _ = draw_sample(rows, seed=SEED + 1)

    keys_a = {(r["owner"], r["repo"]) for r in sample_a}
    keys_b = {(r["owner"], r["repo"]) for r in sample_b}
    assert keys_a != keys_b


def test_stratification_exactly_150_of_each_language():
    rows = _kept_rows()

    sample, _ = draw_sample(rows, seed=SEED)

    java_count = sum(1 for r in sample if r["lang"] == "Java")
    python_count = sum(1 for r in sample if r["lang"] == "Python")
    assert java_count == SAMPLE_PER_LANGUAGE == 150
    assert python_count == SAMPLE_PER_LANGUAGE == 150


def test_disjointness_sample_and_reserve_share_nothing():
    rows = _kept_rows()

    sample, reserve = draw_sample(rows, seed=SEED)

    sample_keys = {(r["owner"], r["repo"]) for r in sample}
    reserve_keys = {(r["owner"], r["repo"]) for r in reserve}
    assert sample_keys.isdisjoint(reserve_keys)


def test_completeness_sample_and_reserve_union_equals_kept_set():
    rows = _kept_rows()

    sample, reserve = draw_sample(rows, seed=SEED)

    sample_keys = {(r["owner"], r["repo"]) for r in sample}
    reserve_keys = {(r["owner"], r["repo"]) for r in reserve}
    kept_keys = {(r["owner"], r["repo"]) for r in rows}
    assert sample_keys | reserve_keys == kept_keys


def test_undersized_language_raises_instead_of_undersampling():
    _, rows = read_csv(SMALL_JAVA_FIXTURE)

    with pytest.raises(ValueError, match="Java"):
        draw_sample(rows, seed=SEED)


def test_build_attrition_funnel_counts():
    _, attrition_rows = read_csv(ATTRITION_FIXTURE)

    result = build_attrition(attrition_rows)
    stages = {stage["stage"]: stage for stage in result["stages"]}

    assert stages["seart_export"]["output_count"] == 8
    assert stages["ci_live"]["input_count"] == 8
    assert stages["ci_live"]["output_count"] == 5  # 8 - 2 no_ci - 1 api_error
    assert stages["has_test_workflow"]["input_count"] == 5
    assert stages["has_test_workflow"]["output_count"] == 4  # 5 - 1 no_test_workflow


def test_build_attrition_records_api_error_with_repo_name():
    _, attrition_rows = read_csv(ATTRITION_FIXTURE)

    result = build_attrition(attrition_rows)

    assert len(result["exclusions"]) == 1
    exclusion = result["exclusions"][0]
    assert exclusion["owner"] == "a"
    assert exclusion["repo"] == "err1"
    assert exclusion["reason"] == "api_error"
    assert exclusion["failing_call"] == "runs"


def test_build_attrition_stages_5_to_8_are_null_not_invented():
    _, attrition_rows = read_csv(ATTRITION_FIXTURE)

    result = build_attrition(attrition_rows)
    stages = {stage["stage"]: stage for stage in result["stages"]}

    not_yet_measured = [s for s in result["stages"] if s["status"] == "not_yet_measured"]
    assert len(not_yet_measured) == 4
    for stage in not_yet_measured:
        assert stage["input_count"] is None
        assert stage["output_count"] is None
        assert stage["removed_count"] is None
