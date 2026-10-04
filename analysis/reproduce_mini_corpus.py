"""End-to-end reproduction of the graph layer on the 3-repo mini-corpus.

Scope: graph layer only. Per D-48 nothing produced here reaches `make tables`,
`release/` or the paper, and the binding figure printed here is the graph-side
`graph_node_binding_rate` diagnostic, which is NOT Gate 1.5 and is not
comparable with D-47's figure (different denominators).

Why this is a bounded reproduction
----------------------------------
`data/graphs/` holds 427 graphs. Rebuilding all of them cold cannot fit a
15-minute budget on a laptop, so this reproduces the full chain -- build, bind,
query -- over `--shas-per-repo` SHAs per repo (default 3, so 9 graphs) and
prints the subset size with every figure. It writes to a fresh `--out-dir` by
default so the builds are genuinely cold rather than reusing
`data/graphs/`; pass `--out-dir data/graphs` to measure the warm path instead.

Repos and clone directories come from `docs/MINI_CORPUS.md`.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import random
import sys
import time

import duckdb

from src.graph.build import build_graph_at, graph_path, load_graph
from src.graph.query import GraphQuery, QueryCache, feature_vector
from src.graph.test_nodes import bind_test_ids

__all__ = ["MINI_CORPUS", "BUDGET_SECONDS", "resolved_base_shas", "verdict"]

#: (repo, clone dir) exactly as docs/MINI_CORPUS.md selects them.
MINI_CORPUS: tuple[tuple[str, str], ...] = (
    ("fla-org/flash-linear-attention", "data/clones/fla-org__flash-linear-attention"),
    ("Stirling-Tools/Stirling-PDF", "data/clones/Stirling-Tools__Stirling-PDF"),
    ("spiculedata/saiku", "data/clones/spiculedata__saiku"),
)

#: ROADMAP T5.6b target for the whole reproduction.
BUDGET_SECONDS = 15 * 60


def resolved_base_shas(repo: str, limit: int) -> list[str]:
    """Return the most recent resolved base SHAs for a repo, deterministically.

    `docs/MINI_CORPUS.md` defines a resolved base as a `base_resolution.parquet`
    row whose status is one of `exact`, `exact_green`, `ancestor` with a non-null
    `base_sha`. Ordering is by `run_id` descending so the selection is stable
    across runs and independent of row order on disk.

    Args:
        repo: Repo in `owner/name` form.
        limit: How many SHAs to return.

    Returns:
        Up to `limit` distinct base SHAs, newest run first.
    """
    rows = duckdb.sql(
        f"""
        select base_sha, max(run_id) as newest
        from read_parquet('data/interim/base_resolution.parquet')
        where repo = '{repo}'
          and status in ('exact', 'exact_green', 'ancestor')
          and base_sha is not null
        group by base_sha
        order by newest desc, base_sha
        limit {int(limit)}
        """
    ).fetchall()
    return [r[0] for r in rows]


def observed_test_ids(repo: str) -> list[str]:
    """Distinct `test_id`s observed in CI outcomes for a repo.

    Args:
        repo: Repo in `owner/name` form.

    Returns:
        The de-duplicated observed ids, the denominator of the binding figure.
    """
    rows = duckdb.sql(
        f"""
        select distinct test_id
        from read_parquet('data/interim/parsed_outcomes.parquet')
        where repo = '{repo}' and test_id is not null
        """
    ).fetchall()
    return [r[0] for r in rows]


def verdict(built: int, total_seconds: float) -> tuple[int, str]:
    """Decide the reproduction's exit status.

    A run that built nothing must not report the budget as met: with the clones
    absent every repo is skipped, wall time is a fraction of a second, and a
    naive `total < BUDGET_SECONDS` check would print MET having reproduced
    nothing at all. That is the one failure mode a reproduction target cannot
    be allowed to have, so it is a hard error rather than a skip.

    Exceeding the budget is reported but does not fail: the figure is a
    measurement on whatever laptop is running, and ROADMAP T5.6b's 15 minutes
    is a target for ours, not a property of the code.

    Args:
        built: Number of graphs actually built.
        total_seconds: Wall time of the whole reproduction.

    Returns:
        `(exit_code, verdict_text)`.
    """
    if built == 0:
        return 1, "NO GRAPHS BUILT — nothing was reproduced, so the budget is not a pass"
    if total_seconds < BUDGET_SECONDS:
        return 0, "MET"
    return 0, "NOT MET (over budget; reported, not fatal — see verdict())"


def main() -> int:
    """Run the bounded reproduction and report timings against the budget.

    Returns:
        Process exit code; see :func:`verdict`.
    """
    parser = argparse.ArgumentParser(description="Reproduce the graph mini-corpus")
    parser.add_argument("--shas-per-repo", type=int, default=3)
    parser.add_argument("--instances", type=int, default=50, help="timed query instances per graph")
    parser.add_argument("--out-dir", type=Path, default=Path("data/graphs_reproduce"))
    parser.add_argument("--keep", action="store_true", help="keep --out-dir afterwards")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.out_dir.exists() and args.out_dir != Path("data/graphs"):
        shutil.rmtree(args.out_dir)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    print(f"Mini-corpus reproduction: {len(MINI_CORPUS)} repos x "
          f"{args.shas_per_repo} SHAs, budget {BUDGET_SECONDS}s (T5.6b)")
    print(f"out-dir: {args.out_dir} (cold builds unless this is data/graphs)\n")

    totals = {"built": 0, "build_s": 0.0, "bind_s": 0.0, "query_s": 0.0}

    for repo, clone_dir in MINI_CORPUS:
        if not Path(clone_dir).exists():
            print(f"[{repo}] SKIPPED: clone absent at {clone_dir}")
            continue

        shas = resolved_base_shas(repo, args.shas_per_repo)
        print(f"[{repo}] {len(shas)} SHAs")

        graphs = []
        for sha in shas:
            t0 = time.perf_counter()
            build_graph_at(repo, sha, clone_dir=clone_dir, out_dir=args.out_dir)
            elapsed = time.perf_counter() - t0
            totals["build_s"] += elapsed
            totals["built"] += 1
            graph = load_graph(graph_path(repo, sha, out_dir=args.out_dir))
            graphs.append((sha, graph))
            print(f"   build {sha[:10]}  {graph.number_of_nodes():>7,} nodes  "
                  f"{graph.number_of_edges():>7,} edges  {elapsed:7.2f}s")

        if not graphs:
            continue

        observed = observed_test_ids(repo)
        t0 = time.perf_counter()
        reports = [bind_test_ids(g, observed, repo=repo) for _, g in graphs]
        totals["bind_s"] += time.perf_counter() - t0
        best = max(reports, key=lambda r: r.n_bound)
        print(f"   bind  graph_node_binding_rate (best of {len(reports)} graphs): "
              f"{best.n_bound}/{best.n_observed}   "
              f"[graph-side diagnostic, NOT Gate 1.5, D-48]")

        sha, graph = graphs[-1]
        test_nodes = [n for n, d in graph.nodes(data=True) if d.get("node_type") == "test"]
        other = [n for n in graph.nodes if n not in set(test_nodes)]
        if test_nodes and other:
            rng = random.Random(args.seed)
            cache = QueryCache()
            GraphQuery(graph, repo=repo, sha=sha, cache=cache)
            n = min(args.instances, len(test_nodes))
            # The first instance at a SHA pays for the cold cache; ROADMAP
            # 19.4's <=100 ms budget is the warm per-instance figure. Averaging
            # the two together hides both, so they are timed separately.
            per_instance_ms: list[float] = []
            t_all = time.perf_counter()
            for i in range(n):
                t0 = time.perf_counter()
                feature_vector(
                    graph,
                    test_nodes[i % len(test_nodes)],
                    rng.sample(other, min(5, len(other))),
                    cache=cache,
                )
                per_instance_ms.append((time.perf_counter() - t0) * 1000)
            totals["query_s"] += time.perf_counter() - t_all
            cold = per_instance_ms[0]
            warm = sorted(per_instance_ms[1:]) or [cold]
            median = warm[len(warm) // 2]
            budget = "MET" if median <= 100 else "NOT MET"
            print(f"   query {n} instances   cold first {cold:8.3f} ms"
                  f"   warm median {median:7.3f} ms   (19.4 <=100 ms: {budget})\n")
        else:
            print("   query SKIPPED: no test nodes or no other nodes\n")

    total = time.perf_counter() - started
    code, text = verdict(totals["built"], total)
    print("-" * 68)
    print(f"graphs built      : {totals['built']}")
    print(f"build time        : {totals['build_s']:8.2f}s")
    print(f"bind time         : {totals['bind_s']:8.2f}s")
    print(f"query time        : {totals['query_s']:8.2f}s")
    print(f"TOTAL wall time   : {total:8.2f}s  of {BUDGET_SECONDS}s budget")
    print(f"T5.6b target      : {text}")

    if not args.keep and args.out_dir != Path("data/graphs"):
        shutil.rmtree(args.out_dir, ignore_errors=True)
        print(f"removed {args.out_dir} (pass --keep to retain)")

    return code


if __name__ == "__main__":
    sys.exit(main())
