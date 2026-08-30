# Phase 007-A: Make the dataset regenerable

This session cleaned up the repository root from 50+ ad-hoc throwaway and patch scripts. It promoted the load-bearing scripts necessary for dataset generation and wired them into `make tables`.

## Actions
- Triaged all root scripts. 
- Promoted `resolve_all.py` -> `analysis/resolve_bases.py`
- Promoted `fetch_base_logs2.py` -> `analysis/fetch_base_logs.py`
- Promoted `parse_base_logs.py` -> `analysis/parse_base_logs.py`
- Promoted `migrate_cursor.py` -> `src/harvest/migrations.py`
- Confirmed `run_stage5.py` was a redundant duplicate to `daemon.py` and deleted it.
- Deleted all remaining untracked root scripts (e.g. `fix_*`, `patch_*`).
- Reconciled discrepancies in 006A/006B sizing (the 1,382 count was merely the denominator of instances having both head/base sets).
- Diagnosed the 43.12% flip rate as a bug in `src/label/fault_revealing.py` incorrectly tracking runs by `head_sha` regardless of `workflow_id`, counting linting/documentation failures as flips. Fixed the logic to include `workflow_id`, plunging the flip rate to 0.55% (64 flips) and correctly retaining 186 strict positives.
- Corrected unit boundaries in `analysis/attrition_funnel.py`.
- Added 4 real-data integration tests enforcing invariant 6 in `test_fault_revealing.py`.

## Git operations
The changes were committed and pushed as requested, ensuring zero failures in the test suite and a clean root directory.
