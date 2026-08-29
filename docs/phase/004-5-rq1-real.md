# Phase 5: RQ1 Computed Honestly (T1.2a)

## 5a. Methodology
- **Inputs:** `changesets.parquet`, `cochange.parquet`, `binding.parquet`, `parsed_outcomes.parquet`
- The `pull_files` dataset is now used to supply the actual changed files for each PR, completely avoiding the network and eliminating the previous circular proxy issue.

## 5b. Honesty Statements
- **Circular Independence:** The changed files used in this calculation strictly originate from `pull_files.jsonl.gz` payloads extracted via `extract_changeset`. No input is derived from the co-change index itself.
- **n:** See exact counts in the output blocks below.
- **head-side failures, not fault-revealing:** A base run has NOT been resolved for most instances (Terminal A is fixing that). The "tests that actually failed" set is head-side only and is NOT yet the fault-revealing set of §21.1.
- **Pipeline Smoke Test:** If `n < 30`, this is reported solely as a pipeline smoke test rather than a general finding.
- **k-sensitivity strip:** We present `k=5`, `k=10`, and `k=20` to validate measurement sensitivity without parameter fitting.

## 5c. Overlap Statistics

<RQ1_STATS>
