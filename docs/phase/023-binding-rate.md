# Phase 023 — Binding Rate on Post-Fix Key Space

## Executive Summary
Re-derivation of test-to-source file binding across all 12,072 eligible logs following D4/D-46 parser defect resolutions.

## Corpus Scope & Outcomes
- **Total outcome rows**: 20,451 (supersedes 20,535 pre-fix)
- **Distinct test_id total**: 5,985 (supersedes 6,014 pre-fix)
  - **Distinct Java test_id**: 5,115 (supersedes 5,144 pre-fix)
  - **Distinct Python test_id**: 870 (matches 870 pre-fix)

> **Superseded by D-50:** exact 5,622 → 5,643 / 5,985 (93.93% → 94.29%); not_found 199 → 178 (3.32% → 2.97%); full confidence 3,819 → 3,820 (63.81% → 63.83%); basename-only 1,803 → 1,823 (30.13% → 30.46%); ambiguous 164 unchanged. Measured against pinned clones. The figures below are the D-47 record.

## Binding Status Breakdown (Total: 5,985)
- **Exact**: 5,622 / 5,985 (93.93%, supersedes 5,629 / 6,014 = 93.60%)
- **Not Found**: 199 / 5,985 (3.32%, supersedes 218 / 6,014 = 3.63%)
- **Ambiguous**: 164 / 5,985 (2.74%, supersedes 167 / 6,014 = 2.78%)
- **Unqualified**: 0 / 5,985 (0.00%, supersedes 0 / 6,014 = 0.00%)

## Quality & Confidence Breakdown
- **Full confidence (1.0)**: 3,819 / 5,985 total (63.81%) | 3,819 / 5,622 exact (67.93%)
- **Basename-only confidence (0.5)**: 1,803 / 5,985 total (30.13%) | 1,803 / 5,622 exact (32.07%)

### Gate 1.5 Verdict
Gate 1.5 (binding >= 70%, ROADMAP §37.1) is met only when 0.5-confidence matches are included. Full confidence alone achieves 63.81% (3,819 / 5,985).

## Residual Bare-Class Fragmentation
- **Bare-class Java test_ids**: 2,043 / 5,115 (39.94%, supersedes 2,067 / 5,144 = 40.18%)
- **Etiology**: Residual fragmentation stems from an absence of evidence in the logs (unqualified test execution lines lacking preceding suite headers or stack frames), rather than a parser limitation.
