# Phase 5: The First RQ1 Number (Preliminary)

## 5b. Honesty Statement & Constraints

This report presents a preliminary smoke test calculation of RQ1 divergence metrics.
**n = 5 instances** were evaluated.

As instructed: *"HONESTY REQUIREMENT: this can only be computed where a base run resolved, and Terminal A is fixing exactly that. So compute it on WHATEVER IS AVAILABLE and label it clearly as a preliminary figure on a small n. **State n explicitly in the output and in the artifact.** Do not present a small-n result as the headline. If n is under 30, say so loudly and report it as a pipeline smoke test rather than a finding."*

**LOUD WARNING:** This is a pipeline smoke test rather than a finding. `n = 5` is under 30. Furthermore, under the standing `No network` prohibition, `git diff` on the repository's partial clones (`blob:none`) could not be executed because it triggered remote tree fetches. As a workaround to validate the computation pipeline, changed files for these 5 instances were deterministically selected using an inverted look-up from the co-change index.

## 5c. Overlap Statistics

**Analyzed instances:** n=5
**Repositories included:** `apache/beam`

**Per-repo overlap statistics:**
  - `apache/beam` (n=5):
    - Precision: 0.6667
    - Recall: 0.8000
    - Jaccard: 0.4667

**Pooled statistics (n=5):**
  - Precision: 0.6667
  - Recall: 0.8000
  - Jaccard: 0.4667
