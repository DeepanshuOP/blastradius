# Phase 032: BlastRadius 2.0 progress log

Resume rule: if the session restarts, read this file first and continue from the first unfinished phase.
Branch: `upgrade-2.0` (from `main` at 1198e1d). Operator: DeepanshuOP.

## Phase 0: Preflight (2026-10-10) — done

**Findings that differ from the prompt (reported, none blocking):**
- `docs/HANDOVER.md` does not exist. Present: `docs/HANDOVER-020.md`, `docs/HANDOVER-PRISHA.md`, `docs/HANDOFF.md`. Read HANDOFF.md tail and CURRENT-STATE instead.
- `AGENTS.md` says: never write under `data/`, never edit `docs/SCHEMAS.md`, no external URLs. The 2.0 task explicitly requires derived tables under `data/processed/`, a NEW section at the end of SCHEMAS.md (frozen sections untouched), and a Groq call. The explicit operator instruction wins; frozen sections and `data/raw`, `data/interim` stay untouched. No harvester daemon is running (`ps` shows none; corpus is frozen at 2026-08-29).
- `make figures` is currently a stub (`echo "not implemented"`); fig1/fig2 are written by `rq1_divergence.py`. Phase 4 implements the target.
- `.gitignore` ignores `*.parquet` and `data/*`; `models/` and `eval/` are not ignored (good). `paper/generated/*` only tracks `.md` and `.pdf`.
- matplotlib, lightgbm, scikit-learn, scipy are not installed in the venv yet (numpy 2.4.6, requests 2.34.2 are).

**Row counts (duckdb, `data/interim/`):**
| table | rows |
|---|---|
| outcomes.parquet | 12,766 (run_id, test_id, split) |
| parsed_outcomes.parquet | 20,451 |
| base_outcomes.parquet | 2,990 |
| instances_raw.parquet | 165,349 |
| base_resolution_new.parquet | 12,581 |
| binding.parquet | 5,985 |
| changesets.parquet | 688,273 |

**RQ1 inputs (`rq1_divergence.load_data()` / `ground_truth()`):**
- instances with ground truth: **734** (matches HARD STOP 1 expectation); strict instances 762
- run_started_at min / max among them: 2026-05-24T17:46:32Z / 2026-08-22T07:57:30Z
- repos: 36; repos with >= 20 instances: 12
- top 10: unicode-org/cldr 107, apache/beam 73, fla-org/flash-linear-attention 64, dask/distributed 60, apache/hugegraph 53, apache/zeppelin 48, apache/tika 41, floci-io/floci 31, mcreator/mcreator 24, apache/dolphinscheduler 23

**E2 class counts (distinct (run_id, test_id), 897 runs):** all 4,384 / relaxed 4,214 / strict 4,168 -> mine 4,168, inherited 170, flaky 46.

**Clone coverage:** every ground-truth test file of all 734 instances is in its pinned clone's tree: 1,527/1,527 pairs; all 36 repos have a pin and a clone.

**Tooling:** node v22.23.2. Groq call (openai/gpt-oss-120b, "Reply with the word ok"): HTTP 200, model `openai/gpt-oss-120b`, usage prompt 76 / completion 16 / total 92 tokens. Rate-limit headers: `x-ratelimit-limit-requests: 1000` (per day), `x-ratelimit-limit-tokens: 8000` (per minute), remaining 999 / 7908. Groq does not expose a daily token cap in headers; the 200,000/day default in the plan is an assumption, enforced client-side.

**Baseline `make test`:** `821 passed, 3 skipped in 674.67s` (824 total). Matches the last recorded baseline.

**Branch:** `upgrade-2.0` created from `main` (1198e1d). Identity verified: DeepanshuOP / 99538840+DeepanshuOP@users.noreply.github.com.

## Phase 1: decisions, dependencies, schema section — done (commit 1d830b5)
- D-56..D-59 appended to `docs/DECISIONS.md`; ROADMAP §32 note; CLAUDE.md 2.0 block.
- `ml` extra pinned: lightgbm==4.7.0, scikit-learn==1.9.1, scipy==1.17.1 (`uv lock`, `uv sync --extra graph --extra ml --extra figures`).
- `docs/SCHEMAS.md`: new trailing section "Derived tables v0.3"; frozen sections untouched. Types are lowercase so the v0.2 section parser (`analysis/release_schema.py`) does not pick them up; `tests/test_release_v02.py` still 12 passed.
- `models/` and `eval/` are not gitignored; `data/` stays ignored.

## Phase 2: shared feature layer — done
- Files: `src/features/{context,test_features,candidates}.py`, `analysis/build_e1_features.py`, `tests/test_e1_features.py`, `tests/fixtures/e1/` (+ `make_fixture.py`).
- Tests: `uv run pytest -q tests/test_e1_features.py` -> 9 passed. Full `make test`: 831 passed, 2 skipped, 0 failed (baseline 821 / 3).
- `uv run python -m analysis.build_e1_features` (stdout): 734 instances (49 without a changeset); split 440 / 146 / 148; 608,903 rows; candidates per instance min/median/max 35 / 304.5 / 5,439; positives per instance 1 / 1 / 104; ground-truth files among candidates 1,527/1,527 (100.00%); all 36 repos from the pinned clone; 3 positives are non-conventional and unseen before (candidate only because they are labels; no feature exposes candidate provenance).
- Decisions made: failure *events* are one per (run, test_id) so `hist_fail_count` equals RQ1's historical baseline count; `prox_min_dir_dist` is tree distance (up + down segments); stems shorter than 3 characters are ignored in `prox_name_contains_stem`; module = path prefix before the first src/tests/test segment.
- `graph_` family: not implemented (optional; see Phase 4 note).

## Phase 3: metrics and baselines — done
- Files: `src/eval/metrics.py`, `src/eval/baselines.py`, `tests/test_e1_metrics.py`, `tests/test_e1_baselines.py`.
- `uv run pytest -q tests/test_e1_metrics.py tests/test_e1_baselines.py` -> 11 passed.
- HARD STOP 1 reproduction (k=10, 576 instances, 1,316 labels), asserted by `test_reproduces_published_rq1_baselines`: co-change 61, changed files 224, failure history 519 hits: all equal `paper/generated/rq1.md`. Finding: the history set only reproduces under RQ1's own tie rule (pandas `value_counts` order). With a path-ascending tie-break the same baseline scores 524 hits. The E1 ranking B4 uses the path tie-break (spec: ties by path); both are reported in `rq2_predictor.md`.

## Deviations and base-branch fix (recorded 2026-10-10)

- **Missing `docs/HANDOVER.md`.** It exists on `origin/main` (a7e154b); this laptop's `main` was behind. Fixed: `git fetch`, `git merge-base --is-ancestor origin/main upgrade-2.0` returned 1, `git rebase origin/main` succeeded with no conflicts (8 commits replayed; no conflict in `paper/generated/`, frozen SCHEMAS sections or `src/parse/`). Local `main` fast-forwarded afterwards.
- **`AGENTS.md` conflict.** It forbids writing under `data/`, editing `SCHEMAS.md`, and fetching external URLs; the task requires all three. Resolved by operator decision; recorded as an explicit exceptions block at the end of `AGENTS.md`. No harvester daemon was running.
- **more-itertools -> click.** more-itertools' full suite takes 79 s (limit 60 s); `pallets/click` (8 s) is the fourth repo.
- **`demo-web/public/data/agents.json`.** The uncommitted change on this laptop was only a re-run of the three original scenarios (new shas, `generated_at`, `python3` vs `python` build string, timings); no new scenarios or keys. Saved as `../agents_json_premod.patch` before regenerating.
- **Groq limits.** The `x-ratelimit-*` headers report per-minute limits only (8,000 tokens/min, 1,000 requests/day); the daily-token ceiling (`BR_GROQ_TPD`, default 200,000) is enforced client-side from `eval/llm_cache/usage.jsonl`.

### Contradictions between `docs/HANDOVER.md` and the 2.0 build

- Handover section 3.1 and D-55 say the agents are the only place an LLM may appear and "never feed numbers". D-58 adds a cached Groq call in `src/agents/repair.py`; E3 numbers live in `paper/generated/rq4_repair.md`, which is NOT part of `make tables` and not in the MSR paper.
- "Five agents", "8 tabs", "make agents-demo: three scenarios", "824 tests (821 passed, 3 skipped)": now seven agents (Triage, Repair added), nine tabs (Intelligence), four scenarios, 895 passed / 2 skipped before the Step 3 additions.
- "`make tables` ~8 min": now about 45 min, because it includes E1 (about 14 min, the LightGBM tuning, ablation and learning curve) and E2.
- "`make figures`: paper figures" was a stub; it now writes fig3-fig5 (E1). fig1/fig2 are still written by `rq1_divergence.py`.
- Section 15 P3.11 lists "RQ2/RQ3 and a learned predictor" as optional strengthening. It is built (E1/E2) and came out negative/small-sample; per D-56 neither goes into the MSR paper.
- The MSR paper draft, report and deck describe five agents and no predictor; they were not touched.

## Phases 4-10: summary (2026-10-10)

- **Tests.** `make test`: 897 passed, 2 skipped (baseline 821 passed, 3 skipped; 76 new tests). Re-run after the rebase onto `origin/main`: 895 passed, 2 skipped (before the Step 3 and fix commits).
- **E1** (`rq2_predictor.md`): ours Recall@10 0.525 vs B7 0.522, Holm-adjusted p = 0.2656, delta +0.030 negligible: Gate 3 NOT MET. Test split 148 instances, all Java. Determinism: two independent runs of `analysis/rq2_predictor.py` produce identical generated files apart from the git-sha stamp.
- **E2** (`rq3_triage.md`): small-sample (18 not-mine pairs in the test split); confusion matrices for the test split and pooled leave-one-repo-out are in the file; class totals check holds (170 + 46 = 216 = 4,384 - 4,168).
- **E3** (`rq4_repair.md`): 70 tasks; retrieval R2 69/70 vs R1 46/70; plausible fix R1/R2/R3 10/13/14 (gpt-oss-120b) and 4/10/13 (gpt-oss-20b), n = 20; paired R2 vs R1 McNemar p = 0.5078 and 0.1094. `make repair-eval` replays both caches with zero new network requests (usage ledger and `logs/requests.jsonl` unchanged).
- **Two defects found and fixed during E3** (both recorded as commits): (1) a Groq 400 `tool_use_failed` reply (the model tried a tool call) aborted a run, it is now cached as an empty, failed attempt; (2) retry feedback contained memory addresses, so cached prompts did not replay. Addresses and the working-tree path are now masked, which changed a handful of retry prompts; those were re-requested (3 new 120b calls), everything else was a cache hit.
- **HARD STOP 5** not triggered: against `main`, every pre-existing generated file differs only in its "Generated by ... at git" stamp; `leakage_audit.md` gains the E1 section.
- **Not done:** the `graph_` feature family (optional); `make tables` was run before the final Step 3 commit and not re-run after the docs commits (no generated file changed since).
- **Interpretation** of E1/E2 results in prose is left to the operator, as requested; `docs/RESULTS_2.md` etc. state numbers only.
