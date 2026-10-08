"""Export recorded demo runs of the pipeline to JSON for the static demo site.

Read-only, offline and deterministic, like `analysis/demo_walkthrough.py`, whose
selection, gates, failure classes and offline graph build it reuses. The only
writes are under `demo-web/public/data/`:

  - `instances/<repo>__<run>.json`: the eight stages of one strict instance
    (change, raw log, parsed outcome, head vs base, verdict, bound test file,
    graph paths, predictors vs reality);
  - `index.json`: the exported instances;
  - `results.json`: headline numbers parsed out of `paper/generated/*.md`, each
    block naming its source file (nothing is hard-coded).

Up to `MAX_INSTANCES` instances that clear gates 1-4 of the walkthrough
(holdout jobs excluded by its guard) and whose graph is on disk or buildable
from local git objects are exported, code-level failures first. Predictions
mirror `analysis/rq1_divergence.py` at k = 10: trailing, symmetric co-change
and the strict historical-frequency baseline. No field carries a wall-clock
time; every file carries `generated_at_git_sha`.

Exit status: 0 exported >= 1 instance; 2 nothing qualified.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

import networkx as nx
import pandas as pd

from analysis import demo_walkthrough as dw
from analysis import paper_md
from analysis import rq1_divergence as rq1

OUT_DIR = Path("demo-web/public/data")
GENERATED = Path("paper/generated")
MAX_INSTANCES = 8
K = 10
N_PATHS = 3
MAX_LOG_LINES = 12


# -- selection ---------------------------------------------------------------


def select_instances(limit: int = MAX_INSTANCES) -> tuple[list[dw.Candidate], list[str]]:
    """Up to `limit` instances clearing gates 1-4 with an on-disk or buildable graph.

    Args:
        limit: Maximum instances.

    Returns:
        `(candidates, report_lines)` in the walkthrough's preference order
        (code-level > unknown > timeout; environment failures are never shown).
    """
    from src.graph.build import graph_path

    rows, report = dw.gated_rows()
    rows = rows[rows["rank"] <= 2].drop_duplicates("run_id", keep="first")
    chosen: list[dw.Candidate] = []
    local: dict[tuple[str, str], bool] = {}
    for r in rows.itertuples():
        if len(chosen) >= limit:
            break
        if graph_path(r.repo, r.base_sha, dw.GRAPH_DIR).exists():
            gdir = dw.GRAPH_DIR
        else:
            key = (r.repo, r.base_sha)
            if key not in local:
                clone = dw.clone_dir(r.repo)
                local[key] = clone.exists() and dw.tree_is_local(clone, r.base_sha)
            if not local[key]:
                continue
            gdir = None
        chosen.append(dw.Candidate(r.repo, int(r.pr_number), int(r.run_id), r.head_sha, r.base_sha,
                                   r.test_id, int(r.job_id), gdir, r.failure_message,
                                   r.failure_class, r.failure_rule))
    report.append(f"exported: {len(chosen)} instance(s) (limit {limit}); (repo, base SHA) pairs "
                  f"checked for a fully local tree: {len(local)}, buildable {sum(local.values())}")
    return chosen, report


def instance_id(c: dw.Candidate) -> str:
    """File-safe id `<owner__name>__<run_id>`."""
    return f"{c.repo.replace('/', '__')}__{c.run_id}"


# -- stages ------------------------------------------------------------------


class Tables:
    """The parquet inputs, read once."""

    def __init__(self) -> None:
        self.inst = dw._read("instances_raw")
        self.res = dw._read("base_resolution_new")
        self.par = dw._read("parsed_outcomes")
        self.bout = dw._read("base_outcomes")
        self.out = dw._read("outcomes")
        self.bind = dw._read("binding")
        self.cs = dw._read("changesets")


def stage_change(c: dw.Candidate, t: Tables) -> dict:
    """Stage 1: the PR, its commits and changed files."""
    row = t.inst[t.inst["run_id"] == c.run_id].iloc[0]
    rres = t.res[t.res["run_id"] == c.run_id].iloc[0]
    cs = t.cs[(t.cs["repo"] == c.repo) & (t.cs["pr_number"].astype(str) == str(c.pr))
              & (t.cs["head_sha"] == c.head_sha)].sort_values("filename")
    return {
        "repo": c.repo, "pr_number": c.pr, "run_id": c.run_id,
        "workflow_name": str(row["workflow_name"]), "language": str(row["language"]),
        "head_sha": c.head_sha, "base_sha": c.base_sha, "base_status": str(rres["status"]),
        "changed_files": [{"path": f.filename, "status": str(f.status), "additions": int(f.additions),
                           "deletions": int(f.deletions)} for f in cs.itertuples()],
    }


def stage_log(c: dw.Candidate) -> dict:
    """Stage 2: raw log lines naming the failing test, failure lines flagged."""
    from src.harvest.rawstore import RawStore

    body = RawStore().read_records(c.repo, "logs", c.job_id)[0].body.decode("utf-8", "replace")
    lines = dw.log_excerpt(body, c.test_id, MAX_LOG_LINES)
    return {"job_id": c.job_id, "test_name_token": dw.short_name(c.test_id),
            "lines": [{"text": ln, "failing": bool(dw._FAIL_WORDS.search(ln))} for ln in lines]}


def stage_parsed(c: dw.Candidate, t: Tables, log: dict) -> dict:
    """Stage 3: raw log line -> canonical test_id and its parsed fields."""
    po = t.par[(t.par["run_id"] == c.run_id) & (t.par["test_id"] == c.test_id)
               & (t.par["job_id"] == c.job_id)].iloc[0]
    raw = next((ln["text"] for ln in log["lines"] if ln["failing"]), log["lines"][0]["text"] if log["lines"] else "")
    return {
        "raw_log_line": raw, "test_id": c.test_id, "status": str(po["status"]),
        "harness": str(po["harness"]), "parser_confidence": round(float(po["parser_confidence"]), 4),
        "is_fqcn_qualified": bool(po["is_fqcn_qualified"]),
        "params": None if pd.isna(po["params"]) else str(po["params"]),
        "failure_message": (c.failure_message or "")[:dw.MAX_LINE_CHARS],
        "failure_class": c.failure_class, "failure_rule": c.failure_rule,
    }


def stage_head_base(c: dw.Candidate, t: Tables) -> tuple[dict, set[str], set[str]]:
    """Stage 4: which tests failed at head and at the resolved base run."""
    rres = t.res[t.res["run_id"] == c.run_id].iloc[0]
    brid = rres["base_run_id"]
    concl = None
    if not pd.isna(brid):
        brow = t.inst[t.inst["run_id"] == int(brid)]
        concl = str(brow["run_conclusion"].iloc[0]) if len(brow) and brow["run_conclusion"].iloc[0] else None
    t_head = set(t.par[t.par["run_id"] == c.run_id]["test_id"])
    t_base = set(t.bout[t.bout["run_id"] == c.run_id]["test_id"])
    return {
        "base_run_id": None if pd.isna(brid) else int(brid),
        "base_run_distance": None if pd.isna(rres["base_run_distance"]) else float(rres["base_run_distance"]),
        "base_run_conclusion": concl,
        "tests": [{"test_id": x, "head": "fail", "base": "fail" if x in t_base else "no failure recorded"}
                  for x in sorted(t_head | t_base)],
    }, t_head, t_base


def stage_verdict(c: dw.Candidate, t: Tables, t_head: set[str], t_base: set[str]) -> dict:
    """Stage 5: T_reveal = T_head_fail - T_base_fail - flaky."""
    flaky, n_sib = dw.run_flaky(c.run_id, c.head_sha, t_head, t.res, t.inst, t.par)
    reveal = t_head - t_base - flaky
    recorded = set(t.out[(t.out["run_id"] == c.run_id) & (t.out["split"] == "strict")]["test_id"])
    return {
        "t_head_fail": sorted(t_head), "t_base_fail": sorted(t_base), "flaky": sorted(flaky),
        "sibling_runs": n_sib, "t_reveal": sorted(reveal),
        "selected_test": c.test_id, "selected_is_fault_revealing": c.test_id in reveal,
        "agrees_with_outcomes_parquet": recorded == reveal, "recorded_strict": len(recorded),
    }


def stage_binding(c: dw.Candidate, t: Tables, reveal: list[str]) -> dict:
    """Stage 6: the test file each fault-revealing test binds to at the pinned commit."""
    b = t.bind[t.bind["repo"] == c.repo].set_index("test_id")
    rows = []
    for x in reveal:
        if x in b.index:
            r = b.loc[x]
            rows.append({"test_id": x, "resolved_path": None if pd.isna(r["resolved_path"]) else str(r["resolved_path"]),
                         "status": str(r["status"]), "candidates_considered": int(r["candidates_considered"])})
        else:
            rows.append({"test_id": x, "resolved_path": None, "status": "absent", "candidates_considered": 0})
    sel = next(r for r in rows if r["test_id"] == c.test_id)
    return {"selected": sel, "all": rows, "pins_file": "docs/CLONE_PINS.json"}


def _edge_relation(graph: nx.MultiDiGraph, a: str, b: str) -> tuple[str, str]:
    """Relation of the edge between `a` and `b` (either direction) and its direction."""
    for src, dst, arrow in ((a, b, "forward"), (b, a, "backward")):
        if graph.has_edge(src, dst):
            data = min((graph.get_edge_data(src, dst) or {}).values(),
                       key=lambda d: str(d.get("edge_type") or d.get("relation") or ""))
            return str(data.get("edge_type") or data.get("relation") or "related"), arrow
    return "related", "forward"


BLAST_HOPS = 4
BLAST_MAX_NODES = 150
BLAST_MAX_EDGES = 400


def node_kind(d: dict) -> str:
    """`test` / `file` / `function` / `class` for one graph node's attributes."""
    if d.get("node_type") == "test" or d.get("test_id"):
        return "test"
    if d.get("source_location") == "L1":
        return "file"
    return "function" if str(d.get("label") or "").endswith(")") else "class"


def blast_radius(graph: nx.MultiDiGraph, undirected: nx.Graph, changed: list[tuple[str, str | None]],
                 preds: dict, path_nodes: list[str]) -> dict:
    """The code-graph neighbourhood within `BLAST_HOPS` hops of any changed file.

    Hops are on the undirected projection. Nodes are taken in priority order
    (changed files, actual failing test files, co-change predictions, history
    predictions, nodes on shortest paths, then nearest by hop, ties by id) up
    to `BLAST_MAX_NODES`; predicted or failing files farther than
    `BLAST_HOPS` hops, or absent from the graph, get `hop: None` (the outer ring).

    Args:
        graph: The bound base-commit graph.
        undirected: Its undirected projection.
        changed: `(changed_file, node_or_None)` pairs.
        preds: Stage 8 (`stage_predictions`) output.
        path_nodes: Node ids on stage 7's shortest paths.

    Returns:
        `{nodes, edges, max_hops, caps, truncated}`.
    """
    file_nodes: dict[str, str] = {}
    for n, d in sorted(graph.nodes(data=True)):
        if d.get("source_location") == "L1" and d.get("source_file"):
            file_nodes.setdefault(str(d["source_file"]), n)
    flags = {"changed": {f for f, _ in changed}, "actual_failing": {x["path"] for x in preds["actual"]},
             "cochange_pred": {x["path"] for x in preds["cochange"]},
             "history_pred": {x["path"] for x in preds["history"]}}
    sources = sorted({n for _, n in changed if n})
    dist: dict[str, int] = {n: 0 for n in sources}
    parent: dict[str, str] = {}
    frontier = list(sources)
    for hop in range(1, BLAST_HOPS + 1):
        nxt = []
        for u in frontier:
            for v in sorted(undirected.neighbors(u)):
                if v not in dist:
                    dist[v], parent[v] = hop, u
                    nxt.append(v)
        frontier = nxt

    def chain(n: str) -> list[str]:
        out = []
        while n in parent:
            n = parent[n]
            out.append(n)
        return out

    order: list[str] = []
    outer: list[str] = []
    for name in ("changed", "actual_failing", "cochange_pred", "history_pred"):
        for f in sorted(flags[name]):
            n = file_nodes.get(f)
            if n is not None and n in dist:
                order.append(n)
            else:
                outer.append(f)
    for n in order[:]:
        order.extend(chain(n))
    order.extend(n for n in path_nodes if n in dist)
    order.extend(sorted(dist, key=lambda n: (dist[n], n)))
    keep: list[str] = []
    seen: set[str] = set()
    outer_ids = [f"outer:{f}" for f in dict.fromkeys(outer)][:BLAST_MAX_NODES]
    room = BLAST_MAX_NODES - len(outer_ids)
    for n in order:
        if n not in seen and len(keep) < room:
            seen.add(n)
            keep.append(n)
    by_node = {n: f for f, n in file_nodes.items()}

    def entry(nid: str) -> dict:
        if nid.startswith("outer:"):
            f, d, hop, kind = nid[len("outer:"):], {}, None, "file"
        else:
            d = graph.nodes[nid]
            f, hop, kind = by_node.get(nid) or d.get("source_file"), dist[nid], node_kind(d)
        lab = str(d.get("label") or (f or nid).rsplit("/", 1)[-1])
        e = {"id": nid, "label": lab, "path": f, "kind": kind, "hop": hop, "in_graph": not nid.startswith("outer:")}
        is_file = nid in by_node or nid.startswith("outer:")
        e.update({k: bool(is_file and f in v) for k, v in flags.items()})
        if kind == "file" and e["actual_failing"]:
            e["kind"] = "test"
        return e

    nodes = [entry(n) for n in keep] + [entry(n) for n in outer_ids]
    nodes.sort(key=lambda e: (e["hop"] is None, e["hop"] or 0, e["id"]))
    kept = set(keep)
    edges = sorted({tuple(sorted((a, b))) for a, b in undirected.subgraph(kept).edges() if a != b},
                   key=lambda ab: (max(dist[ab[0]], dist[ab[1]]), ab))
    return {"nodes": nodes, "edges": [{"source": a, "target": b} for a, b in edges[:BLAST_MAX_EDGES]],
            "max_hops": BLAST_HOPS, "caps": {"nodes": BLAST_MAX_NODES, "edges": BLAST_MAX_EDGES},
            "truncated": {"nodes": len(dist) + len(outer_ids) > len(nodes), "edges": len(edges) > BLAST_MAX_EDGES},
            "within_hops_total": len(dist), "note": "hops on the undirected projection from the nearest changed file"}


def stage_graph(c: dw.Candidate, test_file: str, changed: list[str], cache: dict,
                preds: dict | None = None) -> dict:
    """Stage 7: shortest paths from the test node to the nearest changed files.

    With `preds` (stage 8), also the blast-radius neighbourhood (`blast_radius`).
    """
    from src.graph.build import build_graph_at, graph_path, load_graph
    from src.graph.query import UNREACHABLE, GraphQuery
    from src.graph.test_nodes import bind_test_ids

    key = (c.repo, c.base_sha)
    if key not in cache:
        gdir, built = c.graph_dir, c.graph_dir is None
        with tempfile.TemporaryDirectory(prefix="br-export-") as tmp:
            if built:
                gdir = Path(tmp)
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    build_graph_at(c.repo, c.base_sha, clone_dir=dw.clone_dir(c.repo), out_dir=gdir)
            cache[key] = (load_graph(graph_path(c.repo, c.base_sha, gdir)), built)
    graph, built = cache[key]
    graph = graph.copy()
    bind_test_ids(graph, [c.test_id], repo=c.repo)
    tnode, how, mapped = dw.map_nodes(graph, c.test_id, test_file, changed)
    q = GraphQuery(graph, repo=c.repo, sha=c.base_sha)

    def label(n: str) -> dict:
        d = graph.nodes[n]
        return {"id": n, "label": str(d.get("label") or n), "file": d.get("source_file"),
                "kind": str(d.get("file_type") or d.get("node_type") or "")}

    dists = []
    for f, node in mapped:
        d = q.shortest_path_length(node, tnode) if (node and tnode) else UNREACHABLE
        dists.append({"file": f, "node": node, "hops": None if d == UNREACHABLE else d,
                      "in_graph": node is not None})
    reach = sorted((x for x in dists if x["hops"] is not None), key=lambda x: (x["hops"], x["file"]))
    paths = []
    for x in reach[:N_PATHS]:
        p = nx.shortest_path(q._undirected, tnode, x["node"])
        paths.append({"changed_file": x["file"], "hops": x["hops"], "nodes": [label(n) for n in p],
                      "edges": [dict(zip(("relation", "direction"), _edge_relation(graph, a, b)),
                                     source=a, target=b) for a, b in zip(p, p[1:])]})
    nodes = [n for _, n in mapped if n]
    m = q.min_distance_to_any_changed(tnode, nodes) if (tnode and nodes) else UNREACHABLE
    return {
        "graph_commit": c.base_sha, "built_offline_from_local_git": built,
        "n_nodes": graph.number_of_nodes(), "n_edges": graph.number_of_edges(),
        "test_node": label(tnode) if tnode else None, "test_node_how": how,
        "changed_distances": dists, "paths": paths,
        "min_distance_to_any_changed": None if m == UNREACHABLE else m,
        "distance_note": "hops on the undirected projection (src/graph/query.py)",
        "blast": None if preds is None else blast_radius(
            graph, q._undirected, mapped, preds,
            sorted({n["id"] for p in paths for n in p["nodes"]})),
    }


def stage_predictions(c: dw.Candidate, data: rq1.Rq1Data) -> dict:
    """Stage 8: co-change and historical-frequency top-k vs the actual failing test files.

    Mirrors `rq1_divergence.evaluate_k` for one instance: trailing symmetric
    co-change (top-k partners per changed file, minus the changed files) and
    the strict historical-frequency baseline.
    """
    row = data.valid_runs[data.valid_runs["run_id"] == c.run_id].iloc[0]
    gt = rq1.ground_truth(data).get((c.repo, c.run_id), set())
    changed = data.pr_to_changed.get((c.repo, str(row["pr_number"])), set())
    co: dict[str, float] = {}
    for f in sorted(changed):
        for p in rq1.partner_stats(data, c.repo, f, row)[:K]:
            if p.path not in changed:
                co[p.path] = max(co.get(p.path, 0.0), p.confidence)
    h = rq1.historical_evidence(data, c.repo, row)
    counts = h["resolved_path"].value_counts().head(K) if len(h) else pd.Series(dtype=int)
    co_items = sorted(co.items(), key=lambda kv: (-kv[1], kv[0]))
    co_set, hist_set = set(co), set(counts.index)
    cp, cr, _ = rq1.compute_metrics(co_set, gt)
    hp, hr, _ = rq1.compute_metrics(hist_set, gt)
    return {
        "k": K, "run_started_at": str(row["run_started_at"]),
        "cochange": [{"path": p, "confidence": round(v, 4), "hit": p in gt} for p, v in co_items],
        "history": [{"path": str(p), "past_failures": int(n), "hit": p in gt} for p, n in counts.items()],
        "actual": [{"path": p, "caught_by_cochange": p in co_set, "caught_by_history": p in hist_set}
                   for p in sorted(gt)],
        "metrics": {"cochange": {"precision": round(cp, 4), "recall": round(cr, 4),
                                 "hits": len(co_set & gt), "predicted": len(co_set)},
                    "history": {"precision": round(hp, 4), "recall": round(hr, 4),
                                "hits": len(hist_set & gt), "predicted": len(hist_set)},
                    "n_actual": len(gt)},
    }


def export_instance(c: dw.Candidate, t: Tables, data: rq1.Rq1Data, cache: dict, sha: str) -> dict:
    """All eight stages of one instance."""
    s1 = stage_change(c, t)
    s2 = stage_log(c)
    s3 = stage_parsed(c, t, s2)
    s4, t_head, t_base = stage_head_base(c, t)
    s5 = stage_verdict(c, t, t_head, t_base)
    s6 = stage_binding(c, t, s5["t_reveal"])
    s8 = stage_predictions(c, data)
    s7 = stage_graph(c, s6["selected"]["resolved_path"], [f["path"] for f in s1["changed_files"]], cache, s8)
    return {"id": instance_id(c), "generated_at_git_sha": sha,
            "stages": {"change": s1, "raw_log": s2, "parsed_outcome": s3, "head_vs_base": s4,
                       "verdict": s5, "binding": s6, "graph": s7, "predictions": s8}}


# -- results from paper/generated --------------------------------------------

_RATE = re.compile(r"^([\d,]+)/([\d,]+)")


def md_tables(path: Path) -> list[tuple[list[str], list[str], list[list[str]]]]:
    """Every markdown table in `path` as `(heading_trail, columns, rows)`."""
    out, heads = [], []
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("#"):
            level = len(ln) - len(ln.lstrip("#"))
            heads = heads[:level - 1] + [ln.lstrip("#").strip()]
        if ln.startswith("|") and i + 1 < len(lines) and lines[i + 1].startswith("|---"):
            cols = [x.strip() for x in ln.strip("|").split("|")]
            rows, i = [], i + 2
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([x.strip() for x in lines[i].strip("|").split("|")])
                i += 1
            out.append((list(heads), cols, rows))
            continue
        i += 1
    return out


def find_table(path: Path, *heads: str) -> tuple[list[str], list[list[str]]]:
    """The first table whose heading trail ends with `heads`."""
    for trail, cols, rows in md_tables(path):
        if trail[-len(heads):] == list(heads):
            return cols, rows
    raise SystemExit(f"BLOCKED: no table under {' > '.join(heads)} in {path}")


def rate(cell: str) -> dict:
    """`'1,234/5,678 (21.73%)'` -> `{n, d, text}`."""
    m = _RATE.match(cell)
    if not m:
        raise SystemExit(f"BLOCKED: not a rate: {cell!r}")
    return {"n": int(m.group(1).replace(",", "")), "d": int(m.group(2).replace(",", "")), "text": cell}


def num(cell: str) -> float:
    """A plain number cell."""
    return float(cell.replace(",", ""))


def source_sha(path: Path) -> str | None:
    """The git sha a generated file names in its header."""
    m = re.search(r"at git `([0-9a-f]{7,40}|unknown)`", path.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def results(sha: str) -> dict:
    """Headline numbers parsed out of `paper/generated/*.md`."""
    def src(name: str) -> dict:
        p = GENERATED / name
        return {"source": str(p), "source_generated_at_git_sha": source_sha(p)}

    p = GENERATED / "rq1.md"
    cols, rows = find_table(p, "k = 10", "Overall")
    rq = [{"method": r[0], "n": int(num(r[1])), "mean_precision": num(r[2]), "mean_recall": num(r[3]),
           "mean_jaccard": num(r[4]), "micro_precision": rate(r[5]), "micro_recall": rate(r[6]),
           "median_size": num(r[7])} for r in rows]

    p = GENERATED / "attrition_funnel.md"
    _, rows = find_table(p, "Runs (benchmark instances)")
    funnel = [{"stage": r[0], "count": int(num(r[1])), "of_previous": r[2], "source": r[4]} for r in rows]

    p = GENERATED / "gates.md"
    _, rows = find_table(p, "Gates")
    gates = [{"gate": r[0], "measured": rate(r[1]), "threshold": r[2], "verdict": r[3]} for r in rows]
    p = GENERATED / "binding.md"
    _, rows = find_table(p, "Test-to-file binding (D-47, D-50)")
    binding = [{"measure": r[0], "value": rate(r[1])} for r in rows]

    p = GENERATED / "leakage_audit.md"
    _, cur = find_table(p, "Co-change")
    _, leg = find_table(p, "Co-change", "Legacy static table (`data/interim/cochange.parquet`)")
    cur_row = next(r for r in cur if r[0].startswith("a commit at or after"))
    leg_row = next(r for r in leg if r[0].startswith("a mined commit dated in"))
    audited = next(r for r in cur if r[0].startswith("instances audited"))

    p = GENERATED / "infra_failures.md"
    _, by_class = find_table(p, "Environment-failure audit of the strict labels", "Strict labels by class")
    _, inst = find_table(p, "Environment-failure audit of the strict labels", "Strict instances")

    return {
        "generated_at_git_sha": sha,
        "rq1_k10": {**src("rq1.md"), "k": 10, "methods": rq},
        "runs_funnel": {**src("attrition_funnel.md"), "stages": funnel},
        "gates": {**src("gates.md"), "rows": gates},
        "binding": {**src("binding.md"), "rows": binding},
        "leakage": {**src("leakage_audit.md"), "audited": rate(audited[1]),
                    "legacy_check": leg_row[0], "legacy_violations": rate(leg_row[1]),
                    "current_check": cur_row[0], "current_violations": rate(cur_row[1])},
        "environment_audit": {**src("infra_failures.md"),
                              "labels_by_class": [{"class": r[0], "labels": rate(r[1])} for r in by_class],
                              "instances": [{"measure": r[0], "value": rate(r[1])} for r in inst]},
    }


def overview(sha: str) -> dict:
    """KPI cards and the headline recall chart, parsed out of `paper/generated/*.md`."""
    def row(rows: list[list[str]], first: str) -> list[str]:
        return next(r for r in rows if r[0] == first)

    p_f = GENERATED / "attrition_funnel.md"
    _, repos = find_table(p_f, "Repositories")
    _, runs = find_table(p_f, "Runs (benchmark instances)")
    p_c = GENERATED / "composition.md"
    _, split = find_table(p_c, "Per split")
    strict = row(split, "strict")
    p_b = GENERATED / "binding.md"
    _, bind = find_table(p_b, "Test-to-file binding (D-47, D-50)")
    p_r = GENERATED / "rq1.md"
    _, rq = find_table(p_r, "k = 10", "Overall")
    methods = sorted(({"method": r[0], "n": int(num(r[1])), "micro_recall": rate(r[6])} for r in rq),
                     key=lambda m: (-m["micro_recall"]["n"] / m["micro_recall"]["d"], m["method"]))
    kpi = [
        ("repositories swept", int(num(row(repos, "swept (>= 1 run harvested)")[1])), p_f),
        ("CI runs harvested", int(num(row(runs, "runs discovered")[1])), p_f),
        ("failed runs", int(num(row(runs, "failed runs")[1])), p_f),
        ("strict instances", int(num(row(runs, "with >= 1 strict label")[1])), p_f),
        ("fault-revealing labels (strict)", rate(strict[4])["n"], p_c),
        ("distinct tests (strict)", int(num(strict[5])), p_c),
    ]
    return {
        "generated_at_git_sha": sha,
        "kpis": [{"label": k, "value": v, "source": str(s)} for k, v, s in kpi],
        "binding": {"source": str(p_b),
                    "combined": rate(row(bind, "combined (exact)")[1]),
                    "full_confidence": rate(row(bind, "full confidence (exact, fully-qualified class name)")[1])},
        "headline": {"source": str(p_r), "source_generated_at_git_sha": source_sha(p_r), "k": 10,
                     "methods": methods},
    }


# -- main --------------------------------------------------------------------


def write_json(path: Path, obj: dict) -> None:
    """Deterministic JSON (sorted keys, fixed separators, trailing newline)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main(out_dir: Path = OUT_DIR) -> int:
    """Select, export and index the instances, then write `results.json`.

    Args:
        out_dir: Output directory (the only place written to).

    Returns:
        Process exit status.
    """
    os.environ["GIT_NO_LAZY_FETCH"] = "1"
    sha = paper_md.git_sha()
    chosen, report = select_instances()
    for line in report:
        print(line)
    if not chosen:
        print("NO QUALIFYING INSTANCE: nothing exported")
        return 2
    t, data, cache = Tables(), rq1.load_data(), {}
    inst_dir = out_dir / "instances"
    if inst_dir.exists():
        shutil.rmtree(inst_dir)
    index = []
    for c in chosen:
        doc = export_instance(c, t, data, cache, sha)
        write_json(inst_dir / f"{doc['id']}.json", doc)
        st = doc["stages"]
        index.append({"id": doc["id"], "repo": c.repo, "pr_number": c.pr, "run_id": c.run_id,
                      "failure_class": c.failure_class, "test_count": len(st["verdict"]["t_reveal"]),
                      "selected_test": c.test_id})
        print(f"wrote {inst_dir / doc['id']}.json")
    write_json(out_dir / "index.json", {"generated_at_git_sha": sha, "default": index[0]["id"],
                                        "instances": index, "selection": report})
    write_json(out_dir / "results.json", results(sha))
    write_json(out_dir / "overview.json", overview(sha))
    print(f"wrote {out_dir / 'index.json'}, {out_dir / 'results.json'} and {out_dir / 'overview.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
