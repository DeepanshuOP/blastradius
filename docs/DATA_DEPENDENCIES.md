# Data Dependencies for `make tables`

This document details the data inputs required for each target inside `make tables` and how to obtain them. Note that none of the `data/interim` or `data/raw` directories are tracked in git due to size constraints.

## Important Warning: `data/raw` Expiry
GitHub Actions logs strictly expire after 90 days. The data in `data/raw` **CANNOT** be fully regenerated from scratch by running the harvester today if the underlying CI logs have expired. Any new developer must receive a securely transferred snapshot of `data/raw` and `data/state/cursor.db` from the primary operator.

## Target Breakdown

1. `analysis/resolve_bases.py`
   - **Data Required**: `data/interim/base_resolution.parquet`, `data/interim/instances_raw.parquet`, `data/raw` (via `RawStore` and `cursor.db`).
   - **In Git**: No.
   - **How to obtain**: Requires copying the `data/` snapshot from the operator.

2. `analysis/parse_base_logs.py`
   - **Data Required**: `data/interim/base_resolution_new.parquet`, `data/raw`.
   - **In Git**: No.
   - **How to obtain**: Run `resolve_bases.py` for interim files, and copy `data/raw` from the operator.

3. `src/label/fault_revealing.py`
   - **Data Required**: `data/interim/base_resolution_new.parquet`, `data/interim/instances_raw.parquet`, `data/interim/parsed_outcomes.parquet`, `data/interim/base_outcomes.parquet`.
   - **In Git**: No.
   - **How to obtain**: Supplied via the interim outputs from previous steps and the initial dataset bundle.

4. `analysis/fixture_score.py`
   - **Data Required**: `data/interim/parsed_outcomes.parquet`.
   - **In Git**: No.
   - **How to obtain**: Computed during earlier data extraction, requires `data/interim` snapshot.

5. `analysis/holdout_eval.py`
   - **Data Required**: `tests/fixtures/holdout_v3/` (or similar), models' prediction outputs.
   - **In Git**: Yes (fixtures), No (some interim outputs).
   - **How to obtain**: Run the model evaluations or load the repository fixtures.

6. `analysis/binding_report.py`, `analysis/attrition_funnel.py`, `analysis/rq1_divergence.py`, `analysis/expiry_cliff.py`, `analysis/annotation_census.py`, `analysis/corpus_stats.py`
   - **Data Required**: `data/interim/*.parquet` (binding, changesets, cochange, outcomes, etc.), `data/frame/frame_v1.csv`.
   - **In Git**: No (except some framing data if tracked).
   - **How to obtain**: All of these aggregate upon the pipeline's interim data. A complete `data/interim` snapshot is required.

## Virtual Environment Requirement
The script targets currently import `pandas` and `pyarrow`. However, these are **not** listed in the `pyproject.toml` dependencies. A fresh checkout running `uv sync` will not install them and `make tables` will immediately crash with a `ModuleNotFoundError`. Until `pyproject.toml` is updated with operator permission, developers must manually `uv pip install pandas pyarrow` into their `.venv` before running `make tables`.
