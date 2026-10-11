"""The website's capability matrix obeys its own rules (see the header of docs/compare_matrix.yaml)."""

from __future__ import annotations

from pathlib import Path

from analysis import compare_matrix as cm


def test_the_checked_in_matrix_has_no_violations() -> None:
    doc = cm.load()
    assert len(doc["rows"]) == 10 and len(doc["columns"]) == 8
    assert cm.validate(doc) == []


def test_an_unsupported_yes_for_another_work_is_caught() -> None:
    doc = cm.load()
    row = next(r for r in doc["rows"] if r["id"] == "free_tier")
    row["cells"]["agentless"] = {"value": "yes", "source": "docs/LITERATURE.md #31: \"runs for free\""}
    row["cells"]["br"]["proof"] = ["tests/test_cost_report.py::test_no_such_test"]
    bad = cm.validate(doc)
    assert any("agentless" in b and "not found verbatim" in b for b in bad)
    assert any("test_no_such_test" in b for b in bad)


def test_test_exists_reads_function_definitions_only() -> None:
    assert cm.test_exists("tests/test_cost_report.py::test_the_recorded_bot_run_is_one_call_of_1495_tokens")
    assert not cm.test_exists("tests/test_cost_report.py::nope")
    assert not cm.test_exists("tests/missing.py::test_x", Path("."))
