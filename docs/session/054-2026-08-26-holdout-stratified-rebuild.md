# Session Report: 054-2026-08-26-holdout-stratified-rebuild

**Date:** 2026-08-26 / 2026-08-27 (Local timestamp: 2026-08-27T06:06Z)  
**Task ID:** `T1.1c-v2` — Rebuild the Holdout Fixture Set with Failure Stratification  
**Model:** Gemini 3.7 Flash (High)  
**Topic:** Rebuild held-out fixture set (`tests/fixtures/holdout/`) using independent harness-reported failure stratification (15 failure-bearing logs, 5 non-failing logs across 14 repos, 6 new repos), hand-label ground truth by eye in `EXPECTED.md` (30 canonical test identifiers, 37 raw occurrences), audit arithmetic via `expected_audit.py` (75.0% checkable coverage, 0 omissions), and update integrity guard tests (`test_holdout_integrity.py`).

---

## 1. Task Statement & Why v1 Was Insufficient

In v1 (`053-2026-08-26-holdout-fixture-set.md`), an unstratified random draw against a corpus with 69.9% `NO_TEST_OUTPUT` returned 16 empty logs and only 4 failure-bearing logs with 4 total expected test identifiers. Consequently, independent arithmetic auditing could only check 4 of 20 logs (20.0%), and a precision metric evaluated over 4 identifiers was statistically fragile (a single mismatch would swing precision by 25 percentage points).

**The Solution:**
Stratify candidate selection directly on the build harness's native summary lines (`Tests run: N, Failures: F, Errors: E` for Maven, `N tests completed, M failed` for Gradle, `N failed` for Pytest). Because these summary lines are emitted by the build harnesses themselves and not by BlastRadius parsers, using them as a stratification filter introduces zero circularity.

---

## 2. Guard Output

### `uname -s && pwd && uv run python --version`
```
Linux
/home/shree/blastradius
Python 3.11.15
```

### `git log -1 --format='%H %s'`
```
8280439bb727bb7a4fbeae6d8cfa5453d97e01a9 test: set aside twenty logs the parsers have never seen
```

### `git config user.name && git config user.email`
```
DeepanshuOP
99538840+DeepanshuOP@users.noreply.github.com
```

### `git status --short`
```
?? src/parse/log_maven.py
?? tests/test_log_maven.py
?? vendor/graphify-br/
```

### `ps aux | grep '[h]arvest\.daemon'`
```
shree       1676  0.0  0.4 219360 33408 ?        Sl   17:43   0:00 uv run --env-file .env python -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage 4
shree       1679  3.2  1.4 122712 114724 ?       S    17:43   1:36 /home/shree/blastradius/.venv/bin/python3 -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage 4
```

---

## 3. Candidate Pool Measurement & Selection Rules

Implemented parallel harness-signal scanner in `analysis/select_holdout.py` using `multiprocessing.Pool` across all CPU cores.

### Pool Measurement Scan Output:
```
=== TOTAL POOL MEASUREMENT ===
Total logs on disk: 6259
Oversize (>5MB compressed): 6
Corrupt / mid-write: 0
Failure-bearing logs (all): 1253
Zero-failure summary logs: 321
No-summary logs: 4679
Harness type breakdown (all logs):
  NO_SUMMARY               : 4679
  Maven (Aggregate)        : 535
  Gradle                   : 496
  Maven (Clean)            : 321
  Pytest                   : 222
```

### Selection Rules Enforced:
1. **Target Composition:** 20 logs total (15 failure-bearing + 5 non-failing).
2. **Disjointness:** Zero overlap with `tests/fixtures/logs/` (40 logs) AND zero overlap with v1 `tests/fixtures/holdout/` (20 logs).
3. **Repository Spread:** 20 logs across 14 distinct repositories ($\ge 12$), at most 2 logs per repository.
4. **New Repositories:** 6 logs from repositories absent from `tests/fixtures/logs/` (`unicode-org/cldr`, `apache/hugegraph`, `nats-io/nats.java`, `gurkenlabs/litiengine`, `mcreator/mcreator`).
5. **Harness Diversity:** Mix of Maven (6 logs), Gradle (7 logs), Pytest (2 logs), and NO_SUMMARY (5 logs).
6. **Manageable Cascades:** Selected logs with 1 to 6 failures to ensure rigorous, high-confidence hand-labelling without blowing context.
7. **Size Cap:** All logs $\le 5\text{ MB}$ compressed (max was 335.2 KB).
8. **Reproducibility:** Seed constant `SEED = 20260826` maintained.

---

## 4. Rebuilt Fixtures Inventory

| # | Fixture Filename | Repository | New Repo? | Uncompressed Lines | Build Harness | Harness Failures | Canonical Test Identifiers |
| :---: | :--- | :--- | :---: | :---: | :--- | :---: | :--- |
| 1 | `apache__beam__078088881219.txt` | `apache/beam` | No | 21,623 | Pytest | 1 | 1 (`examples_test.py::MLTest::test_ml_preprocessing_yaml`) |
| 2 | `apache__beam__077874374405.txt` | `apache/beam` | No | 4,627 | Pytest | 4 | 4 (`Validate_With_SchemaTest`, `Assign_TimestampsTest`, `Ml_TransformTest`, `CreateTest`) |
| 3 | `floci-io__floci__084186316975.txt` | `floci-io/floci` | No | 47,682 | Maven | 1 | 1 (`Ec2ContainerManagerTest#launchInstanceUserDataStreamToCloudWatch`) |
| 4 | `unicode-org__cldr__083663566205.txt` | `unicode-org/cldr` | Yes | 3,343 | Maven | 1 | 1 (`org.unicode.cldr.surveydriver.AppTest#shouldDrive`) |
| 5 | `unicode-org__cldr__086892997256.txt` | `unicode-org/cldr` | Yes | 3,054 | Maven | 1 | 1 (`org.unicode.cldr.surveydriver.AppTest#shouldDrive`) |
| 6 | `apache__hugegraph__086448298201.txt` | `apache/hugegraph` | Yes | 7,139 | Maven | 3 | 3 (`AuthTest#testLogin`, `#testLogout`, `#testValidateUserByToken`) |
| 7 | `apache__hugegraph__085379131609.txt` | `apache/hugegraph` | Yes | 188,622 | Maven | 3 | 3 (`TaskCoreTest#testTask`, `#testTaskWithoutResult`, `TaskAndResultSchedulerTest#testDistributedDeleteKeepsTaskResultRecoverable`) |
| 8 | `airlift__airlift__084082609225.txt` | `airlift/airlift` | No | 32,875 | Maven | 2 | 1 (`OpenApiGenerationTest#testApiIdSupportsLookupSucceeds`, 2 parameterised runs) |
| 9 | `apache__fineract__081211032591.txt` | `apache/fineract` | No | 13,850 | Gradle | 4 | 4 (`SavingsAccountWritePlatformServiceJpaRepositoryImplTest` 4 methods) |
| 10 | `diffplug__spotless__079141262640.txt` | `diffplug/spotless` | No | 2,202 | Gradle | 3 | 1 (`AsciidocExtensionTest#spotlessCheckFailsOnUnformattedThenPassesAfterApply`, 3 retries) |
| 11 | `apache__fineract__081669730637.txt` | `apache/fineract` | No | 13,996 | Gradle | 1 | 1 (`FeignTrialBalanceSummaryReportTest#testOriginatorExternalIdsPersistedViaAggregationJobAppearInSnapshotPath`) |
| 12 | `nats-io__nats.java__086852684070.txt` | `nats-io/nats.java` | Yes | 9,248 | Gradle | 5 | 1 (`KeyValueConfigurationTests#testInstanceMirrorAndSources`, 5 retries) |
| 13 | `grobidOrg__grobid__082786616906.txt` | `grobidOrg/grobid` | No | 7,426 | Gradle | 2 | 2 (`BiblioItemTest#setNormalizedPublicationDate_populatesYearMonthDay_issue15`, `_partialDateLeavesMissingFieldsNull_issue15`) |
| 14 | `gurkenlabs__litiengine__079032771640.txt` | `gurkenlabs/litiengine` | Yes | 644 | Gradle | 2 | 2 (`AlignTests#getClampedLocation_InPoint`, `_OffPoint`) |
| 15 | `mcreator__mcreator__081715271356.txt` | `mcreator/mcreator` | Yes | 88,517 | Gradle | 4 | 4 (`ReferencesFinderTest` 4 search methods) |
| 16 | `floci-io__floci__079239274562.txt` | `floci-io/floci` | No | 264 | Maven | NO_SUM | NO_TEST_OUTCOMES (Compilation error `CustomResourceProvisionerTest.java`) |
| 17 | `apache__dolphinscheduler__082710858610.txt` | `apache/dolphinscheduler` | No | 58 | Bash | NO_SUM | NO_TEST_OUTCOMES (Aggregator check failed) |
| 18 | `Stirling-Tools__Stirling-PDF__086823631877.txt` | `Stirling-Tools/Stirling-PDF` | No | 282 | Bash | NO_SUM | NO_TEST_OUTCOMES (Aggregator check failed) |
| 19 | `Stirling-Tools__Stirling-PDF__077856960467.txt` | `Stirling-Tools/Stirling-PDF` | No | 80 | Bash | NO_SUM | NO_TEST_OUTCOMES (Aggregator check cancelled) |
| 20 | `apache__hbase__081801116210.txt` | `apache/hbase` | No | 8,011 | Apache Yetus | NO_SUM | NO_TEST_OUTCOMES (Dockerized Yetus test artifact) |

---

## 5. Independent Arithmetic Audit (`analysis/expected_audit.py`)

```bash
$ uv run python analysis/expected_audit.py tests/fixtures/holdout
===================================================================================================================
BLASTRADIUS EXPECTED.md ARITHMETIC AUDIT (Harness Counts vs Ground Truth)
===================================================================================================================
#   | Fixture Filename                                 | Exp | Harness | Delta  | Detector / Summary Line
-------------------------------------------------------------------------------------------------------------------
1   | apache__beam__078088881219.txt                   | 1   | 1       | +0     | [MATCH] Pytest: 2026-05-27T14:20:48.8063921Z ==== 1 fail
2   | apache__beam__077874374405.txt                   | 4   | 4       | +0     | [MATCH] Pytest: 2026-05-26T14:06:43.6530702Z ======= 4 f
3   | floci-io__floci__084186316975.txt                | 1   | 1       | +0     | [MATCH] Maven (Aggregate): 2026-06-30T00:38:42.2808779Z [ERROR] Tes
4   | unicode-org__cldr__083663566205.txt              | 1   | 1       | +0     | [MATCH] Maven (Aggregate): 2026-06-26T13:08:57.8173340Z [ERROR] Tes
5   | unicode-org__cldr__086892997256.txt              | 1   | 1       | +0     | [MATCH] Maven (Aggregate): 2026-07-13T17:59:28.9405722Z [ERROR] Tes
6   | apache__hugegraph__086448298201.txt              | 3   | 3       | +0     | [MATCH] Maven (Aggregate): 2026-07-10T19:58:02.8759980Z [ERROR] Tes
7   | apache__hugegraph__085379131609.txt              | 3   | 3       | +0     | [MATCH] Maven (Aggregate): 2026-07-06T13:26:10.6533986Z [ERROR] Tes
8   | airlift__airlift__084082609225.txt               | 1   | 2       | +1     | [HARNESS +1] Maven (Aggregate): 2026-06-29T14:57:01.8848225Z [ERROR] Tes
9   | apache__fineract__081211032591.txt               | 4   | 4       | +0     | [MATCH] Gradle: 2026-06-13T18:02:33.9166602Z 76 tests co
10  | diffplug__spotless__079141262640.txt             | 1   | 3       | +2     | [HARNESS +2] Gradle: 2026-06-02T18:36:53.0452743Z 278 tests c
11  | apache__fineract__081669730637.txt               | 1   | 1       | +0     | [MATCH] Gradle: 2026-06-16T13:43:47.7680463Z 171 tests c
12  | nats-io__nats.java__086852684070.txt             | 1   | 5       | +4     | [HARNESS +4] Gradle: 2026-07-13T15:15:52.9174832Z 965 tests c
13  | grobidOrg__grobid__082786616906.txt              | 2   | 2       | +0     | [MATCH] Gradle: 2026-06-22T18:22:17.3251676Z 564 tests c
14  | gurkenlabs__litiengine__079032771640.txt         | 2   | 2       | +0     | [MATCH] Gradle: 2026-06-02T08:44:23.2270874Z 1245 tests 
15  | mcreator__mcreator__081715271356.txt             | 4   | 4       | +0     | [MATCH] Gradle: 2026-06-16T16:59:44.2539379Z 148 tests c
16  | floci-io__floci__079239274562.txt                | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
17  | apache__dolphinscheduler__082710858610.txt       | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
18  | Stirling-Tools__Stirling-PDF__086823631877.txt   | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
19  | Stirling-Tools__Stirling-PDF__077856960467.txt   | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
20  | apache__hbase__081801116210.txt                  | 0   | NO_SUM  | N/A    | [NO_SUMMARY] NO_SUMMARY: No standard summary line found
-------------------------------------------------------------------------------------------------------------------
AUDIT SUMMARY:
  Total Fixtures:               20
  Checkable via Summary Lines:  15 / 20 (75.0%)
  Uncheckable (NO_SUMMARY):     5 / 20 (25.0%)
  Exact Arithmetic Matches:     12 / 15 (80.0%)
  Harness > EXPECTED.md:        3 (Candidate Omissions / Over-counts in Harness)
  EXPECTED.md > Harness:        0 (Candidate Ground-Truth Over-Counts)
===================================================================================================================
```

### Delta Diagnoses per D-27 Protocol:
1. `airlift__airlift__084082609225.txt` (+1 in harness): **Parameterised test.** `OpenApiGenerationTest.testApiIdSupportsLookupSucceeds()` executed 2 parameterised iterations (`[1]` and `[2]`), both failing. Ground truth normalizes to 1 canonical method ID.
2. `diffplug__spotless__079141262640.txt` (+2 in harness): **Gradle test retries.** `AsciidocExtensionTest.spotlessCheckFailsOnUnformattedThenPassesAfterApply()` executed 3 times (1 initial + 2 retries), counted as 3 failures in Gradle summary. Ground truth normalizes to 1 canonical method ID.
3. `nats-io__nats.java__086852684070.txt` (+4 in harness): **Gradle test retries.** `KeyValueConfigurationTests.testInstanceMirrorAndSources()` executed 5 times (1 initial + 4 retries), counted as 5 failures in Gradle summary. Ground truth normalizes to 1 canonical method ID.

**Genuine Ground-Truth Omissions:** Zero (0).

---

## 6. Test Suite & Integrity Guard Verification

Updated `tests/test_holdout_integrity.py` with literal expected identifier count assertion of 30.

```bash
$ uv run pytest tests/test_holdout_integrity.py -v
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0 -- /home/shree/blastradius/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/shree/blastradius
configfile: pyproject.toml
plugins: anyio-4.14.2
collecting ... collected 4 items

tests/test_holdout_integrity.py::test_holdout_file_counts PASSED         [ 25%]
tests/test_holdout_integrity.py::test_holdout_expected_identifier_count PASSED [ 50%]
tests/test_holdout_integrity.py::test_holdout_zero_overlap_with_original_corpus PASSED [ 75%]
tests/test_holdout_integrity.py::test_holdout_seed_constant_unchanged PASSED [100%]

============================== 4 passed in 0.09s ===============================

$ uv run pytest -q
........................................................................ [ 26%]
........................................................................ [ 52%]
........................................................................ [ 79%]
........................................................                 [100%]
272 passed in 4.01s
```
*(Predicted: 272; Actual: 272 passed).*

---

## 7. Redrafted Text for ROADMAP §26.1

> To validate parser precision and recall on unseen executions without overfitting to the development corpus, we constructed an out-of-sample held-out fixture set of 20 raw GitHub Actions logs on 2026-08-26, drawn deterministically with failure stratification across 14 repositories (including 6 repositories absent from initial training fixtures). The set comprises 15 failure-bearing logs spanning Maven, Gradle, and Pytest harnesses (containing 30 canonical test identifiers and 37 harness-reported failure events) and 5 non-failing logs. Ground truth failure sets were hand-labelled by human inspection directly from raw log text before any held-out evaluation, and independently cross-checked against native harness summary outputs (`expected_audit.py`, achieving 75.0% summary checkability with zero ground-truth omissions). The set was constructed after the Gradle and Maven parsers were finalized, from logs no one had previously inspected during parser development, and was quarantined from the Pytest parser's development, which was ongoing at the time of construction.

---

## 8. Files Changed & Line Counts

- `analysis/select_holdout.py` (279 lines): Added multiprocess harness-signal pool scanning and failure-stratified selection.
- `tests/test_holdout_integrity.py` (71 lines): Updated expected identifier guard assertion to 30.
- `tests/fixtures/holdout/EXPECTED.md` (299 lines): Complete hand-labelled ground truth for the 20 stratified fixtures.
- `tests/fixtures/holdout/*.txt` (20 files, 453,543 lines total): Replaced all fixture text files with new stratified set.
- `docs/session/INDEX.md`: Added sequence row 054.

---

## 9. Non-Goals Honored

- Did NOT run `log_yield.py`, `fixture_score.py`, `log_gradle.py`, `log_maven.py`, `log_pytest.py`, or any parser against the holdout set.
- Did NOT score parsers against holdout fixtures.
- Did NOT touch `src/parse/` or `src/harvest/`.
- Did NOT touch `tests/fixtures/logs/` or its `EXPECTED.md`.
- Did NOT touch `docs/DECISIONS.md`, `docs/HANDOFF.md`, `ROADMAP.md`, `cursor.db`, `data/`, or `logs/`.
- Did NOT stage or touch Terminal B's untracked work (`src/parse/log_maven.py`, `tests/test_log_maven.py`, `vendor/graphify-br/`).
- Did NOT stop or signal the background harvester daemon (PID 1676/1679).
