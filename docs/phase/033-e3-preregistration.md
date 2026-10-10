# Phase 033: E3 full-size analysis, pre-registration

Written and committed before any new LLM call of the full-size runs. Date: 2026-10-10. Decided by Deepanshu (spending rule
and plan), written by the Claude Code session on branch `upgrade-2.0`.

## What is fixed

- **Code under test.** `src/agents/repair.py` at commit `20a8176f206b8f6d220af334fa809ff49d641c28` (last commit touching the file; the working tree has no
  uncommitted change to it). Prompts, retrieval, arms R0-R3 and the acceptance rule (full suite green, minus tests already
  failing at the base) are unchanged for this analysis. Retry feedback is masked by `clean_feedback` (same commit).
- **Tasks.** All 70 standard tasks (`eval/seeded/tasks.jsonl`) and all 70 hard-variant tasks (`eval/seeded/tasks_hard.jsonl`,
  the same 70 mutants with 4-6 additional no-op edits inside functions the failing tests execute).
- **Arms.** R0 notify only, R1 log-only retrieval, R2 change-aware retrieval, R3 = R2 plus up to two retries.
- **Models.**
  - primary: `openai/gpt-oss-120b` (Groq, free tier)
  - replications: `openai/gpt-oss-20b` (Groq) and one frontier model on Amazon Bedrock, chosen by the probe in Step 4 and named in
    `docs/phase/033-e3-bedrock-model.md` before its first non-probe call.
- **Sampling.** Temperature 0, max completion 1,500 tokens. Groq also sets seed 0; Bedrock Converse has no seed, so Bedrock runs are
  not bit-reproducible and the cache is the record.

## Primary hypothesis

On the **standard variant, primary model, all 70 tasks**: the R2 plausible-fix rate is greater than the R1 plausible-fix rate.
Plausible fix = the patch applies and the full suite passes. Test: exact McNemar (binomial on the discordant pairs, R2-only vs
R1-only), **one-sided**, alpha = 0.05. This is the only confirmatory test at the unadjusted level.

## Secondary tests (Holm-corrected together, family size 11)

1. R2 > R1, one-sided exact McNemar, for each other (model, variant) cell: standard x gpt-oss-20b, standard x Bedrock model,
   hard x gpt-oss-120b, hard x gpt-oss-20b, hard x Bedrock model (5 tests).
2. R3 > R2, one-sided exact McNemar, for each of the 3 models x 2 variants (6 tests).

Cells that could not be completed (quota, spending cap) are reported with the n that was run and are excluded from the Holm
family, which is then recomputed over the tests actually performed; the file states the family size used.

## Also reported (descriptive, no test)

Exact-restore rate, overfit count (target tests pass, suite fails), edited-seeded-file and edited-seeded-function rates, patches
and chunks landing in a distractor file, per-operator and per-repo plausible-fix rates, tokens per task, USD per model and the
USD total in `eval/llm_cache/usage.jsonl`. Retrieval hit rate R1 vs R2 (no model) on both variants with exact McNemar.

## What is not confirmatory

The n = 20 runs of 2026-10-10 (gpt-oss-120b and gpt-oss-20b on a 20-task operator-stratified subset of the standard variant)
were looked at before this document was written. They are reported separately as a **pilot** and are not part of any test
above. The 20 pilot tasks are part of the 70, and their cached replies are reused in the full-size run; the pilot is therefore
not independent of the confirmatory sample, which is why it is excluded from inference, not from the table of rates.

## Known threats stated in advance

- Seeded bugs are simpler than real ones; the operator mix is uneven (markupsafe is 18 of 19 NEGATE_COND).
- On the standard variant the seeded edit lies inside the diff R2 searches, so part of R2's retrieval advantage is by
  construction; the hard variant measures how much remains.
- Tasks within a repository are not independent; McNemar treats them as exchangeable pairs.
