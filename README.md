# BlastRadius · BR-Bench

**Which tests did a code change actually break?** BlastRadius mines GitHub Actions runs and links each pull-request change to the individual tests that *really failed because of it*, not the files usually edited together (co-change) and not every test that can reach the change (static reachability). The released dataset is **BR-Bench**.

[![Dataset DOI](https://img.shields.io/badge/dataset-10.5281%2Fzenodo.23250262-blue)](https://doi.org/10.5281/zenodo.23250262)
[![Code DOI](https://img.shields.io/badge/code-10.5281%2Fzenodo.23250690-blue)](https://doi.org/10.5281/zenodo.23250690)
![License: MIT (code), CC BY 4.0 (data)](https://img.shields.io/badge/license-MIT%20%2F%20CC%20BY%204.0-green)

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
uv sync --extra graph
make test            # full test suite
make tables          # regenerate every number in paper/generated/ (offline, ~8 min; needs data/)
make demo            # terminal walkthrough of one real instance
make agents-demo     # the five agents, three recorded scenarios
make demo-web        # demo site on http://localhost:3000 (Live run · Results · Analyze a repo · Agents · Corpus · Decisions)
make analyze REPO=https://github.com/pallets/itsdangerous \
  STORY="Add a max_age grace period when validating timestamped signatures"
                     # impact analysis of any public Python/Java repo (shallow clone, offline agent, no LLM)
```

Using the dataset only: download the release from Zenodo and read the Parquet tables with DuckDB or pandas. Schema: `docs/SCHEMAS.md` (section "Release schema v0.2"); datasheet: `docs/DATASHEET.md`; reproduction: `docs/REPRODUCE.md`.

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

See [`CITATION.cff`](CITATION.cff). Dataset: Deepanshu, S. Singh, P. Vadhavkar, Y. R. C A, *BR-Bench* (release v0.1), Zenodo, doi:10.5281/zenodo.23250262.

## Team

Deepanshu (23BIT0264) · Sanskriti Singh (23BIT0256) · Prisha Vadhavkar (23BIT0010) · Guide: Dr. Yoga Raja C A — School of Computer Science Engineering and Information Systems, VIT Vellore. BITE497J Project I, 2026.

Code: MIT. Data: CC BY 4.0. Vendored Graphify: Apache-2.0 with MIT-licensed portions (`vendor/graphify-br/`).
