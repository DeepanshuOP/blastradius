"""The E1 ranker trains deterministically, round-trips through disk and explains itself additively.

Uses a small synthetic feature table with a planted signal (not a mock of corpus
data: it exercises the training code, and the corpus itself is covered by the
`@requires_data` run of analysis/rq2_predictor.py).
"""

import numpy as np
import pandas as pd
import pytest

from src.features.test_features import FEATURE_COLS
from src.models import e1_ranker as R


def make_table(n_inst: int = 36, n_cand: int = 12, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_inst):
        split = "train" if i < 24 else "val" if i < 30 else "test"
        pos = int(rng.integers(0, n_cand))
        for j in range(n_cand):
            r = {c: 0.0 for c in FEATURE_COLS}
            r["hist_fail_count"] = float(rng.integers(0, 3) + (4 if j == pos else 0))
            r["prox_max_jaccard"] = float(rng.random() * 0.3 + (0.5 if j == pos else 0))
            rows.append({"repo": "o/r", "run_id": 1000 + i, "ts": i, "split": split, "label": int(j == pos),
                         "test_file": f"tests/test_{j:02d}.py", **r})
    return pd.DataFrame(rows)


def test_training_is_deterministic() -> None:
    df = make_table()
    a = R.predict(R.train(df, None, seed=3, params={"min_data_in_leaf": 2}), df)
    b = R.predict(R.train(df, None, seed=3, params={"min_data_in_leaf": 2}), df)
    assert np.array_equal(a, b)


def test_model_ranks_planted_positive_first_on_test_split() -> None:
    df = make_table()
    booster = R.train(df, None, seed=0, params={"min_data_in_leaf": 2})
    t = df[df["split"] == "test"].reset_index(drop=True)
    s = R.predict(booster, t)
    top = t.assign(s=s).sort_values(["run_id", "s"], ascending=[True, False]).groupby("run_id").head(1)
    assert top["label"].mean() > 0.8


def test_save_load_round_trip(tmp_path) -> None:
    df = make_table()
    booster = R.train(df, None, seed=0, params={"min_data_in_leaf": 2})
    R.save(booster, tmp_path / "m.txt", {"seed": 0, "n_train": 24})
    loaded, manifest = R.load(tmp_path / "m.txt")
    assert manifest["seed"] == 0 and manifest["feature_list"] == FEATURE_COLS
    assert np.allclose(R.predict(booster, df), R.predict(loaded, df, FEATURE_COLS))


def test_shap_contributions_sum_to_raw_score() -> None:
    df = make_table()
    booster = R.train(df, None, seed=0, params={"min_data_in_leaf": 2})
    contrib = R.explain(booster, df)
    assert contrib.shape == (len(df), len(FEATURE_COLS) + 1)
    assert np.allclose(contrib.sum(axis=1), R.predict(booster, df), atol=1e-6)


def test_grid_is_16_points_in_fixed_order() -> None:
    g = R.grid_params()
    assert len(g) == 16 and g == R.grid_params()
    assert len({tuple(sorted(p.items())) for p in g}) == 16


def test_groups_follow_instance_boundaries() -> None:
    df = make_table(n_inst=3, n_cand=4)
    assert R.groups_of(df).tolist() == [4, 4, 4]
