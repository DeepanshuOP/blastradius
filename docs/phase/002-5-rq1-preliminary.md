# Phase 5: The First RQ1 Number (Preliminary)

## 5b. Honesty Statement & Constraints

This report previously presented a preliminary smoke test calculation of RQ1 divergence metrics.

**LOUD WARNING - VOID NUMBERS:** The computation presented here was circular and the results are void. Under the standing `No network` prohibition, `git diff` on the repository's partial clones (`blob:none`) could not be executed because it triggered remote tree fetches. As a workaround to validate the computation pipeline, changed files for those instances were derived from the co-change index itself and then compared against it. This renders the measurement circular and void. 

The `pull_files` payloads on disk (`data/raw/*/pr/*/*/pull_files.jsonl.gz`) are the correct and non-circular source for changed files and will be used moving forward.

## 5c. Overlap Statistics

**VOID.** No precision, recall, or Jaccard figures are reported here due to the circular derivation of changed files from the co-change index.
