"""Tests for base-run resolution against real raw data in data/raw.

Ground truth derivation commands and payload inspections are documented
verbatim in test docstrings.
"""

from __future__ import annotations

import pytest
from src.label.base_resolve import (
    BaseResolution,
    NoBaseRunError,
    build_commit_graph,
    resolve_base_run,
)
from tests.conftest import requires_data


@requires_data("data/raw")
def test_base_resolve_exact_real_payload() -> None:
    """Test exact base run resolution against real raw payloads in data/raw.

    Ground Truth Derivation:
    -----------------------
    Command to inspect head run:
      uv run python -c "
      import json
      from src.harvest.rawstore import RawStore
      s = RawStore()
      recs = s.read_records('apache/beam', 'runs', '00eb482640b2f52f2ba690845e123c9b42af61da')
      body = json.loads(recs[0].body)
      run = next(r for r in body['workflow_runs'] if r['id'] == 28986910981)
      print(run['workflow_id'], run['name'])
      "
      Output: 67750765 PreCommit Java

    Command to inspect base SHA runs at 58bac320ebd2601e6b66261b5e40a72d59161cff:
      uv run python -c "
      import json
      from src.harvest.rawstore import RawStore
      s = RawStore()
      recs = s.read_records('apache/beam', 'runs', '58bac320ebd2601e6b66261b5e40a72d59161cff')
      body = json.loads(recs[0].body)
      matching = [r for r in body['workflow_runs'] if r['workflow_id'] == 67750765]
      print([(r['id'], r['name'], r['run_started_at']) for r in matching])
      "
      Output: [(30538725876, 'PreCommit Java', '2026-08-20T04:22:42Z')]
    """
    res = resolve_base_run(
        repo="apache/beam",
        head_sha="00eb482640b2f52f2ba690845e123c9b42af61da",
        run_id=28986910981,
        workflow_id=67750765,
        base_sha="58bac320ebd2601e6b66261b5e40a72d59161cff",
    )
    assert res.status == "exact"
    assert res.base_sha == "58bac320ebd2601e6b66261b5e40a72d59161cff"
    assert res.base_run_id == 30538725876
    assert res.base_run_distance == 0
    assert res.can_emit_labels is True
    assert res.require_base_run_id() == 30538725876


@requires_data("data/raw", "data/clones")
def test_base_resolve_ancestor_real_payload() -> None:
    """Test ancestor base run resolution with 3-hop distance against real raw data.

    Ground Truth Derivation:
    -----------------------
    Base SHA: faba9f53eae8b7ca09051b12f99ea5e9f1663748
    Target Workflow ID: 80768812 ('Build and Test Workflow')

    Parent traversal in pull_commits (PR #7397):
      Hop 1: faba9f53eae8b7ca09051b12f99ea5e9f1663748 -> c1275763af98e5ecc3d8fbc8f6fcb8435f638dbe (no matching workflow run)
      Hop 2: c1275763af98e5ecc3d8fbc8f6fcb8435f638dbe -> 3260f5415dba4c21a0dd9353554ea3ccb2bc2a6f (no matching workflow run)
      Hop 3: 3260f5415dba4c21a0dd9353554ea3ccb2bc2a6f -> 0286c716de5206af6d25a4c5dca6835bdbcb5fac (has run 31308832690 of workflow 80768812)

    Command:
      uv run python -c "
      import json
      from src.harvest.rawstore import RawStore
      s = RawStore()
      recs = s.read_records('Stirling-Tools/Stirling-PDF', 'runs', '0286c716de5206af6d25a4c5dca6835bdbcb5fac')
      runs = json.loads(recs[0].body)['workflow_runs']
      print([r['id'] for r in runs if r['workflow_id'] == 80768812])
      "
      Output: [31308832690]

    Phase 017 amendment (spec 3a, Architect ruling)
    -----------------------------------------------
    This test previously asserted `status == "exact_green"` for run 31308832690
    on the strength of its `conclusion == "success"` alone. That expectation
    encoded the defect Phase 016-A found and Phase 017 was tasked with removing:
    a run conclusion is metadata about the run, not evidence about its tests, so
    it can never establish that the base was green (integrity invariant 6,
    ROADMAP §21.3).

    The ancestor-traversal ground truth above is unchanged and is still
    asserted. What changed is only what a *successful* base is allowed to
    resolve to. The assertions below are strengthened, not weakened: the
    resolution must now demote without log evidence, AND must still reach
    `exact_green` when that evidence exists.
    """
    # Without a verification record, a successful base emits nothing.
    res = resolve_base_run(
        repo="Stirling-Tools/Stirling-PDF",
        head_sha="0de2cdf979dbf76bdafb328d0e618ac358b7b452",
        run_id=31326869987,
        workflow_id=80768812,
        base_sha="faba9f53eae8b7ca09051b12f99ea5e9f1663748",
    )
    assert res.status == "no_base"
    assert res.base_sha == "0286c716de5206af6d25a4c5dca6835bdbcb5fac"
    assert res.base_run_id is None
    assert res.can_emit_labels is False
    assert res.base_parse_status == "unverified"

    # With a parsed base log in which tests were observed, the same ancestor
    # traversal resolves to exact_green at the same 3-hop distance.
    verified = resolve_base_run(
        repo="Stirling-Tools/Stirling-PDF",
        head_sha="0de2cdf979dbf76bdafb328d0e618ac358b7b452",
        run_id=31326869987,
        workflow_id=80768812,
        base_sha="faba9f53eae8b7ca09051b12f99ea5e9f1663748",
        base_verdicts={
            ("Stirling-Tools/Stirling-PDF", 31308832690): {
                "base_parse_status": "green_verified",
                "base_jobs_total": 1,
                "base_jobs_retrieved": 1,
            }
        },
    )
    assert verified.status == "exact_green"
    assert verified.base_sha == "0286c716de5206af6d25a4c5dca6835bdbcb5fac"
    assert verified.base_run_id == 31308832690
    assert verified.base_run_distance == 3
    assert verified.can_emit_labels is True
    assert verified.require_base_run_id() == 31308832690


def test_base_resolve_no_base_real_payload() -> None:
    """Test no_base resolution when neither base_sha nor any ancestor has a matching run.

    Ground Truth Derivation:
    -----------------------
    Repo: Stirling-Tools/Stirling-PDF
    Head SHA: 00023523de19eefcb66f2570735dc3ab526b85f2
    Base SHA: 5b9ef852abb971e4942caa8d6a3fd92b3257e331
    Target Workflow ID: 80768812
    """
    res = resolve_base_run(
        repo="Stirling-Tools/Stirling-PDF",
        head_sha="00023523de19eefcb66f2570735dc3ab526b85f2",
        run_id=25441351692,
        workflow_id=80768812,
        base_sha="5b9ef852abb971e4942caa8d6a3fd92b3257e331",
    )
    assert res.status == "no_base"
    assert res.base_run_id is None
    assert res.base_run_distance is None
    assert res.can_emit_labels is False


def test_no_base_cannot_be_mistaken_for_empty_failure_set() -> None:
    """Explicitly test Invariant 6: status='no_base' structurally prevents label emission.

    An unresolved base run MUST NOT provide a base_run_id that could be queried
    against parsed_outcomes to produce an empty set (which would wrongly look like
    'base was green').
    """
    res = BaseResolution(
        base_sha="abcdef1234567890abcdef1234567890abcdef12",
        base_run_id=None,
        base_run_distance=None,
        status="no_base",
    )
    assert not res.can_emit_labels
    assert res.base_run_id is None

    with pytest.raises(NoBaseRunError, match="Cannot emit labels: base run unresolved"):
        res.require_base_run_id()


def test_workflow_id_mismatch_resolves_to_no_base() -> None:
    """Test that a run of a different workflow at base_sha is rejected."""
    # At 58bac320ebd2601e6b66261b5e40a72d59161cff, workflow 67750765 exists, but workflow 999999999 does not.
    res = resolve_base_run(
        repo="apache/beam",
        head_sha="00eb482640b2f52f2ba690845e123c9b42af61da",
        run_id=28986910981,
        workflow_id=999999999,
        base_sha="58bac320ebd2601e6b66261b5e40a72d59161cff",
    )
    assert res.status == "no_base"
    assert res.base_run_id is None
    assert res.can_emit_labels is False


def test_base_resolution_dataclass_invariants() -> None:
    """Test structural safety invariants on BaseResolution dataclass construction."""
    # Invalid status
    with pytest.raises(ValueError, match="invalid resolution status"):
        BaseResolution(base_sha="abc", base_run_id=1, base_run_distance=0, status="invalid")

    # no_base cannot have base_run_id
    with pytest.raises(ValueError, match="base_run_id must be None"):
        BaseResolution(base_sha="abc", base_run_id=123, base_run_distance=None, status="no_base")

    # no_base cannot have base_run_distance
    with pytest.raises(ValueError, match="base_run_distance must be None"):
        BaseResolution(base_sha="abc", base_run_id=None, base_run_distance=2, status="no_base")

    # exact cannot have None base_run_id
    with pytest.raises(ValueError, match="base_run_id cannot be None"):
        BaseResolution(base_sha="abc", base_run_id=None, base_run_distance=0, status="exact")

    # exact must have distance == 0
    with pytest.raises(ValueError, match="base_run_distance must be 0"):
        BaseResolution(base_sha="abc", base_run_id=123, base_run_distance=2, status="exact")

    # ancestor cannot have None base_run_id
    with pytest.raises(ValueError, match="base_run_id cannot be None"):
        BaseResolution(base_sha="abc", base_run_id=None, base_run_distance=2, status="ancestor")

    # ancestor must have distance > 0
    with pytest.raises(ValueError, match="base_run_distance must be positive"):
        BaseResolution(base_sha="abc", base_run_id=123, base_run_distance=0, status="ancestor")


def test_base_resolve_branch_prior() -> None:
    """Test branch_prior resolution fallback using branch-run index."""
    from src.label.base_resolve import resolve_base_run, parse_iso
    
    # Mocking runs in the branch_prior_index
    # We want a run strictly before head_ts.
    # head_ts: 2026-08-20T12:00:00Z
    # r1: 2026-08-19T12:00:00Z (wrong workflow)
    # r2: 2026-08-19T13:00:00Z (correct workflow, correct branch)
    # r3: 2026-08-20T11:00:00Z (correct workflow, wrong branch)
    # r4: 2026-08-20T13:00:00Z (correct workflow, correct branch, but strictly AFTER head_ts)
    
    repo = "test/repo"
    head_sha = "head123"
    run_id = 999
    workflow_id = 42
    
    runs_cache = {
        (repo, head_sha): [
            {
                "id": run_id,
                "workflow_id": workflow_id,
                "run_started_at": "2026-08-20T12:00:00Z",
                "pull_requests": [{"base": {"ref": "main"}}]
            }
        ]
    }
    
    branch_prior_index = {
        repo: [
            {"id": 1, "workflow_id": 99, "_ts": parse_iso("2026-08-19T12:00:00Z"), "head_branch": "main", "head_sha": "sha1"},
            {"id": 2, "workflow_id": 42, "_ts": parse_iso("2026-08-19T13:00:00Z"), "head_branch": "main", "head_sha": "sha2"},
            {"id": 3, "workflow_id": 42, "_ts": parse_iso("2026-08-20T11:00:00Z"), "head_branch": "other", "head_sha": "sha3"},
            {"id": 4, "workflow_id": 42, "_ts": parse_iso("2026-08-20T13:00:00Z"), "head_branch": "main", "head_sha": "sha4"},
        ]
    }
    
    res = resolve_base_run(
        repo=repo,
        head_sha=head_sha,
        run_id=run_id,
        workflow_id=workflow_id,
        base_sha=None, # Trigger fallback
        raw_root=".",
        store=None, # Need a mock or we pass runs_cache
        runs_cache=runs_cache,
        branch_prior_index=branch_prior_index
    )
    assert res.status == "branch_prior"
    assert res.base_run_id == 2
    assert res.base_sha == "sha2"
    assert res.base_time_gap_seconds == parse_iso("2026-08-20T12:00:00Z") - parse_iso("2026-08-19T13:00:00Z")


def test_resolve_bases_outgoing_params_and_pagination(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that analysis.resolve_bases passes branch, created, and per_page=100
    on the initial workflow runs request, and passes params=None on subsequent Link-header requests."""
    import unittest.mock
    import pandas as pd
    from analysis.resolve_bases import run as run_resolve

    calls: list[tuple[str, dict | None]] = []

    # Mock response object
    class MockResponse:
        def __init__(self, status_code: int, data: dict, headers: dict):
            self.status_code = status_code
            self._data = data
            self.headers = headers
            self.text = ""

        def json(self) -> dict:
            return self._data

    resp1 = MockResponse(
        status_code=200,
        data={
            "workflow_runs": [
                {
                    "id": 888888,
                    "head_sha": "unrelated_sha",
                    "run_started_at": "2026-08-19T10:00:00Z",
                    "conclusion": "success",
                }
            ]
        },
        headers={"Link": '<https://api.github.com/next_page_url?page=2>; rel="next"'},
    )

    resp2 = MockResponse(
        status_code=200,
        data={
            "workflow_runs": [
                {
                    "id": 999999,
                    "head_sha": "base_sha_123",
                    "run_started_at": "2026-08-19T09:00:00Z",
                    "conclusion": "success",
                }
            ]
        },
        headers={},
    )

    def mock_get(url: str, params: dict | None = None, pool: object = None) -> MockResponse:
        calls.append((url, params))
        if len(calls) == 1:
            return resp1
        return resp2

    monkeypatch.setattr("analysis.resolve_bases.get_with_backoff", mock_get)
    monkeypatch.setattr("analysis.resolve_bases.build_commit_graph", lambda repo, store=None: {"base_sha_123": []})

    # Mock dataframes
    mock_res = pd.DataFrame([
        {"run_id": 101, "repo": "test/repo", "status": "no_base", "base_sha": "base_sha_123", "base_run_id": None, "base_run_distance": None}
    ])
    mock_inst = pd.DataFrame([
        {
            "run_id": 101,
            "repo": "test/repo",
            "workflow_id": 42,
            "base_ref": "main",
            "base_sha": "base_sha_123",
            "language": "Python",
            "run_started_at": "2026-08-20T12:00:00Z",
        }
    ])

    def mock_read_parquet(path: str) -> pd.DataFrame:
        if "base_resolution_new" in path:
            return mock_res
        return mock_inst

    monkeypatch.setattr("pandas.read_parquet", mock_read_parquet)

    df_out = run_resolve(limit=1, python_first=True)
    assert len(df_out) == 1
    assert df_out.iloc[0]["status"] == "exact_green"
    assert df_out.iloc[0]["base_run_id"] == 999999

    # Verify requests
    assert len(calls) == 2
    # Call 1: must have branch, created, per_page
    url1, params1 = calls[0]
    assert "actions/workflows/42/runs" in url1
    assert params1 is not None
    assert params1["branch"] == "main"
    assert params1["created"] == "<=2026-08-20"
    assert params1["per_page"] == 100

    # Call 2: must have params=None since Link header already includes query params
    url2, params2 = calls[1]
    assert url2 == "https://api.github.com/next_page_url?page=2"
    assert params2 is None

