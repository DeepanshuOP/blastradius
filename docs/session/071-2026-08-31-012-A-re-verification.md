# Session 071

**Date:** 2026-08-31
**Task ID:** 012-A
**Slug:** re-verification

## Task Statement
Re-verify 011-A: paste raw fractions from the 011-A sampled parquet, quantify
cap impact, audit schema divergences against SCHEMAS.md, audit capture_branch_runs
dead code, and restate the frontier_truncated overflow rule as text only. Undo
the uncommitted working-tree change to resolve_bases.py.

## Commands Run

1. `uname -s && pwd && uv run python --version`
2. `git log --oneline -20`
3. `git status -- analysis/resolve_bases.py && git diff HEAD -- analysis/resolve_bases.py | head -30`
4. `git restore analysis/resolve_bases.py`
5. `git diff HEAD -- analysis/resolve_bases.py`  (confirmed empty)
6. `git show 7320545e46c01e6a5904236fa6d7edbb049aa722 -- analysis/resolve_bases.py | grep -n "pages_fetched"`
7. `uv run python -c "..." ` — load base_resolution_new_sampled.parquet, print shape/status counts/distance distribution
8. `uv run python -c "..." ` — load base_resolution_new.parquet + instances_raw.parquet, print group count, size stats
9. `uv run python -c "..." ` — compute max group size and cap-hit counts for sampled 100 groups
10. `uv run python -c "..." ` — full column/dtype audit of all three parquets
11. `uv run python -c "..." ` — compare instances_raw.parquet columns against SCHEMAS.md column list
12. `grep -n "def capture_branch_runs\|def " src/harvest/daemon.py | head -40`
13. `view_file daemon.py lines 1038–1210`
14. `grep -rn "capture_branch_runs" src/ analysis/ tests/`
15. `view_file daemon.py lines 1680–1755` (run() caller)
16. `grep -n "run_stage5\|stage5\|branch_runs" src/harvest/daemon.py | head -30`
17. `git show ec8cf70^..ec8cf70 -- src/harvest/daemon.py`  (date-slice diff)
18. `git log --oneline -- src/harvest/daemon.py | head -5`

## Raw Output

Session guard:
  Linux / /home/shree/blastradius / Python 3.11.15

base_resolution_new_sampled.parquet:
  Shape: (2204, 6)
  status counts: no_base=2118, exact=65, ancestor=21
  distance counts: 0.0→65, 1.0→12, 2.0→4, 5.0→2, 7.0→2, 10.0→1

Group cap analysis:
  Max group size: 800
  Groups > 3400 (34-page cap): 0
  Groups > 1000 (10-page cap): 0
  Groups > 100 (multi-page):   3

instances_raw.parquet divergences vs SCHEMAS.md:
  base_run_id: float64 (schema says int64) — TYPE MISMATCH
  base_run_distance: ABSENT (schema requires int32) — MISSING
  17 schema columns missing; 5 extra columns not in schema

capture_branch_runs:
  LIVE — called from run() at daemon.py:1699
  Enabled when stage in ("5", "all")
  Contains date-slice subdivision with no depth bound (committed ec8cf70)

Uncommitted change undone:
  pages_fetched >= 10 → restored to pages_fetched >= 34 (HEAD)

## Files Changed

- `docs/phase/012A-REPORT.md` (created, ~200 lines)
- `analysis/resolve_bases.py` (restored to HEAD; net diff = 0)
- `docs/session/071-2026-08-31-012-A-re-verification.md` (this file)
- `docs/session/INDEX.md` (appended)

## Test Count
- Before: N/A (re-verification only, no code changes)
- After:  N/A

## Non-goals Honoured
- No code changes committed.
- No subagents spawned.
- No background tasks.
- No heredocs used.
- No new features added.
- No network requests issued (all data read from local parquet/git).
- did not touch tests/fixtures/.
- did not touch analysis/rq1_divergence.py.

## Contradictions Found
1. 011-A report said "10 pages" but committed code had `pages_fetched >= 34`.
   These are inconsistent; 10 × 100 = 1,000 but 34 × 100 = 3,400.
2. An uncommitted modification had changed the code to 10 post-commit.
   This change was unasked and has been reverted.
3. 011-A said the mapping "perfectly fits" into instances.parquet; in fact
   base_run_id is float64 (schema: int64) and base_run_distance is absent
   from instances_raw.parquet entirely.
4. The cap did not actually fire on any of the 100 sampled groups
   (max group = 800 items, which needs only 8 pages).

## Open Questions
1. Should capture_branch_runs() be removed? (Phase 4c — awaiting approval)
2. Should frontier_truncated be implemented? (Phase 5 — awaiting approval)
3. The schema divergences (base_run_id type, missing columns) are escalations.
   Operator decision required before any repair attempt.
