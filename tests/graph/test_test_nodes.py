"""Tests for test-node typing, `test_id` binding and the test→source bridge.

Every expected value is hand-written against the real checked-in tree at
`tests/fixtures/graph/minirepo/`, whose two test modules were written to make
all three §29.6 binding strategies observable:

* `src/test/java/com/example/CalculatorTest.java` — JUnit 5, in the Maven test
  root, calling into `Calculator` (direct), named after it (convention), and
  mirroring its directory (layout);
* `tests/test_shapes.py` — pytest, importing and calling `pkg/shapes.py`;
* `src/main/java/com/example/Rounder.java` — reached only *through* `Calculator`,
  so it checks that a collaborator is not mistaken for a test subject by name.
"""

from __future__ import annotations

import pytest

from src.graph.build import build_graph_at, load_graph
from src.graph.test_nodes import (
    CONFIDENCE_SCORES,
    NODE_TYPES,
    bind_test_ids,
    classify_node,
)

#: The canonical `test_id` of every individual test case in the fixture,
#: hand-derived from §29.6's shapes: `{package}.{Class}#{method}` for Java and
#: `{module_path}::{func}` for Python.
EXPECTED_TEST_IDS = {
    "com.example.CalculatorTest#testAdd",
    "com.example.CalculatorTest#testSubtract",
    "tests/test_shapes.py::test_area",
    "tests/test_shapes.py::test_perimeter",
}

#: Every node the fixture types as `test`: two Java cases, their class and file,
#: two Python cases and their module.
EXPECTED_TEST_NODE_COUNT = 7


@pytest.fixture
def minirepo_graph(minirepo_clone, minirepo_sha, tmp_path):
    """The built graph of the fixture at its single commit."""
    stats = build_graph_at(
        "acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=tmp_path / "graphs"
    )
    return load_graph(stats.graph_path)


# --------------------------------------------------------------------------
# classification
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "source_file,expected",
    [
        ("src/test/java/com/example/FooTest.java", "test"),
        ("src/test/kotlin/com/example/FooTest.kt", "test"),
        ("src/integrationTest/java/com/example/FooIT.java", "test"),
        ("tests/test_shapes.py", "test"),
        ("test/helpers.py", "test"),
        ("pkg/thing_test.py", "test"),
        ("pkg/test_thing.py", "test"),
        ("app/FooTest.java", "test"),
        ("app/FooTests.java", "test"),
        ("app/FooTestCase.java", "test"),
        ("src/main/java/com/example/Foo.java", "source"),
        ("pkg/shapes.py", "source"),
        ("pom.xml", "build"),
        ("build.gradle", "build"),
        ("build.gradle.kts", "build"),
        ("pyproject.toml", "build"),
        ("setup.py", "build"),
        (".github/workflows/ci.yml", "config"),
        ("tox.ini", "config"),
        ("conftest.py", "config"),
    ],
)
def test_classify_node_by_path(source_file, expected):
    record = {"id": "n", "label": source_file.rsplit("/", 1)[-1], "source_file": source_file,
              "file_type": "code"}
    assert classify_node(record) == expected
    assert expected in NODE_TYPES


def test_classify_node_promotes_a_test_symbol_outside_a_test_path():
    """A pytest function in a production path is still a test. The AST signal is
    what catches it; the path heuristic alone would call it source."""
    record = {"id": "n", "label": "test_thing()", "source_file": "pkg/shapes.py",
              "file_type": "code", "_callable": True}
    assert classify_node(record) == "source"
    assert classify_node(record, is_test_symbol=True) == "test"


def test_classify_node_declines_nodes_it_does_not_own():
    """A Graphify `rationale` node (a docstring) and an unresolved external
    symbol belong to none of the four types, and must stay untyped rather than
    be forced into `source`."""
    assert classify_node({"id": "n", "label": "A docstring.", "file_type": "rationale",
                          "source_file": "pkg/shapes.py"}) is None
    assert classify_node({"id": "n", "label": "org.junit.jupiter.api.Test",
                          "file_type": "code", "source_file": ""}) is None


def test_build_leaves_no_source_file_node_untyped(minirepo_graph):
    untyped = [
        node
        for node, data in minirepo_graph.nodes(data=True)
        if data.get("node_type") is None
        and data.get("source_file")
        and data.get("file_type") != "rationale"
    ]
    assert untyped == []


def test_the_fixture_types_the_expected_nodes(minirepo_graph):
    counts: dict[str, int] = {}
    for _, data in minirepo_graph.nodes(data=True):
        key = data.get("node_type")
        counts[key] = counts.get(key, 0) + 1

    assert counts["test"] == EXPECTED_TEST_NODE_COUNT
    assert counts["source"] == 12
    # The 3 untyped: two docstring `rationale` nodes and the external
    # `org.junit.jupiter.api.Test` symbol, which has no source file.
    assert counts[None] == 3
    assert "build" not in counts and "config" not in counts, (
        "the builder dispatches only .java/.py, so pom.xml never becomes a node"
    )


def test_junit_annotated_methods_are_typed_as_tests(minirepo_graph):
    """Graphify models `@Test` as a `references` edge to the annotation symbol
    rather than as a node attribute, so that edge is the AST signal."""
    for node, data in minirepo_graph.nodes(data=True):
        if node.endswith(("_testadd", "_testsubtract")):
            assert data["node_type"] == "test"


def test_a_collaborator_reached_only_through_the_subject_stays_source(minirepo_graph):
    """`Rounder` is constructed inside the test but is not its subject; it must
    not be typed as a test just because a test touches it."""
    rounder = [
        data
        for node, data in minirepo_graph.nodes(data=True)
        if "rounder" in node and data.get("source_file", "").endswith("Rounder.java")
    ]
    assert rounder, "the fixture must contain Rounder nodes"
    assert all(data["node_type"] == "source" for data in rounder)


# --------------------------------------------------------------------------
# test_id binding
# --------------------------------------------------------------------------


def test_test_nodes_bind_to_the_canonical_test_id(minirepo_graph):
    bound = {
        data["test_id"]
        for _, data in minirepo_graph.nodes(data=True)
        if data.get("test_id")
    }
    assert bound == EXPECTED_TEST_IDS


def test_test_ids_round_trip_through_normalize_test_id(minirepo_graph):
    """The ids this layer writes must be exactly what the frozen Week-1 contract
    produces, or the join key differs between the graph and the labels."""
    from src.parse.test_ids import normalize_test_id

    for _, data in minirepo_graph.nodes(data=True):
        canonical = data.get("test_id")
        if not canonical:
            continue
        again = normalize_test_id(canonical)
        assert again is not None, canonical
        assert again.canonical == canonical


def test_test_ids_are_repo_relative_not_worktree_absolute(minirepo_graph):
    """Regression guard: the resolver runs before Graphify relativizes paths, so
    a Python `test_id` once carried the absolute worktree path
    (`/tmp/br-wt-.../tree/tests/test_shapes.py::test_area`) and could never
    match a CI id."""
    for _, data in minirepo_graph.nodes(data=True):
        canonical = data.get("test_id") or ""
        assert not canonical.startswith("/"), canonical
        assert "br-wt-" not in canonical, canonical


def test_containers_do_not_get_a_test_id(minirepo_graph):
    """A test file and a test class are containers, not cases. Giving them an id
    would inflate the binding numerator with things CI never reports."""
    for node, data in minirepo_graph.nodes(data=True):
        if data.get("node_type") != "test":
            continue
        label = str(data.get("label") or "")
        if label.endswith((".java", ".py")) or data.get("_callable_class"):
            assert data.get("test_id") is None, node


def test_every_bound_node_carries_the_lossy_binding_key(minirepo_graph):
    """D-25: `test_id` is the published join key and `graph_binding_key` is the
    internal lossy one. Both must be present, and the key must be the derived
    form of the id, never a second canonical."""
    from src.parse.test_ids import derive_node_id

    for _, data in minirepo_graph.nodes(data=True):
        if not data.get("test_id"):
            continue
        assert data["graph_binding_key"] == derive_node_id(data["test_id"])


# --------------------------------------------------------------------------
# test → source edges
# --------------------------------------------------------------------------


def test_all_three_binding_strategies_are_emitted(minirepo_graph):
    present = {
        key for _, _, key in minirepo_graph.edges(keys=True)
    } & set(CONFIDENCE_SCORES)
    assert present == set(CONFIDENCE_SCORES)


def test_each_strategy_carries_its_own_confidence(minirepo_graph):
    """§10.3 step 3: emit all three with *distinct* confidence so a model can
    learn which to trust. Collapsing them to one score throws that away."""
    for _, _, key, data in minirepo_graph.edges(keys=True, data=True):
        if key not in CONFIDENCE_SCORES:
            continue
        confidence, score = CONFIDENCE_SCORES[key]
        assert data["confidence"] == confidence
        assert data["confidence_score"] == score
    assert CONFIDENCE_SCORES["tests"][1] > CONFIDENCE_SCORES["tests_by_convention"][1]
    assert (
        CONFIDENCE_SCORES["tests_by_convention"][1] > CONFIDENCE_SCORES["tests_by_layout"][1]
    )


def test_direct_dependency_binds_the_java_test_method_to_the_method_it_calls(
    minirepo_graph,
):
    assert minirepo_graph.has_edge(
        "src_test_java_com_example_calculatortest_calculatortest_testadd",
        "src_main_java_com_example_calculator_calculator_add",
        key="tests",
    )


def test_direct_dependency_binds_the_pytest_module_to_the_module_it_imports(
    minirepo_graph,
):
    assert minirepo_graph.has_edge("tests_test_shapes", "pkg_shapes", key="tests")


def test_naming_convention_binds_the_test_class_to_its_subject_class(minirepo_graph):
    """`CalculatorTest` → `Calculator`, the class — not `.Calculator()`, the
    constructor, which an earlier version matched because stripping Graphify's
    label decoration makes both read `Calculator`."""
    assert minirepo_graph.has_edge(
        "src_test_java_com_example_calculatortest_calculatortest",
        "src_main_java_com_example_calculator_calculator",
        key="tests_by_convention",
    )
    assert not minirepo_graph.has_edge(
        "src_test_java_com_example_calculatortest_calculatortest",
        "src_main_java_com_example_calculator_calculator_calculator",
        key="tests_by_convention",
    )


def test_naming_convention_binds_a_pytest_function_to_its_subject_function(
    minirepo_graph,
):
    assert minirepo_graph.has_edge(
        "tests_test_shapes_test_area", "pkg_shapes_area", key="tests_by_convention"
    )


def test_directory_mirroring_binds_across_the_maven_layout(minirepo_graph):
    """`src/test/java/com/example/CalculatorTest.java` ↔
    `src/main/java/com/example/Calculator.java`."""
    assert minirepo_graph.has_edge(
        "src_test_java_com_example_calculatortest",
        "src_main_java_com_example_calculator",
        key="tests_by_layout",
    )


def test_a_direct_binding_and_a_convention_binding_coexist(minirepo_graph):
    """`test_area` both calls and is named after `area`. Both strategies must be
    recorded, with their own confidences — that is the whole point of emitting
    three."""
    assert minirepo_graph.has_edge("tests_test_shapes_test_area", "pkg_shapes_area", key="tests")
    assert minirepo_graph.has_edge(
        "tests_test_shapes_test_area", "pkg_shapes_area", key="tests_by_convention"
    )


def test_binding_edges_only_ever_leave_a_test_node(minirepo_graph):
    for src, dst, key in minirepo_graph.edges(keys=True):
        if key in CONFIDENCE_SCORES:
            assert minirepo_graph.nodes[src]["node_type"] == "test", f"{src} -> {dst}"
            assert minirepo_graph.nodes[dst]["node_type"] == "source", f"{src} -> {dst}"


# --------------------------------------------------------------------------
# graph_node_binding_rate
# --------------------------------------------------------------------------


def test_binding_rate_counts_exact_matches(minirepo_graph):
    report = bind_test_ids(minirepo_graph, sorted(EXPECTED_TEST_IDS), repo="acme/minirepo")

    assert report.n_observed == 4
    assert report.n_bound == 4
    assert report.n_bound_exact == 4
    assert report.n_bound_lossy == 0
    assert report.as_fraction() == "4/4"
    assert report.rate == 1.0
    assert report.unbound_sample == []


def test_binding_rate_recovers_a_bare_class_id_through_the_lossy_key(minirepo_graph):
    """A Gradle corpus reports `CalculatorTest#testAdd` with no package, so an
    exact match is impossible however good the graph is. D-25's lossy key is
    what recovers it, and it is counted separately because a suffix can
    collide."""
    report = bind_test_ids(
        minirepo_graph, ["CalculatorTest#testAdd"], repo="acme/minirepo"
    )

    assert report.n_observed == 1
    assert report.n_bound == 1
    assert report.n_bound_exact == 0
    assert report.n_bound_lossy == 1


def test_binding_rate_reports_unbound_ids_rather_than_hiding_them(minirepo_graph):
    observed = sorted(EXPECTED_TEST_IDS) + [
        "com.example.GhostTest#vanished",
        "tests/test_absent.py::test_nothing",
    ]
    report = bind_test_ids(minirepo_graph, observed, repo="acme/minirepo")

    assert report.as_fraction() == "4/6"
    assert report.n_bound == 4
    assert report.unbound_sample == [
        "com.example.GhostTest#vanished",
        "tests/test_absent.py::test_nothing",
    ]


def test_binding_rate_samples_at_most_twenty_unbound_ids(minirepo_graph):
    observed = [f"com.example.GhostTest{i}#t" for i in range(50)]
    report = bind_test_ids(minirepo_graph, observed, repo="acme/minirepo")

    assert report.n_observed == 50
    assert report.n_bound == 0
    assert len(report.unbound_sample) == 20
    assert report.unbound_sample == sorted(observed)[:20]


def test_binding_rate_is_zero_without_dividing_by_zero(minirepo_graph):
    report = bind_test_ids(minirepo_graph, [], repo="acme/minirepo")
    assert report.n_observed == 0
    assert report.rate == 0.0
    assert report.as_fraction() == "0/0"


def test_binding_report_counts_the_graphs_test_nodes(minirepo_graph):
    report = bind_test_ids(minirepo_graph, sorted(EXPECTED_TEST_IDS), repo="acme/minirepo")
    assert report.n_test_nodes == EXPECTED_TEST_NODE_COUNT
    assert report.n_test_nodes_with_id == len(EXPECTED_TEST_IDS)
