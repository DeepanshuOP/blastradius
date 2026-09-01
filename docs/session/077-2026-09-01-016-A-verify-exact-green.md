# Session 077

**Date:** 2026-09-01  
**Task ID:** 016-A  
**Slug:** verify-exact-green  

## Task Statement
[CLI-1] — PHASE SPEC 016-A: Verify exact_green. Report base-log usability.
- Phase 1: Verify code path assigning `exact_green` and evaluate derivation against Invariant 6 and ROADMAP §21.3.
- Phase 2: Sample 20 `exact_green` instances across >=8 repos (including all 5 Python repos), fetch logs (foreground, <=60 requests cap), parse, and report retrievable/clean/no-test fractions.
- Phase 3: Extrapolate `NO_TEST_OUTPUT` rate to all 4,245 `exact_green` instances, measure dependency of 778 strict instances on `exact_green`, and state safety verdict.
- Phase 4: Conduct 410 census on 2,371 newly resolved base runs (>90 days old from today) per language.
- Non-goals: No resolution re-runs, no parquet modifications, no parser changes, no daemon restarts, no subagents, no commits.

## Commands Run
1. `uname -s && pwd && uv run python --version` (Linux, /home/shree/blastradius, Python 3.11.15)
2. `view_file docs/AGENT_RULES.md`
3. `view_file docs/HANDOFF.md`
4. `view_file docs/session/INDEX.md`
5. `uv run --env-file .env pytest` (baseline verification: 381 passed in 60.81s)
6. `grep_search exact_green` across codebase
7. `view_file src/label/base_resolve.py`
8. `view_file analysis/resolve_bases.py`
9. `view_file src/label/fault_revealing.py`
10. `view_file analysis/fetch_base_logs.py`
11. `view_file analysis/parse_base_logs.py`
12. `uv run python /tmp/inspect_data.py` (exact_green breakdown across 4,245 instances and 60 repos)
13. `uv run python /tmp/inspect_repos.py` (Python vs Java repo inventory: 5 Python repos, 55 Java repos)
14. `uv run python /tmp/select_20_instances.py` (sample 20 instances across 17 repos, 8 Python + 12 Java)
15. `uv run python /tmp/print_sample_details.py` (sample instance details and timestamps)
16. `uv run --env-file .env python /tmp/sample_exact_green.py` (foreground fetch & parse: 40 requests total, 13/20 retrievable, 6/13 clean, 7/13 no-test-output, 0/13 test failure)
17. `uv run python /tmp/inspect_sample_deep.py` (inspect ages and 410 causes)
18. `uv run python /tmp/check_778_strict.py` (compute strict split dependency: 679/778 instances [87.28%], 3,816/4,194 labels [90.99%] on exact_green)
19. `uv run python /tmp/phase4_census.py` (410 census across 2,371 newly resolved: 778/2,371 [32.81%] >90d; Java 763/2,160 [35.32%], Python 15/211 [7.11%])
20. `uv run python /tmp/calculate_ci.py` (Wilson 95% CI: [29.14%, 76.79%]; extrapolated NO_TEST_OUTPUT: 1,237 to 3,260 instances across all 4,245)

## Raw Output Summary
- **Phase 1 Verdict**: `exact_green` is assigned solely from the GitHub Actions metadata `conclusion == "success"` in `src/label/base_resolve.py` (`resolve_base_run()`) and `analysis/resolve_bases.py` (`run()`), without fetching or parsing any base logs.
- **Phase 2 Sampling (20 runs, 17 repos, 40 HTTP requests)**:
  - 2a. Base logs retrievable: **13 / 20** (65.0%)
  - 2b. Of retrievable: genuinely green with tests observed: **6 / 13** (46.15%)
  - 2c. Of retrievable: `NO_TEST_OUTPUT` (success but zero tests run): **7 / 13** (53.85%)
  - Of retrievable: `TEST_FAILURE`: **0 / 13** (0.0%)
- **Phase 3 778 Impact**:
  - Extrapolation: 1,237 to 3,260 `exact_green` instances ran zero tests (Wilson 95% CI: [29.1%, 76.8%], sample $n=13$).
  - Strict dependency: 679 of 778 strict instances (87.28%) and 3,816 of 4,194 strict labels (90.99%) depend on `exact_green`.
  - Verdict: 778 strict figure is **PROVISIONAL AND UNSAFE** pending full base-log parsing.
- **Phase 4 410 Census (2,371 newly resolved base runs relative to 2026-09-01)**:
  - Total >90 days: **778 / 2,371** (32.81%)
  - Java >90 days: **763 / 2,160** (35.32%)
  - Python >90 days: **15 / 211** (7.11%)
- **Hypothesis Verdicts**:
  - H1 (`exact_green` from conclusion alone -> false positive risk): CONFIRMED.
  - H2 (Large share of base logs 410): CONFIRMED (35.0% sample, 32.81% census).
  - H3 (Python 410 rate > Java): REFUTED (Python 7.11% vs Java 35.32%).
  - H4 (Some `exact_green` parse to `TEST_FAILURE`): REFUTED (0/13 observed).
  - H5 (Strict split overwhelmingly dominated by unverified `exact_green`): CONFIRMED (87.28% instances, 90.99% labels).

## Files Changed
- `docs/phase/016A-REPORT.md` (new deliverable)
- `docs/session/077-2026-09-01-016-A-verify-exact-green.md` (this report)
- `docs/session/INDEX.md` (updated)
- `docs/HANDOFF.md` (updated)

## Non-Goals Honoured
- No re-run of resolution sweep.
- No modifications to parsers, `docs/SCHEMAS.md`, fixtures, or parquet files.
- No dependencies added.
- Harvester daemon unmolested.
- No background tasks or subagents used.
- No git commits performed.
