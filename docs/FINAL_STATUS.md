# BlastRadius: final implementation status

Code commit `28d4323`; numbers snapshot tag `paper-numbers-v1.1` (v1 + D-53). Every figure below regenerates with `make tables`; nothing is typed in by hand.

## What is complete

- Harvester, parsers, labelling, base resolution, test-to-file binding, and the RQ1 evaluation (co-change and two baselines) with a per-instance leakage audit (D-52).
- `make tables` writes every paper number to `paper/generated/` with a script and git-sha header and no wall-clock; `make demo` runs the walkthrough.
- Local release bundle `release/v0.1` (pseudonymised authors, secret scan, canary, checksums; git-ignored) and `docs/DATASHEET.md`.
- Decisions D-44 to D-53 recorded in `docs/DECISIONS.md` (D-51 was never assigned).

## Headline figures

| figure | value | file |
|---|---|---|
| strict split | 762 instances, 4,168 labels, 2,466 distinct tests | `labelling_run.md`, `composition.md` |
| Gate 1 (labels, D-44) | 4,168/5,000 (83.36%), NOT MET | `gates.md` |
| Gate 1 (instances) | 762/5,000 (15.24%), NOT MET | `gates.md` |
| Gate 1.5 combined binding | 5,643/5,985 (94.29%), MET | `gates.md`, `binding.md` |
| Gate 1.5 full-confidence binding | 3,820/5,985 (63.83%), NOT MET | `gates.md`, `binding.md` |
| corpus | 77 repos, 175,038 runs, 667,398 jobs | `corpus_stats.md` |
| run-level `no_base` | 5,520/12,581 (43.88%) | `corpus_delta.md` |
| same-SHA flips | 62/11,557 (0.54%) | `flakiness.md` |
| strict labels by class | code-level 729 (17.49%), environment-strict 89 (2.14%), timeout 112 (2.69%), unknown 3,238 (77.69%), each /4,168 | `infra_failures.md` |
| RQ1, k=10, n=576, mean P/R/J | all-partner co-change .011/.051/.010; conventional-test co-change .054/.087/.038; changeset baseline .039/.245/.037; historical frequency .185/.517/.178 | `rq1.md` |
| parser precision (development corpora only) | fixture corpus 46/46; holdout v1 30/30; holdout v5 NOT SCORED (D-53) | `parser_precision.md` |

## Known limitations

- **Gate 1 is NOT MET in both forms** (labels 4,168/5,000; instances 762/5,000).
- **Gate 1.5 is NOT MET at full confidence** (3,820/5,985, 63.83%); it is MET only on the combined figure. Both are always reported together.
- **Parser precision is not independently measured.** Fixture and holdout v1 figures are development sets (fit numbers). No blind human labels exist for holdout v5, which stays unscored; the 029 worksheet is blank (D-53).
- **Environment and timeout labels remain in the strict set.** They are classified by a regex on the failure message (a lower bound; 77.69% of labels are `unknown`) and are reported, not removed.
- **The historical-frequency baseline orders runs by start time.** Completion time is not in `instances_raw`, so a run still executing when an instance started cannot be excluded.
- **`expiry_cliff.md` is stated as of the last capture** (2026-08-29), not as of today.
- **Attribution is observational:** no gold re-executed subset; labels record what CI ran. Corpus is 71 Java and 6 Python repositories, dominated by a few projects.
- **The graph layer covers the mini-corpus only** and is out of the paper (D-48).

## Remaining manual steps

1. Zenodo deposit of `release/v0.1`: draft prepared with reserved DOI 10.5281/zenodo.23250262 and licence CC BY 4.0. The five secret-scan REVIEW findings were checked (Apple icon filenames, Java package names, `adlam.example.com` test addresses). Files cannot change after publishing, so re-upload the current `docs/DATASHEET.md` first.
2. A GitHub release of the source (tag v1.0.0) with a Zenodo code DOI.
3. `CITATION.cff` is in the repository root (final author order).
4. Licence decided: release bundle CC BY 4.0, source code MIT. The schema validator (T1.6a) remains blocked.
