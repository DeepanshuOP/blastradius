"""Tests for the commit-pinned graph builder (ROADMAP §10.2, T2.2).

Expected values are hand-written against the checked-in fixture tree at
`tests/fixtures/graph/minirepo/`, which contains:

| Path                                             | Role                          |
|--------------------------------------------------|-------------------------------|
| `src/main/java/com/example/Calculator.java`      | Java production class         |
| `src/main/java/com/example/Rounder.java`         | Java collaborator             |
| `src/test/java/com/example/CalculatorTest.java`  | JUnit 5 test class            |
| `pkg/shapes.py`                                  | Python production module      |
| `tests/test_shapes.py`                           | pytest module                 |
| `Broken.java`                                    | real syntax error             |
| `build/generated/Generated.java`                 | build output, must be skipped |
| `node_modules/vendored.py`                       | vendored, must be skipped     |
| `README.md`, `pom.xml`                           | not a dispatched suffix       |

So six files reach the extractor: four Java (one of them broken) and two Python.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path

import networkx as nx
import pytest

from src.graph.build import (
    GRAPH_FORMAT_VERSION,
    PARSE_FAILURE_CEILING,
    build_graph_at,
    collect_source_files,
    graph_path,
    language_of,
    load_graph,
    pagerank,
    repo_slug,
    worktree_at,
)
from tests.graph.conftest import git

#: Hand-derived from the fixture: the six files the builder must dispatch, in
#: the sorted order it must dispatch them in.
EXPECTED_SOURCE_FILES = [
    "Broken.java",
    "pkg/shapes.py",
    "src/main/java/com/example/Calculator.java",
    "src/main/java/com/example/Rounder.java",
    "src/test/java/com/example/CalculatorTest.java",
    "tests/test_shapes.py",
]

#: Node and edge counts for the fixture at its single commit. The stored graph
#: is a `MultiDiGraph` keyed by `edge_type` (see
#: `src.graph.test_nodes.add_binding_edges` for why), so the edge count includes
#: the test→source binding edges alongside the structural edges they derive
#: from: 29 structural + 20 binding.
EXPECTED_N_NODES = 22
EXPECTED_N_EDGES = 49
EXPECTED_N_STRUCTURAL_EDGES = 29

#: Edges per `edge_type`, hand-checked against the fixture.
EXPECTED_EDGE_TYPES = {
    "calls": 6,
    "contains": 7,
    "imports": 3,
    "imports_from": 1,
    "method": 6,
    "rationale_for": 2,
    "references": 4,
    "tests": 9,
    "tests_by_convention": 3,
    "tests_by_layout": 8,
}

#: Nodes per source file. `""` is the one import target that no file owns
#: (`org.junit.jupiter.api.Test`, an external symbol).
EXPECTED_NODES_PER_FILE = {
    "": 1,
    "Broken.java": 1,
    "pkg/shapes.py": 4,
    "src/main/java/com/example/Calculator.java": 5,
    "src/main/java/com/example/Rounder.java": 3,
    "src/test/java/com/example/CalculatorTest.java": 4,
    "tests/test_shapes.py": 4,
}


def test_repo_slug_matches_the_clone_directory_convention():
    assert repo_slug("spiculedata/saiku") == "spiculedata__saiku"
    assert repo_slug("fla-org/flash-linear-attention") == "fla-org__flash-linear-attention"


def test_graph_path_is_keyed_by_repo_and_sha():
    path = graph_path("acme/widget", "deadbeef", Path("data/graphs"))
    assert path == Path("data/graphs/graph_acme__widget_deadbeef.json.gz")


def test_language_of_dispatches_java_and_python_only():
    assert language_of("Foo.java") == "java"
    assert language_of("foo.py") == "python"
    assert language_of("Foo.JAVA") == "java"
    # TypeScript is an explicit non-goal (D-03); everything else is unsupported.
    assert language_of("foo.spec.ts") is None
    assert language_of("pom.xml") is None
    assert language_of("README.md") is None


def test_collect_source_files_skips_build_output_and_vendored_trees(minirepo_clone):
    found = [p.relative_to(minirepo_clone).as_posix() for p in collect_source_files(minirepo_clone)]
    assert found == EXPECTED_SOURCE_FILES
    assert "build/generated/Generated.java" not in found
    assert "node_modules/vendored.py" not in found


def test_worktree_at_checks_out_the_sha_and_cleans_up(minirepo_clone, minirepo_sha):
    with worktree_at(minirepo_clone, minirepo_sha) as tree:
        assert (tree / "pkg" / "shapes.py").is_file()
        assert git(tree, "rev-parse", "HEAD").strip() == minirepo_sha
        captured = tree
    assert not captured.exists(), "the worktree must be removed on exit"
    listed = [line.split()[0] for line in git(minirepo_clone, "worktree", "list").splitlines()]
    assert str(captured) not in listed, "the worktree must be pruned from the clone"


def test_worktree_at_rejects_a_sha_that_is_not_a_commit(minirepo_clone):
    with pytest.raises(RuntimeError, match="not a commit"):
        with worktree_at(minirepo_clone, "0" * 40):
            pass


def test_worktree_at_cleans_up_when_the_body_raises(minirepo_clone, minirepo_sha):
    with pytest.raises(ZeroDivisionError):
        with worktree_at(minirepo_clone, minirepo_sha) as tree:
            captured = tree
            1 / 0
    assert not captured.exists()


def test_build_graph_at_produces_the_expected_graph(minirepo_clone, minirepo_sha, tmp_path):
    stats = build_graph_at(
        "acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=tmp_path / "graphs"
    )

    assert stats.repo == "acme/minirepo"
    assert stats.sha == minirepo_sha
    assert stats.n_nodes == EXPECTED_N_NODES
    assert stats.n_edges == EXPECTED_N_EDGES
    assert stats.n_files_considered == len(EXPECTED_SOURCE_FILES) == 6
    assert stats.incremental_from is None
    assert stats.communities_inherited is False
    assert Path(stats.graph_path).is_file()


def test_build_graph_at_counts_the_real_syntax_error_as_a_parse_failure(
    minirepo_clone, minirepo_sha, tmp_path
):
    """Broken.java is error-recovered by tree-sitter, so it still yields its file
    node and never reaches `failed_sources`. Counting only hard failures would
    report 0/6 on a corpus the parser is silently mangling, so the cached
    `parse_errors` marker is what the gate reads."""
    stats = build_graph_at(
        "acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=tmp_path / "graphs"
    )

    assert stats.failed_source_files == ["Broken.java"]
    assert stats.n_parse_failures == 1
    assert stats.parse_failure_rate == round(1 / 6, 6)
    assert stats.per_language == {
        "java": {"files": 4, "failures": 1, "rate": 0.25},
        "python": {"files": 2, "failures": 0, "rate": 0.0},
    }


def test_build_graph_at_does_not_flag_a_repo_below_the_ceiling(
    minirepo_clone, minirepo_sha, tmp_path
):
    stats = build_graph_at(
        "acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=tmp_path / "graphs"
    )
    assert stats.parse_failure_rate < PARSE_FAILURE_CEILING
    assert stats.flagged is False
    assert stats.flag_reason is None


def test_build_graph_at_flags_a_repo_above_the_ceiling_with_a_reason(
    minirepo_clone, tmp_path
):
    """Delete the clean Java files so the broken one dominates: 1 failure out of
    2 remaining Java files plus 2 Python files = 1/3 > 20%."""
    for doomed in (
        "src/main/java/com/example/Calculator.java",
        "src/main/java/com/example/Rounder.java",
    ):
        (minirepo_clone / doomed).unlink()
    git(minirepo_clone, "add", "--all")
    git(minirepo_clone, "commit", "--quiet", "-m", "drop the clean java")
    sha = git(minirepo_clone, "rev-parse", "HEAD").strip()

    stats = build_graph_at(
        "acme/minirepo", sha, clone_dir=minirepo_clone, out_dir=tmp_path / "graphs"
    )

    assert stats.n_files_considered == 4
    assert stats.n_parse_failures == 1
    assert stats.parse_failure_rate == 0.25
    assert stats.flagged is True
    assert "exceeds the ROADMAP §19.4 ceiling" in stats.flag_reason
    assert "1/4" in stats.flag_reason
    assert "java 1/2" in stats.flag_reason


def test_orphan_rate_is_reported(minirepo_clone, minirepo_sha, tmp_path):
    stats = build_graph_at(
        "acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=tmp_path / "graphs"
    )
    graph = load_graph(stats.graph_path)
    orphans = [n for n in graph if graph.degree(n) == 0]

    assert stats.n_orphan_nodes == len(orphans)
    assert stats.orphan_rate == pytest.approx(len(orphans) / stats.n_nodes, abs=1e-6)


def test_graph_file_is_byte_identical_on_rebuild(minirepo_clone, minirepo_sha, tmp_path):
    """Determinism is a requirement (D-17) and the equivalence assertion in
    §10.2 step 6 rests on it: no timestamp in the payload, every collection
    sorted, and a fixed gzip mtime."""
    out = tmp_path / "graphs"
    first = Path(build_graph_at(
        "acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=out
    ).graph_path).read_bytes()
    second = Path(build_graph_at(
        "acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=out, force=True
    ).graph_path).read_bytes()

    assert first == second


def test_graph_payload_is_sorted_and_carries_no_timestamp(
    minirepo_clone, minirepo_sha, tmp_path
):
    stats = build_graph_at(
        "acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=tmp_path / "graphs"
    )
    with gzip.open(stats.graph_path, "rt", encoding="utf-8") as fh:
        payload = json.load(fh)

    node_keys = [
        (n.get("source_file") or "", n.get("source_location") or "", n["id"])
        for n in payload["nodes"]
    ]
    assert node_keys == sorted(node_keys)
    link_keys = [
        (l["source"], l["target"], str(l.get("edge_type") or ""), str(l.get("key") or ""))
        for l in payload["links"]
    ]
    assert link_keys == sorted(link_keys)
    assert "built_at" not in json.dumps(payload)
    assert payload["meta"]["format_version"] == GRAPH_FORMAT_VERSION
    assert payload["meta"]["repo"] == "acme/minirepo"
    assert payload["meta"]["sha"] == minirepo_sha


def test_loaded_graph_is_directed_and_matches_the_stats(
    minirepo_clone, minirepo_sha, tmp_path
):
    stats = build_graph_at(
        "acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=tmp_path / "graphs"
    )
    graph = load_graph(stats.graph_path)

    assert graph.is_directed()
    assert graph.is_multigraph(), (
        "a `tests` binding must coexist with the `calls` edge it derives from"
    )
    assert graph.number_of_nodes() == stats.n_nodes == EXPECTED_N_NODES
    assert graph.number_of_edges() == stats.n_edges == EXPECTED_N_EDGES


def test_nodes_are_attributed_to_the_expected_source_files(
    minirepo_clone, minirepo_sha, tmp_path
):
    stats = build_graph_at(
        "acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=tmp_path / "graphs"
    )
    graph = load_graph(stats.graph_path)

    counts: dict[str, int] = {}
    for _, data in graph.nodes(data=True):
        counts[data.get("source_file") or ""] = counts.get(data.get("source_file") or "", 0) + 1
    assert counts == EXPECTED_NODES_PER_FILE
    # Nothing from the skipped trees may appear.
    assert not any("node_modules" in key or key.startswith("build/") for key in counts)


def test_every_node_carries_the_schema_fields_this_layer_owns(
    minirepo_clone, minirepo_sha, tmp_path
):
    """`community_id`, `degree`, `pagerank`, `start_line` and `parse_status` are
    `docs/SCHEMAS.md` `graph_nodes` field names; this layer must populate them
    under those names rather than invent its own."""
    stats = build_graph_at(
        "acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=tmp_path / "graphs"
    )
    graph = load_graph(stats.graph_path)

    for node, data in graph.nodes(data=True):
        for key in ("community_id", "degree", "pagerank", "start_line", "parse_status"):
            assert key in data, f"{node} is missing {key}"
        assert data["degree"] == graph.degree(node)
        assert 0.0 <= data["pagerank"] <= 1.0


def test_every_edge_carries_the_schema_fields_this_layer_owns(
    minirepo_clone, minirepo_sha, tmp_path
):
    stats = build_graph_at(
        "acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=tmp_path / "graphs"
    )
    graph = load_graph(stats.graph_path)

    for src, dst, key, data in graph.edges(keys=True, data=True):
        for field in ("edge_type", "confidence", "confidence_score", "weight"):
            assert field in data, f"{src}->{dst} is missing {field}"
        assert data["confidence"] in {"EXTRACTED", "INFERRED", "AMBIGUOUS"}
        assert 0.0 <= data["confidence_score"] <= 1.0
        assert key == data["edge_type"], "the multigraph key must be the edge_type"
    counts: dict[str, int] = {}
    for *_, data in graph.edges(data=True):
        counts[data["edge_type"]] = counts.get(data["edge_type"], 0) + 1
    assert counts == EXPECTED_EDGE_TYPES


def test_the_binding_edges_do_not_displace_the_structural_edges(
    minirepo_clone, minirepo_sha, tmp_path
):
    """Regression guard for a real defect found in this step: emitting the
    `tests` edge during extraction overwrote the `calls` edge it was derived
    from, destroying 7 of the fixture's 29 structural edges, because
    Graphify assembles into a single-edge `nx.DiGraph`."""
    stats = build_graph_at(
        "acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=tmp_path / "graphs"
    )
    graph = load_graph(stats.graph_path)

    structural = [
        data
        for *_, data in graph.edges(data=True)
        if data["edge_type"] not in ("tests", "tests_by_convention", "tests_by_layout")
    ]
    assert len(structural) == EXPECTED_N_STRUCTURAL_EDGES
    # Every `calls` edge of the fixture must survive.
    assert sum(1 for data in structural if data["edge_type"] == "calls") == 6


def test_rebuild_is_reused_without_force(minirepo_clone, minirepo_sha, tmp_path):
    out = tmp_path / "graphs"
    first = build_graph_at(
        "acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=out
    )
    reused = build_graph_at(
        "acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=out
    )
    assert reused.as_dict() == first.as_dict(), "the sidecar stats must be replayed verbatim"


def test_stats_sidecar_round_trips(minirepo_clone, minirepo_sha, tmp_path):
    stats = build_graph_at(
        "acme/minirepo", minirepo_sha, clone_dir=minirepo_clone, out_dir=tmp_path / "graphs"
    )
    sidecar = Path(stats.graph_path).with_suffix("").with_suffix(".stats.json")
    assert json.loads(sidecar.read_text(encoding="utf-8")) == stats.as_dict()


def test_build_graph_at_rejects_a_missing_clone(tmp_path):
    with pytest.raises(FileNotFoundError, match="no clone at"):
        build_graph_at("acme/absent", "deadbeef", clone_dir=tmp_path / "nope")


def test_pagerank_is_a_distribution_and_order_independent():
    """SciPy is outside the `graph` extra, so PageRank is a local power
    iteration. It must still behave like PageRank, and must not depend on
    insertion order."""
    forward = nx.DiGraph()
    forward.add_edges_from([("a", "b"), ("b", "c"), ("c", "a"), ("a", "c")])
    shuffled = nx.DiGraph()
    shuffled.add_edges_from([("a", "c"), ("c", "a"), ("b", "c"), ("a", "b")])

    scores = pagerank(forward)
    assert sum(scores.values()) == pytest.approx(1.0)
    assert set(scores) == {"a", "b", "c"}
    # c has two in-edges, b has one: c must rank above b.
    assert scores["c"] > scores["b"]
    assert pagerank(shuffled) == scores


def test_pagerank_handles_dangling_nodes_and_empty_graphs():
    dangling = nx.DiGraph()
    dangling.add_edge("a", "b")  # b has no out-edges
    scores = pagerank(dangling)
    assert sum(scores.values()) == pytest.approx(1.0)
    assert scores["b"] > scores["a"]
    assert pagerank(nx.DiGraph()) == {}


def test_parallel_and_serial_extraction_agree(minirepo_clone, tmp_path):
    """The builder uses Graphify's multiprocess extractor for speed. Determinism
    is a hard requirement (D-17), so the two modes must agree exactly — node
    set, edge set, every attribute, and the community partition. A divergence
    here means the graphs in `data/graphs/` depend on the machine's core count.
    """
    from src.graph.build import _assemble, _extract, collect_source_files

    files = collect_source_files(minirepo_clone)
    serial = _extract(files, minirepo_clone, tmp_path / "cache-serial", parallel=False)
    parallel = _extract(files, minirepo_clone, tmp_path / "cache-parallel", parallel=True)

    serial_graph, serial_communities = _assemble([serial], minirepo_clone)
    parallel_graph, parallel_communities = _assemble([parallel], minirepo_clone)

    assert set(serial_graph.nodes()) == set(parallel_graph.nodes())
    assert set(serial_graph.edges()) == set(parallel_graph.edges())
    assert {n: dict(d) for n, d in serial_graph.nodes(data=True)} == {
        n: dict(d) for n, d in parallel_graph.nodes(data=True)
    }
    assert {(u, v): dict(d) for u, v, d in serial_graph.edges(data=True)} == {
        (u, v): dict(d) for u, v, d in parallel_graph.edges(data=True)
    }
    assert serial_communities == parallel_communities
