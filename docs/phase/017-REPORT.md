# Phase 017 Report — root cleanup, exact_green verification, label rebuild

## Root: before / after

| | Untracked files at repository root |
|---|---:|
| Before | **49** |
| After | **0** |

`git status --short` ends showing only intended paths plus `vendor/graphify-br/`.

**Moved as evidence (3):** `holdout_v3_score.txt`, `holdout_v3_score2.txt`,
`holdout_v3_score_corrected.txt` → `docs/phase/009B-holdout-v3-scorecard-run{1,2,3}-*.txt`
plus a provenance README. Classification accuracy chain 90.00% → 96.67% → 100.00%;
precision/recall identical across all three (95.74% / 97.83%). The paper's honest
83.87% / 55.32% is the *first* scoring and is in none of them; the README says so.

**Deleted (46), each inspected first:**

| Group | n | Basis |
|---|---:|---|
| `tmp_rq1*.py` (6) + 2 zero-byte `.log` | 8 | `rq1_divergence.py` proven strict superset, byte-identical output |
| `scratch*.py` exploratory one-liners | 14 | one-shot parquet probes |
| `scratch_resolve{,2,3}.py`, `phase3.py` | 4 | superseded by `analysis/resolve_bases.py` |
| `scratch_eval.py` | 1 | differs from `analysis/holdout_eval.py` by ONE line (a constant) |
| `scratch_label{,2}.py`, `scratch_out.txt` | 3 | produced the VOID machine labels |
| `fix_*.py` (3) | 3 | mutate `holdout_v4/EXPECTED.md`, deleted in 012-B |
| `tmp_patch.py`, `patch_holdout_eval.py` | 2 | one-shot source patchers, applied |
| `tmp_add/amend/reconcile/tasks/tick/v3.py` | 6 | one-shot doc mutators, applied |
| `tmp_eval{,_v3}.py`, `tmp_test.py` | 3 | wrappers; `tmp_test.py` already in `tests/test_fixture_score.py:85-106` |
| `tmp_scan.py` | 1 | promoted to `analysis/secret_scan.py` |
| `package_release.py` | 1 | prints schema mismatches, writes nothing |

## The 2a plan as implemented

- **Endpoint:** `GET /repos/{repo}/actions/runs/{id}/jobs?per_page=100&page=N&filter=latest`,
  paginated to `total_count` (`fetch_all_jobs`). `filter=latest` pins the attempt per D-35.
- **Every job:** the base-side `conclusion != "failure"` skip is removed in both
  `fetch_base_logs.py` and `parse_base_logs.py`. Head-side filter untouched.
- **D-12 union:** any job `TEST_FAILURE` → base failed; else any `TEST_RAN_CLEAN`
  → tests observed; else no tests.
- **Proof it is not an unfetched job:** `dask/distributed` head run `30544820449`
  (workflow `Linting`, 1 job `pre-commit hooks`, failure) against base
  `29199157403` (same workflow, 1 job `pre-commit hooks`, success). The head ran
  zero tests too.

## Phase 2 — the six fractions

Sweep coverage: **220 / 1,732 base runs (12.7%)**, **762 / 4,245 instances (18.0%)**.
Python **167 / 167 (100.0%)**, Java **53 / 1,565 (3.4%)**. 45-minute cap reached.
Jobs enumerated 1,137; job logs retrieved **855 / 1,137 (75.2%)**.

Denominator is the 762 verified instances.

| Bucket | Fraction | Consequence |
|---|---:|---|
| retrievable(all jobs) + TEST_RAN_CLEAN | **163 / 762** (21.4%) | stays `exact_green` |
| partial + tests found in retrieved legs | **47 / 762** (6.2%) | stays `exact_green` |
| retrievable + TEST_FAILURE | **1 / 762** (0.1%) | reclassify as `exact` |
| retrievable(all jobs) + NO_TEST_OUTPUT | **346 / 762** (45.4%) | demote, **CONFIRMED** test-free |
| partial + no tests in retrieved legs | **157 / 762** (20.6%) | demote, **UNVERIFIABLE** |
| all jobs 410 | **48 / 762** (6.3%) | demote, **UNVERIFIABLE** |

Demotions CONFIRMED **346 / 762**; demotions UNVERIFIABLE **205 / 762**. Never summed.

### Predicted vs actual

Predictions were instance-weighted over all 4,245; actuals are over the 762
verified. Rates, not counts, are the honest comparison.

| Bucket | Predicted rate | Actual rate | Verdict |
|---|---:|---:|---|
| 410 / unretrievable | 41.2% | **6.3%** instance-weighted, **13.2%** run-weighted | **over-predicted** |
| TEST_RAN_CLEAN (stays) | 27.6% | **27.6%** (163+47 = 210/762) | **exact** |
| NO_TEST_OUTPUT (demote) | 32.4% | **66.0%** (346+157 = 503/762) | **under-predicted** |
| TEST_FAILURE | 0.9% | **0.1%** | over-predicted |

The 410 prediction was **instance-weighted from 016-A**; the sweep is
**run-weighted over 1,732**. Both bases are given above. It over-predicted
because Python — which 016-A measured at 7.11% >90d — was swept first by D-40.

## 2c — reversals

- Verified base runs with **zero** `conclusion == "failure"` jobs: **220 / 220**
- Instances the old path would have demoted: **762**
- Instances the every-job fix **keeps**: **211**

**211 of 762 (27.7%) demotions were a bug, not a finding.**

## Phase 4 — what moved

Two scenarios, because the sweep is 18% complete and one number would mislead in
one direction or the other.

| | Baseline | EVIDENCE-ONLY | INVARIANT-6 | Supersedes |
|---|---:|---:|---:|---|
| 4a. no_base | 5,520 / 12,581 (43.88%) | **6,071 / 12,581 (48.26%)** | **9,554 / 12,581 (75.94%)** | 43.88% (014-A) |
| 4b. exact_green | 4,245 | **3,693** | **210** | 4,245 (016-A) |
| 4c. strict instances | 778 | **725** | **122** | 778 (014-A) |
| 4d. strict labels | 4,194 | **4,100** | **423** | 4,194 (D-44) |
| 4e. Gate 1 (labels) | 4,194 / 5,000 | **4,100 / 5,000 NOT MET** | **423 / 5,000 NOT MET** | 4,194 / 5,000 |

EVIDENCE-ONLY applies verdicts only where a base run was verified; unswept
instances stay `exact_green` and are PROVISIONAL. INVARIANT-6 is what
`src/label/base_resolve.py` now produces: no log evidence, no green base. One
instance reclassified `exact_green` → `exact` in both.

**4f.** Under EVIDENCE-ONLY the corpus is **LARGER** than the published 524, by
**201** (725 vs 524). Under INVARIANT-6 it is **SMALLER** by **402** (122 vs 524).
The truth is bracketed by the two and moves toward the first as the sweep completes.

**4g.** 620 `exact_green` instances sit in visibly test-free workflows (`Clang
format linter` 145, `PR Lint` 132, `CodeQL` 122, `CodeQL Advanced` 81, `lint` 75,
`Auto PR V2 Deployment` 65). Surviving into strict: **11 / 620** under
EVIDENCE-ONLY, **0 / 620** under INVARIANT-6. The 11 are a **corpus-inclusion
defect, not a labelling one**, and await a ruling. Separately, **3,562 / 4,245
(83.9%)** of `exact_green` instances have `head_ran_tests == False`.

## Fresh-checkout results per target

**Reordering, stated:** Phase 5 was run AFTER Phase 6's commit. A clone at the
previous HEAD would have tested the code this round replaces, which measures
nothing. Cloned `https://github.com/DeepanshuOP/blastradius.git` into
`/tmp/br-verify` at `39839fd`, `uv sync` (clean), then each target.

`make test` on the clone: **380 passed, 14 failed, 4 errors, 4 skipped.** Every
failure is a missing `data/` input; both new fixture-backed suites
(`test_base_verify.py`, `test_secret_scan.py`) pass with no data.

`make tables` **stops at target 2**, on data, not on code or dependencies.
**6 of 15 targets pass with no data at all:**

| Target | Fresh clone | First missing input |
|---|---|---|
| `analysis/secret_scan.py` | **PASS** | — (no `release/`; exits 0) |
| `analysis/resolve_bases.py` | FAIL | `data/interim/base_resolution_new.parquet` |
| `analysis/fetch_base_logs.py` | FAIL | same (also needs 3 PATs) |
| `analysis/parse_base_logs.py` | FAIL | same (also needs `data/raw`) |
| `src/label/fault_revealing.py` | FAIL | same |
| `analysis/fixture_score.py` | **PASS** | — |
| `analysis/holdout_eval.py` | **PASS** | — |
| `analysis/binding_report.py` | FAIL | `data/interim/parsed_outcomes.parquet` |
| `analysis/attrition_funnel.py` | FAIL | `data/interim/instances_raw.parquet` |
| `analysis/rq1_divergence.py` | FAIL | `data/interim/outcomes.parquet` |
| `analysis/expiry_cliff.py` | **PASS** | — |
| `analysis/annotation_census.py` | **PASS** | — |
| `analysis/corpus_stats.py` | **PASS** | — |
| `analysis/verify_exact_green.py --report-only` | FAIL | `data/interim/exact_green_verification.parquet` |
| `analysis/corpus_delta.py` | FAIL | `data/interim/base_resolution_new.parquet` |

`rq1_divergence.py` now fails on **data**, not on matplotlib: the lazy import
works. `docs/DATA_DEPENDENCIES.md` rewritten from these measurements, and states
explicitly that `data/raw` (4.6 GB) cannot be regenerated because GitHub Actions
logs expire at 90 days — and that job *metadata* never expires while job *logs*
do, which is why `base_jobs_total` / `base_jobs_retrieved` are columns.

`/tmp/br-verify` removed after measurement.

## Suite

**Predicted 402, actual 402 passed.** (390 before + 12 new in
`tests/test_base_verify.py`.) One pre-existing test failed first and was amended,
not weakened: `test_base_resolve_ancestor_real_payload` asserted `exact_green`
from conclusion alone. Its ancestor ground truth is unchanged; the successful-base
case is now asserted twice — demote without evidence, `exact_green` with it.

## Hypothesis verdicts

1. **Some NO_TEST_OUTPUT verdicts reverse once every job is parsed.** —
   **CONFIRMED, and it is the round's largest finding.** 211 / 762 (27.7%).
2. **Demoting drops strict below the published 524.** — **CONFIRMED under
   INVARIANT-6: 122, below 524 by 402.** REFUTED under EVIDENCE-ONLY: 725, above
   by 201. Both stated plainly.
3. **Some exact_green bases parse to TEST_FAILURE.** — **CONFIRMED, 1 / 762.**
   016-A saw 0 / 13; at scale it is nonzero but rare.
4. **410 instances are a permanent ceiling.** — **CONFIRMED.** 48 / 762 fully
   unretrievable, plus 157 / 762 partially. Job *metadata* never expires, so these
   runs are enumerable but unreadable, forever.
5. **(added) Partial retrievability is a fifth bucket.** — **CONFIRMED.** 157 / 762
   are partial-with-no-tests, larger than the fully-410 bucket.

### Defects found that were not predicted

- `per_page=100` with no page turn silently truncated any run with >100 jobs.
- `get_with_backoff()` **raises** on non-retryable 4xx, so every
  `resp.status_code == 410` branch in `fetch_base_logs.py` was dead code and its
  410 counter read zero by construction.
- `analysis/fetch_base_logs.py`'s `__main__` referenced an undefined `stats`,
  raising `NameError` — `make tables` could not reach step 3.
- `scratch_eval.py` was a 444-line copy of `analysis/holdout_eval.py` differing
  in one constant, because `holdout_eval.py`'s `main()` has no `--holdout-dir`.
- `release/v0.1/` has **no regenerating script**; `package_release.py` writes nothing.

## Git

```
commit  39839fd68f27914970bf7f565d03861e29ae0a53
message fix: require a parsed base log before calling a base run green
HEAD        39839fd68f27914970bf7f565d03861e29ae0a53
origin/main 39839fd68f27914970bf7f565d03861e29ae0a53
```

No trailers. Identity verified `DeepanshuOP` /
`99538840+DeepanshuOP@users.noreply.github.com` before committing. Explicit
paths only, never `git add -A`. The `ghp_` placeholder in
`tests/fixtures/secret_scan/` did not trip GitHub push protection.

A follow-up commit carries this report's Phase 5 section and
`docs/DATA_DEPENDENCIES.md`, which could only be written after the push.
