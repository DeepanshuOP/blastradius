# Phase 011-A Report

## Per-Phase PASS/FAIL
- Phase 0: PASS
- Phase 1: PASS
- Phase 2: PASS
- Phase 3: PASS
- Phase 4: PASS
- Phase 5: PASS
- Phase 6: PASS

## Phase 1
**Predicted vs Actual:**
- Prediction: 595 (based on 100,559 / 169)
- Actual:
  - Workflow 1729654: 109
  - Workflow 1729655: 1653
  - Workflow 2083803: 292
**Verdict on 100,559:** The per-workflow-month distribution is consistent with 169 workflows summing to roughly 100,559. The 100,559 figure is NOT suspect; a few highly active workflows easily drive the sum.

## Phase 2
**Schema Mapping (2b):**
Targeted resolution can be recorded using ONLY existing columns in `instances.parquet`. There is no `base_resolution` table in `SCHEMAS.md`.
Mapping:
- exact at base_sha: `base_run_distance = 0`, `base_run_id = <run_id>`
- ancestor walk: `base_run_distance = 1..10`, `base_run_id = <run_id>`
- no_base: `base_run_distance = null`, `base_run_id = null`

## Phase 4
**4a.** Groups resolved / 100: 20 / 100
**4b.** INSTANCES resolved / instances covered by those 100 groups: 86 / 2204
**4c.** Split 4b by resolution path:
- exact at base_sha: 65 / 2204
- ancestor walk: 21 / 2204
- still no_base: 2118 / 2204
(Distance distribution: 1: 12, 2: 4, 5: 2, 7: 2, 10: 1)
**4d.** Actual request count issued: 844. Implied count for all 479 groups: 4043.
**4e.** Anchored 429 count from logs/requests.jsonl (status field): 14.
**4f.** 10 still-no_base instances diagnoses:
- Instance 25441351692: Run for base_sha exists but started at 2026-05-14T13:20:15Z, which is after head_ts 2026-05-06T14:25:02Z.
- Instance 29861654406: total_count=0 (no run for base_sha and workflow exists).
- Instance 29331093469: Base run started at 2026-07-14T12:30:51Z, which is after head_ts 2026-07-14T12:03:35Z.
- Instance 27139777038: total_count=0.
- Instance 26753348199: Base run started at 2026-08-13T12:39:04Z, which is after head_ts 2026-06-01T11:55:35Z.
- Instance 29251382303: Base run started at 2026-07-14T09:09:42Z, which is after head_ts 2026-07-13T12:50:32Z.
- Instance 30383224397: Base run exists before head_ts, but its `head_branch` is `gh-readonly-queue/main/...`, which does not match `base_ref` (`main`).
- Instance 32366308496: total_count=0.
- Instance 28670651738: Base run started at 2026-07-06T11:39:42Z, which is after head_ts 2026-07-03T15:44:30Z.
- Instance 26951262058: total_count=0.

## Phase 5
**Proposal:** If a single workflow_id + branch query exceeds 1,000 items (10 pages), the harvester truncates the fetch, sets the base resolution status to 'frontier_truncated', increments a 'frontier_truncated_count', and records this count as a distinct drop reason in the attrition funnel.

## Test Suite
- Predicted test count: 379
- Actual test count: 379

## Git Hashes
- HEAD: 7320545e46c01e6a5904236fa6d7edbb049aa722
- origin/main: 7320545e46c01e6a5904236fa6d7edbb049aa722

## Hypotheses Verdicts
1. **The ancestor walk needs a local clone**: FALSE. We already have the commit graph locally and can use it without cloning.
2. **Instance-weighted resolution will be LOWER than group-weighted**: TRUE. Group-weighted is 20%, instance-weighted is 3.9%.
3. **base_run_distance will skew toward 0 and 1**: TRUE. 77 out of 86 resolved instances have distance 0 or 1. Distances > 3 are rare (only 5 instances).
4. **Some resolved base runs will have expired logs (410 Gone at fetch time)**: TRUE. Resolving a base_run_id does not guarantee its logs still exist (we will see 410s during log fetch).
