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
(`rq2_predictor.md`). Gate 3 NOT MET: ours vs B7 Holm-adjusted p = 0.2656, Cliff's delta +0.030 (negligible).
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
Plausible fix, 20 tasks per model, R1 / R2 / R3: gpt-oss-120b 10 / 13 / 14; gpt-oss-20b 4 / 10 / 13; paired R2 vs R1 p = 0.5078 and
0.1094 (`rq4_repair.md`).
**Say:** Change-awareness puts the bug in front of the model far more often, partly because the seeded edit lies in the diff. The
repair gain is in the expected direction and not statistically distinguishable at n = 20. Seeded bugs are easier than real ones.
**Why is the LLM outside the core?** Only the repair step may call a model (D-58), with a pinned model, temperature 0, every reply
cached and replayable; E1, E2 and `make tables` contain no model call.

## Slides 21-22: limitations and what is next
- Gate 3 not met; E2 small-sample; E3 on seeded bugs; the E1 test split is Java only; the model's detection order is no better than
  alphabetical on the seeded repos (mean first-failure position 11.73 vs 8.79, `rq4_repair.md`).
- Next: re-execution of real instances (GitBug-Actions style), more Python repositories, the graph feature family, a GNN on Colab.
