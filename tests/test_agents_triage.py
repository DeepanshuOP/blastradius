"""Triage agent and the 2.0 pipeline (scenario 4), offline.

Scenario 4 replays the one model reply recorded in `src/agents/demo/llm_cache.jsonl`; every other
step is real (real git, real pytest, the E1 and E2 models on disk).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.agents.triage import CLASSES, TriageAgent

pytest.importorskip("networkx")
pytest.importorskip("graphify")


def write_history(path: Path) -> None:
    ev = [
        {"ts": "2026-01-01T00:00:00+00:00", "commit": "r1", "test_id": "t::A", "outcome": "failed", "message": "boom 1", "branch": "main"},
        {"ts": "2026-01-01T00:00:00+00:00", "commit": "r1", "test_id": "t::B", "outcome": "passed", "message": "", "branch": "main"},
        {"ts": "2026-01-02T00:00:00+00:00", "commit": "r2", "test_id": "t::A", "outcome": "failed", "message": "boom 2", "branch": "main"},
        {"ts": "2026-01-03T00:00:00+00:00", "commit": "r3", "test_id": "t::D", "outcome": "failed", "message": "disk full", "branch": "main"},
        # the run being triaged: its own failures must never count as history
        {"ts": "2026-01-04T00:00:00+00:00", "commit": "cur", "test_id": "t::C", "outcome": "failed", "message": "fresh", "branch": "main"},
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(e) for e in ev) + "\n")


FAILURES = [
    {"test_id": "t::A", "outcome": "failed", "message": "boom 3"},       # failed in r1, r2 and same message shape
    {"test_id": "t::C", "outcome": "failed", "message": "fresh"},        # only fails in the commit being triaged
    {"test_id": "t::E", "outcome": "failed", "message": "boom 4"},       # never failed, but "boom N" was seen
]


def test_rules_classify_by_branch_history_and_message(tmp_path) -> None:
    h = tmp_path / "h.jsonl"
    write_history(h)
    rep = TriageAgent(use_model=False).run(FAILURES, h, branch="main", commit="cur")
    by = {f.test_id: f for f in rep.failures}
    assert rep.model == "rules"
    assert by["t::A"].klass == "inherited" and by["t::A"].route == "ignore"   # R-branch fires
    assert by["t::C"].klass == "mine" and by["t::C"].route == "repair"        # its own failure is excluded
    assert by["t::E"].klass == "flaky" and by["t::E"].route == "rerun"        # R-msg only: no prior failure of E
    assert rep.counts() == {"mine": 1, "inherited": 1, "flaky": 1}


def test_a_failure_is_not_its_own_history(tmp_path) -> None:
    h = tmp_path / "h.jsonl"
    write_history(h)
    with_self = TriageAgent(use_model=False).run([FAILURES[1]], h, commit="")      # commit unknown: counted
    without = TriageAgent(use_model=False).run([FAILURES[1]], h, commit="cur")
    assert with_self.failures[0].klass == "inherited" and without.failures[0].klass == "mine"


def test_model_output_is_well_formed(tmp_path) -> None:
    h = tmp_path / "h.jsonl"
    write_history(h)
    agent = TriageAgent()
    assert agent.name in ("e2-lgbm-v1", "rules")
    rep = agent.run(FAILURES, h, branch="main", commit="cur")
    assert [f.test_id for f in rep.failures] == ["t::A", "t::C", "t::E"]
    for f in rep.failures:
        assert f.klass in CLASSES and 0.0 <= f.confidence <= 1.0 and f.route in ("repair", "ignore", "rerun")


def test_empty_history_makes_everything_mine(tmp_path) -> None:
    rep = TriageAgent(use_model=False).run(FAILURES, tmp_path / "none.jsonl")
    assert rep.counts() == {"mine": 3, "inherited": 0, "flaky": 0}


@pytest.fixture(scope="module")
def demo(tmp_path_factory):
    from src.agents.demo.run_demo import run_demo

    return run_demo(tmp_path_factory.mktemp("agents-demo-v2"))


def test_scenario_four_repairs_and_deploys(demo) -> None:
    s = {x["id"]: x for x in demo["scenarios"]}["repaired"]
    steps = {st["agent"]: st for st in s["steps"]}
    assert s["outcome"] == "Deployed"
    first = steps["Regression Suite Agent"]
    assert first["status"] == "failed" and first["outputs"]["full"]["failed"] == 3   # the 3 new FESTIVE20 tests
    assert first["outputs"]["first failing test"] and first["outputs"]["first failure position"] >= 1
    tri = steps["Triage Agent"]["outputs"]["classes"]
    assert set(tri.values()) == {"mine"} and len(tri) == 3
    rep = steps["Repair Agent"]
    assert rep["outputs"]["accepted"] and rep["outputs"]["files"] == ["shopcart/pricing.py"]
    assert "shopcart/pricing.py::apply_discount" in rep["inputs"]["chunks shown to the model"]
    assert steps["Regression Suite Agent (after repair)"]["outputs"]["verdict"] == "PASS"
    assert steps["PR Reviewer Agent"]["outputs"]["verdict"] == "APPROVE"
    assert steps["Build & Deploy Agent"]["outputs"]["status"] == "deployed"
    # the repaired file really is the cap, not the floor
    repo = Path(s["repo"])
    assert "discount = min(discount, cap)" in (repo / "shopcart" / "pricing.py").read_text()


def test_repair_failure_blocks_the_merge(tmp_path) -> None:
    """With no model the Repair agent only notifies: nothing is reviewed, merged or deployed."""
    from src.agents.cli import pipeline
    from src.agents.demo.run_demo import PATCHES, STORY, baseline, make_repo

    repo = make_repo(tmp_path / "shopcart")
    baseline(repo)
    res = pipeline(repo, STORY, provider="offline", patch=str(PATCHES / "festive20_bug.json"), stages="2.0",
                   repair_llm=None)
    assert res["outcome"] == "Repair failed, team notified"
    assert "review" not in res and "deploy" not in res
    log = (repo / ".blastradius" / "notifications.jsonl").read_text().splitlines()
    assert json.loads(log[-1])["event"] == "repair_failed"
