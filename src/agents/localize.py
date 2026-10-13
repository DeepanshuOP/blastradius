"""Graph-guided fault localisation (no model): which function most likely holds the fault?

Candidates are every function and method of the source files (`repair.index_functions`, the same universe L1 / L4
rank). Four signals, each a ranking of candidates:

    diff     the function overlaps a line the change touches (all such functions tie at rank 1)
    hops     minimum hop distance from a failing test's node, following `calls` edges caller -> callee
    reach    number of failing tests whose `calls` closure reaches the function (more first)
    frames   the function holds a frame of a failing test's traceback (deepest frame first)

They are fused by reciprocal rank fusion, ``sum 1 / (k + rank)`` with k = 60, ties at equal rank sharing it; the fused
order is broken by file path, then line. Every candidate keeps its evidence: the signals it scored on, its hop count and
the node-id path from the nearest failing test.

The graph is the project's code graph (`src.graph.build.build_graph_at`) in the Live Lab's view shape
(`src.lab.graphview.to_cytoscape`): nodes with file / line / type, edges with their relation.
"""

from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

from src.agents.repair import Chunk, changed_line_ranges, index_functions

RRF_K = 60
MAX_HOPS = 6
SIGNALS = ("diff", "hops", "reach", "frames")
_FRAME_PY = re.compile(r'File "([^"]+\.py)", line (\d+)')
_FRAME_PYTEST = re.compile(r"(?m)^([\w./\\-]+\.py):(\d+):")


@dataclass
class Candidate:
    """One ranked function with its evidence."""

    file: str
    qualname: str
    start: int
    end: int
    score: float = 0.0
    ranks: dict[str, int] = field(default_factory=dict)       # signal -> rank (1 best)
    node: str | None = None                                    # graph node id of the function
    hops: int | None = None
    reach: int = 0
    path: list[str] = field(default_factory=list)              # node ids, failing test -> ... -> function
    frame_depth: int | None = None                             # 0 = deepest frame

    @property
    def key(self) -> tuple[str, str]:
        return self.file, self.qualname

    def to_json(self) -> dict:
        return {"file": self.file, "qualname": self.qualname, "line": self.start, "end": self.end,
                "score": round(self.score, 6), "ranks": self.ranks, "node": self.node or f"{self.file}::{self.qualname}",
                "hops": self.hops, "reach": self.reach, "path": self.path, "frame_depth": self.frame_depth}


# ---- graph helpers ---------------------------------------------------------------------------------
def _name(label: str) -> str:
    return label.lstrip(".").removesuffix("()")


def node_index(view: dict, chunks: list[Chunk]) -> tuple[dict[str, tuple[str, str]], dict[tuple[str, str], list[str]]]:
    """Map graph function nodes to candidate keys, and test nodes to `(file, test name)`.

    A function node maps to the innermost candidate of its file whose span holds the node's line and whose name ends
    with the node's label. Returns `(node id -> candidate key, (test file, test name) -> test node ids)`.
    """
    by_file: dict[str, list[Chunk]] = {}
    for c in chunks:
        by_file.setdefault(c.file, []).append(c)
    fn: dict[str, tuple[str, str]] = {}
    tests: dict[tuple[str, str], list[str]] = {}
    for n in view.get("nodes", []):
        if n.get("type") == "test":
            tests.setdefault((n["file"], _name(n["label"])), []).append(n["id"])
            continue
        if n.get("type") != "function" or n.get("line") is None:
            continue
        name = _name(n["label"])
        hits = [c for c in by_file.get(n["file"], []) if c.start <= int(n["line"]) <= c.end
                and c.qualname.split(".")[-1] == name]
        if hits:
            best = min(hits, key=lambda c: c.end - c.start)
            fn[n["id"]] = best.file, best.qualname
    return fn, tests


def calls_adjacency(view: dict) -> dict[str, list[str]]:
    """Directed `calls` edges, caller -> callees, in a stable order."""
    adj: dict[str, list[str]] = {}
    for e in view.get("edges", []):
        if e.get("relation") == "calls":
            adj.setdefault(e["source"], []).append(e["target"])
    return {k: sorted(set(v)) for k, v in adj.items()}


def bfs(adj: dict[str, list[str]], seeds: list[str], limit: int = MAX_HOPS) -> dict[str, tuple[int, list[str]]]:
    """Shortest `calls` path from any seed: node -> (hops, node-id path). Seeds are expanded in sorted order."""
    out: dict[str, tuple[int, list[str]]] = {}
    q: deque[str] = deque()
    for s in sorted(set(seeds)):
        out[s] = (0, [s])
        q.append(s)
    while q:
        u = q.popleft()
        d, p = out[u]
        if d >= limit:
            continue
        for v in adj.get(u, []):
            if v not in out:
                out[v] = (d + 1, p + [v])
                q.append(v)
    return out


def test_key(test_id: str, test_files: set[str] | None = None) -> tuple[str, str]:
    """The (test file, test function) of a test id, in either form the project meets.

    `tests/a.py::Cls::test_x[p]` (pytest node id) -> `("tests/a.py", "test_x")`; `tests.a.Cls::test_x[p]` (JUnit
    classname form) -> `("tests/a.py", "test_x")`, the module being the longest dotted prefix that is a known test file.
    """
    parts = test_id.split("::")
    name = re.sub(r"\[.*\]$", "", parts[-1]) if len(parts) > 1 else ""
    head = parts[0]
    if head.endswith(".py") or "/" in head:
        return head, name
    dotted = head.split(".")
    for i in range(len(dotted), 0, -1):
        cand = "/".join(dotted[:i]) + ".py"
        if test_files is None or cand in test_files:
            return cand, name
    return head, name


def frames(output: str, repo_root: str | None = None) -> list[tuple[str, int]]:
    """`(path, line)` of each traceback frame in `output`, outermost first (relative paths when under `repo_root`)."""
    out: list[tuple[int, str, int]] = []
    for rx in (_FRAME_PY, _FRAME_PYTEST):
        for m in rx.finditer(output or ""):
            p = m.group(1).replace("\\", "/")
            if repo_root and p.startswith(repo_root.rstrip("/") + "/"):
                p = p[len(repo_root.rstrip("/")) + 1:]
            out.append((m.start(), p, int(m.group(2))))
    return [(p, ln) for _, p, ln in sorted(out)]


def _ranks(values: dict[tuple[str, str], float], higher_better: bool) -> dict[tuple[str, str], int]:
    """Competition ranks (1 best); equal values share a rank."""
    xs = sorted(values.values(), reverse=higher_better)
    return {k: 1 + sum(1 for x in xs if (x > v if higher_better else x < v)) for k, v in values.items()}


# ---- localisation ----------------------------------------------------------------------------------
def localize(repo: Path, source_files: list[str], failing: list[dict], pr_diff: str, view: dict | None,
             chunks: list[Chunk] | None = None) -> list[Candidate]:
    """Rank candidate functions by RRF over the four signals (best first; only candidates with a signal).

    Args:
        repo: Working tree in the failing state.
        source_files: Repo-relative non-test source files.
        failing: `[{"test_id", "output"}]` of the failing tests.
        pr_diff: The change.
        view: The code graph in `graphview.to_cytoscape` shape, or None (graph signals then absent).
        chunks: Candidates (default: `index_functions(repo, source_files)`).
    """
    chunks = chunks if chunks is not None else index_functions(repo, source_files)
    cands = {(c.file, c.qualname): Candidate(c.file, c.qualname, c.start, c.end) for c in chunks}
    signal: dict[str, dict[tuple[str, str], float]] = {s: {} for s in SIGNALS}
    # diff
    lines = changed_line_ranges(pr_diff)
    for c in chunks:
        if any(c.start <= ln <= c.end for ln in lines.get(c.file, [])):
            signal["diff"][(c.file, c.qualname)] = 1.0
    # hops / reach over calls
    if view:
        fn_of, tests = node_index(view, chunks)
        node_of = {}
        for nid, key in sorted(fn_of.items()):
            node_of.setdefault(key, nid)
        adj = calls_adjacency(view)
        per_test: list[dict[str, tuple[int, list[str]]]] = []
        test_files = {f for f, _ in tests}
        for t in failing:
            seeds = tests.get(test_key(t["test_id"], test_files), [])
            if seeds:
                per_test.append(bfs(adj, seeds))
        for key, cand in cands.items():
            cand.node = node_of.get(key)
            if cand.node is None:
                continue
            best = None
            for reach in per_test:
                if cand.node in reach:
                    cand.reach += 1
                    if best is None or reach[cand.node][0] < best[0] or (
                            reach[cand.node][0] == best[0] and reach[cand.node][1] < best[1]):
                        best = reach[cand.node]
            if best is not None:
                cand.hops, cand.path = best
                signal["hops"][key] = float(best[0])
                signal["reach"][key] = float(cand.reach)
    # frames: deepest first
    root = str(repo.resolve())
    depth: dict[tuple[str, str], int] = {}
    for t in failing:
        fr = frames(t.get("output", ""), root)
        for d, (p, ln) in enumerate(reversed(fr)):
            hits = [c for c in chunks if c.file == p and c.start <= ln <= c.end]
            if hits:
                key = min(hits, key=lambda c: c.end - c.start)
                k = (key.file, key.qualname)
                depth[k] = min(depth.get(k, 10 ** 6), d)
    for k, d in depth.items():
        signal["frames"][k] = float(d)
        cands[k].frame_depth = d
    # fuse
    ranks = {"diff": _ranks(signal["diff"], True), "hops": _ranks(signal["hops"], False),
             "reach": _ranks(signal["reach"], True), "frames": _ranks(signal["frames"], False)}
    out = []
    for key, cand in cands.items():
        cand.ranks = {s: ranks[s][key] for s in SIGNALS if key in ranks[s]}
        cand.score = sum(1.0 / (RRF_K + r) for r in cand.ranks.values())
        if cand.ranks:
            out.append(cand)
    out.sort(key=lambda c: (-c.score, c.file, c.start, c.qualname))
    return out


def graph_coverage(view: dict, chunks: list[Chunk], failing: list[dict]) -> dict:
    """How much the graph can say: failing tests found as graph nodes, and source functions their `calls` reach."""
    fn_of, tests = node_index(view, chunks)
    files = {f for f, _ in tests}
    seeds = sorted({s for t in failing for s in tests.get(test_key(t["test_id"], files), [])})
    reach = bfs(calls_adjacency(view), seeds) if seeds else {}
    return {"failing_tests": len(failing),
            "mapped_tests": sum(1 for t in failing if tests.get(test_key(t["test_id"], files))),
            "reachable_functions": sum(1 for nid in reach if nid in fn_of)}


def evidence(ranked: list[Candidate], n: int = 5) -> dict:
    """What the decision log stores for a localisation: top candidates and their graph paths (node ids, hops)."""
    top = ranked[:n]
    return {"ranked": [c.to_json() for c in top],
            "paths": [{"node": c.node or f"{c.file}::{c.qualname}", "hops": c.hops, "path": c.path} for c in top if c.path],
            "signals": {s: sum(1 for c in ranked if s in c.ranks) for s in SIGNALS}, "rrf_k": RRF_K, "max_hops": MAX_HOPS}


def as_chunks(ranked: list[Candidate], repo: Path, n: int = 3) -> list[Chunk]:
    """The top `n` candidates as repair chunks (the repair context when ``BR_LOCALIZE=graph``)."""
    out = []
    for c in ranked[:n]:
        lines = (repo / c.file).read_text(encoding="utf-8").splitlines()
        out.append(Chunk(c.file, c.qualname, c.start, c.end, c.start, c.score, "\n".join(lines[c.start - 1:c.end])))
    return out
