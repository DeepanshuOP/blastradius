# HANDOFF-019 — resuming the `exact_green` Java sample

**Written:** 1 September 2026, mid-sweep, after Phase 018.
**Purpose:** let a session with **no prior context** resume segment 2 correctly.
**Every number below was read off disk at handoff time.** Re-verify before
trusting it — the commands to do so are given. This file outranks nothing; if it
disagrees with `docs/ROADMAP.md` or `docs/SCHEMAS.md`, they win.

---

## 0. What this sweep is

Phase 016-A found that `exact_green` was assigned from a base run's
`conclusion == "success"` alone, with no base log ever parsed. A run that
executes a linter and no tests concludes `success`, so that assignment asserts
`T_base_fail = ∅` on no evidence — the trap integrity invariant 6 and ROADMAP
§21.3 forbid. 4,245 instances carried it.

`analysis/verify_exact_green.py` re-derives each verdict by enumerating **every**
job of the base run and parsing every log it can retrieve. Python is finished.
**Java is being sampled, not censused** — a full Java census measured out at
~13 hours, which is not a thing to run.

---

## 1. Resume command for segment 2

**Confirm the checkpoint first. Do not skip this.**

```bash
cd /home/shree/blastradius
uname -s && pwd && uv run python --version      # Linux, /home/shree/blastradius, 3.11.15
ps -o pid,etime,cmd -C python3 --no-headers     # MUST be empty: no daemon, no stray sweep

uv run python -c "
import pandas as pd
df = pd.read_parquet('data/interim/exact_green_verification.parquet')
v = df[df['base_parse_status'] != 'not_processed']
print('base runs verified:', len(v.drop_duplicates(subset=['repo','base_run_id'])))
print('instances covered :', len(v), 'of', len(df))
"
```

Expected before segment 2: **275 base runs, 878 of 4,245 instances.** If it
reads differently, something ran that should not have — stop and report rather
than continuing.

Then run **one** segment, foreground, and stop:

```bash
timeout 560 env PYTHONUNBUFFERED=1 uv run --env-file .env \
  python analysis/verify_exact_green.py \
  --sample-java 107 --seed 20260901 \
  --time-budget-s 420 --as-of 2026-08-29T14:13:00Z
```

- `--seed 20260901` is **fixed**. Changing it redraws a different sample and
  invalidates every rate already collected.
- `--sample-java 107` is the size of the draw from the unswept Java set, made
  once and reproducible from the seed. It is not "107 more each time" — the
  script re-derives the same 107 and skips those already done.
- The outer `timeout 560` exceeds `--time-budget-s 420` deliberately: the budget
  is only checked *between* base runs, and one run has taken over 110 s. The
  checkpoint writes every 25 runs, so a kill loses at most 25.
- After each segment: print cumulative count, elapsed, runs/min, and **STOP for
  the operator.** Do not chain segments.

Report the buckets with:

```bash
uv run python analysis/verify_exact_green.py --report-only
```

---

## 2. Current state, as raw numbers

Read from `data/interim/exact_green_verification.parquet` at handoff.

| | |
|---|---:|
| Base runs verified | **275 / 1,732** |
| Instances covered | **878 / 4,245** |
| Python base runs | **167 / 167 — COMPLETE** |
| Java base runs | **108 / 200 sampled** (of 1,565 total) |

Java still needs **92 runs**, roughly **6 segments** at the measured 1.8
runs/min.

### The buckets so far (878 instances)

| `base_parse_status` | Instances | Demotes as |
|---|---:|---|
| `no_tests_confirmed` | **364** | CONFIRMED test-free |
| `no_tests_unverifiable` | **184** | UNVERIFIABLE |
| `green_verified` | **181** | stays `exact_green` |
| `unretrievable` | **79** | UNVERIFIABLE (measured) |
| `green_verified_partial` | **53** | stays `exact_green` |
| `inferred_expired` | **12** | INFERRED |
| `oversize_unread` | **4** | UNREAD |
| `base_failed` | **1** | reclassified `exact` |

**These four are never summed.** CONFIRMED, UNVERIFIABLE, INFERRED and UNREAD
demote alike under invariant 6 but are four different epistemic claims:

- `unretrievable` — every job log fetched, none readable. **Measured.**
- `inferred_expired` — one probed job log 410'd, the rest **inferred** expired.
  Rests on log retention being per-run, measured over 33 qualifying runs at
  three disjoint offsets: 32 all-410, 1 (410+404), **0 mixed**, including four
  27-job `apache/beam` runs. `classify_retention()` is unit-tested to prove the
  MIXED branch is reachable, so that zero is measured, not structural.
- `oversize_unread` — the log exceeded the 15 MB ceiling in
  `get_with_backoff()`. **Retrievable but unread: our limit, not GitHub's
  retention.**

---

## 3. Quarantine record

A background/`nohup` run was started against the rules and killed by the
operator after ~2.5 hours. It had written **375 base runs** into the checkpoint
with nobody watching. A dropped connection is indistinguishable from an expired
log in the current code — it is caught, the job is skipped, and the run is then
classified `unretrievable` or `no_tests_unverifiable`. During that window
`unretrievable` doubled, 76 → 148, which is exactly that shape.

**Those 375 runs' verdicts were discarded.** Discarded:

| Verdict discarded | n |
|---|---:|
| `no_tests_confirmed` | 338 |
| `inferred_expired` | 93 |
| `unretrievable` | 72 |
| `no_tests_unverifiable` | 31 |
| `green_verified` | 20 |
| `green_verified_partial` | 4 |

**Retained: 260 base runs / 851 instances, every one foreground-supervised.**
(Now 275 / 878 after segment 1 of the random sample.)

**Backup, not deleted:**
`data/interim/exact_green_verification_unattended_backup.parquet`. It is
evidence of what an unattended run produced, and it must never be merged back
in.

**The bytes were kept, the verdicts were not.** Job logs the unattended pass
downloaded are still in `RawStore` under `data/raw`, and they are real logs that
were successfully retrieved — a 200 response with a body is not in doubt. What
is in doubt is the *verdict*, which depends on jobs that may have been skipped
by a transient failure. So re-verifying those runs re-reads mostly from cache
(segment 1 saw `logs_cached: 31`), making the quarantine cheap: it costs
re-classification, not re-fetching.

---

## 4. Rulings in force

1. **INVARIANT-6 is the headline scenario.** EVIDENCE-ONLY is retained only as
   the upper bound. Leaving unswept instances at `exact_green` on conclusion
   alone is the assumption §21.3 forbids, not a scenario. Both bounds appear in
   the report; the headline is INVARIANT-6.
2. **The 11 CodeQL instances STAY.** They were provisionally flagged as
   "test-free workflows" by a name-based census. All 11 have
   `head_ran_tests == True`, and their identifiers are ordinary Java tests
   (`org.fife.ui.rsyntaxtextarea.HtmlUtilTest#testGetTextAsHtml_happyPath`).
   CodeQL's Java analysis builds the project and the Gradle/Maven build runs the
   suite. The name-based census was unsound — which is the round's own finding.
   See `docs/phase/018-mining-pitfalls.md` §1.
3. **The 5,684 `head_ran_tests` removals are a correctness guard, never a corpus
   correction.** All three splits are **unchanged at 778 instances / 4,194
   labels**: none of the 5,684 ever produced a label. The filter prevents a
   future defect; it did not fix a present one. Do not describe it as shrinking
   or cleaning the corpus.

---

## 5. What must NOT happen

- **No background execution.** No `nohup`, no `&`, no `setsid`, no detached
  task, no "run it overnight". `docs/AGENT_RULES.md` requires every command to
  run in the foreground and be read in the same step. This was violated once
  this round; the cost was 375 discarded runs.
- **No unattended runs.** One segment, ≤10 minutes, then stop and report. The
  operator's Wi-Fi drops overnight, and dropped requests get written into the
  checkpoint as if they were results.
- **No ordered selection for Java.** Checkpoint order is repo- and id-sorted and
  skews to `apache/beam`. Java is a **random sample, seed `20260901`**. Do not
  "just take the next N".
- **No commit without the identity check.** `git config user.name` must be
  `DeepanshuOP` and `git config user.email` must be
  `99538840+DeepanshuOP@users.noreply.github.com`. Mismatch = STOP and report.
- **No trailers, ever.** No `Co-Authored-By`, no `Generated-with`, no
  `Claude-Session`. This history carries none.
- **Never `git add -A` or `git add .`.** Explicit paths only.
- **Never edit a fixture to make a test pass.** If ground truth looks wrong,
  stop and justify from the spec.
- Do not touch `docs/SCHEMAS.md`, `tests/fixtures/holdout_v3/` or
  `holdout_v4/`, `release/`, or the daemon. No new dependency.

---

## 6. Open items after the sweep

1. **Parser defects, diagnosed but unfixed** — `docs/phase/012B-parser-defects.md`:
   - **3a**, pytest emits leaf iterations, violating **D-32** (the canonical
     `test_id` is the selectable unit; parameters live in `TestId.params`).
   - **3b**, Gradle prefixes `Gradle suite` and emits dot separators.
   - **3c**, Java suffix reconciliation drops the package, against **D-39** (the
     canonical Java `test_id` is FQCN + `::` + method; the parser recovers the
     package from the surefire header, the `Running <FQCN>` line, or an `at`
     frame, and **never guesses**, setting `fqcn_incomplete=True` instead).
2. **Holdout v5** — protocol written and not yet executed,
   `docs/phase/013B-holdout-v5-protocol.md`. holdout_v3 is CLOSED (scored once,
   invariant 9) and holdout_v4's scoring is VOID (D-38, circular ground truth).
   **There is currently no valid held-out parser measurement of the current
   parser.** v5 must be hand-labelled before any parser number reaches the paper.
   Fix the 012-B defects first, or v5 burns on known bugs.
3. **`release/v0.1` remains WITHDRAWN** — `release/v0.1/WITHDRAWN.md`. It also
   has **no regenerating script**: `package_release.py` was inspected during the
   Phase 017 root cleanup, found to print schema mismatches and write nothing,
   and deleted. Rebuilding the release needs a script that does not exist yet.
   Do not rebuild it without a ruling.
4. **After the Java sample lands:** report Java as an extrapolated **range** with
   Wilson 95% CIs and `n` stated, never a point estimate; compare
   `inferred_expired` against measured-410 rates and say plainly whether the
   inferred population skews to `apache/beam`; then give the final INVARIANT-6
   figures with the sweep completion percentage beside each, and say plainly
   whether BR-Bench is a few hundred instances or a few thousand.

---

## 7. Numbers this round supersedes

Never replace one silently; name what it supersedes.

| Figure | Superseded value | Source |
|---|---|---|
| `no_base` rate | 43.88% | Phase 014-A |
| `exact_green` count | 4,245 | Phase 016-A |
| strict instances | 778 | Phase 014-A |
| strict labels | 4,194 | Phase 014-A / D-44 |
| Gate 1 (labels, D-44) | 4,194 / 5,000 | D-44 |
| published corpus size | 524 | Phase 007-B |

Current INVARIANT-6 figures are a **floor** while the sweep is incomplete, and
must be labelled as such.
