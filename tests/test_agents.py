"""Agentic workflow (D-55): five agents run end to end on the checked-in shopcart sample repo.

The sample repo (`src/agents/demo/sample_repo`) and the recorded change sets
(`src/agents/demo/patches`) are real files; nothing is mocked. Expected values are
hand-computed from the sample code and are ground truth: if a test here fails,
fix the code, not the expectation.

Hand count: the sample has 15 tests (catalog 2, pricing 4, cart 3, tax 2,
inventory 2, receipt 2). A change to pricing/cart reaches the 4 pricing and 3
cart tests (7) and none of the other 8. The FESTIVE20 change set adds 2 pricing
tests and 1 cart test (18 in all); the scope-creep change set also breaks both
receipt tests.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.agents.codebase import is_test_path, tokens
from src.agents.coding import CodingAgent, CodingError, _safe_path
from src.agents.forge import LocalForge
from src.agents.impact import ImpactAnalysis, ImpactAnalysisAgent
from src.agents.llm import LLMError, OfflineLLM, extract_json, get_llm

pytest.importorskip("networkx")
pytest.importorskip("graphify")

STORY = ("As a shopper, I want to apply the discount code FESTIVE20 at checkout to get 20% off "
         "my cart total, capped at Rs 500.")
AT_RISK = {
    "tests/test_cart.py::test_add_rejects_zero_quantity",
    "tests/test_cart.py::test_subtotal_sums_lines",
    "tests/test_cart.py::test_total_applies_discount_then_tax",
    "tests/test_pricing.py::test_code_is_case_insensitive",
    "tests/test_pricing.py::test_no_code_leaves_subtotal",
    "tests/test_pricing.py::test_unknown_code_is_ignored",
    "tests/test_pricing.py::test_welcome10_takes_ten_percent",
}


@pytest.fixture(scope="module")
def demo(tmp_path_factory):
    from src.agents.demo.run_demo import run_demo

    return run_demo(tmp_path_factory.mktemp("agents-demo"))


@pytest.fixture()
def repo(tmp_path):
    from src.agents.demo.run_demo import make_repo

    return make_repo(tmp_path / "shopcart")


def test_tokens_split_camel_snake_and_stopwords():
    assert tokens("applyDiscount to the cart_total") == ["apply", "discount", "cart", "total"]


def test_is_test_path():
    assert is_test_path("tests/test_cart.py")
    assert is_test_path("src/test/java/org/x/CartTest.java")
    assert not is_test_path("shopcart/cart.py")


def test_extract_json_handles_fences_and_rejects_prose():
    assert extract_json('Sure:\n```json\n{"a": 1}\n```') == {"a": 1}
    with pytest.raises(LLMError):
        extract_json("no json here")


def test_offline_flag_forces_offline_provider(monkeypatch):
    monkeypatch.setenv("BR_OFFLINE", "1")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    assert isinstance(get_llm("anthropic"), OfflineLLM)


def test_impact_analysis_selects_exactly_the_reachable_tests(repo):
    analysis, out = ImpactAnalysisAgent("offline").run(STORY, repo, title="FESTIVE20")
    assert "shopcart/pricing.py" in analysis.change_files
    assert {t.test_id for t in analysis.tests} == AT_RISK
    assert len(analysis.unaffected_tests) == 8
    assert not any(t.startswith(("tests/test_tax", "tests/test_receipt")) for t in {x.test_id for x in analysis.tests})
    assert (out / "impact.md").read_text(encoding="utf-8").startswith("# Impact Analysis: FESTIVE20")
    again = ImpactAnalysis.load(out / "impact.json")
    assert {t.test_id for t in again.tests} == AT_RISK and again.base_sha == analysis.base_sha


def test_coding_agent_needs_a_change_source_offline(repo):
    analysis, _ = ImpactAnalysisAgent("offline").run(STORY, repo)
    with pytest.raises(CodingError, match="no LLM"):
        CodingAgent("offline").run(analysis, repo, LocalForge(repo, repo / ".blastradius"))


def test_coding_agent_refuses_paths_outside_the_tree(repo):
    with pytest.raises(CodingError):
        _safe_path(repo, "../escape.py")
    with pytest.raises(CodingError):
        _safe_path(repo, ".git/config")


def test_clean_scenario_merges_deploys_and_passes(demo):
    s = {x["id"]: x for x in demo["scenarios"]}["clean"]
    agents = {st["agent"]: st for st in s["steps"]}
    assert s["outcome"] == "Deployed"
    assert agents["Coding Agent"]["outputs"]["changed files"] == ["shopcart/pricing.py", "tests/test_cart.py", "tests/test_pricing.py"]
    assert agents["PR Reviewer Agent"]["outputs"]["verdict"] == "APPROVE"
    repo = Path(s["repo"])
    merge = agents["PR Reviewer Agent"]["outputs"]["commit id"]
    parents = __import__("subprocess").check_output(["git", "-C", str(repo), "rev-list", "--parents", "-n1", merge], text=True).split()
    assert len(parents) == 3  # a real merge commit: itself + two parents
    assert (repo / ".blastradius" / "deploy" / "CURRENT").read_text().strip().startswith(merge)
    assert agents["Regression Suite Agent"]["outputs"]["verdict"] == "PASS"
    assert agents["Regression Suite Agent"]["outputs"]["selection"] == "10/18"


def test_out_of_scope_change_is_blocked_under_strict_policy(demo):
    s = {x["id"]: x for x in demo["scenarios"]}["blocked"]
    review = {st["agent"]: st for st in s["steps"]}["PR Reviewer Agent"]
    assert review["outputs"]["verdict"] == "REQUEST_CHANGES" and not review["outputs"]["merged"]
    scope = next(c for c in review["outputs"]["checks"] if c["check"] == "scope")
    assert not scope["ok"] and "shopcart/receipt.py" in scope["detail"]
    assert s["outcome"] == "Blocked at review"


def test_build_failure_notifies_and_regression_reports_missed_failures(demo):
    s = {x["id"]: x for x in demo["scenarios"]}["build-fails"]
    agents = {st["agent"]: st for st in s["steps"]}
    assert agents["Build & Deploy Agent"]["outputs"]["status"] == "build_failed"
    assert [n["event"] for n in s["notifications"]] == ["build_failed"]
    log = Path(s["repo"]) / ".blastradius" / "notifications.jsonl"
    assert json.loads(log.read_text().splitlines()[-1])["event"] == "build_failed"
    assert not (Path(s["repo"]) / ".blastradius" / "deploy" / "CURRENT").exists()
    reg = agents["Regression Suite Agent"]["outputs"]
    assert reg["impact recall"] == "0/2"
    assert reg["missed failures"] == ["tests/test_receipt.py::test_format_rupees",
                                      "tests/test_receipt.py::test_receipt_line_contains_amount"]


def test_regression_history_feeds_the_next_impact_analysis(demo):
    s = {x["id"]: x for x in demo["scenarios"]}["build-fails"]
    repo = Path(s["repo"])
    analysis, _ = ImpactAnalysisAgent("offline").run("Show the rupee sign on receipt lines", repo)
    assert analysis.history_used
    receipt = [t for t in analysis.tests if t.file == "tests/test_receipt.py"]
    assert receipt and all("failed 1/" in " ".join(t.reasons) for t in receipt)
