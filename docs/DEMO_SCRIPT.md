# Demo script: 7 minutes, live, in front of the review panel

The home page is the **Live Lab**: a working simulation of the whole system. Everything in it is real execution shown as it
happens, or an honest replay of a recorded run (the badge at top left says which: green LIVE, amber REPLAY with the recording date).
The research results sit under **Evidence**; nothing was removed.

## Before you go in (5 minutes, once)

1. `make demo-check` the day before. It prints PASS or FAIL per check and needs no network; the last three checks cover the lab
   (engine tests, recorded runs, `/api/lab/*` on a started server).
2. `make demo-web` (builds and serves http://127.0.0.1:3000, localhost only). Open it and look at the badge: **READY · live
   available** means the Python side is reachable; **READY · replay only** means this is a static build, and the picker says why.
3. Check the model line under the top bar. If it says the key is missing or the daily quota is used up, live runs still go through
   graph, prediction, tests and triage; the Repair studio then says "unavailable" and you switch to the recorded run for that
   step (see Fallbacks). `python -m src.lab status` prints whether a key exists; it does not print the key.
4. Do one dry run of the flow below so the first run on stage is not the first run of the day (the graph of a repository is
   built once and cached).

## The flow (7 minutes)

| min | what | where |
|---|---|---|
| 0:00 | Pick itsdangerous | Step 1, repository cards: the graph appears in the centre panel |
| 0:45 | Inject a bug in front of the panel | Step 2, "Inject a bug" |
| 1:45 | Graph wave | centre panel, the moment the run starts |
| 2:30 | Test race against retest-all | panel "Test race" |
| 3:30 | Triage | panel "Triage" |
| 4:30 | Live repair and validation | panel "Repair studio" |
| 5:45 | Jenkins stage view | pipeline rail |
| 6:15 | Evidence for the numbers | Evidence tab |

### 1. Pick itsdangerous (0:45)

**Click.** The itsdangerous card. Point at the graph that appears: files, classes, functions and tests, coloured by type.
The line under it says how many nodes, edges and parse failures the builder reported.

**Say.** "This is a real Python library, 15 source files and a 297-case test suite. The graph is built by our own builder at a pinned
commit, not drawn by hand; the counts under it come from that build."

### 2. Inject a bug (1:00)

**Click.** "Inject a bug", file `src/itsdangerous/timed.py`, function `TimestampSigner.unsign`, operator `ARITH_SWAP` (line 139:
`age = self.get_timestamp() - ts_int` becomes `+`). The side-by-side preview shows exactly what will be committed. Press **Run**.

**Say.** "I am choosing a real function and a real mutation operator from the list the tool derives from the source, so this is the
same kind of change our seeded benchmark makes. Nothing is scripted: the change is committed in a scratch copy of the repository."

### 3. The wave (0:45)

**Watch.** Orange rings expand from the changed function through the graph, hop by hop, then the event log fills.

**Say.** "The rings are the blast radius: how far the change can reach in the code graph. The ranking next to it is the E1 model's,
with its top three reasons per test file."

### 4. The race (1:00)

**Point at.** The two lanes under "Test race". Each tick is one test case, green or red.

**Say.** "Both lanes are this one run. The bottom lane is the order pytest actually ran, at-risk files first. The top lane is what a
retest-all job does, alphabetical order; we did not run it separately, we computed it from the durations we measured in this run, and
the panel says so. On the rehearsal run the first failure was at position 127 of 297 risk-first and 283 alphabetical; read the numbers
off the screen, they depend on the machine."

### 5. Triage (1:00)

**Point at.** The three columns. Open one card.

**Say.** "Every failing test was re-run on the base commit. All five are 'mine': they passed before the change. If a test had already
been failing it would sit in 'inherited' and nobody should be paged for it. Counts are per unique test id; where one test method is
inherited by several subclasses the panel states how many cases that is."

### 6. Repair and validation (1:15)

**Point at.** The context chunks and why each was chosen, the token count, then the five checks ticking: patch applies, syntax
compiles, previously failing tests pass, **full suite passes**, no edits outside the allowed files. Open "Show the model's reply".

**Say.** "The model sees at most three functions: those the diff touches, ranked against the failure output. A patch is shown as
accepted only after the full suite passes with it, and the check list is the evidence. This is about 1,500 tokens."

### 7. Jenkins stage view (0:30)

**Click.** "Show as Jenkins stage view", then "Jenkinsfile".

**Say.** "This is the same run laid out the way Jenkins draws a pipeline. No Jenkins server was involved, and the Jenkinsfile is an
example we have not deployed; the point is that these are stages you add to the job you already have."

### 8. Evidence (0:45)

**Click.** Evidence tab. Read the four cards at the top, each with its source file.

**Say.** "None of the numbers on this tab come from the live run. Gate 3 is not met: the ranker is not significantly better than the
best baseline, and we report that. The repair result is the pre-registered one: R2 against R1, exact McNemar."

## Fallbacks

| problem | what you see | what to do |
|---|---|---|
| No network (clone, model) | prepared repositories still run; the model call fails | Run as usual. The Repair studio shows "model unavailable (network)" and **nothing was retried**. Pick the recorded run "Seeded task: one swapped operator, fixed and validated" and press Run to show the repair step. |
| Quota exhausted | Repair studio: "daily token quota is used up (next call possible after ...)" | Same as above. The recorded run is labelled REPLAY with its date. |
| A test run hangs | the Tests stage stays running; each pytest process has a timeout (300 s by default) | Press **Reset**: the server kills the whole process group. Use the recorded run. |
| Static build, no server | badge "READY · replay only" with the reason | Recorded runs replay in the browser, with their original timing. Add `?speed=2` to the URL to play faster. |
| Anything looks wrong | | Open **Integrity** (top bar): commands, SHAs, model and temperature, cache file, what was live and what was recorded. |

## "Jenkins can do this" in three lines

1. "Jenkins runs the stages, and it will run all of them: it reports every red test in alphabetical order. That is the top lane."
2. "BlastRadius decides the order (the bottom lane), tells you whose failure each one is (mine, inherited, flaky), and proposes a fix it
   has already verified on the full suite. Those three are the columns Jenkins does not have."
3. "It sits inside Jenkins as stages; you keep your job, your agents and your reports."

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
