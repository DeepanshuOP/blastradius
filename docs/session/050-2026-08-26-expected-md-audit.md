# Session Report: EXPECTED.md Ground-Truth Audit, Decision D-27, and Corpus Re-Scoring

**Task ID:** T1.1a / ROADMAP §25.3 / §9.1  
**Date:** 2026-08-26  
**Author:** Terminal B  
**Target File:** `docs/session/050-2026-08-26-expected-md-audit.md`

---

## 1. Task Statement & Background

**Task:** Amend `tests/fixtures/logs/EXPECTED.md` for fixture 10 (`apache__flink__079848838447.txt`), record decision **D-27** in `docs/DECISIONS.md`, draft paper internal validity text for ROADMAP §26.1, add regression tests, and re-score the 40-log fixture corpus without changing extractor code.

**Background:**
During the extractor precision evaluation against the 40 hand-labelled fixtures, fixture 10 appeared as 1 False Positive (`org.apache.flink.test.runtime.IPv6HostnamesITCase#testClusterWithIPv6host`). An arithmetic audit script (`analysis/expected_audit.py`) comparing test harness summary lines (Surefire, Gradle, Pytest) against `EXPECTED.md` revealed that Maven Surefire reported `Tests run: 856, Failures: 1, Errors: 1` on line 7786. Inspection of raw log lines 7291, 7292, and 7784 confirmed that `IPv6HostnamesITCase` is a genuine failure block that was omitted during initial manual hand-labelling.

Three other deltas identified by the harness audit (Airlift #18, TheAlgorithms #40, Spotless #23) were verified as valid non-omissions: parameterized test executions counted multiple times by the harness, and Gradle runner retries (3 tests x 3 attempts = 9 failures), all collapsing to single canonical test identifiers per D-25.

---

## 2. Guard & Environment Verification

### Command:
```bash
uname -s && pwd && uv run python --version
```
### Raw Output:
```
Linux
/home/shree/blastradius
Python 3.11.15
```

### Command:
```bash
git log -1 --format='%H %s' && git config user.name && git config user.email && git status --short
```
### Raw Output:
```
31d8f2bf61c73bf4626042f160714f5140192145 fix: extract real test names instead of classes and build tasks
DeepanshuOP
99538840+DeepanshuOP@users.noreply.github.com
?? analysis/expected_audit.py
?? vendor/graphify-br/
```

---

## 3. Ground-Truth Arithmetic Audit Table

### Command:
```bash
uv run python analysis/expected_audit.py
```
### Raw Output (Post-Amendment):
```
===================================================================================================================
BLASTRADIUS EXPECTED.md ARITHMETIC AUDIT (Harness Counts vs Ground Truth)
===================================================================================================================
#   | Fixture Filename                                 | Exp | Harness | Delta  | Detector / Summary Line
-------------------------------------------------------------------------------------------------------------------
1   | apache__beam__077621011187.txt                   | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
2   | apache__beam__077630056646.txt                   | 1   | 1       | +0     | [MATCH] Gradle: 2026-05-24T22:03:17.8203063Z 356 tests c
3   | apache__beam__082575659629.txt                   | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
4   | apache__beam__082592431584.txt                   | 8   | 8       | +0     | [MATCH] Pytest: 2026-06-21T18:29:46.6227577Z ====== 8 fa
5   | apache__beam__086455350919.txt                   | 2   | 2       | +0     | [MATCH] Gradle: 2026-07-10T20:18:01.0337272Z 2 tests com
6   | apache__dolphinscheduler__083801509824.txt       | 1   | 1       | +0     | [MATCH] Maven (Aggregate): 2026-06-27T07:41:41.2109509Z [ERROR] Tes
7   | apache__fineract__080132127199.txt               | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
8   | apache__fineract__083161294301.txt               | 1   | 1       | +0     | [MATCH] Gradle: 2026-06-24T10:02:04.2681282Z 83 tests co
9   | apache__flink__079221420559.txt                  | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
10  | apache__flink__079848838447.txt                  | 2   | 2       | +0     | [MATCH] Maven (Aggregate): 2026-06-06T04:33:52.0506117Z Jun 06 04:3
11  | apache__hbase__078892029185.txt                  | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
12  | apache__hbase__082907939305.txt                  | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
13  | apache__hbase__083382132597.txt                  | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
14  | apache__hbase__084057821217.txt                  | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
15  | apache__zeppelin__079328560137.txt               | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
16  | apache__zeppelin__084837475646.txt               | 1   | 1       | +0     | [MATCH] Maven (Aggregate): 2026-07-02T17:52:56.1335585Z [ERROR] Tes
17  | airlift__airlift__081878478589.txt               | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
18  | airlift__airlift__084082609180.txt               | 1   | 2       | +1     | [HARNESS +1] Maven (Aggregate): 2026-06-29T14:54:46.4406741Z [ERROR] Tes
19  | apple__servicetalk__085939947321.txt             | 1   | 1       | +0     | [MATCH] Gradle: 2026-07-08T17:45:14.0433504Z 3285 tests 
20  | baomidou__mybatis-plus__085831964676.txt         | 1   | 1       | +0     | [MATCH] Gradle: 2026-07-08T09:18:40.8038107Z 184 tests c
21  | crimera__piko__083277376521.txt                  | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
22  | diffplug__spotless__077697425370.txt             | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
23  | diffplug__spotless__086063491051.txt             | 3   | 9       | +6     | [HARNESS +6] Gradle: 2026-07-09T07:43:06.2679206Z 328 tests c
24  | floci-io__floci__081814559712.txt                | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
25  | floci-io__floci__082492942956.txt                | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
26  | floci-io__floci__084479785666.txt                | 1   | 1       | +0     | [MATCH] Maven (Aggregate): 2026-07-01T07:52:00.1246165Z [ERROR] Tes
27  | grobidOrg__grobid__085264981989.txt              | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
28  | jhipster__prettier-java__084966237571.txt        | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
29  | openremote__openremote__082946004526.txt         | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
30  | openremote__openremote__084103046129.txt         | 1   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
31  | opentripplanner__opentripplanner__077860984374.txt | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
32  | opentripplanner__opentripplanner__077865124037.txt | 4   | 4       | +0     | [MATCH] Maven (Aggregate): 2026-05-26T12:57:58.6730774Z [ERROR] Tes
33  | sirixdb__sirix__079909436297.txt                 | 6   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
34  | sirixdb__sirix__086198357085.txt                 | 1   | 1       | +0     | [MATCH] Gradle: 2026-07-09T18:40:35.7943450Z 1345 tests 
35  | spiculedata__saiku__080014373865.txt             | 0   | 0       | +0     | [MATCH] Maven (Clean): 2026-06-08T02:48:51.8884710Z [WARNING] T
36  | spiculedata__saiku__082534301666.txt             | 8   | 8       | +0     | [MATCH] Maven (Aggregate): 2026-06-21T02:30:57.3468054Z [ERROR] Tes
37  | Stirling-Tools__Stirling-PDF__077860967858.txt   | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
38  | Stirling-Tools__Stirling-PDF__081016086095.txt   | 1   | 1       | +0     | [MATCH] Gradle: 2026-06-12T11:17:51.0108050Z [backend:bu
39  | Stirling-Tools__Stirling-PDF__085817860968.txt   | 1   | 1       | +0     | [MATCH] Gradle: 2026-07-08T08:05:31.8682182Z [backend:bu
40  | thealgorithms__java__080494921200.txt            | 1   | 2       | +1     | [HARNESS +1] Maven (Aggregate): 2026-06-10T06:25:01.1582860Z [ERROR] Tes
--------------------------------------------------------------------------------------------------------------
AUDIT SUMMARY:
  Total Fixtures:               40
  Checkable via Summary Lines:  19 / 40 (47.5%)
  Uncheckable (NO_SUMMARY):     21 / 40 (52.5%)
  Exact Arithmetic Matches:     16 / 19 (84.2%)
  Harness > EXPECTED.md:        3 (Candidate Omissions / Over-counts in Harness)
  EXPECTED.md > Harness:        0 (Candidate Ground-Truth Over-Counts)
===================================================================================================================
```

---

## 4. Decision Record D-27

Recorded in `docs/DECISIONS.md`:

```markdown
| **D-27** | EXPECTED.md amendment protocol & ground-truth validation | **EXPECTED.md may be amended only with recorded evidence from a source independent of any BlastRadius extractor — harness-reported counts, or a human reading raw log text. Never amend EXPECTED.md to make a parser's output match.** (a) **Candidate vs Confirmed Omission:** A test harness summary count exceeding EXPECTED.md is a candidate omission, not a confirmed one. Parameterised executions (fixture 18 Airlift x2, fixture 40 TheAlgorithms x2) and runner retries (fixture 23 Spotless 3 tests x 3 attempts = 9 failures) legitimately cause harness counts to exceed distinct test counts; these collapse to single canonical test identifiers per D-25. Only a case with a distinct method or failure block absent from EXPECTED.md (e.g. fixture 10 Flink IPv6HostnamesITCase#testClusterWithIPv6host) constitutes a confirmed omission. (b) **Measured hand-labelling miss rate:** Exactly 1 omission was detected across the 19 checkable log fixtures in the 40-log corpus (1/19 = 5.26% log miss rate; 1 omitted test out of 46 total = 2.17% identifier miss rate); 0 over-counts were detected (EXPECTED.md never exceeded harness counts). (c) **Audit coverage and limits:** 19/40 logs (47.5%) are checkable via explicit harness summary lines (Maven aggregate/class lines, Gradle summary lines, Pytest footer lines); 21/40 logs (52.5%) are uncheckable (NO_SUMMARY) due to pre-test CI setup/infrastructure failures or runners that omit aggregate counts. Crucially, test-bearing fixtures 30 (OpenRemote Spock narrative tests, 1 test) and 33 (SirixDB Kotlin Native smoke tests, 6 tests) carry 7 expected identifiers that NO independent harness summary check has ever confirmed. This audit limitation is an explicit residual risk for parser evaluation. (d) **Revisit trigger:** Any future harness-count delta observed during log audit or parser evaluation that is not fully explained by parameterisation or retry. | one-way for amendment rules; two-way for specific fixture corrections with documented independent evidence | Any future harness-count delta that is not explained by parameterisation or retry, or when new parsers cover previously uncheckable log formats |
```

---

## 5. Paper Consequence Draft (ROADMAP §26.1 Internal Validity)

*Draft paragraph prepared for paper §VI / ROADMAP §26.1:*

> **Threats to Internal Validity — Ground-Truth Label Integrity & Parser Evaluation:**  
> Ground-truth labels for the 40-log benchmark fixture corpus were constructed through manual inspection of raw console logs prior to parser implementation. To mitigate human labelling omissions, we cross-validated hand-labelled expectations against test harness aggregate outcome reports (Maven Surefire module summaries, Gradle execution tallies, and Pytest summary footers) across the 19 fixtures containing machine-readable harness summaries. The audit identified exactly one hand-labelling omission (a Surefire error block in Apache Flink omitted from fixture 10, representing a 2.17% test-level miss rate [1/46] and a 5.26% log-level miss rate [1/19]), which was corrected with line-number provenance under a strict change protocol (Decision D-27). No false positives or over-counts were found in the hand-labelled set. A residual threat remains for the 21 fixtures without standard summary footers—notably Spock (fixture 30) and Kotlin Native (fixture 33) test logs containing 7 distinct identifiers—where no automated harness cross-check is possible and ground truth rests exclusively on manual verification.

---

## 6. Scorecard Re-Evaluation (Post-Amendment)

### Predicted vs. Actual Metrics:
| Metric | Predicted | Actual | Status |
| :--- | :--- | :--- | :--- |
| **True Positives (TP)** | 34 | 34 | Match |
| **False Positives (FP)** | 0 | 0 | Match |
| **False Negatives (FN)** | 12 | 12 | Match |
| **Expected Identifiers** | 46 | 46 | Match |
| **Extracted Identifiers** | 34 | 34 | Match |
| **Precision** | **1.0000 (100.00%)** | **1.0000 (100.00%)** | Match |
| **Recall** | **0.7391 (73.91%)** | **0.7391 (73.91%)** | Match |
| **F1 Score** | 0.8500 | 0.8500 | Match |
| **Classification Accuracy** | 0.9500 (38/40) | 0.9500 (38/40) | Match |

### Command:
```bash
uv run python analysis/fixture_score.py
```
### Raw Output:
```
==============================================================================================================
BLASTRADIUS FIXTURE CORPUS SCORECARD (T1.1a Evaluation)
==============================================================================================================
Normalization Rule: Strip trailing '()', replace '#' and ' > ' with '::' on both expected and extracted IDs.
--------------------------------------------------------------------------------------------------------------
#   | Fixture Filename                                 | Exp Class   | Act Class   | Exp | Ext | TP  | FP  | FN  | Match
--------------------------------------------------------------------------------------------------------------
1   | apache__beam__077621011187.txt                   | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
2   | apache__beam__077630056646.txt                   | TEST_FAILURE | TEST_FAILURE | 1   | 1   | 1   | 0   | 0   | OK
3   | apache__beam__082575659629.txt                   | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
4   | apache__beam__082592431584.txt                   | TEST_FAILURE | TEST_FAILURE | 8   | 8   | 8   | 0   | 0   | OK
5   | apache__beam__086455350919.txt                   | TEST_FAILURE | TEST_FAILURE | 2   | 2   | 2   | 0   | 0   | OK
6   | apache__dolphinscheduler__083801509824.txt       | TEST_FAILURE | TEST_FAILURE | 1   | 1   | 1   | 0   | 0   | OK
7   | apache__fineract__080132127199.txt               | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
8   | apache__fineract__083161294301.txt               | TEST_FAILURE | TEST_FAILURE | 1   | 0   | 0   | 0   | 1   | DIFF
9   | apache__flink__079221420559.txt                  | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
10  | apache__flink__079848838447.txt                  | TEST_FAILURE | TEST_FAILURE | 2   | 2   | 2   | 0   | 0   | OK
11  | apache__hbase__078892029185.txt                  | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
12  | apache__hbase__082907939305.txt                  | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
13  | apache__hbase__083382132597.txt                  | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
14  | apache__hbase__084057821217.txt                  | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
15  | apache__zeppelin__079328560137.txt               | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
16  | apache__zeppelin__084837475646.txt               | TEST_FAILURE | TEST_FAILURE | 1   | 1   | 1   | 0   | 0   | OK
17  | airlift__airlift__081878478589.txt               | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
18  | airlift__airlift__084082609180.txt               | TEST_FAILURE | TEST_FAILURE | 1   | 1   | 1   | 0   | 0   | OK
19  | apple__servicetalk__085939947321.txt             | TEST_FAILURE | TEST_FAILURE | 1   | 1   | 1   | 0   | 0   | OK
20  | baomidou__mybatis-plus__085831964676.txt         | TEST_FAILURE | TEST_FAILURE | 1   | 1   | 1   | 0   | 0   | OK
21  | crimera__piko__083277376521.txt                  | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
22  | diffplug__spotless__077697425370.txt             | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
23  | diffplug__spotless__086063491051.txt             | TEST_FAILURE | TEST_FAILURE | 3   | 0   | 0   | 0   | 3   | DIFF
24  | floci-io__floci__081814559712.txt                | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
25  | floci-io__floci__082492942956.txt                | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
26  | floci-io__floci__084479785666.txt                | TEST_FAILURE | TEST_FAILURE | 1   | 1   | 1   | 0   | 0   | OK
27  | grobidOrg__grobid__085264981989.txt              | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
28  | jhipster__prettier-java__084966237571.txt        | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
29  | openremote__openremote__082946004526.txt         | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
30  | openremote__openremote__084103046129.txt         | TEST_FAILURE | NO_TEST_OUTPUT | 1   | 0   | 0   | 0   | 1   | DIFF
31  | opentripplanner__opentripplanner__077860984374.txt | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
32  | opentripplanner__opentripplanner__077865124037.txt | TEST_FAILURE | TEST_FAILURE | 4   | 4   | 4   | 0   | 0   | OK
33  | sirixdb__sirix__079909436297.txt                 | TEST_FAILURE | NO_TEST_OUTPUT | 6   | 0   | 0   | 0   | 6   | DIFF
34  | sirixdb__sirix__086198357085.txt                 | TEST_FAILURE | TEST_FAILURE | 1   | 1   | 1   | 0   | 0   | OK
35  | spiculedata__saiku__080014373865.txt             | TEST_RAN_CLEAN | TEST_RAN_CLEAN | 0   | 0   | 0   | 0   | 0   | OK
36  | spiculedata__saiku__082534301666.txt             | TEST_FAILURE | TEST_FAILURE | 8   | 8   | 8   | 0   | 0   | OK
37  | Stirling-Tools__Stirling-PDF__077860967858.txt   | NO_TEST_OUTPUT | NO_TEST_OUTPUT | 0   | 0   | 0   | 0   | 0   | OK
38  | Stirling-Tools__Stirling-PDF__081016086095.txt   | TEST_FAILURE | TEST_FAILURE | 1   | 1   | 1   | 0   | 0   | OK
39  | Stirling-Tools__Stirling-PDF__085817860968.txt   | TEST_FAILURE | TEST_FAILURE | 1   | 0   | 0   | 0   | 1   | DIFF
40  | thealgorithms__java__080494921200.txt            | TEST_FAILURE | TEST_FAILURE | 1   | 1   | 1   | 0   | 0   | OK
--------------------------------------------------------------------------------------------------------------
CORPUS TOTALS & METRICS:
  Total Fixtures:              40
  Total Expected Identifiers:  46
  Total Extracted Identifiers: 34
  True Positives (TP):         34
  False Positives (FP):        0
  False Negatives (FN):        12
  Precision:                   1.0000 (100.00%)
  Recall:                      0.7391 (73.91%)
  F1 Score:                    0.8500
  Classification Accuracy:     0.9500 (95.00%) [38/40]
  No-Failure Fixtures with FP: 0/20
==============================================================================================================
```

### Command:
```bash
uv run python analysis/fixture_score.py --show-errors
```
### Raw Output:
```
==============================================================================================================
DETAILED ERROR BREAKDOWN (FALSE POSITIVES & FALSE NEGATIVES)
==============================================================================================================

[8] apache__fineract__083161294301.txt (Confidence: AMBIGUOUS)
    Expected (1):  ['org.apache.fineract.integrationtests.cob.CobPartitioningTest::testLoanCOBPartitioningQuery']
    Extracted (0): []
    FN (1):        ['org.apache.fineract.integrationtests.cob.CobPartitioningTest::testLoanCOBPartitioningQuery']

[23] diffplug__spotless__086063491051.txt (Confidence: CERTAIN)
    Expected (3):  ['com.diffplug.spotless.rdf.RdfFormatterTest::blankNodeOrderingIsNotStableInCoolRdfFormatter_2_0_0', 'com.diffplug.spotless.rdf.RdfFormatterTest::testCoolRdfFormatter_2_0_0_DefaultStyle', 'com.diffplug.spotless.rdf.RdfFormatterTest::testCoolRdfFormatter_2_0_0_style01']
    Extracted (0): []
    FN (3):        ['com.diffplug.spotless.rdf.RdfFormatterTest::blankNodeOrderingIsNotStableInCoolRdfFormatter_2_0_0', 'com.diffplug.spotless.rdf.RdfFormatterTest::testCoolRdfFormatter_2_0_0_DefaultStyle', 'com.diffplug.spotless.rdf.RdfFormatterTest::testCoolRdfFormatter_2_0_0_style01']

[30] openremote__openremote__084103046129.txt (Confidence: AMBIGUOUS)
    Expected (1):  ['org.openremote.test.assets.ApplyPredictedDataPointsServiceTest::Does not emit attribute events after asset deletion']
    Extracted (0): []
    FN (1):        ['org.openremote.test.assets.ApplyPredictedDataPointsServiceTest::Does not emit attribute events after asset deletion']

[33] sirixdb__sirix__079909436297.txt (Confidence: AMBIGUOUS)
    Expected (6):  ['io.sirix.cli.NativeImageSmokeTest::Basic arithmetic query', 'io.sirix.cli.NativeImageSmokeTest::Conditional expression', 'io.sirix.cli.NativeImageSmokeTest::FLWOR expression', 'io.sirix.cli.NativeImageSmokeTest::Let expression with computation', 'io.sirix.cli.NativeImageSmokeTest::Sequence operations', 'io.sirix.cli.NativeImageSmokeTest::String manipulation query']
    Extracted (0): []
    FN (6):        ['io.sirix.cli.NativeImageSmokeTest::Basic arithmetic query', 'io.sirix.cli.NativeImageSmokeTest::Conditional expression', 'io.sirix.cli.NativeImageSmokeTest::FLWOR expression', 'io.sirix.cli.NativeImageSmokeTest::Let expression with computation', 'io.sirix.cli.NativeImageSmokeTest::Sequence operations', 'io.sirix.cli.NativeImageSmokeTest::String manipulation query']

[39] Stirling-Tools__Stirling-PDF__085817860968.txt (Confidence: AMBIGUOUS)
    Expected (1):  ['WebMvcConfig::registers all five resource handler groups']
    Extracted (0): []
    FN (1):        ['WebMvcConfig::registers all five resource handler groups']
==============================================================================================================
```

---

## 7. Test Suite Execution

### Command:
```bash
uv run pytest -q
```
### Raw Output:
```
........................................................................ [ 30%]
........................................................................ [ 61%]
........................................................................ [ 91%]
...................                                                      [100%]
235 passed in 3.05s
```
- **Predicted:** 235 passed (Baseline 233 + 2 new tests).
- **Actual:** 235 passed.

---

## 8. Files Changed & Line Counts

- `tests/fixtures/logs/EXPECTED.md`: +4 lines in §10 only.
- `docs/DECISIONS.md`: +1 line (D-27 decision record).
- `analysis/expected_audit.py`: Untracked script created to audit harness counts (245 lines).
- `tests/test_log_yield.py`: +20 lines (2 regression tests: Flink fixture 10 dual extraction, EXPECTED.md 46-identifier assertion).
- `docs/session/050-2026-08-26-expected-md-audit.md`: Session report.
- `docs/session/INDEX.md`: +1 line for sequence 050.

---

## 9. Non-Goals Honoured & Invariants Preserved

- `src/harvest/` untouched.
- `data/` and `logs/` untouched.
- No background processes or ManageTask polling used.
- No external web search or URL fetches performed.
- No trailers (`Co-Authored-By`, `Claude-Session`) added.
- `EXPECTED.md` entries outside §10 left completely unmodified.
- `docs/HANDOFF.md` left untouched.
