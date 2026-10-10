"""Per-candidate test-file features for E1 (and the raw inputs of E2).

One implementation for BR-Bench and for live repos: everything the features
know about the past comes through a :class:`~src.features.context.HistoryView`,
and every view call is cut off strictly before `ctx.ts`.

Feature families (the prefix is the family; ablation drops by prefix):

``hist_``    prior failures of the test file in this repo
``cochg_``   trailing co-change between the changed files and the test file (D-52)
``cofail_``  earlier instances in which the file failed while the changed file was in the change
``prox_``    path proximity of the test file to the change
``chg_``     properties of the change itself (identical on every row of an instance)
``graph_``   reverse-reachability distance (optional; NaN where no graph exists)
"""

from __future__ import annotations

import re
from bisect import bisect_left

import pandas as pd

from src.features.context import SECONDS_PER_DAY, ChangeContext, HistoryView

HIST_COLS = ["hist_fail_count", "hist_fail_30d", "hist_fail_90d", "hist_days_since_last",
             "hist_head_fail_count", "hist_repo_rank"]
COCHG_COLS = ["cochg_max_support", "cochg_sum_support", "cochg_max_conf", "cochg_sum_conf",
              "cochg_n_files_with_partner"]
COFAIL_COLS = ["cofail_max", "cofail_sum"]
PROX_COLS = ["prox_in_change", "prox_max_jaccard", "prox_min_dir_dist", "prox_name_contains_stem",
             "prox_same_module"]
CHG_COLS = ["chg_n_files", "chg_n_lines", "chg_touches_test", "chg_touches_build", "chg_touches_ci",
            "chg_docs_only"]
GRAPH_COLS = ["graph_hops"]
FAMILIES = {"hist_": HIST_COLS, "cochg_": COCHG_COLS, "cofail_": COFAIL_COLS, "prox_": PROX_COLS,
            "chg_": CHG_COLS, "graph_": GRAPH_COLS}
FEATURE_COLS = HIST_COLS + COCHG_COLS + COFAIL_COLS + PROX_COLS + CHG_COLS  # graph_ is opt-in

_CAMEL = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+")
_MIN_STEM = 3  # shorter stems ("a", "io") would match nearly every file name
_BOUNDARY_DIRS = ("src", "tests", "test")


def path_tokens(path: str) -> frozenset[str]:
    """Lowercase tokens of a path: split on `/ _ - .` and camelCase.

    Args:
        path: Repo-relative path.

    Returns:
        The token set, e.g. `src/UserService_test.py` ->
        `{src, user, service, test, py}`.
    """
    out: set[str] = set()
    for part in re.split(r"[/_\-.]", path):
        out.update(t.lower() for t in _CAMEL.findall(part))
    return frozenset(out)


def jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    """`|a & b| / |a | b|`, 0.0 when both are empty."""
    union = len(a | b)
    return len(a & b) / union if union else 0.0


def dir_distance(a: str, b: str) -> int:
    """Directory-tree distance between two files.

    The number of directory segments to walk up from `a`'s directory to the
    common ancestor plus the number to walk down to `b`'s directory.

    Args:
        a: Repo-relative path.
        b: Repo-relative path.

    Returns:
        0 for files in the same directory.
    """
    da, db = a.split("/")[:-1], b.split("/")[:-1]
    common = 0
    for x, y in zip(da, db):
        if x != y:
            break
        common += 1
    return (len(da) - common) + (len(db) - common)


def module_of(path: str) -> str:
    """The module a file belongs to: the path prefix before its first `src` / `tests` / `test` segment.

    A path that starts with one of those segments belongs to the root module `""`.
    """
    parts = path.split("/")[:-1]
    for i, seg in enumerate(parts):
        if seg in _BOUNDARY_DIRS:
            return "/".join(parts[:i])
    return "/".join(parts[:1])  # no boundary segment: the top-level directory


def stem_of(path: str) -> str:
    """Lowercase file stem (`a/B.test.py` -> `b.test`)."""
    name = path.rsplit("/", 1)[-1]
    return (name.rsplit(".", 1)[0] if "." in name else name).lower()


def featurize(ctx: ChangeContext, candidates: list[str], history: HistoryView,
              graph_hops: dict[str, float] | None = None) -> pd.DataFrame:
    """Feature rows for every candidate test file of one change.

    Args:
        ctx: The change and its cutoff time.
        candidates: Candidate test files, repo-relative.
        history: Past of the repo; only called with `ctx.ts` as the cutoff.
        graph_hops: Optional `{test_file: hops}` from the code graph (the `graph_` family).

    Returns:
        One row per candidate, in the given order: `test_file` plus the columns of
        :data:`FEATURE_COLS` (plus `graph_hops`).
    """
    ts, changed = ctx.ts, list(ctx.changed_files)
    changed_set = set(changed)
    ch_tokens = [path_tokens(c) for c in changed]
    ch_stems = sorted({s for s in (stem_of(c) for c in changed) if len(s) >= _MIN_STEM})
    ch_modules = {module_of(c) for c in changed}
    partners = [history.cochange_partners(c, ts, ctx.head_sha) for c in changed]
    n_with_partner = sum(1 for p in partners if p)

    rows = []
    for tf in candidates:
        fails = history.failures_before(tf, ts)
        ftimes = [t for t, _ in fails]
        n30 = len(ftimes) - bisect_left(ftimes, ts - 30 * SECONDS_PER_DAY)
        n90 = len(ftimes) - bisect_left(ftimes, ts - 90 * SECONDS_PER_DAY)
        last = (ts - ftimes[-1]) / SECONDS_PER_DAY if ftimes else float("nan")

        sup = [p[tf][0] for p in partners if tf in p]
        conf = [p[tf][1] for p in partners if tf in p]
        cof = [history.cofailure_count(c, tf, ts) for c in changed]

        tt = path_tokens(tf)
        name = tf.rsplit("/", 1)[-1].lower()
        rows.append({
            "test_file": tf,
            "hist_fail_count": len(fails),
            "hist_fail_30d": n30,
            "hist_fail_90d": n90,
            "hist_days_since_last": last,
            "hist_head_fail_count": len(history.head_failures_before(tf, ts)),
            "cochg_max_support": max(sup, default=0),
            "cochg_sum_support": sum(sup),
            "cochg_max_conf": max(conf, default=0.0),
            "cochg_sum_conf": sum(conf),
            "cochg_n_files_with_partner": n_with_partner,
            "cofail_max": max(cof, default=0),
            "cofail_sum": sum(cof),
            "prox_in_change": int(tf in changed_set),
            "prox_max_jaccard": max((jaccard(tt, c) for c in ch_tokens), default=0.0),
            "prox_min_dir_dist": min((dir_distance(tf, c) for c in changed), default=0),
            "prox_name_contains_stem": int(any(s in name for s in ch_stems)),
            "prox_same_module": int(module_of(tf) in ch_modules),
            "chg_n_files": len(changed),
            "chg_n_lines": ctx.n_lines_changed,
            "chg_touches_test": int(ctx.touches_test_file),
            "chg_touches_build": int(ctx.touches_build_config),
            "chg_touches_ci": int(ctx.touches_ci_config),
            "chg_docs_only": int(ctx.is_docs_only),
        })
    df = pd.DataFrame(rows, columns=["test_file", *HIST_COLS[:5], *COCHG_COLS, *COFAIL_COLS, *PROX_COLS, *CHG_COLS])
    # rank by prior failures within the repo's candidate list (1 = most failing), ties by path
    order = df.sort_values(["hist_fail_count", "test_file"], ascending=[False, True]).index
    rank = pd.Series(range(1, len(df) + 1), index=order)
    df["hist_repo_rank"] = rank.reindex(df.index).astype("int32")
    if graph_hops is not None:
        df["graph_hops"] = [graph_hops.get(t, float("nan")) for t in df["test_file"]]
    return df[["test_file", *FEATURE_COLS] + (GRAPH_COLS if graph_hops is not None else [])]
