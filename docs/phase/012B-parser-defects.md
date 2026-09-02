# Phase 012-B: Parser Defects Diagnosis (Bug Report for CLI-1)

**Role**: CLI-2 (Read-only diagnosis; no modifications to `src/` made).  
**Purpose**: Document three concrete parser defects identified during the holdout v4 audit for CLI-1 remediation.

---

## 1. Defect 3a: pytest Parameterisation Emits Leaf Iterations (D-32 Violation)

### 1.1 Citation by Function Name
- `src/parse/log_pytest.py`: `parse_pytest_log_with_stats()` (lines 170–398), `_SUMMARY_LINE_RE` (line 87), `_PROGRESS_LINE_RE` (line 92), `_XDIST_PROGRESS_LINE_RE` (line 97).
- `src/parse/test_ids.py`: `_extract_params_and_method()` (lines 73–89), `normalize_test_id()` (lines 91–419).

### 1.2 Raw Log Lines
- `tests/fixtures/holdout_v4/dask__distributed__084645769341.txt:4015`:
  ```
  2026-07-01T22:02:54.1287396Z FAILED distributed/tests/test_nanny.py::test_failure_during_worker_initialization[45-100] - TimeoutError: Test timeout (30) hit after 30.000552999999968s.
  ```
- `tests/fixtures/holdout_v4/dask__distributed__084757793457.txt:10792`:
  ```
  2026-07-02T12:00:40.2795756Z FAILED distributed/tests/test_active_memory_manager.py::test_RetireWorker_stress[False-17-100] - TimeoutError: Test timeout (180) hit after 179.9853481s.
  ```
- `tests/fixtures/holdout_v4/fla-org__flash-linear-attention__082566635619.txt:709`:
  ```
  2026-06-21T11:35:36.7152616Z FAILED tests/models/test_modeling_forgetting_transformer.py::test_modeling[L4-B4-T1024-H4-D64-l2True-bsNone-torch.bfloat16] - RuntimeError: No CUDA GPUs are available
  ```
- `tests/fixtures/holdout_v4/fla-org__flash-linear-attention__086098926451.txt:779`:
  ```
  2026-07-09T10:42:18.0446013Z FAILED tests/models/test_modeling_comba.py::test_generation[L2-B4-T2000-H8-D64-torch.float16] - TypeError: Can't instantiate abstract class FLALayer without an implementation for abstract method 'get_max_length'
  ```

### 1.3 Parser Output
- `distributed/tests/test_nanny.py::test_failure_during_worker_initialization[45-100]`
- `distributed/tests/test_active_memory_manager.py::test_RetireWorker_stress[False-17-100]`
- `tests/models/test_modeling_forgetting_transformer.py::test_modeling[L4-B4-T1024-H4-D64-l2True-bsNone-torch.bfloat16]`
- `tests/models/test_modeling_comba.py::test_generation[L2-B4-T2000-H8-D64-torch.float16]`

### 1.4 Diagnosis & Location Where pytest Path Should Strip It
- **D-32 Specification**: Decision D-32 mandates: *"The canonical `test_id` is the SELECTABLE UNIT: the method, or for Spock the feature method. The iteration or parameter set lives in `TestId.params`, never in the canonical id. A pytest `[2-3-5]`, a JUnit `[1]` and a Spock `@Unroll` iteration are the same construct."*
- **Was D-32 ever implemented in code at all?**
  **NO.** D-32 was never implemented in the pytest log parsing pipeline. In fact, `src/parse/log_pytest.py` contains explicit comments directly violating D-32 (lines 28–31):
  ```python
  # Parameterised Test Identifiers:
  # Parameterised test IDs keep their parameter brackets '[...]' and do NOT collapse
  # (unlike Surefire execution indices), because pytest parameterised instances are
  # independently addressable test node CLI targets.
  ```
- **Remediation location**:
  In `src/parse/log_pytest.py`, inside `parse_pytest_log_with_stats()` (lines 245, 295, 349) where `raw_node_id` is parsed. The parameter bracket `\[.*?\]` must be stripped from `raw_node_id` to form canonical `test_id` (e.g. via `_extract_params_and_method()` or `normalize_test_id()`), and the parameter string must be recorded in `TestOutcome.params` / `TestId.params`.

---

## 2. Defect 3b: Gradle Parser Prefixes "Gradle suite" and Emits Dot Separators

### 2.1 Citation by Function Name
- `src/parse/log_gradle.py`: `parse_gradle_log_with_stats()` (lines 285–325, Chevron single-line matching), `_clean_line()` (lines 160–164).

### 2.2 Raw Log Line
- `tests/fixtures/holdout_v4/linkedin__brooklin__077863844421.txt:3577`:
  ```
  2026-05-26T13:05:09.6365165Z Gradle suite > Gradle test > com.linkedin.datastream.server.TestCoordinator.testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation FAILED
  ```

### 2.3 Parser Output
- Emitted test identifier:
  `Gradle suite::com.linkedin.datastream.server.TestCoordinator.testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation`
  (internal intermediate: `Gradle suite#com.linkedin.datastream.server.TestCoordinator.testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation`)

### 2.4 Diagnosis & Root Cause
- When TestNG / Gradle multi-level suite executions run, Gradle outputs:
  `Gradle suite > Gradle test > <fqcn>.<method> FAILED`.
- In `src/parse/log_gradle.py`:
  1. `_clean_line()` removes timestamps, leaving `Gradle suite > Gradle test > com.linkedin.datastream.server.TestCoordinator.testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation FAILED`.
  2. `segments = prefix.split(" > ")` yields 3 segments:
     - `segments[0] = "Gradle suite"`
     - `segments[1] = "Gradle test"`
     - `segments[2] = "com.linkedin.datastream.server.TestCoordinator.testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation"`
  3. The Chevron parser logic sets `cls_name = segments[0]` (`"Gradle suite"`) and `method_raw = segments[-1]` (the entire FQCN + method string).
  4. It constructs `test_id = f"{cls_name}#{method_raw}"`.
  5. The parser fails to strip known Gradle runner harness wrappers (`"Gradle suite"`, `"Gradle test"`), and fails to split `<fqcn>.<method>` where dot notation separates class from method.
- **Expected Canonical Form**:
  `com.linkedin.datastream.server.TestCoordinator::testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation` (or `#testLeader...`).

---

## 3. Defect 3c: Java Suffix Reconciliation Drops Package on Custom Test Summaries

### 3.1 Citation by Function Name
- `src/parse/log_gradle.py`: `parse_gradle_log_with_stats()` (lines 183–194 stack trace collection, lines 285–325 chevron extraction, lines 347–382 Pass 1 suffix join).

### 3.2 Raw Log Lines
- `tests/fixtures/holdout_v4/sirixdb__sirix__092352347826.txt`:
  - Line 384:
    ```
    2026-08-05T15:30:56.2947870Z RegionOnlyPredicateCountTest > negationConjoinedWithAnAnchoringLeafIsRepresentable() FAILED
    ```
  - Line 387:
    ```
    2026-08-05T15:30:57.7205480Z RegionOnlyPredicateCountTest > numericAndBooleanFuseIntoOnePass() FAILED
    ```
  - Line 395:
    ```
    2026-08-05T15:31:18.4774570Z FAILED-TEST: io.sirix.query.scan.RegionOnlyPredicateCountTest > negationConjoinedWithAnAnchoringLeafIsRepresentable(): org.opentest4j.AssertionFailedError: predicate not claimed at all: $u.year gt 1990 and not($u.active) ==> expected: <true> but was: <false>
    ```
  - Line 396:
    ```
    2026-08-05T15:31:18.4812950Z FAILED-TEST: io.sirix.query.scan.RegionOnlyPredicateCountTest > numericAndBooleanFuseIntoOnePass(): org.opentest4j.AssertionFailedError: no page served from the fused columns for $u.year gt 1990 and not($u.active) (served=0, fellBack=0) ==> expected: <true> but was: <false>
    ```

### 3.3 Parser Output
- `RegionOnlyPredicateCountTest::negationConjoinedWithAnAnchoringLeafIsRepresentable`
- `RegionOnlyPredicateCountTest::numericAndBooleanFuseIntoOnePass`

### 3.4 Diagnosis & Root Cause
- In `src/parse/log_gradle.py`:
  1. The chevron parser matches lines 384 and 387, producing `test_id = "RegionOnlyPredicateCountTest#negationConjoinedWithAnAnchoringLeafIsRepresentable"`.
  2. In Pass 1 (suffix reconciliation, lines 357–380), the parser checks `stack_fqcns` for `("RegionOnlyPredicateCountTest", "negationConjoinedWithAnAnchoringLeafIsRepresentable")`.
  3. `stack_fqcns` is populated *strictly* by `_AT_FRAME_RE` (matching `^\s*at\s+([A-Za-z0-9_$.]+)\.([^\n(]+)\(`).
  4. In this build log, JUnit 5 threw assertion errors whose stack traces only contained assertion library frames (`at org.junit.jupiter.api.AssertionUtils...`) without an `at io.sirix.query.scan.RegionOnlyPredicateCountTest...` frame.
  5. The FQCN was present in the log header banner (`FAILED-TEST: io.sirix.query.scan.RegionOnlyPredicateCountTest > ...`), but `log_gradle.py` has no pattern matching `FAILED-TEST:` summary banners.
  6. As a result, `candidates` was empty (`len(candidates) == 0`), suffix join did not occur, and the parser emitted the bare class name missing `io.sirix.query.scan.` (or `org.sirix.index.path.summary.`).
- **Remediation**:
  `src/parse/log_gradle.py` should index FQCNs from `FAILED-TEST:` and test execution banners, not exclusively from `\s*at\s+` stack frames.

---

## 4. Defect 4: Maven Class-Level Last-Dot Split (D-46 Violation)

Maven FORM A splits a class-level failure line at the last dot, so "org.apache.hugegraph.core.CoreTestSuite  Time elapsed: 2.946 s  <<< ERROR!" — which names a class and no method — emits org.apache.hugegraph.core#CoreTestSuite, package-as-class and class-as-method. Evidence: apache__hugegraph__084221602296.txt, row 57e11a35966e. Governed by D-46. NOT FIXED in this task.

