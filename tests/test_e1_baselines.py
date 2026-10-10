"""B0-B5 scoring on tiny frames, and the HARD STOP 1 reproduction of RQ1's published baselines."""

import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.eval import baselines as b
from tests.conftest import requires_data


def frame() -> pd.DataFrame:
    return pd.DataFrame({
        "test_file": ["tests/test_b.py", "tests/test_a.py", "tests/test_c.py"],
        "prox_in_change": [0, 1, 0], "cochg_max_support": [4, 0, 4], "hist_fail_count": [1, 0, 7],
    })


def test_simple_baselines_and_tie_break() -> None:
    g = frame()
    files = g["test_file"].tolist()
    assert b.rank(files, b.score_b0(g)) == ["tests/test_a.py", "tests/test_b.py", "tests/test_c.py"]
    assert b.rank(files, b.score_b2(g))[0] == "tests/test_a.py"
    assert b.rank(files, b.score_b3(g)) == ["tests/test_b.py", "tests/test_c.py", "tests/test_a.py"]  # tie by path
    assert b.rank(files, b.score_b4(g)) == ["tests/test_c.py", "tests/test_b.py", "tests/test_a.py"]


def test_random_baseline_is_seeded() -> None:
    g = frame()
    assert np.array_equal(b.score_b1(g, 3, 9), b.score_b1(g, 3, 9))
    assert not np.array_equal(b.score_b1(g, 3, 9), b.score_b1(g, 4, 9))
    assert not np.array_equal(b.score_b1(g, 3, 9), b.score_b1(g, 3, 10))  # instances are independent


def test_b5_prefers_path_overlap() -> None:
    g = pd.DataFrame({"test_file": ["tests/test_cart.py", "tests/test_user.py", "tests/test_misc.py"]})
    s = b.score_b5(g, ["src/cart.py"])
    # every path shares the token `py` with the query, so the floor is > 0; `cart` lifts the first
    assert s[0] > s[1] > 0 and s[1] == s[2]


@requires_data("data/interim/outcomes.parquet", "data/interim/binding.parquet", "data/interim/changesets.parquet",
               "data/interim/cochange.parquet", "data/interim/instances_raw.parquet", "docs/CLONE_PINS.json",
               "data/clones", "paper/generated/rq1.md")
def test_reproduces_published_rq1_baselines() -> None:
    """HARD STOP 1: B2, B3, B4 on the RQ1 subset (k = 10) equal paper/generated/rq1.md."""
    from analysis.build_e1_features import build_contexts
    from analysis.rq1_divergence import ground_truth, load_data
    from src.features.context import BrBenchHistory

    data = load_data()
    gt = ground_truth(data)
    ctxs = {c.instance_key: (c, started) for c, started in build_contexts(data, gt)}
    got = b.reproduce_rq1(data, ctxs, BrBenchHistory(data), gt, k=10)

    text = Path("paper/generated/rq1.md").read_text()
    k10 = text.split("## k = 10", 1)[1].split("### Overall", 1)[1]

    def hits(label: str) -> tuple[int, int]:
        m = re.search(re.escape(label) + r" \| (\d+) \|.*?\| ([\d,]+)/[\d,]+ \([\d.]+%\) \| ([\d,]+)/([\d,]+) \(",
                      k10)
        assert m, label
        return int(m.group(3).replace(",", "")), int(m.group(4).replace(",", ""))

    co, actual = hits("co-change, all partner files")
    ch, _ = hits("changeset baseline")
    hi, _ = hits("historical-frequency baseline")
    n = int(re.search(r"all partner files \| (\d+) \|", k10).group(1))
    assert {k: got[k] for k in ("n", "actual", "co_hits", "changed_hits", "hist_hits")} == {
        "n": n, "actual": actual, "co_hits": co, "changed_hits": ch, "hist_hits": hi}
    # the path tie-break is a different arbitrary rule, so it may differ by a handful of hits; it must stay close
    assert abs(got["hist_hits_path_ties"] - hi) <= 10
