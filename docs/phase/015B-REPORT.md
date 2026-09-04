# Phase 015-B Report: Schema Conformance Ruling, Count Reconciliation, and Negatives Architecture

## 1. Recategorised UNDECLARED List with Reasons

Per Architect Ruling (Phase 015-B), extra columns present on disk that carry data required by the pipeline or decision records are NOT defects. The following 9 columns have been recategorised from `DEFECT` to `UNDECLARED` (documented, retained on disk, never deleted):

1. `base_ref` (`instances.parquet`): Required by base resolution; present in the query CLI-1 executes today.
2. `job_ids` (`instances.parquet`): Matrix-leg evidence; required to verify decision D-12.
3. `job_conclusions` (`instances.parquet`): Matrix-leg evidence; required to verify decision D-12.
4. `created_at` (`instances.parquet`): Run provenance.
5. `n_commits_a` (`cochange.parquet`): The provenance of support and lift; without them the co-change comparison arm of RQ1 is uncheckable.
6. `n_commits_b` (`cochange.parquet`): The provenance of support and lift; without them the co-change comparison arm of RQ1 is uncheckable.
7. `n_commits_total` (`cochange.parquet`): The provenance of support and lift; without them the co-change comparison arm of RQ1 is uncheckable.
8. `window_days` (`cochange.parquet`): The provenance of support and lift; without them the co-change comparison arm of RQ1 is uncheckable.
9. `conf_b_to_a` (`cochange.parquet`): Directional pair; retain both directions.

---

## 2. Reconciled Column Counts Per Table

Across all in-scope tables, every column evaluated satisfies the exact identity:
$$\text{MATCH} + \text{DEFECT} + \text{NOT MEASURED} + \text{RENAMED} + \text{RESTRUCTURED} + \text{UNDECLARED} = \text{Declared} + \text{Extra}$$

### Summary Table
| Table | Declared Columns | Extra on Disk | Total Evaluated | MATCH | DEFECT | NOT MEASURED | RENAMED | RESTRUCTURED | UNDECLARED | Total Discrepancies (Table Rows) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `instances.parquet` | 34 | 5 | 39 | 15 | 11 | 8 | 1 | 0 | 4 | 24 |
| `outcomes.parquet` | 18 | 3 | 21 | 1 | 10 | 5 | 0 | 5 | 0 | 20 |
| `cochange.parquet` | 8 | 8 | 16 | 4 | 0 | 0 | 5 | 2 | 5 | 12 |
| **TOTAL** | **60** | **16** | **76** | **20** | **21** | **13** | **6** | **7** | **9** | **56** |

### Per-Table Detailed Arithmetic

1. **`instances.parquet`** (34 declared, 22 on disk):
   - **Declared Columns (34)** = 15 MATCH + 11 DEFECT + 8 NOT MEASURED.
   - **Extra on Disk (5)** = 1 RENAMED (`repo_full`) + 4 UNDECLARED (`base_ref`, `created_at`, `job_ids`, `job_conclusions`).
   - **Total Evaluated** = 34 + 5 = **39**.
   - **Categories**: MATCH (15) + DEFECT (11) + NOT MEASURED (8) + RENAMED (1) + RESTRUCTURED (0) + UNDECLARED (4) = **39**.
   - **Divergence Table Rows** = 19 declared divergent + 5 extra on disk = **24**.

2. **`outcomes.parquet`** (18 declared, 4 on disk):
   - **Declared Columns (18)** = 1 MATCH (`test_id`) + 9 DEFECT + 5 NOT MEASURED + 3 RESTRUCTURED (`instance_id`, `split_strict`, `split_permissive`).
   - **Extra on Disk (3)** = 1 DEFECT (`__index_level_0__`) + 2 RESTRUCTURED (`run_id`, `split`).
   - **Total Evaluated** = 18 + 3 = **21**.
   - **Categories**: MATCH (1) + DEFECT (10) + NOT MEASURED (5) + RENAMED (0) + RESTRUCTURED (5) + UNDECLARED (0) = **21**.
   - **Divergence Table Rows** = 17 declared divergent + 3 extra on disk = **20**.

3. **`cochange.parquet`** (8 declared, 12 on disk):
   - **Declared Columns (8)** = 4 MATCH (`file_a`, `file_b`, `support`, `lift`) + 3 RENAMED (`repo`, `window_end`, `n_cochanges`) + 1 RESTRUCTURED (`confidence`).
   - **Extra on Disk (8)** = 2 RENAMED (`repo_full`, `as_of`) + 1 RESTRUCTURED (`conf_a_to_b`) + 5 UNDECLARED (`conf_b_to_a`, `n_commits_a`, `n_commits_b`, `n_commits_total`, `window_days`).
   - **Total Evaluated** = 8 + 8 = **16**.
   - **Categories**: MATCH (4) + DEFECT (0) + NOT MEASURED (0) + RENAMED (5) + RESTRUCTURED (2) + UNDECLARED (5) = **16**.
   - **Divergence Table Rows** = 4 declared divergent + 8 extra on disk = **12**.

---

## 3. The `instance_id` Correction

In Phase 014-B, `instance_id` was erroneously listed as `DEFECT` (absent) while `run_id` was separately listed as `RESTRUCTURED` (foreign key used instead). This was a single architectural fact counted twice under conflicting categories.

**Correction**: `instance_id` is deterministically defined in `docs/SCHEMAS.md` as:
$$\text{instance\_id} = \text{sha256}(\text{repo} \mid \text{head\_sha} \mid \text{run\_id})$$
It is strictly derivable from `run_id` when joined with instance metadata. It is now recorded **once** under category **`RESTRUCTURED`** with its derivation, reducing declared `DEFECT` count in `outcomes.parquet` from 10 to 9.

---

## 4. `candidates.parquet` Schema Specification (Benchmark Addition)

Per D-43, `candidates.parquet` provides the universe of observed candidate tests per repository and trailing window. It is recorded in `docs/SCHEMA_CONFORMANCE.md` §4 as an ADDITION (not an edit to frozen `SCHEMAS.md`).

- **Grain**: One row per `(repo, window_end, test_id)`.
- **Window Definition**: Trailing observation window (30-day or 90-day window preceding an instance's `run_started_at`), bounding active candidate tests for that repository at that point in time.

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

## 5. Empirical Class Imbalance: Query, Range, and Median — **WITHDRAWN (Phase 016-B)**

> **WITHDRAWN.** This section's "candidate pool" was built by grouping `test_id` in
> `data/interim/parsed_outcomes.parquet` by `repo`. That table contains **zero rows** with
> `status` outside `('fail', 'error')` — only failing runs were ever parsed for test-level
> outcomes (see Phase 016-B §1a/§1c: 0 of 6,014 distinct `test_id`s in the candidate universe
> were ever observed via a non-failing status). The "candidate pool" and the "positive pool"
> are therefore drawn from the identical population by construction. Dividing one by the
> other, as §5.1–5.2 below do, does not measure class imbalance — it measures how many
> distinct tests failed at least once per repo versus how many failed in one run, both counted
> off the same failure-only slice. The resulting **1:35 / 1:82.5 / 1:1,707 figures are not a
> measurement of class imbalance and must not be cited as one.** True class imbalance requires
> a denominator of tests actually *executed* (pass or fail), which this project has not yet
> captured for the vast majority of runs — see Phase 016-B §3 (10 of 117,923 successful runs
> have any job log on disk). The query, range, and median below are retained unmodified as a
> record of what was computed and why it is invalid; nothing in this section has been deleted.
> *(Correction: Distinct test_ids figure 6,014 is superseded by **5,985** post-fix per Phase 023 consolidation).*

This is the first measurement and reporting of class imbalance in the BlastRadius project.
**(Superseded by the WITHDRAWN notice above — this was not, in fact, a measurement of class
imbalance.)**

### 5.1 Measurement Query
```python
import pyarrow.parquet as pq
import pandas as pd

# Load empirical observations
df_parsed = pq.read_table('data/interim/parsed_outcomes.parquet').to_pandas()
df_outcomes = pq.read_table('data/interim/outcomes.parquet').to_pandas()
df_instances = pq.read_table('data/interim/instances_raw.parquet').to_pandas()

# Candidate test pool: distinct tests observed per repo in observation window
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

### 5.2 Measurement Results
- **Repository Candidate Test Suites (42 repos)**: Range **[1, 1,707]** distinct tests, Median **25.0**, Mean **143.19**. Top suites: `apache/beam` (1,707), `sirixdb/sirix` (1,309), `castorini/anserini` (560), `floci-io/floci` (449), `Stirling-Tools/Stirling-PDF` (307).
- **Positives per Instance**:
  - Raw parsed outcomes (1,863 runs): Range **[1, 1,245]**, Median **1.0**, Mean **8.29**.
  - Filtered benchmark outcomes (656 runs): Range **[1, 520]**, Median **1.0**, Mean **4.75**.
- **Empirical Class Imbalance (1 positive per N candidates)**:
  - Across all parsed runs (1,863 runs): Range **[1:1.0, 1:1,707.0]**, Median **1:82.5** (Mean: **1:449.6**).
  - Across filtered benchmark runs (656 runs): Range **[1:1.0, 1:1,707.0]**, Median **1:35.0** (Mean: **1:175.7**).

---

## 6. Verbatim Datasheet Limitation — **REWRITTEN (Phase 016-B)**

> **Superseded.** The paragraph originally here (see git history / Phase 015-B) quoted "1
> positive per 35 to 1,707 candidate tests" as an empirical class imbalance figure. Per the
> Phase 016-B §1–2 finding, that figure is circular: the "candidate tests" universe and the
> "positive" universe were both drawn exclusively from `parsed_outcomes.parquet`, which
> contains only rows with `status in ('fail', 'error')` — no passing test was ever parsed or
> counted. The replacement paragraph below is the honest entry.

The following limitation paragraph replaces it verbatim in the BR-Bench datasheet and paper limitations:

> *"BR-Bench ships exclusively positive fault-revealing test execution outcomes (`status in ('fail', 'error')`), derived from parsing only the workflow runs that concluded with a failure or produced failing/erroring test jobs. The observed test universe (`candidates.parquet`, per repository and trailing observation window) is therefore built from the same failure-only slice as the positive labels: it contains no test ever observed passing, because passing-run logs were never parsed for test-level outcomes (of 117,923 successful workflow runs in the harvested frame, job logs survive on disk for 10). Consequently, true class imbalance — the ratio of failing to passing test executions per candidate pool — is UNMEASURED by this project. ROADMAP §9.3 anticipates an expected imbalance on the order of 1:200–2,000 based on prior RTS literature, but BlastRadius has not parsed a corpus of passing runs sufficient to confirm, refute, or refine that figure, and no number purporting to state the imbalance should be read from this dataset as measured. Negative examples remain derivable rather than materialised: consumers reconstruct negative instances by taking the set difference between the full observed candidate test set in `candidates.parquet` and the positive failure set in `outcomes.parquet`, but should not assume the resulting ratio reflects the true skew of executed-test outcomes without independently sampling and parsing passing-run logs."*

---

## 7. Decision Record D-43

**Decision Number**: **D-43** (appended to `docs/DECISIONS.md`; D-21 remains RESERVED).

### D-43: Derivable negatives and candidate test universes
**Context**: Reconciling binary classification framing and negative test outcome generation with severe empirical class imbalance.
**Decision**: Negative examples are derivable, not materialised. BR-Bench ships positives plus candidates.parquet giving the full observed test set per repo per trailing window. Consumers derive negatives at any ratio. Rationale: materialising at the observed imbalance produces tens of millions of rows for 8,980 positives, and a frozen sampling ratio is a weaker artifact than the universe it was sampled from.
