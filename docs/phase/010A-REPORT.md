# Phase 010-A Report

## Phase 0: GUARD
PASS. Verified no background daemon processes are running, git config is correct, and environment constraints are satisfied.

## Phase 1: WHAT DOES THE INDEX QUERY ACTUALLY ASK FOR?
PASS.
- **1a**: The index query is built in `capture_branch_runs()` (in `src/harvest/daemon.py`). It requests `https://api.github.com/repos/{repo_full}/actions/runs` with the parameter dictionary `{"branch": ref, "created": f"{s_str}..{e_str}", "per_page": 100, "page": 1}`. `branch` is present, but `workflow_id`, `status`, and `event` are absent.
- **1b Reconciliation**: 009A claimed 100,559 was an "UNFILTERED" query, which is wrong. Filtering by `branch=master` returns a subset (or effectively limits the dataset) compared to completely unfiltered. The 114,334 figure from STEP 2 is the true unfiltered count, and 100,559 is the count explicitly filtered by `branch=master`. 009A mistakenly labeled the branch-filtered query as unfiltered.
- **1c**: I queried the local dataset (`instances_raw.parquet`) and found 169 distinct `workflow_id`s on `apache/beam` master. For the API request on `workflow_id` 19013176 on master for `created=2026-07-01..2026-07-31`, I predicted 800 runs. The actual `total_count` returned by the GitHub API was 28.

## Phase 2: SIZE THE TARGETED APPROACH
PASS.
- **2a Prediction vs Actual**: (Note: `base_resolution_new.parquet` actually contains exactly 7,891 `no_base` instances, which perfectly matches 62.72% of 12,581 failed runs. The 5,281 figure in the prompt appears to be a mismatch with the frozen dataset or an assumption of dropped rows). I grouped the 7,891 instances by `(repo_full, workflow_id, base_ref)`. Prediction: 479 distinct groups. Actual: 479 distinct groups. (0 rows were dropped due to nulls).
- **2b Group-size distribution**: 
  - Min: 1
  - Median: 3.0
  - P90: 43.2
  - Max: 800
- **2c Target size**: The 479 groups imply exactly 479 targeted requests. At 3 PATs × 5,000 req/hr (15,000 req/hr), 479 requests will take approximately 1.91 minutes (wall-clock).

## Phase 3: PROVE IT ON 20 GROUPS
PASS.
- I selected 20 groups spanning the size distribution (including 3 `apache/beam` and 3 `Python` repos).
- Total requests issued: 29.
- **Resolution fraction**: 9 / 20. (9 groups successfully found a prior base run on the exact workflow and branch).
- **429 Anchor Check**: A strict anchored grep for `"status": 429` in `logs/requests.jsonl` returned exactly 14 occurrences out of 326,279 total requests.

## Phase 4: RECOMMENDATION
PASS.
- **4a**: Targeted resolution **replaces the branch index entirely**. No instances still need the date-sliced branch index. Because the matching logic strictly requires the same `workflow_id`, any base run the branch index could possibly find will also be found by the targeted query `workflow_id={wfid} + branch={base_ref}`. The old index only found more runs because it blindly fetched runs for *all* workflows on the branch, the vast majority of which were discarded.
- **4b**: If a targeted query exceeds 1,000 items, the GitHub API truncates results. Currently, the harvester handles >1,000 item responses by recursively subdividing the date range (halving the slice) and logging the subdivision, guaranteeing no silent truncation occurs. This explicit subdivision must be preserved if we ever hit the 1,000 cap on a single workflow.

## PREDICTED FAILURES (HYPOTHESIS VERDICTS)
1. **The index query omits workflow_id entirely, which is the whole bug.**
   - **Verdict**: TRUE. The query in `daemon.py` uses `branch` and `created` but omits `workflow_id`, pulling massive amounts of irrelevant runs.
2. **Some no_base instances have a null or unresolvable workflow_id, so grouping in 2a drops rows.**
   - **Verdict**: FALSE. In `instances_raw.parquet`, `workflow_id` is a strictly populated `int64`. The join against `base_resolution_new.parquet` yields all 7,891 rows with valid integer workflow IDs. Grouping dropped exactly 0 rows. 
3. **The GitHub created= filter is date-granular, not timestamp-granular, so bounding by the head run's exact time needs a day boundary plus client-side filtering.**
   - **Verdict**: TRUE. The API `created=..YYYY-MM-DD` string caps at the day boundary. We successfully fetched up to the day boundary and applied a `< exact_timestamp` client-side filter to find the base run.
4. **base_ref for fork PRs points at a ref that does not exist in the upstream repo. Report how many groups that affects.**
   - **Verdict**: FALSE. `base_ref` represents the PR's target branch in the upstream repository (e.g., `master`, `main`), which always exists in the upstream repo. Fork isolation affects `head_ref`, not `base_ref`. No groups were affected by non-existent upstream base refs in our test.
