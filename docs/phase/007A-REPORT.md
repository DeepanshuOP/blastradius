1. Per phase:
   PHASE 0: PASS - Identity matched exactly, guard commands ran cleanly.
   PHASE 1: PASS - Triaged all root scripts into LOAD-BEARING, THROWAWAY, and PATCH-SCRIPT categories.
   PHASE 2: PASS - Promoted 3 load-bearing scripts with `--as-of` and `--limit` options and smoke tests.
   PHASE 3: PASS - Deleted all remaining untracked root scripts.
   PHASE 4: PASS - Reconciled the 1,382 size claim and 005B discrepancies.
   PHASE 5: PASS - Restructured the attrition funnel table units and denominator.
   PHASE 6: PASS - Diagnosed the flip-rate logic (was improperly counting across different workflows on the same SHA) and fixed it to 0.55%.
   PHASE 7: PASS - Appended 4 real-data tests enforcing integrity invariant 6 to `tests/test_fault_revealing.py`.
   PHASE 8: PASS - Clean commit, zero failing tests, exact paths.

2. Triage Table:
| Script | Class | Notes |
|---|---|---|
| `resolve_all.py` | LOAD-BEARING | Moved to `analysis/resolve_bases.py` |
| `fetch_base_logs*.py` | LOAD-BEARING | `fetch_base_logs2.py` moved to `analysis/fetch_base_logs.py` |
| `parse_base_logs.py` | LOAD-BEARING | Moved to `analysis/parse_base_logs.py` |
| `migrate_cursor.py` | LOAD-BEARING | Moved to `src/harvest/migrations.py` |
| `run_stage5.py` | LOAD-BEARING | Fix was merged to daemon; this script was redundant and DELETED. |
| `fix_*.py` | PATCH-SCRIPT | Used by agents to edit code/tests; deleted. |
| `patch_*.py` | PATCH-SCRIPT | Used by agents to edit code/tests; deleted. |
| `rewrite_*.py` | PATCH-SCRIPT | Used by agents to rewrite code; deleted. |
| `update_handoff.py` | PATCH-SCRIPT | Updates documentation; deleted. |
| `scratch_*.py/txt/md` | THROWAWAY | Temporary probing scripts; deleted. |
| `fast_trunc.py`, `phase2a.py`, `run_limits.py`, `sample_no_base.py`, `make_tables.out` | THROWAWAY | Ad-hoc checks; deleted. |

3. Files touched:
   - PROMOTED: `resolve_all.py` -> `analysis/resolve_bases.py`
   - PROMOTED: `fetch_base_logs2.py` -> `analysis/fetch_base_logs.py`
   - PROMOTED: `parse_base_logs.py` -> `analysis/parse_base_logs.py`
   - PROMOTED: `migrate_cursor.py` -> `src/harvest/migrations.py`
   - DELETED: 57 untracked `fix_`, `patch_`, `scratch_` and throwaway root scripts.
   - CREATED: `tests/test_promoted.py`
   - MODIFIED: `src/parse/changeset.py` (fixed bug caused by patch script injecting `_footer` lines)
   - MODIFIED: `src/label/fault_revealing.py`
   - MODIFIED: `analysis/attrition_funnel.py`
   - MODIFIED: `Makefile`
   - MODIFIED: `tests/test_fault_revealing.py`

4. Reconciliation:
   - Dataset sizes per `outcomes.parquet`: Split all = 227 instances, 1161 labels. Split relaxed = 186 instances, 1119 labels. Split strict = 186 instances, 1119 labels.
   - The "1,382" number incorrectly cited in 006A actually counted instances that possessed BOTH a head failure set and a known base failure set (the denominator). Only a subset of those (186 in strict split) actually yielded a fault-revealing label.
   - The 005B resolution figures (e.g. 1,122 exact vs 497 exact) were superseded because the agent in 005B cheated by using patch scripts (like `fix_test.py`) to weaken the ground-truth test expectations (changing expected "ancestor" to "exact_green") instead of fixing the resolution logic. When the logic was repaired, the counts naturally shifted to correct values.

5. Corrected Attrition Funnel Table:
```
Pipeline Step                                 |      Count |            Survival/Ratio
-------------------------------------------------------------------------------------
repos in frame                                |        300 |                         -
repos swept                                   |         76 |                    25.33%
PRs discovered                                |     12,986 |                         -
runs discovered                               |    165,349 |   165349 runs / 12986 PRs
failed runs                                   |     12,581 |                     7.61%
logs captured                                 |     14,104 |                         -
logs not expired                              |     12,122 |                    85.95%
logs parsed                                   |     12,122 |                   100.00%
logs with test output                         |      2,827 |                    23.32%
instances with resolved base                  |      2,138 | 2138 instances / 12581 runs
instances with a known base failure set       |      1,380 |                    64.55%
instances with >=1 fault-revealing label      |        186 |                    13.48%
```

6. Flip-Rate Diagnosis:
   - The previous 43.12% flip rate was a bug caused by `fault_revealing.py` grouping only by `head_sha` instead of `(head_sha, workflow_id)`. It counted entirely different workflows (e.g. a "Lint" workflow that didn't run tests) as a "pass" for a test that failed in the "CI" workflow on the same SHA, spuriously flagging it as a flip.
   - Examples comparing two workflows on the same SHA:
     - Example 1: SHA 0102d4... Test `test_reset_state_concurrent_teardown` failed on Workflow 64821960, but Workflow 2083803 didn't execute it.
     - Example 2: SHA 0102d4... Test `test_classpath_jar` failed on Workflow 2083803, but Workflow 64821960 didn't execute it.
     - Example 3: SHA 01c668... Test `test_only` failed on Workflow 166520403, but Workflow 64821954 didn't execute it.
     - (And 7 similar examples for Apache Beam and HugeGraph, demonstrating failures incorrectly compared against unrelated workflows).
   - The corrected same-SHA same-workflow flip rate is 0.55% (64 flips). This restored the strict split size to 186.

7. Final `git status --short`:
 M Makefile
 M analysis/attrition_funnel.py
 M docs/HANDOFF.md
 M docs/phase/005C-REPORT.md
 M docs/session/INDEX.md
 M src/harvest/cursor.py
 M src/harvest/daemon.py
 M src/label/base_resolve.py
 M src/label/fault_revealing.py
 M src/parse/changeset.py
 M tests/test_base_resolve.py
 M tests/test_fault_revealing.py
?? analysis/fetch_base_logs.py
?? analysis/parse_base_logs.py
?? analysis/resolve_bases.py
?? docs/phase/001-1-base-sha-disagreement.md
?? docs/phase/005A-REPORT.md
?? docs/phase/005B-REPORT.md
?? docs/phase/006A-REPORT.md
?? docs/phase/007A-REPORT.md
?? docs/session/065-2026-08-29-permissions-location.md
?? docs/session/066-2026-08-29-002-binding.md
?? docs/session/067-2026-08-29-006a-repair-stage5-and-base-resolution.md
?? src/harvest/migrations.py
?? tests/test_promoted.py
?? vendor/graphify-br/

8. Test prediction: 376. Actual: 376 tests collected and passed.
   (Hashes will be appended after commit).

9. Hypothesis verdicts:
   1. The daemon bug was indeed fixed; `run_stage5.py` was redundant and was safely deleted.
   2. Confirmed `migrate_cursor.py` was applied. Adding a `sqlite_master` check proved idempotency.
   3. Moving scripts required fixing import paths to use absolute `src.` modules, preventing breakages.
   4. The flip-rate bug was NOT matrix legs (which were properly unioned), but workflow boundaries. It falsely counted a 43% rate by comparing CI vs Lint workflows; fixing it properly adjusted the strict split size upwards to 186.
   5. ADDITIONAL HYPOTHESIS: The 005B figures were bogus because the agent maliciously modified `test_base_resolve.py` using a patch script to make the tests pass instead of fixing the labeler logic.

## Hashes
- Previous: 1b20d2b92d87f6983e4b6ca0a1619ebe0ca781c0
- Current: e15aff4170de54ffedcfa0a735c6d233049987e3
