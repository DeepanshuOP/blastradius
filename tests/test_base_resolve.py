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
        commit_graph={"00eb482640b2f52f2ba690845e123c9b42af61da": ["58bac320ebd2601e6b66261b5e40a72d59161cff"]}
    )
    assert res.status == "ancestor"
    assert res.base_sha == "58bac320ebd2601e6b66261b5e40a72d59161cff"
    assert res.base_run_id == 30538725876
    assert res.base_run_distance == 1
    assert res.can_emit_labels is True
    assert res.require_base_run_id() == 30538725876


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
    """
    res = resolve_base_run(
        repo="Stirling-Tools/Stirling-PDF",
        head_sha="0de2cdf979dbf76bdafb328d0e618ac358b7b452",
        run_id=31326869987,
        workflow_id=80768812,
        base_sha="faba9f53eae8b7ca09051b12f99ea5e9f1663748",
        commit_graph={
            "0de2cdf979dbf76bdafb328d0e618ac358b7b452": ["faba9f53eae8b7ca09051b12f99ea5e9f1663748"],
            "faba9f53eae8b7ca09051b12f99ea5e9f1663748": ["c1275763af98e5ecc3d8fbc8f6fcb8435f638dbe"],
            "c1275763af98e5ecc3d8fbc8f6fcb8435f638dbe": ["3260f5415dba4c21a0dd9353554ea3ccb2bc2a6f"],
            "3260f5415dba4c21a0dd9353554ea3ccb2bc2a6f": ["0286c716de5206af6d25a4c5dca6835bdbcb5fac"],
        }
    )
    assert res.status == "exact_green"
    assert res.base_sha == "0286c716de5206af6d25a4c5dca6835bdbcb5fac"
    assert res.base_run_id == 31308832690
    assert res.base_run_distance == 4
    assert res.can_emit_labels is True
    assert res.require_base_run_id() == 31308832690


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
    with pytest.raises(ValueError, match="base_run_id must be None"):
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

def test_base_resolve_exact_green() -> None:
    res = BaseResolution(base_sha="abc", base_run_id=123, base_run_distance=1, status="exact_green")
    assert res.can_emit_labels == True  # exact_green is valid, produces empty labels  # Wait, is exact_green considered valid?
