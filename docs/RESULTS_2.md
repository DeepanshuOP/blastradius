# BlastRadius 2.0: results

Every number below is copied from a generated file (`paper/generated/rq2_predictor.md`, `rq2_ablation.md`, `rq3_triage.md`,
`rq4_repair.md`). Two tables, never merged: Table 1 compares methods on **the same data** (BR-Bench or BR-Seeded); Table 2 is
**context from other papers' data** and is not a comparison. Per D-56, E1 does not go into the MSR 2027 paper (Gate 3 not met).
E3 numbers come from cached model replies and are not part of `make tables`.

## Table 1: same data

### E1: predict which test files a change breaks

On the chronological test split (148 instances, all Java), the learned ranker reached Recall@10 = 0.525 (95% CI 0.447-0.599). A learned ranker restricted to readily available signals (B7, after Elsner et al.) reached 0.522. The difference is not significant (Holm-adjusted p = 0.382, Cliff's δ = 0.030, negligible), so Gate 3 is not met. Our ranker does place failing test files above the failure-history heuristic B4 (0.439; adjusted p = 0.010), but the effect is negligible (δ = 0.114); neither learned baseline separates from B4 after correction (B6 vs B4 adjusted p = 0.382, B7 vs B4 adjusted p = 0.243). The ablation explains the result: removing failure-history features costs 0.140 Recall@10 and removing path-proximity features 0.075, while removing co-change (−0.007) or co-failure (−0.001) features changes the score by less than the seed-to-seed spread (0.009-0.012). Once history and proximity are known, co-change adds no measurable signal. This agrees with RQ1, where co-change recovered 4.64% of fault-revealing tests. A random ordering reaches 0.029.

| method (test split, n = 148) | Recall@10 | MAP | source |
|---|---|---|---|
| B1 random, 20 seeds | 0.029 ± 0.011 | 0.020 ± 0.003 | rq2_predictor.md, "Side by side" |
| B4 failure history | 0.439 | 0.249 | same |
| B6 history-only LTR | 0.477 ± 0.021 | 0.341 ± 0.013 | same |
| B7 readily-available-info LTR | 0.522 ± 0.021 | 0.359 ± 0.020 | same |
| ours, all feature families | 0.525 ± 0.010 | 0.381 ± 0.006 | same |

Candidate test files per test instance: median 595, max 3,079 (`rq2_predictor.md`). Leave-one-repo-out: ours beats both B4 and B5 on
9 of 12 held-out repos (`rq2_predictor.md`, "By language").

On the seeded Python repositories, which have no failure history, ordering tests with the BR-Bench model put the first failing test file at mean position 10.91, behind alphabetical order (8.11) and random order (10.37). The model's strongest signal, failure history, does not exist on a fresh repository, so a deployment needs history before ranking pays off.

### E2: is a failure mine, inherited or flaky? **small-sample (18 not-mine pairs in the test split)**

Triage is a small-sample result: the whole corpus holds 216 not-mine failures (170 inherited, 46 flaky) against 4,168 mine, and the chronological test split holds 18 against 1,015. Every method trades one error for the other. Pooled across repositories, the branch rule clears 145 of 216 not-mine failures but wrongly clears 1,262 of 4,168 mine failures; the message rule clears 135 and wrongly clears 848. The learned models are more conservative: logistic regression clears 74 and wrongly clears 123, LightGBM clears 31 and wrongly clears 57. On the test split, LightGBM clears 10 of 18 not-mine failures and wrongly clears 33 of 1,015 mine failures. Blame-all, what a CI server does by default, clears nothing and errs on nothing. Separating a developer's own failures from inherited and flaky ones needs more not-mine examples than BR-Bench holds, so we report the trade-off, not a working triager.

| method | test split (1,033 pairs: 18 not-mine, 1,015 mine): not-mine cleared | mine wrongly cleared | pooled leave-one-repo-out (4,384 pairs: 216 not-mine, 4,168 mine): not-mine cleared | mine wrongly cleared |
|---|---|---|---|---|
| Blame-all | 0/18 | 0/1,015 | 0/216 | 0/4,168 |
| R-branch | 11/18 | 125/1,015 | 145/216 | 1,262/4,168 |
| R-msg | 12/18 | 223/1,015 | 135/216 | 848/4,168 |
| Logistic regression | 3/18 | 30/1,015 | 74/216 | 123/4,168 |
| LightGBM | 10/18 | 33/1,015 | 31/216 | 57/4,168 |

### E3: change-aware repair on BR-Seeded

**Completeness.** The pre-registered analysis covers 70 tasks per model and variant. At the time of writing the Groq free-tier daily quota stopped both runs: gpt-oss-120b has 47 and gpt-oss-20b 45 of the 70 standard tasks replayable from the cache, the hard variant has no model run yet, and no Bedrock model was usable (all four probed candidates returned HTTP 400 "Operation not allowed"). The tasks not yet run are the last ones in task-id order (markupsafe, shopcart and a few of the others), so the partial sample is not a random subset. Everything below is therefore interim.

**Retrieval (all 70 tasks, no model).** On the standard variant the seeded edit lies inside the diff that R2 searches, so part of R2's retrieval advantage is by construction; the hard variant, which places 4-6 no-op edits inside functions the failing tests execute, measures how much remains. The seeded function is among the three chunks shown for 69/70 tasks (98.57%) with R2 against 46/70 (65.71%) with R1 on the standard variant (23 vs 0, exact McNemar p = 2.384e-07). On the hard variant R2 reaches 63/70 (90.00%) against 46/70 for R1 (17 vs 0, p = 1.526e-05), while 146 of R2's 210 chunks now sit in a distractor function (69.52%).

**Primary pre-registered test (standard variant, gpt-oss-120b, n = 47 of 70 so far).** R2 has 33/47 plausible fixes (full suite green) against 20/47 for R1 (R2 only 17, R1 only 4; exact one-sided McNemar p = 0.0036). On this partial sample R2 > R1 is supported at alpha = 0.05; the confirmatory test at n = 70 is not yet complete.

**Replication.** gpt-oss-20b, standard, n = 45 of 70: R2 29/45 against R1 10/45 (R2 only 21, R1 only 2; unadjusted one-sided p = 3.3e-05, Holm-adjusted p = 9.9e-05 in a family of 3). R3 (R2 plus up to two retries) is ahead of R2 by 4 tasks with no reversals in both models (37/47 vs 33/47 and 33/45 vs 29/45); the one-sided p is 0.0625 and the Holm-adjusted p 0.125, so this is not significant. R0 (notify only) fixes 0 tasks.

**Descriptive.** Overfit patches (target tests pass, suite fails): gpt-oss-120b R1 0, R2 3, R3 2; gpt-oss-20b R1 0, R2 3, R3 1. Exact restore: gpt-oss-120b R2 30/47, gpt-oss-20b R2 27/45. Tokens per task: gpt-oss-120b R1 1,947, R2 1,449, R3 2,363; gpt-oss-20b R1 1,701, R2 1,419, R3 2,546. Cost: USD 0 (Groq free tier); Bedrock ledger total USD 0.00.

**Pilot.** The 20-task pilot is reported separately in `paper/generated/rq4_repair.md` and is not part of the tests above.

| arm (standard variant, interim) | gpt-oss-120b (n = 47) | gpt-oss-20b (n = 45) |
|---|---|---|
| R0 notify only | 0/47 | 0/45 |
| R1 log-only | 20/47 | 10/45 |
| R2 change-aware | 33/47 | 29/45 |
| R3 R2 + up to 2 retries | 37/47 | 33/45 |

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
