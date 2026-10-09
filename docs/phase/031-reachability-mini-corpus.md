# 031 — Graph reachability vs real failures on the mini-corpus

**Script**: `analysis/reachability_mini.py` · **git sha**: `cd19f68` (working tree, uncommitted) · **Date**: 2026-10-09
**Test**: `tests/graph/test_reachability_mini.py` (7 tests, hand-computed against `tests/fixtures/graph/minirepo`).
**Scope**: course result only (D-48). Not in `make tables`, `paper/generated/`, `release/` or the paper. `BR_OFFLINE=1`, no LLM, no new dependency. The reachability rule is copied from `src/agents/codebase.py`, not imported (D-55); it omits inherits/extends/implements as specified.

## Result

**No result tables: the population is empty.** The three mini-corpus repos have strict instances, but none has a graph at its base SHA in `data/graphs/`.

| Step | n |
|---|---|
| strict instances, all repos | 762 |
| strict instances in the 3 mini-corpus repos | 79 (fla 64, saiku 14, Stirling 1) |
| ... with a resolved base SHA (`base_resolution.status != no_base`) | 36 (fla 22, saiku 14, Stirling 0) |
|     distinct resolved base SHAs | 36 |
| ... with a graph at that SHA in `data/graphs/` | **0** |
| ... with a known changeset (population) | **0** |
| GT test_ids with no graph node | n/d = 0/0 (no instances) |

The 5 graphs on disk are at SHAs that `base_resolution` lists for 7 runs (2 Stirling, 5 fla), and none of those 7 runs has any row in `outcomes.parquet`, so they are not labelled instances.

## What would make it run

Build the 36 missing graphs (22 fla, 14 saiku) with `build_graph_at` from the local clones (no network). That writes into `data/graphs/` and was not done: the task fixed the population as "has a graph in `data/graphs/`". Decision for Deepanshu.

## Method (implemented, unexercised on real data)

- R = graph test nodes carrying a `test_id` that reach any changed file node along calls/imports/imports_from/uses/method/tests/tests_by_convention/tests_by_layout, plus `contains` followed symbol to file; ranked by hop then `test_id`.
- GT test_ids bind to graph ids by the exact then lossy (D-25) tiers of `bind_test_ids`; recall's denominator is all GT ids, unbound ones included and counted as n/d.
- Test-id level: R at k=5/10/20 and unbounded. File level (the unit `rq1_divergence` predicts): R's test files, trailing co-change (all partners and test files) and historical frequency at k=5/10/20, on the same instances. The co-change "fires" condition of `evaluate_k` is not applied.
