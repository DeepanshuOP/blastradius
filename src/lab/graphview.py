"""The code graph of a repository at one commit, in a Cytoscape-ready shape.

Built with `src.graph.build.build_graph_at` (the project's own builder) into a scratch directory. Node types are
derived from what that graph records: a node's `node_type` (`test` marks test code), its label (`name()` is a
function or method, `x.py` a file, anything else a class). Edge types are families of the graph's relations.
"""

from __future__ import annotations

import ast
import json
import re
from collections import deque
from pathlib import Path

import networkx as nx

MAX_STREAM_NODES = 600
HOP_LIMIT = 4
EDGE_FAMILY = {"calls": "call", "imports": "import", "imports_from": "import", "re_exports": "import",
               "contains": "contains", "method": "contains", "tests": "tests", "tests_by_convention": "tests"}
_TEST_PATH = re.compile(r"(^|/)(tests?|test_[^/]*|[^/]*_test\.py)(/|$)")


def _kind(label: str, source_file: str, node_type: str | None) -> str:
    if label.endswith("()"):
        return "test" if node_type == "test" else "function"
    if re.search(r"\.(py|java)$", label) or label.endswith("/__init__.py"):
        return "file"
    return "class"


def to_cytoscape(g: nx.MultiDiGraph) -> dict:
    """All source nodes and the edges between them. Placeholder nodes for external names are left out and counted."""
    nodes, keep = [], set()
    external = rationale = 0
    for nid, d in g.nodes(data=True):
        if d.get("file_type") == "rationale":
            rationale += 1
            continue
        if not d.get("source_file"):
            external += 1
            continue
        label = str(d.get("label", nid))
        sf = str(d.get("source_file", ""))
        kind = _kind(label, sf, d.get("node_type"))
        keep.add(nid)
        nodes.append({"id": str(nid), "label": label, "type": kind, "file": sf, "line": d.get("start_line"),
                      "community": d.get("community_id"), "pagerank": round(float(d.get("pagerank") or 0), 5),
                      "is_test_file": bool(_TEST_PATH.search(sf)) or d.get("node_type") == "test"})
    edges, seen = [], set()
    for u, v, d in g.edges(data=True):
        if u in keep and v in keep and u != v:
            rel = str(d.get("relation", "ref"))
            fam = EDGE_FAMILY.get(rel, "ref")
            k = (str(u), str(v), fam)
            if k in seen:
                continue
            seen.add(k)
            edges.append({"id": f"e{len(edges)}", "source": str(u), "target": str(v), "type": fam, "relation": rel,
                          "line": str(d.get("source_location", ""))})
    nodes.sort(key=lambda n: n["id"])
    return {"nodes": nodes, "edges": edges, "external_nodes_omitted": external, "rationale_nodes_omitted": rationale}


def undirected(view: dict) -> nx.Graph:
    """Undirected projection (impact travels both ways along an edge, as `GraphQuery` measures it)."""
    u = nx.Graph()
    u.add_nodes_from(n["id"] for n in view["nodes"])
    u.add_edges_from((e["source"], e["target"]) for e in view["edges"])
    return u


def hops_from(u: nx.Graph, seeds: list[str], limit: int = HOP_LIMIT) -> dict[str, int]:
    """Hop distance of every node within `limit` of the nearest seed."""
    dist = {s: 0 for s in seeds if s in u}
    q = deque(dist)
    while q:
        cur = q.popleft()
        if dist[cur] >= limit:
            continue
        for nb in u.neighbors(cur):
            if nb not in dist:
                dist[nb] = dist[cur] + 1
                q.append(nb)
    return dist


def stream_subset(view: dict, changed_nodes: list[str], changed_files: list[str]) -> tuple[dict, bool]:
    """Everything when it has at most MAX_STREAM_NODES nodes; else file nodes plus the 2-hop neighbourhood of the change."""
    if len(view["nodes"]) <= MAX_STREAM_NODES:
        return view, False
    u = undirected(view)
    seeds = [n for n in changed_nodes if n in u]
    seeds += [n["id"] for n in view["nodes"] if n["file"] in set(changed_files) and n["type"] == "file"]
    keep = {n["id"] for n in view["nodes"] if n["type"] == "file"} | set(hops_from(u, seeds, 2))
    nodes = [n for n in view["nodes"] if n["id"] in keep]
    edges = [e for e in view["edges"] if e["source"] in keep and e["target"] in keep]
    return {**view, "nodes": nodes, "edges": edges}, True


def count_by_type(view: dict) -> dict:
    out = {"nodes": {}, "edges": {}}
    for n in view["nodes"]:
        out["nodes"][n["type"]] = out["nodes"].get(n["type"], 0) + 1
    for e in view["edges"]:
        out["edges"][e["type"]] = out["edges"].get(e["type"], 0) + 1
    return out


def function_spans(source: str) -> list[tuple[int, int, str, int]]:
    """`(first line incl. decorators, last line, qualified name, def line)` of every function in a Python source."""
    return _spans(source)[0]


def _spans(source: str) -> tuple[list[tuple[int, int, str, int]], list[tuple[int, int, str]]]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [], []
    funcs: list[tuple[int, int, str, int]] = []
    classes: list[tuple[int, int, str]] = []

    def walk(node: ast.AST, scope: list[str]) -> None:
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                q = [*scope, ch.name]
                first = min([ch.lineno] + [d.lineno for d in ch.decorator_list])
                if isinstance(ch, ast.ClassDef):
                    classes.append((first, ch.end_lineno or ch.lineno, ".".join(q)))
                else:
                    funcs.append((first, ch.end_lineno or ch.lineno, ".".join(q), ch.lineno))
                walk(ch, q)
            else:
                walk(ch, scope)

    walk(tree, [])
    return funcs, classes


def changed_line_ranges(diff: str) -> dict[str, list[int]]:
    """Old-side (base commit) line numbers touched by each file's hunks: removed lines, and the line before an insertion."""
    out: dict[str, list[int]] = {}
    cur = None
    old = 0
    for ln in diff.splitlines():
        if ln.startswith("--- a/"):
            cur = ln[6:]
            out.setdefault(cur, [])
        elif ln.startswith("--- /dev/null"):
            cur = None
        elif ln.startswith("+++ b/") and cur is None:
            cur = ln[6:]
            out.setdefault(cur, [])
        elif ln.startswith("@@"):
            m = re.match(r"@@ -(\d+)", ln)
            old = int(m.group(1)) if m else 0
        elif cur is not None and ln.startswith("-") and not ln.startswith("---"):
            out[cur].append(old)
            old += 1
        elif cur is not None and ln.startswith("+") and not ln.startswith("+++"):
            out[cur].append(max(old - 1, 1))
        elif cur is not None and ln.startswith(" "):
            old += 1
    return out


def map_changed_nodes(view: dict, diff: str, base_sources: dict[str, str]) -> tuple[list[str], list[dict]]:
    """Graph node ids of the functions (and, failing that, files) the diff touches in the base commit.

    Returns:
        `(node ids, details)`; details carry file, function, and the node's line.
    """
    by_file: dict[str, list[dict]] = {}
    for n in view["nodes"]:
        by_file.setdefault(n["file"], []).append(n)
    ids: list[str] = []
    detail: list[dict] = []
    for path, lines in changed_line_ranges(diff).items():
        nodes = by_file.get(path, [])
        spans, class_spans = _spans(base_sources.get(path, ""))
        hit: set[str] = set()
        for ln in lines:
            inner = [s for s in spans if s[0] <= ln <= s[1]]
            if not inner:
                continue
            s = min(inner, key=lambda x: x[1] - x[0])           # innermost function containing the line
            leaf = s[2].rsplit(".", 1)[-1]
            owner = s[2].rpartition(".")[0]
            owner_span = next((c for c in class_spans if c[2] == owner), None) if owner else None
            cand = []
            for n in nodes:
                if n["type"] not in ("function", "test") or n["label"].lstrip(".") != f"{leaf}()" or n["line"] is None:
                    continue
                if owner_span is not None and not (owner_span[0] <= n["line"] <= owner_span[1]):
                    continue
                if owner_span is None and any(c[0] <= n["line"] <= c[1] for c in class_spans):
                    continue
                cand.append(n)
            # overloads share one graph node (the first definition): take the nearest at or before this definition
            cand = [n for n in cand if n["line"] <= s[3]] or cand
            for n in sorted(cand, key=lambda x: -x["line"])[:1]:
                if n["id"] not in hit:
                    hit.add(n["id"])
                    ids.append(n["id"])
                    detail.append({"id": n["id"], "file": path, "function": s[2], "line": s[3], "end": s[1]})
        if not hit:                                              # a change outside any function: its file node
            for n in nodes:
                if n["type"] == "file" and n["id"] not in ids:
                    ids.append(n["id"])
                    detail.append({"id": n["id"], "file": path, "function": "<module>", "line": 1, "end": None})
                    break
    return ids, detail


def paths_to_tests(view: dict, changed: list[str], at_risk_files: list[str], max_files: int = 10) -> list[dict]:
    """For each at-risk test file, the shortest path (node ids) from the nearest changed node to a test node there."""
    u = undirected(view)
    seeds = [c for c in changed if c in u]
    out: list[dict] = []
    if not seeds:
        return out
    # multi-source BFS keeping parents
    parent: dict[str, str | None] = {s: None for s in seeds}
    q = deque(seeds)
    while q:
        cur = q.popleft()
        for nb in u.neighbors(cur):
            if nb not in parent:
                parent[nb] = cur
                q.append(nb)
    for f in at_risk_files[:max_files]:
        cand = [n["id"] for n in view["nodes"] if n["file"] == f and n["type"] in ("test", "function", "file", "class")
                and n["id"] in parent]
        if not cand:
            out.append({"test_file": f, "path": [], "length": None, "reason": "no path from a changed node in the graph"})
            continue
        def depth(x: str) -> int:
            d = 0
            while parent[x] is not None:
                x = parent[x]
                d += 1
            return d
        best = min(cand, key=lambda x: (depth(x), x))
        path = [best]
        while parent[path[-1]] is not None:
            path.append(parent[path[-1]])
        path.reverse()
        out.append({"test_file": f, "path": path, "length": len(path) - 1, "target": best})
    return out


def store(view: dict, path: Path) -> None:
    """Write the full graph for `/api/lab/graph`."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(view, separators=(",", ":")), encoding="utf-8")
