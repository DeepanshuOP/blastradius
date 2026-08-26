# Session Report: Extractor Precision Measurement & Surefire / Gradle Fixes

**Task ID:** T1.1a / ROADMAP §25.3  
**Date:** 2026-08-26  
**Author:** Terminal B  
**Target File:** `docs/session/049-2026-08-26-extractor-precision.md`

---

## 1. Executive Summary & Delta

Against the 40-log hand-labelled ground truth fixture corpus (`tests/fixtures/logs/EXPECTED.md`):

| Metric | Baseline (Pre-Fix) | Post-Fix | Delta | ROADMAP §25.3 Target |
| :--- | :--- | :--- | :--- | :--- |
| **Precision** | **42.86%** (15 TP / 35 Ext) | **97.06%** (33 TP / 34 Ext) | **+54.20%** | $\ge 95.0\%$ (**MET**) |
| **Recall** | **33.33%** (15 TP / 45 Exp) | **73.33%** (33 TP / 45 Exp) | **+40.00%** | — |
| **F1 Score** | **0.3750** | **0.8354** | **+0.4604** | — |
| **Classification Accuracy** | **95.00%** (38 / 40) | **95.00%** (38 / 40) | $0.0\%$ | — |
| **No-Failure Fixtures with FP** | **0 / 20** | **0 / 20** | $0$ | 0 |

### Critical Finding on Previously Reported Metrics
The previously reported corpus-wide figure of **3,251 distinct failing identifiers** was produced by the 42.86%-precision baseline extractor. It is **not a floor**; it was a substantial mismeasurement caused by:
1. **D1 (Class Granularity Collapse)**: Maven `<<< FAILURE! ... in FQN` emitted class-level identifiers rather than test methods, collapsing multiple failures into class names and causing false positives.
2. **D2 (Phantom Gradle Identifiers)**: `> Task :x:test FAILED` manufactured build target strings (e.g. `:mybatis-plus-core:test`, `***-pdf:test`) as fake test identifiers.

Removing the Gradle task pattern eliminates phantom identifiers in exchange for true precision. Full corpus re-measurement will take place in a separate dedicated run.

---

## 2. Defects Identified & Implemented Solutions

1. **ANSI Escape Stripping**: 35 of the 40 raw logs contain ANSI escape sequences (e.g. 2,839 in OTP). Stripping ANSI sequences via `_ANSI_RE` before line filtering and regex matching unblocks clean extraction across all builds.
2. **FAIL_KEYWORDS Gate**: Added `[ERROR]  ` (with 2 spaces) to admit Surefire 3.x summary lines while strictly rejecting single-spaced noise like `[ERROR] Tests run:` or `[ERROR] Failed to execute goal`.
3. **Surefire Forms A, B, C, D & Parameter Collapse**:
   - **FORM A**: Captures `(pkg.Class, method)` while stripping parameter types and parameter indices (`[1]`, `[2]`), collapsing parameterized tests (e.g., Airlift #18, TheAlgorithms #40) to single canonical IDs.
   - **FORM B**: Captures dotted package FQNs from `<<< FAILURE! ... in pkg.Class`.
   - **FORM C**: Captures short `(Class, method)` summaries from `[ERROR]   Class.method:LINE`.
   - **FORM D**: Captures bare methods `[ERROR] method  Time elapsed: ...` (DolphinScheduler #6).
4. **D2 Gradle Task Elimination**: Removed `>\s*Task\s+:.*test.*FAILED` from `TEST_ID_PATTERNS`.
5. **Two-Pass Join & Deduplication Rule**:
   - Gathers all known FQN classes across FORM A and FORM B.
   - Reconciles short `(Class, method)` summaries into `pkg.Class::method` without consuming the class on the first method match (enabling multi-method classes like Saiku #36).
   - Reconciles bare methods when unambiguous.
   - Retains unconsumed FQN classes only if no finer-grained test method was extracted.

---

## 3. Scorecard Acceptance Criteria (All 5 Met)

1. **Precision $\ge 0.90$**: **97.06%** (exceeds 95% target).
2. **OpenTripPlanner (#32)**: Exactly 4 TP, 0 FP, 0 FN (all 4 tests identified).
3. **Gradle Single-FP Fixtures (2, 5, 19, 20, 34, 38)**: Dropped from 1 FP to 0 FP.
4. **Target Maven Fixtures (6, 16, 18, 26, 40)**: Reached TP = Exp with FP = 0.
5. **No-Failure Fixtures (19 no-failure + 1 clean pass)**: 0 False Positives.

---

## 4. Error Reconciliation

- **Remaining False Positive (1)**:
  - `apache__flink__079848838447.txt`: `org.apache.flink.test.runtime.IPv6HostnamesITCase::testClusterWithIPv6host`. (A genuine failure in the log text not labelled in `EXPECTED.md`'s primary expectation).
- **Remaining False Negatives (12)**:
  - **Spock (#30)**: 1 narrative name with spaces (`openremote`).
  - **Kotlin (#33)**: 6 narrative names with spaces (`sirix`).
  - **Gradle Multi-Line Context (#8, #23)**: 4 tests where class names sit on preceding lines separate from the method outcome lines (`fineract`, `spotless`).
  - **Gradle 3-Segment (#39)**: 1 narrative assertion string (`Stirling-PDF`).

---

## 5. Verification Commands

```bash
uv run python analysis/fixture_score.py
uv run python analysis/fixture_score.py --show-errors
uv run pytest -q
```
Suite test count: 229 passed.

*Note for Operator: Terminal A holds git this round; add an entry for `049-2026-08-26-extractor-precision.md` to `docs/session/INDEX.md` in the next commit sequence.*
