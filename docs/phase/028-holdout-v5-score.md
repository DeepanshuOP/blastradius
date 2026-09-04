# Phase 028: Holdout v5 Scorecard & Closure

**Date**: 2026-09-04 | **Status**: CLOSED (D-37) | **Corpus**: `tests/fixtures/holdout_v5/` (40 logs)

## Headline Score
First valid held-out parser precision figure for BlastRadius:
- **Precision**: 10 / 41 (24.39%)
- **Recall**: 10 / 22 (45.45%)
- **F1 Score**: 20 / 63 (0.3175)
- **Classification Accuracy**: 25 / 40 (62.50%)
- **Counts**: TP = 10, FP = 31, FN = 12, Total Expected = 22, Total Extracted = 41

**Supersedes**:
- 83.87% (Holdout v3) measured a parser that no longer exists.
- 100.00% (20-log holdout) is a development-set fit.
- 58.33% (Holdout v4) is void under D-38 (machine-derived ground truth).

## Expected Class Mapping Note
Expected Class was mechanically derived from operator Expected Identifiers via approved rules:
identifiers present → `TEST_FAILURE`; begins with `NO_TEST` → `NO_TEST_OUTPUT`; except Sections 9 & 10 explicitly ruled `TEST_RAN_CLEAN`. Multi-identifiers in 14 (3) and 33 (2) split on `; `.

## Disagreement Analysis (26 Fixtures)
According to raw log bytes, root causes classify into:
- **PARSER WRONG (2)**:
  - #8 (`apache/flink`): Syslog prefix (`Jun 08...`) masked pytest `FAILED` line.
  - #18 (`sirixdb/sirix`): Parser extracted bare class; FQCN was present in raw log `FAILED-TEST:`.
- **OPERATOR WRONG (24)**:
  - *Missed test failures entirely (9)*: #1 (`beam`), #3 (`beam`), #15 (`openremote`), #16 (`mybatis-plus`), #17 (`openremote`), #19 (`spotless`), #20 (`grobid`), #29 (`atlas`), #35 (`tika`). Blind excerpt truncated before failure lines.
  - *Missed additional failing methods (2)*: #11 (`spotless`), #33 (`hertzbeat`).
  - *Omitted pytest parameterization `[...]` (3)*: #2 (`fla`), #4 (`fla`), #6 (`distributed`).
  - *Omitted Java package name present in log bytes (6)*: #26 (`cldr`), #27 (`zeppelin`), #28 (`cldr`), #30 (`flink`), #32 (`zeppelin`), #33 (`hertzbeat`).
  - *Clean test runs labelled NO_TEST (5)*: #36 (`jline3`), #37 (`nitrite`), #38 (`thealgorithms`), #39 (`saiku`), #40 (`tika`). Tests ran and passed 100%.

## Parser Defects Recorded (Fix Nothing Per D-37)
1. Pytest parser fails when syslog timestamps precede `FAILED` (#8).
2. Gradle parser misses FQCN in `FAILED-TEST:` blocks (#18).

This corpus is CLOSED under D-37 and may never be re-scored.
