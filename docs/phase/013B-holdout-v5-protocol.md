# Holdout v5 Sampling & Stratification Protocol (Phase 013-B)

**Date**: 2026-08-31  
**Status**: APPROVED PROTOCOL — SAMPLING GATED (DO NOT SAMPLE UNTIL CLI-1 PARSER FIXES LAND)  
**Governing Decisions**: D-27, D-29, D-32, D-37, D-38  
**Deterministic Seed**: `20261111`

---

## 1. Objective & Purpose

Holdout v5 establishes a clean, quarantined 40-log held-out evaluation corpus to measure the generalized precision and classification accuracy of the BlastRadius log parser suite (`src/parse/log_*.py`).

Under **D-37** (Holdout corpus lifecycle) and **D-38** (Void versus superseded scoring), Holdout v5 will be sampled only once, hand-labelled via an unpopulated human worksheet with zero automated machine extraction, and scored exactly once after CLI-1 lands the three outstanding parser defect fixes:
1. **pytest parameterisation**: stripping bracketed iterations per D-32.
2. **Gradle/TestNG suite formatting**: handling `"Gradle suite"` prefixes and dot separators.
3. **Gradle package recovery**: recovering packages from assertion-only stack frames and Surefire headers.

---

## 2. Sampling Frame & Quota Stratification

The corpus draws 40 logs across the 300-repo frozen frame (`data/frame/frame_v1.csv`), stratified across harnesses and execution outcomes:

| Harness | Failing Logs (`conclusion == 'failure'`) | Clean Logs (`conclusion == 'success'` + Test Summary) | Total Quota |
| :--- | :---: | :---: | :---: |
| **Maven** | 10 | 5 | **15** |
| **Gradle** | 10 | 5 | **15** |
| **pytest** | 8 | 2 | **10** |
| **TOTAL** | **28** | **12** | **40** |

---

## 3. Stratum Selection Rules & The Clean Log Verification Guard

### 3.1 Failing Stratum Selection
- Drawn from workflow runs where GitHub Actions metadata records `run_conclusion == 'failure'`.
- Target job logs must be unexpired and present in `data/raw/{repo}/job/*/*/logs.jsonl.gz`.

### 3.2 Clean Stratum Selection (The Critical Guard)
- Drawn from workflow runs where GitHub Actions metadata records `run_conclusion == 'success'`.
- **Mandatory Filter**: The raw log text **MUST contain an explicit test execution summary of any kind**:
  - **Maven**: Surefire / Failsafe summary line (e.g. `Tests run: \d+, Failures: 0, Errors: 0, Skipped: \d+`).
  - **Gradle**: Explicit test task execution block (e.g. `> Task :test`, `:testClasses`, or Gradle test summary report line).
  - **pytest**: Pytest summary footer line (e.g. `=== \d+ passed.* in \d+.\d+s ===`).
- **Rationale**: A workflow run that succeeded because it compiled code, ran a linter, skipped tests, or executed a deployment task has no test execution in its log. Without this summary verification guard, such runs would be silently mislabelled `TEST_RAN_CLEAN` instead of `NO_TEST_OUTPUT`, corrupting the ground truth of the classification boundary.

---

## 4. Sampling Constraints & Isolation Rules

1. **Repository Diversity**: Maximum of **2 logs per repository** across the 40-log sample.
2. **Quarantine Isolation**: Zero job ID or run ID overlap with:
   - Development fixtures: `tests/fixtures/logs/` (40 logs)
   - Holdout v2: `tests/fixtures/holdout/` (20 logs)
   - Holdout v3: `tests/fixtures/holdout_v3/` (40 logs)
   - Voided Holdout v4: `tests/fixtures/holdout_v4/` (32 logs)
3. **Payload Size Limit**: Maximum uncompressed log size $\le 8\text{ MB}$ (verified via gzip ISIZE trailer).
4. **Reproducibility**: Candidate selection must be sorted deterministically by `(repo, run_id, job_id)` before applying `Random(seed=20261111).shuffle()`.

---

## 5. Labelling & Scoring Workflow (Post-Sampling)

1. **Sampling Script**: CLI-1 or the designated runner implements `analysis/build_holdout_v5.py` strictly adhering to this protocol.
2. **Raw Log Extraction**: 40 raw `.txt` files extracted into `tests/fixtures/holdout_v5/`.
3. **Worksheet Generation**: A blank markdown worksheet (`docs/phase/013B-holdout-v5-worksheet.md`) generated containing 40 sections with raw excerpts and empty templates (`Expected Class: ___`, `Expected Identifier Count: ___`, `Expected Identifiers: ___`).
4. **Zero Machine Labels**: No automated grep, no regex parser, and no BlastRadius code may prefill the worksheet (D-38).
5. **Single Scoring Event**: Ground truth hand-labelled by the operator; scored once via `analysis/holdout_eval.py` (D-37).

---

## 6. Current Operational State

**SAMPLING IS DEFERRED.**  
No sampling has occurred in this round. The sampling script will be executed only after CLI-1 completes the parser repair round.
