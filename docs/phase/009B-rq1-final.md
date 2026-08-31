# RQ1: Co-change Applicability and Accuracy

## Axis 1: Applicability
On the strict-split labelled instances (144 instances), we identify 10,909 total changed files.
- Total changed files: 10,909
- Changed files with >=1 co-change partner at support >= 3: 2,619 (24.0%)
- Changed files with >=1 co-change partner at support >= 2: 4,229 (38.8%)

Distribution of partners-per-changed-file (any support):
- 0: 6,680
- 1-2: 1,322
- 3-5: 746
- 6-10: 735
- 11+: 1,426

At the instance level, there are 503 valid instances (runs with at least one labelled test and non-empty changeset).
- Instances with at least one changed file with any partner: 379 / 503 (75.3%)
- The co-change proxy is **entirely silent** on 124 / 503 (24.7%) of instances.

## Axis 2: Accuracy (Conditional on Proxy Firing)
Evaluated only over the 353 instances where the proxy makes at least one prediction (predicts > 0 partners), comparing co-change against two null baselines:
1. **Changeset Baseline:** Predict the test files that changed in the changeset itself.
2. **Historical Top-k Baseline:** Predict the k most frequently failing test files in that repo over the trailing window.

**Leakage Statement:** To prevent leakage from the future, the trailing window for Baseline 2 is strictly cut at the instance's `run_started_at`. We enforced this by filtering `all_outcomes[all_outcomes['run_started_at'] < instance_run_time]` before computing the top-k most frequently failing tests.

| Predictor | k | n | Precision | Recall | Jaccard | Median \|Predicted\| |
| --- | --- | --- | --- | --- | --- | --- |
| Co-change | 5 | 353 | 0.012 | 0.031 | 0.009 | 9.0 |
| Baseline 1 (Changeset) | 5 | 353 | 0.033 | 0.202 | 0.030 | 10.0 |
| Baseline 2 (Hist. Top-k) | 5 | 353 | 0.219 | 0.493 | 0.204 | 5.0 |
| Co-change | 10 | 353 | 0.011 | 0.055 | 0.009 | 14.0 |
| Baseline 1 (Changeset) | 10 | 353 | 0.033 | 0.202 | 0.030 | 10.0 |
| Baseline 2 (Hist. Top-k) | 10 | 353 | 0.198 | 0.569 | 0.189 | 6.0 |
| Co-change | 20 | 353 | 0.010 | 0.061 | 0.009 | 20.0 |
| Baseline 1 (Changeset) | 20 | 353 | 0.033 | 0.202 | 0.030 | 10.0 |
| Baseline 2 (Hist. Top-k) | 20 | 353 | 0.186 | 0.620 | 0.180 | 6.0 |
