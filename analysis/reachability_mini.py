"""Graph reachability vs real failures on the 3-repo mini-corpus (course result, D-48).

Question: on instances whose base-SHA graph exists in `data/graphs/`, how well does
"every test that can reach a changed file in the code graph" recover the tests that
actually failed, and what does that safety-style predictor cost in predicted size?

Nothing here feeds `make tables`, `paper/generated/`, `release/` or the paper (D-48).
The reachability rule below is copied from `src/agents/codebase.py` on purpose and is
NOT imported from it (D-55): the research script must not depend on the agent layer.
It deliberately uses only the edge set named in the task (no inherits/extends/implements).

Two scoring units, because the predictors emit different things:
  - test-id level: R (reachability) against strict fault-revealing `test_id`s;
  - file level: R's test files, trailing co-change and historical frequency, against the
    bound test files of the strict labels, exactly as `analysis/rq1_divergence.py`
    scores them (that script predicts files, never test ids).

Run: `BR_OFFLINE=1 uv run python -m analysis.reachability_mini [--json PATH]`
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
from collections import defaultdict, deque
from pathlib import Path
from typing import Iterable

import networkx as nx
import pandas as pd

from src.graph.build import graph_path, load_graph, repo_slug
from src.parse.test_ids import derive_node_id

K_VALS = [5, 10, 20]
MINI_CORPUS = ["fla-org/flash-linear-attention", "Stirling-Tools/Stirling-PDF", "spiculedata/saiku"]

#: Copied from src/agents/codebase.py (minus inherits/extends/implements, per the task).
DEP_EDGES = {"calls", "imports", "imports_from", "uses", "method", "tests",
             "tests_by_convention", "tests_by_layout"}


def file_node(graph: nx.MultiDiGraph, path: str) -> str | None:
    """The file-level node (`source_location` L1) of `path`, or None.

    Same rule as `analysis.demo_walkthrough.file_node`, copied so this script does not
    import that module's CLI dependencies.
    """
    return next((n for n, d in sorted(graph.nodes(data=True))
                 if d.get("source_file") == path and d.get("source_location") == "L1"), None)


def dependency_graph(graph: nx.MultiDiGraph) -> nx.DiGraph:
    """Dependency direction (u depends on v), `contains` followed from symbol to file."""
    dep = nx.DiGraph()
    dep.add_nodes_from(graph.nodes)
    for u, v, e in graph.edges(data=True):
        et = e.get("edge_type")
        if et in DEP_EDGES:
            dep.add_edge(u, v)
        elif et == "contains":
            dep.add_edge(v, u)
    return dep


def reachable_tests(graph: nx.MultiDiGraph, changed: Iterable[str]) -> list[tuple[str, int, str]]:
    """Graph test nodes that reach any changed file node, ranked.

    Args:
        graph: A bound graph (test nodes carry `test_id`).
        changed: Changed file paths of the instance.

    Returns:
        `(test_id, hop, test_file)` sorted by hop distance then `test_id`. A test_id
        reached through several nodes keeps its smallest hop.
    """
    dep = dependency_graph(graph)
    seeds = [n for n in (file_node(graph, f) for f in sorted(set(changed))) if n is not None]
    dist: dict[str, int] = {}
    queue: deque[str] = deque()
    for s in seeds:
        dist[s] = 0
        queue.append(s)
    while queue:  # multi-source BFS over reversed dependency edges
        cur = queue.popleft()
        for pred in dep.predecessors(cur):
            if pred not in dist:
                dist[pred] = dist[cur] + 1
                queue.append(pred)
    best: dict[str, tuple[int, str]] = {}
    for node, hop in dist.items():
        d = graph.nodes[node]
        tid = d.get("test_id")
        if d.get("node_type") != "test" or not tid:
            continue
        if tid not in best or hop < best[tid][0]:
            best[tid] = (hop, str(d.get("source_file", "")))
    return sorted(((t, h, f) for t, (h, f) in best.items()), key=lambda x: (x[1], x[0]))


def canonical_ids(graph: nx.MultiDiGraph, observed: Iterable[str]) -> dict[str, set[str]]:
    """Map each observed CI `test_id` to the graph's canonical test ids.

    Same two tiers as `src.graph.test_nodes.bind_test_ids`: exact, else the D-25 lossy
    key (a Gradle id without its package binds by suffix). Unbound ids map to an empty set.
    """
    exact: set[str] = set()
    keys: dict[str, set[str]] = defaultdict(set)
    for _, d in graph.nodes(data=True):
        if d.get("node_type") != "test" or not d.get("test_id"):
            continue
        exact.add(str(d["test_id"]))
        keys[str(d.get("graph_binding_key") or derive_node_id(str(d["test_id"])))].add(str(d["test_id"]))
    out: dict[str, set[str]] = {}
    for t in sorted({str(x) for x in observed if x}):
        if t in exact:
            out[t] = {t}
            continue
        probe = derive_node_id(t)
        out[t] = {c for k, ids in keys.items() if probe and (k == probe or k.endswith("_" + probe))
                  for c in ids}
    return out


def score_ids(ranked: list[str], gt: set[str], mapping: dict[str, set[str]]) -> tuple[float, float, float, int]:
    """P/R/J and hit count of a ranked list of canonical ids against CI ground-truth ids.

    Recall's denominator is all of `gt`, including ids with no graph node. Precision
    counts predicted ids that some GT id binds to. Jaccard is hits / (|R| + |GT| - hits).

    Returns:
        `(precision, recall, jaccard, hits)`.
    """
    pred = set(ranked)
    hits = sum(1 for g in gt if mapping.get(g, set()) & pred)
    hit_nodes = len(pred & {c for g in gt for c in mapping.get(g, set())})
    p = hit_nodes / len(pred) if pred else 0.0
    r = hits / len(gt) if gt else 0.0
    union = len(pred) + len(gt) - hits
    return p, r, (hits / union if union else 0.0), hits


def local_tree_status(repo: str, sha: str, clones_root: Path = Path("data/clones")) -> str:
    """Whether `sha` can be checked out from the local clone without any network.

    Args:
        repo: Repo in `owner/name` form.
        sha: Commit to probe.
        clones_root: Where clones live.

    Returns:
        `"local"` when the commit and every blob of its tree are on disk,
        `"no_commit"` when the commit is absent, `"missing_blobs"` when it is a
        partial clone lacking some of the tree's blobs, `"no_clone"` otherwise.
    """
    clone = clones_root / repo_slug(repo)
    if not clone.exists():
        return "no_clone"
    env = os.environ | {"GIT_NO_LAZY_FETCH": "1"}
    git = ["git", "-C", str(clone)]
    if subprocess.run([*git, "cat-file", "-e", f"{sha}^{{commit}}"], capture_output=True, env=env).returncode:
        return "no_commit"
    tree = subprocess.run([*git, "ls-tree", "-r", "--object-only", sha], capture_output=True, text=True, env=env)
    if tree.returncode:
        return "missing_blobs"
    check = subprocess.run([*git, "cat-file", "--batch-check"], input=tree.stdout, capture_output=True,
                           text=True, env=env)
    return "missing_blobs" if " missing" in check.stdout else "local"


def _git_sha() -> str:
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()


def population() -> tuple[pd.DataFrame, list[tuple[str, int]]]:
    """Strict mini-corpus instances with a graph at the base SHA and a known changeset.

    Returns:
        The instances (columns repo, run_id, pr_number, base_sha, started) and the
        funnel as `(step, count)` pairs.
    """
    out = pd.read_parquet("data/interim/outcomes.parquet")
    inst = pd.read_parquet("data/interim/instances_raw.parquet")
    base = pd.read_parquet("data/interim/base_resolution.parquet")
    chg = pd.read_parquet("data/interim/changesets.parquet")
    funnel: list[tuple[str, int]] = []
    strict = out[out["split"] == "strict"].drop_duplicates("run_id")
    funnel.append(("strict instances, all repos", len(strict)))
    s = strict.merge(inst[["run_id", "repo", "pr_number"]], on="run_id")
    s = s[s["repo"].isin(MINI_CORPUS)]
    funnel.append(("strict instances in the 3 mini-corpus repos", len(s)))
    s = s.merge(base[["run_id", "status", "base_sha"]], on="run_id", how="left")
    s = s[s["status"].notna() & (s["status"] != "no_base") & s["base_sha"].notna()]
    funnel.append(("... with a resolved base SHA (status != no_base)", len(s)))
    funnel.append(("    distinct resolved base SHAs", s["base_sha"].nunique()))
    status = {(r, x): local_tree_status(r, x) for r, x in sorted(set(zip(s["repo"], s["base_sha"])))}
    for st, label in (("local", "fully local (buildable offline)"), ("no_commit", "commit absent from the local clone"),
                      ("missing_blobs", "commit local, blobs missing (partial clone)"), ("no_clone", "no local clone")):
        n = sum(1 for v in status.values() if v == st)
        if n:
            funnel.append((f"    base SHAs: {label}", n))
    s = s[[graph_path(r, x).exists() for r, x in zip(s["repo"], s["base_sha"])]]
    funnel.append(("... with a graph at that SHA in data/graphs/", len(s)))
    known = set(zip(chg["repo"], chg["pr_number"].astype(str)))
    s = s[[(r, str(p)) in known for r, p in zip(s["repo"], s["pr_number"])]]
    funnel.append(("... with a known changeset (population)", len(s)))
    return s.reset_index(drop=True), funnel


def _fmt(df: pd.DataFrame, key: str) -> list[str]:
    hits, act = int(df[f"{key}_hit"].sum()), int(df["n_gt"].sum())
    return [f"{df[f'{key}_p'].mean():.3f}", f"{df[f'{key}_r'].mean():.3f}", f"{df[f'{key}_j'].mean():.3f}",
            f"{100 * hits / act:.2f}% ({hits}/{act})" if act else "n/a",
            f"{statistics.median(df[f'{key}_size']):g}"]


def _table(df: pd.DataFrame, keys: list[tuple[str, str]]) -> list[dict]:
    rows = []
    for label, key in keys:
        hits, act = int(df[f"{key}_hit"].sum()), int(df["n_gt"].sum())
        rows.append({"method": label, "mean_p": round(float(df[f"{key}_p"].mean()), 4),
                     "mean_r": round(float(df[f"{key}_r"].mean()), 4), "mean_j": round(float(df[f"{key}_j"].mean()), 4),
                     "micro_hits": hits, "micro_actual": act, "median_size": float(statistics.median(df[f"{key}_size"]))})
    return rows


#: Filled by `run()`; written by `--json`.
PAYLOAD: dict = {}


def run() -> list[str]:
    """Run the measurement and return the report as markdown lines (and fill `PAYLOAD`)."""
    pop, funnel = population()
    PAYLOAD.clear()
    PAYLOAD.update({"source": "analysis/reachability_mini.py", "generated_at_git_sha": _git_sha(),
                    "funnel": [{"step": a.strip(), "n": int(n)} for a, n in funnel], "n": len(pop),
                    "unbound": None, "test_id_level": [], "file_level": []})
    lines = ["### Population funnel", "", "| step | n |", "|---|---|"]
    lines += [f"| {a} | {n} |" for a, n in funnel]
    if pop.empty:
        lines += ["", "Population is empty: no result tables can be produced (nothing is estimated or filled in)."]
        return lines

    from analysis import rq1_divergence as rq  # heavy load, only when there is something to score

    data = rq.load_data()
    gt_files = rq.ground_truth(data)
    rows_id, rows_file = [], []
    unbound_n = unbound_d = 0
    runs = data.valid_runs.set_index("run_id")
    for inst in pop.itertuples():
        graph = load_graph(graph_path(inst.repo, inst.base_sha))
        gt = set(data.strict_labels[data.strict_labels["run_id"] == inst.run_id]["test_id"])
        changed = data.pr_to_changed[(inst.repo, str(inst.pr_number))]
        mapping = canonical_ids(graph, gt)
        unbound_n += sum(1 for g in gt if not mapping[g])
        unbound_d += len(gt)
        ranked = reachable_tests(graph, changed)
        ids = [t for t, _, _ in ranked]
        rec = {"repo": inst.repo, "run_id": inst.run_id, "n_gt": len(gt)}
        for name, cut in (("R5", 5), ("R10", 10), ("R20", 20), ("Rinf", None)):
            sel = ids[:cut] if cut else ids
            p, r, j, h = score_ids(sel, gt, mapping)
            rec.update({f"{name}_p": p, f"{name}_r": r, f"{name}_j": j, f"{name}_size": len(sel), f"{name}_hit": h})
        rows_id.append(rec)

        GTf = gt_files.get((inst.repo, inst.run_id))
        if not GTf:
            continue
        row = runs.loc[inst.run_id].to_dict() | {"run_id": inst.run_id}
        files: list[str] = []
        for _, _, f in ranked:  # ranked by hop already; first occurrence keeps best hop
            if f and f not in files:
                files.append(f)
        frec = {"repo": inst.repo, "run_id": inst.run_id, "n_gt": len(GTf)}
        F = set(changed)
        h = rq.historical_evidence(data, inst.repo, row)
        for k in K_VALS:
            C_co, C_test = set(), set()
            for f in sorted(F):
                partners = rq.cochange_partners(data, inst.repo, f, row)
                C_co.update(partners[:k])
                C_test.update([b for b in partners if rq.is_conventional_test_file(b)][:k])
            preds = {f"R{k}": set(files[:k]), f"co{k}": C_co - F, f"cot{k}": C_test - F,
                     f"hist{k}": set(h["resolved_path"].value_counts().head(k).index) if len(h) else set()}
            for name, C in preds.items():
                p, r, j = rq.compute_metrics(C, GTf)
                frec.update({f"{name}_p": p, f"{name}_r": r, f"{name}_j": j, f"{name}_size": len(C),
                             f"{name}_hit": len(C & GTf)})
        pr, rr, jr = rq.compute_metrics(set(files), GTf)
        frec.update({"Rinf_p": pr, "Rinf_r": rr, "Rinf_j": jr, "Rinf_size": len(files), "Rinf_hit": len(set(files) & GTf)})
        rows_file.append(frec)

    df_id, df_file = pd.DataFrame(rows_id), pd.DataFrame(rows_file)
    lines += ["", f"Ground-truth test_ids with no graph node: {unbound_n}/{unbound_d}", ""]
    PAYLOAD["unbound"] = {"n": unbound_n, "d": unbound_d}
    for scope, sub in [("overall", df_id)] + [(r, g) for r, g in df_id.groupby("repo")]:
        PAYLOAD["test_id_level"].append({"scope": scope, "n": len(sub), "rows": _table(
            sub, [("reachability k=5", "R5"), ("reachability k=10", "R10"), ("reachability k=20", "R20"),
                  ("reachability unbounded", "Rinf")])})
    for scope, sub in ([("overall", df_file)] + [(r, g) for r, g in df_file.groupby("repo")]) if not df_file.empty else []:
        keys = [(f"{lab} k={k}", f"{p}{k}") for k in K_VALS for lab, p in (
            ("reachability", "R"), ("co-change (all partners)", "co"), ("co-change (test files)", "cot"),
            ("historical frequency", "hist"))] + [("reachability unbounded", "Rinf")]
        PAYLOAD["file_level"].append({"scope": scope, "n": len(sub), "rows": _table(sub, keys)})
    for title, df, keys in (
        ("Test-id level (R vs strict fault-revealing test_ids)", df_id, ["R5", "R10", "R20", "Rinf"]),
    ):
        for scope, sub in [("overall", df)] + [(r, g) for r, g in df.groupby("repo")]:
            lines += [f"### {title}: {scope} (n={len(sub)})", "", "| method | mean P | mean R | mean J | micro recall | median size |", "|---|---|---|---|---|---|"]
            lines += [f"| {k} | " + " | ".join(_fmt(sub, k)) + " |" for k in keys]
            lines.append("")
    if not df_file.empty:
        for scope, sub in [("overall", df_file)] + [(r, g) for r, g in df_file.groupby("repo")]:
            lines += [f"### File level: {scope} (n={len(sub)})", "", "| method | mean P | mean R | mean J | micro recall | median size |", "|---|---|---|---|---|---|"]
            for k in K_VALS:
                for label, key in (("reachability", f"R{k}"), ("co-change (all partners)", f"co{k}"),
                                   ("co-change (test files)", f"cot{k}"), ("historical frequency", f"hist{k}")):
                    lines.append(f"| {label} k={k} | " + " | ".join(_fmt(sub, key)) + " |")
            lines.append("| reachability unbounded | " + " | ".join(_fmt(sub, "Rinf")) + " |")
            lines.append("")
    return lines


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path, help="also write the result as JSON here")
    args = ap.parse_args()
    print(f"analysis/reachability_mini.py @ {_git_sha()}")
    print("\n".join(run()))
    if args.json:
        args.json.write_text(json.dumps(PAYLOAD, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
