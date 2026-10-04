"""Guards on the T5.6b mini-corpus reproduction target.

The reproduction itself takes minutes and needs the three clones, so it is not
run here. What is tested is everything that decides whether its output can be
believed: that the repo list still agrees with `docs/MINI_CORPUS.md`, that the
SHA selection is deterministic and filtered as the doc defines, and above all
that a run which builds nothing cannot report the budget as met.

Fixtures are the real `docs/MINI_CORPUS.md` and the real interim parquet
tables; the data-dependent tests skip rather than fail on a fresh clone.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from analysis.reproduce_mini_corpus import (
    BUDGET_SECONDS,
    MINI_CORPUS,
    observed_test_ids,
    resolved_base_shas,
    verdict,
)
from tests.conftest import requires_data

REPO_ROOT = Path(__file__).resolve().parent.parent
MINI_CORPUS_DOC = REPO_ROOT / "docs/MINI_CORPUS.md"
BASE_RESOLUTION = "data/interim/base_resolution.parquet"
PARSED_OUTCOMES = "data/interim/parsed_outcomes.parquet"


def test_budget_is_the_roadmap_target() -> None:
    """T5.6b's budget is fifteen minutes; the constant must say so."""
    assert BUDGET_SECONDS == 15 * 60


def test_mini_corpus_matches_the_doc() -> None:
    """The three repos and clone dirs are the ones MINI_CORPUS.md selects."""
    text = MINI_CORPUS_DOC.read_text(encoding="utf-8")
    for repo, clone_dir in MINI_CORPUS:
        assert f"`{repo}`" in text, f"{repo} is not named in MINI_CORPUS.md"
        assert f"`{clone_dir}`" in text, f"{clone_dir} is not named in MINI_CORPUS.md"
    assert len(MINI_CORPUS) == 3
    assert len({repo for repo, _ in MINI_CORPUS}) == 3
    assert len({clone for _, clone in MINI_CORPUS}) == 3


def test_clone_dirs_follow_the_owner__name_convention() -> None:
    """`owner/name` maps to `data/clones/owner__name`, as the doc specifies."""
    for repo, clone_dir in MINI_CORPUS:
        owner, name = repo.split("/")
        assert clone_dir == f"data/clones/{owner}__{name}"


# --- verdict(): the one thing that must never silently pass ----------------


def test_zero_graphs_built_is_a_failure_however_fast() -> None:
    """With the clones absent the run is fast and reproduces nothing."""
    code, text = verdict(built=0, total_seconds=0.4)
    assert code == 1
    assert "NO GRAPHS BUILT" in text
    assert "MET" != text


def test_within_budget_with_graphs_is_a_pass() -> None:
    code, text = verdict(built=9, total_seconds=BUDGET_SECONDS - 1)
    assert code == 0
    assert text == "MET"


def test_over_budget_is_reported_but_not_fatal() -> None:
    """The budget is a measurement of this laptop, not a property of the code."""
    code, text = verdict(built=9, total_seconds=BUDGET_SECONDS + 1)
    assert code == 0
    assert text.startswith("NOT MET")


def test_budget_boundary_is_strict() -> None:
    """Exactly at the budget is not under it."""
    assert verdict(1, float(BUDGET_SECONDS))[1].startswith("NOT MET")


# --- SHA selection ---------------------------------------------------------


@requires_data(BASE_RESOLUTION)
@pytest.mark.parametrize("repo", [repo for repo, _ in MINI_CORPUS])
def test_resolved_base_shas_are_deterministic(repo: str) -> None:
    """Two calls agree, so a reported figure names a reproducible SHA set."""
    assert resolved_base_shas(repo, 3) == resolved_base_shas(repo, 3)


@requires_data(BASE_RESOLUTION)
@pytest.mark.parametrize("repo", [repo for repo, _ in MINI_CORPUS])
def test_resolved_base_shas_are_distinct_full_shas(repo: str) -> None:
    """Every selected SHA is a distinct 40-hex commit id, never null."""
    shas = resolved_base_shas(repo, 3)
    assert shas, f"{repo} has no resolved base in {BASE_RESOLUTION}"
    assert len(set(shas)) == len(shas)
    for sha in shas:
        assert re.fullmatch(r"[0-9a-f]{40}", sha), sha


@requires_data(BASE_RESOLUTION)
def test_resolved_base_shas_honours_the_limit() -> None:
    """`--shas-per-repo` is an upper bound, and a prefix of the larger set."""
    repo = MINI_CORPUS[0][0]
    assert len(resolved_base_shas(repo, 1)) <= 1
    assert resolved_base_shas(repo, 1) == resolved_base_shas(repo, 3)[:1]


@requires_data(BASE_RESOLUTION)
def test_resolved_base_shas_only_returns_resolved_statuses() -> None:
    """Selected SHAs come from exact/exact_green/ancestor rows, not no_base."""
    import duckdb

    repo = MINI_CORPUS[0][0]
    shas = resolved_base_shas(repo, 3)
    placeholders = ", ".join(f"'{sha}'" for sha in shas)
    statuses = {
        row[0]
        for row in duckdb.sql(
            f"""select distinct status
                from read_parquet('{BASE_RESOLUTION}')
                where repo = '{repo}' and base_sha in ({placeholders})"""
        ).fetchall()
    }
    assert statuses <= {"exact", "exact_green", "ancestor"}, statuses


@requires_data(PARSED_OUTCOMES)
def test_observed_test_ids_are_distinct_and_non_null() -> None:
    """The binding denominator must be de-duplicated, or the rate is wrong."""
    ids = observed_test_ids(MINI_CORPUS[0][0])
    assert ids, "no observed test ids for the first mini-corpus repo"
    assert len(set(ids)) == len(ids)
    assert all(i is not None and i != "" for i in ids)
