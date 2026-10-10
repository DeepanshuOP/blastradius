"""E2 triage features: is this failing test caused by the change, or not?

Everything here is time-safe: a feature of a failure at time `ts` reads only
failure events with time strictly before `ts`. No LLM, no model score from E1.

The classes (`analysis/rq3_triage.py`) are `mine` (the test fails at head and
passed at base: BR-Bench strict), `inherited` (failing at head, already failing
at base) and `flaky` (relaxed but not strict: the same commit's reruns flip).
"""

from __future__ import annotations

import hashlib
import re
from bisect import bisect_left

import numpy as np
import pandas as pd

from analysis.failure_class import CODE, ENVIRONMENT, TIMEOUT, UNKNOWN, classify

__all__ = ["message_hash", "TriageHistory", "TRIAGE_COLS", "RULE_BRANCH_N", "fclass_onehot"]

DAY = 86400
RULE_BRANCH_N = 3
_HEX = re.compile(r"0x[0-9a-f]+|\b[0-9a-f]{7,40}\b")
_NUM = re.compile(r"\d+")
_WS = re.compile(r"\s+")

#: Model feature columns (E2), in order. `prox_*` / `cochg_*` are the E1 raw features of the bound file.
TRIAGE_COLS = [
    "prior_head_fail_7d", "prior_head_fail_30d", "failed_prev3_branch", "failed_prev10_branch", "msg_hash_seen",
    "fclass_environment", "fclass_timeout", "fclass_code", "fclass_unknown", "status_error", "n_job_rows",
    "duration_s", "bound",
    "cochg_max_support", "cochg_sum_support", "cochg_max_conf", "cochg_sum_conf", "cochg_n_files_with_partner",
    "prox_in_change", "prox_max_jaccard", "prox_min_dir_dist", "prox_name_contains_stem", "prox_same_module",
]


def message_hash(message: str | None) -> str | None:
    """Stable short hash of a failure message with numbers and hex ids masked.

    Args:
        message: The parsed failure message.

    Returns:
        16 hex characters, or None for an empty message.
    """
    if not isinstance(message, str) or not message.strip():
        return None
    t = _WS.sub(" ", _NUM.sub("#", _HEX.sub("#", message.lower()))).strip()[:300]
    return hashlib.sha1(t.encode("utf-8")).hexdigest()[:16]


def fclass_onehot(message: str | None) -> dict[str, int]:
    """One-hot of `failure_class.classify`."""
    c, _ = classify(message)
    return {"fclass_environment": int(c == ENVIRONMENT), "fclass_timeout": int(c == TIMEOUT),
            "fclass_code": int(c == CODE), "fclass_unknown": int(c == UNKNOWN)}


class TriageHistory:
    """Past test failures of every repo, queryable strictly before a time.

    Built from one row per (run, test) failure event. Only runs that have parsed
    test output are known runs: a run with no parsed output tells nothing about a
    test, so "the previous N runs on a branch" means the previous N such runs.
    """

    def __init__(self, events: pd.DataFrame) -> None:
        """Index the events.

        Args:
            events: Columns `repo`, `run_id`, `ts` (epoch s), `test_id`, `base_ref`, `msg_hash`.
        """
        ev = events.drop_duplicates(["run_id", "test_id"])
        self._by_test: dict[tuple[str, str], list[int]] = {}
        for r in ev.sort_values("ts").itertuples():
            self._by_test.setdefault((r.repo, r.test_id), []).append(int(r.ts))
        self._msg_first: dict[tuple[str, str], int] = {}
        for r in ev.dropna(subset=["msg_hash"]).sort_values("ts").itertuples():
            self._msg_first.setdefault((r.repo, r.msg_hash), int(r.ts))
        runs = ev.groupby(["repo", "base_ref", "run_id"], sort=False).agg(ts=("ts", "min"), tests=("test_id", set))
        self._branch: dict[tuple[str, str], list[tuple[int, int, set]]] = {}
        for (repo, ref, rid), row in runs.iterrows():
            self._branch.setdefault((repo, ref), []).append((int(row["ts"]), int(rid), row["tests"]))
        for v in self._branch.values():
            v.sort(key=lambda x: (x[0], x[1]))
        self._branch_ts = {k: [t for t, _, _ in v] for k, v in self._branch.items()}

    def prior_failures(self, repo: str, test_id: str, ts: int, within_days: int | None = None) -> int:
        """Failure events of `test_id` with time strictly before `ts` (optionally within `within_days`)."""
        lst = self._by_test.get((repo, test_id), [])
        hi = bisect_left(lst, ts)
        lo = bisect_left(lst, ts - within_days * DAY) if within_days else 0
        return hi - lo

    def failed_in_previous(self, repo: str, base_ref: str, test_id: str, ts: int, n: int) -> bool:
        """Did `test_id` fail in any of the previous `n` known runs on this branch (started strictly before `ts`)?"""
        key = (repo, base_ref)
        i = bisect_left(self._branch_ts.get(key, []), ts)
        return any(test_id in tests for _, _, tests in self._branch.get(key, [])[max(0, i - n):i])

    def message_seen(self, repo: str, msg_hash: str | None, ts: int) -> bool:
        """Was this message hash seen in a run of the repo that started strictly before `ts`?"""
        if msg_hash is None:
            return False
        first = self._msg_first.get((repo, msg_hash))
        return first is not None and first < ts


def feature_frame_nan_safe(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure every column of :data:`TRIAGE_COLS` exists (NaN when absent) and is numeric."""
    out = df.copy()
    for c in TRIAGE_COLS:
        if c not in out:
            out[c] = np.nan
    out[TRIAGE_COLS] = out[TRIAGE_COLS].apply(pd.to_numeric, errors="coerce")
    return out
