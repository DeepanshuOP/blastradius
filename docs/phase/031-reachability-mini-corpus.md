# 031 — Graph reachability vs real failures on the mini-corpus

**Script**: `analysis/reachability_mini.py` · **git sha**: `926bbb4` + this commit · **Date**: 2026-10-09
**Test**: `tests/graph/test_reachability_mini.py` (7 tests, hand-computed against `tests/fixtures/graph/minirepo`).
**Scope**: course result only (D-48). Not in `make tables`, `paper/generated/`, `release/` or the paper. `BR_OFFLINE=1`, no LLM, no new dependency. The reachability rule is copied from `src/agents/codebase.py`, not imported (D-55); it omits inherits/extends/implements as specified.

## Result

**No result tables: the population is still empty (n = 0).** Nothing below is estimated or padded.

| Step | n |
|---|---|
| strict instances, all repos | 762 |
| strict instances in the 3 mini-corpus repos | 79 (fla 64, saiku 14, Stirling 1) |
| ... with a resolved base SHA (`base_resolution.status != no_base`) | 36 (fla 22, saiku 14, Stirling 0) |
|     distinct resolved base SHAs | 36 |
|     base SHAs: commit absent from the local clone | 22 (all fla) |
|     base SHAs: commit local, blobs missing (partial clone) | 14 (all saiku) |
| ... with a graph at that SHA in `data/graphs/` | **0** |
| ... with a known changeset (population) | **0** |
| GT test_ids with no graph node | n/d = 0/0 (no instances) |

The 5 graphs on disk are at SHAs that `base_resolution` lists for 7 runs (2 Stirling, 5 fla), and none of those 7 runs has any row in `outcomes.parquet`, so they are not labelled instances.

## Build attempt (2026-10-09)

All 36 missing graphs were attempted with `src.graph.build.build_graph_at` from `data/clones/`, offline, `GIT_NO_LAZY_FETCH=1`. **0 built, 36 skipped**:

- `fla-org/flash-linear-attention` (22): `git cat-file -e <sha>^{commit}` fails, the base commits are not in the local clone (2,119 commits, newest 2026-08-29).
- `spiculedata/saiku` (14): the commits are local, but the clone is a `blob:none` partial clone; `git worktree add` stops with `fatal: could not fetch <blob> from promisor remote`.

The funnel rows for these two causes are computed by the script itself (`local_tree_status`), so the counts regenerate. Making the result run needs a network fetch: `git fetch origin <sha>` for the 22 fla SHAs and a blob backfill for saiku (`git -C data/clones/spiculedata__saiku fetch origin --refetch` or a full clone), then rerun. That was out of scope for an offline session.

Export: `demo-web/public/data/reachability.json` (funnel, `n`, empty tables), via `BR_OFFLINE=1 uv run python -m analysis.reachability_mini --json demo-web/public/data/reachability.json`.

## Method (implemented, unexercised on real data)

- R = graph test nodes carrying a `test_id` that reach any changed file node along calls/imports/imports_from/uses/method/tests/tests_by_convention/tests_by_layout, plus `contains` followed symbol to file; ranked by hop then `test_id`.
- GT test_ids bind to graph ids by the exact then lossy (D-25) tiers of `bind_test_ids`; recall's denominator is all GT ids, unbound ones included and counted as n/d.
- Test-id level: R at k=5/10/20 and unbounded. File level (the unit `rq1_divergence` predicts): R's test files, trailing co-change (all partners and test files) and historical frequency at k=5/10/20, on the same instances. The co-change "fires" condition of `evaluate_k` is not applied.
