# Data Dependencies for `make tables`

What each `make tables` target needs, and what a fresh clone can actually do.

**The table below is measured, not asserted.** It comes from cloning
`https://github.com/DeepanshuOP/blastradius.git` into `/tmp/br-verify`, running
`uv sync`, and running each target, at commit `39839fd`. Re-verify it the same
way rather than trusting this page.

**Tracked data files:** `data/frame/` contains 9 tracked files in git (including `frame_v1.csv`, `ATTRITION.json`, etc.), and `data/interim/` contains 3 tracked PIN files (`COCHANGE_PIN.json`, `CORPUS_PIN.json`, `INSTANCES_PIN.json`). All raw logs and generated parquet datasets under `data/` are untracked.

## `data/raw` cannot be regenerated. Ever.

**GitHub Actions job logs expire 90 days after the run.** Much of this corpus is
already past that at source, so re-running the harvester today would not
reproduce `data/raw` — it would produce a strictly smaller, different corpus.
The snapshot (2.73 GB apparent content for transfer sizing / 4.9 GiB on disk for destination free space; supersedes earlier unqualified 4.9 GB and 4.6 GB figures) is irreplaceable and must be transferred, not rebuilt. The
same is true of `data/state/cursor.db` (131 MB), which `--as-of` reproduction
needs.

Phase 017 sharpened one distinction that matters here: **job *metadata* does not
expire, job *logs* do.** An expired base run can still be enumerated
(`/actions/runs/{id}/jobs` returns 200 indefinitely) but never read. That is why
`base_jobs_total` and `base_jobs_retrieved` are columns in
`data/interim/exact_green_verification.parquet` — the gap between them is the
permanently unverifiable share, and no future work closes it.

| Path | Size | In git | Regenerable | Action |
|---|---:|---|---|---|
| `data/raw/` | 2.73 GB apparent / 4.9 GiB on disk | No | **NO — 90-day expiry** | Transfer: 2.73 GB transfer sizing, 4.9 GiB destination free space (supersedes 4.9 GB / 4.6 GB) |
| `data/state/cursor.db` | 131 MB | No | No | Transfer; `--as-of` needs it |
| `data/interim/*.parquet` | 33 MB | No (3 PIN files tracked) | Yes, slowly, from `data/raw` | Transfer anyway (supersedes ~31 MB) |
| `vendor/graphify-br/` | 34 MB | **Yes** (flat tree) | Yes (from upstream `safishamsi/graphify`) | Nothing (vendored in repo) |
| `data/clones/` | 1.7 GB | No | Yes (`git clone --filter=blob:none`) | Re-clone |
| `data/frame/` | 18 MB | **Partial (9 tracked files)** | Frozen under T0.8 | Nothing (tracked files present in git) |
| `tests/fixtures/` | small | **Yes** | — | Nothing |

## Measured: what runs on a fresh clone

**6 of 14 targets pass with no data at all.** The other 8 fail on a named
missing file — the first one each needs is given.

| # | Target | Fresh clone | First missing input |
|---:|---|---|---|
| 1 | `analysis/secret_scan.py` | **PASS** | — (no `release/`, exits 0: nothing to scan) |
| 2 | `analysis/resolve_bases.py` (explicit `make resolve-bases`, no longer in `tables`) | FAIL | `data/interim/base_resolution_new.parquet` |
| 3 | `analysis/fetch_base_logs.py` | FAIL | `data/interim/base_resolution_new.parquet` (also needs 3 PATs) |
| 4 | `analysis/parse_base_logs.py` | FAIL | `data/interim/base_resolution_new.parquet` (also needs `data/raw`) |
| 5 | `src/label/fault_revealing.py` | FAIL | `data/interim/base_resolution_new.parquet` |
| 6 | `analysis/fixture_score.py` | **PASS** | — (scores checked-in fixtures) |
| 7 | `analysis/holdout_eval.py` | **PASS** | — (scores checked-in fixtures) |
| 8 | `analysis/binding_report.py` | FAIL | `data/interim/parsed_outcomes.parquet` |
| 9 | `analysis/attrition_funnel.py` | FAIL | `data/interim/instances_raw.parquet` |
| 10 | `analysis/rq1_divergence.py` | FAIL | `data/interim/outcomes.parquet` |
| 11 | `analysis/expiry_cliff.py` | **PASS** | — |
| 12 | `analysis/annotation_census.py` | **PASS** | — |
| 13 | `analysis/corpus_stats.py` | **PASS** | — |
| 14 | `analysis/verify_exact_green.py --report-only` | FAIL | `data/interim/exact_green_verification.parquet` |
| 15 | `analysis/corpus_delta.py` | FAIL | `data/interim/base_resolution_new.parquet` |

`make tables` therefore **stops at target 2** on a clean clone. It is a data
problem, not a code or dependency problem: `uv sync` succeeds and `make test`
reaches 380 passed / 14 failed / 4 errors, where every failure is a missing
`data/` input.

`analysis/rq1_divergence.py` no longer requires `matplotlib`. It imports it
lazily inside `write_figures()` and prints every number without it, warning that
the two PDFs were skipped. Numbers are the paper; figures are optional.

## Not wired into `make tables`, and why

`analysis/verify_exact_green.py`'s **sweep** needs 3 PATs and runs for tens of
minutes, so it is an explicit step:

```bash
uv run --env-file .env python analysis/verify_exact_green.py
```

It is resumable — re-running it continues from `--out` — and `--time-budget-s`
bounds a single slice. `make tables` runs only its `--report-only` mode, which
regenerates every printed number from the committed parquet with no network.

## Virtual environment

Always `uv run`, and `uv run --env-file .env` for anything issuing HTTP. Plain
`uv run` fails with "no GitHub PAT found in environment": `TokenPool.from_env()`
reads `os.environ` and nothing else loads `.env` into it.
