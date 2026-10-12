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

## Step 0b (2026-10-10): qwen `reasoning_effort="none"`

- `src/agents/llm.py`: `GROQ_REASONING_PARAMS` gains `"qwen/qwen3.8-27b": {"reasoning_effort": "none"}` (no `include_reasoning`). The
  gpt-oss entry is untouched. The 400-drop logic still applies to it.
- `tests/test_e3_replay.py`: the qwen assertion (was `{}`) now expects `{"reasoning_effort": "none"}`: that is the requested behaviour change,
  not a fixture edit. New `test_gpt_oss_request_params_and_cache_keys_are_unchanged` re-derives every recorded key of both gpt-oss caches
  from current code (real checked-in cache) and pins the params.
- Archive: the qwen cache exists only in the frozen worktree `~/br-e3` (not in this tree). I **copied** it (read-only; the original is
  untouched, md5 identical) to `eval/llm_cache/archive/e3_qwen_qwen3.8-27b.no-reasoning-param.jsonl` (52 records at 22:42 UTC) with a
  README label "no-reasoning-param run, superseded". The qwen cache in the main tree therefore starts empty. **The copy in `~/br-e3`
  must be moved by the operator** before qwen is re-run there; I did not touch it.
- D-62 dated note added in `docs/DECISIONS.md`.

## Step 2.1-0 (2026-10-10): decisions and dependency

- D-61 (RAG layer) and D-63 (PR bot) appended to `docs/DECISIONS.md`.
- `fastembed` latest stable at lock time: **0.9.0** (`uv add --optional rag fastembed`, then pinned `==0.9.0`; `uv lock`; `uv sync --extra graph
  --extra ml --extra figures --extra rag`). `uv.lock` gained 21 packages (onnxruntime 1.31.0, tokenizers 0.23.3, huggingface-hub 1.33.0,
  numpy etc. already present); nothing removed.
- `jinaai/jina-embeddings-v2-base-code` is in `TextEmbedding.list_supported_models()` (768-d, 0.64 GB, apache-2.0): used, no substitution.
  Downloaded once (3 min) from Hugging Face; snapshot `516f4baf13dec4ddddda8631e019b5737c8bc250` copied to `data/rag/models/` (ignored).
- Deviation to note: AGENTS.md says "no external sources / do not fetch any URL" and forbids writes under `data/`. The model download is a
  pinned dependency fetch (D-61 approves it), and `data/rag/` is a new git-ignored directory the brief names; neither touches `data/raw`,
  `data/interim` or logs.

## Step 1 (2026-10-10): RAG index, `src/rag/`

- Files: `src/rag/{__init__,chunks,index,history}.py`, `tests/test_rag.py` (14 tests, offline; real git repo with 3 commits in `tmp_path`).
- `chunks.py`: Python via `ast` (same granularity as `repair.index_functions`, asserted equal on the sample repo), Java via tree-sitter-java
  (the parser Graphify uses; `Parser` called directly, no Graphify graph), commit subjects by `git log -L` (cap 3) with `--follow -n 3` fallback.
- `index.py`: sparse = `repair.bm25_scores` over `repair._doc_tokens` (reused, not reimplemented); dense = fastembed cosine, vectors
  content-addressed in `data/rag/emb_<model>.sqlite`; hybrid = RRF k = 60. The sparse ranking lists only chunks with BM25 > 0. `build(repo, sha)`
  caches chunk digest + vectors under `data/rag/<repo>@<sha12>.<model>.{json,npz}`; `search(query, k, mode, restrict_to, tokens)`.
  Chunk text is cut at 2,000 characters before embedding (CPU cost).
- `history.py`: `fix_history(repo, rev, file, qualname)` -> up to 2 `(sha, subject, hunk <= 40 lines)` from `git log -L` at the function's
  range as of `rev`.
- Finding: `git log -L` attributes lines by diff alignment, so a function appended in a commit that also edits a neighbouring line can be
  credited with that neighbour's history (reproduced while writing the fixture). The fixture avoids it; the limitation is inherent to `-L`.
- **Finding for Step 3:** the three seeded pallets repos (click, itsdangerous, markupsafe) are depth-1 clones (`.git/shallow`, 1 commit);
  `data/clones` does not hold them. `fix_history` on them returns nothing, so R4's history block would be empty for all 70 tasks until the
  clones are deepened (a `git fetch --deepen`, network, which I have not done). Raised to the operator in the Step 3 report.
- `make test`: **931 passed, 2 skipped** (917 + 14 new) in 769 s.

## Step 2 (2026-10-11): localization retrieval study (`analysis/rq5_retrieval.py`, `make rag-eval`)

- No LLM. L1 and L4 are `repair.select_chunks` itself (cut at three lifted to read the rank), so they are R1 / R2 and not copies:
  L1 = 46/70 and L4 = 69/70 (standard), 63/70 (hard) match `rq4_repair.md` (R1 46/70, R2 69/70 and 63/70).
- Dense vectors: `jinaai/jina-embeddings-v2-base-code`, pinned snapshot, CPU, one thread, text cut at 2,000 characters; 868 unique
  vectors for the 70 tasks x 2 variants (content-addressed in `data/rag/emb_*.sqlite`, git-ignored). First run ~35 min on one thread
  (CPU embedding; batches sorted by length).
- Result (source `paper/generated/rq5_retrieval.md`): hit@3 standard / hard: L1 46 / 46, L2 21 / 21, L3 32 / 32, L4 69 / 63, L5 69 / 58
  of 70. L3 vs L1: 3 only L3, 17 only L1, p = 0.0026, Holm (family of 4) 0.010. L5 vs L4 hard: 3 vs 8, Holm 0.453.
  **Smarter retrieval alone does not close the gap: it is worse than BM25 here.**
- Deviation: the brief's Holm "across those tests" is taken as one family of 4 (two comparisons x two variants); stated in the file.
- `tests/test_rq5.py` (3 tests): scoring, gap reading both ways, Holm arithmetic by hand.

## Step 3 (2026-10-11): arm R4 (code; no live run)

- `src/agents/repair.py`: `ARMS` is unchanged (`R0..R3`); `RAG_ARMS = ("R4",)`, `ALL_ARMS`. R4 = R2's sections + fix history of the top chunk + up
  to two similar functions (dense search on the top chunk's code, target chunks excluded); cap 3,500 tokens (system + user, characters /
  3.5), trimming history first, then similar chunks, never the target. One attempt (like R2). `build_prompt` is untouched.
- `src/rag/context.py` (`RagContext`): L5 selection, history via `history.fix_history(repo, "HEAD", ...)`, similar via dense search.
- `analysis/rq4_repair.py`: `--arms` (env `ARMS`, default `R1,R2,R3`), `estimate_run(..., arms, rag)`; `eval` replays R4 only if the cache
  holds R4-marked prompts and reports it in a new "Exploratory (not pre-registered)" section (R4 next to R2, paired two-sided McNemar,
  n stated). The third model (D-62) is excluded from the confirmatory family and tests and gets its own exploratory table.
- Proof R0-R3 did not move: `tests/test_rag_r4.py` pins sha256 of SYSTEM and of the R1 / R2 / R3 prompts (with and without retry
  feedback) recorded from commit 5807f36 on the shopcart sample (before R4 existed), and asserts `ARMS`. Full replay: see the
  `make repair-eval` entry below.
- **Limitation to decide on:** the seeded pallets repos are depth-1 clones, so `fix_history` returns nothing for them (a shallow boundary
  commit is ignored on purpose). R4's history block is empty for all 70 tasks unless the clones are deepened with a network
  `git fetch --deepen` (not done: needs your decision). The similar-code block works without history. See the final report.
- Command for the operator (not run here): `make repair-run MODEL=openai/gpt-oss-120b ARMS=R4 BR_E3_TASKS=70` (and `VARIANT=hard`).
  `make repair-estimate ... ARMS=R4` prints the uncached worst case first.

## Step 3 verification (2026-10-11): R0-R3 did not move

- `BR_OFFLINE=1 BR_LLM_REPLAY=1 make repair-eval` (replay, network forbidden, a miss raises `CacheMiss`): exit 0 (under 20 min). Every
  pre-existing line of `paper/generated/rq4_repair.md` is byte-identical to the committed one except the "Generated by ... at git" stamp:
  same primary line (n = 47 of 70, R2 33/47 vs R1 20/47, p = 0.003599), same notes ("47 of 70 tasks done; 23 not run (cache incomplete)"),
  no task lost. A prompt that had moved would have shown up as a newly "not run" task. The only new content is the empty
  "Exploratory (not pre-registered)" section.
- Prompt hashes of R0-R3 are pinned in `tests/test_rag_r4.py` (recorded at 5807f36).

## Step 4 (2026-10-11): Ask BlastRadius

- Files: `src/rag/knowledge.py`, `src/agents/ask.py`, `python -m src.agents ask`, `analysis/ask_eval.py`, `eval/ask/questions.jsonl`
  (15 questions: 5 test-failure from seeded tasks, 5 impact on seeded source files, 5 history on real BR-Bench test ids), `tests/test_ask.py` (17).
- Sources: code chunks (tests included), BR-Bench failure documents from `data/interim` (one per (test_id, run_id) with a message:
  message, date, repo, label class: 2,926 documents, 2,111 with a known label class), README + `docs/*.md` sections. k = 8, at most 4 per source; impact questions add the
  E1 top-5 block (SHAP reasons) as one of the 8. History questions search the failure source only (so docs cannot crowd it out).
- Retrieval evaluation (`make rag-eval`, second table of `rq5_retrieval.md`): 709 test-split failures with a message; documents strictly
  earlier in the same repository (asserted per query). Same test_id (n eligible = 90): hit@1 BM25 55/90 (61.11%), dense 55/90, hybrid
  53/90 (58.89%), chance 16.74%; hit@5 76.67% / 71.11% / 75.56%, chance 29.14%. Same failure class (n = 708): hybrid hit@1 94.92% vs
  chance 52.01%. Time safety is a test (`test_retrieval_is_time_safe_strictly_before_the_query`): a document at the query's time is excluded.
- Website: Ask tab (`demo-web/components/Ask.tsx`, localhost-only `app/api/ask/route.ts` that accepts only seeded repo names and needs
  `GROQ_API_KEY`; otherwise recorded answers). `npm run build` passes; Next.js not upgraded, no `npm audit fix`.
- Cost note: first embedding of the click test chunks (750 functions) took about 50 min of one CPU thread; vectors are cached.

## Step 5 (2026-10-11): PR bot

- Files: `src/agents/bot.py`, `forge.py` (comment create / list / edit, inline suggestion review), `cli.py` (`bot`), `Makefile`
  (`bot-local`), `integrations/github-actions/{blastradius-bot.yml,BOT_SETUP.md}`, `analysis/bot_demo.py`, `tests/test_bot.py` (8),
  `tests/test_bot_workflow.py` (1).
- Deviation: a pull request has changed files, not a user story, so the story-keyed `ImpactAnalysisAgent` is replaced by the same E1 ranker
  (`rank_tests`) over the diff's files, wrapped in an `ImpactAnalysis` so `RegressionSuiteAgent` runs it unchanged.
- Deviation: GitHub renders "Apply suggestion" only on inline review comments, so the bot posts (1) the single issue comment it edits in
  place and (2) one review of inline `suggestion` comments for validated hunks that lie inside the PR diff (skipped if already posted).
- Found while building the recording scenario: `run_pytest` ran a worktree's tests against whichever checkout an editable install pointed
  at (a `src/` layout), which would have validated patches against unpatched code. Fixed (worktree and its `src/` are first on
  PYTHONPATH) with a test (`test_pytest_runs_import_the_worktree_src_not_an_editable_install`).
- Bot recording scenario: `itsdangerous-ARITH_SWAP-00` (the first itsdangerous task by id, not chosen by outcome). The seeded operator
  breaks the signer, so 260 of 297 tests fail; the bot's comment caps its tables and says so.

## Step 6 (2026-10-11): third model

- `qwen/qwen3.8-27b` is in `analysis/rq4_repair.py` as `THIRD_MODEL` (D-62) and is excluded from the confirmatory family; `make repair-eval`
  renders an exploratory table (arms R1-R3, paired R2 vs R1, "n of 70 tasks" stated) when `eval/llm_cache/e3_qwen_qwen3.8-27b.jsonl` exists
  (`tests/test_rag_r4.py::test_exploratory_section_*`). Not run in this session. Sent with `reasoning_effort="none"` (Step 0b).

## Recording runs (2026-10-11, operator confirmed E3 runs complete; openai/gpt-oss-20b, the only live calls of this session)

- **Why they waited:** the client-side ledger showed 197,925 of 200,000 tokens used in the rolling 24 h, so the first attempt stopped
  with `DailyQuotaReached` before sending anything (no tokens spent); the runs went ahead when the ledger had headroom (11:37 and 11:46 UTC).
- **PR bot** (`python -m analysis.bot_demo record`): task `itsdangerous-ARITH_SWAP-00`; 1 model call, 1,495 tokens, patch applied on the
  first attempt and **validated by the full suite**; one suggestion (`src/itsdangerous/signer.py` line 204). Comment 12,529 characters
  (cap 65,000), saved to `src/agents/demo/bot_comment.md`; cache `eval/llm_cache/bot_openai_gpt-oss-20b.jsonl` (1 record). Replay
  (`python -m analysis.bot_demo replay`, `tests/test_bot_demo.py`) reproduces the committed comment byte for byte (the head sha is
  stable because the commit dates are fixed).
- **Ask** (`python -m analysis.ask_eval record`): 15 questions, 15 calls, 17,969 tokens (largest 2,201), cache
  `eval/llm_cache/ask_openai_gpt-oss-20b.jsonl`; `report` replays it with the network forbidden and `answers.json` is identical
  except `from_cache`. Faithfulness (`rq5_retrieval.md`): no `[Sk]` outside the retrieved items in 15/15, at least one citation in
  14/15 (test-failure 4/5, impact 5/5, history 5/5), 1 answered "not in the context". Correctness was not scored.
- Tokens this session on Groq: 19,464 (gpt-oss-20b only), the sum of the two runs above; gpt-oss-120b 0; qwen 0; no other provider.

## Fix found by the R4 dry run (2026-10-11)

`make repair-estimate ... ARMS=R4` logged `BUG: chunk ... focus line ... outside its function` for click's `edit` and itsdangerous'
overloads: the L5 selector keyed focus lines and the touched set by `(file, qualname)`, which typing overloads and re-definitions share.
Keys are now `(file, qualname, start)` (`CodeChunk.ukey`; `Index.search(restrict_to=...)` accepts either form; test
`test_restrict_to_with_a_start_line_does_not_match_a_same_named_sibling`). The same key fix applies to the L5 mode of the localization
study, so L5 moved from 68 / 57 to **69 / 58** (standard / hard) and the hard-variant L5 vs L4 test from p = 0.146 to 0.2266
(Holm 0.4531). L1 to L4, L2 and L3 and the failure-history tables did not change. Docs were patched to the regenerated file.

## Slide figures and the PR-bot sandbox (2026-10-11)

- **Pushed** `upgrade-2.0` and `upgrade-2.1` to origin after checking all 39 commits not on origin/main: author and committer
  DeepanshuOP (noreply), no trailer lines (`git log --format=%(trailers)` empty, no `Co-Authored-By` / `Claude-Session`).
- **PR bot, first live run** on a fork of `pallets/itsdangerous` (`DeepanshuOP/itsdangerous`, workflow pinned to a pushed sha).
  Run 1 failed in 16 s: `ModuleNotFoundError: networkx`. `networkx` arrives with the `graph` extra (`graphifyy`), which the template did
  not install. Fix: `uv sync` and `uv run` take `--extra graph --extra ml --extra rag` in `blastradius-bot.yml` and in `make bot-local`.
  Run 2 succeeded (job 26 s). The sandbox's own dependency step also needed `freezegun` (its tests import it).
- **Bot output on the demo bug** (`age > max_age` flipped to `<` in `TimestampSigner.unsign`, 5 of 297 tests fail): E1 listed six test
  files, E2 called all five failures "mine", and the model reply "could not be applied", so the patch is shown as **not validated**
  (no suggestion). One model call, 2,194 tokens.
- **fig6 / fig7** (`analysis/slide_figures.py`, `make figures`). fig6 replays the E3 caches through `rq4_repair.replay_runs` (the code
  `repair-eval` uses; extracted from `eval`, same behaviour) with 95% Wilson intervals; fig7 parses `rq5_retrieval.md`. Replay at
  this commit reproduces `rq4_repair.md` (120b R1/R2/R3 20/33/37 of 47, 20b 10/29/33 of 45).
- **Seeded-tree contention.** A live E3 run in another checkout shares `data/seeded` through a symlink, so a replay queues on the
  per-repo `br-seeded.lock`. `BR_SEEDED_DIR` (default unchanged) points a replay at a copy of `data/seeded` whose venv `.pth` paths are
  rewritten; the figures were produced that way so the live run was not touched.

## PR bot: "the model's reply could not be applied" (2026-10-11)

- **Cause (reproduced locally with `make bot-local`, gpt-oss-20b, same 2,194 tokens).** Two attempts, both well-formed SEARCH/REPLACE
  blocks aimed at the right line (`if age < max_age:` -> `>` in `TimestampSigner.unsign`), both found 0 times by the strict applier:
  attempt 1 shifted the block four columns right; attempt 2 copied the separator space of the `NNN| ` gutter, so every line had one extra
  leading space. Replies are checked in at `tests/fixtures/bot_tolerant/`.
- **Why the artifact did not show it:** `upload-artifact@v4` skips dot-directories; the cache never reached the artifact. Now
  `include-hidden-files: true`.
- **Fix (bot only).** `bot.apply_blocks_tolerant`: exact match first; otherwise gutter stripped and lines compared with surrounding
  whitespace ignored, must still match exactly once, replacement re-indented by the same offset; failure feedback tells the model to
  drop the gutter and keep the file's indentation. `RepairAgent(applier=...)` (default `apply_blocks`, so E3 R0-R3 and the pinned prompt
  hashes are untouched). Bot retries: 2 (3 attempts, R3 feedback). Workflow template model: `openai/gpt-oss-120b`.
- Offline replay of the recorded 20b reply with the fix: patch applied on attempt 1, **validated by the full suite**, one suggestion
  (`src/itsdangerous/timed.py` line 141).

## Final sprint (2026-10-11): Compare, Use it, demo-check, then a HARD STOP at `make tables`

- **Step 1.** `BOT_SETUP.md` names `openai/gpt-oss-120b`. Usage ledger committed. The strict-versus-tolerant applier sentence is in
  `docs/RESULTS_2.md` and the E3 card (strict `apply_blocks`, tolerant `apply_blocks_tolerant`, both tested). `make e3-sync`
  (`scripts/e3_sync.sh`): copies `~/br-e3/eval/llm_cache/*.jsonl` (read-only on the runner), then runs `repair-eval`, `figures`,
  `demo-data` and `cost_report` against a scratch copy of `data/seeded` (so the live run's repo locks are never taken), prints the
  primary-test block and n per model/variant, commits nothing.
- **Step 2, Compare tab** (`demo-web/components/Compare.tsx`, data `compare.json` from `analysis/export_demo_data.py`). Capability matrix
  from `docs/compare_matrix.yaml` (JSON subset of YAML, no new dependency) with a source per cell; every yes/no for another work
  quotes `docs/LITERATURE.md` verbatim (enforced by `tests/test_compare_matrix.py`), most other cells are "not reported". Safety
  checklist backed by named tests; four were missing and written (`tests/test_safety_claims.py`, a reasons test in `tests/test_bot.py`,
  `tests/test_cost_report.py`). `analysis/cost_report.py` (not in `make tables`) reads `paper/generated/e3_usage.json`, which
  `repair-eval` now also writes (per model/variant/arm token sums; no number in `rq4_repair.md` changes).
- **Step 3, Use it tab.** Setup steps from `BOT_SETUP.md`, workflow YAML pinned to the exporting commit, Jenkinsfile, CLI. The bot comment
  shown is the latest comment on PR #1 (`src/agents/demo/pr1_comment.md`, read with `gh api`); `bot_comment.md` is left as it was because
  `tests/test_bot_demo.py` replays the seeded recording byte for byte.
- **Step 4, `make demo-check`** (`analysis/demo_check.py`): 9 of 9 PASS (131-test subset, 12 named safety tests with none skipped,
  demo-data, site build, 4 agent scenarios, Ask replay of 15, bot replay byte-identical, JSON load check, 99 Compare numbers matched to sources).
- **Step 5.** Full `make test`: 993 passed, 2 skipped.
- **HARD STOP.** `make tables` completed (exit 0) but one pre-existing number moved: `paper/generated/rq2_predictor.md`, main table row
  "B5 BM25 path tokens", columns Recall@20% 0.457 -> 0.456, first-fail pos. 349.480 -> 349.527 (everything else differs only in the
  `Generated by ... at git` stamp, and `models/*.json` only in `git_sha`). Cause found: `bm25_scores` in `src/eval/baselines.py` iterates
  `set(query)` (string hashing), so float summation order, hence tie-breaking, depends on `PYTHONHASHSEED`. Re-running
  `analysis.rq2_predictor` with `PYTHONHASHSEED=0` gives 349.345 (APFD 0.624, suite frac 0.395) and `=1` gives 349.527; the committed
  value 349.480 matches a third, unrecorded seed. Only B5's Recall@20%, first-fail position, APFD and suite fraction move; Recall@10, MAP,
  every Holm p and the Gate 3 verdict were identical in all three. The generated files were restored to HEAD; nothing was merged to
  `main`. The fix is `for t in sorted(set(query))`, but it changes a published B5 value, so it is the operator's decision.

## Finish sprint (2026-10-11 to 2026-10-12)

- **B5 (D-64).** `sorted(set(query))` in `bm25_scores`. `make tables` at the new code reproduces the committed B5 row exactly (Recall@20%
  0.457, first-fail position 349.480); the drift of the earlier HARD STOP was the unpinned hash seed. `tests/test_determinism_hashseed.py`
  (BM25 under four seeds; `analysis.rq2_predictor` under `PYTHONHASHSEED=0` and `=1`, about 30 minutes) passes. No generated value changed.
- **E3 sync.** Standard variant complete at n = 70 for gpt-oss-120b and gpt-oss-20b: primary test R2 50/70 vs R1 33/70, one-sided exact
  McNemar p = 0.0007569 (confirmatory, docs/phase/033). Hard variant 29 and 17 of 70, qwen 25 of 70: interim. R4 built, not run.
- **Site.** Six-section research-page layout (Overview, Data, Results, Compare, Try it, Use it); commercial-tools matrix with vendor URLs;
  `make demo-check` 10 of 10; full `make test` 998 passed, 2 skipped; `make tables` stamp-only diffs.
