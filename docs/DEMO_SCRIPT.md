# Demo script: 8 minutes, live, in front of the review panel

The home page is the **Live Lab**: a working simulation of the whole system. Everything in it is real execution shown as it
happens, or an honest replay of a recorded run (the badge at top left says which: green LIVE, amber REPLAY with the recording
date). The main screen carries almost no prose: explanations sit behind the **Explain** switch and the small **i** buttons.
The talk opens with the **Challenge** and is given from **presenter mode** (the Present button): one stage per screen,
projector-sized, one caption line each, and a "what is real here" popover on every screen. The research results sit under
**Evidence**, as cards with a small chart; the tables are behind "Show table".

## Before you go in (5 minutes, once)

1. `make demo-check` the day before. It prints PASS or FAIL per check and needs no network. The lab checks are: engine tests
   (stage order, test gap, probe, PR mode), recorded runs, `/api/lab/*` on a started server, the strategy arena and its columns
   against a recorded run, the history row with and without runs of the same diff, the BlastRadius order against the
   hand-computed order, the coverage plugin, every presenter screen from every recording, the challenge seed, the text budget of
   the main screen and the separate token ledgers.
2. `make demo-web` (builds and serves http://127.0.0.1:3000, localhost only). The badge should read **READY · live available**.
3. Check the model line under the top bar. `uv run --env-file .env python -m src.lab quota --need 4000` prints the rolling 24 h
   total of E3's ledger and the lab's ledger together against the daily cap. If the quota is used up, live runs still go through
   graph, prediction, tests, arena and triage, the repair step says "unavailable", and **Fix it** in the challenge is disabled with
   that reason; use the recorded runs for that step (see Fallbacks).
4. Press **Reset history** in the arena tab once before you start, so that the failure-history row on stage learns only from what
   happens on stage. Then do one dry run, so the first run on stage is not the first run of the day: the graph and the per-test
   coverage of a repository are built once and cached (coverage of itsdangerous takes about 2 s the first time).

## The flow (8 minutes)

| min | what | where |
|---|---|---|
| 0:00 | **Challenge**: "Will the tests catch this bug?", a panel member answers, live run, reveal | Challenge button, itsdangerous |
| 1:30 | The change and the blast radius | **Present**, screens 1 and 2 |
| 2:30 | The test race | screen 3 |
| 3:15 | The arena race: the answer to "Jenkins does this" | screen 4 (or the Strategy arena tab) |
| 4:45 | Triage, then repair and the five checks (**Fix it** in the challenge, or the recorded PR 1 run) | screens 5 and 6 |
| 6:00 | The test gap | challenge seed 135, or the recorded "Test gap" run, screen 7 |
| 7:15 | Evidence, and close | screen 8 |

### 1. The challenge (1:30)

**Click.** Pick itsdangerous, press **Challenge**. The card shows a function and an operator drawn by a seeded generator, and the
seed. Seed 7 draws `NEGATE_COND` in `HMACAlgorithm.__init__` (`digest_method is None` becomes `not (digest_method is None)`);
seed 135 draws `CMP_FLIP` on line 141 of `TimestampSigner.unsign`. Ask a panel member: **Will the tests catch this bug?** Press
their answer. The change is committed in a scratch copy and the whole suite runs. The reveal says caught or survived, whether
they were right, the session tally of correct guesses, where BlastRadius and retest-all reached their first failure, and, if the
bug survived, the test-gap card. A panel member who prefers to choose the function themselves presses **Pick the function myself**,
then clicks a function in the graph (right-click, long-press, or arrow to the node and Shift+F10).

**Say.** "Nobody rehearsed this bug: a seeded random draw over every function of the library that has a mutation, and the seed is
on screen, so you can ask for the same draw again. No model is called unless I press **Fix it**."

**Rehearsal numbers (read the real ones off the screen).** Seed 7: 4 tests fail; BlastRadius reaches its first failure at test 5,
retest-all at test 119 of 297. Seed 135: all 297 tests pass, a test gap.

### 2. The change and the blast radius (1:00)

**Click.** Present. **Watch.** Screen 1: the edit on the left, the changed function at the centre of the graph on the right.
Screen 2: the shockwave sweeps out ring by ring, the paths to the at-risk test files light up, and the most at-risk files are
listed with their three strongest reasons. In live mode a screen holds and shows "running…" until its stage has finished.

**Say.** "The rings are hop distances in our own code graph of this commit. The ranking and its reasons are the E1 model's."

### 3. The test race (0:45)

**Watch.** Two lanes fill left to right: retest-all in alphabetical order on top, BlastRadius risk-first below, with the first
failure marked in each. The caption states both positions; it does not claim a win.

**Say.** "Both lanes are this one run. The bottom lane is the order pytest actually ran. The top lane is computed from the same
measured durations in alphabetical order; we did not run it twice, and the popover says so."

### 4. The arena race: "Jenkins does this" (1:30)

**Watch.** Screen 4, or the **Strategy arena** tab: one lane per strategy, all on one clock built from this run's measured
durations, a flag where each lane meets its first failure, then a podium by time to first failure with the cost of each. The table
is behind **Details**. Orderers (retest-all, BlastRadius) run every test and are judged by tests and time until the first failure;
selectors (static reachability, per-test coverage, failure history, co-change) run fewer tests and can miss failures. The **Needs**
column says what each one requires first: nothing; a code graph; an instrumented coverage run at the base with its measured cost;
earlier runs; git history; a graph and a model.

**Say.** "Jenkins runs every test in a fixed order: that is the first lane. The other lanes are the approaches people use instead,
re-implemented here and scored on this run's measured results; none is a vendor's product and none was run separately. On the PR 1
change (`if age > max_age` flipped to `<`, recorded 2026-10-12) retest-all meets its first failure at test 283 after 886 ms,
BlastRadius at test 17 after 97 ms; per-test coverage needs an instrumented run first (2.5 s here) and then selects 97 tests."

**The failure-history row, said plainly.** "Failure history learns from earlier lab runs. Earlier runs of this very diff are
excluded by default, because with them it has seen the answer. The toggle shows both: on the recorded PR 1 run, excluding the four
earlier runs of the same diff, history selects 3 tests and catches 0 of 5; including them, it selects 8, catches 5 of 5 and meets
the first failure at test 1. Both are real; we show the excluded one." (Numbers: `itsdangerous-pr1`, history 6 earlier runs,
4 of them on this same diff.)

**Not always a win.** On the recorded hard-variant run (`hard-decoys`, 30 failing cases) retest-all meets its first failure at
test 45 after 151 ms and BlastRadius at test 99 after 739 ms. Say so if asked; it is in the recording.

### 5. Triage, repair and validation (1:15)

**Watch.** Screen 5: mine, inherited and flaky, with base and head outcomes. Screen 6: the context chunks, then the patch, then the
five checks ticking: patch applies, syntax compiles, previously failing tests pass, **full suite passes**, no edits outside the
allowed files. In the challenge, **Fix it** does the same live (about 600 to 1,500 tokens).

**Say.** "Every failing test was re-run on the base commit; a test that already failed there is inherited and nobody is paged for
it. The model sees at most three functions; a patch is accepted only after the full suite passes, and the checks are the evidence."

### 6. The test gap (1:15)

**Click.** Challenge seed 135, or Reset, the recorded run **"Test gap: a real bug the whole suite lets through"**, Present, screen 7.

**Say.** "This change flips `>` to `>=` on line 141. All 297 tests pass. The panel names the tests that execute this function and
the test files that reach it in the graph: none of them tells the two versions of this line apart. Nobody had to write a bug report
for us to find that."

### 7. Evidence (0:45)

**Watch.** Screen 8: the four BR-Bench results, each with a small chart and the file it was read from.

**Say.** "None of these numbers comes from the live run. RQ1: co-change recovers 4.64% of failing test files at k = 10, failure
history 39.44%. Gate 3 is not met: the ranker is not significantly better than the best baseline, and we report that. The repair
result is the pre-registered one: R2 against R1, exact McNemar."

## Fallbacks

| problem | what you see | what to do |
|---|---|---|
| Quota exhausted | top line: "Repair is unavailable: the daily token quota of … is used up"; the repair-arena toggle is disabled with that reason | Run as usual: graph, prediction, tests, arena and triage are live. For screen 6 pick the recorded run "Seeded task: one swapped operator, fixed and validated" (REPLAY, with its date). |
| No network (clone, model) | prepared repositories still run; the model call fails | Same as above. The Repair tab shows "model unavailable (network)"; nothing was retried. |
| A test run hangs | the Tests stage stays running; each pytest process has a timeout (300 s by default) | Press **Reset**: the server kills the whole process group. Use a recorded run. |
| Static build, no server | badge "READY · replay only" with the reason | Recorded runs replay in the browser, with their original timing; `?speed=2` plays faster. Presenter mode works on a replay. |
| Anything looks wrong | | Open **Integrity** (top bar or the last result tab): commands, SHAs, model and temperature, cache and ledger files, what was live and what was recorded. |

The model recordings of `make lab-record` (`itsdangerous-pr1`, `inherited-failure`, `hard-decoys`, `repair-arena`, plus `test-gap`
without a model) were made on 2026-10-12 with gpt-oss-120b; `make lab-record` checks the quota first and stops if 16,000 more
tokens do not fit under the cap. Their chips are labelled **Replay** and the badge says REPLAY with the date.

## "Jenkins can do this" in three lines

1. "Jenkins runs every test in a fixed order and reports every red one: that is the **Retest-all** row of the arena, first failure
   at its alphabetical position, 100% of the suite every time."
2. "The arena puts that row next to static reachability, per-test coverage, failure history, co-change and ours, on the same
   change and the same measured results, so you can see what each one buys and what it misses."
3. "BlastRadius adds the order, whose failure each one is, and a fix it has verified on the full suite, as stages inside the
   Jenkins job you already have."

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
