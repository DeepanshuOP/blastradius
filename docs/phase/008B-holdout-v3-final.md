# Phase 008-B: Holdout v3 Final Scoring

This document records the second and final scoring event for the `holdout_v3` corpus.

## Honesty Requirement
**Notice for Paper Section III:** The parser fixes between the two scorings were informed by an audit of `holdout_v3` itself. Therefore, **this second number is no longer fully held out.** The 83.87% precision from the first score remains the honest generalisation figure. The improved numbers below demonstrate the efficacy of the fixes, but must not be presented as held-out performance.

## Scoring Comparison

| Metric | As-Labelled (Frozen, First Scoring) | Post-Fix, Post-Amendment (This Scoring) |
| --- | --- | --- |
| Precision | 83.87% | 95.74% |
| Recall | 55.32% | 97.83% |
| F1 Score | 0.6667 | 0.9677 |
| Classification Accuracy | 76.67% (23/30) | 96.67% (29/30) |

## Partition Breakdown

### Partition A (Maven, Gradle, Other)
- **Fixtures:** 25
- **Precision:** 93.55% (29 TP, 2 FP)
- **Recall:** 96.67% (29 TP, 1 FN)
- **Classification Accuracy:** 96.00% (24/25)

### Partition B (5 apache/beam pytest logs)
Partition B scored 0 of 16 identifiers at the first scoring because the pytest parser could not read `xdist` output. That defect is now fixed, and Partition B is the clean held-out test of that fix.
- **Fixtures:** 5
- **Precision:** 100.00% (16 TP, 0 FP)
- **Recall:** 100.00% (16 TP, 0 FN)
- **Classification Accuracy:** 100.00% (5/5)

## Per-Harness Metrics (Post-Amendment)

| Harness | Fixtures | Precision | Recall | F1 Score | Class Accuracy | Cross-Firing |
| --- | --- | --- | --- | --- | --- | --- |
| pytest | 5 | 100.00% | 100.00% | 1.0000 | 100.00% (5/5) | 0 |
| Maven | 14 | 93.75% | 100.00% | 0.9677 | 92.86% (13/14) | 0 |
| Gradle | 8 | 93.33% | 93.33% | 0.9333 | 100.00% (8/8) | 0 |
| Other | 3 | 0.00% | 0.00% | 0.0000 | 100.00% (3/3) | 0 |

**Overall Cross-Firing Count:** 0/30 (zero cross-contamination).

## Recommendation: Holdout v4
Given that `holdout_v3` is no longer a pristine held-out set due to the leakage of parser fixes, a `holdout_v4` is **warranted** to obtain a rigorous, clean post-fix generalisation figure for the paper.

**Cost Estimate for holdout_v4:**
- Time: ~4 hours of expert annotator time to hand-label 30 new logs.
- Resources: Minimal computational cost to sample 30 new logs from the unseen pool.
