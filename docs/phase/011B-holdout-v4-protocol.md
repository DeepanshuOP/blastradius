# Phase 011-B: Holdout v4 Protocol

## RNG Seed
20260831

## Sampling Frame
All raw build logs available in `data/raw/` (originating from `data/frame/frame_v1.csv` for both Java and Python).

## Target Size & Stratification
**Target Size:** 40 logs

We stratify by harness and expected class (Failing / Clean):
- **Maven**: 15 logs (10 Failing, 5 Clean)
- **Gradle**: 15 logs (10 Failing, 5 Clean)
- **pytest**: 10 logs (8 Failing, 2 Clean)

## Exclusion Rules
- **Zero log-identity overlap** with the dev corpus (`tests/fixtures/logs/`).
- **Zero log-identity overlap** with the v2 holdout corpus (`tests/fixtures/holdout/`).
- **Zero log-identity overlap** with the v3 holdout corpus (`tests/fixtures/holdout_v3/`).
- Overlap is checked by repository and job ID.
- Max 2 logs per repository.
- Maximum uncompressed size: 8 MB (to remain within context limits).
