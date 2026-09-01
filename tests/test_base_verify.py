"""Integrity invariant 6: a successful base run that ran no tests is not green.

Ground truth is hand-written in `tests/fixtures/base_verify/EXPECTED.md`. The
fixture is a real `agno-agi/agno` base run — conclusion `success`, one job,
"Lint PR Title and Body" — extracted unmodified from `data/raw`.

Fixture values are ground truth. If one of these fails, fix the code.
"""

import json
from pathlib import Path

import pytest

from src.label.base_resolve import (
    GREEN_VERDICTS,
    BaseResolution,
    _resolve_successful_base,
)
from src.parse.dispatch import classify_dispatch_log

FIXTURES = Path(__file__).parent / "fixtures" / "base_verify"
JOBS_JSON = FIXTURES / "agno-agi__agno__run32727954465__jobs.json"
LOG_TXT = FIXTURES / "agno-agi__agno__job97433407085__log.txt"

REPO = "agno-agi/agno"
BASE_RUN_ID = 32727954465


def test_fixture_run_concluded_success_with_a_single_job():
    payload = json.loads(JOBS_JSON.read_text())

    assert payload["total_count"] == 1
    job = payload["jobs"][0]
    assert job["conclusion"] == "success"
    assert job["name"] == "Lint PR Title and Body"


def test_that_successful_run_parses_to_no_test_output():
    classification, ids, _truncated = classify_dispatch_log(
        LOG_TXT.read_text(encoding="utf-8", errors="replace")
    )

    assert classification == "NO_TEST_OUTPUT"
    assert ids == set()


def test_success_plus_no_test_output_resolves_to_no_base_and_emits_nothing():
    verdicts = {
        (REPO, BASE_RUN_ID): {
            "base_parse_status": "no_tests_confirmed",
            "base_jobs_total": 1,
            "base_jobs_retrieved": 1,
        }
    }

    res = _resolve_successful_base(
        repo=REPO,
        base_sha="0" * 40,
        base_run_id=BASE_RUN_ID,
        base_run_distance=0,
        failed_status="exact",
        base_verdicts=verdicts,
    )

    assert res.status == "no_base"
    assert res.base_run_id is None
    assert res.can_emit_labels is False
    assert res.base_parse_status == "no_tests_confirmed"


def test_an_unverified_successful_base_also_emits_nothing():
    """No verification record at all is not permission to assume green."""
    res = _resolve_successful_base(
        repo=REPO,
        base_sha="0" * 40,
        base_run_id=BASE_RUN_ID,
        base_run_distance=0,
        failed_status="exact",
        base_verdicts=None,
    )

    assert res.status == "no_base"
    assert res.can_emit_labels is False
    assert res.base_parse_status == "unverified"


@pytest.mark.parametrize(
    "parse_status",
    ["no_tests_confirmed", "no_tests_unverifiable", "unretrievable", "unverified", None],
)
def test_exact_green_is_rejected_without_observed_tests(parse_status):
    with pytest.raises(ValueError, match="requires base_parse_status"):
        BaseResolution(
            base_sha="0" * 40,
            base_run_id=BASE_RUN_ID,
            base_run_distance=0,
            status="exact_green",
            base_parse_status=parse_status,
        )


@pytest.mark.parametrize("parse_status", sorted(GREEN_VERDICTS))
def test_exact_green_is_allowed_only_with_observed_tests(parse_status):
    res = BaseResolution(
        base_sha="0" * 40,
        base_run_id=BASE_RUN_ID,
        base_run_distance=0,
        status="exact_green",
        base_parse_status=parse_status,
    )

    assert res.status == "exact_green"
    assert res.can_emit_labels is True


def test_a_base_that_failed_its_tests_is_not_green():
    verdicts = {
        (REPO, BASE_RUN_ID): {
            "base_parse_status": "base_failed",
            "base_jobs_total": 1,
            "base_jobs_retrieved": 1,
        }
    }

    res = _resolve_successful_base(
        repo=REPO,
        base_sha="0" * 40,
        base_run_id=BASE_RUN_ID,
        base_run_distance=0,
        failed_status="exact",
        base_verdicts=verdicts,
    )

    assert res.status == "exact"
    assert res.base_run_id == BASE_RUN_ID
