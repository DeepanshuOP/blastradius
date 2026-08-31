# Reproducing BR-Bench Data & Paper Numbers

This document provides the exact command sequence from a fresh clone to generate every paper number, in order.

## 1. Environment Setup
```bash
git clone <repo-url>
cd blastradius
uv sync
# Ensure .env is populated with 3 GitHub PATs
```
*Expected runtime: 2-3 minutes*

## 2. Daemon Harvest (Stages 1–4)
To capture PRs, check-runs, workflow conclusions, and job logs from candidate repositories:
```bash
uv run python src/harvest/daemon.py --stage all --max-logs 1000
```
*Expected runtime: Varies significantly (hours to days depending on network and GitHub API quota).*

## 3. Data Parsing and Base Run Resolution (Phase 006A)
To resolve base runs and parse test outcomes:
```bash
uv run python analysis/fetch_base_logs.py
uv run python analysis/parse_base_logs.py
uv run python analysis/resolve_bases.py
```
*Expected runtime: ~15-30 minutes*

## 4. Fault-Revealing Split & Attrition (Phase 007A/B)
Extract the strict/permissive splits and calculate the attrition funnel:
```bash
uv run python src/label/fault_revealing.py
uv run python analysis/attrition_funnel.py
```
*Expected runtime: ~2 minutes*

## 5. Paper Tables & Numbers
Generate all numbers and tables required for the paper (including the final strict split size, metrics, and funnel steps):
```bash
make tables
```
*Expected runtime: ~25 seconds (cold), ~20 seconds (warm)*

## 6. Fixture Scorer Evaluation
Evaluate the parser suite precision/recall on the held-out dataset:
```bash
uv run python analysis/holdout_eval.py
```
*Expected runtime: ~10 seconds*
