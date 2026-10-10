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
