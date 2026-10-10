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

**E1.** The learned ranker reaches Recall@10 = 0.525 on the chronological test split (n = 148 instances, all Java), statistically
indistinguishable from the strongest baseline B7 (0.522; Holm-adjusted p = 0.2656, Cliff's delta +0.030, negligible). Gate 3 is
NOT MET (`rq2_predictor.md`). It ranks above the failure-history heuristic B4 (0.439; Holm-adjusted p = 0.006148) with a negligible
effect (+0.114). Removing co-change features changes Recall@10 by -0.007 (seed std 0.012) and co-failure features by -0.001 (std
0.009); removing history features gives -0.140 (`rq2_ablation.md`).

**E2 (small-sample: 18 not-mine pairs in the test split).** On the test split LightGBM clears 10 of 18 not-mine failures and
wrongly clears 33 of 1,015 mine failures; the rules R-branch and R-msg clear 11 and 12 of 18 at 125 and 223 wrongly cleared; logistic
regression clears 3 of 18 at 30. Pooled over leave-one-repo-out (216 not-mine, 4,168 mine) LightGBM clears 31 of 216 at 57 wrongly
cleared (`rq3_triage.md`). The numbers show a trade-off between the two kinds of error; they do not show that triage works.

**E3.** The seeded function is among the shown chunks for 69/70 tasks (change-aware) against 46/70 (log-only), exact McNemar
p = 2.384e-07; part of this is by construction, since the seeded edit lies inside the diff. Plausible-fix rates on a 20-task subset:
gpt-oss-120b R1 10/20, R2 13/20, R3 14/20 (McNemar R2 vs R1 p = 0.5078); gpt-oss-20b R1 4/20, R2 10/20, R3 13/20 (p = 0.1094). R2 is
higher in both, and the paired difference is not statistically distinguishable at this n (`rq4_repair.md`).

## 6. Limitations

- Seeded bugs are simpler than real failures, and 18 of the 19 markupsafe tasks use one operator.
- The E1 test split is chronological and contains only Java instances; Python appears only in leave-one-repo-out.
- The E2 test split has 18 not-mine pairs and no flaky ones; the pooled evaluation uses models that never saw the held-out repo but
  were configured on chronological validation data.
- Labels are observational (no gold re-execution). Gate 1 is not met: 4,168 of 5,000 labels (`gates.md`). Binding is 94.29% combined
  and 63.83% full confidence, always reported together (`binding.md`).
- E1 detection on the seeded repos: the E1 order places the first failing file at mean position 11.73, alphabetical order at 8.79
  (`rq4_repair.md`). The model was trained on Java CI history and these repos have none.
- Corpus skew: 71 Java and 6 Python repos.

## 7. Future work

Docker re-execution of BR-Bench instances in the style of GitBug-Actions; more Python repositories; the graph feature family
(reverse reachability) for E1; a GNN on Colab; and a human-labelled holdout for parser precision.
