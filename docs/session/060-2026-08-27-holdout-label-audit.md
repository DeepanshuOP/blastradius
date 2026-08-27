# Session Report: 060-2026-08-27-holdout-label-audit

**Date:** 2026-08-27  
**Task ID:** `T1.1c` — Audit and correct holdout labelling-discipline violation, add Decision D-29, and re-score  
**Model:** Gemini 3.7 Flash (High)  
**Topic:** Audit of holdout fixture annotations against raw log text, correction of external repository lookup violations (Fixtures 14 & 15), adoption of Decision D-29 (Ground-Truth Labelling Discipline), re-evaluation of union precision/recall (29.73% -> 45.95% precision, 36.67% -> 56.67% recall), and queuing of three genuine parser defect work items.

---

## 1. Executive Summary & Audit Verdicts

### Step 1 Audit Findings (Per-Fixture Verification)

| Fixture Filename | Candidate Package String | Log Match Count | Verdict | Action Taken |
| :--- | :--- | :---: | :--- | :--- |
| **`nats-io__nats.java__086852684070.txt`** (12) | `io.nats.client.api` | **5** | **Present in Log** (Stack trace lines 2755, 9120, 9133, 9149, 9165) | Retained as `io.nats.client.api.KeyValueConfigurationTests#testInstanceMirrorAndSources` per raw log evidence |
| **`gurkenlabs__litiengine__079032771640.txt`** (14) | `de.gurkenlabs.litiengine.AlignTests` | **0** | **Confirmed External Lookup** (Only bare `AlignTests` appears on failure lines 564/567; package on line 426 was compiler note for unrelated `ArrayUtilities.java`) | **Corrected** to `AlignTests#getClampedLocation_InPoint` and `AlignTests#getClampedLocation_OffPoint` |
| **`mcreator__mcreator__081715271356.txt`** (15) | `net.mcreator.integration.ReferencesFinderTest` | **0** | **Confirmed External Lookup** (Failure lines 88212 emit bare `ReferencesFinderTest`; stack traces reference base setup class `IntegrationTestSetup`; file path is `workspace.ReferencesFinderTest`) | **Corrected** to `ReferencesFinderTest#...` (4 methods) |

---

## 2. Guard Commands & Step 0 Output

### Guard Output
```bash
$ uname -s && pwd && uv run python --version
Linux
/home/shree/blastradius
Python 3.11.15

$ git log -1 --format='%H %s'
5ccb4eda741c1ac1d3cd96e16f07baa309ee723e test: measure parser precision against logs they never saw

$ git status --short
?? vendor/graphify-br/

$ ps aux | grep -E '[r]un_supervised|[h]arvest'
shree       3726  0.0  0.0   4944  3456 ?        Ss   17:44   0:00 bash ./run_supervised.sh both
shree       3730  0.0  0.2 225508 33536 ?        Sl   17:44   0:00 uv run --env-file .env python -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both
shree       3733  4.6  0.5  73400 66424 ?        S    17:44   2:11 /home/shree/blastradius/.venv/bin/python3 -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both
```

---

## 3. Step 2 & 3 — Decision D-29 & Ground-Truth Labelling Correction

Confirmed from `docs/DECISIONS.md` that the last decision was **D-27**. Decision **D-28** is reserved by the Architect. The next free sequence number is **D-29**.

Added **D-29** to `docs/DECISIONS.md`:
> **D-29 — Ground-truth labelling discipline & raw-log derivation.**
> Fixture and held-out expectations in `EXPECTED.md` must derive strictly and exclusively from information visible within the raw log text itself. Hand-labellers may not consult external source repositories, file trees, or IDE class search to fabricate package prefixes, class hierarchies, or method signatures that do not appear in the log. When a log outputs only a simple class name (e.g. `AlignTests > testFoo FAILED`), the expected canonical identifier is `AlignTests#testFoo`, leaving package and path binding to downstream AST/source reconciliation (`resolve_test_file()`). This applies uniformly to development and holdout fixture corpora going forward. Cross-reference D-27 and D-09.

Updated `tests/fixtures/holdout/EXPECTED.md` for Fixtures 14 and 15 to reflect raw log text bare class names.

---

## 4. Step 4 — Re-Scored Held-Out Corpus Metrics

### Verbatim Output of `uv run python -m analysis.holdout_eval`
```
========================================================================================================================
BLASTRADIUS HELD-OUT CORPUS SCORECARD (Union Scorer Evaluation — ROADMAP §25.3 / §34.4)
========================================================================================================================
Strategy: Union of log_gradle, log_maven, and log_pytest extractors + most specific classification.
Normalization Rule: Strip trailing '()', replace '#' and ' > ' with '::' on both expected and extracted IDs.
------------------------------------------------------------------------------------------------------------------------
#   | Fixture Filename                             | Harness | Exp Class   | Act Class   | Exp | Ext | TP  | FP  | FN  | Fired        | Match
------------------------------------------------------------------------------------------------------------------------
1   | apache__beam__078088881219.txt               | pytest  | TEST_FAILURE | NO_TEST_OUTPUT | 1   | 0   | 0   | 0   | 1   | none         | DIFF
2   | apache__beam__077874374405.txt               | pytest  | TEST_FAILURE | TEST_FAILURE | 4   | 4   | 4   | 0   | 0   | pytest       | OK
3   | floci-io__floci__084186316975.txt            | Maven   | TEST_FAILURE | TEST_FAILURE | 1   | 1   | 1   | 0   | 0   | maven        | OK
4   | unicode-org__cldr__083663566205.txt          | Maven   | TEST_FAILURE | TEST_FAILURE | 1   | 1   | 1   | 0   | 0   | maven        | OK
5   | unicode-org__cldr__086892997256.txt          | Maven   | TEST_FAILURE | TEST_FAILURE | 1   | 1   | 1   | 0   | 0   | maven        | OK
6   | apache__hugegraph__086448298201.txt          | Maven   | TEST_FAILURE | TEST_FAILURE | 3   | 6   | 0   | 6   | 3   | maven        | DIFF
7   | apache__hugegraph__085379131609.txt          | Maven   | TEST_FAILURE | TEST_FAILURE | 3   | 6   | 0   | 6   | 3   | maven        | DIFF
8   | airlift__airlift__084082609225.txt           | Maven   | TEST_FAILURE | TEST_FAILURE | 1   | 1   | 1   | 0   | 0   | maven        | OK
9   | apache__fineract__081211032591.txt           | Gradle  | TEST_FAILURE | TEST_FAILURE | 4   | 4   | 1   | 3   | 3   | gradle       | DIFF
10  | diffplug__spotless__079141262640.txt         | Gradle  | TEST_FAILURE | TEST_FAILURE | 1   | 1   | 1   | 0   | 0   | gradle       | OK
11  | apache__fineract__081669730637.txt           | Gradle  | TEST_FAILURE | TEST_FAILURE | 1   | 1   | 1   | 0   | 0   | gradle       | OK
12  | nats-io__nats.java__086852684070.txt         | Gradle  | TEST_FAILURE | TEST_FAILURE | 1   | 1   | 0   | 1   | 1   | gradle       | DIFF
13  | grobidOrg__grobid__082786616906.txt          | Gradle  | TEST_FAILURE | TEST_FAILURE | 2   | 4   | 0   | 4   | 2   | gradle       | DIFF
14  | gurkenlabs__litiengine__079032771640.txt     | Gradle  | TEST_FAILURE | TEST_FAILURE | 2   | 2   | 2   | 0   | 0   | gradle       | OK
15  | mcreator__mcreator__081715271356.txt         | Gradle  | TEST_FAILURE | TEST_FAILURE | 4   | 4   | 4   | 0   | 0   | gradle       | OK
16  | floci-io__floci__079239274562.txt            | Maven   | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | none         | OK
17  | apache__dolphinscheduler__082710858610.txt   | Other   | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | none         | OK
18  | Stirling-Tools__Stirling-PDF__086823631877.txt | Other   | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | none         | OK
19  | Stirling-Tools__Stirling-PDF__077856960467.txt | Other   | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | none         | OK
20  | apache__hbase__081801116210.txt              | Other   | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | none         | OK
------------------------------------------------------------------------------------------------------------------------
HOLD-OUT TOTALS & AGGREGATE METRICS:
  Total Holdout Fixtures:      20
  Total Expected Identifiers:  30
  Total Extracted Identifiers: 37
  True Positives (TP):         17
  False Positives (FP):        20
  False Negatives (FN):        13
  Precision:                   0.4595 (45.95%)
  Recall:                      0.5667 (56.67%)
  F1 Score:                    0.5075
  Classification Accuracy:     0.9500 (95.00%) [19/20]
  Cross-Firing Fixtures:       0/20 (zero cross-contamination)
------------------------------------------------------------------------------------------------------------------------
PER-HARNESS BREAKDOWN:
  Harness    | Fixtures | Exp IDs | Ext IDs | TP  | FP  | FN  | Precision  | Recall     | F1     | Class Acc
  -----------+----------+---------+---------+-----+-----+-----+------------+------------+--------+----------
  pytest     | 2        | 5       | 4       | 4   | 0   | 1   | 100.00%    |  80.00%    | 0.8889 |  50.00% (1/2)
  Maven      | 7        | 10      | 16      | 4   | 12  | 6   |  25.00%    |  40.00%    | 0.3077 | 100.00% (7/7)
  Gradle     | 7        | 15      | 17      | 9   | 8   | 6   |  52.94%    |  60.00%    | 0.5625 | 100.00% (7/7)
  Other      | 4        | 0       | 0       | 0   | 0   | 0   |   0.00%    |   0.00%    | 0.0000 | 100.00% (4/4)
========================================================================================================================
```

### Pre-Correction vs Post-Correction Delta

| Metric | Initial Run (Mislabeled FQCNs) | Re-Scored (D-29 Compliant) | Absolute Delta | Relative Gain |
| :--- | :---: | :---: | :---: | :---: |
| **True Positives (TP)** | 11 | **17** | +6 | +54.5% |
| **False Positives (FP)** | 26 | **20** | -6 | -23.1% |
| **False Negatives (FN)** | 19 | **13** | -6 | -31.6% |
| **Overall Precision** | 29.73% | **45.95%** | **+16.22%** | **+54.6%** |
| **Overall Recall** | 36.67% | **56.67%** | **+20.00%** | **+54.5%** |
| **Overall F1 Score** | 0.3284 | **0.5075** | **+0.1791** | **+54.5%** |
| **Gradle Precision** | 17.65% | **52.94%** | **+35.29%** | **+200.0%** |
| **Gradle Recall** | 20.00% | **60.00%** | **+40.00%** | **+200.0%** |
| **Classification Accuracy** | 95.00% | **95.00%** | 0.00% | — |
| **Cross-Contamination Rate** | 0.00% | **0.00%** | 0.00% | — |

---

## 5. Queued Work Items for Future Prompts (Known & Filed Parser Gaps)

Per strict non-goal instructions, zero parser code was modified during this audit session. The three remaining genuine parser defects are filed for dedicated single-file prompt remediation:

1. **`src/parse/log_maven.py` — JUnit 4 Surefire Method-Before-Class Shape (Fixtures 6 & 7):**
   - *Signature:* `[ERROR] testMethodName(pkg.Class)  Time elapsed: ... <<< ERROR!`
   - *Impact:* `_SUREFIRE_FORM_A` expects `pkg.Class.methodName`; failure to match causes fallback Form D to attach method names to enclosing suite classes (`CoreTestSuite`).
   - *Resolution Plan:* Add dedicated regex for `methodName(pkg.Class)` with higher precedence than Form D.

2. **`src/parse/log_gradle.py` — S1 Multiline Attachment State Reset Bug (Fixture 9):**
   - *Signature:* In multi-failure blocks under a single class header, exception stack trace lines contain FQCNs that clear `current_class`.
   - *Impact:* First failure binds FQCN; subsequent failures in the same block emit bare method names.
   - *Resolution Plan:* Distinguish stack trace FQCN lines from genuine new class headers to preserve S1 state across the full failure block.

3. **`src/parse/log_pytest.py` — Thread Dump Interleaving under `pytest-timeout` (Fixture 1):**
   - *Signature:* Progress line `path/to/test.py::Class::method ++++ Timeout ++++` followed by 50+ lines of thread stack traces before `FAILED [ 99%]` and missing from `short test summary info`.
   - *Impact:* Extraction drops test ID and classification defaults to `NO_TEST_OUTPUT`.
   - *Resolution Plan:* Add multiline state-machine or `Timeout` header matching to pair timeout banners with subsequent `FAILED` indicators.

---

## 6. Step 5 — Test Suite Verification

Updated `tests/test_holdout_eval.py` with assertions for Fixtures 14 & 15 and updated aggregate metrics.

- **Predicted Test Count:** 289 baseline + 2 new = **291 passed**
- **Actual Test Count:** **291 passed in 46.10s**

```bash
$ uv run pytest -q
........................................................................ [ 24%]
........................................................................ [ 49%]
........................................................................ [ 74%]
........................................................................ [ 98%]
...                                                                      [100%]
291 passed in 46.10s
```
