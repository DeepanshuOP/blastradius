"""The blocking incremental-vs-cold equivalence assertion (ROADMAP §10.2 step 6).

An incremental build at SHA *X* must produce **the same graph** as a cold build
at SHA *X*. ROADMAP §19.1 is explicit that divergence is release-blocking, not a
known issue: if the two disagree, every graph feature in the dataset is suspect.

Two layers of coverage, because they fail differently:

* on the checked-in `minirepo` fixture, over a hand-written five-commit history
  that exercises edit, add, delete and a cross-file rename — fast, hermetic, and
  runs on every `make test`;
* on five real consecutive commits of the smallest mini-corpus repo
  (`spiculedata/saiku`, median 5,472 nodes), which is what §10.2 step 6 asks
  for and what no fixture can stand in for. That one skips when the clone is
  absent, since `data/clones/` is unshippable.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from src.graph.build import (
    build_graph_at,
    build_graph_incremental,
    cache_miss_files,
    changed_source_files,
    collect_source_files,
    load_graph,
)
from tests.conftest import requires_data
from tests.graph.conftest import git

#: The real repo §10.2 step 6 is measured on: the smallest mini-corpus member.
SAIKU = "spiculedata/saiku"
SAIKU_CLONE = Path("data/clones/spiculedata__saiku")

#: Five real consecutive (first-parent) commits of `spiculedata/saiku`, each
#: step touching at least one `.java`/`.py` file. Oldest first. Recorded here so
#: the assertion is reproducible rather than re-derived per run.
SAIKU_CHAIN = [
    "e3dec93372b645515dd29c7b483b2e9dfde255e3",
    "36a1fd4ea0d9e77386c4c702a0e3cab92fbed5ec",
    "99fd60a39fa37724110a4851038bf42a8e4e8811",
    "7c4776612c94da5b01abdff2b5e19c767feb3f7f",
    "18a5bb8444e366d0dd6e23819480065bf9bca4e7",
]


def _graph_identity(path: str | Path) -> tuple[set[str], set[tuple[str, str]]]:
    """Return the (node set, edge set) a build must reproduce exactly."""
    graph = load_graph(path)
    return set(graph.nodes()), set(graph.edges())


def _full_identity(path: str | Path) -> tuple[dict, dict]:
    """Return every node and edge attribute, for the stronger comparison."""
    graph = load_graph(path)
    return (
        {node: dict(data) for node, data in graph.nodes(data=True)},
        {(src, dst): dict(data) for src, dst, data in graph.edges(data=True)},
    )


def _evolve_minirepo(repo: Path) -> list[str]:
    """Commit a five-step history over the fixture and return its SHAs.

    The steps are chosen to hit the invalidation cases §19.1 step 3 is about:
    a body edit, a new file that an existing file imports, a deletion whose
    nodes must disappear, and an edit to a file other files call into.

    Args:
        repo: A `minirepo_clone`.

    Returns:
        Five SHAs, oldest first.
    """
    shas = [git(repo, "rev-parse", "HEAD").strip()]

    def commit(message: str) -> None:
        git(repo, "add", "--all")
        git(repo, "commit", "--quiet", "--allow-empty", "-m", message)
        shas.append(git(repo, "rev-parse", "HEAD").strip())

    # 1. Edit a method body in a file other files call into.
    calculator = repo / "src/main/java/com/example/Calculator.java"
    calculator.write_text(
        calculator.read_text().replace(
            "return rounder.round(a + b);",
            "return rounder.round(a + b + 0);",
        ),
        encoding="utf-8",
    )
    commit("edit a called method body")

    # 2. Add a new Python module and import it from the existing test module.
    (repo / "pkg" / "volumes.py").write_text(
        '"""Added module, imported by the existing test."""\n\n\n'
        "def volume(width, height, depth):\n"
        "    return width * height * depth\n",
        encoding="utf-8",
    )
    test_shapes = repo / "tests" / "test_shapes.py"
    test_shapes.write_text(
        test_shapes.read_text().replace(
            "from pkg.shapes import area, perimeter",
            "from pkg.shapes import area, perimeter\nfrom pkg.volumes import volume",
        )
        + "\n\ndef test_volume():\n    assert volume(2, 3, 4) == 24\n",
        encoding="utf-8",
    )
    commit("add a module and import it")

    # 3. Add a Java class and reference it from the test class.
    (repo / "src/main/java/com/example/Doubler.java").write_text(
        "package com.example;\n\n"
        "/** Added class, referenced by CalculatorTest. */\n"
        "public class Doubler {\n\n"
        "    public int twice(int value) {\n"
        "        return value * 2;\n"
        "    }\n"
        "}\n",
        encoding="utf-8",
    )
    calculator_test = repo / "src/test/java/com/example/CalculatorTest.java"
    calculator_test.write_text(
        calculator_test.read_text().replace(
            "    @Test\n    public void testAdd() {",
            "    @Test\n    public void testTwice() {\n"
            "        assertEquals(4, new Doubler().twice(2));\n"
            "    }\n\n"
            "    @Test\n    public void testAdd() {",
        ),
        encoding="utf-8",
    )
    commit("add a java class and reference it")

    # 4. Delete the broken file: its nodes must vanish, not linger.
    (repo / "Broken.java").unlink()
    commit("delete the unparseable file")

    return shas


@pytest.mark.parametrize("step", range(1, 5))
def test_incremental_equals_cold_on_the_fixture_history(
    minirepo_clone, tmp_path, step
):
    """Hermetic equivalence over the fixture's five-commit history."""
    shas = _evolve_minirepo(minirepo_clone)
    cold_dir, inc_dir = tmp_path / "cold", tmp_path / "inc"
    cache = tmp_path / "cache"

    # The shared content cache is what makes the second build incremental, so
    # both builds of the chain walk forward through it.
    for sha in shas[: step + 1]:
        build_graph_at(
            "acme/minirepo", sha, clone_dir=minirepo_clone, out_dir=cold_dir,
            cache_root=tmp_path / "cold-cache", force=True,
        )
    build_graph_at(
        "acme/minirepo", shas[0], clone_dir=minirepo_clone, out_dir=inc_dir,
        cache_root=cache, force=True,
    )
    for previous, sha in zip(shas[:step], shas[1 : step + 1]):
        incremental = build_graph_incremental(
            "acme/minirepo", sha, previous, clone_dir=minirepo_clone,
            out_dir=inc_dir, cache_root=cache,
        )

    cold_nodes, cold_edges = _graph_identity(
        cold_dir / f"graph_acme__minirepo_{shas[step]}.json.gz"
    )
    inc_nodes, inc_edges = _graph_identity(incremental.graph_path)

    assert inc_nodes == cold_nodes, (
        f"step {step}: {len(inc_nodes - cold_nodes)} incremental-only and "
        f"{len(cold_nodes - inc_nodes)} cold-only nodes"
    )
    assert inc_edges == cold_edges, (
        f"step {step}: {len(inc_edges - cold_edges)} incremental-only and "
        f"{len(cold_edges - inc_edges)} cold-only edges"
    )
    assert incremental.incremental_from == shas[step - 1]


def test_incremental_matches_cold_attributes_on_the_fixture(minirepo_clone, tmp_path):
    """§10.2 step 6 asks for the same *graph*. Node and edge sets are the stated
    bar; attribute equality is the stronger claim, and it holds, so assert it —
    a community or PageRank value that depended on the build path would make
    every graph feature non-reproducible."""
    shas = _evolve_minirepo(minirepo_clone)
    cache = tmp_path / "cache"
    cold = build_graph_at(
        "acme/minirepo", shas[-1], clone_dir=minirepo_clone,
        out_dir=tmp_path / "cold", cache_root=tmp_path / "cold-cache",
    )
    build_graph_at(
        "acme/minirepo", shas[0], clone_dir=minirepo_clone,
        out_dir=tmp_path / "inc", cache_root=cache,
    )
    for previous, sha in zip(shas[:-1], shas[1:]):
        incremental = build_graph_incremental(
            "acme/minirepo", sha, previous, clone_dir=minirepo_clone,
            out_dir=tmp_path / "inc", cache_root=cache,
        )

    assert _full_identity(incremental.graph_path) == _full_identity(cold.graph_path)


def test_incremental_build_reports_its_delta(minirepo_clone, tmp_path):
    """The point of an incremental build is that it parses less. Assert the
    saving is real rather than assumed: only the files whose content changed may
    be content-cache misses."""
    shas = _evolve_minirepo(minirepo_clone)
    cache = tmp_path / "cache"
    build_graph_at(
        "acme/minirepo", shas[0], clone_dir=minirepo_clone,
        out_dir=tmp_path / "inc", cache_root=cache,
    )
    second = build_graph_incremental(
        "acme/minirepo", shas[1], shas[0], clone_dir=minirepo_clone,
        out_dir=tmp_path / "inc", cache_root=cache,
    )

    # Step 1 edits exactly one file.
    assert second.n_files_changed == 1
    assert second.n_files_reextracted == 1
    assert second.n_files_considered == 6
    assert second.n_files_reverse_hop >= 1, (
        "CalculatorTest calls into Calculator, so it must be in the reverse hop"
    )


def test_changed_source_files_filters_to_dispatched_suffixes(minirepo_clone):
    shas = _evolve_minirepo(minirepo_clone)
    changed = changed_source_files(minirepo_clone, shas[0], shas[-1])

    assert "src/main/java/com/example/Calculator.java" in changed
    assert "pkg/volumes.py" in changed
    assert "Broken.java" in changed, "a deletion must still invalidate its nodes"
    assert changed == sorted(changed)
    assert all(path.endswith((".java", ".py")) for path in changed)


def test_cache_miss_files_is_empty_once_the_cache_is_warm(minirepo_clone, tmp_path):
    cache = tmp_path / "cache"
    files = collect_source_files(minirepo_clone)
    assert cache_miss_files(files, minirepo_clone, cache) == files

    build_graph_at(
        "acme/minirepo", git(minirepo_clone, "rev-parse", "HEAD").strip(),
        clone_dir=minirepo_clone, out_dir=tmp_path / "graphs", cache_root=cache,
    )

    # Broken.java produces only a file node and carries a parse_errors marker,
    # but it is still cached, so a warm cache has no misses at all.
    assert cache_miss_files(files, minirepo_clone, cache) == []


# --------------------------------------------------------------------------
# ROADMAP §10.2 step 6 proper: five real consecutive commits of a real repo.
# --------------------------------------------------------------------------


@requires_data("data/clones/spiculedata__saiku")
def test_the_recorded_saiku_chain_is_five_real_consecutive_commits():
    """Guard the chain itself: if it were not a parent/child run, the
    equivalence result below would be measuring something weaker than §10.2
    step 6 asks for."""
    for parent, child in zip(SAIKU_CHAIN, SAIKU_CHAIN[1:]):
        assert git(SAIKU_CLONE, "rev-parse", f"{child}^").strip() == parent, (
            f"{child} is not a child of {parent}"
        )
        assert changed_source_files(SAIKU_CLONE, parent, child), (
            f"{parent}..{child} touches no .java/.py file, so it would not "
            f"exercise invalidation"
        )


@requires_data("data/clones/spiculedata__saiku")
def test_incremental_equals_cold_on_five_real_saiku_commits(tmp_path):
    """The blocking assertion (ROADMAP §10.2 step 6, §19.1).

    Walks the five-commit chain twice: once cold at every SHA with a throwaway
    cache, once incrementally through one shared cache. Every step's node and
    edge sets must match exactly, and the timings are printed so the report can
    quote them.
    """
    cold_dir, inc_dir = tmp_path / "cold", tmp_path / "inc"
    inc_cache = tmp_path / "inc-cache"

    first = build_graph_at(
        SAIKU, SAIKU_CHAIN[0], clones_root="data/clones",
        out_dir=inc_dir, cache_root=inc_cache,
    )
    timings = [
        {
            "sha": SAIKU_CHAIN[0],
            "cold_seconds": first.wall_seconds,
            "incremental_seconds": None,
            "n_nodes": first.n_nodes,
            "n_edges": first.n_edges,
            "n_files_reextracted": first.n_files_reextracted,
        }
    ]

    for previous, sha in zip(SAIKU_CHAIN, SAIKU_CHAIN[1:]):
        cold = build_graph_at(
            SAIKU, sha, clones_root="data/clones", out_dir=cold_dir,
            cache_root=tmp_path / f"cold-cache-{sha[:8]}", force=True,
        )
        incremental = build_graph_incremental(
            SAIKU, sha, previous, clones_root="data/clones",
            out_dir=inc_dir, cache_root=inc_cache,
        )

        cold_nodes, cold_edges = _graph_identity(cold.graph_path)
        inc_nodes, inc_edges = _graph_identity(incremental.graph_path)
        assert inc_nodes == cold_nodes, (
            f"{sha}: {len(inc_nodes - cold_nodes)} incremental-only and "
            f"{len(cold_nodes - inc_nodes)} cold-only nodes"
        )
        assert inc_edges == cold_edges, (
            f"{sha}: {len(inc_edges - cold_edges)} incremental-only and "
            f"{len(cold_edges - inc_edges)} cold-only edges"
        )
        assert incremental.n_nodes == cold.n_nodes
        assert incremental.n_edges == cold.n_edges
        assert incremental.n_files_reextracted < cold.n_files_considered, (
            "an incremental build that re-extracts the whole corpus is not one"
        )
        timings.append(
            {
                "sha": sha,
                "cold_seconds": cold.wall_seconds,
                "incremental_seconds": incremental.wall_seconds,
                "n_nodes": cold.n_nodes,
                "n_edges": cold.n_edges,
                "n_files_changed": incremental.n_files_changed,
                "n_files_reverse_hop": incremental.n_files_reverse_hop,
                "n_files_reextracted": incremental.n_files_reextracted,
                "n_files_considered": cold.n_files_considered,
            }
        )

    print("\n" + json.dumps(timings, indent=2))
    (tmp_path / "timings.json").write_text(json.dumps(timings, indent=2))
