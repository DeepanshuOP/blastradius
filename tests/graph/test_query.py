"""Tests for the five §10.5 query primitives and their DuckDB cache.

Distances are hand-computed on a small fixture graph whose shape is drawn below,
so a failure names a wrong number rather than "the algorithm changed". A second
layer runs the same primitives over the real built `minirepo` graph, which is
what catches a disagreement between the fixture's idea of the graph and the one
the builder actually produces.

The fixture graph (edge direction shown, distances measured undirected):

```
    t1 ──calls──▶ a ──calls──▶ b ──calls──▶ c        d (isolated)
     │                                  ▲
     └────────tests_by_layout───────────┘            t2 ──calls──▶ b
```

Undirected hop distances, worked out by hand:

| from | a | b | c | t1 | t2 | d |
|------|---|---|---|----|----|---|
| `a`  | 0 | 1 | 2 | 1  | 2  | — |
| `b`  | 1 | 0 | 1 | 2  | 1  | — |
| `c`  | 2 | 1 | 0 | 1  | 2  | — |

`t1` is 1 from `c` because of the layout edge, but 2 from `b`: it reaches `b`
only through `a` or `c`. `d` is isolated and unreachable from everything.
"""

from __future__ import annotations

import time

import networkx as nx
import pytest

from src.graph.build import build_graph_at, load_graph
from src.graph.query import UNREACHABLE, GraphQuery, QueryCache, feature_vector


@pytest.fixture
def fixture_graph() -> nx.MultiDiGraph:
    """The hand-drawn graph from this module's docstring."""
    graph = nx.MultiDiGraph()
    graph.graph["meta"] = {"repo": "acme/widget", "sha": "f" * 40}
    # Two communities: the a-b-c chain plus t1, and t2 on its own.
    nodes = {
        "t1": {"node_type": "test", "community_id": 0, "pagerank": 0.10},
        "t2": {"node_type": "test", "community_id": 1, "pagerank": 0.10},
        "a": {"node_type": "source", "community_id": 0, "pagerank": 0.30},
        "b": {"node_type": "source", "community_id": 0, "pagerank": 0.40},
        "c": {"node_type": "source", "community_id": 0, "pagerank": 0.08},
        "d": {"node_type": "source", "community_id": 2, "pagerank": 0.02},
    }
    for node, data in nodes.items():
        graph.add_node(node, **data)
    graph.add_edge("t1", "a", key="calls", edge_type="calls")
    graph.add_edge("a", "b", key="calls", edge_type="calls")
    graph.add_edge("b", "c", key="calls", edge_type="calls")
    graph.add_edge("t1", "c", key="tests_by_layout", edge_type="tests_by_layout")
    graph.add_edge("t2", "b", key="calls", edge_type="calls")
    return graph


@pytest.fixture
def query(fixture_graph) -> GraphQuery:
    return GraphQuery(fixture_graph)


# --------------------------------------------------------------------------
# shortest_path_length
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "changed,test_node,expected",
    [
        ("a", "t1", 1),
        ("a", "b", 1),
        ("a", "c", 2),
        ("a", "t2", 2),
        ("a", "a", 0),
        ("c", "t1", 1),
        ("c", "a", 2),
        ("c", "t2", 2),
        ("b", "t1", 2),
        ("b", "t2", 1),
        ("a", "d", UNREACHABLE),
        ("d", "t1", UNREACHABLE),
    ],
)
def test_shortest_path_length_matches_hand_computed_distances(
    query, changed, test_node, expected
):
    assert query.shortest_path_length(changed, test_node) == expected


def test_shortest_path_length_is_measured_undirected(query):
    """A change to a callee must reach its callers. The only edge between `t1`
    and `a` points `t1 → a`, so a directed traversal seeded at the changed node
    `a` would never find `t1`, and every test that calls into a changed callee
    would be invisible."""
    assert query.graph.has_edge("t1", "a", key="calls")
    assert not query.graph.has_edge("a", "t1", key="calls")
    assert query.shortest_path_length("a", "t1") == 1
    # Two hops away against the edge direction, through `a`.
    assert query.shortest_path_length("b", "t1") == 2


def test_shortest_path_length_returns_unreachable_for_absent_nodes(query):
    assert query.shortest_path_length("ghost", "t1") == UNREACHABLE
    assert query.shortest_path_length("a", "ghost") == UNREACHABLE


def test_cochange_mode_refuses_rather_than_silently_ignoring(query):
    """§10.5 asks for distances with and without `co_changes`. Those edges are
    T2.4, which stays CUT under D-48, so the honest answer is to refuse — not to
    return the without-co_changes number under the with-co_changes name."""
    with pytest.raises(NotImplementedError, match="T2.4"):
        query.shortest_path_length("a", "t1", with_cochange=True)
    with pytest.raises(NotImplementedError):
        query.min_distance_to_any_changed("t1", ["a"], with_cochange=True)


# --------------------------------------------------------------------------
# min_distance_to_any_changed
# --------------------------------------------------------------------------


def test_min_distance_takes_the_nearest_of_several_changed_nodes(query):
    # `c` is 1 hop from t1 via the layout edge; `b` is 2.
    assert query.min_distance_to_any_changed("t1", ["c"]) == 1
    assert query.min_distance_to_any_changed("t1", ["b"]) == 2
    assert query.min_distance_to_any_changed("t1", ["b", "c"]) == 1
    assert query.min_distance_to_any_changed("t2", ["a", "c"]) == 2
    # `a` is 2 hops from t2, `b` is 1 — the minimum must win.
    assert query.min_distance_to_any_changed("t2", ["a", "b"]) == 1


def test_min_distance_ignores_unreachable_members_of_the_changed_set(query):
    assert query.min_distance_to_any_changed("t1", ["d", "a"]) == 1


def test_min_distance_is_unreachable_when_nothing_is_reachable(query):
    assert query.min_distance_to_any_changed("t1", ["d"]) == UNREACHABLE
    assert query.min_distance_to_any_changed("t1", []) == UNREACHABLE


def test_min_distance_is_zero_for_a_changed_test(query):
    """A test whose own file changed is distance 0 from the change. The leakage
    rule that excludes such instances lives in the labelling layer, not here —
    this primitive must report the truth."""
    assert query.min_distance_to_any_changed("t1", ["t1"]) == 0


# --------------------------------------------------------------------------
# k_hop_neighborhood
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "k,expected",
    [
        (0, {"a"}),
        (1, {"a", "t1", "b"}),
        (2, {"a", "t1", "b", "c", "t2"}),
        (3, {"a", "t1", "b", "c", "t2"}),
    ],
)
def test_k_hop_neighborhood_grows_as_expected(query, k, expected):
    assert query.k_hop_neighborhood(["a"], k) == expected


def test_k_hop_neighborhood_unions_over_the_changed_set(query):
    assert query.k_hop_neighborhood(["a", "d"], 0) == {"a", "d"}
    assert query.k_hop_neighborhood(["c", "d"], 1) == {"c", "b", "t1", "d"}


def test_k_hop_neighborhood_handles_degenerate_input(query):
    assert query.k_hop_neighborhood([], 3) == set()
    assert query.k_hop_neighborhood(["a"], -1) == set()
    assert query.k_hop_neighborhood(["ghost"], 3) == set()


def test_k_hop_neighborhood_never_reaches_an_isolated_node(query):
    assert "d" not in query.k_hop_neighborhood(["a"], 99)


# --------------------------------------------------------------------------
# same_community
# --------------------------------------------------------------------------


def test_same_community_uses_the_stored_partition(query):
    assert query.same_community("t1", ["a"]) is True
    assert query.same_community("t1", ["b", "c"]) is True
    assert query.same_community("t1", ["d"]) is False
    assert query.same_community("t2", ["a"]) is False
    assert query.same_community("t2", ["t2"]) is True


def test_same_community_is_false_for_an_unpartitioned_node(fixture_graph):
    """A node the partitioner never placed has no community, so the answer is
    False rather than an accidental match with every other unplaced node."""
    fixture_graph.add_node("orphan", node_type="source", pagerank=0.0)
    query = GraphQuery(fixture_graph)
    assert query.same_community("orphan", ["a"]) is False
    assert query.same_community("orphan", ["orphan"]) is False


# --------------------------------------------------------------------------
# pagerank_delta
# --------------------------------------------------------------------------


def test_pagerank_delta_is_the_changed_share_of_total_mass(query):
    # The fixture's scores sum to 1.0, so the share is the raw sum.
    assert query.pagerank_delta(["b"]) == pytest.approx(0.40)
    assert query.pagerank_delta(["a", "b"]) == pytest.approx(0.70)
    assert query.pagerank_delta(["d"]) == pytest.approx(0.02)


def test_pagerank_delta_ranks_a_hub_above_a_leaf(query):
    assert query.pagerank_delta(["b"]) > query.pagerank_delta(["d"])


def test_pagerank_delta_is_bounded_and_degenerate_safe(query):
    assert query.pagerank_delta([]) == 0.0
    assert query.pagerank_delta(["ghost"]) == 0.0
    assert query.pagerank_delta(query.graph.nodes()) == pytest.approx(1.0)
    assert GraphQuery(nx.MultiDiGraph()).pagerank_delta(["a"]) == 0.0


def test_pagerank_is_recomputed_when_the_graph_stored_none(fixture_graph):
    """A graph written before PageRank was stored reads as all zeroes, which is a
    silently wrong feature rather than a missing one."""
    for _, data in fixture_graph.nodes(data=True):
        data["pagerank"] = 0.0
    query = GraphQuery(fixture_graph)
    assert query.pagerank_delta(["b"]) > 0.0
    assert sum(query.pagerank().values()) == pytest.approx(1.0)


# --------------------------------------------------------------------------
# the DuckDB cache
# --------------------------------------------------------------------------


def test_cache_round_trips_distance_layers(fixture_graph, tmp_path):
    db = tmp_path / "cache.duckdb"
    with QueryCache(db) as cache:
        first = GraphQuery(fixture_graph, cache=cache)
        assert first.min_distance_to_any_changed("t2", ["a"]) == 2
        assert cache.misses >= 1
        stored = cache.get("acme/widget", "f" * 40, "layers", "a")
    assert stored["t2"] == 2

    # A fresh GraphQuery over the same (repo, sha) must read it back, not redo it.
    with QueryCache(db) as cache:
        second = GraphQuery(fixture_graph, cache=cache)
        assert second.min_distance_to_any_changed("t2", ["a"]) == 2
        assert cache.hits >= 1


def test_cache_is_keyed_per_repo_and_sha(fixture_graph, tmp_path):
    """Two SHAs of a repo have different graphs, so a shared cache entry would
    serve one SHA's distances for another — the cheapest possible way to make
    every graph feature wrong."""
    db = tmp_path / "cache.duckdb"
    with QueryCache(db) as cache:
        GraphQuery(fixture_graph, repo="acme/widget", sha="aaa", cache=cache).k_hop_neighborhood(
            ["a"], 1
        )
        assert cache.get("acme/widget", "aaa", "layers", "a") is not None
        assert cache.get("acme/widget", "bbb", "layers", "a") is None
        assert cache.get("other/repo", "aaa", "layers", "a") is None


def test_cache_entries_are_versioned(fixture_graph, tmp_path):
    """A cached value whose meaning changed must miss rather than answer wrongly."""
    import src.graph.query as query_module

    db = tmp_path / "cache.duckdb"
    with QueryCache(db) as cache:
        GraphQuery(fixture_graph, cache=cache).k_hop_neighborhood(["a"], 1)

    original = query_module.CACHE_SCHEMA_VERSION
    try:
        query_module.CACHE_SCHEMA_VERSION = original + 1
        with QueryCache(db) as cache:
            assert cache.get("acme/widget", "f" * 40, "layers", "a") is None
    finally:
        query_module.CACHE_SCHEMA_VERSION = original


def test_cache_survives_without_a_repo_or_sha(fixture_graph, tmp_path):
    """A graph with no `meta` must still answer queries; it just cannot be
    cached, because there is no key to cache it under."""
    bare = nx.MultiDiGraph(fixture_graph)
    bare.graph.pop("meta", None)
    with QueryCache(tmp_path / "cache.duckdb") as cache:
        query = GraphQuery(bare, cache=cache)
        assert query.min_distance_to_any_changed("t2", ["a"]) == 2
        assert cache.hits == 0 and cache.misses == 0


def test_an_unopened_cache_touches_no_file(tmp_path):
    db = tmp_path / "never.duckdb"
    cache = QueryCache(db)
    cache.close()
    assert not db.exists()


# --------------------------------------------------------------------------
# the full feature set, and the real graph
# --------------------------------------------------------------------------


def test_features_returns_every_primitive(query):
    features = query.features("t1", ["b"], k=1)
    assert set(features) == {
        "min_distance_to_any_changed",
        "in_k_hop_neighborhood",
        "k_hop_neighborhood_size",
        "same_community",
        "pagerank_delta",
    }
    assert features["min_distance_to_any_changed"] == 2
    # 1 hop from `b` reaches {b, a, c, t2}; t1 is 2 hops away.
    assert features["in_k_hop_neighborhood"] is False
    assert features["k_hop_neighborhood_size"] == 4
    assert features["same_community"] is True
    assert features["pagerank_delta"] == pytest.approx(0.40)

    # At k=2 the neighbourhood reaches t1.
    wider = query.features("t1", ["b"], k=2)
    assert wider["in_k_hop_neighborhood"] is True
    assert wider["k_hop_neighborhood_size"] == 5


def test_feature_vector_wrapper_agrees_with_the_class(fixture_graph):
    assert feature_vector(fixture_graph, "t1", ["b"], k=2) == GraphQuery(
        fixture_graph
    ).features("t1", ["b"], k=2)


def test_primitives_run_on_the_real_built_graph(minirepo_clone, minirepo_sha, tmp_path):
    """The fixture graph pins the arithmetic; this pins that the arithmetic is
    being done on the shape the builder actually produces."""
    stats = build_graph_at(
        "acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=tmp_path / "graphs"
    )
    graph = load_graph(stats.graph_path)
    query = GraphQuery(graph)

    test_node = "tests_test_shapes_test_area"
    changed = ["pkg_shapes_area"]
    assert query.shortest_path_length("pkg_shapes_area", test_node) == 1
    assert query.min_distance_to_any_changed(test_node, changed) == 1
    assert test_node in query.k_hop_neighborhood(changed, 1)
    assert 0.0 <= query.pagerank_delta(changed) <= 1.0

    features = query.features(test_node, changed, k=3)
    assert features["min_distance_to_any_changed"] == 1
    assert features["in_k_hop_neighborhood"] is True


def test_full_feature_set_meets_the_latency_budget_on_the_real_graph(
    minirepo_clone, minirepo_sha, tmp_path
):
    """ROADMAP §19.4: ≤100 ms for the full feature set per instance. Measured
    here on the fixture graph as a regression floor; the mini-corpus benchmark
    lives in the session report, where the real graph sizes are."""
    stats = build_graph_at(
        "acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=tmp_path / "graphs"
    )
    query = GraphQuery(load_graph(stats.graph_path))
    changed = ["pkg_shapes_area", "src_main_java_com_example_calculator_calculator_add"]
    test_nodes = [
        node
        for node, data in query.graph.nodes(data=True)
        if data.get("node_type") == "test"
    ]
    # Warm the layers once, as a real run does for all instances at a SHA.
    query.features(test_nodes[0], changed)

    started = time.perf_counter()
    for test_node in test_nodes:
        query.features(test_node, changed)
    per_instance_ms = (time.perf_counter() - started) / len(test_nodes) * 1000

    assert per_instance_ms < 100, f"{per_instance_ms:.3f} ms per instance"
