"""Tests for src.harvest.frame — workflow classification, verdicts, resumability.

No network: all GitHub calls go through get_with_backoff and are intercepted
with `responses` at the transport layer, same convention as test_ratelimit.py.
"""

import csv

import responses

from src.harvest.frame import (
    RepoResult,
    classify_workflows,
    process_repo,
    run_frame,
)
from src.harvest.ratelimit import TokenPool

SINCE = "2026-05-07"


def _pool():
    return TokenPool(["tok_a"])


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

    # only owner/new-c should ever be fetched over the network
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
    assert len(responses.calls) == 2  # exactly the two calls for new-c

    attrition_rows = list(csv.DictReader(attrition_path.open(newline="", encoding="utf-8")))
    assert {r["repo"] for r in attrition_rows} == {"already-a", "already-b", "new-c"}
