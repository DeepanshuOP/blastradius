"""E1: LightGBM lambdarank over candidate test files, one query group per instance.

Determinism: `deterministic=True`, `force_row_wise=True`, `num_threads=1` and a
fixed `seed` for every reported run (D-59). SHAP values are LightGBM's own
`pred_contrib=True`, so there is no extra dependency. No LLM, no network.
"""

from __future__ import annotations

import json
import subprocess
from datetime import date
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

from src.features.test_features import FEATURE_COLS

__all__ = ["BASE_PARAMS", "GRID", "grid_params", "train", "predict", "explain", "save", "load", "groups_of"]

BASE_PARAMS = {
    "objective": "lambdarank", "metric": "ndcg", "eval_at": [10], "deterministic": True, "force_row_wise": True,
    "num_threads": 1, "verbosity": -1, "learning_rate": 0.1, "num_leaves": 31, "min_data_in_leaf": 20,
    "feature_fraction": 1.0,
}
GRID = {"num_leaves": [15, 31], "learning_rate": [0.05, 0.1], "min_data_in_leaf": [5, 20],
        "feature_fraction": [0.8, 1.0]}
MAX_ROUNDS = 500
EARLY_STOPPING = 30


def grid_params() -> list[dict]:
    """Every combination of :data:`GRID`, in a fixed order."""
    out = [{}]
    for name in sorted(GRID):
        out = [{**p, name: v} for p in out for v in GRID[name]]
    return out


def groups_of(df: pd.DataFrame) -> np.ndarray:
    """Query-group sizes of `df`, whose rows must be contiguous per instance `(repo, run_id)`."""
    key = df["repo"].astype(str) + "#" + df["run_id"].astype(str)
    changed = key.ne(key.shift()).to_numpy()
    starts = np.flatnonzero(changed)
    return np.diff(np.append(starts, len(df)))


def _dataset(df: pd.DataFrame, cols: list[str]) -> lgb.Dataset:
    return lgb.Dataset(df[cols].to_numpy(dtype=np.float64), label=df["label"].to_numpy(), group=groups_of(df),
                       feature_name=cols, free_raw_data=False)


def train(df: pd.DataFrame, feature_cols: list[str] | None, seed: int, params: dict | None = None,
          fit_splits: tuple[str, ...] = ("train",), valid_split: str | None = "val",
          n_rounds: int | None = None) -> lgb.Booster:
    """Fit a lambdarank model.

    Args:
        df: Feature table (`e1_features.parquet` rows), contiguous per instance.
        feature_cols: Feature columns (default :data:`FEATURE_COLS`).
        seed: Seed for every LightGBM random source.
        params: Overrides of :data:`BASE_PARAMS` (a grid point).
        fit_splits: Splits to fit on.
        valid_split: Split for early stopping on NDCG@10 (patience 30), or None.
        n_rounds: Fixed number of rounds; when given there is no early stopping.

    Returns:
        The booster; `best_iteration` is set when early stopping ran.
    """
    cols = feature_cols or FEATURE_COLS
    p = {**BASE_PARAMS, **(params or {}), "seed": seed, "bagging_seed": seed, "feature_fraction_seed": seed,
         "data_random_seed": seed}
    tr = _dataset(df[df["split"].isin(fit_splits)], cols)
    if n_rounds is not None or valid_split is None:
        return lgb.train(p, tr, num_boost_round=n_rounds or 100)
    va = _dataset(df[df["split"] == valid_split], cols)
    return lgb.train(p, tr, num_boost_round=MAX_ROUNDS, valid_sets=[va], valid_names=["val"],
                     callbacks=[lgb.early_stopping(EARLY_STOPPING, verbose=False)])


def predict(booster: lgb.Booster, df: pd.DataFrame, feature_cols: list[str] | None = None) -> np.ndarray:
    """Raw ranking scores for each row of `df`."""
    cols = feature_cols or booster.feature_name()
    return booster.predict(df[cols].to_numpy(dtype=np.float64), num_iteration=booster.best_iteration or None)


def explain(booster: lgb.Booster, df: pd.DataFrame, feature_cols: list[str] | None = None) -> np.ndarray:
    """Per-feature SHAP contributions, shape `(rows, features + 1)`; the last column is the bias."""
    cols = feature_cols or booster.feature_name()
    return booster.predict(df[cols].to_numpy(dtype=np.float64), pred_contrib=True,
                           num_iteration=booster.best_iteration or None)


def save(booster: lgb.Booster, path: Path, manifest: dict) -> None:
    """Write the text model to `path` and a JSON manifest next to it (`<stem>.json`).

    Args:
        booster: Trained model.
        path: Destination `.txt`.
        manifest: Extra manifest fields (seed, params, instance counts, date range).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    booster.save_model(str(path), num_iteration=booster.best_iteration or None)
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, OSError):
        sha = "unknown"
    meta = {"git_sha": sha, "feature_list": booster.feature_name(), "lightgbm": lgb.__version__, **manifest}
    path.with_suffix(".json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load(path: Path) -> tuple[lgb.Booster, dict]:
    """Load a model and its manifest."""
    return lgb.Booster(model_file=str(path)), json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
