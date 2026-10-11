# Slide notes: replacements for slides 2, 5-6, 8, 13-14, 18, 21-22 of the 25-slide deck

Numbers come from `paper/generated/` (cited). The original deck is `docs/slides/BlastRadius_Final_Review.pptx`; these replace
slide content only and do not change the slide count.

## Slide 2: the pitch
**On slide:** "When a pull request is opened, BlastRadius predicts which tests it will break, runs those first, tells the developer
which failures are really theirs, and proposes a verified fix, using models trained on real GitHub Actions failures."
**Say:** A normalised dataset was not enough output, so the dataset became the training and scoring ground for four stages.
Each stage is an experiment that may fail. I will show what came out, including what did not work.

## Slides 5-6: architecture (one slide for the stages, one for the shared feature layer)
**On slide 5:** Predict (E1) -> Run (CI executes) -> Triage (E2) -> Repair (E3), fed by BR-Bench. Diagram: `docs/ARCHITECTURE.md`.
**On slide 6:** one `featurize`, two history adapters (benchmark, live repo); every feature uses data strictly before the run.
**Say:** The same code scores the benchmark and a real repository. Time-safety is a property of the interface; a leakage audit
recomputed 200 sampled cells from raw rows and found 0 violations (`leakage_audit.md`).
**Q: Why not just Jenkins?** Jenkins is the executor and the baseline row in every experiment: retest-all, blame-all, notify-only.
BlastRadius supplies what a CI server does not: what to run first, why it failed, how to fix it. It does not gate merges.

## Slide 8: E1 results
**On slide:** Recall@10 on the chronological test split (n = 148, all Java): ours 0.525, B7 0.522, B6 0.477, B4 0.439, random 0.029
(`rq2_predictor.md`). Gate 3 NOT MET: ours vs B7 Holm-adjusted p = 0.382, Cliff's delta +0.030 (negligible).
**Say:** The learned ranker is statistically indistinguishable from the best baseline; I report that as a negative result. It ranks
above plain failure history with a negligible effect. History and path-proximity features carry the signal; removing co-change or
co-failure features moves Recall@10 by -0.007 and -0.001, inside the seed spread (`rq2_ablation.md`).
**Why LightGBM and not an LLM to predict?** An LLM is a poor fit for impact prediction: Stengg et al. (2025) report that GPT-5
performs poorly at change impact analysis, and an LLM would break the determinism of every published number (D-17).

## Slides 13-14: triage (E2), labelled small-sample
**On slide 13:** classes mine / inherited / flaky; 4,168 / 170 / 46 pairs (`rq3_triage.md`).
**On slide 14:** the confusion trade-off. Test split (18 not-mine, 1,015 mine): LightGBM clears 10 of 18 not-mine at 33 mine wrongly
cleared; R-branch 11 of 18 at 125; R-msg 12 of 18 at 223. Pooled (216 not-mine, 4,168 mine): LightGBM 31 at 57; R-branch 145 at 1,262.
**Say:** Clearing a failure that was the change's own is the dangerous error, and every method that clears many not-mine failures
also clears many mine ones. This is a trade-off, not a working triage. 18 not-mine pairs is too few to claim more.

## Slide 18: repair (E3)
**On slide:** retrieval hit rate over 70 seeded tasks: change-aware 69 (98.57%), log-only 46 (65.71%), McNemar p = 2.384e-07.
Plausible fix, standard variant, interim (47 and 45 of 70 tasks), R1 / R2 / R3: gpt-oss-120b 20 / 33 / 37 of 47; gpt-oss-20b 10 / 29 / 33
of 45; pre-registered primary test (120b) one-sided McNemar p = 0.0036 (`rq4_repair.md`). Hard variant retrieval: R2 63/70, R1 46/70.
**Say:** Change-awareness puts the bug in front of the model far more often, partly because the seeded edit lies in the diff. The
interim repair result supports the pre-registered primary hypothesis on the tasks run so far; the full 70-task test and the hard variant
are pending the next quota window. Seeded bugs are easier than real ones.
**Why is the LLM outside the core?** Only the repair step may call a model (D-58), with a pinned model, temperature 0, every reply
cached and replayable; E1, E2 and `make tables` contain no model call.

## Slide 19 (new, exploratory): retrieval study
**On slide:** hit@3 for the seeded function, 70 tasks, standard / hard: whole-repo BM25 46 / 46; whole-repo dense 21 / 21; whole-repo
hybrid 32 / 32; change-aware BM25 69 / 63; change-aware hybrid 69 / 58 (`rq5_retrieval.md`, made by `make rag-eval`).
**Say:** The reviewer's question is whether change-aware repair just has better retrieval. It does not: retrieval that is smarter but
does not know the change is worse than plain BM25 here (L3 vs L1: 3 tasks vs 17, Holm-adjusted p = 0.010), and what helps is
restricting the search to what the change touched. Exploratory; one untuned embedding model; seeded Python repos.

## Slide 20a (new, exploratory): PR bot
**On slide:** the comment from the recording run (`src/agents/demo/bot_comment.md`, excerpt; most rows elided here):

```markdown
## BlastRadius
PR #1 · `672971d66a` → `a24e22e7a1` · 297 tests · **260 failing** · first failure at position 9 of 297

### 1. Tests most at risk (e1-lgbm-v1)
| # | Test file | Score | Why |
| 4 | `tests/test_itsdangerous/test_serializer.py` | -1.96 | cochg_n_files_with_partner=0 (+0.70); hist_repo_rank=3 (-0.48); ... |

### 2. Results, risk-first
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_alt_salt[Serializer]` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |

### 3. Triage of each failure
260 mine, 0 inherited, 0 flaky (of 260 failing).

### 4. Proposed fix
Validated: the full suite passed with this patch (1 attempt(s)).
`src/itsdangerous/signer.py` line 204:
    bytes, self.digest_method(self.salt + b"signer" + secret_key).digest()   <- shown as a GitHub suggestion

<sub>model `openai/gpt-oss-20b` · 1,495 tokens · validated: full suite passed · this bot only comments</sub>
```

**Say:** One comment per pull request: tests most at risk with reasons, results risk-first, triage of each failure, and a fix only
if the full suite passed with it. It only comments; the workflow token has `contents: read` and `pull-requests: write`. One
recorded run on one seeded task, not a success rate. A patch that does not pass is shown as a collapsed diff, never as a suggestion.

## Slide 20b (new, exploratory): Ask BlastRadius
**On slide:** a question, the answer with `[S1]`-style citation chips, and the retrieved items; citation faithfulness over 15 fixed
questions (openai/gpt-oss-20b, `rq5_retrieval.md`): no citation outside the retrieved items in 15/15 answers, 14/15 cite at least one,
1 answered "not in the context"; failure-history retrieval (same test_id: hit@1 61.11% BM25 / dense, 58.89% hybrid vs 16.74% chance).
**Say:** The model may answer only from retrieved context and must cite it; the check we run is that every citation points at a
retrieved item, not that the answer is right (correctness was not scored).

## Slides 21-22: limitations and what is next
- Gate 3 not met; E2 small-sample; E3 on seeded bugs; the E1 test split is Java only; the model's detection order is no better than
  alphabetical on the seeded repos (mean first-failure position 10.91 vs 8.11, `rq4_repair.md`).
- Next: re-execution of real instances (GitBug-Actions style), more Python repositories, the graph feature family, a GNN on Colab.
