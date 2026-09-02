# Reproducing BR-Bench Data & Paper Numbers

This document provides the exact command sequence from a fresh clone to generate every paper number, in order.

> **CRITICAL OPERATIONAL RULE:**
> The harvester daemon is currently **OFF and must stay off**.
> **NEVER** run any step in this document in the background, with `nohup`, `setsid`, `&`, or via background tasks/subagents. All commands must be run interactively in the foreground.

## 0. Prerequisites & Non-Git Data Transfer

The following assets are **not tracked in git** and cannot be regenerated from source due to GitHub Actions' 90-day log retention expiry clock. They **must be physically copied** into the repository root before running analysis or paper reproduction pipelines (see `docs/DATA_TRANSFER.md`):
- `data/raw/` (4.9 GB, irreplaceable raw job logs and workflow responses)
- `data/state/cursor.db` (131 MB, required for point-in-time `--as-of` state reproduction)
- `data/interim/instances_raw.parquet` (and other `data/interim/*.parquet` files, ~33 MB total, required for base resolution, fault labeling, and paper tables)
- `vendor/graphify-br/` (31 MB flat vendored tree, tracked in git)

## 1. Environment Setup
```bash
git clone <repo-url>
cd blastradius
uv sync
# Ensure .env is populated with 3 GitHub PATs (required for live harvest/network steps)
```
*Expected runtime: 2-3 minutes*

## 2. Daemon Harvest (Stages 1–4)
> **Note:** Do NOT run this during standard paper reproduction. The dataset is pinned. If running a new harvest pass:
```bash
uv run --env-file .env python src/harvest/daemon.py --stage all --max-logs 1000
```
*Expected runtime: Varies significantly (hours to days depending on network and GitHub API quota).*

## 3. Data Parsing and Base Run Resolution
*Prerequisites: requires transferred `data/raw/`, `data/state/cursor.db`, and `data/interim/instances_raw.parquet`.*
To resolve base runs and parse test outcomes (note: `resolve_bases.py` must run **before** `fetch_base_logs.py`):
```bash
uv run python analysis/resolve_bases.py
uv run python analysis/fetch_base_logs.py
uv run python analysis/parse_base_logs.py
```
*Expected runtime: ~15-30 minutes*

## 4. Fault-Revealing Split & Attrition
*Prerequisites: requires `data/interim/base_resolution_new.parquet` and `data/interim/instances_raw.parquet`.*
Extract the strict/permissive splits and calculate the attrition funnel:
```bash
uv run python src/label/fault_revealing.py
uv run python analysis/attrition_funnel.py
```
*Expected runtime: ~2 minutes*

## 5. Paper Tables & Numbers
*Prerequisites: requires transferred `data/raw/`, `data/state/cursor.db`, and `data/interim/*.parquet`.*
Generate all numbers and tables required for the paper (including the final strict split size, metrics, and funnel steps):
```bash
make tables
```
*Expected runtime: ~25 seconds (cold), ~20 seconds (warm)*

## 6. Fixture Scorer Evaluation
Run the parser suite regression check against the `tests/fixtures/holdout/` development set (runs on checked-in fixtures; requires no external data). This corpus is **fitted, not held out**: under D-37 it became a development set permanently once parser fixes were diagnosed by inspecting its own failures, and `tests/test_holdout_eval.py` pins the parsers to its identifiers. It therefore yields **no held-out precision figure** — its precision/recall is a development-set fit measurement only. See `docs/phase/027-scorer-provenance.md`.
```bash
uv run python analysis/holdout_eval.py
```
*Expected runtime: ~10 seconds*
