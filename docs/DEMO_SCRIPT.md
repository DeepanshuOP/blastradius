# Demo script: 8 minutes, live, in front of the review panel

The home page is the **Live Lab**: a working simulation of the whole system. Everything in it is real execution shown as it
happens, or an honest replay of a recorded run (the badge at top left says which: green LIVE, amber REPLAY with the recording date).
The talk is given from **presenter mode** (the Present button): one stage per screen, projector-sized, with a plain-English
caption and a "what is real here" footnote on every screen. The research results sit under **Evidence**; nothing was removed.

## Before you go in (5 minutes, once)

1. `make demo-check` the day before. It prints PASS or FAIL per check and needs no network. The last seven cover the lab: engine
   tests (stage order, test gap, probe, PR mode), recorded runs, `/api/lab/*` on a started server, the strategy arena against a
   recorded run, the coverage plugin, every presenter screen from every recording, and the separate token ledgers.
2. `make demo-web` (builds and serves http://127.0.0.1:3000, localhost only). The badge should read **READY · live available**.
3. Check the model line under the top bar. `uv run --env-file .env python -m src.lab quota --need 4000` prints the rolling 24 h
   total of E3's ledger and the lab's ledger together against the daily cap. If the line under the top bar says the quota is used
   up, live runs still go through graph, prediction, tests, arena and triage, and the repair step says "unavailable"; use the
   recorded runs for that step (see Fallbacks).
4. Do one dry run of the flow so the first run on stage is not the first run of the day: the graph and the per-test coverage of a
   repository are built once and cached (coverage of itsdangerous takes about 2 s the first time).

## The flow (8 minutes)

| min | what | where |
|---|---|---|
| 0:00 | Pick itsdangerous; a panel member chooses a function in the graph | Scenario cards, then right-click a function node |
| 1:00 | Run the injected bug, open **Present** | top bar |
| 1:15 | The change and the blast radius | presenter screens 1 and 2 |
| 2:15 | Test race | presenter screen 3 |
| 3:00 | Strategy arena: how others choose tests, against ours | presenter screen 4 |
| 4:15 | Triage, then live repair and the five checks | presenter screens 5 and 6 |
| 5:30 | The test-gap example | recorded run "Test gap", presenter screen 7 |
| 6:45 | Evidence, and close | presenter screen 8 |

### 1. A panel member chooses the function (1:00)

**Click.** The itsdangerous card. The graph appears in rings by node type (no change yet). Ask a panel member to name a function,
or point at `TimestampSigner.unsign` in `timed.py`. Right-click it (long-press on a touch screen; on the keyboard, focus the graph,
arrow to the node, Shift+F10). The menu lists the real mutation operators for that function with a diff preview. A good choice
for a visible result is `NEGATE_COND L141` (`if age > max_age:` becomes `if not (age > max_age):`). Press **Run this bug**, then
**Present**.

**Say.** "You chose the function; the operators come from the source, not from a script. The change is committed in a scratch copy
of a real library, 15 source files and a 297-case test suite."

### 2. The change and the blast radius (1:00)

**Watch.** Screen 1: the edit on the left, the changed function at the centre of the graph on the right. Screen 2: the shockwave
sweeps out ring by ring (1, 2, 3, 4 or more hops), the paths to the at-risk test files light up, and the four most at-risk files
are listed with their three strongest reasons. In live mode a screen holds and shows "running…" until its stage has finished.

**Say.** "The rings are hop distances in our own code graph of this commit. The ranking and its reasons are the E1 model's."

### 3. The test race (0:45)

**Watch.** Two lanes fill left to right: retest-all in alphabetical order on top, BlastRadius risk-first below, with the first
failure marked in each and the time saved underneath.

**Say.** "Both lanes are this one run. The bottom lane is the order pytest actually ran. The top lane is computed from the same
measured durations in alphabetical order; we did not run it twice, and the footnote says so. On the rehearsal run of the PR 1
change (`if age > max_age` flipped to `<`), the first failure came at test 127 risk-first against 283 alphabetical. Read the numbers
off the screen; they depend on the change."

### 4. The strategy arena (1:15)

**Watch.** Screen 4: one row per strategy, each re-implemented here and scored on this run's full-suite results: retest-all,
static reachability (STARTS-style), per-test coverage (the approach Datadog TIA documents), failure history (Develocity /
Meta-style), co-change, and BlastRadius. Columns: tests run, failures caught, first failure, CI time. The caption is the takeaway
sentence, generated from the numbers.

**Say.** "None of these is the vendor's product, and none was run separately: each is computed from this run's measured results.
On the rehearsal of the PR 1 change, BlastRadius ran all 297 tests, because the ranker marked all six test files at risk, and caught
5 of 5 failures with the first at test 127; per-test coverage ran 97 tests (33%) and caught all 5. Failure history shows 'cold
start: no history' on a fresh repository: that is the honest point, and it matches BR-Bench, where history is the strongest signal
once it exists. Co-change has no history here: the prepared repositories are pinned one-commit snapshots, and the row says so."

### 5. Triage, live repair and validation (1:15)

**Watch.** Screen 5: mine, inherited and flaky, with base and head outcomes. Screen 6: the context chunks, then the patch, then the
five checks ticking: patch applies, syntax compiles, previously failing tests pass, **full suite passes**, no edits outside the
allowed files.

**Say.** "Every failing test was re-run on the base commit; a test that already failed there is inherited and nobody is paged for
it. The model sees at most three functions; a patch is accepted only after the full suite passes, and the checks are the evidence.
This is about 1,500 tokens."

### 6. The test gap (1:15)

**Click.** Esc, Reset, pick the recorded run **"Test gap: a real bug the whole suite lets through"**, Run, Present, go to screen 7
(or run it live: inject `CMP_FLIP L141` in `TimestampSigner.unsign`; it needs no model and takes about 8 s).

**Say.** "This change flips `>` to `>=` on line 141. All 297 tests pass. The panel names the tests that execute this function and
the test files that reach it in the graph: none of them tells the two versions of this line apart. Nobody had to write a bug report
for us to find that."

### 7. Evidence (0:45)

**Watch.** Screen 8: the four BR-Bench results, each with the file it was read from.

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

The model recordings of `make lab-record` (`itsdangerous-pr1`, `inherited-failure`, `hard-decoys`, `repair-arena`) are made when the
quota allows; `make lab-record` checks first and stops if 16,000 more tokens do not fit under the cap.

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
