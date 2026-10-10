# Phase 034: BlastRadius 2.1 progress (E3 cache-miss diagnosis and fixes)

Branch `upgrade-2.1` from `upgrade-2.0` @ 57658ce. Operator DeepanshuOP. No live LLM call in this step (`BR_OFFLINE=1` / replay
only). Nothing pushed or merged. Log is appended step by step.

## Step 0 (2026-10-10): read-in

- Read CLAUDE.md, AGENTS.md, D-55..D-60, 032, 033, `src/agents/{repair,llm,llm_cache}.py`, `analysis/rq4_repair.py`.
- Branch `upgrade-2.1` created from `upgrade-2.0` HEAD 57658ce; git identity verified (DeepanshuOP, noreply email).
- Reading note: in `GroqLLM.chat` the cache lookup already precedes the quota check, so replayed *requests* cannot consume
  quota. Misses must therefore be real key mismatches. `estimate_run` however ignores the cache (upper bound) and `run` prints
  the worst case before any task; to be addressed under Rule 2.

## Step A (2026-10-10): diagnosis of the cache misses (read-only, then replay; no live call)

Scripts lived in the session scratchpad (not committed). Everything below was run with `BR_OFFLINE=1` or `BR_LLM_REPLAY=1`
(a miss raises `CacheMiss`; `requests.post` is unreachable on a hit, and in replay a miss never reaches it either).

### A1. Request keys recomputed with the code at HEAD (57658ce), standard variant, subset of 70 in task-id order

| model | records | R1 hit / miss | R2 hit / miss | tasks with at least one miss | tasks whose R1 and R2 first calls both hit |
|---|---|---|---|---|---|
| openai/gpt-oss-120b | 114 | 47 / 23 | 47 / 23 | 23 | 47 |
| openai/gpt-oss-20b | 113 | 46 / 24 | 45 / 25 | 25 | 45 |

- 120b tasks with a miss: itsdangerous-NEGATE_COND-03, -04, itsdangerous-OFF_BY_ONE-01, markupsafe-NEGATE_COND-00, -03, -05 ... -09,
  -11 ... -17, shopcart-ARITH_SWAP-00, -01, shopcart-CMP_FLIP-00, shopcart-NEGATE_COND-00, -01, -02.
- 20b: the same plus itsdangerous-NEGATE_COND-01, -02. One of them, itsdangerous-NEGATE_COND-01, has R1 cached and R2 not: that is where
  the 20b run actually stopped (quota between its two first calls).
- **The 47 (120b) and 45 (20b) tasks the progress log called replayable all hit**, and in task-id order the sequential runner replays a
  prefix of 39 (120b) / 37 (20b) tasks and then hits the first never-run task; the remaining 8 fully cached tasks of each model are
  pilot tasks (n = 20 run) that sit later in task-id order, so they are replayed only after the uncached ones are run.
- Cached `system` prompt equals the current `SYSTEM` in 114 / 114 and 113 / 113 records.

### A2. Unified diff of cached vs current prompt for the first two missing tasks

**There is nothing to diff.** For itsdangerous-NEGATE_COND-03 and -04 (120b) and itsdangerous-NEGATE_COND-02 (20b) the cache holds no
request whose failing-test header and output match the task (0 records each); the 120b run never reached them. The first
missing task of each model is a task that was *never run*, not one whose prompt changed. (Records carry no task id; tasks were matched by
the exact `Failing tests:` + `Test output` head of the prompt.)

### A3. The operator's symptom is not reproduced

- Full replay of the 70 tasks through `RepairAgent` with the real suite validator (retries included), 120b: the 47 fully cached tasks completed with every
  call a cache hit, including the 8th task `click-BOOL_RETURN-01` (3 calls, 3 hits, R2 accepted so no retry) and every task that needed
  R3 retries: 188 calls, 109 distinct keys, every one a hit; the 109 are the 94 first calls plus 15 retries, and
  the other 5 of the 114 records are the pre-masking orphans described in A4 (the dry run's "20 recorded retries" counts them too). First miss in task-id order: task 40, `itsdangerous-NEGATE_COND-03`, a never-run task.
- The operator's own command, `BR_LLM_REPLAY=1 BR_E3_TASKS=70 make repair-run MODEL=openai/gpt-oss-120b` (so `uv run --env-file .env`,
  the real `.env`, never printed): printed `... 1,679 tokens left today by the client-side ledger`, replayed tasks 1-39, then raised
  `CacheMiss` at task 40 (itsdangerous-NEGATE_COND-03). Same for `MODEL=openai/gpt-oss-20b`: 37 tasks replayed, miss on the 38th
  (itsdangerous-NEGATE_COND-01, R2).
  With the network call removed this is exactly what the live command does until its first uncached request.
- `PYTHONHASHSEED` 1, 2, 3 against the default: all 140 standard first-call prompts byte-identical.

### A4. Checklist from the brief

| suspect | finding |
|---|---|
| prompt text changed by later fixes (shopcart classname, coverage config, retry-feedback masking) | No. `git diff 20a8176 HEAD -- src/agents/repair.py` is empty; `src/eval/seeded/` differs only by the new `hard.py`; `eval/seeded/tasks.jsonl` was committed once (1142457) and never changed. The classname/coverage fixes live in `analysis/rq4_repair.py` (`test_file_of`) and `hard.py`, which build tasks/detection, not standard prompts. The masking fix (20a8176) is the pre-registered code. |
| chunk selection changed | No: 140 / 140 standard prompts (R1 + R2, both models' tasks) byte-identical before and after this step's edits, and all hit. |
| absolute paths or timestamps in prompts | Not in first-call prompts (they come from checked-in `tasks.jsonl` plus the working tree under `head_state`). Retry feedback masks addresses and the repo path (20a8176). 5 of the 120b cache's 114 records (all retries) predate that fix (10:34-10:35 UTC) and carry raw `0x...` addresses (two different addresses for the same test: the original defect); they are orphans that nothing requests and cost nothing. |
| non-deterministic ordering | One real source found and fixed: `bm25_scores` sums over `set(query)`, whose order depends on `PYTHONHASHSEED`, so scores can differ in the last bits across processes. Chunk ranking rounds to 9 decimals so it did not bite in the 140 prompts tried, but the prompt must not depend on it. `source_files` (sorted rglob), `rank_tests` (sorted candidates), `sorted(changed_files)` are fine. |
| subset or task order changing | No: `subset()` is a seeded, sorted, operator round-robin; `BR_E3_TASKS=70` is all tasks, in task-id order. |
| quota check before cache lookup | No: in `GroqLLM.chat` the cache lookup returns before any quota arithmetic (a hit costs nothing and is not blocked by `BR_GROQ_TPD=0`). The one place that ignored the cache was `estimate_run`: it priced all 70 tasks as new (384,625 in + 420,000 out) and printed that as the run's cost. Fixed under Rule 2. |

### A5. The pre-registered code and the diff against it

033 fixes `src/agents/repair.py` at `20a8176f206b8f6d220af334fa809ff49d641c28`.

`git diff 20a8176 HEAD --stat -- src/agents/repair.py src/eval/seeded/ analysis/rq4_repair.py`:

```
 analysis/rq4_repair.py  | 463 +++++++++++++++++++---------------
 src/eval/seeded/hard.py | 279 +++++++++++++++++++++++++++++
 2 files changed, 604 insertions(+), 138 deletions(-)
```

`src/agents/repair.py`: no change. Hunks of `analysis/rq4_repair.py` that touch prompts or chunk selection: none. It adds the hard
variant, `estimate_run`, `subset` re-use, the cost table and report sections; `build_prompt` / `select_chunks` are called exactly as before.

### A6. What I could not establish

The overnight symptoms ("stopped on the 8th task", "0 of 70 on the very first task", and the hard-variant `IndexError`) do not occur from
a clean tree on this machine with this cache. I have no log of that run, so I cannot say what differed. What the repository does permit,
and what fits all three symptoms, is **two runs sharing one working tree**: `head_state` rewrites each seeded repo (`git checkout -- .`,
`git apply`), and nothing stopped a second process (the 20b run, the hard run, or a leftover run) from doing so between another process's
`index_functions` and `render_chunk`. That yields chunk line ranges from one tree rendered from another (the `IndexError`, and prompts that
never match a cached key). This is a hypothesis, not a finding; it is addressed by construction below (lock + rendering from the indexed text).

### Decision (rules from the brief)

- **Rule 1: not triggered.** No prompt text or chunk logic changed after the pre-registered commit, so nothing is restored, there is no
  amendment to 033 and the third commit is not made.
- **Rule 2: applied.** `estimate_run` now estimates only the uncached remainder; `chat` is cache-first (documented, tested with
  `BR_GROQ_TPD=0`); the quota stop message names the task it stopped at.
- **Rule 3: applied.** Hash-seed-independent BM25 summation in `repair.py` (the baseline, which feeds `make tables`, is untouched);
  fresh-process hash test; per-repo lock around `head_state`.
- **Rule 4:** tasks to re-run because of cache invalidation: **0** for both models (47 of 120b, 45 of 20b all replay). The uncached
  remainders are tasks that were never run. The interim numbers in RESULTS_2.md stay interim; nothing is superseded by this step.

## Step B (2026-10-10): hard-variant crash

- **Reproduction attempt.** `BR_LLM_REPLAY=1 BR_E3_TASKS=70 make repair-run MODEL=openai/gpt-oss-120b VARIANT=hard` from a clean tree:
  `estimate_run` and `build_prompt` completed for all 70 hard tasks (no `IndexError`), then the first request missed as expected (the
  hard variant has 19 / 18 cached first calls, see below, but task 1 is not one of them). The dry-run `estimate` mode also builds
  all 70 hard prompts in one process without error. So the crash is **not deterministic at HEAD**; see A6 for the explanation that fits.
- **Defect in the code regardless.** `render_chunk` re-read the file (`lines[i - 1]`) although the chunk's `start`, `end` and `focus` had been
  computed from an earlier read. Any change of the tree between the two reads (another process's `git checkout -- .` / `git apply`
  on the shared seeded repo, or a caller that built chunks from one tree and rendered another) made `lines[i - 1]` run past the end of
  the file. Fixed in two layers:
  1. `render_chunk` renders from `Chunk.text`, the text the chunk was indexed from. Output is byte-identical where the tree is
     consistent (the 140 standard prompts are unchanged). A focus line outside the function is clamped, logged with `log.error("BUG: ...")`
     and recorded in `repair.CLAMPED`; it is never silent.
  2. `head_state` holds an exclusive `flock` on `<repo>/.git/br-seeded.lock` for the whole block, so two runs on one seeded repo take turns.
- **Tests** (`tests/test_e3_replay.py`): a hand-written module where a distractor inserts a comment line above the target function
  (and the mutant moves one line down) asserts the rendered chunk contains `def target(x):` at its real line number; rendering after the
  file changed on disk does not raise; a stale focus is clamped and logged; a second process blocks on the lock until the first lets go.
- **Hard-variant retrieval, no LLM, all 70 (`BR_OFFLINE=1 make repair-eval`, which runs it):**

  | | before (rq4_repair.md at 67f9614) | after (this step) |
  |---|---|---|
  | R1 seeded function among the 3 chunks | 46/70 | 46/70 |
  | R2 seeded function among the 3 chunks | 63/70 | 63/70 |
  | R2 hit where R1 misses / reverse | 17 / 0 | 17 / 0 |
  | chunks in a distractor, R1 / R2 | 75/210, 146/210 | 75/210, 146/210 |

  Standard variant also unchanged (46/70 vs 69/70). The regenerated `paper/generated/rq4_repair.md` differed from the committed one only in
  the "Generated by ... at git" stamp, so it was restored and is not part of the commits (nothing in it changed).
- **Dry-run estimates, hard variant** (`make repair-estimate`, no key, no request; worst case = R2 priced with two retries, uncached only):

  | model | first calls cached / to send | tasks needing a live call | worst-case tokens | days at 200K/day |
  |---|---|---|---|---|
  | openai/gpt-oss-120b | 19 / 121 | 70 | 425,132 in + 391,500 out = **816,632** | 5 |
  | openai/gpt-oss-20b | 18 / 122 | 70 | 426,650 in + 393,000 out = **819,650** | 5 |

  (The cached hard first calls are requests byte-identical to standard-variant ones: same chunks, same text.) Measured on the cache,
  a completed task costs about 4,200 tokens (120b: 197,690 tokens over 47 tasks) and 4,000 (20b), so the expected figure is about
  300K tokens, i.e. 2 days; 5 days is the bound.

## Step C (2026-10-10): third model, D-62

- `qwen/qwen3.8-27b` (Groq preview model) is the exploratory third model; recorded as **D-62** in `docs/DECISIONS.md` (D-61 is
  unassigned; noted there). `.env.example`, README and the Makefile comments name it. `analysis/rq4_repair.py`: `THIRD_MODEL`,
  and `is_groq` now means "an `org/model` id" so a non-gpt-oss Groq model is not sent to Bedrock.
- **Reasoning parameters.** `reasoning_effort` and `include_reasoning` are sent only to the `openai/gpt-oss` family (the models they were
  recorded for; the cache keys depend on them). Other models receive neither. If Groq answers a request with a 400 whose message
  names one of those two parameters, the provider drops exactly that parameter and retries; the request that is cached and keyed is the
  one that was accepted, and a later process finds it without asking again (tested). `temperature`, `seed` and the completion budget are
  never dropped.
- **What was not checked.** The brief asks to check the parameter handling against Groq's error message rather than guess. No live call is
  allowed in this step and `AGENTS.md` forbids fetching external pages, so I have not seen Groq's actual message for qwen3.8-27b. The
  provider therefore reads the parameter name out of the 400 at run time instead of assuming it. The first live request of that model
  is its parameter probe; if the model needs a parameter this code does not know (for example a reasoning-format setting so that its
  thinking is not returned inside `content` and does not eat the 1,500 completion tokens), that appears as truncated or malformed replies
  and is a decision for the operator before the full run. `make repair-estimate MODEL=qwen/qwen3.8-27b` gives its worst case:
  804,625 tokens standard, 877,484 hard (nothing cached), 5 days each at 200K/day, about 3 days measured by the other models' mean.

## Step D (2026-10-10): verification

- `make test` (no global `BR_OFFLINE`): **912 passed, 2 skipped in 859.87 s**. 032 recorded 895 passed, 2 skipped before its later
  additions; 11 of the difference are this step's tests (`tests/test_e3_replay.py`), the other 6 predate this step.
- `BR_OFFLINE=1 make repair-eval` (the target exports `BR_OFFLINE=1` and `BR_LLM_REPLAY=1`): exit 0 in 28 min (it validates every
  replayed patch with the real suites). Zero network calls: replay mode raises on any miss before the HTTP layer; both cache files
  and `usage.jsonl` have identical md5 before and after; `logs/requests.jsonl` mtime unchanged.
- Primary-test block of `rq4_repair.md` (unchanged by the step):

  > Standard variant, openai/gpt-oss-120b, n = 47: R2 plausible-fix rate 33/47 vs R1 20/47; R2 only 17, R1 only 4; exact McNemar
  > one-sided p = 0.003599 (alpha = 0.05): **R2 > R1 supported**. (47 of 70 tasks done; 23 not run (cache incomplete))

## Resume

Both models resume from their cache; nothing already recorded is re-requested. See the final message of the session for commands and
days. The client-side ledger frees tokens on a rolling 24 h window (about 100K tokens free from 2026-10-11 ~15:00 UTC for 120b and ~15:20
for 20b; the earlier note "after 10:00 UTC" was too early by that ledger; Groq's own reset rule was not observed).

## Correction (2026-10-10, frozen-runner setup)

Earlier text and the end-of-step message said the 120b run replays 47 tasks in task-id order and first misses at task 48. That was
wrong. The 47 (120b) / 45 (20b) tasks are *fully cached*, but not a prefix: the sequential runner replays 39 (120b) / 37 (20b) tasks and
stops at the first never-run task (40th / 38th), because 8 pilot tasks per model sit later in task-id order. The 47 / 45 counts, the key
analysis (A1) and the conclusion (no cached request is invalidated) stand. Reproduced in the frozen worktree `~/br-e3` at 8b1e922:
120b 39 tasks then `CacheMiss`; 20b 37 tasks then `CacheMiss`; caches and ledger byte-identical to the main repo's.

## Qwen run exit=2 at 7/70 (2026-10-10 20:00 and 21:15 UTC, `~/br-e3/e3_run.log`)

- **Cause:** a dropped network, not the model. After 7 tasks (22 recorded replies, 7 tasks of live calls succeeded) the next live request failed
  with `socket.gaierror: Temporary failure in name resolution` -> `requests.exceptions.ConnectionError` for `api.groq.com`.
  `GroqLLM.chat` caught only HTTP statuses, so the exception escaped `run_task` and `main` and the process died (`make` exit 2). The 21:15 run
  replayed the same 7 cached tasks and failed at the same first live request (DNS still down). No reply was lost: records are written only
  after a response.
- **Fix:** network errors (`ConnectionError`, `Timeout`) are retried with backoff 5, 10, 20, 40, 80, 120 s inside the existing retry budget;
  if the provider stays unreachable `NetworkUnavailable` is raised, nothing is recorded, and `analysis/rq4_repair.py run` stops cleanly
  ("re-run the same command to resume", exit 0) like a quota stop. Same for the Bedrock provider. No prompt, key or cache change.
  Tests: backoff then success; persistent failure records nothing and writes no ledger line.
- **Not a bug, but note:** 9 of the 22 qwen replies contain no SEARCH/REPLACE block (the model writes prose such as "I need to look at ...", one
  reply used all 1,500 completion tokens). With no reasoning parameter sent, qwen's visible reasoning counts against the completion budget.
  That is a property of the exploratory model under D-62, to be reported, not changed mid-run.
