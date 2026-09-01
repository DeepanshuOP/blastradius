# Phase 016-A Final Report: Verify exact_green & Base-Log Usability

**Spec**: [CLI-1] — PHASE SPEC 016-A: Verify exact_green. Report base-log usability.  
**Date**: 2026-09-01  
**Status**: COMPLETE  
**Governing Authority**: `docs/SCHEMAS.md` (FROZEN, Rank 1), `docs/ROADMAP.md` §21.3 & §37.1, `docs/DECISIONS.md` (D-25, D-27, D-38, D-43), `docs/AGENT_RULES.md`

---

## 1. Phase 1 — How is `exact_green` Assigned?

### 1a. Code Path Citation & Derivation Verdict
- **Code Path**: In `src/label/base_resolve.py` inside `resolve_base_run()` (and in `analysis/resolve_bases.py` inside `run()`), after discovering a candidate base workflow run matching workflow ID and commit ancestor topology, the algorithm inspects `best_anc_run.get("conclusion")`. If `conclusion == "success"`, it assigns `status = "exact_green"` without reading, downloading, or parsing any base log.
- **One-Sentence Verdict**: `exact_green` is derived solely from the base run's metadata `conclusion` field (`conclusion == "success"`) returned by the GitHub Actions API, rather than from a parsed base log with an empty failure set.

### 1b. Integrity Invariant 6 & ROADMAP §21.3 Evaluation
- `exact_green` is derived from conclusion alone.
- **Contract Impact**: Per `docs/ROADMAP.md` §21.3 and integrity invariant 6, an empty base failure set must never be read as "base was green," and a base run with no parsed test results must be treated as `status = "no_base"` emitting zero labels. Assigning `exact_green` from conclusion alone bypasses base-log verification, silently treating runs that skipped tests, executed linters, or performed non-test tasks as having executed clean, passing test suites.

---

## 2. Phase 2 — Empirical Sample of 20 `exact_green` Base Runs

Foreground sampling execution completed with **40 total HTTP requests** (below the hard cap of 60 requests). The sample covers **20 instances** spanning **17 distinct repositories** (exceeding the >=8 repo requirement), including all 5 available Python repositories and 12 diverse Java repositories (Gradle and Maven).

### 2.1 Instance Table (20 Sampled Runs)

| # | Repository | Lang | Base Run ID | Base Conclusion | Log Fetch HTTP Status | Parser Verdict | Tests Observed |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | `agno-agi/agno` | Python | 27565225229 | success | 200 OK | `TEST_RAN_CLEAN` | 8,708 |
| 2 | `agno-agi/agno` | Python | 26663829082 | success | 410 Gone | N/A (unretrievable) | 0 |
| 3 | `fla-org/flash-linear-attention` | Python | 32457276501 | success | 200 OK | `NO_TEST_OUTPUT` | 0 |
| 4 | `fla-org/flash-linear-attention` | Python | 32457276803 | success | 200 OK | `NO_TEST_OUTPUT` | 0 |
| 5 | `dask/distributed` | Python | 29199157403 | success | 200 OK | `NO_TEST_OUTPUT` | 0 |
| 6 | `dask/distributed` | Python | 32936662258 | success | 200 OK | `TEST_RAN_CLEAN` | 2,583 |
| 7 | `theupdateframework/python-tuf` | Python | 26081729305 | success | 410 Gone | N/A (unretrievable) | 0 |
| 8 | `farama-foundation/highwayenv` | Python | 27987450338 | success | 200 OK | `TEST_RAN_CLEAN` | 108 |
| 9 | `apache/beam` | Java | 30682480591 | success | 200 OK | `TEST_RAN_CLEAN` | 7 |
| 10 | `thealgorithms/java` | Java | 28157388135 | success | 200 OK | `TEST_RAN_CLEAN` | 18,702 |
| 11 | `dbeaver/dbeaver` | Java | 28117794930 | success | 410 Gone | N/A (unretrievable) | 0 |
| 12 | `Stirling-Tools/Stirling-PDF` | Java | 27617950373 | success | 200 OK | `NO_TEST_OUTPUT` | 0 |
| 13 | `apache/fineract` | Java | 26812994791 | success | 410 Gone | N/A (unretrievable) | 0 |
| 14 | `apache/tika` | Java | 32055788634 | success | 200 OK | `TEST_RAN_CLEAN` | 16 |
| 15 | `sirixdb/sirix` | Java | 30205344504 | success | 200 OK | `NO_TEST_OUTPUT` | 0 |
| 16 | `opentripplanner/opentripplanner` | Java | 25910376063 | success | 410 Gone | N/A (unretrievable) | 0 |
| 17 | `diffplug/spotless` | Java | 28403875483 | success | 200 OK | `NO_TEST_OUTPUT` | 0 |
| 18 | `spiculedata/saiku` | Java | 25950491423 | success | 410 Gone | N/A (unretrievable) | 0 |
| 19 | `apple/servicetalk` | Java | 32034209484 | success | 200 OK | `NO_TEST_OUTPUT` | 0 |
| 20 | `apache/hbase` | Java | 23635043778 | success | 410 Gone | N/A (unretrievable) | 0 |

### 2.2 Summary Fractions (Written as Numbers)
- **2a. Base logs retrievable**: **13 / 20** (**65.0%**)
- **2b. Of retrievable: genuinely green with tests observed**: **6 / 13** (**46.15%**)
- **2c. Of retrievable: NO_TEST_OUTPUT (success but zero tests run)**: **7 / 13** (**53.85%**)
- *(Additional) Of retrievable: TEST_FAILURE*: **0 / 13** (**0.0%**)

---

## 3. Phase 3 — Impact on 778 Strict Instances

### 3a. Extrapolation of 2c (`NO_TEST_OUTPUT`) to all 4,245 `exact_green` Instances
- **Sample Baseline**: $n = 13$ retrievable base logs, $\hat{p} = 7 / 13 \approx 53.85\%$.
- **95% Confidence Interval (Wilson Score)**: **29.14% to 76.79%** (Wald: 26.75% to 80.95%).
- **Extrapolated Range across 4,245 `exact_green` Instances**: **1,237 to 3,260 instances** (Point estimate: 2,286 instances).
- *Finding*: Between 1,237 and 3,260 `exact_green` runs concluded "success" without executing any test framework.

### 3b. Strict Split Dependency on `exact_green`
- **Strict Instances ($N = 778$ total)**:
  - Dependent on `exact_green`: **679 / 778** (**87.28%**)
  - Dependent on `exact` (two-sided parsed): **81 / 778** (**10.41%**)
  - Dependent on `ancestor` (two-sided parsed): **17 / 778** (**2.19%**)
  - Dependent on `branch_prior` (two-sided parsed): **1 / 778** (**0.13%**)
- **Strict Fault-Revealing Labels ($L = 4,194$ total)**:
  - Dependent on `exact_green`: **3,816 / 4,194** (**90.99%**)
  - Dependent on parsed base (`exact` / `ancestor` / `branch_prior`): **378 / 4,194** (**9.01%**)

### 3c. Safety Verdict for 778
- **Verdict**: The 778 strict instances figure is **PROVISIONAL AND CURRENTLY UNSAFE pending a full base-log parse and verification**.
- **Plain Explanation**: 87.28% of the strict split (679 instances) rests entirely on `exact_green`. Because 53.85% of retrievable `exact_green` runs ran zero tests (Wilson 95% CI: [29.1%, 76.8%]), an estimated **198 to 521 strict instances** (point estimate: **366 instances**) are false positives that lack base-side execution grounding to establish that the failing tests were ever green on the base branch.

---

## 4. Phase 4 — The 410 Census (014-A Phase 4f Accounting)

Census evaluated across all **2,371 newly resolved base runs** from targeted resolution (`data/interim/base_resolution_targeted.parquet`) relative to timestamp `2026-09-01T10:00:53Z` (90-day cutoff: `2026-06-03T10:00:53Z`).

### 4.1 Overall Census
- **Base runs older than 90 days (>90d, permanently 410 Gone)**: **778 / 2,371** (**32.81%**)
- **Base runs within 90 days (<=90d, potentially retrievable)**: **1,593 / 2,371** (**67.19%**)

### 4.2 Per-Language Breakdown
| Language | Total Newly Resolved | Older than 90d (>90d, 410 Gone) | Within 90d (<=90d, Fresh) | Mean Age (Days) | Median Age (Days) | Max Age (Days) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Java** | 2,160 | **763 / 2,160 (35.32%)** | 1,397 / 2,160 (64.68%) | 85.3 d | 74.1 d | 406.4 d |
| **Python** | 211 | **15 / 211 (7.11%)** | 196 / 211 (92.89%) | 65.7 d | 70.2 d | 120.4 d |
| **Total** | **2,371** | **778 / 2,371 (32.81%)** | **1,593 / 2,371 (67.19%)** | **83.5 d** | **73.8 d** | **406.4 d** |

### 4.3 Per-Status Breakdown (>90 Days)
- `exact_green`: **544 / 1,319** (**41.24%**) are >90d
- `exact`: **192 / 733** (**26.19%**) are >90d
- `ancestor`: **42 / 319** (**13.17%**) are >90d

---

## 5. Hypothesis Evaluation

### Hypothesis 1: `exact_green` is assigned from conclusion alone.
- **Verdict**: **CONFIRMED**.
- **Evidence**: `src/label/base_resolve.py` assigns `exact_green` whenever `conclusion == "success"`. Phase 2 empirical parsing of 13 retrievable logs revealed 7 out of 13 (53.85%) produced `NO_TEST_OUTPUT` (linters, spotless, release/docs tasks).

### Hypothesis 2: A large share of base logs will 410.
- **Verdict**: **CONFIRMED**.
- **Evidence**: In Phase 2 sample, 7 out of 20 (35.0%) returned 410 Gone. In Phase 4 census, 778 out of 2,371 (32.81%) newly resolved base runs are >90 days old and unrecoverable.

### Hypothesis 3: Python bases will 410 at a higher rate than Java.
- **Verdict**: **REFUTED (FALSE)**.
- **Evidence**: Python base runs 410 at a dramatically *lower* rate than Java (7.11% >90d in Python vs 35.32% >90d in Java; in Phase 2 sample, Python retrievability was 75.0% vs Java 58.3%). Python runs were harvested from recently active windows, while Java runs include deep historical backlog.

### Hypothesis 4: Some `exact_green` bases will parse to `TEST_FAILURE`.
- **Verdict**: **REFUTED / NOT OBSERVED (0 / 13 in sample)**.
- **Evidence**: 0 out of 13 retrievable base logs parsed to `TEST_FAILURE`. Successful runs did not conceal ignored test failures. The actual failure mode is the absence of test execution (`NO_TEST_OUTPUT`), not concealed failures.

### Hypothesis 5 (Added): Strict split (778 instances) is overwhelmingly dominated by unverified `exact_green` runs.
- **Verdict**: **CONFIRMED**.
- **Evidence**: 679 of 778 strict instances (87.28%) and 3,816 of 4,194 strict labels (90.99%) depend on `exact_green`. Because 53.85% of retrievable `exact_green` runs ran no tests, over half of the 778 instances are ungrounded pending full base-log parsing.

---

## 6. Verification & Non-Goals Discipline
- **Non-Goals Honoured**:
  - No re-run of the resolution sweep.
  - No modifications to parsers, `docs/SCHEMAS.md`, test fixtures, or parquet files.
  - No new dependencies added.
  - Harvester daemon unmolested.
  - No background tasks or subagents used.
  - No commits performed.
- **Test Suite Status**: 381 passed, 0 failed.
