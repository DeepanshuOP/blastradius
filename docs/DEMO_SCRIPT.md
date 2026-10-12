# Demo script: 10 minutes for the review panel

Run `make demo-web` (site at http://127.0.0.1:3000) and open the page in a browser. The page is one scroll with a table of contents
on the left (a menu at the top on a phone). Every number below is on the page and comes from a generated file named in the page. If
the network is down, nothing here breaks: the page replays recorded data, and the steps that are live say so on screen. Run
`make demo-check` the day before; it prints PASS or FAIL per check and needs no network.

| min | section | what to click |
|---|---|---|
| 0:00 | Overview | scroll slowly |
| 1:30 | Data | funnel figure, corpus table, Known limits |
| 3:00 | Results | RQ1, E1, E2, E3 |
| 5:30 | Compare | papers matrix, products matrix, cost |
| 7:30 | Try it | Agent scenarios, live-run replay, Ask |
| 9:00 | Use it | workflow YAML, live PR link |

## 1. Overview (1.5 min)

**Click.** Stay on Overview. Point at Figure 1 (the pull request 1 comment), then Figure 2 (the pipeline), then the three findings.
Click "Open the live pull request".

**Say.** "A pull request flipped one comparison in itsdangerous. Five of 297 tests failed; BlastRadius traced them to
`src/itsdangerous/timed.py:141`, proposed the one-line fix, and showed it only because all 297 tests passed with it. The pipeline has four
stages, predict, run, triage, repair, all measured on BR-Bench, a dataset of tests that really failed in GitHub Actions."

**If the network is down.** The figure is recorded data; the live-PR link will not open, so say the comment text is the recorded one.

## 2. Data (1.5 min)

**Click.** Funnel figure, the corpus table, then open "Known limits".

**Say.** "A test is labelled when it fails at head, did not fail at the base commit, and is not flaky. The funnel goes from 165,349
discovered runs to 762 instances with a strict label, 4,168 labels. We did not reach the 5,000-label gate, and binding is
94.29% combined but 63.83% at full confidence; we always show both. The corpus is 35 Java and 2 Python repositories, and parser
precision was measured on development sets only."

**If the network is down.** No change; this section is static.

## 3. Results (2.5 min)

**Click.** RQ1 table, E1 figure and table, E2 table, E3 tables (120b standard first).

**Say.** "Co-change names 4.64% of the failing tests in its top 10 and failure history 39.44%, so history beats co-change. The E1
ranker reaches Recall@10 0.525 against 0.522 for the best baseline; the difference is not significant, Gate 3 is not met, and that is a
result, not a failure of the project. Triage is a small-sample trade-off: 18 not-mine pairs in the test split. Repair is the
confirmatory result: on 70 seeded tasks, change-aware repair fixed 50 against 33 for log-only, exact one-sided McNemar p = 0.0007569,
pre-registered in docs/phase/033. The hard variant and the third model are interim and still running; R4 is built but not run."

**If the network is down.** No change; results are read from files.

## 4. Compare (2 min)

**Click.** Papers matrix (click one "not reported" cell and one BlastRadius cell), products matrix (click the Develocity "works without
project history" cell), then the same-data table, the "other data" banner, and Cost.

**Say.** "Each mark has a source; a BlastRadius yes names the test that proves it. The commercial tools are shown only as their own
documentation describes them, with the vendor URL on each cell; anything their pages do not state says 'not documented'. Same-data
results and other papers' numbers are never in one table. We paid USD 0.00; at list prices the tokens would cost a fraction of a cent per task."

**If the network is down.** The vendor URLs will not open; the cell text and the URL are still shown.

## 5. Try it (1.5 min)

**Click.** Agent scenarios: pick the clean scenario, "Run the agents". Live-run replay: "Replay run". Ask: read the mode line, open
one recorded answer and click a citation chip.

**Say.** "These replay recordings, nothing is executed. Ask says on screen whether it is live or recorded; with a key and the
network it calls the model, otherwise it shows the recorded answers. Citation checks say only that citations point at retrieved
items, not that answers are correct."

**If the network is down.** This is the fallback: Ask shows "recorded answers", the rest is unchanged. "Analyze repository" needs
a clone and a local server; if it is unavailable, use the command-line twin shown on the page.

## 6. Use it (1 min)

**Click.** Copy the workflow YAML; show the Jenkinsfile and the CLI lines.

**Say.** "Three ways in: a GitHub Action that comments on every pull request, a Jenkins stage where Jenkins stays the executor, and a
command line. The bot only comments; it never pushes or merges, and that is a tested claim in the Compare safety panel."

**If the network is down.** Static content; the live-PR link will not open.

## Likely panel questions

1. **"Jenkins already does this."** Jenkins and GitHub Actions run the suite and report every red test; that is the retest-all row
   (B0). On the BR-Bench test split, retest-all finds 0.119 of the failing test files in the first 10% of the suite against 0.735 for the ranker
   (`paper/generated/rq2_predictor.md`, Recall@10%), and it does not say which failures are yours. In our design Jenkins stays the executor.

2. **"Why is the LLM not in your core pipeline?"** Reproducibility: E1, E2, features, labels and `make tables` call no model
   (D-17, D-58), a safety test enforces it (`tests/test_safety_claims.py`), and every number regenerates offline. Only the repair step
   calls a model, with replies cached and replayable.

3. **"Do you beat other papers?"** We make no such claim. Their numbers are on other data and sit in a separate table with a banner
   (Compare, "Published numbers on other data"). Our comparisons are on the same split: the ranker is not significantly above the best
   baseline (Holm-adjusted p = 0.3823).

4. **"Why seeded bugs?"** Real failures have no known fix location, so repair needs a controlled setting: one mutation per task, 70 tasks,
   full suite as the judge. Seeded bugs are simpler than real ones, so repair rates do not transfer; the real-failure evidence is the
   dataset and E1/E2. The hard variant adds no-op edits to test whether retrieval still works (`rq4_repair.md`).

5. **"What does Gate 3 not met mean?"** Gate 3 required the ranker to beat the best baseline with an adjusted p below 0.05 and
   |Cliff's delta| of at least 0.147. We got 0.525 against 0.522, p = 0.3823, delta +0.030 (`rq2_predictor.md`, "Gate 3 verdict"). It means
   the predictor is not a contribution; the dataset and the measurement are. The paper reports it as a negative result.

6. **"Is it safe to let it change code?"** It does not change code: the bot comments with a suggestion and never pushes or merges
   (`tests/test_safety_claims.py::test_bot_never_merges_pushes_or_approves`, workflow permission `contents: read`). A patch is shown
   only after the full suite passes; 3 of 70 R2 patches for each model passed the target tests but failed the suite (overfit) and
   were rejected.

7. **"What did it cost?"** USD 0.00 paid; the tokens were on the Groq free tier (`cost_report.md`). The recorded PR-bot run used
   one model call and 1,495 tokens; at list prices the E3 runs cost fractions of a cent per task.

8. **"How does someone use it tomorrow?"** Copy the workflow from the Use it section into a repository, set one secret, open a pull
   request; or run the CLI. It needs failure history to rank well: on fresh repositories the ranker puts the first failing file at mean position
   10.91 against 8.11 for alphabetical order (`rq4_repair.md`, Detection).

9. **"What is your novelty?"** The dataset: per-test, per-pull-request labels from real GitHub Actions runs with the base run
   subtracted and flaky tests filtered (4,168 strict labels, DOI 10.5281/zenodo.23250262), and honest measurement on it, including the
   negatives. The pre-registered repair test is the other result: change-aware context raised plausible fixes from 33 to 50 of 70.

10. **"What are the limits?"** Gate 1 not met (4,168 of 5,000 labels); binding 94.29% combined and 63.83% at full confidence;
    parser precision measured on development sets only; the corpus is mostly Java and the E1 test split is Java only; triage rests
    on 18 not-mine test pairs; seeded repair bugs are easier than real ones; the hard variant and the third model are interim.
    All are on the page under Data, Known limits and in `docs/RESULTS_2.md`.
