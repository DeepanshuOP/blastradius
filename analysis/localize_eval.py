"""RQ5 addendum (exploratory, not pre-registered): graph-guided localisation L6 against L1 and L4.

    uv run --extra graph --extra ml python -m analysis.localize_eval      (offline, no model; `make localize-eval`)

On every BR-Seeded task of the standard and hard variants: is the ground-truth function at rank 1 / in the top 3, and
its reciprocal rank, for

    L1  BM25 over every function                    (= arm R1's retrieval; `repair.select_chunks("R1")`)
    L4  BM25 over the functions the diff touches     (= arm R2's retrieval; `repair.select_chunks("R2")`, E1 tie-break)
    L6  graph-guided: RRF over diff / calls hops from the failing tests / failing tests reaching / traceback frames
        (`src.agents.localize`)

L1 and L4 are recomputed with the same calls `analysis.rq5_retrieval` makes, so they equal the rows of
`rq5_retrieval.md`. Paired comparison: exact two-sided McNemar on hit@3 and on hit@1, L6 against L4, per variant,
Holm-adjusted over the four tests. The code graph is built once per repository at the task's base commit (the seeded
edits change operators and add no-op statements, never a call), so a task's `calls` edges are the base's.
Writes `paper/generated/rq5_graph_localize.md`. NOT part of `make tables`; L6 losing is a reportable result.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

import analysis.rq4_repair as rq4
from analysis import paper_md
from analysis.rq5_retrieval import full_ranking
from src.agents import localize as L
from src.agents import repair
from src.agents.repair import FailureReport
from src.eval.seeded.build import SEEDED, source_files
from src.eval.seeded.validate import head_state
from src.features.online import diff_stats

RESULT_MD = "rq5_graph_localize.md"
MODES = ("L1", "L4", "L6")
LABELS = {"L1": "L1 BM25, whole repo (= R1)", "L4": "L4 BM25, functions touched by the diff (= R2)",
          "L6": "L6 graph-guided RRF (diff, calls hops, reach, frames)"}
NOTE = ("**Exploratory, not pre-registered; produced by `make localize-eval`, not `make tables`.** The pre-registered "
        "E3 analysis is unchanged and the E3 arms are not re-run. No LLM is involved.")


def graph_view(repo_name: str, sha: str, clone: Path, out: Path) -> dict:
    """The code graph of a seeded repository at `sha`, in the Live Lab's view shape."""
    from src.graph.build import build_graph_at, load_graph
    from src.lab import graphview

    st = build_graph_at(f"seeded/{repo_name}", sha, clone_dir=clone, out_dir=out)
    return graphview.to_cytoscape(load_graph(st.graph_path))


def rankings(task: dict, repo: Path, srcs: list[str], view: dict) -> tuple[dict[str, list[tuple[str, str]]], dict]:
    """Full rankings per mode as `(file, qualname)`, and the L6 evidence of the ground truth."""
    changed, n_lines = diff_stats(task["pr_diff"])
    report = FailureReport(failing=task["failing_tests"], pr_diff=task["pr_diff"], triage="mine",
                           changed_files=list(changed))
    tie = rq4.e1_priority(repo, changed, n_lines)
    out: dict[str, list[tuple[str, str]]] = {}
    with full_ranking():
        out["L1"] = [(c.file, c.qualname) for c in repair.select_chunks("R1", repo, srcs, report)]
        out["L4"] = [(c.file, c.qualname) for c in repair.select_chunks("R2", repo, srcs, report, tie)]
    chunks = repair.index_functions(repo, srcs)
    ranked = L.localize(repo, srcs, task["failing_tests"], task["pr_diff"], view, chunks)
    cov = L.graph_coverage(view, chunks, task["failing_tests"])
    out["L6"] = [c.key for c in ranked]
    gt = next((c for c in ranked if c.key == (task["gt_file"], task["gt_function"])), None)
    ev = {"signals": sorted(gt.ranks) if gt else [], "hops": gt.hops if gt else None, "reach": gt.reach if gt else 0,
          "n_ranked": len(ranked), "mapped": cov["mapped_tests"] > 0, "reachable": cov["reachable_functions"] > 0}
    return out, ev


def score(task: dict, ranks: dict[str, list[tuple[str, str]]], ev: dict) -> dict:
    gt = (task["gt_file"], task["gt_function"])
    rec: dict = {"task_id": task["task_id"], "repo": task["repo"], "operator": task["operator"], "gt_evidence": ev}
    for m, ranked in ranks.items():
        pos = ranked.index(gt) + 1 if gt in ranked else 0
        rec[m] = {"hit1": pos == 1, "hit3": 1 <= pos <= 3, "rr": 1.0 / pos if pos else 0.0, "pos": pos}
    return rec


def evaluate(variant: str, pins: dict, graphs: dict, gdir: Path) -> list[dict]:
    recs = []
    for t in rq4.load_variant(variant):
        repo = SEEDED / "repos" / t["repo"]
        if not repo.exists():
            raise SystemExit(f"{repo} is missing: run `make seeded` first")
        key = (t["repo"], t["base_sha"])
        if key not in graphs:
            graphs[key] = graph_view(t["repo"], t["base_sha"], repo, gdir)
        with head_state(repo, t["pr_diff"]):
            srcs = source_files(repo, {"src_dirs": pins[t["repo"]]["src_dirs"]})
            ranks, ev = rankings(t, repo, srcs, graphs[key])
            recs.append(score(t, ranks, ev))
    return recs


def mode_table(recs: list[dict]) -> str:
    n = len(recs)
    rows = [[LABELS[m], paper_md.rate(sum(r[m]["hit1"] for r in recs), n), paper_md.rate(sum(r[m]["hit3"] for r in recs), n),
             f"{sum(r[m]['rr'] for r in recs) / n:.3f}" if n else "n/a"] for m in MODES]
    return paper_md.table(["mode", "hit@1", "hit@3", "MRR"], rows)


def signal_table(recs: list[dict]) -> str:
    """On how many tasks each L6 signal scored the ground-truth function."""
    n = len(recs)
    rows = [[s, paper_md.rate(sum(1 for r in recs if s in r["gt_evidence"]["signals"]), n)] for s in L.SIGNALS]
    hops = [r["gt_evidence"]["hops"] for r in recs if r["gt_evidence"]["hops"] is not None]
    rows.append(["a failing test is a node of the graph", paper_md.rate(sum(1 for r in recs if r["gt_evidence"]["mapped"]), n)])
    rows.append(["its `calls` closure reaches any source function",
                 paper_md.rate(sum(1 for r in recs if r["gt_evidence"]["reachable"]), n)])
    rows.append(["calls path to the ground truth found (hops: min / median / max)",
                 f"{len(hops)}/{n}" + (f" ({min(hops)} / {sorted(hops)[len(hops) // 2]} / {max(hops)})" if hops else "")])
    return paper_md.table(["ground truth scored by signal", "tasks"], rows)


def paired(by_variant: dict[str, list[dict]]) -> str:
    from src.eval import stats as S

    tests = []
    for v, recs in by_variant.items():
        for k in ("hit3", "hit1"):
            a = sum(1 for r in recs if r["L6"][k] and not r["L4"][k])
            b = sum(1 for r in recs if r["L4"][k] and not r["L6"][k])
            tests.append((v, k, a, b, rq4.mcnemar_twosided(a, b)))
    adj = S.holm_adjust([t[-1] for t in tests])
    rows = [[v, f"L6 vs L4 ({k.replace('hit', 'hit@')})", a, b, f"{p:.4g}", f"{h:.4g}"]
            for (v, k, a, b, p), h in zip(tests, adj)]
    return paper_md.table(["variant", "comparison", "L6 only", "L4 only", "p (exact McNemar, two-sided)",
                           f"Holm-adjusted (family of {len(tests)})"], rows)


def reading(v: str, recs: list[dict]) -> str:
    n = len(recs)
    h = {m: sum(r[m]["hit3"] for r in recs) for m in MODES}
    h1 = {m: sum(r[m]["hit1"] for r in recs) for m in MODES}
    cmp3 = "above" if h["L6"] > h["L4"] else "below" if h["L6"] < h["L4"] else "equal to"
    cmp1 = "above" if h1["L6"] > h1["L4"] else "below" if h1["L6"] < h1["L4"] else "equal to"
    return (f"{v}: hit@3 is {h['L1']}/{n} (L1), {h['L4']}/{n} (L4) and {h['L6']}/{n} (L6); L6 is {cmp3} L4 on hit@3 "
            f"and {cmp1} it on hit@1 ({h1['L6']}/{n} vs {h1['L4']}/{n}).")


def main(argv: list[str] | None = None) -> int:
    os.environ.setdefault("BR_OFFLINE", "1")
    pins = json.loads(rq4.REPOS_JSON.read_text())
    graphs: dict = {}
    by_variant: dict[str, list[dict]] = {}
    with tempfile.TemporaryDirectory(prefix="br-l6-") as gdir:
        for v in ("standard", "hard"):
            try:
                by_variant[v] = evaluate(v, pins, graphs, Path(gdir))
            except FileNotFoundError:
                continue
    text = paper_md.header("RQ5 addendum (exploratory): graph-guided localisation (L6) against L1 and L4",
                           "analysis/localize_eval.py", NOTE)
    text += ("\n## Method\n\n"
             "L6 ranks every function of the source files by reciprocal rank fusion (k = 60) of four rankings: the "
             "function overlaps a changed line; minimum hop distance from a failing test's node over `calls` edges "
             f"(caller to callee, at most {L.MAX_HOPS} hops); the number of failing tests whose `calls` closure reaches "
             "it; the function holds a frame of a failing test's traceback (deepest first). Ties at equal rank share it; "
             "the fused order is broken by file path, then line. L1 and L4 are the E3 retrievers (`repair.select_chunks`), "
             "with the cut at three chunks lifted to read the rank of the ground truth. The graph is built once per "
             "repository at the base commit with `src.graph.build.build_graph_at`.\n")
    for v, recs in by_variant.items():
        text += f"\n## {v.capitalize()} variant (n = {len(recs)})\n\n" + mode_table(recs) + "\n\n" + signal_table(recs) + "\n"
    if by_variant:
        text += "\n## Paired tests\n\n\"L6 only\" = L6 has the ground truth at the cut and L4 does not.\n\n" + paired(by_variant) + "\n"
        text += "\n## Reading\n\n" + "\n\n".join(reading(v, r) for v, r in by_variant.items()) + "\n"
        allr = [r for recs in by_variant.values() for r in recs]
        text += ("\nThe graph signals rarely fire: over both variants a failing test is a graph node on "
                 f"{sum(r['gt_evidence']['mapped'] for r in allr)}/{len(allr)} tasks, but its `calls` closure reaches a "
                 f"source function on only {sum(r['gt_evidence']['reachable'] for r in allr)}/{len(allr)} (the static "
                 "graph resolves few calls made through objects), so L6 is mostly the diff and frame signals fused. On the "
                 "hard variant the diff signal ties the seeded function with the decoy edits, and the fusion does not "
                 "separate them as L4's BM25 does.\n")
    paper_md.write(RESULT_MD, text)
    print(f"wrote paper/generated/{RESULT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
