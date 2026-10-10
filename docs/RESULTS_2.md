# BlastRadius 2.0: results

Every number below is copied from a generated file and cites it. Two tables, never merged: Table 1 compares
methods on **the same data** (BR-Bench or BR-Seeded); Table 2 is **context from other papers' data** and is not a comparison.

Per D-56, E1 does not go into the MSR 2027 paper (Gate 3 not met). E3's numbers come from cached model replies and are not
part of `make tables`.

## Table 1: same data

### E1: predict which test files a change breaks (`paper/generated/rq2_predictor.md`, `rq2_ablation.md`)

The learned ranker reaches Recall@10 = 0.525 (95% bootstrap CI [0.447, 0.599]) on the chronological test split
(n = 148 instances, all Java), statistically indistinguishable from the strongest baseline B7 (0.522; Holm-adjusted
p = 0.2656, Cliff's delta +0.030, negligible). **Gate 3 is NOT MET.**

| method (test split, n = 148) | Recall@10 | MAP | source |
|---|---|---|---|
| B1 random, 20 seeds (floor) | 0.029 ± 0.011 | 0.020 ± 0.003 | rq2_predictor.md, "Side by side" |
| B4 failure history | 0.439 | 0.249 | same |
| B6 history-only LTR | 0.477 ± 0.021 | 0.341 ± 0.013 | same |
| B7 readily-available-info LTR | 0.522 ± 0.021 | 0.359 ± 0.020 | same |
| ours, all feature families | 0.525 ± 0.010 | 0.381 ± 0.006 | same |

- Ours vs B4: Holm-adjusted p = 0.006148, Cliff's delta +0.114 (negligible). Ours vs B6: adjusted p = 0.1117, delta +0.071 (negligible).
  The generated file tests ours against every baseline; it does not test B6 or B7 against B4 separately.
- Removing co-change features changes Recall@10 by -0.007 (seed std 0.012; full-model std 0.010); removing co-failure features
  by -0.001 (std 0.009). Removing `hist_` gives -0.140 and `prox_` -0.075 (`rq2_ablation.md`, "Ablation deltas against seed variability").
- Leave-one-repo-out: ours beats both B4 and B5 on 9 of 12 held-out repos. Of the two Python repos with at least 20
  instances, fla-org/flash-linear-attention is 0.801 against B4 0.721, and dask/distributed is 0.453 against B4 0.474
  (`rq2_predictor.md`, "By language").
- The test split contains only Java instances (148 of 148); a Python result exists only in the leave-one-repo-out table.

### E2: is a failure mine, inherited or flaky? (`paper/generated/rq3_triage.md`) **small-sample (18 not-mine pairs in the test split)**

Positive class = not-mine (inherited + flaky). Cells are cleared-not-mine / not-mine and mine-wrongly-cleared / mine.

| method | test split (1,033 pairs: 18 not-mine, 1,015 mine): not-mine cleared | mine wrongly cleared | pooled leave-one-repo-out (4,384 pairs: 216 not-mine, 4,168 mine): not-mine cleared | mine wrongly cleared |
|---|---|---|---|---|
| Blame-all | 0/18 | 0/1,015 | 0/216 | 0/4,168 |
| R-branch | 11/18 | 125/1,015 | 145/216 | 1,262/4,168 |
| R-msg | 12/18 | 223/1,015 | 135/216 | 848/4,168 |
| Logistic regression | 3/18 | 30/1,015 | 74/216 | 123/4,168 |
| LightGBM | 10/18 | 33/1,015 | 31/216 | 57/4,168 |

The numbers show a trade-off, not a working triage: every method that clears a meaningful share of not-mine failures also
clears mine failures a developer would then ignore (LightGBM pooled: 31 of 216 not-mine cleared at 57 of 4,168 mine wrongly
cleared; the rules clear more not-mine at 15 to 22 times the wrong clearances). The test split has no flaky pairs.

### E3: change-aware repair on BR-Seeded (`paper/generated/rq4_repair.md`)

**Retrieval (all 70 tasks, no model).** The seeded function is among the three chunks shown for 69/70 (98.57%) with the
change-aware arm R2 and 46/70 (65.71%) with the log-only arm R1 (paired, 23 vs 0, exact McNemar p = 2.384e-07). R2's
advantage is partly by construction: the seeded edit is inside the diff that R2 searches.

**Repair (n = 20 tasks per model, same subset, plausible fix = full suite green).** R2 has more plausible fixes than R1 with
both models, but the paired difference is not statistically distinguishable at n = 20.

| arm | gpt-oss-120b | gpt-oss-20b |
|---|---|---|
| R0 notify only | 0/20 | 0/20 |
| R1 log-only | 10/20 | 4/20 |
| R2 change-aware | 13/20 | 10/20 |
| R3 R2 + up to 2 retries | 14/20 | 13/20 |
| McNemar R2 vs R1 (R2 only : R1 only) | p = 0.5078 (6 : 3) | p = 0.1094 (8 : 2) |

- Overfit patches (target tests pass, suite fails): 120b R2 1, R3 1; 20b R2 1, R3 0.
- Tokens per task: 120b R1 1,907, R2 1,452, R3 2,554; 20b R1 1,558, R2 1,390, R3 2,754. Cost USD 0 (Groq free tier).
- Detection (63 tasks with a resolvable failing test file): mean position of the first failing test file is 11.73 under E1
  order, 8.79 alphabetical and 11.14 random. **The E1 order does not help on these repos.**
- Seeded bugs are simpler than real ones, and the operator mix is uneven (markupsafe: 18 of 19 tasks are NEGATE_COND).

## Table 2: context only, different data

| work | reported result | data |
|---|---|---|
| T-TS (Plyusnin et al., 2025) | recall 0.95 at 15% of tests | proprietary |
| Pan & Pradel, ISSTA 2021 | suite-level AUC gain of 13.9% | 242 projects |
| LogSage (Xu et al., 2025) | RCA precision above 98% | 367 failures |
| CI-Bench (Nabil et al., 2026) | 13-36% repair success | 100 BugSwarm failures |
| CI-Repair-Bench (Muna et al., 2026) | Pass@1 7.9-18.9% | 567 GitHub Actions failures |

These come from different data; we do not claim to beat them.
