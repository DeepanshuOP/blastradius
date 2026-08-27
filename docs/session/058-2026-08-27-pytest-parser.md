# Session Report: 058-2026-08-27-pytest-parser

**Date:** 2026-08-27  
**Task ID:** `T1.1d` — Implement `src/parse/log_pytest.py` and `tests/test_log_pytest.py`  
**Model:** Gemini 3.7 Flash (High)  
**Topic:** Rebuild pytest execution log parser, commit uncommitted Maven parser deliverable, evaluate 40-row development fixture corpus scorecard, verify zero cross-contamination against Gradle fixtures, and assert 46/46 fitted combined coverage.

---

## 1. Stage 4 Completion Context & Filed Defect

### Stage 4 Completion Figures
Stage 4 log capture has completed with the following final empirical totals:
- **Captured Logs:** 11,207 logs
- **Failed Job Logs:** 1,546 logs
- **Permanently Lost (90-Day Wall):** 5,516 units
- **On-Disk Corpus Volume:** 1.37 GB
- **Mean Compressed Size per Log:** 119.2 KB

### Filed Defect: Expiry Cliff Log Size Underestimate
- **Defect Location:** `analysis/expiry_cliff.py`
- **Current Constants:**
  - `MEASURED_LOG_ON_DISK_MB = 0.0070` (7.0 KB)
  - `MEASURED_LOG_MB = 0.0266` (26.6 KB)
- **Empirical Ground Truth (Corpus-Wide):**
  - Actual mean compressed log on disk: **119.2 KB** (`~0.1192 MB`), which is **~17.0x larger** than `MEASURED_LOG_ON_DISK_MB`.
  - Actual decompressed volume: roughly **38x larger** than `MEASURED_LOG_MB`.
- **Status:** Filed defect. `analysis/expiry_cliff.py` was left untouched in this session per strict non-goals.

---

## 2. Guard Commands & Step 0 Output

### Guard Output
```bash
$ uname -s && pwd && uv run python --version
Linux
/home/shree/blastradius
Python 3.11.15

$ git log -1 --format='%H %s'
2e6f1d89464f6d8d678810927524cb3fa054ad6f docs: record why stage four stalls and correct the holdout claim

$ git config user.name && git config user.email
DeepanshuOP
99538840+DeepanshuOP@users.noreply.github.com

$ git status --short
?? src/parse/log_maven.py
?? tests/test_log_maven.py
?? vendor/graphify-br/

$ ps aux | grep -E '[r]un_supervised|[h]arvest'
shree       3726  0.0  0.0   4944  3456 ?        Ss   17:44   0:00 bash ./run_supervised.sh both
shree       3730  0.0  0.2 225508 33536 ?        Sl   17:44   0:00 uv run --env-file .env python -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both
shree       3733 99.8  0.6  94852 77936 ?        R    17:44   0:41 /home/shree/blastradius/.venv/bin/python3 -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both
```

---

## 3. Step 1 — Commit `log_maven.py` Unchanged

Ran test suite prior to staging:
- Predicted test count: **272**
- Actual test count: **272 passed** in 6.04s

```bash
$ git add src/parse/log_maven.py tests/test_log_maven.py
$ git commit -m "feat: read failing test names out of maven build logs"
[main 3b94b0d] feat: read failing test names out of maven build logs
 2 files changed, 661 insertions(+)
 create mode 100644 src/parse/log_maven.py
 create mode 100644 tests/test_log_maven.py
```

---

## 4. Step 2 — Pytest Parser Design & Implementation

Implemented `src/parse/log_pytest.py` per the approved architectural specification:
- **Module Interface:**
  - `parse_pytest_log_with_stats(body, run_id, job_id, repo, head_sha) -> tuple[list[TestOutcome], PytestParseStats]`
  - `parse_pytest_log(...) -> list[TestOutcome]`
  - `extract_pytest_failing_test_ids(body) -> set[str]`
  - `classify_pytest_log(body) -> tuple[str, set[str], bool]`
- **`PytestParseStats` Dataclass:**
  - `total_outcomes: int = 0`
  - `summary_fail_count: int = 0`
  - `summary_error_count: int = 0`
  - `progress_fail_count: int = 0`
  - `progress_error_count: int = 0`
  - `dedup_merged_count: int = 0`
- **Provisional Confidence Constants:**
  - `CONFIDENCE_PYTEST_SUMMARY = 0.90`
  - `CONFIDENCE_PYTEST_PROGRESS = 0.85`
  - Merged confidence: `max(existing.parser_confidence, CONFIDENCE_PYTEST_SUMMARY)`
- **Deduplication & Enrichment:**
  Progress execution lines (`node_id FAILED [ 28%]`) instantiate initial outcomes. Summary lines (`FAILED node_id - Exception: msg`) enrich the existing progress record with `failure_message` and elevate confidence to 0.90 without dropping either representation.
- **Parameter Preservation:**
  Parameterised test IDs retain full bracket expressions (e.g. `tests/test_calc.py::test_add[2-3-5]`) as first-class addressable CLI targets. Inner `::` characters within parameters do not fragment node IDs.
- **XFAIL / XPASS Policy:**
  Explicit unsupported branch with comment noting pytest's strict xfail mode (`xfail_strict=true`) where XPASS causes suite failures.
- **Normalization Boundary:**
  Emits raw pytest node IDs for downstream normalization via `normalize_test_id()`.

---

## 5. Step 3 — Scorecard & Acceptance Evaluation

Evaluated `src/parse/log_pytest.py` across all 40 development fixtures in `tests/fixtures/logs/`:

```
==============================================================================================================
BLASTRADIUS FIXTURE CORPUS SCORECARD (T1.1a Evaluation)
==============================================================================================================
Normalization Rule: Strip trailing '()', replace '#' and ' > ' with '::' on both expected and extracted IDs.
--------------------------------------------------------------------------------------------------------------
#   | Fixture Filename                                 | Exp Class   | Act Class   | Exp | Ext | TP  | FP  | FN  | Match
--------------------------------------------------------------------------------------------------------------
1   | apache__beam__077621011187.txt                   | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
2   | apache__beam__077630056646.txt                   | TEST_FAILURE | NO_TEST_OUTPUT | 1   | 0   | 0   | 0   | 1   | DIFF
3   | apache__beam__082575659629.txt                   | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
4   | apache__beam__082592431584.txt                   | TEST_FAILURE | TEST_FAILURE | 8   | 8   | 8   | 0   | 0   | OK
5   | apache__beam__086455350919.txt                   | TEST_FAILURE | NO_TEST_OUTPUT | 2   | 0   | 0   | 0   | 2   | DIFF
6   | apache__dolphinscheduler__083801509824.txt       | TEST_FAILURE | NO_TEST_OUTPUT | 1   | 0   | 0   | 0   | 1   | DIFF
7   | apache__fineract__080132127199.txt               | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
8   | apache__fineract__083161294301.txt               | TEST_FAILURE | NO_TEST_OUTPUT | 1   | 0   | 0   | 0   | 1   | DIFF
9   | apache__flink__079221420559.txt                  | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
10  | apache__flink__079848838447.txt                  | TEST_FAILURE | NO_TEST_OUTPUT | 2   | 0   | 0   | 0   | 2   | DIFF
11  | apache__hbase__078892029185.txt                  | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
12  | apache__hbase__082907939305.txt                  | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
13  | apache__hbase__083382132597.txt                  | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
14  | apache__hbase__084057821217.txt                  | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
15  | apache__zeppelin__079328560137.txt               | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
16  | apache__zeppelin__084837475646.txt               | TEST_FAILURE | NO_TEST_OUTPUT | 1   | 0   | 0   | 0   | 1   | DIFF
17  | airlift__airlift__081878478589.txt               | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
18  | airlift__airlift__084082609180.txt               | TEST_FAILURE | NO_TEST_OUTPUT | 1   | 0   | 0   | 0   | 1   | DIFF
19  | apple__servicetalk__085939947321.txt             | TEST_FAILURE | NO_TEST_OUTPUT | 1   | 0   | 0   | 0   | 1   | DIFF
20  | baomidou__mybatis-plus__085831964676.txt         | TEST_FAILURE | NO_TEST_OUTPUT | 1   | 0   | 0   | 0   | 1   | DIFF
21  | crimera__piko__083277376521.txt                  | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
22  | diffplug__spotless__077697425370.txt             | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
23  | diffplug__spotless__086063491051.txt             | TEST_FAILURE | NO_TEST_OUTPUT | 3   | 0   | 0   | 0   | 3   | DIFF
24  | floci-io__floci__081814559712.txt                | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
25  | floci-io__floci__082492942956.txt                | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
26  | floci-io__floci__084479785666.txt                | TEST_FAILURE | NO_TEST_OUTPUT | 1   | 0   | 0   | 0   | 1   | DIFF
27  | grobidOrg__grobid__085264981989.txt              | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
28  | jhipster__prettier-java__084966237571.txt        | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
29  | openremote__openremote__082946004526.txt         | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
30  | openremote__openremote__084103046129.txt         | TEST_FAILURE | NO_TEST_OUTPUT | 1   | 0   | 0   | 0   | 1   | DIFF
31  | opentripplanner__opentripplanner__077860984374.txt | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
32  | opentripplanner__opentripplanner__077865124037.txt | TEST_FAILURE | NO_TEST_OUTPUT | 4   | 0   | 0   | 0   | 4   | DIFF
33  | sirixdb__sirix__079909436297.txt                 | TEST_FAILURE | NO_TEST_OUTPUT | 6   | 0   | 0   | 0   | 6   | DIFF
34  | sirixdb__sirix__086198357085.txt                 | TEST_FAILURE | NO_TEST_OUTPUT | 1   | 0   | 0   | 0   | 1   | DIFF
35  | spiculedata__saiku__080014373865.txt             | TEST_RAN_CLEAN | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | DIFF
36  | spiculedata__saiku__082534301666.txt             | TEST_FAILURE | NO_TEST_OUTPUT | 8   | 0   | 0   | 0   | 8   | DIFF
37  | Stirling-Tools__Stirling-PDF__077860967858.txt   | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
38  | Stirling-Tools__Stirling-PDF__081016086095.txt   | TEST_FAILURE | NO_TEST_OUTPUT | 1   | 0   | 0   | 0   | 1   | DIFF
39  | Stirling-Tools__Stirling-PDF__085817860968.txt   | TEST_FAILURE | NO_TEST_OUTPUT | 1   | 0   | 0   | 0   | 1   | DIFF
40  | thealgorithms__java__080494921200.txt            | TEST_FAILURE | NO_TEST_OUTPUT | 1   | 0   | 0   | 0   | 1   | DIFF
--------------------------------------------------------------------------------------------------------------
CORPUS TOTALS & METRICS:
  Total Fixtures:              40
  Total Expected Identifiers:  46
  Total Extracted Identifiers: 8
  True Positives (TP):         8
  False Positives (FP):        0
  False Negatives (FN):        38
  Precision:                   1.0000 (100.00%)
  Recall:                      0.1739 (17.39%)
  F1 Score:                    0.2963
  Classification Accuracy:     0.5000 (50.00%) [20/40]
  No-Failure Fixtures with FP: 0/20
==============================================================================================================
```

### Acceptance Criteria Verification
1. **Fixture 4:**
   - TP = 8, FP = 0, FN = 0.
   - `dedup_merged_count = 8` (all 8 tests matched across both progress and summary lines).
2. **Zero False Positives:**
   - Total FP = 0 across all 40 fixtures.
   - All 20 no-failure fixtures + Fixture 35 produced 0 FP.
3. **Cross-Contamination Checks:**
   - Fixture 2 (`apache__beam__077630056646.txt`, Gradle Java harness): Extracted = 0, FP = 0.
   - Fixture 5 (`apache__beam__086455350919.txt`, Gradle Groovy runner): Extracted = 0, FP = 0.
4. **Combined Coverage across `log_gradle` + `log_maven` + `log_pytest`:**
   - Gradle fixtures: 19/19 expected identifiers extracted with 0 FP.
   - Maven fixtures: 19/19 expected identifiers extracted with 0 FP.
   - Pytest fixtures: 8/8 expected identifiers extracted with 0 FP.
   - Combined Total: **46 / 46 identifiers (100.00% recall, 100.00% precision, 0 FP)**.
   - **Important Note:** This 46/46 is a **FITTED** metric on the development fixture corpus, not the held-out evaluation figure required by ROADMAP §25.3.

---

## 6. Step 4 — Unit Test Suite

Implemented `tests/test_log_pytest.py` with 12 comprehensive unit tests:
- `test_fixture_4_eight_identifiers`: Real fixture 4 all 8 outcomes verified.
- `test_fixture_4_dedup_merge_enrichment`: Real fixture 4 message and confidence elevation verified.
- `test_fixture_2_boundary_yields_empty`: Real fixture 2 boundary verified.
- `test_fixture_5_boundary_yields_empty`: Real fixture 5 boundary verified.
- `test_no_failure_fixtures_yield_empty`: Real clean/setup fixtures verified.
- `test_synthetic_module_level_failure`: Minimal synthetic module-level error.
- `test_synthetic_error_fixture_setup`: Minimal synthetic fixture setup ERROR.
- `test_synthetic_parameterised_brackets_preserved`: Minimal synthetic parameter bracket preservation.
- `test_synthetic_parameterised_complex_brackets`: Minimal synthetic parameter bracket with nested `::`.
- `test_synthetic_doctest_failure`: Minimal synthetic doctest failure.
- `test_synthetic_xfail_xpass_unsupported`: Minimal synthetic xfail/xpass drop assertion.
- `test_classify_pytest_log_contracts`: Real fixture contracts for `classify_pytest_log`.

### Test Execution
- **Predicted Test Count:** 284
- **Actual Test Count:** 284 passed in 4.74s

```bash
$ uv run pytest -q
........................................................................ [ 25%]
........................................................................ [ 50%]
........................................................................ [ 76%]
....................................................................     [100%]
284 passed in 4.74s

$ uv run python -c "import src.parse; import src.parse.log_pytest; print('imports ok')"
imports ok
```

---

## 7. Quarantine & Non-Goals Compliance

- **Quarantine:** `tests/fixtures/holdout/` was NOT read, opened, globbed, grepped, or scored.
- **Harvester Isolation:** `src/harvest/`, `cursor.db`, `data/`, `logs/` were completely untouched while the supervisor ran stages 1+2.
- **Shared Code Integrity:** `src/parse/log_gradle.py`, `src/parse/log_maven.py`, `src/parse/outcome.py`, and `analysis/expiry_cliff.py` remained untouched.
