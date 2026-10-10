"""Regenerate the tiny E1 fixture tables (synthetic, hand-computed in tests/test_e1_features.py).

Run: uv run python tests/fixtures/e1/make_fixture.py
T is the prediction time of instance (o/a, 100): 2026-06-01T00:00:00Z. Offsets are days before T.
"""
import datetime as dt
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
T = dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc)


def iso(days_before: float) -> str:
    return (T - dt.timedelta(days=days_before)).strftime("%Y-%m-%dT%H:%M:%SZ")


def epoch(days_before: float) -> int:
    return int((T - dt.timedelta(days=days_before)).timestamp())


# runs of repo o/a: (run_id, days_before_T, changed files, labelled test file or None, extra head-only failure)
RUNS_A = [
    (1, 120, ["src/cart.py"], "tests/test_cart.py"),
    (2, 90, ["src/cart.py", "docs/x.md"], "tests/test_cart.py"),   # exactly 90 d: inside the 90-day window
    (3, 60, ["src/cart.py"], "tests/test_cart.py"),
    (4, 10, ["src/other.py"], "tests/test_cart.py"),               # changed file differs: no co-failure
    (5, 0, ["src/cart.py"], "tests/test_cart.py"),                 # exactly T: must NOT count
    (6, -1, ["src/cart.py"], "tests/test_cart.py"),                # after T: must NOT count
    (100, 0, ["src/cart.py"], None),                               # the instance being predicted
]
runs, changed, strict = [], [], []
for rid, d, files, tf in RUNS_A:
    runs.append(dict(repo="o/a", run_id=rid, pr_number=rid, run_started_at=iso(d), head_sha=f"h{rid}"))
    changed += [dict(repo="o/a", pr_number=str(rid), filename=f) for f in files]
    if tf:
        strict.append(dict(repo="o/a", run_id=rid, test_id=f"tests.test_cart::case{rid}", run_started_at=iso(d),
                           resolved_path=tf, split="strict"))
# a failure in ANOTHER repo with the same file name must never leak across repos
runs.append(dict(repo="o/c", run_id=300, pr_number=300, run_started_at=iso(5), head_sha="h300"))
changed.append(dict(repo="o/c", pr_number="300", filename="src/cart.py"))
strict.append(dict(repo="o/c", run_id=300, test_id="tests.test_cart::c", run_started_at=iso(5),
                   resolved_path="tests/test_cart.py", split="strict"))
# a cold-start repo: no history at all
runs.append(dict(repo="o/b", run_id=200, pr_number=200, run_started_at=iso(0), head_sha="h200"))
changed.append(dict(repo="o/b", pr_number="200", filename="lib/core.py"))
strict = pd.DataFrame(strict)
heads = strict.assign(split="all")
extra = pd.DataFrame([  # head-only failures (inherited / flaky): 40 d and 5 d before T
    dict(repo="o/a", run_id=7, test_id="tests.test_cart::inh", run_started_at=iso(40), resolved_path="tests/test_cart.py", split="all"),
    dict(repo="o/a", run_id=8, test_id="tests.test_cart::flk", run_started_at=iso(5), resolved_path="tests/test_cart.py", split="all"),
])
runs += [dict(repo="o/a", run_id=7, pr_number=7, run_started_at=iso(40), head_sha="h7"),
         dict(repo="o/a", run_id=8, pr_number=8, run_started_at=iso(5), head_sha="h8")]

# commits (committer time) of o/a: src/cart.py <-> tests/test_cart.py three times (support 3);
# src/cart.py <-> tests/test_other.py once (support 1, below threshold); src/cart.py alone once.
# Two more commits that contain the pair at exactly T and after T must be invisible.
commits = [
    ("c1", 200, ["src/cart.py", "tests/test_cart.py"]),
    ("c2", 150, ["src/cart.py", "tests/test_cart.py"]),
    ("c3", 100, ["src/cart.py", "tests/test_cart.py"]),
    ("c4", 50, ["src/cart.py", "tests/test_other.py"]),
    ("c5", 20, ["src/cart.py"]),
    ("c6", 0, ["src/cart.py", "tests/test_cart.py"]),
    ("c7", -2, ["src/cart.py", "tests/test_cart.py"]),
    ("c8", 400, ["src/cart.py", "tests/test_cart.py"]),   # older than the 365-day window: invisible
]
pd.DataFrame([dict(repo="o/a", sha=s, ts=epoch(d), files="|".join(f)) for s, d, f in commits]).to_parquet(HERE / "commits.parquet", index=False)
strict.to_parquet(HERE / "strict.parquet", index=False)
pd.concat([heads, extra], ignore_index=True).to_parquet(HERE / "head_all.parquet", index=False)
pd.DataFrame(runs).to_parquet(HERE / "runs.parquet", index=False)
pd.DataFrame(changed).to_parquet(HERE / "changed.parquet", index=False)
print("T epoch:", epoch(0))
