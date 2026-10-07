"""`analysis/parser_precision_table.py` against the real checked-in corpora."""

from __future__ import annotations

from analysis.fixture_score import score_corpus
from analysis.holdout_eval import evaluate_holdout
from analysis.parser_precision_table import (
    FIXTURE_INDEPENDENCE,
    HOLDOUT_V1_INDEPENDENCE,
    _row,
)


def test_fixture_row_is_n_over_d_and_marked_not_independent() -> None:
    rep = score_corpus()
    row = _row("fixtures", rep, FIXTURE_INDEPENDENCE)
    tp, fp, fn = rep.true_positives, rep.false_positives, rep.false_negatives
    assert row[3] == f"{tp}/{tp + fp} ({tp / (tp + fp):.2%})"
    assert row[4] == f"{tp}/{tp + fn} ({tp / (tp + fn):.2%})"
    assert row[5].startswith(f"{rep.class_matches}/{rep.total_fixtures} ")
    assert row[-1].startswith("NO.")


def test_holdout_v1_row_is_marked_a_development_set_under_d37() -> None:
    rep = evaluate_holdout()
    row = _row("holdout v1", rep, HOLDOUT_V1_INDEPENDENCE)
    assert row[1] == rep.total_fixtures == 20
    assert row[-1].startswith("NO.") and "D-37" in row[-1]
