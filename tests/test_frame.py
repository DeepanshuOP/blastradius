"""Tests for src.harvest.frame — workflow classification, verdicts, resumability.

No network: all GitHub calls go through get_with_backoff and are intercepted
with `responses` at the transport layer, same convention as test_ratelimit.py.
"""

import csv
import time
from unittest.mock import Mock

import pytest
import responses

from src.harvest.frame import (
    AbortRun,
    RepoResult,
    classify_workflows,
    process_repo,
    run_frame,
)
from src.harvest.ratelimit import TokenPool

SINCE = "2026-05-07"
RATE_LIMIT_URL = "https://api.github.com/rate_limit"


def _pool():
    return TokenPool(["tok_a"])


def _mock_rate_limit_ok():
    responses.add(responses.GET, RATE_LIMIT_URL, json={"resources": {"core": {"remaining": 5000}}}, status=200)


def _row(name="owner/repo", lang="Java", stars="600", commits="1200", branch="main", license_="MIT"):
    return {
        "name": name,
        "mainLanguage": lang,
        "stargazers": stars,
        "commits": commits,
        "defaultBranch": branch,
        "license": license_,
    }


def _runs_url(owner, repo):
    return f"https://api.github.com/repos/{owner}/{repo}/actions/runs"


def _workflows_url(owner, repo):
    return f"https://api.github.com/repos/{owner}/{repo}/actions/workflows"


def test_workflow_classification_returns_exactly_test_intent_ids():
    workflows = [
        {"id": 1, "name": "CI", "path": ".github/workflows/ci.yml"},
        {"id": 2, "name": "Release", "path": ".github/workflows/release.yml"},
        {"id": 3, "name": "Docs", "path": ".github/workflows/docs.yml"},
        {"id": 4, "name": "Pytest", "path": ".github/workflows/pytest.yml"},
    ]

    assert classify_workflows(workflows) == [1, 4]


@responses.activate
def test_total_count_99_gets_no_ci_and_100_gets_kept():
    responses.add(responses.GET, _runs_url("owner", "repo99"), json={"total_count": 99}, status=200)
    responses.add(
        responses.GET,
        _workflows_url("owner", "repo99"),
        json={"workflows": [{"id": 1, "name": "CI", "path": ".github/workflows/ci.yml"}]},
        status=200,
    )
    responses.add(responses.GET, _runs_url("owner", "repo100"), json={"total_count": 100}, status=200)
    responses.add(
        responses.GET,
        _workflows_url("owner", "repo100"),
        json={"workflows": [{"id": 1, "name": "CI", "path": ".github/workflows/ci.yml"}]},
        status=200,
    )

    result_99 = process_repo(_row(name="owner/repo99"), _pool(), SINCE)
    result_100 = process_repo(_row(name="owner/repo100"), _pool(), SINCE)

    assert result_99.verdict == "no_ci"
    assert result_99.n_runs_90d == "99"
    assert result_100.verdict == "kept"
    assert result_100.n_runs_90d == "100"
    assert result_100.test_workflow_ids == "1"


@responses.activate
def test_runs_but_zero_test_workflows_gets_no_test_workflow():
    responses.add(responses.GET, _runs_url("owner", "repo"), json={"total_count": 150}, status=200)
    responses.add(
        responses.GET,
        _workflows_url("owner", "repo"),
        json={
            "workflows": [
                {"id": 1, "name": "Release", "path": ".github/workflows/release.yml"},
                {"id": 2, "name": "Docs", "path": ".github/workflows/docs.yml"},
            ]
        },
        status=200,
    )

    result = process_repo(_row(), _pool(), SINCE)

    assert result.verdict == "no_test_workflow"
    assert result.test_workflow_ids == ""


def _write_input_csv(path, names):
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["name", "mainLanguage", "stargazers", "commits", "defaultBranch", "license"]
        )
        writer.writeheader()
        for name in names:
            writer.writerow(_row(name=name))


def _write_partial_csv(path, results):
    from src.harvest.frame import PARTIAL_COLUMNS

    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=PARTIAL_COLUMNS)
        writer.writeheader()
        for result in results:
            writer.writerow(vars(result))


@responses.activate
def test_resumability_skips_repos_already_in_partial(tmp_path):
    input_path = tmp_path / "repos_raw.csv"
    partial_path = tmp_path / "repos.partial.csv"
    output_path = tmp_path / "repos.csv"
    attrition_path = tmp_path / "attrition_stage.csv"

    names = ["owner/already-a", "owner/already-b", "owner/new-c"]
    _write_input_csv(input_path, names)

    already_done = [
        RepoResult(
            owner="owner", repo="already-a", lang="Java", stars="600", commits="1200",
            default_branch="main", license="MIT", n_runs_90d="500", n_workflows="1",
            n_test_workflows="1", test_workflow_ids="1", verdict="kept",
        ),
        RepoResult(
            owner="owner", repo="already-b", lang="Java", stars="600", commits="1200",
            default_branch="main", license="MIT", n_runs_90d="10", n_workflows="1",
            n_test_workflows="0", test_workflow_ids="", verdict="no_ci",
        ),
    ]
    _write_partial_csv(partial_path, already_done)

    # only owner/new-c should ever be fetched over the network (plus the
    # one startup token-validation ping)
    _mock_rate_limit_ok()
    responses.add(responses.GET, _runs_url("owner", "new-c"), json={"total_count": 200}, status=200)
    responses.add(
        responses.GET,
        _workflows_url("owner", "new-c"),
        json={"workflows": [{"id": 9, "name": "CI", "path": ".github/workflows/ci.yml"}]},
        status=200,
    )

    summary = run_frame(
        pool=_pool(),
        input_path=input_path,
        partial_path=partial_path,
        output_path=output_path,
        attrition_path=attrition_path,
        since=SINCE,
        limit=20,
    )

    assert summary["newly_processed"] == 1
    assert summary["total_recorded"] == 3
    assert len(responses.calls) == 3  # 1 rate_limit validation + 2 for new-c


def _setup_run(tmp_path, names):
    input_path = tmp_path / "repos_raw.csv"
    partial_path = tmp_path / "repos.partial.csv"
    output_path = tmp_path / "repos.csv"
    attrition_path = tmp_path / "attrition_stage.csv"
    _write_input_csv(input_path, names)
    return input_path, partial_path, output_path, attrition_path


@responses.activate
def test_404_on_call_1_writes_terminal_verdict_naming_status(tmp_path):
    _mock_rate_limit_ok()
    responses.add(responses.GET, _runs_url("owner", "gone-repo"), status=404)

    input_path, partial_path, output_path, attrition_path = _setup_run(tmp_path, ["owner/gone-repo"])

    summary = run_frame(
        pool=_pool(), input_path=input_path, partial_path=partial_path,
        output_path=output_path, attrition_path=attrition_path, since=SINCE, limit=20,
    )

    assert summary["newly_processed"] == 1
    rows = list(csv.DictReader(partial_path.open(newline="", encoding="utf-8")))
    assert len(rows) == 1
    assert rows[0]["verdict"] == "api_error"
    assert rows[0]["failing_call"] == "runs"
    assert rows[0]["status"] == "404"
    assert rows[0]["exception_class"] == "HTTPError"


@responses.activate
def test_403_remaining_0_not_written_to_partial(tmp_path):
    _mock_rate_limit_ok()
    # GitHub always sends X-RateLimit-Reset alongside a rate-limit 403; a
    # fixture without it is unfaithful to the real API.
    reset_at = str(int(time.time()) + 1800)
    for _ in range(6):
        responses.add(
            responses.GET,
            _runs_url("owner", "exhausted-repo"),
            status=403,
            headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": reset_at},
        )

    input_path, partial_path, output_path, attrition_path = _setup_run(tmp_path, ["owner/exhausted-repo"])

    summary = run_frame(
        pool=_pool(), input_path=input_path, partial_path=partial_path,
        output_path=output_path, attrition_path=attrition_path, since=SINCE, limit=20,
    )

    assert summary["newly_processed"] == 0
    assert not partial_path.exists() or list(
        csv.DictReader(partial_path.open(newline="", encoding="utf-8"))
    ) == []


@responses.activate
def test_transient_failures_abort_run_after_ladder_exhausted(tmp_path):
    """Supersedes the old test_5_consecutive_transient_failures_abort_run,
    which encoded the pre-governor contract: abort the instant the 5th
    consecutive transient failure is seen. TransientGovernor (this task)
    deliberately replaced that with pause-and-probe, so AbortRun now fires
    only once the pause ladder itself is exhausted — proven here by
    checking the full 1260s ladder was actually slept through (via the
    injected fake sleep) rather than skipped, i.e. the abort was not simply
    "on the 5th consecutive transient alone."
    """
    _mock_rate_limit_ok()  # consumed once, by validate_tokens' startup ping
    responses.add(responses.GET, RATE_LIMIT_URL, status=503)  # every ladder probe after that fails

    names = [f"owner/flaky{i}" for i in range(5)]
    for i in range(5):
        responses.add(responses.GET, _runs_url("owner", f"flaky{i}"), status=401)

    input_path, partial_path, output_path, attrition_path = _setup_run(tmp_path, names)

    fake_sleep = Mock()

    with pytest.raises(AbortRun, match="ladder exhausted"):
        run_frame(
            pool=_pool(), input_path=input_path, partial_path=partial_path,
            output_path=output_path, attrition_path=attrition_path, since=SINCE, limit=20,
            sleep=fake_sleep, monotonic=lambda: 0.0,
        )

    assert fake_sleep.call_count == 3
    assert sum(call.args[0] for call in fake_sleep.call_args_list) == 1260.0
    assert not partial_path.exists()


@responses.activate
def test_transient_failure_retried_on_next_invocation(tmp_path):
    input_path, partial_path, output_path, attrition_path = _setup_run(tmp_path, ["owner/flaky-repo"])

    _mock_rate_limit_ok()
    responses.add(responses.GET, _runs_url("owner", "flaky-repo"), status=401)

    run_frame(
        pool=_pool(), input_path=input_path, partial_path=partial_path,
        output_path=output_path, attrition_path=attrition_path, since=SINCE, limit=20,
    )
    assert not partial_path.exists()

    _mock_rate_limit_ok()
    responses.add(responses.GET, _runs_url("owner", "flaky-repo"), json={"total_count": 200}, status=200)
    responses.add(
        responses.GET,
        _workflows_url("owner", "flaky-repo"),
        json={"workflows": [{"id": 1, "name": "CI", "path": ".github/workflows/ci.yml"}]},
        status=200,
    )

    run_frame(
        pool=_pool(), input_path=input_path, partial_path=partial_path,
        output_path=output_path, attrition_path=attrition_path, since=SINCE, limit=20,
    )

    rows = list(csv.DictReader(partial_path.open(newline="", encoding="utf-8")))
    assert len(rows) == 1
    assert rows[0]["verdict"] == "kept"


@responses.activate
def test_startup_validation_aborts_on_bad_token_naming_index(tmp_path):
    responses.add(responses.GET, RATE_LIMIT_URL, status=401)

    input_path, partial_path, output_path, attrition_path = _setup_run(tmp_path, ["owner/whatever"])

    with pytest.raises(AbortRun, match="token_idx"):
        run_frame(
            pool=_pool(), input_path=input_path, partial_path=partial_path,
            output_path=output_path, attrition_path=attrition_path, since=SINCE, limit=20,
        )

    assert not partial_path.exists()
