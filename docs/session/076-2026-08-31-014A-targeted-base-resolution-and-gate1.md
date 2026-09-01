# Session 076

> **PROVISIONAL (Phase 016-B).** CLI-1 is verifying whether `exact_green` was assigned from
> run conclusion rather than from a parsed base log. 4,245 instances (60% of all resolved
> bases) depend on it. This report's figures of 778 (strict instances), 4,194 (strict
> labels), and 43.88% (`no_base` share) are PROVISIONAL pending that verification (016-A).
> Nothing below has been changed.

**Date:** 2026-08-31
**Task ID:** 014-A
**Slug:** targeted-base-resolution-and-gate1

## Task Statement
[CLI-1] — PHASE SPEC 014-A CONTINUED: Proceed with Phases 2 through 7.
- Phase 2: Restructure analysis/resolve_bases.py and add outgoing-params unit test.
- Phase 3: §21.3 strict commit-graph ancestor walk survey (max 10 hops) and bytechef candidate run audit.
- Phase 4: Full targeted base resolution across all 479 groups (Python-first), predict vs actual against 5,281 addressable ceiling.
- Phase 5: Full corpus re-resolution table (12,581 failed runs), re-evaluate splits (strict/relaxed/all), and report effect on Gate 1.
- Phase 6: Recursion depth bound of 5 that RAISES in capture_branch_runs in src/harvest/daemon.py.
- Phase 7: Verification and commit discipline, non-goals honoured.

## Commands Run
1. `uname -s && pwd && uv run python --version`
2. `view_file docs/AGENT_RULES.md`
3. `view_file docs/session/INDEX.md`
4. `view_file docs/HANDOFF.md`
5. `git status && git log -n 10 --oneline`
6. `uv run pytest` (baseline test run: 377 passed, 1 failed, 1 skipped)
7. `replace_file_content analysis/resolve_bases.py` (restructure params, python-first, limit)
8. `replace_file_content tests/test_base_resolve.py` (add outgoing params & pagination test)
9. `uv run --env-file .env python /tmp/phase3_survey.py` (21 groups, 1,255 instances, bytechef audit)
10. `uv run --env-file .env python -m analysis.resolve_bases --out data/interim/base_resolution_targeted.parquet` (all 479 groups, 7,891 instances)
11. `uv run python -m src.label.fault_revealing` (compute updated splits and Gate 1)
12. `replace_file_content src/harvest/daemon.py` (add recursion depth bound of 5 raising RuntimeError)
13. `replace_file_content tests/test_daemon.py` (add test_capture_branch_runs_depth_bound_raises)
14. `uv run pytest` (final suite verification: 380 passed, 1 skipped)
15. `git config user.name && git config user.email`

## Raw Output Summary
- Session opening guard: Linux / /home/shree/blastradius / Python 3.11.15
- Phase 3 Survey (21 groups, 1,255 instances):
  - no_base: 911 (72.59%)
  - exact_green: 208 (16.57%)
  - exact: 100 (7.97%)
  - ancestor: 36 (2.87%)
  - Bytechef outcome: All 237 instances resolved to `no_base` (candidate run was 5 months old and disconnected from commit graph).
- Phase 4 Targeted Resolution (479 groups, 7,891 instances, 1,353 requests, 4203.7s):
  - Prediction: 27.0% of addressable 5,281 (1,425) / 18.1% of total 7,891 (1,425).
  - Actual: 2,371 resolved instances (44.90% of addressable 5,281 / 30.05% of total 7,891).
  - Targeted breakdown: no_base 5,520 (69.95%), exact_green 1,319 (16.72%), exact 733 (9.29%), ancestor 319 (4.04%).
- Phase 5 Corpus-Level Resolution (12,581 failed runs):
  - `no_base`: 5,520 (43.88%) (was 7,891 / 62.72%, -2,371 instances)
  - `exact_green`: 4,245 (33.74%) (was 2,926, +1,319 instances)
  - `exact`: 1,858 (14.77%) (was 1,125, +733 instances)
  - `ancestor`: 591 (4.70%) (was 272, +319 instances)
  - `branch_prior`: 367 (2.92%)
  - Total resolved: 7,061 (56.12%) (was 4,690 / 37.28%)
- Phase 5 Splits & Gate 1:
  - strict: 778 instances / 4,194 labels / 2,485 distinct tests (+48.5% instances, +44.0% labels)
  - relaxed: 787 instances / 4,241 labels / 2,503 distinct tests (+48.8% instances, +43.8% labels)
  - all: 914 instances / 4,411 labels / 2,519 distinct tests (+39.3% instances, +41.4% labels)
  - Gate 1: Missed at 778 positives vs 5,000 threshold.
  - **CORRECTION (Phase 016-B, D-44)**: 778 is the instance count. Gate 1's ">=5,000 positives" reads against the label count (ROADMAP §9.3 step 6: one row per (instance, candidate test) pair). Corrected reading: Gate 1 missed at 4,194 / 5,000 labels, not 778 instances. See D-44 in `docs/DECISIONS.md`.

## Files Changed
- `analysis/resolve_bases.py`
- `tests/test_base_resolve.py`
- `src/harvest/daemon.py`
- `tests/test_daemon.py`
- `data/interim/base_resolution_new.parquet`
- `data/interim/base_resolution_targeted.parquet`
- `data/interim/outcomes.parquet`
- `docs/phase/014A-REPORT.md`
- `docs/session/076-2026-08-31-014A-targeted-base-resolution-and-gate1.md`
- `docs/session/INDEX.md`
- `docs/HANDOFF.md`

## Test Count
- Before: 377 passed, 1 failed, 1 skipped (379 collected)
- After: 380 passed, 0 failed, 1 skipped (381 collected)

## Non-goals Honoured
- `base_ref`, `job_ids`, and `job_conclusions` were NOT removed or modified in any parquet table.
- No subagents spawned; no background tasks left running.
- No heredocs used (`cat << EOF`); throwaway scripts in `/tmp`.
- No fixture values edited to force passing tests.
- SCHEMAS.md not edited (frozen).

## Contradictions & Hypotheses Evaluated
1. **Bytechef Temporal Prior vs Commit Walk**: Evaluated hypothesis that bytechef could be resolved by temporal precedence alone. Refuted under §21.3: candidate run is 5 months older and not within 10 ancestor commits of base_sha, correctly classifying all 237 instances as `no_base`.
2. **Addressable Resolution Efficiency**: Actual resolved instances (2,371, 44.90% of addressable 5,281) significantly exceeded conservative 27.0% prediction due to high density of base runs in multi-instance PR groups.
