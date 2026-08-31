# Phase 008B Report

## Per-Phase Pass/Fail
- **Phase 0:** PASS
- **Phase 1:** PASS
- **Phase 2:** PASS
- **Phase 3:** PASS
- **Phase 4:** PASS
- **Phase 5:** PASS
- **Phase 6:** PENDING (Waiting for operator signal)

## Scorer Accuracy Before/After
- **Logs Corpus:** Before 100.00% (40/40) | After 100.00% (40/40)
- **Holdout Corpus:** Before 100.00% (20/20) | After 100.00% (20/20)

## D-32 Text as Committed
```markdown
## D-32 — Parameterisation

The canonical `test_id` is the SELECTABLE UNIT: the method, or for Spock the feature method. The iteration or parameter set lives in `TestId.params`, never in the canonical id. A pytest `[2-3-5]`, a JUnit `[1]` and a Spock `@Unroll` iteration are the same construct.

**Consequence:** for holdout_v3 fixture 15 (graphql-java), the hand label naming the feature template `#scenario` was CORRECT and the parser emitting the leaf iteration `directives on every schema kind` was wrong. This overturns the session-060 audit verdict on that fixture.

**Limitation (Accepted):** The canonical id casefolds the Python path component, which is lossy on a case-sensitive filesystem. Accepted because two Python test files in one repo differing only in case is close to nonexistent.
```

## Holdout_v3 Amendments & Justifications
### Amendments (D-27)
- **Fixture 4 (apache/streampark)**: Amended expected outcomes from TEST_FAILURE to NO_TEST_OUTPUT. Justifying grep: `grep "Timed out waiting for container port to open" tests/fixtures/holdout_v3/apache__streampark__086548451141.txt`
- **Fixture 20 (apache/hertzbeat)**: Added explicit Expected Class TEST_RAN_CLEAN. Justifying grep: `grep "Tests run: 242" tests/fixtures/holdout_v3/apache__hertzbeat__089678606855.txt`
- **Fixture 23 (oracle/opengrok)**: Added explicit Expected Class TEST_RAN_CLEAN. Justifying grep: `grep "Tests run: 286" tests/fixtures/holdout_v3/oracle__opengrok__083435392401.txt`
- **Fixture 15 (graphql-java)**: NO CHANGE. Per D-32 the existing label is correct.

## Holdout_v3 Scoring Table
| Metric | As-Labelled (Frozen, First Scoring) | Post-Fix, Post-Amendment (This Scoring) |
| --- | --- | --- |
| Precision | 83.87% | 95.74% |
| Recall | 55.32% | 97.83% |
| F1 Score | 0.6667 | 0.9677 |
| Classification Accuracy | 76.67% (23/30) | 96.67% (29/30) |

### Partition Breakdown
- **Partition A (Maven, Gradle, Other):** Precision 93.55%, Recall 96.67%, Class Accuracy 96.00% (24/25)
- **Partition B (pytest logs):** Precision 100.00%, Recall 100.00%, Class Accuracy 100.00% (5/5)

## Measured Sizes (Phase 5c)
- `data/raw`: 4.6 GB
- `data/state/cursor.db`: 131 MB
- `data/interim/*.parquet`: ~31 MB total
- `data/clones`: 1.7 GB
- `data/frame`: 18 MB

## TASKS.md Counts
Corrected counts: **27 done, 91 open** (and 44 flagged as CUT).

## File Changes
**CREATED:**
- `docs/phase/008B-holdout-v3-final.md`
- `docs/SETUP.md`
- `docs/REPRODUCE.md`
- `docs/DATA_TRANSFER.md`
- `docs/phase/008B-REPORT.md`

**MODIFIED:**
- `analysis/fixture_score.py`
- `analysis/holdout_eval.py`
- `tests/test_fixture_score.py`
- `tests/fixtures/logs/EXPECTED.md`
- `tests/fixtures/holdout/EXPECTED.md`
- `tests/fixtures/holdout_v3/EXPECTED.md`
- `docs/DECISIONS.md`
- `docs/TASKS.md`

## Git Hashes
- **HEAD:** (Uncommitted)
- **origin/main:** e15aff4170de54ffedcfa0a735c6d233049987e3

## PREDICT vs ACTUAL & Hypothesis Verdicts
- **Hypothesis 1:** "Adding the Expected Class field will change dev-corpus and holdout-v2 classification accuracy away from 100%." -> **VERDICT: INCORRECT.** Both corpora remained at exactly 100.00% accuracy.
- **Hypothesis 2:** "Partition B may still score below 100% even after the xdist fix." -> **VERDICT: INCORRECT.** Partition B scored a perfect 100% precision and recall (16/16).
- **Hypothesis 3:** "`du -sh data/raw` may be large enough that physical transfer needs an external drive." -> **VERDICT: INCORRECT.** At 4.6GB, it can be easily transferred over the network.
- **Hypothesis 4:** "TASKS.md may have entries that no longer correspond to any roadmap task." -> **VERDICT: CORRECT.** 44 tasks in the Graph Layer and Predictor sections were flagged as `(CUT)`.
- **Test Counts:** PREDICTED 6 tests for `fixture_score` vs ACTUAL 6.
