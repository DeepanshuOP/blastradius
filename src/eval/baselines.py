"""Baselines B0-B7 for E1. Every baseline returns one score per candidate (higher = riskier).

Ties are broken deterministically by test-file path (`rank`), never by input order.

| ID | Name | Cited as |
|----|------|----------|
| B0 | retest-all, alphabetical | practice / Jenkins |
| B1 | random, mean over 20 seeds | floor |
| B2 | changed test files | RQ1 "changed files" |
| B3 | trailing co-change support (D-52) | RQ1; ROADMAP §24 B7 |
| B4 | prior strict failure count (D-52) | RQ1 |
| B5 | BM25 over path tokens | Peng et al., ISSTA 2020 (path-token variant) |
| B6 | LightGBM lambdarank on `hist_` only | Bertolino et al., ICSE 2020 (MART-style LTR) |
| B7 | LightGBM lambdarank on `hist_` + `prox_` + `chg_` | Elsner et al., ISSTA 2021 (feature subset) |

B6/B7 are trained by `src/models/e1_ranker.py` on the column lists below.
"""

from __future__ import annotations

import math
import re
from collections import Counter

import numpy as np
import pandas as pd

from src.features.test_features import CHG_COLS, HIST_COLS, PROX_COLS

__all__ = ["B6_COLS", "B7_COLS", "BASELINE_NAMES", "rank", "score_b0", "score_b1", "score_b2", "score_b3",
           "score_b4", "score_b5", "bm25_scores", "path_token_list", "RANDOM_SEEDS"]

RANDOM_SEEDS = tuple(range(20))
B6_COLS = list(HIST_COLS)
B7_COLS = [*HIST_COLS, *PROX_COLS, *CHG_COLS]
BASELINE_NAMES = {
    "B0": "retest-all (alphabetical)", "B1": "random (20 seeds)", "B2": "changed test files",
    "B3": "co-change support", "B4": "failure history", "B5": "BM25 path tokens",
    "B6": "history-only LTR", "B7": "readily-available-info LTR",
}
_CAMEL = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+")


def rank(files: list[str], scores: np.ndarray | list[float]) -> list[str]:
    """Order `files` by score descending, ties by path ascending."""
    order = sorted(range(len(files)), key=lambda i: (-float(scores[i]), files[i]))
    return [files[i] for i in order]


def score_b0(g: pd.DataFrame) -> np.ndarray:
    """B0: every candidate scores 0, so the ranking is alphabetical by path."""
    return np.zeros(len(g))


def score_b1(g: pd.DataFrame, seed: int) -> np.ndarray:
    """B1: a seeded uniform random score per candidate.

    Args:
        g: One instance's candidate rows.
        seed: Permutation seed (combined with the row count so instances differ).
    """
    return np.random.default_rng([seed, len(g)]).random(len(g))


def score_b2(g: pd.DataFrame) -> np.ndarray:
    """B2: 1 if the test file is itself part of the change."""
    return g["prox_in_change"].to_numpy(dtype=float)


def score_b3(g: pd.DataFrame) -> np.ndarray:
    """B3: max trailing co-change support with any changed file (support >= 2, D-52)."""
    return g["cochg_max_support"].to_numpy(dtype=float)


def score_b4(g: pd.DataFrame) -> np.ndarray:
    """B4: prior strict failure events of the file in this repo (D-52 rule)."""
    return g["hist_fail_count"].to_numpy(dtype=float)


def path_token_list(path: str) -> list[str]:
    """Lowercase token list (with repeats) of a path: split on `/ _ - .` and camelCase."""
    out: list[str] = []
    for part in re.split(r"[/_\-.]", path):
        out.extend(t.lower() for t in _CAMEL.findall(part))
    return out


def bm25_scores(docs: list[list[str]], query: list[str], k1: float = 1.2, b: float = 0.75) -> np.ndarray:
    """Okapi BM25 of each document against a query, in-house.

    `score(d) = sum over distinct query terms t of idf(t) * tf * (k1 + 1) / (tf + k1 * (1 - b + b * |d| / avgdl))`
    with `idf(t) = ln(1 + (N - df + 0.5) / (df + 0.5))`; `N`, `df` and `avgdl` over `docs`.

    Args:
        docs: Token lists, one per candidate.
        query: Query tokens (distinct terms are used).
        k1: Term-frequency saturation.
        b: Length normalisation.

    Returns:
        One score per document; zeros when the query or the corpus is empty.
    """
    n = len(docs)
    if n == 0 or not query:
        return np.zeros(n)
    avgdl = sum(len(d) for d in docs) / n or 1.0
    df = Counter(t for d in docs for t in set(d))
    out = np.zeros(n)
    for i, d in enumerate(docs):
        tf = Counter(d)
        norm = k1 * (1 - b + b * len(d) / avgdl)
        for t in set(query):
            if t in tf:
                idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
                out[i] += idf * tf[t] * (k1 + 1) / (tf[t] + norm)
    return out


def score_b5(g: pd.DataFrame, changed_files: list[str]) -> np.ndarray:
    """B5: BM25 of each candidate's path tokens against the tokens of the changed paths.

    Path-token variant of Peng et al. (ISSTA 2020), which indexes test source
    code; this one never reads file contents, only paths.
    """
    query = [t for c in changed_files for t in path_token_list(c)]
    return bm25_scores([path_token_list(f) for f in g["test_file"]], query)


def reproduce_rq1(data, contexts: dict, hist, gt: dict, k: int = 10) -> dict:
    """Recompute RQ1's three set baselines at `k` from the E1 building blocks.

    Same population and rules as `analysis.rq1_divergence.evaluate_k`: instances
    with a changeset and ground truth on which the all-partners co-change set (after
    removing the changed files) is non-empty. Used as the HARD STOP 1 check.

    The historical-frequency set uses RQ1's own tie rule (`value_counts` order of
    the evidence rows). The E1 ranking B4 breaks ties by path instead, which is a
    different but equally arbitrary choice; `hist_hits_path_ties` reports what that
    rule scores on the same instances so the difference is visible, not hidden.

    Args:
        data: `Rq1Data`.
        contexts: `{(repo, run_id): (ChangeContext, run_started_at)}`.
        hist: `BrBenchHistory`.
        gt: `{(repo, run_id): set of ground-truth files}`.
        k: Partners / files kept.

    Returns:
        `{"n", "actual", "co_hits", "changed_hits", "hist_hits", "hist_hits_path_ties"}`.
    """
    frame = data.hist_all
    n = actual = co_hits = ch_hits = hi_hits = hi_path = 0
    for key, (ctx, started) in contexts.items():
        truth = gt.get(key)
        if not truth or not ctx.changed_files:
            continue
        repo = ctx.repo
        F = set(ctx.changed_files)
        c_co: set[str] = set()
        for f in sorted(F):
            c_co.update(list(hist.cochange_partners(f, ctx.ts, ctx.head_sha, repo))[:k])
        c_co -= F
        if not c_co:
            continue
        n += 1
        actual += len(truth)
        co_hits += len(c_co & truth)
        ch_hits += len(F & truth)
        ev = frame[(frame["repo"] == repo) & (frame["run_started_at"] < started)]
        if len(ev):
            vc = ev["resolved_path"].value_counts()
            hi_hits += len(set(vc.head(k).index) & truth)
            counts = vc.to_dict()
            hi_path += len(set(sorted(counts, key=lambda f: (-counts[f], f))[:k]) & truth)
    return {"n": n, "actual": actual, "co_hits": co_hits, "changed_hits": ch_hits, "hist_hits": hi_hits,
            "hist_hits_path_ties": hi_path}
