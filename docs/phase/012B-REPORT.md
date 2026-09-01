# Phase 012-B REPORT

## Per-Phase Status
- **PHASE 1 (QUARANTINE)**: PASS
  - `tests/fixtures/holdout_v4/EXPECTED.md` moved to `docs/phase/011B-VOIDED-machine-labels.md` with explicit quarantine evidence header.
  - `docs/phase/011B-holdout-v4-score.md` marked VOID at the top, citing the automated extraction root cause and the `1::254 s` separator artifact.
  - Confirmed remaining files in `tests/fixtures/holdout_v4/` contain strictly the 32 raw `.txt` execution logs and zero derived identifiers.
- **PHASE 2 (WORKSHEET)**: PASS
  - Created `docs/phase/012B-holdout-v4-worksheet.md` containing 32 sections (one per log).
  - Each section carries the log filename, workflow conclusion (`failure`), byte-for-byte raw excerpt under 60 lines (ANSI and timestamps intact, elisions marked), and unpopulated template fields (`Expected Class: ___`, `Expected Identifier Count: ___`, `Expected Identifiers: ___`).
  - Zero empty fields were prefilled or suggested.
- **PHASE 3 (PARSER DEFECTS)**: PASS
  - Created `docs/phase/012B-parser-defects.md` diagnosing the three parser bugs:
    - 3a (pytest parameterisation bracket retention violating D-32; confirmed D-32 was never implemented in `log_pytest.py`).
    - 3b (Gradle suite prefix `"Gradle suite"` and dot separator in TestNG / multi-level chevrons).
    - 3c (Java dropped package due to assertion-only stack traces bypassing `_AT_FRAME_RE` in `log_gradle.py`).
- **PHASE 4 (FRAME ANALYSIS & STRATIFICATION)**: PASS (STOP for approval)
  - 4a: Confirmed `analysis/build_holdout_v4.py` filtered candidates via `analysis/expected_audit.py`'s `_PYTEST_SUMMARY_RE` and `_GRADLE_SUMMARY_RE`, which require failure tokens (`failed`), discarding clean logs as `NO_SUMMARY`.
  - 4b: Counted workflow runs with `run_conclusion == 'success'` across `data/raw/` / `instances_raw.parquet`:
    - **Gradle**: 64,926 success (out of 93,823 total runs)
    - **Maven**: 44,803 success (out of 58,702 total runs)
    - **pytest**: 8,194 success (out of 12,752 total runs)
    - **Total**: 117,923 success runs (out of 165,277 total runs)
  - 4c: Proposed amended stratification below. **STOPPING for approval. Sampled nothing.**
- **PHASE 5 (DECISION RECORD)**: PASS
  - Appended **D-38** ("Void versus superseded scoring") to `docs/DECISIONS.md`. D-21 remains RESERVED.
- **PHASE 6 (COMMIT)**: WAITING for operator authorization ("CLI-1 has pushed").

---

## Phase 4c Proposed Amended Stratification (For Operator Approval)

### Proposed Sampling Stratification:
To honestly evaluate the `TEST_RAN_CLEAN` vs `NO_TEST_OUTPUT` classification boundary under the Spec 008-B scorer contract, the sampling frame for clean strata must be selected purely on workflow run metadata (`conclusion == 'success'`) independent of log text regexes.

1. **Total Sample Size**: 40 logs across the frozen repository frame (`data/frame/frame_v1.csv`).
2. **Harness Allocation**:
   - **Maven**: 15 logs (10 Failing drawn from runs with `conclusion == 'failure'`, 5 Clean drawn from runs with `conclusion == 'success'`).
   - **Gradle**: 15 logs (10 Failing drawn from runs with `conclusion == 'failure'`, 5 Clean drawn from runs with `conclusion == 'success'`).
   - **pytest**: 10 logs (8 Failing drawn from runs with `conclusion == 'failure'`, 2 Clean drawn from runs with `conclusion == 'success'`).
3. **Selection Criteria**:
   - Clean logs are selected from runs where GitHub Actions reported `conclusion == 'success'` without pre-filtering on log body patterns.
   - Failing logs are selected from runs where GitHub Actions reported `conclusion == 'failure'`.
   - Max 2 logs per repository.
   - Zero job ID overlap with dev fixtures (`tests/fixtures/logs/`) or prior holdout sets (`tests/fixtures/holdout/`, `tests/fixtures/holdout_v3/`).
   - Maximum uncompressed size $\le 8\text{ MB}$.

---

## File Manifest
- **CREATED**:
  - `docs/phase/011B-VOIDED-machine-labels.md` (quarantine copy of voided machine labels)
  - `docs/phase/012B-holdout-v4-worksheet.md` (32-section hand-labelling worksheet)
  - `docs/phase/012B-parser-defects.md` (read-only bug report for CLI-1)
  - `docs/phase/012B-REPORT.md` (this report)
  - `docs/session/072-2026-08-31-012B-void-v4-worksheet.md` (session report)
- **MODIFIED**:
  - `docs/phase/011B-holdout-v4-score.md` (marked VOID)
  - `docs/DECISIONS.md` (appended D-38)
  - `docs/session/INDEX.md` (added session 072)
  - `docs/HANDOFF.md` (appended handoff entry)
- **DELETED**:
  - `tests/fixtures/holdout_v4/EXPECTED.md` (quarantined)

---

## Verification Summary
- `git status` confirms zero changes to `src/`, `tests/`, or `Makefile`.
- `holdout_v4/` contains exactly 32 `.txt` files and no `EXPECTED.md`.
