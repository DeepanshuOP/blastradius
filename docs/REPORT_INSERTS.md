# Report inserts: BlastRadius 2.0

Chapter-ready text. Every number is followed by the generated file it comes from. Wording rules: no "outperforms",
"state-of-the-art", "intelligent"; "significantly better" only where the corrected p and the effect size both support it.

## Abstract (about 190 words)

BlastRadius mines GitHub Actions runs to record which tests each pull request actually broke (BR-Bench: 762 instances, 4,168
fault-revealing labels; `paper/generated/gates.md`). This project builds a change-aware CI assistant on that data in four stages:
predict which test files a change will break, run them first, triage each failure as the change's own, inherited or flaky, and
propose a patch accepted only if the full suite passes. Each stage is one experiment and each may fail. A learned ranker reaches
Recall@10 = 0.525 on a chronological test split of 148 Java instances, statistically indistinguishable from the strongest baseline
(0.522; `rq2_predictor.md`). A triage classifier trades wrongly cleared failures against cleared inherited ones on a small sample
(18 not-mine pairs in the test split; `rq3_triage.md`). On a seeded-bug benchmark of 70 tasks the change-aware retrieval places the
bug in the model's context for 69 of 70 tasks against 46 of 70 for a log-only baseline (`rq4_repair.md`). The contribution is the
dataset and the measurement, including the negative results.

## 1. Introduction: the three developer questions

When a pull request fails CI, a developer asks three questions that a CI server does not answer: *which tests should run first*,
*is this failure mine*, and *how do I fix it*. The server's own answers are the baselines of this report: retest everything in file
order, treat every failure as the change's own, and send a notification.

## 2. Problem and objectives

- RQ1 (done before 2.0): how far do co-change and history proxies diverge from execution reality (`rq1.md`)?
- RQ2 (E1): can a model trained on change and history features rank the failing test files earlier than the proxies?
- RQ3 (E2): can a failure be attributed to the change, to the base, or to flakiness from CI history alone?
- RQ4 (E3): does knowing the change improve a language model's repair of the failures the change introduced?

## 3. Architecture

Four stages over one shared feature layer (see `docs/ARCHITECTURE.md`). The same `featurize` runs on the benchmark and on a live
repository through a history interface that only returns information strictly before the prediction time; a leakage audit
re-derives a sample of feature cells from raw rows and found 0 violations in 200 cells (`leakage_audit.md`).

## 4. Implementation

- **Features (E1).** Five families: history, co-change, co-failure, path proximity and change size (24 features). 608,903 candidate
  rows for 734 instances; median 304.5 candidates per instance (`build_e1_features` output in the progress log).
- **Model.** LightGBM lambdarank, one group per instance, tuned on the validation split only (16 grid points), seeds 0-4
  (`rq2_predictor.md`, "Tuning").
- **Triage (E2).** Logistic regression and LightGBM over history, message and failure-class features, against two rules
  (`rq3_triage.md`).
- **Repair (E3).** One cached model call per attempt with at most three code chunks; patches applied strictly; accepted only if the
  full suite passes (`src/agents/repair.py`).

## 5. Results

**E1.** On the chronological test split (148 instances, all Java), the learned ranker reached Recall@10 = 0.525 (95% CI 0.447-0.599). A learned ranker restricted to readily available signals (B7, after Elsner et al.) reached 0.522. The difference is not significant (Holm-adjusted p = 0.382, Cliff's δ = 0.030, negligible), so Gate 3 is not met. Our ranker does place failing test files above the failure-history heuristic B4 (0.439; adjusted p = 0.010), but the effect is negligible (δ = 0.114); neither learned baseline separates from B4 after correction (B6 vs B4 adjusted p = 0.382, B7 vs B4 adjusted p = 0.243). The ablation explains the result: removing failure-history features costs 0.140 Recall@10 and removing path-proximity features 0.075, while removing co-change (−0.007) or co-failure (−0.001) features changes the score by less than the seed-to-seed spread (0.009-0.012). Once history and proximity are known, co-change adds no measurable signal. This agrees with RQ1, where co-change recovered 4.64% of fault-revealing tests. A random ordering reaches 0.029.

On the seeded Python repositories, which have no failure history, ordering tests with the BR-Bench model put the first failing test file at mean position 10.91, behind alphabetical order (8.11) and random order (10.37). The model's strongest signal, failure history, does not exist on a fresh repository, so a deployment needs history before ranking pays off.

**E2 (small-sample: 18 not-mine pairs in the test split).** Triage is a small-sample result: the whole corpus holds 216 not-mine failures (170 inherited, 46 flaky) against 4,168 mine, and the chronological test split holds 18 against 1,015. Every method trades one error for the other. Pooled across repositories, the branch rule clears 145 of 216 not-mine failures but wrongly clears 1,262 of 4,168 mine failures; the message rule clears 135 and wrongly clears 848. The learned models are more conservative: logistic regression clears 74 and wrongly clears 123, LightGBM clears 31 and wrongly clears 57. On the test split, LightGBM clears 10 of 18 not-mine failures and wrongly clears 33 of 1,015 mine failures. Blame-all, what a CI server does by default, clears nothing and errs on nothing. Separating a developer's own failures from inherited and flaky ones needs more not-mine examples than BR-Bench holds, so we report the trade-off, not a working triager.

**E3.** **Completeness.** The pre-registered analysis covers 70 tasks per model and variant. The standard variant is complete for both pre-registered models (gpt-oss-120b and gpt-oss-20b, 70 of 70 tasks each) and is the **confirmatory** result, pre-registered in `docs/phase/033-e3-preregistration.md`. The hard variant is **interim, run continuing**: gpt-oss-120b has 29 of 70 and gpt-oss-20b 17 of 70 tasks replayable from the cache, because the Groq free-tier daily quota stopped the runs. The exploratory third model (qwen/qwen3.8-27b, D-62) is **interim, run continuing** at 25 of 70 standard tasks. Arm R4 is **built, not run**. No Bedrock model was usable (all four probed candidates returned HTTP 400 "Operation not allowed").

**Retrieval (all 70 tasks, no model).** On the standard variant the seeded edit lies inside the diff that R2 searches, so part of R2's retrieval advantage is by construction; the hard variant, which places 4-6 no-op edits inside functions the failing tests execute, measures how much remains. The seeded function is among the three chunks shown for 69/70 tasks (98.57%) with R2 against 46/70 (65.71%) with R1 on the standard variant (23 vs 0, exact McNemar p = 2.384e-07). On the hard variant R2 reaches 63/70 (90.00%) against 46/70 for R1 (17 vs 0, p = 1.526e-05), while 146 of R2's 210 chunks now sit in a distractor function (69.52%).

**Primary pre-registered test (confirmatory, standard variant, gpt-oss-120b, n = 70).** R2 has 50/70 plausible fixes (full suite green) against 33/70 for R1 (R2 only 22, R1 only 5; exact one-sided McNemar p = 0.0007569). R2 > R1 is supported at alpha = 0.05.

**Replication (confirmatory).** gpt-oss-20b, standard, n = 70: R2 41/70 against R1 19/70 (R2 only 25, R1 only 3; one-sided p = 1.372e-05, Holm-adjusted p = 9.604e-05 in the pre-registered family of 7). R3 (R2 plus up to two retries) is ahead of R2 by 5 tasks with no reversals for gpt-oss-120b (55/70 vs 50/70; p = 0.03125, Holm-adjusted 0.09375, not significant) and by 7 for gpt-oss-20b (48/70 vs 41/70; p = 0.007812, Holm-adjusted 0.03125). R0 (notify only) fixes 0 tasks.

**Hard variant (interim, run continuing).** gpt-oss-120b, n = 29 of 70: R1 9/29, R2 17/29, R3 22/29 (R2 > R1: 8 vs 0, Holm-adjusted p = 0.01953). gpt-oss-20b, n = 17 of 70: R1 0/17, R2 9/17, R3 10/17 (R2 > R1: 9 vs 0, Holm-adjusted p = 0.01172). These are partial samples and may move.

**Third model (exploratory, interim, run continuing).** qwen/qwen3.8-27b, standard, n = 25 of 70: R1 8/25, R2 12/25, R3 13/25 (R2 only 6, R1 only 2, unadjusted two-sided exact McNemar p = 0.2891). Not part of the pre-registered family.

**Descriptive (standard, n = 70).** Overfit patches (target tests pass, suite fails): gpt-oss-120b R1 0, R2 3, R3 2; gpt-oss-20b R1 0, R2 3, R3 1. Exact restore: gpt-oss-120b R2 43/70, gpt-oss-20b R2 39/70. Tokens per task: gpt-oss-120b R1 1,813, R2 1,369, R3 2,206; gpt-oss-20b R1 1,601, R2 1,386, R3 2,525. Cost: USD 0 (Groq free tier).

The E3 evaluation uses a strict patch applier (exact match), while the PR bot uses a whitespace-tolerant applier; E3 fix rates are therefore conservative relative to the bot. The strict applier is `apply_blocks` (`src/agents/repair.py`, tested by `tests/test_agents_repair.py::test_search_must_match_exactly_once`); the tolerant one is `apply_blocks_tolerant` (`src/agents/bot.py`, tested by `tests/test_bot.py::test_strict_apply_rejects_the_real_replies_and_tolerant_apply_fixes_them`).

**Pilot.** The 20-task pilot is reported separately in `paper/generated/rq4_repair.md` and is not part of the tests above.

## 5b. Exploratory: retrieval-augmented generation (2.1)

Not pre-registered; every number is from `paper/generated/rq5_retrieval.md` (`make rag-eval`) and involves no model. We asked
whether the change-aware gain in repair is just better retrieval. It is not: whole-repo hybrid retrieval that does not know the
change places the seeded function in its top three chunks for 32 of 70 tasks (45.71%), fewer than whole-repo BM25 (46 of 70,
65.71%; exact McNemar p = 0.0026, Holm-adjusted 0.010), while retrieval restricted to the functions the diff touches reaches
69 of 70 (98.57%) on the standard variant and 63 of 70 (90.00%) on the hard variant. Combining dense vectors with the
change-aware search does not improve on BM25 alone (hard variant: 58 against 63 of 70; Holm-adjusted p = 0.453). Retrieval of past
failures for the Ask assistant finds a past failure of the same test at rank 1 for 55 of 90 eligible test-split queries
(61.11%) with BM25 or dense vectors, against 16.74% for a random order. In 15 recorded Ask answers (openai/gpt-oss-20b) no citation points outside the retrieved items and 14 cite at least
one (the other answered "not in the context"); correctness was not scored. One recorded PR-bot run on a seeded task
produced a patch that passed the full suite and was offered as a suggestion (1,495 tokens). The R4 repair arm is
implemented and tested offline; its model run is pending and is not reported here.

## 6. Limitations

- Seeded bugs are simpler than real failures, and 18 of the 19 markupsafe tasks use one operator.
- The E1 test split is chronological and contains only Java instances; Python appears only in leave-one-repo-out.
- The E2 test split has 18 not-mine pairs and no flaky ones; the pooled evaluation uses models that never saw the held-out repo but
  were configured on chronological validation data.
- Labels are observational (no gold re-execution). Gate 1 is not met: 4,168 of 5,000 labels (`gates.md`). Binding is 94.29% combined
  and 63.83% full confidence, always reported together (`binding.md`).
- E1 detection on the seeded repos: the E1 order places the first failing file at mean position 10.91, alphabetical order at 8.11
  (`rq4_repair.md`). The model was trained on Java CI history and these repos have none.
- E3: the standard variant is complete at n = 70 for both pre-registered models (confirmatory). The hard variant (29 and 17 of 70) and the
  third model (25 of 70) are interim, run continuing; arm R4 is built, not run; no Bedrock model was usable (probe: HTTP 400 "Operation not allowed").
- Corpus skew: 71 Java and 6 Python repos.

## 7. Future work

Docker re-execution of BR-Bench instances in the style of GitBug-Actions; more Python repositories; the graph feature family
(reverse reachability) for E1; a GNN on Colab; and a human-labelled holdout for parser precision.
