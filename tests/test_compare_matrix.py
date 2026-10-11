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


def test_every_vendor_cell_carries_a_source_url() -> None:
    doc = cm.load()
    products = doc["products"]
    assert len(products["rows"]) == 9 and len(products["columns"]) == 5
    assert cm.validate_products(products) == []
    row = products["rows"][0]
    row["cells"]["datadog"]["source"] = "docs/LITERATURE.md"
    row["cells"]["copilot"]["source"] = ""
    row["cells"]["develocity"]["value"] = "yes-ish"
    bad = cm.validate_products(products)
    assert any("datadog" in b and "vendor URL" in b for b in bad)
    assert any("copilot" in b and "no source" in b for b in bad)
    assert any("develocity" in b and "value" in b for b in bad)


def test_the_vendor_sources_are_the_pages_the_operator_named() -> None:
    urls = {c["source"] for r in cm.load()["products"]["rows"] for k, c in r["cells"].items() if k != "br"}
    joined = " ".join(urls)
    for u in ("https://docs.develocity.ai/2026.3/guides/predictive-test-selection/",
              "https://www.cloudbees.com/blog/how-cloudbees-smart-tests-works",
              "https://docs.datadoghq.com/tests/test_impact_analysis/how_it_works/",
              "https://github.blog/changelog/2026-05-18-one-click-fixes-for-failing-actions-with-copilot-cloud-agent/",
              "https://github.blog/changelog/2026-06-04-fix-with-copilot-for-failing-actions-now-in-pro-pro-and-max/"):
        assert u in joined
