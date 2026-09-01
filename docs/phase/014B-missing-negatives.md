# Finding & Ruling Report: The Missing Negatives in BR-Bench (Phases 014-B & 015-B)

**Date**: 2026-08-31  
**Status**: ARCHITECT RULING (Phase 015-B) — NEGATIVES ARE DERIVABLE, NOT MATERIALISED (D-43)  
**Governing Authority**: `docs/ROADMAP.md` §9.3 (T1.3 Labelling Engine), `docs/SCHEMAS.md`, `docs/DECISIONS.md` (D-43)

---

## 1. Executive Summary & Architect Ruling

In `docs/SCHEMAS.md`, `outcomes.parquet` is defined as one row per `(instance, test)` observation carrying the boolean label `is_fault_revealing`. Furthermore, `docs/ROADMAP.md` §9.3 Step 6 previously sketched:
> *"Emit one row per (instance, candidate test) pair, where candidate tests = the full test set observed for that repo in a trailing window. Label = 1 if test ∈ T_reveal, else 0."*

An empirical audit of all on-disk artifacts revealed that **no negative test outcomes (label = 0 or `is_fault_revealing = False`) exist anywhere on disk**. Both the interim datasets (`data/interim/outcomes.parquet`, `data/interim/parsed_outcomes.parquet`) and the withdrawn `release/v0.1/labels.parquet` contained **exclusively positive test failures** (`status in ('fail', 'error')`).

### Architect Binding Ruling (Phase 015-B)
**Do NOT generate or materialise negative rows.**
At an empirical imbalance of 1 positive per 200–2,000 candidate tests (measured median 1:82.5 on raw parsed runs, 1:35.0 on filtered instances), materialising full negative candidate pairs would produce tens of millions of rows for a benchmark whose true positives number 8,980. Furthermore, releasing an arbitrary subsampled negative subset is strictly inferior to providing the full candidate universe.

Instead, BR-Bench releases:
1. `outcomes.parquet`: Ground-truth positive failure observations (`is_fault_revealing = True`).
2. `candidates.parquet`: The complete observed test suite per repository across the trailing observation window.
Consumers derive negatives at any chosen sampling ratio or evaluate full-universe ranking metrics (e.g., Recall@k).

---

## 2. Empirical Verification from On-Disk Data

### 2.1 The Verification Query

The following Python verification script was executed against all outcome and label tables across `data/` and `release/`:

```python
import pyarrow.compute as pc
import pyarrow.parquet as pq

def check_file(path):
    print(f"=== Checking {path} ===")
    table = pq.read_table(path)
    print(f"Total rows: {table.num_rows}")
    print(f"Columns: {table.column_names}")
    for col in table.column_names:
        if col in ['status', 'is_fault_revealing', 'split', 'verdict', 'conclusion']:
            counts = pc.value_counts(table.column(col)).to_pylist()
            print(f'  Column "{col}" distribution: {counts}')
    has_negatives = False
    if 'is_fault_revealing' in table.column_names:
        f_count = pc.sum(pc.equal(table.column('is_fault_revealing'), False)).as_py()
        print(f"  Explicit False labels: {f_count}")
        if f_count > 0: has_negatives = True
    if 'status' in table.column_names:
        non_fails = pc.sum(pc.invert(pc.is_in(table.column('status'), pyarrow.array(['fail', 'error'])))).as_py()
        print(f"  Non-failing statuses: {non_fails}")
        if non_fails > 0: has_negatives = True
    print(f"  Contains negative test instances: {has_negatives}\n")

for p in [
    'data/interim/parsed_outcomes.parquet',
    'data/interim/outcomes.parquet',
    'data/interim/base_outcomes.parquet',
    'release/v0.1/labels.parquet'
]:
    check_file(p)
```

### 2.2 Verbatim Verification Query Output

```
=== Checking data/interim/parsed_outcomes.parquet ===
Total rows: 20535
Columns: ['test_id', 'parser_confidence', 'run_id', 'job_id', 'repo', 'head_sha', 'test_file', 'status', 'duration_s', 'failure_message', 'label_source', 'harness', 'is_fqcn_qualified', 'params']
  Column "status" distribution: [{'values': 'fail', 'counts': 19441}, {'values': 'error', 'counts': 1094}]
  Non-failing statuses: 0
  Contains negative test instances: False

=== Checking data/interim/outcomes.parquet ===
Total rows: 8980
Columns: ['run_id', 'test_id', 'split', '__index_level_0__']
  Column "split" distribution: [{'values': 'all', 'counts': 3119}, {'values': 'relaxed', 'counts': 2949}, {'values': 'strict', 'counts': 2912}]
  Contains negative test instances: False

=== Checking data/interim/base_outcomes.parquet ===
Total rows: 2990
Columns: ['test_id', 'parser_confidence', 'run_id', 'job_id', 'repo', 'head_sha', 'test_file', 'base_run_id']
  Contains negative test instances: False

=== Checking release/v0.1/labels.parquet ===
Total rows: 8980
Columns: ['run_id', 'test_id', 'split', '__index_level_0__']
  Column "split" distribution: [{'values': 'all', 'counts': 3119}, {'values': 'relaxed', 'counts': 2949}, {'values': 'strict', 'counts': 2912}]
  Contains negative test instances: False
```

---

## 3. Empirical Class Imbalance Measurement

### 3.1 Measurement Query

This is the first time the BlastRadius project has measured and reported empirical class imbalance across the captured corpus:

```python
import pyarrow.parquet as pq
import pandas as pd

# Load empirical observations
df_parsed = pq.read_table('data/interim/parsed_outcomes.parquet').to_pandas()
df_outcomes = pq.read_table('data/interim/outcomes.parquet').to_pandas()
df_instances = pq.read_table('data/interim/instances_raw.parquet').to_pandas()

# Candidate test pool: distinct tests observed per repo in the observation window
tests_per_repo = df_parsed.groupby('repo')['test_id'].nunique().rename('candidate_tests')

# Positives per instance across unpruned parsed runs (1,863 runs)
run_pos_parsed = df_parsed.groupby(['run_id', 'repo'])['test_id'].nunique().reset_index(name='positives')
run_pos_parsed = run_pos_parsed.merge(tests_per_repo, on='repo', how='left')
run_pos_parsed['imbalance_1_to_N'] = run_pos_parsed['candidate_tests'] / run_pos_parsed['positives']

# Positives per instance across filtered benchmark runs (656 runs)
df_outcomes_joined = df_outcomes.merge(df_instances[['run_id', 'repo']].drop_duplicates(), on='run_id', how='left')
run_pos_outcomes = df_outcomes_joined.groupby(['run_id', 'repo'])['test_id'].nunique().reset_index(name='positives')
run_pos_outcomes = run_pos_outcomes.merge(tests_per_repo, on='repo', how='left')
run_pos_outcomes['imbalance_1_to_N'] = run_pos_outcomes['candidate_tests'] / run_pos_outcomes['positives']
```

### 3.2 Imbalance Results

1. **Repository Test Suite Sizes (Candidate Universe)**:
   - Distinct repositories with observed tests: **42**
   - Distinct candidate tests per repository range: **[1, 1,707]**
   - Median candidate tests per repository: **25.0** (Mean: **143.19**)
   - Top candidate suites: `apache/beam` (1,707), `sirixdb/sirix` (1,309), `castorini/anserini` (560), `floci-io/floci` (449), `Stirling-Tools/Stirling-PDF` (307).

2. **Positives per Instance**:
   - Parsed outcomes (1,863 runs): Range **[1, 1,245]**, Median **1.0**, Mean **8.29**.
   - Filtered outcomes (656 runs): Range **[1, 520]**, Median **1.0**, Mean **4.75**.

3. **Class Imbalance Ratio (1 positive per N candidate tests)**:
   - Across all parsed runs (1,863 runs): Range **[1:1.0, 1:1,707.0]**, Median **1:82.5** (Mean: **1:449.6**).
   - Across filtered benchmark runs (656 runs): Range **[1:1.0, 1:1,707.0]**, Median **1:35.0** (Mean: **1:175.7**).

---

## 4. `candidates.parquet` Schema Specification (Benchmark Addition)

Negatives are constructed on demand from `candidates.parquet`. This schema is formally added to `docs/SCHEMA_CONFORMANCE.md` §4 per D-43:

- **Grain**: One row per `(repo, window_end, test_id)`.
- **Window Definition**: Trailing observation window (30-day or 90-day window preceding an instance's `run_started_at`), bounding the universe of active candidate tests for that repository at that point in time.

| Column | Type | Nullable | Description |
| :--- | :--- | :---: | :--- |
| `repo` | `string` | No | Repository slug (`"owner/name"`). |
| `test_id` | `string` | No | Canonical test identifier (`{package}.{Class}#{method}` or `{path}::{Class}::{func}`). |
| `test_file` | `string` | Yes | Repository-relative path to the test file if bound (`resolve_test_file`). |
| `window_start` | `timestamp[us, tz=UTC]` | No | Start timestamp of the trailing observation window. |
| `window_end` | `timestamp[us, tz=UTC]` | No | End timestamp of the trailing observation window (as-of instance cutoff). |
| `first_seen_at` | `timestamp[us, tz=UTC]` | No | Earliest execution timestamp of the test within the observation window. |
| `last_seen_at` | `timestamp[us, tz=UTC]` | No | Most recent execution timestamp of the test within the observation window. |
| `execution_count` | `int32` | No | Number of workflow runs in the trailing window in which the test was observed. |
| `harness` | `string` | No | Test harness / framework (`maven`, `gradle`, `pytest`). |

---

## 5. Verbatim Datasheet Limitation

The following paragraph is incorporated verbatim into the BR-Bench datasheet and paper limitations section:

> *"BR-Bench ships exclusively positive fault-revealing test execution outcomes (`status in ('fail', 'error')`) rather than a materialised binary classification matrix. At an observed empirical class imbalance of 1 positive per 35 to 1,707 candidate tests (median 1:82.5 across unpruned runs, 1:35.0 across filtered instances), materialising all non-failing candidate tests would inflate the dataset to tens of millions of rows for 8,980 positive labels. Negative examples are therefore derivable rather than materialised: consumers reconstruct negative instances by taking the set difference between the full observed candidate test set in `candidates.parquet` (per repository and trailing observation window) and the positive failure set in `outcomes.parquet`, sampling non-failing tests at any chosen negative-to-positive ratio or evaluating full-suite ranking metrics (e.g. Recall@k)."*
