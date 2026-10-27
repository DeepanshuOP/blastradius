# BlastRadius · BR-Bench

**Which tests did a code change actually break?** BlastRadius mines GitHub Actions runs and links each pull-request change to the individual tests that *really failed because of it*, not the files usually edited together (co-change) and not every test that can reach the change (static reachability). The released dataset is **BR-Bench**.

[![Dataset DOI](https://img.shields.io/badge/dataset-10.5281%2Fzenodo.23688064-blue)](https://doi.org/10.5281/zenodo.23688064)
[![Code DOI](https://img.shields.io/badge/code-10.5281%2Fzenodo.23250690-blue)](https://doi.org/10.5281/zenodo.23250690)
![License: MIT (code), CC BY 4.0 (data)](https://img.shields.io/badge/license-MIT%20%2F%20CC%20BY%204.0-green)

Team: Deepanshu, Sanskriti Singh and Prisha Vadhavkar; guide Dr. Yoga Raja C A; VIT BITE497J Project I.

## What it does, in one sentence

BlastRadius tells a team, for each pull request, which tests are most at risk, runs them first, says which failures are the change's own, and proposes a fix only when the whole test suite passes with it; it comments, and never merges or pushes.

## Three ways to use it

| | | |
|---|---|---|
| **GitHub Action** | a comment on every pull request, with inline suggestions for validated patches | copy [`integrations/github-actions/blastradius-bot.yml`](integrations/github-actions/blastradius-bot.yml), follow [`BOT_SETUP.md`](integrations/github-actions/BOT_SETUP.md) |
| **Jenkins** | Jenkins stays the executor; BlastRadius decides order, triage and fix | [`integrations/jenkins/Jenkinsfile`](integrations/jenkins/Jenkinsfile) (an example, not deployed on a Jenkins server) |
| **Command line** | `impact`, `ask`, `bot`, `pipeline` | `uv run --extra graph --extra ml --extra rag python -m src.agents --help` |

A live example, the bot's comment on a pull request in a sandbox repository: <https://github.com/DeepanshuOP/itsdangerous/pull/1>.

The project page replays everything offline. `make demo-data` (once, after any change to the generated files), then `make demo-web`, opens it at <http://localhost:3000>: Overview, Data, Results, Compare (papers and commercial tools, same-data results, cost, time, safety), Try it (analyze a repository, ask, agent scenarios, run replay) and Use it. `make demo-check` verifies it offline before a presentation; `docs/DEMO_SCRIPT.md` is a 10-minute walkthrough with panel questions.

## Headline numbers and their status

| result | value | status |
|---|---|---|
| BR-Bench strict split | 762 instances, 4,168 labels (Gate 1 of 5,000 not met) | released, DOI above |
| Test-to-file binding | 94.29% combined; 63.83% at full confidence | both always shown; full confidence below its 70% gate |
| RQ1, k = 10, n = 576 | failure history 39.44%, co-change 4.64% | descriptive |
| E1 ranker, Recall@10 (n = 148, Java only) | 0.525 against 0.522 for the best baseline | Gate 3 not met (Holm-adjusted p = 0.3823) |
| E2 triage | small sample: 18 not-mine pairs in the test split | exploratory trade-off, not a working triager |
| E3 repair, standard variant (n = 70) | gpt-oss-120b 50 vs 33 plausible fixes, one-sided McNemar p = 0.0007569; gpt-oss-20b 41 vs 19 | pre-registered (docs/phase/033), confirmatory |
| E3 hard variant, third model | 29 and 17 of 70; 25 of 70 | interim, run continuing |
| E3 arm R4 | none | built, not run |

## BlastRadius 2.0 (course deliverable, D-56)

On top of the dataset, BlastRadius 2.0 is a change-aware CI assistant in four stages: **predict** which test files a change will break (E1), **run** them first, **triage** each failure as the change's own, inherited or flaky (E2), and **repair** the ones that are the change's own, accepting a patch only if the full suite passes (E3). Each stage is an experiment scored on BR-Bench (E3 on a seeded-bug benchmark) and each may come out negative; results, including the ones that did not work, are in [`docs/RESULTS_2.md`](docs/RESULTS_2.md) and architecture in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). The MSR 2027 paper stays a dataset paper.

Results so far (all regenerate from `paper/generated/`; details and caveats in `docs/RESULTS_2.md`): the E1 ranker reaches Recall@10 = 0.525 on a Java-only chronological test split, statistically indistinguishable from the best baseline (0.522; Gate 3 not met). E2 is a small-sample trade-off (18 not-mine pairs in the test split), not a working triager. E3 is confirmatory on the standard variant (pre-registered, docs/phase/033; n = 70): change-aware retrieval places the seeded function in the model's context for 69/70 tasks against 46/70 log-only (63/70 on the harder variant), and R2 beats R1 on plausible fixes (gpt-oss-120b: 50 vs 33 of 70, one-sided exact McNemar p = 0.0007569; gpt-oss-20b: 41 vs 19). The hard variant (29 and 17 of 70) and the third model (25 of 70) are interim, run continuing; arm R4 is built, not run.

## Why

Change impact analysis is usually scored against co-change, and regression test selection against static reachability. Neither label records a test failure. Industrial predictive test selection (Meta, Google) uses the right label, but on private data. BR-Bench puts the right label on public data:

> a test is **fault-revealing** for a change if it failed at the head commit, did not fail in the resolved base run, and did not flip on the same commit:
> `T_reveal = T_head_fail − T_base_fail − T_flaky`

## Headline results

Every number below regenerates offline with `make tables` (sources in `paper/generated/`).

| | |
|---|---|
| Corpus | 165,349 workflow runs from 76 swept repositories (Java, Python); 12,581 failed runs |
| Benchmark (strict split) | **762 instances, 4,168 fault-revealing labels, 2,466 distinct tests** |
| Test-to-file binding | 94.29% combined (5,643/5,985); 63.83% at full confidence (3,820/5,985) |
| Flakiness | 62/11,557 same-commit flips (0.54%), removed |
| RQ1, k = 10, n = 576 | failure history recalls **39.44%** of failing tests (519/1,316); co-change **4.64%** (61/1,316); the changed files themselves 17.02% |

Honest negatives, stated up front: Gate 1 (5,000 strict labels) is **not met** (4,168); full-confidence binding is below its 70% gate; parser precision is measured on development sets only (blind holdout v5 unscored, D-53); labels are observational (no re-execution).

## How it works

```
SEART frame ─▶ Harvester ─▶ raw store ─▶ parsers (Gradle · Maven · pytest) ─▶ canonical test_id
   ─▶ labelling engine (base-run resolution · T_reveal · flake filter) ─▶ binding (pinned clones)
   ─▶ make tables ─▶ BR-Bench release (pseudonymised, secret-scanned, checksummed)
   └─▶ graph layer: commit-pinned code graphs, test nodes bound to test_id, query API
```

An empty base failure set is never read as "the base was green": no base run means no labels (`status = no_base`, 5,520 of 12,581 failed runs). The full design is in `docs/ROADMAP.md`; every design decision is in `docs/DECISIONS.md` (D-01 to D-55).

## Agentic workflow (from user story to deployment)

Five agents in `src/agents/` carry the impact analysis into the everyday life of a change:

| Agent | Input | Output |
|---|---|---|
| Impact Analysis | user story, codebase | impact analysis document: files to change, tests at risk (code-graph reachability, weighted by failure history) |
| Coding | impact analysis, codebase | changed files, pull request |
| PR Reviewer | PR, impact analysis | scope + compile + tests-at-risk checks; merges and returns the commit id |
| Build & Deploy | commit id, branch | build, package, deploy; notification on failure |
| Regression Suite | impact analysis, regression suite | test report with impact recall |

They run fully offline (`make agents-demo`), use a language model when `ANTHROPIC_API_KEY` is set, and open real PRs with `--forge github`. They are a separate demo path (D-55): no agent output reaches the dataset, `make tables` or the paper. See [`src/agents/README.md`](src/agents/README.md).

## Quick start

WSL2 Ubuntu or Linux, Python 3.11, [uv](https://docs.astral.sh/uv/):

```bash
uv sync --extra graph --extra ml --extra figures
make test            # full test suite
make tables          # regenerate every number in paper/generated/ (offline, ~45 min incl. E1/E2; needs data/)
make demo            # terminal walkthrough of one real instance
make agents-demo     # seven agents, four recorded scenarios (offline; scenario 4 replays one cached model reply)
make e1 / make e2    # E1 ranker and baselines / E2 triage (offline, deterministic; both also run inside make tables)
make seeded          # BR-Seeded benchmark (clones 3 repos, needs the network once)
make repair-run MODEL=openai/gpt-oss-120b   # E3 live (Groq free tier, GROQ_API_KEY in .env), caches every reply
                     # models: openai/gpt-oss-120b (primary), openai/gpt-oss-20b, qwen/qwen3.8-27b (exploratory preview model, D-62)
make repair-estimate MODEL=qwen/qwen3.8-27b VARIANT=hard   # E3 dry run: cached vs left, tokens, days (no request)
make repair-eval     # E3 results from the cache, offline
make demo-web        # demo site on http://localhost:3000 (Live run · Results · Analyze a repo · Agents · Corpus · Decisions)
make analyze REPO=https://github.com/pallets/itsdangerous \
  STORY="Add a max_age grace period when validating timestamped signatures"
                     # impact analysis of any public Python/Java repo (shallow clone, offline agent, no LLM)
```

Using the dataset only: download release v0.2 from Zenodo (DOI 10.5281/zenodo.23688064) and read the Parquet tables with DuckDB or pandas. Schema: `docs/SCHEMAS.md` (section "Release schema v0.2"); datasheet: `docs/DATASHEET.md`; reproduction: `docs/REPRODUCE.md`.

## Run the Live Lab

1. Prerequisites: WSL2 Ubuntu or Linux, `uv sync --extra graph --extra ml --extra rag --extra figures`, Node >= 18 and `npm ci` in `demo-web/` once.
2. `make lab` builds the site and prints `Live Lab ready: http://127.0.0.1:3000` when it answers (Ctrl-C stops it).
3. Open that URL and pick a scenario; the recorded runs replay at once.
4. **Present** gives a full-screen walkthrough of the run; **Challenge** lets the audience pick the bug.
5. Offline: every replay, the arena, graph, test-gap and offline live runs; no model call is made.
6. Needs `GROQ_API_KEY` in `.env` (never printed): only the live repair step and the repair arena.

## Repository map

| Path | What |
|---|---|
| `src/harvest/` | rate-limited, resumable GitHub API capture (`get_with_backoff()` is the only GET path) |
| `src/parse/` | log parsers and the `test_id` normaliser |
| `src/label/` | base-run resolution and fault-revealing labels |
| `src/graph/` | commit-pinned code graphs over a stripped Graphify fork (no LLM pass) |
| `src/agents/` | the five-agent workflow |
| `analysis/` | every reported number, the release builder, the validator |
| `demo-web/` | Next.js demo site; static replay plus a localhost-only `/api/analyze` route |
| `paper/` | MSR 2027 Data & Tool Showcase draft and generated tables |

## Citation

See [`CITATION.cff`](CITATION.cff). Dataset: Deepanshu, S. Singh, P. Vadhavkar, Y. R. C A, *BR-Bench* (release v0.2), Zenodo, doi:10.5281/zenodo.23688064.

## Team

Deepanshu (23BIT0264) · Sanskriti Singh (23BIT0256) · Prisha Vadhavkar (23BIT0010) · Guide: Dr. Yoga Raja C A — School of Computer Science Engineering and Information Systems, VIT Vellore. BITE497J Project I, 2026.

Code: MIT. Data: CC BY 4.0. Vendored Graphify: Apache-2.0 with MIT-licensed portions (`vendor/graphify-br/`).
