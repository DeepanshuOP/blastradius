# BlastRadius — Claude Code Operating Instructions

> Read automatically at session start. Derived from `docs/ROADMAP.md` §30.1, §34.1–34.3.
> **If this file and the roadmap disagree, the roadmap wins — and tell Deepanshu so it gets fixed here.**

## Project

BlastRadius — execution-grounded change impact prediction for CI. We mine GitHub Actions runs to build a dataset linking code changes to the individual tests that actually failed, then predict that from a code graph.

**Target:** MSR 2027 Data & Tool Showcase. Abstract 5 Nov 2026, paper 10 Nov 2026.
**Course:** VIT BITE497J Project I. Team: Prisha Vadhavkar (23BIT0010), Sanskriti Singh (23BIT0256), Deepanshu (23BIT0264). Guide: Dr. Yoga Raja C A.

**The contribution is the dataset and the honest measurement, not a novel predictor.** A negative model result is publishable (roadmap §37.1 Gate 3). Do not optimise numbers at the cost of correctness.

## Repository layout

```
src/harvest/          GitHub API capture (raw → data/raw/*.jsonl.gz)
src/parse/            Test-result parsers (→ TestOutcome records)
src/label/            Labelling engine (→ instances/outcomes parquet)
src/graph/            Commit-pinned graph builder over vendor/graphify-br
src/features/         Feature extraction
src/models/           LightGBM + PyG
src/eval/             Baselines, metrics, statistics
analysis/             Every number in the paper regenerates from here
tests/fixtures/       Real checked-in fixtures, never mocks
vendor/graphify-br/   Forked graphify (MIT), LLM pass removed
docs/                 ROADMAP.md, SCHEMAS.md, DECISIONS.md, TASKS.md
```

## Environment

Python 3.11 · uv · **WSL2 Ubuntu, not PowerShell** for anything in this repo · DuckDB + Parquet for storage · pytest for tests · NetworkX for in-process graph traversal.

## Hard rules

1. **One task, one session, one file** (or one tightly-coupled pair). If a request looks like more than that, say so and ask to split it.
2. **Schema first, code second.** If a schema is involved, show the schema and **STOP for approval** before writing implementation code.
3. **Every data-touching function gets a pytest test against a REAL fixture** in `tests/fixtures/` — a checked-in log file with hand-written expected output, never a mock.
4. **Never invent data.** No invented benchmark numbers, paper titles, star counts, API behaviours, or statistics. If you don't know, say you don't know. Every number that reaches the paper must regenerate via `make tables`.
5. **Determinism is a requirement.** Seed everything. Pin every dependency. **No LLM calls anywhere in the reproducible pipeline** (roadmap D-17).
6. **No new dependencies without asking first.**
7. Type hints everywhere. Google-style docstrings.
8. Commit at every green test. Conventional messages: `feat:` `fix:` `data:` `paper:`.
9. **Do not build ahead of the current stage.** Build order: harvester → parsers → labels → graph → features → baselines → model → demo → paper.

## Commit hygiene

- **Commit identity is `DeepanshuOP` with the operator's GitHub noreply email.** Before any commit, verify with `git config user.name && git config user.email`. If either is wrong, **STOP and report** — GitHub attributes by email, and a mismatch drops the commit from the operator's contribution history. Repo-local config only; never touch `--global`.
- **No trailers, ever.** Never append `Co-Authored-By`, `Claude-Session`, or anything else to a commit message. This history carries no trailers. Use the operator's `-m` string verbatim and nothing more.
- **Never `git add -A` or `git add .`.** Always name explicit paths.
- **Never commit without explicit operator authorization** given as its own step.

## Frozen contracts — changing these breaks the project

| Contract | Where | Frozen |
|---|---|---|
| `test_id` canonical format | `src/parse/ids.py`, extends `vendor/graphify-br/graphify/ids.py` | **Week 1 — the join key for the entire project** |
| `instances.parquet` / `outcomes.parquet` | `docs/SCHEMAS.md` | Week 2 |
| `graph_nodes` / `graph_edges` | `docs/SCHEMAS.md` | Week 2 |

The `test_id` contract test must pass on every merge. If a change would alter `test_id` output for any existing input, **stop and flag it** rather than updating the expected values.

## Hard constraints

- **Storage:** 200–500 GB raw logs; prune success-run logs after parsing, keep failure logs. Plus ~60–120 GB repo mirrors, ≤150 GB graph store.
- **Compute:** everything runs on a laptop except the GNN (Colab/Kaggle free tier, checkpoint to Drive) and gold re-execution.
- **Rate limits:** 5,000 req/hr/token, three tokens. All GitHub HTTP goes through `get_with_backoff()` — no exceptions, no direct `requests.get`.
- **Network:** the harvester must survive hostel Wi-Fi. Resumable cursors, aggressive retry, nightly mirror.

## Explicit non-goals — do not build these

Blocking merges on predicted risk · safety guarantees in the RTS sense · TypeScript support · cross-repo blast radius · IDE plugin · hosted service · data-flow/PDG layer · graph database backend · LLM anywhere in the pipeline.

If a task seems to need one of these, **stop and ask** — it is either scope creep or a genuine gap in the roadmap, and Deepanshu decides which.

## Scope discipline

`docs/ROADMAP.md` Part IV is a **specification**, not a work order. It describes fifteen node types and twenty edge types tiered CORE / v1.5 / DEFERRED (§16.2–16.3). **Build only what the current task names.** Never implement a tier because it is documented.
