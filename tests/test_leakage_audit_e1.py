"""The E1 section of the leakage audit passes the real feature table and catches an injected future row."""

import pandas as pd

from analysis.leakage_audit import E1_FEATURES, audit_e1
from tests.conftest import requires_data

NEEDS = ("data/interim/outcomes.parquet", "data/interim/binding.parquet", "data/interim/changesets.parquet",
         "data/interim/cochange.parquet", "data/interim/instances_raw.parquet", "docs/CLONE_PINS.json",
         "data/clones", str(E1_FEATURES))


@requires_data(*NEEDS)
def test_real_features_have_no_violations_and_inflated_ones_are_caught() -> None:
    from analysis.rq1_divergence import load_data

    data = load_data()
    feats = pd.read_parquet(E1_FEATURES)
    clean = audit_e1(data, feats, n_cells=60, seed=1)
    assert clean["violations"] == 0
    # a feature that also counted one row at or after the cutoff is exactly what the audit must flag
    leaked = feats.copy()
    for c in ("hist_fail_count", "hist_fail_30d", "hist_fail_90d", "hist_head_fail_count", "cofail_max",
              "cofail_sum", "cochg_max_support", "cochg_sum_support"):
        leaked[c] = leaked[c] + 1
    caught = audit_e1(data, leaked, n_cells=60, seed=1)
    assert caught["violations"] > 0
