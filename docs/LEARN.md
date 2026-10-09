# LEARN — one-page study guide for the viva

Every number below is copied from the file named next to it; regenerate with `make tables` before quoting.

## The pipeline in 10 steps

1. **Frame.** SEART export of 3,671 repos → CI-live → has a test workflow → 300 sampled (`paper/generated/attrition_funnel.md`).
2. **Harvest.** `src/harvest/` pulls PR, run and job metadata through `get_with_backoff()` (rate-limited, resumable): 165,349 runs, 12,581 failed.
3. **Logs.** Failed-job logs stored under `data/raw/`; success logs pruned. 6,586 failed runs have a log on disk (90-day expiry, step 10 of the funnel).
4. **Parse.** `src/parse/` harness parsers (Maven/Gradle/JUnit, pytest) turn a log into `TestOutcome` records.
5. **Canonical `test_id`.** One normaliser (`src/parse/test_ids.py`, extends Graphify's `ids.py`) is the join key for the whole project (frozen week 1).
6. **Base-run resolution.** Walk the real commit graph from the PR head and find the CI run of the base (D-34): statuses `exact`, `exact_green`, `ancestor`, `branch_prior`, `no_base`.
7. **Fault-revealing labels.** A test is labelled iff it fails at head, did not fail at base, and does not flip on the same SHA (`src/label/fault_revealing.py`). Strict = relaxed minus flips.
8. **Binding.** Each labelled test bound to its test file at the pinned commits in `docs/CLONE_PINS.json` (D-50).
9. **RQ1.** Co-change and baselines (changeset, historical frequency) predict test files at k = 5/10/20, scored on the same instances, leakage-audited (`analysis/rq1_divergence.py`).
10. **Release.** `analysis/build_release.py` → 4 Parquet tables, `schema.json`, validator (T1.6a), pseudonymised logins, secret scan; Zenodo DOI 10.5281/zenodo.23250262.

## Make targets

| target | does |
|---|---|
| `make test` | full pytest suite (do not set `BR_OFFLINE`; the HTTP tests need it unset) |
| `make tables` | freshness check, secret scan, then every `analysis/` script that writes `paper/generated/*.md` (offline, ~8 min) |
| `make reproduce` | 3-repo graph mini-corpus: build → bind → query on 3 SHAs per repo (graph layer, D-48) |
| `make demo` | terminal walkthrough of one real strict instance |
| `make demo-data` | export recorded runs + all result tables to `demo-web/public/data/` |
| `make agents-demo` | the five agents, three recorded offline scenarios (D-55) |
| `make demo-web` | build and serve the dashboard on http://127.0.0.1:3000 |
| `make analyze REPO=… STORY="…"` | shallow-clone any public Python/Java repo and run the offline impact analysis |
| `make resolve-bases`, `make fetch-base-logs` | network steps; not part of `tables` |

## Where the headline numbers come from

| number | file |
|---|---|
| 762 strict instances, 4,168 labels, 37 repos | `attrition_funnel.md`, `gates.md`, `composition.md` |
| binding 94.29% combined (5,643/5,985), 63.83% full confidence (3,820/5,985) | `binding.md` |
| history 39.44% (519/1,316) vs co-change 4.64% (61/1,316) micro recall, k = 10 | `rq1.md` |
| Gate 1 NOT MET: 4,168/5,000 labels | `gates.md` |
| no_base 5,520/12,581 (43.88%) | `base_resolution.md` |
| flips 62/11,557; 46/4,214 relaxed labels removed as flaky | `flakiness.md` |
| 4,458/13,422 failed-run logs already expired (>90 days) | `expiry_cliff.md` |
| leakage 640/713 → 0/713 | `leakage_audit.md` |
| parser precision 100% on development sets only; v5 not scored | `parser_precision.md` |
| graph reachability on the mini-corpus: n = 0 (no buildable base graph offline) | `docs/phase/031-reachability-mini-corpus.md` |

## 15 likely questions

1. **How is the base run found?** By walking the real commit graph (`git rev-list --parents`) from the PR's base and looking up runs in a branch-run index, depth ≤ 10 (D-34). `run.pull_requests[].base.sha` was present on only 10.27% of failed runs, so it was not used.
2. **Why does `no_base` emit no label?** Without a base run we cannot tell "broken by this PR" from "already broken". Emitting labels would be invariant 6's trap; the code asserts no `no_base` run reaches the valid set.
3. **What is `exact_green`?** The base run was observed and succeeded, so its failure set is empty by observation, not by assumption.
4. **How is flakiness handled?** A (head SHA, workflow, test) that fails in some but not all runs on the same SHA is a flip; flips are removed from strict labels (46 of 4,214 relaxed labels).
5. **Why two binding numbers?** D-47: "combined" counts basename-only matches at 0.5 confidence; "full confidence" needs a fully-qualified class name. Gate 1.5 (≥ 70%) is MET on combined, NOT MET on full confidence; both are always reported.
6. **Gate 1 was missed. Is the paper dead?** No. The contribution is the dataset and an honest measurement (D-02); 4,168/5,000 labels is reported as NOT MET, not hidden. The funnel shows where runs were lost (log expiry, unparsed logs, no_base).
7. **What is D-48?** The graph layer is excluded from the MSR paper and `make tables`; it continues as the course deliverable on a 3-repo mini-corpus.
8. **What is D-55?** The five agents are a separate, cuttable demo path: nothing in the pipeline imports them and no agent number reaches the paper. Offline by default; an LLM only with `ANTHROPIC_API_KEY`.
9. **Why does history beat co-change?** Co-change predicts files that changed with the edited files; most partners are not tests (restricting to test files lifts it only to 7.67%). Failing tests recur across PRs in the same repo, which history captures directly.
10. **How do the agents use the graph?** Impact Analysis matches story terms to files, then reverse-walks calls/imports/uses/tests edges to find tests that reach a changed file; risk = 0.55 × graph proximity + 0.15 × story terms + 0.3 × past failure rate (history weighted above co-change, following RQ1).
11. **Was the leakage fixed?** Yes. In the legacy static co-change table, a commit dated after the run started touched a changed file in 640/713 audited instances; with per-instance trailing history, 0/713 (`leakage_audit.md`).
12. **Is parser precision 100%?** Only on development sets that tuned the parsers; it is not a held-out figure. The independent v5 holdout is unscored (D-53).
13. **Why did graph reachability produce no result?** The 36 base SHAs were not buildable offline: 22 fla commits are absent from the clone, and saiku is a blobless partial clone. n = 0 is reported, not padded.
14. **Is it deterministic?** Seeds fixed, dependencies pinned, no LLM in the reproducible pipeline (D-17); every paper number regenerates via `make tables`.
15. **Limitations?** Gate 1 missed; 43.88% no_base; log expiry loses a third of failed runs; static reachability over-approximates and misses reflection; full-confidence binding below 70%; parser precision has no independent figure; Java + Python only.
