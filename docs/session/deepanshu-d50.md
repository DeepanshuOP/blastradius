# Session report: open round, D-50 blocked

Date: 2026-10-07. HEAD 616a4e8. Identity DeepanshuOP <99538840+DeepanshuOP@users.noreply.github.com>. Nothing committed.

## Step 1: dashboard extra (PATH A applied)
- `streamlit==1.61.1` caps `pyarrow<25`; the project locks pyarrow 25.0.1, so the ruling's path A was taken. pyarrow never moved.
- `dashboard = ["streamlit>=1.61.1"]` resolved streamlit **1.65.0**; re-pinned to `dashboard = ["streamlit==1.65.0"]`, re-locked.
- Lockfile proof: HEAD's 50 locked name==version pairs vs the new uv.lock: `changed/removed: []`; 50 -> 75 packages, 25 added (streamlit's tree). Run twice (after >= and after ==).
- `uv sync --extra graph --extra dashboard` needed a retry (first attempt: network timeout fetching altair; second with UV_HTTP_TIMEOUT=600 succeeded).
- `import streamlit, pyarrow` prints `1.65.0 25.0.1`. `import dashboard` prints "dashboard import ok" (only a bare-mode caching warning). Not launched.
- Note: the approved 1.61.1 is not the pin. 1.65.0 is, and it needs the operator's sign-off since it differs from the approved version.
- ENVIRONMENT.md: no change (path D not used).

## Step 2: PAT isolation
- `make` has no .env include and no loader. PATs reach it only from the shell environment (or `uv run --env-file .env` in run_supervised.sh / verify_exact_green.py, neither used).
- `env | grep -c ^GITHUB_PAT` = 0 in the session shell. Every run used `env -u GITHUB_PAT_1 -u GITHUB_PAT_2 -u GITHUB_PAT_3`.
- make tables output: `[tables] SKIP analysis/fetch_base_logs.py — no GITHUB_PAT_1/_2/_3 in env;` / `corpus is pinned, base side is local RawStore only (D-49).` No GitHub API call made. .env never read or printed.

## Step 3: rebuild (D-49 chain)
Commands: corpus_parse.py --as-of 2026-08-29T14:13:00Z --overwrite (pin written to scratchpad so tracked CORPUS_PIN.json was untouched; 27m19s) -> parse_base_logs.py -> src/label/fault_revealing.py -> make tables (exit 0). Pre-run data/interim backed up in the session scratchpad.

| | PREDICT | ACTUAL |
|---|---|---|
| positives (labels, strict) | 4,168 | 4,168 |
| strict instances | 762 | 762 |

Raw: `Split strict: 762 instances, 4168 labels, 2466 distinct tests`; `Gate 1 Positives: 762 / 5000 (Met? No)`; all=897/4384, relaxed=770/4214; same-SHA flips 62 (0.54%); base parse: 452 logs, 2990 outcome rows, 172 distinct test_ids. Reproduces across machines.

## Step 4: release key
- build_release.py with BR_PSEUDONYM_KEY absent: prints an error to stderr, exit 1, before build() runs. build() itself now requires a key and raises ValueError before touching out_dir (so an existing bundle is not rmtree'd either). NOT_PUBLISHABLE text, write and BLOCKED branch removed. Bundle not rebuilt.
- Tests (tests/test_release_pseudonym.py): build without key raises and creates/removes nothing; CLI without key exits non-zero, no out dir, no NOT_PUBLISHABLE.md; CLI with key exits 0, ships CHECKSUMS, no NOT_PUBLISHABLE, key not echoed. The old "no-key leaves raw logins" test was replaced.

## Step 5: scorer split
- `re.split(r"[,\s]+")` -> `raw_ids.split(",")` with strip. Fixture tests/fixtures/holdout_v5_scorer/filled_spaces.md has identifiers with spaces; new test passes.
- The v5 worksheet was never opened or scored. Deviation to note: four existing tests read/run against docs/phase/029-holdout-v5-worksheet.md (test_generated_worksheet_has_every_answer_field_empty, test_generated_worksheet_covers_every_fixture, test_parse_worksheet_reports_every_empty_cell, test_scorer_refuses_the_blank_shipped_worksheet_and_writes_no_seal). I deselected them in step 9 to honour the never-touch rule. They likely assert a blank worksheet, which the closed v5 sheet no longer is. Needs a ruling on retiring or repointing them.

## Step 6
docs/GRAPH_LAYER.md §6.1 table: "MET, by 0.25 ms" -> "MET, at the limit".

## Steps 7-8
D-50 BLOCKED: clone-heads TSV not pushed (docs/clone_heads_2026-10-05.tsv absent). Skipped; no CLONE_PINS.json, no D-50 entry, no PREDICT/ACTUAL for 5,985/5,623/3,801.

## Step 9: pytest
Full run (4 worksheet tests deselected): `1 failed, 653 passed, 1 skipped, 4 deselected in 405.26s`. The one failure was my new test (fixture lacked a Confidence field); fixed, and tests/test_score_holdout_v5.py + tests/test_release_pseudonym.py re-run: `18 passed, 4 deselected`. Expected full-suite state: 654 passed, 1 skipped, 4 deselected (the full suite was not re-run after the fixture fix).

## Proposed commits (not made; none authorised)
1. `feat: add dashboard extra pinning streamlit 1.65.0` — pyproject.toml, uv.lock
2. `fix: build_release exits non-zero without BR_PSEUDONYM_KEY and writes no bundle` — analysis/build_release.py, tests/test_release_pseudonym.py
3. `fix: split holdout v5 expected identifiers on commas only` — analysis/score_holdout_v5.py, tests/test_score_holdout_v5.py, tests/fixtures/holdout_v5_scorer/filled_spaces.md
4. `docs: describe the 99.7 ms graph query result as MET, at the limit` — docs/GRAPH_LAYER.md
5. `docs: session report for the open round` — docs/session/deepanshu-d50.md
Step 3 produced no tracked changes (data/ is ignored; paper/generated unchanged per git status).

## Needs ruling
Should the PAT-gated fetch (analysis/fetch_base_logs.py) run inside make tables at all now that the corpus is closed? It is skipped without PATs, and run silently if any GITHUB_PAT_* is in the shell, which would move base logs under the pinned corpus. Suggest moving it out of tables into an explicit target.

---

# Round 2 (rulings applied)

Rulings: streamlit 1.65.0 signed off; this report stays untracked (old commit 5 dropped). `docs/phase/029-holdout-v5-worksheet.md` was not opened, scored or modified. `.env` never read or printed. Everything foreground; PATs unset in every run.

## R2-1: worksheet tests repointed
`tests/test_score_holdout_v5.py`: a `worksheet` fixture runs `analysis/build_holdout_v5_worksheet.py --out <tmp_path>/blank-worksheet.md`; the four tests (`..._every_answer_field_empty`, `..._covers_every_fixture`, `test_parse_worksheet_reports_every_empty_cell`, and the scorer-refusal test, renamed `test_scorer_refuses_a_blank_worksheet_and_writes_no_seal`) use that copy. Every original assertion kept. The refusal test passes the tmp worksheet and a tmp seal path. The `WORKSHEET` constant is gone.

## R2-2: fetch out of `tables`
- `Makefile`: the PAT-gated `fetch_base_logs.py` block removed from `tables`; new `fetch-base-logs` target, which exits 1 without `GITHUB_PAT_1/_2/_3` and otherwise runs the script. `.PHONY` updated.
- `tests/test_makefile_pat_gate.py` rewritten (its old premise, a gate *inside* `tables`, no longer exists): `make -n tables` does not mention `fetch_base_logs` with no PAT and with `GITHUB_PAT_1=dummy`; `make -n fetch-base-logs` accepts each of `DEFAULT_ENV_KEYS`; `make fetch-base-logs` with no PAT fails and names `GITHUB_PAT`.
- `docs/REPRODUCE.md` updated.
- **FLAG, needs a ruling: `make tables` still makes a network call.** `analysis/resolve_bases.py` (Makefile line ~57, run unconditionally) calls `get_with_backoff` against `api.github.com/.../actions/workflows/<id>/runs`; with no PAT it falls back to `TokenPool(["dummy_pat_for_test"])`. `logs/requests.jsonl` shows it: `2026-10-07T18:13:16Z ... agno-agi/agno/actions/workflows/159196477/runs status 401`, which is the earlier `make tables` run. So the Step 3 claim above, "No GitHub API call made", was wrong. It is called without `--out`, so it writes nothing: its only product is stdout. Ruling "make tables must never invoke ... any network call" is therefore not yet true. Recommended fix (not applied, it removes a pipeline step): drop `resolve_bases.py` from `tables` and give it an explicit `make resolve-bases` target. `tests/test_base_resolve.py` / `test_promoted.py` import it and are unaffected.

## R2-3: full suite (before items 4-5)
`uv run --extra graph --extra dashboard pytest -q`, nothing deselected: **`658 passed, 1 skipped in 393.44s`**.

## R2-4: results inventory (read-only)
Method: ran the print-only scripts (rq1_divergence, corpus_delta, attrition_funnel, fixture_score, holdout_eval, verify_exact_green --report-only) and read parquet via DuckDB. Did not re-run `fault_revealing.py` / `binding_report.py` (they rewrite interim parquet); their figures come from the parquet on disk, written 2026-10-07 18:14. Of everything `make tables` runs, only **3 files reach `paper/generated/`**: `annotation_census.md`, `corpus_stats.md`, `expiry_cliff.md`. Everything else is stdout only. `paper/generated/attrition_funnel.md` is dated Aug 18 and **no script writes it**: stale, not regenerated by `make tables`.

| Step / output | What it measures | Headline |
|---|---|---|
| check_freshness.py | interim artifact older than an input | gate, no number |
| secret_scan.py | credential-shaped strings in release bundle | gate, no number |
| resolve_bases.py | base-run resolution (network, discards output; see R2-2) | stdout only |
| parse_base_logs.py | base-side parse | 452 logs, 2,990 outcome rows, 172 distinct test_ids (Step 3) |
| fault_revealing.py -> `outcomes.parquet` | labels, splits, flips | below |
| fixture_score.py | dev-fixture parser P/R | 46/46 TP, 0 FP, 0 FN, class acc 40/40 |
| holdout_eval.py | v1 held-out parser P/R | P=R=1.0000, class acc 20/20, cross-firing 0/20 |
| binding_report.py -> `binding.parquet` | test_id -> test file | below (e) |
| attrition_funnel.py | stage funnel | 300 frame repos, 76 swept, 12,986 PRs, 165,349 runs, 12,581 failed, 2,912 logs with test output, 7,061 with resolved base, 4,648 with known base-failure set, **762 with >=1 label** |
| rq1_divergence.py | RQ1 | below (a) |
| verify_exact_green.py --report-only | exact_green re-verification | 859/4,245 instances swept (20.2%); 265/1,732 base runs; 360 confirmed test-free; 410-exposure 9.0% instance / 14.0% run |
| corpus_delta.py | what the sweep moved | baseline strict 762 inst / 4,168 labels; evidence-only 703 / 4,020; invariant-6 137 / 439 |
| expiry_cliff.py, annotation_census.py, corpus_stats.py | log expiry, annotations, harvest state | corpus_stats: 77/300 repos, 175,038 runs, 13,422 failed runs |

**(a) RQ1 co-change vs fault-revealing: PRODUCED** (`rq1_divergence.py`, stdout; figures skipped, matplotlib absent). Comparison is on **files**: co-change top-k partner files vs bound test files of strict labels, n=558 instances where the proxy fires.

| k | Precision | Recall | Jaccard |
|---|---|---|---|
| 5 | 0.015 | 0.064 | 0.013 |
| 10 | 0.013 | 0.079 | 0.012 |
| 20 | 0.012 | 0.087 | 0.011 |

Also: 26.0% (4,053/15,604) changed files have a partner at support>=3; proxy silent on 143/734 instances (19.5%). Baselines at k=10: changeset J 0.035; historical top-k P 0.176 / R 0.522 / J 0.169. Note the denominators: n=558 here vs 734 instances with GT vs 762 strict.

**(b) Dataset composition: PARTIAL, no single script.**
- Splits (`fault_revealing.py` stdout / outcomes.parquet): all 897 inst / 4,384 labels / 2,500 distinct tests; relaxed 770 / 4,214 / 2,484; **strict 762 / 4,168 / 2,466**.
- Repos: strict labels span 37 repos (Java 35, Python 2); the 12,581 failed runs span 69 repos (Java 64, Python 5); `instances_raw` 76 repos; binding/parsed outcomes 43 repos; 20,451 parsed head outcome rows, 5,985 distinct test_ids.
- Languages by instance (strict): Java 638, Python 124.
- "Positives" is ambiguous: 762 instances vs 4,168 labels (see (f)).
- NOT PRODUCED as one table: repos x languages x instances x positives. Closest: `corpus_stats.py` (harvest state only, no labels) and `build_release.py`. Computed ad hoc above; no script emits it.

**(c) no_base rate and base_run_distance: PARTIAL.**
- no_base: **5,520 / 12,581 (43.88%)** (corpus_delta baseline, from `base_resolution_new`). Scenarios: evidence-only 6,147 (48.86%); invariant-6 9,533 (75.77%). Status mix: no_base 5,520, exact_green 4,245, exact 1,858, ancestor 591, branch_prior 367.
- base_run_distance distribution: **NOT PRODUCED**. `resolve_bases.py` prints `value_counts()` but only to stdout during a run whose output is discarded (and it hits the network). Ad hoc from `base_resolution_new` (not a script output): of 6,025 non-no_base rows, 4,809 at distance 0, 505 at 1, 227 at 2, 104 at 3, 128 at 4, then a tail to 10; 1,036 null (367 branch_prior, 669 exact_green); median 0, p90 2, p99 8, max 10. Script that should produce it: a small step in `corpus_delta.py` or `corpus_stats.py`.

**(d) Same-SHA flip / flakiness: PRODUCED but only on `fault_revealing.py` stdout**: 62 flips, 0.54% (Step 3). Not in any `paper/generated` file, no standalone script.

**(e) Binding, both numbers: PRODUCED (`binding_report.py` stdout), but the on-disk value disagrees with the published one.** `binding.parquet` on THIS machine (43/43 clones): **exact 5,643 / 5,985 (94.29%); full-confidence FQCN 3,820 (63.83%); basename-only 1,823 (30.46%)**; ambiguous 164, not_found 178. The recorded figures are 5,623 / 3,801 / 1,822 (DATASHEET §9, commit 631475a) and 5,622 / 3,819 / 1,803 (D-47). Three different machines/clone states, three different numbers on a 5,985 key space: exactly what the missing D-50 clone-pin TSV would resolve. Gate 1.5 (>=70%) holds on the combined figure and not on full-confidence in all three.

**(f) Gate 1, instance and label counts: PARTIAL, and one script reports it wrongly.**
- `corpus_delta.py` prints the label form per D-44 (baseline 4,168; evidence-only 4,020 / 5,000; invariant-6 439 / 5,000), all NOT MET.
- `fault_revealing.py` ends with `Gate 1 Positives: 762 / 5000 (Met? No)`, which counts **instances**, contrary to D-44 (labels). The current figure is **4,168 labels (strict) / 762 instances**, both against 5,000. Not fixed here (no new analyses; flagged).

## R2-5: demo
- `analysis/demo_walkthrough.py`, `make demo` (`uv run --extra graph python analysis/demo_walkthrough.py`), `tests/test_demo_walkthrough.py` (5 tests), REPRODUCE.md paragraph.
- Read-only (temp dir only), offline (`GIT_NO_LAZY_FETCH=1`), deterministic (sorted `(repo, PR, run, test)`, no RNG, no timing in stdout). Repos parsed from `docs/MINI_CORPUS.md`. Gates: strict label in mini repo -> bound test -> no holdout job -> raw log in RawStore -> graph in `data/graphs/`.
- **Holdout guard caveat:** `docs/session/holdout-exclusion.txt` does not exist on this machine (untracked, held elsewhere). The guard uses the 122 job ids parsed from FILE NAMES in `tests/fixtures/holdout*/` (names only, no contents) plus the exclusion file when present, and the output states which. It excludes any run with a head job in that set (79 -> 76 instances). Without the exclusion file this is a lower bound on the holdout list.
- **`data/graphs/` is empty here** (0 graphs; REPRODUCE.md expects 427). So plain `make demo` prints the selection report and exits 2 `NO QUALIFYING INSTANCE`, by design. `--build-graph-offline` builds the missing graph in a temp dir from local objects only. The corpus clones are `--filter=blob:none`; trees with missing blobs are skipped, not fetched. 4 instances qualify that way.
- Disclosure: while exploring the graph API I ran one `build_graph_at` on `fla-org/flash-linear-attention@7378dfed` WITHOUT `GIT_NO_LAZY_FETCH`; on a blobless clone that checkout may have lazily fetched blobs from GitHub (unauthenticated git, no PAT). That is why that tree is now local and the offline demo can use it. It changed only ignored `data/clones/` state.
- Timing: `make demo` 1.4 s (exit 2); `--build-graph-offline` 32 s wall (rc 0), under 60 s.

### `make demo` output (full)
```
uv run --extra graph python analysis/demo_walkthrough.py
SELECTION (sorted by repo, PR, run, test; first instance clearing every gate)
  mini-corpus repos (docs/MINI_CORPUS.md): Stirling-Tools/Stirling-PDF, fla-org/flash-linear-attention, spiculedata/saiku
  holdout exclusion: 122 job ids from tests/fixtures/holdout*/ names; docs/session/holdout-exclusion.txt ABSENT on this machine, fixture names only
  gate 1 strict labels in mini-corpus repos: 222 labels, 79 instances
  gate 2 with a bound test and a resolved base: 222 labels, 79 instances
  gate 3 not touching a holdout job: 76 instances
  gate 4 raw log in local RawStore: 76 instances
  gate 5 graph in data/graphs/: 0 instances (0 graphs on disk)

NO QUALIFYING INSTANCE: nothing cleared every gate, so nothing is shown.
  (a populated data/graphs/ is required; see docs/REPRODUCE.md, or pass --build-graph-offline)
make: *** [Makefile:91: demo] Error 2

real	0m1.393s
user	0m2.461s
sys	0m0.478s
rc=2
```

### `--build-graph-offline` output (full)
```
SELECTION (sorted by repo, PR, run, test; first instance clearing every gate)
  mini-corpus repos (docs/MINI_CORPUS.md): Stirling-Tools/Stirling-PDF, fla-org/flash-linear-attention, spiculedata/saiku
  holdout exclusion: 122 job ids from tests/fixtures/holdout*/ names; docs/session/holdout-exclusion.txt ABSENT on this machine, fixture names only
  gate 1 strict labels in mini-corpus repos: 222 labels, 79 instances
  gate 2 with a bound test and a resolved base: 222 labels, 79 instances
  gate 3 not touching a holdout job: 76 instances
  gate 4 raw log in local RawStore: 76 instances
  gate 5 graph in data/graphs/: 0 instances (0 graphs on disk)
  gate 5 (--build-graph-offline) buildable from local objects: 4 instances

1) THE CHANGE
  repo        fla-org/flash-linear-attention
  pull request #935  (workflow 'nvidia-h100-ci', run 26953319747)
  head commit 49a32325aa49875b5d1035614dbca43bdb04cd22
  base commit 7378dfed2ac08242b3770be43fd4539df636afc3   (resolved base, status 'exact_green')

2) THE RAW CI LOG  (job 79523862541, lines that name the failing test)
  | 2026-06-04T13:01:45.6359864Z tests/layers/test_layer_cache_layer_idx.py::test_cache_requires_layer_idx[linear_attn] FAILED
  | 2026-06-04T13:01:45.6388642Z FAILED tests/layers/test_layer_cache_layer_idx.py::test_cache_requires_layer_idx[linear_attn] - RuntimeError: No CUDA GPUs are available
  | 2026-06-04T13:01:45.6361526Z __________________ test_cache_requires_layer_idx[linear_attn] __________________
  | 2026-06-04T13:01:45.6364849Z     def test_cache_requires_layer_idx(builder, hidden_states):

3) THE PARSED OUTCOME
  canonical test_id  tests/layers/test_layer_cache_layer_idx.py::test_cache_requires_layer_idx
  status fail, harness pytest, parser confidence 0.90, fqcn-qualified True

4) THE BASE RUN
  base run 26951686117, distance 0 commits, conclusion not captured
  this test at the base run: no failure recorded

5) THE FAULT-REVEALING VERDICT
  T_head_fail  = 2 tests failed at head
  T_base_fail  = 0 tests failed at base
  flaky        = 0 (fail in some but not all of 1 run(s) of this workflow on this head SHA)
  T_reveal     = T_head_fail - T_base_fail - flaky = 2 tests
  this test: in head True, in base False, flaky False  ->  fault-revealing True
  agrees with outcomes.parquet (strict split): True (2 recorded)

6) THE BOUND TEST FILE
  tests/layers/test_layer_cache_layer_idx.py  (binding 'exact', 1 candidate file(s) considered)

7) GRAPH CONTEXT  (graph at the base commit; hops on the undirected projection)
  the PR changed 32 file(s)
  graph: built into a throw-away temp dir from local git objects (data/graphs/ has none for this SHA)
  test node: tests_layers_test_layer_cache_layer_idx_test_cache_requires_layer_idx [the test's own node]
    fla/ops/comba/wy_fast.py: 5 hop(s) to the test
    fla/ops/delta_rule/chunk.py: 4 hop(s) to the test
    fla/ops/delta_rule/wy_fast.py: 5 hop(s) to the test
    fla/ops/gated_delta_rule/chunk.py: 4 hop(s) to the test
    fla/ops/gated_delta_rule/chunk_fwd.py: 5 hop(s) to the test
    fla/ops/gated_delta_rule/wy_fast.py: 5 hop(s) to the test
    fla/ops/gated_oja_rule/chunk.py: 4 hop(s) to the test
    fla/ops/gated_oja_rule/chunk_h.py: 5 hop(s) to the test
    fla/ops/gated_oja_rule/wy_fast.py: 5 hop(s) to the test
    fla/ops/generalized_delta_rule/iplr/chunk.py: 5 hop(s) to the test
    ... 22 more
  min_distance_to_any_changed = 4 hop(s)

8) CO-CHANGE vs WHAT ACTUALLY FAILED
  co-change set (top 10 partners per changed file): 20 files
  actual failing set (bound test files): 2 files
  overlap: 0   precision 0.000  recall 0.000  jaccard 0.000
    predicted: fla/ops/common/chunk_o.py, fla/ops/gated_delta_product/chunk.py, fla/ops/gated_delta_rule/fused_recurrent.py, fla/ops/gated_delta_rule/gate.py, fla/ops/gla/chunk.py ...
    actual: tests/layers/test_layer_cache_layer_idx.py, tests/models/test_modeling_comba.py
    overlap: -

real	0m32.201s
user	0m55.792s
sys	0m16.789s
rc=0
```

## R2-6: full suite after all changes
`uv run --extra graph --extra dashboard pytest -q`, nothing deselected: **`663 passed, 1 skipped in 422.17s (0:07:02)`**. (658 + 5 new demo tests; the 4 previously deselected worksheet tests now run against tmp copies and pass.)

## R2 proposed commits (not made; none authorised). Identity checked: DeepanshuOP / 99538840+DeepanshuOP@users.noreply.github.com. No trailers.
1. `feat: add dashboard extra pinning streamlit 1.65.0` — pyproject.toml, uv.lock
2. `fix: build_release exits non-zero without BR_PSEUDONYM_KEY and writes no bundle` — analysis/build_release.py, tests/test_release_pseudonym.py
3. `fix: split holdout v5 expected identifiers on commas only` — analysis/score_holdout_v5.py, tests/test_score_holdout_v5.py, tests/fixtures/holdout_v5_scorer/filled_spaces.md
4. `docs: describe the 99.7 ms graph query result as MET, at the limit` — docs/GRAPH_LAYER.md
5. `test: generate the blank holdout v5 worksheet into tmp_path instead of reading the closed one` — tests/test_score_holdout_v5.py (shares a file with 3; commit 3 first, or fold 5 into 3 with `git add -p`)
6. `fix: move base-log fetch out of make tables into make fetch-base-logs` — Makefile, tests/test_makefile_pat_gate.py, docs/REPRODUCE.md (Makefile also carries the `demo` target; fold item 7's Makefile hunk with `git add -p`)
7. `feat: add read-only demo walkthrough and make demo` — analysis/demo_walkthrough.py, tests/test_demo_walkthrough.py, Makefile (demo hunk), docs/REPRODUCE.md (demo paragraph)

Item 8 (inventory) is report-only; no commit. Needs a ruling: R2-2 flag (`resolve_bases.py` in `tables`), and (f) the `fault_revealing.py` Gate 1 line.

---

# ROUND 3 (2026-10-07)

All runs foreground, `GITHUB_PAT_1/2/3` unset, `.env` never printed, `docs/phase/029-holdout-v5-worksheet.md` never opened, scored or modified. Nothing committed in Round 3.

## R3-0: Part 1, commit round 2 (done, pushed)

Identity checked before committing: `DeepanshuOP` / `99538840+DeepanshuOP@users.noreply.github.com`. No trailers (CLAUDE.md overrides the harness attribution reminder). Order 1,2,3,5,4,6,7:

| # | sha | message |
|---|---|---|
| 1 | b96d2b1 | feat: add dashboard extra pinning streamlit 1.65.0 |
| 2 | 73dcd93 | fix: build_release exits non-zero without BR_PSEUDONYM_KEY and writes no bundle |
| 3 | b54b037 | fix: split holdout v5 expected identifiers on commas only |
| 5 | d9c1b7d | test: generate the blank holdout v5 worksheet into tmp_path instead of reading the closed one |
| 4 | 37ab59e | docs: describe the 99.7 ms graph query result as MET, at the limit |
| 6 | a84d5d6 | fix: move base-log fetch out of make tables into make fetch-base-logs |
| 7 | 4e76919 | feat: add read-only demo walkthrough and make demo |

Shared files were split by building the staged blob directly (not interactive `git add -p`, which is unavailable here): commit 3 staged the test file with only the `FILLED_SPACES` constant and the new test; commit 5 then took the rest. Commit 6 staged Makefile and REPRODUCE.md with the `demo` target, `make demo` line and demo paragraph removed; commit 7 added them back. Full suite after the last commit: **663 passed, 1 skipped in 402 s**. `git push origin main` (no force): `616a4e8..4e76919`; `git rev-parse main origin/main` both `4e76919452e83ec45d08214fbb3003fe35d1591b`. Session report left untracked.

## R3-1: demo

`analysis/demo_walkthrough.py`, new `analysis/failure_class.py`, `Makefile` (`demo` now sets `GIT_NO_LAZY_FETCH=1` itself as well as in the script).
- A missing graph is now built offline by default (temp dir, local git objects only, `GIT_NO_LAZY_FETCH=1`). `--no-build-graph` restores the strict behaviour; `--build-graph-offline` is accepted and is a no-op.
- Selection ranks candidates code-level, then unknown, then environment, and the selection report prints the classification counts and the chosen rule. The offline-buildable check is lazy and cached per (repo, base SHA): 1 pair checked, 1 buildable.
- Classification (ordered, case-insensitive regex; full list is printed in `paper/generated/infra_failures.md`): 1. message starts with an assertion marker, then code-level; 2. environment patterns anywhere (CUDA/GPU, OOM, timeout, connection, DNS, missing service); 3. code patterns anywhere (assertion, expected-vs-actual); 4. unknown.
- Result of the final `make demo`: **exit 0, 27.7 s** (before this round the same instance was selected at 32 s). Candidates: code-level 65/228, unknown 101/228, environment 62/228. Selected instance is code-level (`leading-assertion`). Full output is in the transcript above.

## R3-2: network guard

`src/harvest/ratelimit.py`: `OfflineError`; `get_with_backoff()` raises it first thing when `BR_OFFLINE=1`, before a token is acquired or a socket opened (and before anything is logged). `Makefile`: `tables: export BR_OFFLINE=1`; `resolve_bases.py` removed from `tables` and made `make resolve-bases` (refuses without `GITHUB_PAT_1/_2/_3`). Tests (`tests/test_network_guard.py`, 5): `make -n tables` mentions neither `resolve_bases` nor `fetch_base_logs`, with and without a PAT; the Makefile exports `BR_OFFLINE`; `resolve-bases` is a target; `get_with_backoff` raises under `BR_OFFLINE=1` with `socket.socket` and `create_connection` replaced by failing stubs, opens none, writes no log line.
`make tables`, run twice with PATs unset: `logs/requests.jsonl` **335,543 → 335,543 lines (0 gained)** both times, rc 0.

## R3-3: Gate 1 line

`src/label/fault_revealing.py` now prints `Gate 1 (D-44, primary) labels: 4168 / 5000 (Met? No)` then `Gate 1 (secondary) instances: 762 / 5000 (Met? No)`, via `gate1_lines()`. Old: `Gate 1 Positives: 762 / 5000` (instances). Two tests added to `tests/test_fault_revealing.py`.

## R3-4: D-50

- All 43 corpus clones pass `is_usable_clone()` (checked before pinning).
- `docs/CLONE_PINS.json` written from the 43 HEADs (`python analysis/binding_report.py --write-pins`; sorted keys, no timestamp, byte-stable on rewrite).
- `binding_report.py` now binds through `bind_tests(..., pins)` using `_get_git_tree(repo, <pin sha>)` (new `rev` argument, default `HEAD`); it never reads HEAD and exits with BLOCKED if the pin file is absent or any pinned tree is missing. `is_usable_clone(path, pin=None)` requires the pinned tree to list at least one path; blobless clones pass (tested against a real `--filter=blob:none` clone). Tree index is now built from sorted paths, so candidate order is deterministic.
- Tests (`tests/test_binding_pins.py`, 6): a moved HEAD still binds against the pin (and does not against HEAD); a missing pinned sha is rejected; unpinned or absent-sha repos are listed by `missing_clones`; blobless clone passes; `write_pins` is deterministic; `load_pins` refuses a missing file. `tests/test_binding_clone_guard.py` assertion changed from citing D-47's figure to citing D-50.
- **PREDICT vs ACTUAL, over 5,985 rows: combined 5,643 predicted / 5,643 actual; full confidence 3,820 / 3,820; rows 5,985 / 5,985. No difference.** Residuals: basename-only 1,823/5,985 (30.46%), not_found 178/5,985 (2.97%), ambiguous 164/5,985 (2.74%), unqualified 0.
- Old → new: combined 5,622 → 5,643 (93.93% → 94.29%); full 3,819 → 3,820 (63.81% → 63.83%); basename-only 1,803 → 1,823 (30.13% → 30.46%); not_found 199 → 178 (3.32% → 2.97%); ambiguous 164 → 164. (Prisha's 5,623 / 3,801 are superseded too.) Gate 1.5: **MET** combined (94.29% vs 70%), **NOT MET** full confidence (63.83%).
- D-50 appended to `docs/DECISIONS.md` (Decided by: Deepanshu; revisit trigger: per-instance-SHA binding); D-47 got a "superseded in part by D-50" line.
- Supersession notes or in-place updates in: `docs/CURRENT-STATE.md` (3 places), `docs/DATASHEET.md`, `docs/HANDOVER-020.md` §3.4, `docs/phase/023-binding-rate.md`, `docs/phase/005C-REPORT.md`, `docs/phase/020-parser-survey-REPORT.md`, `docs/HANDOFF.md`, `docs/session/prisha-087-impl-report.md`, `tests/test_binding_clone_guard.py` (docstring), `analysis/binding_report.py` (docstring). Untouched by design: `data/frame/*.csv` hits for "3819"/"5622" are unrelated star/commit counts.

## R3-5: paper/generated/

New: `analysis/paper_md.py` (header with script + full git sha, `n/d (x.xx%)` rates, no timestamps), `analysis/paper_numbers.py` (composition, base_resolution, binding, gates), `analysis/parser_precision_table.py`, `analysis/capture_stdout.py`. `make tables` order now: freshness, secret_scan, parse_base_logs, fault_revealing, fixture_score, holdout_eval, parser_precision_table, binding_report, paper_numbers, attrition_funnel, rq1_divergence, infra_failure_audit, verify_exact_green --report-only, corpus_delta, expiry_cliff, annotation_census, corpus_stats.
Files written (all regenerated by the final `make tables`): `composition.md`, `base_resolution.md`, `flakiness.md` (written by `fault_revealing.py`, which holds the flip statistics; new `n_sha_test_pairs` stat), `binding.md`, `gates.md`, `attrition_funnel.md` (rewritten from the current script), `parser_precision.md`, plus `rq1.md`, `infra_failures.md`.
Headline checks: strict 762 instances / 4,168 labels / 2,466 distinct tests (all 897/4,384, relaxed 770/4,214, unchanged); same-SHA flips 62/11,557 (0.54%); no_base 5,520/12,581 (43.88%); base_run_distance (6,025/7,061 resolved rows carry one) median 0, p90 2, p99 8, max 10; Gate 1 labels 4,168/5,000 NOT MET, instances 762/5,000 NOT MET.
(g): fixture corpus 46/46 precision, 46/46 recall, 40/40 class; holdout v1 30/30, 30/30, 20/20. **Both are marked NOT independent of development**, citing `docs/phase/013B-holdout-v5-protocol.md` §4 and `docs/phase/027-scorer-provenance.md` / `docs/HANDOVER-020.md` §3.5 (D-37).
**Stdout-only headlines:** to satisfy "nothing only on stdout", `capture_stdout.py` runs a script unchanged and also writes its stdout VERBATIM (fenced) to markdown. Used for `parse_base_logs.py` → `base_log_parse.md`, `fault_revealing.py` → `labelling_run.md`, `binding_report.py` → `binding_run.md`, `verify_exact_green.py --report-only` → `exact_green_report.md`, `corpus_delta.py` → `corpus_delta.md`. Not captured: `check_freshness`, `secret_scan` (gating diagnostics, not paper figures), `fixture_score`/`holdout_eval` per-fixture tables (their headline is in `parser_precision.md`).

## R3-6: RQ1, fair variant

`analysis/rq1_divergence.py` refactored into `load_data` / `ground_truth` / `evaluate_k` / `write_rq1_md` (so item 7 can reuse it); the old printed numbers are **unchanged** (diffed old vs new stdout: identical except the new test-restricted lines). Writes `paper/generated/rq1.md`: for k in {5,10,20}, P/R/J with n for four methods, overall and per language (Java, Python), plus micro P and R as n/d, plus the three denominators: **strict 762 → with ground truth 734/762 (96.33%) → proxy fires 558/734 (76.02%)** at each k. All four methods are scored on the same 558 instances.
Overall, k=10 (n=558), mean P/R/J: co-change all 0.013/0.079/0.012; co-change test-only 0.036/0.087/0.026; changeset 0.038/0.249/0.035; historical frequency 0.176/0.522/0.169. Restricting to test files roughly triples co-change precision and does not close the gap to either baseline.
**Needs your ruling:** "the same test-file predicate the binding step uses" does not exist. The binding step resolves ids to files by name and has no file-level predicate. The only one in the pipeline is `"test" in filename.lower()` (behind `touches_test_file` in `src/parse/changeset.py`); I factored it out as `is_test_filename()` (behaviour unchanged) and used it. It passes 1,527/1,527 (100.00%) of ground-truth (instance, file) pairs, so it cannot cap recall, but it is also permissive. The restriction is applied before the top-k cut. If you meant a different predicate, one line changes.

## R3-7: environment-failure audit (measurement only, no label changed)

`analysis/infra_failure_audit.py` → `paper/generated/infra_failures.md`. Per strict label (rows of one label: code-level if any row is, else environment if any is, else unknown):
- **code-level 727/4,168 (17.44%), environment 203/4,168 (4.87%), unknown 3,238/4,168 (77.69%)**, of which no message recorded 2,231/4,168 (53.53%) and message matched no pattern 1,007/4,168 (24.16%). The audit is blind where the message is empty.
- Instances: with at least one environment label 121/762 (15.88%); all labels environment 86/762 (11.29%).
- **By language: Python 131/313 (41.85%) environment (mostly CUDA/GPU and timeouts); Java 72/3,855 (1.87%).**
- Rules: timeout 114, cuda-gpu-unavailable 66, connection-error 22, missing-service 1 (labels).
- RQ1 sensitivity (environment labels removed, n 558 → 491), co-change all partners mean R: k=5 0.064 → 0.054, k=10 0.079 → 0.072, k=20 0.087 → 0.081; precision 0.015 → 0.013, 0.013 → 0.011, 0.012 → 0.010. Historical baseline R: 0.424 → 0.421, 0.522 → 0.505, 0.585 → 0.563. The qualitative ordering does not change.
- Hand review of the 10 sampled messages (seed 20261110): 2 are unambiguous environment (`No CUDA GPUs are available`); the other 8 are all timeouts: 3 Awaitility `ConditionTimeout`, 1 Selenium visibility wait, 3 bare or asyncio `TimeoutError`, 1 pytest-timeout. Any of those can be a real hang caused by the change. **The `timeout` rule (114 of 203 environment labels) over-includes**: a timeout is a symptom, not proof the environment is at fault. Also `timed? ?out` matches the substring in an identifier such as `PARTIAL_TIMEOUT`. Read 203 as a ceiling on environment labels among labels that carry a message, and a floor overall, since 53.53% carry none.

## R3-8: figures extra

`pyproject.toml`: `figures = ["matplotlib==3.11.2"]`. Proof it changed no locked package: compared package→version of the lock before and after: **75 previously locked, 0 changed, 0 removed; 6 added** (matplotlib 3.11.2, contourpy 1.3.3, cycler 0.12.1, fonttools 4.66.1, kiwisolver 1.5.1, pyparsing 3.3.3), all reachable only via the extra. `rq1_divergence.py` writes `fig1_applicability.pdf` and `fig2_accuracy.pdf` to `paper/generated/` when matplotlib is importable (fig2 now includes the test-restricted line) and skips with a warning otherwise; the PDFs are byte-identical across runs (`CreationDate` suppressed; tested).

## R3-9: verification

- Full suite, nothing deselected (`--extra graph --extra dashboard --extra figures`): **711 passed, 1 skipped in 544 s** (663 → 711, +48 tests).
- `make tables` (final): rc 0, 6 m 41 s (an earlier run took 9 m 30 s; it sits close to a 10-minute tool timeout), `requests.jsonl` +0 lines.
- `make demo` (final): rc 0, 27.7 s.
- `git status --short --ignored paper/generated/` prints only `!! paper/generated/`: **the directory is git-ignored (`.gitignore:6`)**, so none of these files can be committed as things stand. 19 files on disk: the 11 above, `base_log_parse`, `labelling_run`, `binding_run`, `exact_green_report`, `corpus_delta`, plus the 3 older ones (`annotation_census`, `corpus_stats`, `expiry_cliff`) and 2 PDFs. I did not touch `.gitignore`.

## Things that need a decision or that look wrong

1. **`paper/generated/` is git-ignored.** If the tables are meant to be reviewable in git, un-ignore it (or the specific files). Not changed.
2. **Test-file predicate for the RQ1 fair variant** (see R3-6).
3. **Attrition funnel is internally inconsistent**: `logs not expired` 15,259 exceeds `logs captured` 14,104 (108.19%), and `logs captured` includes a hard-coded +394 and a hard-coded 13,710 fallback. Recorded as caveats in the md, not fixed. Also `parse_base_logs` reports 4,649 instances with both head and base failure sets while the funnel computes 4,648.
4. The frame-stage funnel (SEART → sample draw: 3,671 / 2,646 / 2,333 / 300) in the old Aug-18 md is gone; its generator was replaced in d6990fb (recoverable from c042ea8). Not regenerated.
5. The historical-frequency baseline counts labels from all three splits (`all`, `relaxed`, `strict` rows), so strict-label tests are triple-weighted in the ranking. Pre-existing; unchanged so the old numbers reproduce.
6. `corpus_delta.py` (now captured in `corpus_delta.md`) prints alternative scenarios; its invariant-6 scenario gives 137 instances / 439 labels (Gate 1 439/5,000). That is a counterfactual, not the committed corpus, but a reader of the md could mistake it.
7. `make tables` is long (6.7 to 9.5 min).

## R3 proposed commits (not made; none authorised). Identity: DeepanshuOP / 99538840+DeepanshuOP@users.noreply.github.com. No trailers.

Several files are shared between items, so the hunks need splitting as in Part 1. Suggested order: 4, 2, 3, 1, 8, 6, 7, 5.

1. `feat: build the demo graph offline by default and prefer code-level failures` — analysis/demo_walkthrough.py, analysis/failure_class.py, tests/test_failure_class.py, tests/test_demo_walkthrough.py, Makefile (demo hunk only), docs/REPRODUCE.md (demo paragraph and `make demo` line)
2. `fix: move resolve_bases out of make tables and refuse network calls under BR_OFFLINE` — src/harvest/ratelimit.py, tests/test_network_guard.py, Makefile (PHONY, `tables: export`, `resolve_bases` removal, `resolve-bases` target), docs/DATA_DEPENDENCIES.md, docs/REPRODUCE.md (network paragraph)
3. `fix: print Gate 1 as labels (D-44, primary) and instances` — src/label/fault_revealing.py (`gate1_lines` hunks only), tests/test_fault_revealing.py (the two gate1 tests)
4. `data: pin binding to clone commits and record D-50` — analysis/binding_report.py, src/parse/test_files.py, docs/CLONE_PINS.json, tests/test_binding_pins.py, tests/test_binding_clone_guard.py, docs/DECISIONS.md, docs/CURRENT-STATE.md, docs/DATASHEET.md, docs/HANDOVER-020.md, docs/HANDOFF.md, docs/phase/005C-REPORT.md, docs/phase/020-parser-survey-REPORT.md, docs/phase/023-binding-rate.md, docs/session/prisha-087-impl-report.md
5. `feat: write every paper number to paper/generated from make tables` — analysis/paper_md.py, analysis/paper_numbers.py, analysis/parser_precision_table.py, analysis/capture_stdout.py, analysis/attrition_funnel.py, src/label/fault_revealing.py (flakiness hunks), tests/test_paper_numbers.py, tests/test_parser_precision_table.py, tests/test_capture_stdout.py, tests/test_fault_revealing.py (flakiness test), Makefile (tables wiring), docs/REPRODUCE.md (paper/generated paragraph)
6. `feat: add test-file-restricted co-change and per-language results to RQ1` — analysis/rq1_divergence.py (all but the savefig metadata and the figure test), src/parse/changeset.py, tests/test_rq1_divergence.py (all but the figure test)
7. `feat: add the environment-failure audit with an RQ1 sensitivity table` — analysis/infra_failure_audit.py, tests/test_infra_failure_audit.py, Makefile (`infra_failure_audit` line). Depends on commits 1 and 6 (`failure_class.py`, `rq1_divergence.py`).
8. `feat: add figures extra pinning matplotlib 3.11.2` — pyproject.toml, uv.lock, analysis/rq1_divergence.py (deterministic `savefig` metadata), tests/test_rq1_divergence.py (figure test)

STOP: nothing committed, nothing pushed in Round 3.

# ROUND 4 (2026-10-07). Identity DeepanshuOP / 99538840+DeepanshuOP@users.noreply.github.com. No trailers. PATs unset in every run, `.env` never printed, `docs/phase/029-holdout-v5-worksheet.md` never opened, scored or modified. All commands foreground.

## R4-0: Part 1, commit round 3 (done, pushed)

Order 4,2,3,1,8,6,7,5. Shared files were split by building the staged blob (zero-context `git apply` mis-placed the `resolve-bases` block in the first attempt, and my REPRODUCE helper read `HEAD` instead of the pre-round base and duplicated two paragraphs; both were caught before anything was pushed and the three affected commits were redone from the working tree, which is the source of truth).

| # | sha | message |
|---|---|---|
| 4 | 669eff3 | data: pin binding to clone commits and record D-50 |
| 2 | 648ef2b | fix: move resolve_bases out of make tables and refuse network calls under BR_OFFLINE |
| 3 | 27416fc | fix: print Gate 1 as labels (D-44, primary) and instances |
| 1 | 8594ebf | feat: build the demo graph offline by default and prefer code-level failures |
| 8 | ca2dc34 | feat: add figures extra pinning matplotlib 3.11.2 |
| 6 | 6952a37 | feat: add test-file-restricted co-change and per-language results to RQ1 |
| 7 | e8d252f | feat: add the environment-failure audit with an RQ1 sensitivity table |
| 5 | f79ace1 | feat: write every paper number to paper/generated from make tables |

Deviations from the Round 3 plan: the `docs/REPRODUCE.md` binding-pin paragraph went in commit 4; the figure test lives in `tests/test_rq1_divergence.py`, so it shipped with commit 6, not 8 (commit 8 carries only the `savefig` metadata change, the extra and the lock). Full suite after the last: **711 passed, 1 skipped in 470 s**. `git push origin main` (no force): `4e76919..f79ace1`; `git rev-parse main origin/main` both `f79ace18dc08cc2473ed46cd78b6840bfa660668`.

## R4-1: leakage audit (`analysis/leakage_audit.py` → `paper/generated/leakage_audit.md`, run by `make tables`)

Every one of the 762 strict instances is checked; the script exits non-zero if a CURRENT method violates anything (it does not).

**(a) Historical-frequency baseline.** It already read only runs that started strictly before the instance (`run_started_at <`), so it did **not** leak in time. Its defects were different. Current (strict labels, once each) vs legacy (all splits), violations are instances n/d:

| check | current | legacy |
|---|---|---|
| evidence from a run starting at/after the instance | 0/762 (0.00%) | 0/762 (0.00%) |
| the instance's own run in the evidence | 0/762 (0.00%) | 0/762 (0.00%) |
| non-strict rows in the evidence | 0/762 (0.00%) | 723/762 (94.88%) |
| a (run, test) counted more than once | 0/762 (0.00%) | 721/762 (94.62%) |
| evidence rows / distinct (run, test) labels, summed | 72,809 / 72,809 | 224,758 / 78,399 |
| observation: evidence includes another run of the same head commit | 47/762 (6.17%) | 47/762 (6.17%) |

Triple counting confirmed: 224,758 rows for 78,399 distinct labels (2.87x). Caveat the audit prints: the baseline orders by START time; `instances_raw` has no completion time, so a run still executing at the instance's start would be visible here and not in deployment. Not checkable locally. The 47 same-head-commit instances are an observation, not a violation (the rule is "before", not "different commit"); say if you want them excluded.

**(b) Co-change LEAKED.** `data/interim/cochange.parquet` is mined over a window ending at the corpus pin (2026-08-29T14:13:00Z), so every instance saw commits that landed after it ran:

| check | n/d |
|---|---|
| legacy: window ends after the instance started | 713/713 (100.00%) |
| legacy: a mined commit dated in `[run_started_at, as_of]` touches a changed file of the instance | 640/713 (89.76%) |
| current (per-instance trailing history): a commit at/after `run_started_at` behind a partner (times re-read from git) | 0/713 (0.00%) |
| current: a used commit git cannot time / older than the 365-day window / the instance's own head commit used | 0/713, 0/713, 0/713 |

(713 = strict instances with a changeset; 49 strict instances have none and cannot be scored by either method.) Fix: `analysis/cochange_trailing.py` mines the same statistic (365 d, support >= 2 as in `COCHANGE_PIN.json`, merges and >50-file commits skipped) from the clone's log at the **pinned** commit (`docs/CLONE_PINS.json`), restricted per instance to committer time in `[run_started_at - 365 d, run_started_at)` and excluding the instance's own head sha. Ranking is now deterministic (confidence, support, path); the static table's tie order was not. Note: the clones are blobless, so `git log --no-renames` is used (rename detection needs blobs and fails offline); a renamed file appears under old and new path. Axis 1 (applicability) is trailing too.

**Found while fixing, NOT changed (needs your ruling): the static table was looked up one-sidedly.** It stores each pair once as `file_a < file_b` and RQ1 read it by `file_a` only, so a changed file's candidates were only the lexicographically LATER paths. The fixed version keeps this reach so the leakage effect is isolated; the last column below shows both directions. Both directions lowers all-partner co-change recall at k=10 from .082 to .051 (P .017 → .011), leaves the test-restricted variant about the same (R .090 → .087), and moves n 533 → 576.

### RQ1 old → new, mean P / R / J (n = instances where the all-partners proxy fires). Stages are separate so each effect is visible.

Stage 0 reproduces the Round 3 numbers exactly (n=558; e.g. historical k=10 0.176/0.522/0.169). Stage 1 = baseline counted once from the strict split only (co-change unchanged). Stage 2 = co-change trailing only (baseline unchanged). Stage 3 = both = current. The "test" rows: old test-only row = `is_test_filename`; current primary = `is_conventional_test_file` (item 2).

| k | method | 0 old | 1 dedupe only | 2 leak fix only | 3 both (new) | info: both directions |
|---|---|---|---|---|---|---|
| 5 | co-change, all | 558: .015/.064/.013 | same | 532: .018/.066/.016 | 532: .018/.066/.016 | 575: .012/.038/.011 |
| 5 | co-change, "test" in path (old test-only) | .036/.073/.026 | same | .054/.071/.035 | .054/.071/.035 | .046/.061/.030 |
| 5 | co-change, conventional test files (new primary) | n/a | n/a | .061/.073/.041 | .061/.073/.041 | .054/.069/.037 |
| 5 | changeset | .038/.249/.035 | same | .037/.251/.034 | .037/.251/.034 | .039/.245/.037 |
| 5 | historical frequency | .198/.424/.186 | .202/.419/.189 | .196/.422/.183 | .200/.417/.186 | .201/.423/.188 |
| 10 | co-change, all | 558: .013/.079/.012 | same | 533: .017/.082/.015 | 533: .017/.082/.015 | 576: .011/.051/.010 |
| 10 | co-change, "test" in path | .036/.087/.026 | same | .055/.090/.037 | .055/.090/.037 | .048/.087/.033 |
| 10 | co-change, conventional | n/a | n/a | .063/.090/.043 | .063/.090/.043 | .054/.087/.038 |
| 10 | changeset | .038/.249/.035 | same | .036/.250/.034 | .036/.250/.034 | .039/.245/.037 |
| 10 | historical frequency | .176/.522/.169 | .186/.514/.179 | .175/.517/.168 | .186/.509/.178 | .185/.517/.178 |
| 20 | co-change, all | 558: .012/.087/.011 | same | 533: .016/.089/.014 | 533: .016/.089/.014 | 576: .011/.063/.010 |
| 20 | co-change, "test" in path | .037/.098/.027 | same | .055/.091/.037 | .055/.091/.037 | .048/.089/.033 |
| 20 | co-change, conventional | n/a | n/a | .063/.091/.043 | .063/.091/.043 | .054/.089/.038 |
| 20 | changeset | .038/.249/.035 | same | .036/.250/.034 | .036/.250/.034 | .039/.245/.037 |
| 20 | historical frequency | .165/.585/.160 | .178/.573/.172 | .163/.580/.158 | .177/.568/.170 | .177/.575/.170 |

Reading (measurement, not a claim about the method): the leak fix **raised** co-change precision slightly and recall slightly (k=10: R .079 → .082) and cost 25 instances (558 → 533, k=10) where the proxy no longer fires; the dedupe moved the historical baseline by +0.010 P / -0.008 R at k=10 (stage 0 → 1). The ordering (historical > changeset > co-change on recall; historical best on P) is unchanged. Applicability (Axis 1) with trailing history: changed files with a partner at support >= 2 4,777/15,604 (30.61%) (was 6,442/15,604, 41.3%); proxy entirely silent on 169/734 (23.02%) (was 143/734, 19.5%).

Tests: `tests/test_cochange_trailing.py` (8, a real git repo built with fixed committer dates: strict-before cutoff, commit at the cutoff invisible, own head excluded, window, one-sided vs both, tie order, oversize and merge skipped), `tests/test_leakage_audit.py` (5, injected leaks are each counted), plus 5 new in `tests/test_rq1_divergence.py`.

## R4-2: test-file predicate

`is_conventional_test_file(path)` in `src/parse/changeset.py`: `.java/.kt/.groovy` under `src/test/` or stem `*Test`, `*Tests`, `Test*`, `*IT`; `.py` named `test_*.py`/`*_test.py` or under a `tests/` or `test/` directory; anything else False. It is the primary test-only co-change variant; `is_test_filename()` is kept as the sensitivity row. **Ground-truth (instance, file) pairs accepted: conventional 1,522/1,527 (99.67%); old predicate 1,527/1,527 (100.00%).** So the conventional predicate can cap that variant's recall at 99.67% of what is recoverable.
**Ruling I made, say if wrong:** `src/test/resources/x.json` is **not** a test file, because the Java rule applies to Java/Kotlin/Groovy sources; a resource under `src/test/` is not something that can be bound to a test id. If you meant "everything under `src/test/`", it is one line. Unit tests (`tests/test_test_file_predicates.py`, 25) use real paths including `latest.py`, `contest.py`, `Latest.java`, `src/test/resources/x.json`, `FooIT.java`.

## R4-3: failure classes

`analysis/failure_class.py`: `TIMEOUT` is its own class between environment and code. The timeout rule is `\bTimeoutError\b|\bTimeout(Exception|Expired)\b|\bConditionTimeout(Exception)?\b|\bSocketTimeout(Exception)?\b|\b(Read|Connect)Timeout\b|(?<![\w-])timeout(?![\w-])|(?<![\w-])timed?[ -]?out(?![\w-])|(?<![\w-])deadline exceeded(?![\w-])`: exception names are whole words; the generic words may not be glued to a word character **or a hyphen**. `sockettimeout` moved from connection-error to timeout. Order: leading assertion → environment-strict → timeout → code → unknown.

**A mistake of mine, caught and fixed before the snapshot:** my first version used plain `\btimeout\b`. That excludes `PARTIAL_TIMEOUT` but not the hyphenated path `...\output\json\emit-partial-timeout` in the same real message (`PARTIAL_TIMEOUT result must still be emitted ... ==> expected: <true> but was: <false>`), and I wrote in a draft of this report that those messages were not timeouts without checking. They were still classified `timeout`. Fix: the hyphen lookarounds above; the verbatim message is now a test case and classifies code-level (`expected-vs-actual`; the leading-assertion rule does not fire because the path pushes `==> expected` beyond its 120-character reach). Effect on the corpus, measured against the previous patterns over every distinct strict-label message: 89 messages move environment(timeout rule) → timeout (the class split itself); **2 messages (the two `PARTIAL_TIMEOUT` ones, 2 labels) move to code-level**; nothing else changes. Old 203 environment labels = environment-strict 89 + timeout 112 + 2 now code-level.

`paper/generated/infra_failures.md` summary (strict labels, 4,168; no label changed):
- code-level 729/4,168 (17.49%) (leading-assertion 607, expected-vs-actual 122); **environment-strict 89/4,168 (2.14%)** (cuda-gpu-unavailable 66, connection-error 22, missing-service 1); **timeout 112/4,168 (2.69%)**; unknown 3,238/4,168 (77.69%) = no message recorded 2,231 (53.53%) + message matched no pattern 1,007 (24.16%).
- Instances: >= 1 environment-strict label 39/762 (5.12%); all labels environment-strict 37/762 (4.86%); >= 1 timeout label 80/762 (10.50%); all labels environment-strict or timeout 84/762 (11.02%); >= 1 code-level 268/762 (35.17%).
- By language: Python environment-strict 67/313 (21.41%), timeout 64/313 (20.45%), code-level 72/313 (23.00%); Java environment-strict 22/3,855 (0.57%), timeout 48/3,855 (1.25%), code-level 657/3,855 (17.04%).
- RQ1 sensitivity, k=10 (all strict n=533 → environment-strict removed n=506 → environment-strict + timeout removed n=478), mean P/R/J: co-change all .017/.082/.015 → .011/.068/.010 → .012/.073/.011; co-change conventional-test .063/.090/.043 → .036/.077/.028 → .039/.082/.030; changeset .036/.250/.034 → .037/.257/.035 → .038/.267/.036; historical .186/.509/.178 → .187/.494/.179 → .192/.495/.184. Ordering unchanged. (k=5 and k=20 are in the md.)
- The demo still ranks code-level first: rank is code-level, unknown, timeout, environment, and the printed rule now says so (`preference code-level > unknown > timeout > environment`; it was stale in my first `make demo`). Final `make demo`: candidates code-level 65/228, unknown 101/228, timeout 0/228, environment 62/228; selected instance is code-level (`leading-assertion`). The 228 are the rows that already pass gates 1-4; none has a timeout message (112 strict timeout labels exist overall).

## R4-4: attrition funnel (`analysis/attrition_funnel.py`, rewritten; `paper/generated/attrition_funnel.md`)

No hard-coded numbers, no fallbacks (a missing input raises). Three funnels, because a funnel is only monotone while its unit does not change (runs outnumber PRs outnumber repos). Each stage is the intersection of its predicate with the previous stage, with an assertion. The frame stages come from `data/frame/attrition_stage.csv` and `frame_v1.csv`, as c042ea8 computed them.

| funnel | stages (count; n/d of previous) |
|---|---|
| repos | SEART export 3,671 → CI-live 2,646 (2,646/3,671, 72.08%) → test-intent 2,333 (88.17%) → sampled 300 (12.86%) → swept 76 (25.33%) → with a failed run 69 (90.79%) → with a strict instance 37 (53.62%) |
| PRs | discovered 12,986 → with a failed run 4,005 (4,005/12,986, 30.84%) → with a strict instance 419 (10.46%) |
| runs | discovered 165,349 → failed 12,581 (7.61%) → failed-job log on disk 6,586 (52.35%) → parsed head test failure 1,774 (26.94%) → resolved base 1,348 (75.99%) → known base failure set 897 (66.54%) → >= 1 strict label 762 (84.95%) |

All 76 swept repos are in the 300-repo sample and all 762 strict runs sit inside the nested chain, so nesting lost nothing at the last stage. Old → new: the old md's `logs not expired 15,259 / logs captured 14,104` (108.19%), the hard-coded `+394` and the `13,710` fallback are gone; the log-level stages (captured, not expired, parsed, with test output) are **omitted** with a one-line note (their unit is logs and they do not nest into runs). Graph-build and binding stages are omitted with a note (no local artefact records a per-run graph outcome that nests with runs; binding is in `binding.md`).

**4,648 vs 4,649, cause (verified by re-parsing the 452 base logs):** one base run, `32039276446` (`Stirling-Tools/Stirling-PDF`, head run `32042225074`), made the parser return records, but every identifier failed `normalize_test_id`. `parse_base_logs.py` set `base_run_yielded_identifiers[b] = True` as soon as the parser returned anything, so it counted that head run (4,245 exact_green + 404 = 4,649); `base_outcomes.parquet`, which the funnel reads, holds only normalised ids (4,245 + 403 = 4,648). `parse_base_logs.py` now sets the flag after normalisation: it prints **4,648** (old 4,649) and "base runs yielding zero identifiers" **1,106 of 1,236** (old 1,105); `base_outcomes.parquet` is unchanged. The funnel md prints the 4,245 / 403 / 4,648 split as n/d.

## R4-5: corpus_delta.md

`capture_stdout.py` takes `--note TEXT` (placed under the header line). `corpus_delta.md` now begins: "The evidence-only and invariant-6 scenarios below are counterfactuals, not the committed corpus." Tests for the note and the CLI flag.

## R4-6: RQ1 by change size

`rq1.md` has a "Change size (k = 10)" section with all five methods' mean P/R/J, micro P/R as n/d and median size per stratum (1, 2-5, 6-20, >20 changed files). n per stratum: 43 + 128 + 192 + 170 = 533. The k=10 table is below.

## R4-7: tracking

`.gitignore`: `paper/generated/*` with `!paper/generated/*.md` and `!paper/generated/*.pdf` (a directory ignore cannot be negated per file). `tests/test_gitignore_generated.py` uses `git check-ignore`.

## Final rq1.md table at k = 10 (n = 533 of 734 with ground truth of 762 strict; mean P / R / J)

| slice | n | co-change all | co-change conventional test files | co-change "test" in path (sensitivity) | changeset | historical frequency |
|---|---|---|---|---|---|---|
| overall | 533 | .017/.082/.015 | .063/.090/.043 | .055/.090/.037 | .036/.250/.034 | .186/.509/.178 |
| Java | 439 | .009/.067/.008 | .032/.075/.026 | .023/.075/.018 | .036/.278/.035 | .198/.488/.190 |
| Python | 94 | .052/.151/.047 | .208/.164/.127 | .207/.164/.126 | .039/.122/.028 | .131/.604/.122 |
| 1 changed file | 43 | .009/.023/.004 | .032/.053/.019 | .030/.053/.017 | .000/.000/.000 | .091/.423/.083 |
| 2-5 files | 128 | .036/.083/.034 | .077/.091/.065 | .064/.091/.053 | .071/.169/.063 | .114/.430/.104 |
| 6-20 files | 192 | .016/.115/.014 | .082/.120/.049 | .079/.120/.046 | .041/.334/.040 | .128/.531/.126 |
| >20 files | 170 | .005/.058/.005 | .038/.066/.027 | .029/.066/.020 | .014/.280/.014 | .329/.564/.317 |

Micro P/R as n/d, medians and the k = 5 / 20 tables are in `paper/generated/rq1.md`. The changeset baseline is 0/157 on single-file PRs by construction (the one changed file is not a test file). Historical frequency has the highest mean P, R and J in every stratum (R .423 / .430 / .531 / .564 against the changeset baseline's .000 / .169 / .334 / .280); co-change is below both baselines in every stratum.

## Verification

Order of events: seven commits → suite → `make tables` → `make demo` → inspection found the `PARTIAL_TIMEOUT` mistake and a stale demo string (see R4-3) → both fixed and folded into the item-3 commit, and a load-time fix folded into the item-1 commit, by `commit --fixup` + `rebase --autosquash` on the **unpushed** local commits (so the shas differ from any earlier draft) → everything below re-run on the final HEAD `ef096551b42590ff545ae1b6a64e59873d5e1201` → snapshot recreated at that sha.

- Full suite, nothing deselected (`--extra graph --extra dashboard --extra figures`), on the final HEAD: **780 passed, 1 skipped in 472 s** (711 → 780, +69 tests).
- `make tables` (PATs unset): **rc 0, 7 m 50 s**. `logs/requests.jsonl` 335,543 → 335,543 lines (0 gained). (My first run took 9 m 52 s, 8 s under the tool limit; `load_data()` built the changeset lookup and the two baseline frames with `iterrows`/row-wise `apply`; vectorising them cut `rq1_divergence.py` from ~55 s to ~35 s and its output is byte-identical apart from the sha line, checked by diff.)
- `make demo`: **rc 0, 22.7 s**; selected instance code-level (`leading-assertion`).
- Snapshot headers: every `paper/generated/*.md` in the snapshot carries `at git ef096551b42590ff545ae1b6a64e59873d5e1201`, the HEAD the files were generated at (grep over every file before committing; the snapshot is the immediately following commit). The two PDFs have no header and are byte-stable.

## Things that need a decision or that look wrong

1. **Three files are NOT in the snapshot and are still untracked:** `annotation_census.md`, `corpus_stats.md`, `expiry_cliff.md`. They carry no git-sha header and two of them embed wall-clock time (`corpus_stats.md` and `expiry_cliff.md` have an "As of" timestamp; `annotation_census.md` prints its own runtime), so they change on every `make tables` and cannot satisfy "header sha equals the generating commit". Fixing them means changing three older scripts; your call.
2. **One-sided co-change lookup** (R4-1). Reported, not changed.
3. `make tables` is now 7 m 50 s, but three scripts (rq1, leakage, infra) each re-read every repo's git log through `load_data()`; loading it once would save roughly another minute and a half. Not done (scope).
4. Two local commits were rewritten with `fixup` + `rebase --autosquash` because I found problems after committing (R4-3, Verification). Nothing had been pushed, so no published history changed. Say if you would rather have separate fix commits.
5. The historical baseline orders by run START; completion time is not in `instances_raw` (R4-1a).
6. The binding map (`test_id` → file) comes from the pinned clone tree and is applied to every instance regardless of date; it is a mapping, not outcome evidence, so it is not part of the audit, but it is a source of temporal looseness.

## Local commit list (Round 4; NOT pushed; `main` is 8 commits ahead of `origin/main` at f79ace1)

| sha | message |
|---|---|
| 7296716 | fix: mine RQ1 co-change per instance from trailing history, count baseline failures once, add leakage audit |
| 066d14a | feat: add is_conventional_test_file and use it for the RQ1 test-only co-change variant |
| 0b787b5 | feat: split timeout out of environment failures into its own class |
| 3dbbebb | fix: compute every attrition funnel stage from local data and reconcile the base failure set count |
| 251b97c | paper: state that the corpus_delta scenarios are counterfactuals |
| 810c372 | feat: add RQ1 results by change size |
| ef09655 | fix: track paper/generated markdown and pdf files |
| d8b9ca7 | data: snapshot paper/generated at ef09655 |

Working tree: clean except untracked files: this report and the three files in item 1. Identity checked before the first Round 4 commit: `DeepanshuOP` / `99538840+DeepanshuOP@users.noreply.github.com`; no trailers. Nothing pushed in Round 4.

STOP.


# ROUND 5 REPORT

Code commit `b51bd7a`; snapshot `c4bc574`; tag `paper-numbers-v1` (annotated object `62880987131654958c110a046b638c9c8fa5c976` -> `c4bc574b4b7c05b1b4f218fb8eacc82919ae4862`). PATs unset for every run; `.env` never printed (only `BR_PSEUDONYM_KEY`'s line was read, into the process environment).

## Part 1: Round 4 pushed

`git push origin main` (no force): `f79ace1..d8b9ca7`. After the fetch, `main` = `origin/main` = `d8b9ca7a957393fb3bf7355b1fe6ed98fa281d19`.

## R5-1 Symmetric co-change lookup

`RepoHistory.partners()` now defaults to `both_directions=True`. In `rq1_divergence.py` mode `trailing` is symmetric; the old reach is kept only as the labelled sensitivity mode `trailing_oneside` (used by leakage-audit stages 2-3). The audit's staged table now has stages 0-4 (4 = symmetric, strict baseline, current).

Tests: `test_symmetric_partner_counts_and_top_k_match_the_hand_computed_table` builds a real git repo in `tmp_path` (9 commits, fixed committer dates, days 1-7 inside the window, a commit AT the cutoff on day 10 and one after it on day 20). Expected partners, support, confidence and top-2 are written by hand in the docstring and asserts (b: a, c, d each 2/6; c: b 2/3; a: b 1.0; d: b 2/3; one-sided: b -> c, d only, c and d -> nothing), including that a cutoff one second later makes the day-10 commit visible (c 3/7). Plus `test_trailing_mode_reads_partners_in_both_directions_and_oneside_does_not` at RQ1 level. 20 tests in the two files pass.

RQ1 old (Round 4, pushed) -> new, overall, mean P / R / J:

| k | method | n | mean P | mean R | mean J |
|---|---|---|---|---|---|
| 5 | co-change, all partner files | 532 → 575 | 0.018 → 0.012 | 0.066 → 0.038 | 0.016 → 0.011 |
| 5 | co-change, restricted to conventional test files | 532 → 575 | 0.061 → 0.054 | 0.073 → 0.069 | 0.041 → 0.037 |
| 5 | co-change, restricted to files with "test" in th | 532 → 575 | 0.054 → 0.046 | 0.071 → 0.061 | 0.035 → 0.030 |
| 5 | changeset baseline | 532 → 575 | 0.037 → 0.039 | 0.251 → 0.245 | 0.034 → 0.037 |
| 5 | historical-frequency baseline | 532 → 575 | 0.200 → 0.201 | 0.417 → 0.423 | 0.186 → 0.188 |
| 10 | co-change, all partner files | 533 → 576 | 0.017 → 0.011 | 0.082 → 0.051 | 0.015 → 0.010 |
| 10 | co-change, restricted to conventional test files | 533 → 576 | 0.063 → 0.054 | 0.090 → 0.087 | 0.043 → 0.038 |
| 10 | co-change, restricted to files with "test" in th | 533 → 576 | 0.055 → 0.048 | 0.090 → 0.087 | 0.037 → 0.033 |
| 10 | changeset baseline | 533 → 576 | 0.036 → 0.039 | 0.250 → 0.245 | 0.034 → 0.037 |
| 10 | historical-frequency baseline | 533 → 576 | 0.186 → 0.185 | 0.509 → 0.517 | 0.178 → 0.178 |
| 20 | co-change, all partner files | 533 → 576 | 0.016 → 0.011 | 0.089 → 0.063 | 0.014 → 0.010 |
| 20 | co-change, restricted to conventional test files | 533 → 576 | 0.063 → 0.054 | 0.091 → 0.089 | 0.043 → 0.038 |
| 20 | co-change, restricted to files with "test" in th | 533 → 576 | 0.055 → 0.048 | 0.091 → 0.089 | 0.037 → 0.033 |
| 20 | changeset baseline | 533 → 576 | 0.036 → 0.039 | 0.250 → 0.245 | 0.034 → 0.037 |
| 20 | historical-frequency baseline | 533 → 576 | 0.177 → 0.177 | 0.568 → 0.575 | 0.170 → 0.170 |

**Why the non-co-change rows moved.** Every method is scored on the SAME instances, those where the all-partners co-change proxy fires. The symmetric lookup makes it fire on more instances (k=10: 533 -> 576 of 734; silent instances 169/734 (23.02%) -> 142/734 (19.35%)), so the shared population grew by 43 instances and every other method is averaged over a different set. No other method's code or inputs changed. Co-change fell (k=10 all-partners P .017 -> .011, R .082 -> .051). I did not separate how much of that is the larger candidate sets and how much is the 43 newly scored instances; that split was not measured. Micro figures and per-language / per-stratum tables are in `rq1.md`.

Applicability: changed files with a partner at support >= 2: 4,777/15,604 (30.61%) -> 5,593/15,604 (35.84%); at support >= 3: 2,945/15,604 (18.87%) -> 3,528/15,604 (22.61%).

## R5-2 Predicate

`is_conventional_test_file` unchanged. Resources are not test files (ruling confirmed).

## R5-3 Older paper scripts

`annotation_census.py`, `corpus_stats.py`, `expiry_cliff.py` now write through `paper_md.header` (script + git sha), no wall-clock in the file; wall-clock goes to stdout (`[stdout only] ...`). Each was run twice: output byte-identical. They are in the snapshot, all headers = `b51bd7a`.

Three behavioural consequences that change figures, since each had a wall-clock input:
- `expiry_cliff`: ages are measured against the latest `fetched_at` in `data/raw` (2026-08-29 22:03:22 UTC) instead of "now". Recoverable failed-run logs 4,952/13,422 (36.9%) -> 8,964/13,422 (66.8%); expired 8,470 (63.1%) -> 4,458 (33.2%). The old figures were true on 2026-10-07; the new ones are true at capture. Wording changed from "TODAY" to "AT THE LAST CAPTURE" (`b98a812`). Anyone who wants the figure for today must pass an `as_of` explicitly.
- `corpus_stats`: criterion 1 (72 h uninterrupted) now reports the recorded harvest span from cursor.db, 511.35 h (21d 7h 21m), instead of the live daemon's uptime; still MET. The daemon pid/uptime print to stdout only. The span is NOT proof of uninterrupted running.
- `annotation_census`: runtime removed from the file.

## R5-4 D-52

Appended to `docs/DECISIONS.md` (commit `c75b0b9`). The Context quotes the leakage audit (640/713 (89.76%) instances had a mined commit dated in [run_started_at, as_of] touching a changed file; 713/713 windows ended after the run started), the triple counting (224,758 evidence rows for 78,399 labels; strict once-each 72,809/72,809), the one-sided lookup, and the old -> new k=10 figures. Note: D-51 does not exist in `DECISIONS.md`; I used D-52 as instructed.

## R5-5 Release build (local, nothing uploaded)

Rebuilt `release/v0.1` with `BR_PSEUDONYM_KEY` from `.env`. The directory was replaced (build removes it first); the old withdrawn bundle, including its `WITHDRAWN.md`, was copied to the session scratchpad first. Contents: instances 165,349 rows; outcomes 12,766; cochange 175,204; failure_messages 3,490; CANARY.txt; CHECKSUMS.sha256 (`sha256sum -c`: 5/5 OK).

| release blocker | result |
|---|---|
| secret scan (`analysis/secret_scan.py`) | 4 files, BLOCKER 0, REVIEW 5 (same classes as D-45: Apple asset filenames, Java package fragments) |
| canary | in `CANARY.txt`: yes; in any other bundle file (byte search): none; key bytes in any bundle file: none |
| checksum manifest | written, 5/5 verify |
| HMAC round-trip, distinct authors | 1,791/1,791 (100.00%) recompute to the released pseudonym; rows 165,349/165,349 (100.00%) (joined on repo, run_id, head_sha); distinct pseudonyms 1,791/1,791 (no collisions); every released value 16-hex; raw logins surviving in `author_login`: 0/1,791 |
| byte-level substring grep of the 1,791 raw logins | 12 hits (7 logins of <= 4 chars, 5 longer), same as the datasheet |

Note: the first row-by-row comparison I ran gave 125,846/165,349 because the DuckDB copy reorders rows; that was my positional join, not a release defect. The key-joined comparison above is the real one.

Datasheet check against `paper/generated/` (and the release output):
- Mismatch fixed: same-SHA flip rate was `62 (0.54%)`; now `62/11,557 (0.54%)` (flakiness.md, labelling_run.md).
- Sources updated to cite the generated tables for the label rows, run-level rows, `no_base` (baseline row only; other `no_base` rates in corpus_delta.md are counterfactual) and Gate 1; added Gate 1 secondary and both Gate 1.5 figures (all n/d).
- Matched without change: 165,349 / 12,766 / 175,204 / 3,490 rows; 4,384 / 4,214 / 4,168 labels; 762; 2,466; 12,581; 5,520/12,581 (43.88%); 77/300; 71 Java + 6 Python; 175,038; 667,398; 13,710; 13,422; 12,072; 20,451 parsed rows and 5,985 test_ids (read from `parsed_outcomes.parquet`); the harvest dates and 21d 7h 21m; 59,143 top-repo runs; binding 5,643 / 3,820 / 1,823; 1,791 authors; scan 4 files / 0 / 5; 12 substring hits.
- Not checked against a generated file (no generated source): the parser-defect counts (60 rows, 21 identifiers), the earlier D-47 history table, and the 33-identifier D-49 count. They are historical statements quoted from earlier decisions.

## R5-6 Final run

Commits (all DeepanshuOP / `99538840+DeepanshuOP@users.noreply.github.com`, no trailers; identity checked before the first):

| sha | message |
|---|---|
| e4939f1 | fix: read RQ1 co-change partners in both directions |
| 1da3e3d | fix: write annotation_census, corpus_stats and expiry_cliff through paper_md with no wall-clock in the file |
| c75b0b9 | paper: record D-52 RQ1 method corrections |
| b98a812 | fix: label expiry_cliff figures as of the last capture, not today |
| b51bd7a | paper: reconcile datasheet figures with paper/generated |
| c4bc574 | data: snapshot paper/generated at b51bd7a |

(`b98a812` is an extra commit beyond the four you listed, for the wording change in R5-3.) The release/ directory is not tracked.

- Full suite, nothing deselected (`--extra graph --extra dashboard --extra figures`): **782 passed, 1 skipped in 489 s** (780 -> 782, +2).
- `make tables`: **rc 0, 7 m 43 s** on the final code commit. `logs/requests.jsonl` 335,543 -> 335,543 (0 gained). (An earlier run in this session took 9 m 52 s, 8 s under the 10-minute tool limit; the machine's speed varies. If it exceeds 10 minutes, this tool backgrounds it.)
- `make demo`: **rc 0, 27 s**; selected instance: failure class code-level, rule `leading-assertion`.
- Header check: every `paper/generated/*.md` carries `at git b51bd7a720523a4d5bf5001307acb7bb26d52644`, the code commit. The snapshot is the next commit.
- Push: `d8b9ca7..c4bc574 main -> main`, tag `paper-numbers-v1` pushed. `main` = `origin/main` = `c4bc574b4b7c05b1b4f218fb8eacc82919ae4862`; `git ls-remote --tags origin` shows `paper-numbers-v1` -> `62880987131654958c110a046b638c9c8fa5c976`.

Environment-failure audit on the 4,168 strict labels: environment-strict 89/4,168 (2.14%); timeout 112/4,168 (2.69%); code-level 729/4,168 (17.49%); unknown 3,238/4,168 (77.69%).

## Final rq1.md tables

### k = 10, overall

| method | n | mean P | mean R | mean J | micro P (hits/predicted) | micro R (hits/actual) | median size |
|---|---|---|---|---|---|---|---|
| co-change, all partner files | 576 | 0.011 | 0.051 | 0.010 | 61/13,109 (0.47%) | 61/1,316 (4.64%) | 14 |
| co-change, restricted to conventional test files | 576 | 0.054 | 0.087 | 0.038 | 101/4,674 (2.16%) | 101/1,316 (7.67%) | 4 |
| co-change, restricted to files with "test" in the path (sensitivity) | 576 | 0.048 | 0.087 | 0.033 | 101/5,737 (1.76%) | 101/1,316 (7.67%) | 6 |
| changeset baseline | 576 | 0.039 | 0.245 | 0.037 | 224/14,001 (1.60%) | 224/1,316 (17.02%) | 9 |
| historical-frequency baseline | 576 | 0.185 | 0.517 | 0.178 | 519/4,099 (12.66%) | 519/1,316 (39.44%) | 10 |


### k = 10, per language

### Java (n=462)

| method | n | mean P | mean R | mean J | micro P (hits/predicted) | micro R (hits/actual) | median size |
|---|---|---|---|---|---|---|---|
| co-change, all partner files | 462 | 0.005 | 0.034 | 0.005 | 33/11,572 (0.29%) | 33/1,063 (3.10%) | 15 |
| co-change, restricted to conventional test files | 462 | 0.026 | 0.071 | 0.021 | 65/4,176 (1.56%) | 65/1,063 (6.11%) | 4 |
| co-change, restricted to files with "test" in the path (sensitivity) | 462 | 0.019 | 0.071 | 0.015 | 65/5,156 (1.26%) | 65/1,063 (6.11%) | 7 |
| changeset baseline | 462 | 0.040 | 0.279 | 0.039 | 201/13,145 (1.53%) | 201/1,063 (18.91%) | 13 |
| historical-frequency baseline | 462 | 0.199 | 0.496 | 0.192 | 380/3,040 (12.50%) | 380/1,063 (35.75%) | 8 |

### Python (n=114)

| method | n | mean P | mean R | mean J | micro P (hits/predicted) | micro R (hits/actual) | median size |
|---|---|---|---|---|---|---|---|
| co-change, all partner files | 114 | 0.034 | 0.123 | 0.032 | 28/1,537 (1.82%) | 28/253 (11.07%) | 11 |
| co-change, restricted to conventional test files | 114 | 0.171 | 0.151 | 0.108 | 36/498 (7.23%) | 36/253 (14.23%) | 3.5 |
| co-change, restricted to files with "test" in the path (sensitivity) | 114 | 0.166 | 0.151 | 0.106 | 36/581 (6.20%) | 36/253 (14.23%) | 4.5 |
| changeset baseline | 114 | 0.037 | 0.105 | 0.026 | 23/856 (2.69%) | 23/253 (9.09%) | 5 |
| historical-frequency baseline | 114 | 0.128 | 0.601 | 0.120 | 139/1,059 (13.13%) | 139/253 (54.94%) | 10 |


### k = 10, per change-size stratum

## Change size (k = 10)

Strata by number of changed files in the PR; the strata partition the 576 scored instances.

### 1 changed files (n=51)

| method | n | mean P | mean R | mean J | micro P (hits/predicted) | micro R (hits/actual) | median size |
|---|---|---|---|---|---|---|---|
| co-change, all partner files | 51 | 0.007 | 0.020 | 0.004 | 3/319 (0.94%) | 3/167 (1.80%) | 6 |
| co-change, restricted to conventional test files | 51 | 0.025 | 0.044 | 0.014 | 5/128 (3.91%) | 5/167 (2.99%) | 1 |
| co-change, restricted to files with "test" in the path (sensitivity) | 51 | 0.024 | 0.044 | 0.013 | 5/154 (3.25%) | 5/167 (2.99%) | 1 |
| changeset baseline | 51 | 0.020 | 0.020 | 0.020 | 1/51 (1.96%) | 1/167 (0.60%) | 1 |
| historical-frequency baseline | 51 | 0.086 | 0.435 | 0.080 | 32/385 (8.31%) | 32/167 (19.16%) | 10 |

### 2-5 changed files (n=148)

| method | n | mean P | mean R | mean J | micro P (hits/predicted) | micro R (hits/actual) | median size |
|---|---|---|---|---|---|---|---|
| co-change, all partner files | 148 | 0.029 | 0.071 | 0.028 | 17/1,434 (1.19%) | 17/323 (5.26%) | 10 |
| co-change, restricted to conventional test files | 148 | 0.066 | 0.090 | 0.060 | 24/613 (3.92%) | 24/323 (7.43%) | 2 |
| co-change, restricted to files with "test" in the path (sensitivity) | 148 | 0.053 | 0.090 | 0.048 | 24/773 (3.10%) | 24/323 (7.43%) | 3 |
| changeset baseline | 148 | 0.074 | 0.176 | 0.066 | 32/480 (6.67%) | 32/323 (9.91%) | 3 |
| historical-frequency baseline | 148 | 0.125 | 0.448 | 0.116 | 109/1,190 (9.16%) | 109/323 (33.75%) | 10 |

### 6-20 changed files (n=207)

| method | n | mean P | mean R | mean J | micro P (hits/predicted) | micro R (hits/actual) | median size |
|---|---|---|---|---|---|---|---|
| co-change, all partner files | 207 | 0.007 | 0.047 | 0.006 | 19/3,738 (0.51%) | 19/368 (5.16%) | 15 |
| co-change, restricted to conventional test files | 207 | 0.073 | 0.112 | 0.043 | 38/1,343 (2.83%) | 38/368 (10.33%) | 3 |
| co-change, restricted to files with "test" in the path (sensitivity) | 207 | 0.071 | 0.112 | 0.041 | 38/1,687 (2.25%) | 38/368 (10.33%) | 7 |
| changeset baseline | 207 | 0.039 | 0.320 | 0.038 | 84/2,332 (3.60%) | 84/368 (22.83%) | 11 |
| historical-frequency baseline | 207 | 0.134 | 0.548 | 0.131 | 159/1,474 (10.79%) | 159/368 (43.21%) | 10 |

### >20 changed files (n=170)

| method | n | mean P | mean R | mean J | micro P (hits/predicted) | micro R (hits/actual) | median size |
|---|---|---|---|---|---|---|---|
| co-change, all partner files | 170 | 0.002 | 0.049 | 0.002 | 22/7,618 (0.29%) | 22/458 (4.80%) | 37.5 |
| co-change, restricted to conventional test files | 170 | 0.030 | 0.066 | 0.021 | 34/2,590 (1.31%) | 34/458 (7.42%) | 10 |
| co-change, restricted to files with "test" in the path (sensitivity) | 170 | 0.024 | 0.066 | 0.016 | 34/3,123 (1.09%) | 34/458 (7.42%) | 13 |
| changeset baseline | 170 | 0.014 | 0.280 | 0.014 | 107/11,138 (0.96%) | 107/458 (23.36%) | 67 |
| historical-frequency baseline | 170 | 0.329 | 0.564 | 0.317 | 219/1,050 (20.86%) | 219/458 (47.82%) | 6.5 |

## Things that need a decision or look wrong

1. At k=10 overall (n=576) historical frequency is highest on mean P, R and J (.185 / .517 / .178). All-partners co-change is below the changeset baseline on all three (.011 / .051 / .010 vs .039 / .245 / .037). Conventional-test co-change is slightly above the changeset baseline on P and J (.054 vs .039; .038 vs .037) and far below on R (.087 vs .245). The ordering is unchanged from Round 4; the symmetric lookup lowered the co-change rows. These are macro means over instances; micro figures are in `rq1.md`.
2. The historical baseline orders runs by START time; completion time is not in `instances_raw`, so a run that was still executing when the instance began cannot be excluded (stated in `leakage_audit.md`).
3. `expiry_cliff.md` now states figures as of the last capture (see R5-3); the paper must not call 8,964 "recoverable today".
4. `make tables` takes 7-10 minutes and three scripts re-read every repo's git log. A single shared load would save about 1.5 minutes. Not done (scope).
5. The `trailing_oneside` mode exists only for the audit's staged table. If you would rather not keep dead-weight methods, say so and I will remove it with the stage rows.
6. PDFs differ from the previous snapshot because the figures use the new RQ1 data.

STOP.
