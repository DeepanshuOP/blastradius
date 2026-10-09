"""Index a codebase for impact analysis, using the BlastRadius graph layer.

The code graph is built with ``src.graph.build.build_graph_at`` (the same
commit-pinned, tree-sitter extractor as the course graph layer, D-48), so the
agents and the research pipeline share one notion of "what depends on what".

Impact follows dependency direction: a test is affected by a change to node X
when the test can reach X along ``calls``/``imports``/``uses``/``tests`` edges
(``contains`` is followed upward, symbol -> file). We search that relation in
reverse from the changed nodes, so a caller of a changed function is reached but
an unrelated module that merely sits in the same package is not.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import networkx as nx

from src.agents import gitops

DEP_EDGES = {"calls", "imports", "imports_from", "uses", "method", "tests", "tests_by_convention", "tests_by_layout", "inherits", "extends", "implements"}
SOURCE_SUFFIXES = (".py", ".java")
STOPWORDS = set("""
a an and are as at be by can for from get gets i in into is it its me my of on or our so that the their them then
this to us we when where which while who will with want wants should would able user users as shopper customer
""".split())


def tokens(text: str) -> list[str]:
    """Lower-case word tokens: split camelCase and snake_case, drop stopwords, light stemming."""
    out: list[str] = []
    for word in re.findall(r"[A-Za-z][A-Za-z0-9]*", text):
        for part in re.findall(r"[A-Z]+(?![a-z])|[A-Z]?[a-z0-9]+", word) or [word]:
            t = part.lower()
            if len(t) < 2 or t in STOPWORDS:
                continue
            for suffix in ("ing", "ed", "es", "s"):
                if len(t) > len(suffix) + 3 and t.endswith(suffix):
                    t = t[: -len(suffix)]
                    break
            out.append(t)
    return out


def is_test_path(path: str) -> bool:
    """Conventional test file: under a tests/test dir, or named test_*.py / *_test.py / *Test.java."""
    name = Path(path).name
    return (
        "/test/" in f"/{path}" or "/tests/" in f"/{path}"
        or name.startswith("test_") or name.endswith("_test.py")
        or bool(re.match(r".*Tests?\.java$", name))
    )


@dataclass
class TestCase:
    """One runnable test: its graph node and its runner id."""

    node: str
    test_id: str  # pytest node id (path::[Class::]name) or Java Class#method
    file: str
    name: str


@dataclass
class CodeIndex:
    """A codebase at one commit: files, file text tokens, and the dependency graph."""

    repo: Path
    sha: str
    graph: nx.MultiDiGraph
    dep: nx.DiGraph  # dependency direction: u depends on v
    files: list[str]
    file_tokens: dict[str, Counter]
    file_nodes: dict[str, list[str]]
    tests: dict[str, TestCase]
    stats: dict = field(default_factory=dict)

    @property
    def source_files(self) -> list[str]:
        """Non-test source files."""
        return [f for f in self.files if f.endswith(SOURCE_SUFFIXES) and not is_test_path(f)]

    def idf(self) -> dict[str, float]:
        """Inverse document frequency over non-test source files."""
        docs = [self.file_tokens.get(f, Counter()) for f in self.source_files]
        n = max(len(docs), 1)
        df = Counter(t for d in docs for t in d)
        return {t: math.log(1 + n / c) for t, c in df.items()}

    def reverse_reach(self, seeds: list[str], cutoff: int = 6) -> dict[str, int]:
        """Distance from each node that depends (transitively) on any seed node."""
        rev = self.dep.reverse(copy=False)
        best: dict[str, int] = {}
        for s in seeds:
            if s not in rev:
                continue
            for node, d in nx.single_source_shortest_path_length(rev, s, cutoff=cutoff).items():
                if node not in best or d < best[node]:
                    best[node] = d
        return best


def _test_id(graph: nx.MultiDiGraph, node: str, data: dict) -> TestCase | None:
    label = str(data.get("label", ""))
    path = str(data.get("source_file", ""))
    if not data.get("_callable"):
        return None
    name = label.lstrip(".").rstrip("()")
    if path.endswith(".py"):
        if not name.startswith("test"):
            return None
        owner = None
        for u, _, e in graph.in_edges(node, data=True):
            if e.get("edge_type") == "method":
                owner = str(graph.nodes[u].get("label", "")).rstrip("()")
        tid = f"{path}::{owner}::{name}" if owner else f"{path}::{name}"
        return TestCase(node=node, test_id=tid, file=path, name=name)
    if path.endswith(".java"):
        cls = Path(path).stem
        return TestCase(node=node, test_id=f"{cls}#{name}", file=path, name=name)
    return None


def build_index(repo: Path | str, state_dir: Path | str, rev: str = "HEAD") -> CodeIndex:
    """Build (or reuse) the graph of ``repo`` at ``rev`` and index it.

    Args:
        repo: A git working copy.
        state_dir: The agents' state directory; graphs are cached under ``graphs/``.
        rev: Revision to index.
    """
    from src.graph.build import build_graph_at, graph_path, load_graph

    repo = Path(repo).resolve()
    state_dir = Path(state_dir)
    sha = gitops.head_sha(repo, rev)
    slug = f"local/{repo.name}"
    out_dir = state_dir / "graphs"
    stats = build_graph_at(slug, sha, clone_dir=repo, out_dir=out_dir)
    graph = load_graph(graph_path(slug, sha, out_dir))

    dep = nx.DiGraph()
    dep.add_nodes_from(graph.nodes)
    for u, v, e in graph.edges(data=True):
        et = e.get("edge_type")
        if et in DEP_EDGES:
            dep.add_edge(u, v, edge_type=et)
        elif et == "contains":  # symbol -> its container: a change inside reaches the file
            dep.add_edge(v, u, edge_type="contained_in")

    files = [f for f in gitops.tracked_files(repo)]
    file_nodes: dict[str, list[str]] = {}
    tests: dict[str, TestCase] = {}
    for node, data in graph.nodes(data=True):
        sf = data.get("source_file")
        if sf and data.get("node_type") in ("source", "test"):
            file_nodes.setdefault(sf, []).append(node)
        if data.get("node_type") == "test":
            tc = _test_id(graph, node, data)
            if tc:
                tests[tc.test_id] = tc

    file_tokens: dict[str, Counter] = {}
    for f in files:
        if f.endswith(SOURCE_SUFFIXES):
            try:
                text = (repo / f).read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            file_tokens[f] = Counter(tokens(f.replace("/", " ") + " " + text))

    return CodeIndex(
        repo=repo, sha=sha, graph=graph, dep=dep, files=files, file_tokens=file_tokens,
        file_nodes=file_nodes, tests=dict(sorted(tests.items())),
        stats={"nodes": stats.n_nodes, "edges": stats.n_edges, "files_parsed": stats.n_files_considered,
               "parse_failures": stats.n_parse_failures, "graphify_commit": stats.graphify_commit},
    )


def file_node(index: CodeIndex, path: str) -> str | None:
    """The module/file node of ``path`` (the one whose label is the file name)."""
    name = Path(path).name
    for n in index.file_nodes.get(path, []):
        if str(index.graph.nodes[n].get("label")) == name:
            return n
    return None
