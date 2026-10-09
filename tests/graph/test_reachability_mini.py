"""Tests for `analysis/reachability_mini.py` against the checked-in `minirepo`.

Every expected value is hand-derived from the fixture sources, not from the code:

* `tests/test_shapes.py` imports and calls `pkg/shapes.py` (`area`, `perimeter`);
* `CalculatorTest` calls `Calculator.add/subtract`, which call `Rounder.round`;
* `Rounder` is never called by a test directly, only through `Calculator`.
"""

from __future__ import annotations

import pytest

from analysis.reachability_mini import canonical_ids, reachable_tests, score_ids
from src.graph.build import build_graph_at, load_graph

JAVA = {"com.example.CalculatorTest#testAdd", "com.example.CalculatorTest#testSubtract"}
PY = {"tests/test_shapes.py::test_area", "tests/test_shapes.py::test_perimeter"}
CALC = "src/main/java/com/example/Calculator.java"
ROUNDER = "src/main/java/com/example/Rounder.java"


@pytest.fixture
def graph(minirepo_clone, minirepo_sha, tmp_path):
    stats = build_graph_at("acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=tmp_path / "graphs")
    return load_graph(stats.graph_path)


def test_python_change_reaches_only_python_tests(graph):
    assert {t for t, _, _ in reachable_tests(graph, ["pkg/shapes.py"])} == PY


def test_java_change_reaches_only_java_tests(graph):
    assert {t for t, _, _ in reachable_tests(graph, [CALC])} == JAVA


def test_collaborator_is_reached_through_its_caller_and_ranks_later(graph):
    via_calc = {t: h for t, h, _ in reachable_tests(graph, [CALC])}
    via_rounder = {t: h for t, h, _ in reachable_tests(graph, [ROUNDER])}
    assert set(via_rounder) == JAVA
    for t in JAVA:  # one more hop: test -> Calculator -> Rounder
        assert via_rounder[t] > via_calc[t]


def test_ranking_is_hop_then_test_id_and_reports_the_test_file(graph):
    ranked = reachable_tests(graph, ["pkg/shapes.py", CALC])
    assert [(h, t) for t, h, _ in ranked] == sorted((h, t) for t, h, _ in ranked)
    assert {f for _, _, f in ranked} == {"tests/test_shapes.py", "src/test/java/com/example/CalculatorTest.java"}


def test_unrelated_and_unknown_files_reach_nothing(graph):
    assert reachable_tests(graph, ["README.md", "not/in/graph.py"]) == []


def test_lossy_binding_maps_a_package_less_gradle_id_and_leaves_unknowns_unbound(graph):
    mapping = canonical_ids(graph, ["CalculatorTest#testAdd", "tests/test_shapes.py::test_area", "Nope#nothing"])
    assert mapping["CalculatorTest#testAdd"] == {"com.example.CalculatorTest#testAdd"}
    assert mapping["tests/test_shapes.py::test_area"] == {"tests/test_shapes.py::test_area"}
    assert mapping["Nope#nothing"] == set()


def test_score_ids_hand_computed(graph):
    gt = {"CalculatorTest#testAdd", "Nope#nothing", "tests/test_shapes.py::test_area"}
    mapping = canonical_ids(graph, gt)
    ranked = sorted(JAVA)  # R = both Java tests
    p, r, j, hits = score_ids(ranked, gt, mapping)
    # GT hit by R: testAdd only. R has 2 ids, 1 of them bound by some GT id.
    assert hits == 1
    assert p == pytest.approx(1 / 2)
    assert r == pytest.approx(1 / 3)  # unbound GT id stays in the denominator
    assert j == pytest.approx(1 / (2 + 3 - 1))
