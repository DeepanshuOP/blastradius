# BlastRadius 2.0: results

Every number below is copied from a generated file (`paper/generated/rq2_predictor.md`, `rq2_ablation.md`, `rq3_triage.md`,
`rq4_repair.md`). Two tables, never merged: Table 1 compares methods on **the same data** (BR-Bench or BR-Seeded); Table 2 is
**context from other papers' data** and is not a comparison. Per D-56, E1 does not go into the MSR 2027 paper (Gate 3 not met).
E3 numbers come from cached model replies and are not part of `make tables`. The standard-variant E3 result (n = 70) is confirmatory, pre-registered in `docs/phase/033`.

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

**Completeness.** The pre-registered analysis covers 70 tasks per model and variant. The standard variant is complete for both pre-registered models (gpt-oss-120b and gpt-oss-20b, 70 of 70 tasks each) and is the **confirmatory** result, pre-registered in `docs/phase/033-e3-preregistration.md`. The hard variant is **interim, run continuing**: gpt-oss-120b has 29 of 70 and gpt-oss-20b 17 of 70 tasks replayable from the cache, because the Groq free-tier daily quota stopped the runs. The exploratory third model (qwen/qwen3.8-27b, D-62) is **interim, run continuing** at 25 of 70 standard tasks. Arm R4 is **built, not run**. No Bedrock model was usable (all four probed candidates returned HTTP 400 "Operation not allowed").

**Retrieval (all 70 tasks, no model).** On the standard variant the seeded edit lies inside the diff that R2 searches, so part of R2's retrieval advantage is by construction; the hard variant, which places 4-6 no-op edits inside functions the failing tests execute, measures how much remains. The seeded function is among the three chunks shown for 69/70 tasks (98.57%) with R2 against 46/70 (65.71%) with R1 on the standard variant (23 vs 0, exact McNemar p = 2.384e-07). On the hard variant R2 reaches 63/70 (90.00%) against 46/70 for R1 (17 vs 0, p = 1.526e-05), while 146 of R2's 210 chunks now sit in a distractor function (69.52%).

**Primary pre-registered test (confirmatory, standard variant, gpt-oss-120b, n = 70).** R2 has 50/70 plausible fixes (full suite green) against 33/70 for R1 (R2 only 22, R1 only 5; exact one-sided McNemar p = 0.0007569). R2 > R1 is supported at alpha = 0.05.

**Replication (confirmatory).** gpt-oss-20b, standard, n = 70: R2 41/70 against R1 19/70 (R2 only 25, R1 only 3; one-sided p = 1.372e-05, Holm-adjusted p = 9.604e-05 in the pre-registered family of 7). R3 (R2 plus up to two retries) is ahead of R2 by 5 tasks with no reversals for gpt-oss-120b (55/70 vs 50/70; p = 0.03125, Holm-adjusted 0.09375, not significant) and by 7 for gpt-oss-20b (48/70 vs 41/70; p = 0.007812, Holm-adjusted 0.03125). R0 (notify only) fixes 0 tasks.

**Hard variant (interim, run continuing).** gpt-oss-120b, n = 29 of 70: R1 9/29, R2 17/29, R3 22/29 (R2 > R1: 8 vs 0, Holm-adjusted p = 0.01953). gpt-oss-20b, n = 17 of 70: R1 0/17, R2 9/17, R3 10/17 (R2 > R1: 9 vs 0, Holm-adjusted p = 0.01172). These are partial samples and may move.

**Third model (exploratory, interim, run continuing).** qwen/qwen3.8-27b, standard, n = 25 of 70: R1 8/25, R2 12/25, R3 13/25 (R2 only 6, R1 only 2, unadjusted two-sided exact McNemar p = 0.2891). Not part of the pre-registered family.

**Descriptive (standard, n = 70).** Overfit patches (target tests pass, suite fails): gpt-oss-120b R1 0, R2 3, R3 2; gpt-oss-20b R1 0, R2 3, R3 1. Exact restore: gpt-oss-120b R2 43/70, gpt-oss-20b R2 39/70. Tokens per task: gpt-oss-120b R1 1,813, R2 1,369, R3 2,206; gpt-oss-20b R1 1,601, R2 1,386, R3 2,525. Cost: USD 0 (Groq free tier).

The E3 evaluation uses a strict patch applier (exact match), while the PR bot uses a whitespace-tolerant applier; E3 fix rates are therefore conservative relative to the bot. The strict applier is `apply_blocks` (`src/agents/repair.py`, tested by `tests/test_agents_repair.py::test_search_must_match_exactly_once`); the tolerant one is `apply_blocks_tolerant` (`src/agents/bot.py`, tested by `tests/test_bot.py::test_strict_apply_rejects_the_real_replies_and_tolerant_apply_fixes_them`).

**Pilot.** The 20-task pilot (gpt-oss-120b R1/R2/R3 10/13/14 of 20; gpt-oss-20b 4/10/13 of 20) is reported separately in `paper/generated/rq4_repair.md`, labelled pilot, and is not part of the tests above.

| arm (standard variant, n = 70, confirmatory) | gpt-oss-120b | gpt-oss-20b |
|---|---|---|
| R0 notify only | 0/70 | 0/70 |
| R1 log-only | 33/70 | 19/70 |
| R2 change-aware | 50/70 | 41/70 |
| R3 R2 + up to 2 retries | 55/70 | 48/70 |

- Seeded bugs are simpler than real ones, and the operator mix is uneven (markupsafe: 18 of 19 tasks are NEGATE_COND).

## Exploratory: RAG (BlastRadius 2.1, not pre-registered)

Source: `paper/generated/rq5_retrieval.md`, produced by `make rag-eval` (not `make tables`); no model is involved in
these numbers. Everything in this section is exploratory. Arm R4 has not been run against a model yet, so no repair number exists for it; the Ask
and PR-bot recording runs are described at the end of this section.

**Does smarter retrieval replace knowing the change? No, on these 70 seeded tasks.** Whole-repo hybrid retrieval (L3, BM25
plus dense vectors, no knowledge of the change) puts the seeded function among its top three chunks for 32 of 70 tasks
(45.71%), below whole-repo BM25 (L1, 46 of 70, 65.71%): 17 tasks only BM25 finds, 3 only hybrid (exact McNemar p = 0.0026,
Holm-adjusted p = 0.010 in a family of 4). Knowing the change (L4, BM25 over the functions the diff touches) reaches 69 of 70
(98.57%) on the standard variant and 63 of 70 (90.00%) on the hard variant. Dense retrieval alone (L2) finds 21 of 70 (30.00%).

| mode (top 3 chunks, 70 tasks) | standard hit@3 | hard hit@3 | hard MRR |
|---|---|---|---|
| L1 BM25, whole repo (= R1) | 46/70 (65.71%) | 46/70 (65.71%) | 0.581 |
| L2 dense, whole repo | 21/70 (30.00%) | 21/70 (30.00%) | 0.308 |
| L3 hybrid, whole repo | 32/70 (45.71%) | 32/70 (45.71%) | 0.426 |
| L4 BM25, touched functions (= R2) | 69/70 (98.57%) | 63/70 (90.00%) | 0.800 |
| L5 hybrid, touched functions | 69/70 (98.57%) | 58/70 (82.86%) | 0.637 |

Adding dense vectors to the change-aware retriever does not help: on the hard variant L5 has the seeded function in its top
three for 58 tasks against 63 for L4 (3 only L5, 8 only L4; unadjusted p = 0.2266, Holm-adjusted p = 0.4531, not
distinguishable from no difference with 70 tasks). The change-aware gain in E3 is therefore not explained by better generic
retrieval; most of it comes from restricting the search to what the change touched. This is a statement about this
embedding model (`jina-embeddings-v2-base-code`, untuned, queries are test output) and these Python repositories.

**Failure-history retrieval (the Ask source; 709 test-split failures with a message, strictly earlier runs of the same
repository).** Retrieving a past failure of the same test_id (90 queries have one): hit@1 61.11% for BM25 and dense, 58.89%
for hybrid, against 16.74% for a random order; hit@5 76.67% / 71.11% / 75.56% against 29.14%. Retrieving a past failure
of the same failure class is nearly saturated and only modestly above chance at rank 1 (hybrid 94.92% against 52.01%).

**Ask: citation faithfulness (15 fixed questions, answers recorded once with openai/gpt-oss-20b, `rq5_retrieval.md`).** The
assistant is shown 8 retrieved items and told to answer only from them and cite each claim. In all 15 answers no `[Sk]` points
outside the retrieved items; 14 of 15 cite at least one item (test-failure 4/5, impact 5/5, history 5/5) and the 15th answered
"not in the context". This scores citation hygiene only: whether an answer is correct was not scored, and several impact
answers cite only the E1-ranker block. Recording cost 17,969 tokens in all (sum of the 15 usage records) (`eval/llm_cache/ask_openai_gpt-oss-20b.jsonl`).

**PR bot: one recording run** on seeded task `itsdangerous-ARITH_SWAP-00` (`src/agents/demo/bot_comment.md`, replays
offline from `eval/llm_cache/bot_openai_gpt-oss-20b.jsonl`). The seeded edit breaks the signer, so 260 of 297 tests fail and
all 260 are triaged mine; the model proposed one one-line patch on its first attempt (1,495 tokens), the full suite passed
with it, and the bot offered it as a suggestion on `src/itsdangerous/signer.py` line 204. This is one run on one seeded task,
not a rate.

**Not yet run.** Arm R4 against a model (`make repair-run ... ARMS=R4`, operator-run after the confirmatory runs) and the
third model (`qwen/qwen3.8-27b`, exploratory, D-62), so no repair rate exists for either.

## Table 2: context only, different data

| work | reported result | data |
|---|---|---|
| T-TS (Plyusnin et al., 2025) | recall 0.95 at 15% of tests | proprietary |
| Pan & Pradel, ISSTA 2021 | suite-level AUC gain of 13.9% | 242 projects |
| LogSage (Xu et al., 2025) | RCA precision above 98% | 367 failures |
| CI-Bench (Nabil et al., 2026) | 13-36% repair success | 100 BugSwarm failures |
| CI-Repair-Bench (Muna et al., 2026) | Pass@1 7.9-18.9% | 567 GitHub Actions failures |

These come from different data; we do not claim to beat them.
