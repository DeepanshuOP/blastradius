"""Parser precision/recall table for the paper: `paper/generated/parser_precision.md`.

Scores the fixture corpus (`analysis/fixture_score.py`) and holdout v1
(`analysis/holdout_eval.py`) and states, per corpus, whether it is independent
of parser development. Neither is: that status comes from the protocol
documents, not from this script, and is quoted with its source.
"""

from __future__ import annotations

from analysis import paper_md
from analysis.fixture_score import score_corpus
from analysis.holdout_eval import evaluate_holdout
from analysis.paper_md import rate

FIXTURE_INDEPENDENCE = (
    "NO. Development corpus: the parsers were built and tuned against these logs "
    "(`docs/phase/013B-holdout-v5-protocol.md` §4, 'Development fixtures'; `docs/session/059-2026-08-27-holdout-scoring.md`)."
)
HOLDOUT_V1_INDEPENDENCE = (
    "NO. Permanently a development set under D-37: it drove three parser fixes diagnosed from its own "
    "failures, and `tests/test_holdout_eval.py` pins the parsers to its ids "
    "(`docs/phase/027-scorer-provenance.md`; `docs/HANDOVER-020.md` §3.5). The 100% is a fit number "
    "and may not be reported as held-out performance."
)
V5_ROW = [
    "holdout v5 (independent of development)", "NOT SCORED",
    "no blind human labels (D-53); corpus unconsumed",
]


def _row(name: str, rep, independent: str) -> list:
    tp, fp, fn = rep.true_positives, rep.false_positives, rep.false_negatives
    n = rep.total_fixtures
    cls = getattr(rep, "class_matches")
    return [name, n, rep.total_expected, rate(tp, tp + fp), rate(tp, tp + fn), rate(cls, n),
            f"{tp} / {fp} / {fn}", independent]


def main() -> None:
    fixture = score_corpus()
    holdout = evaluate_holdout()
    text = paper_md.header(
        "Parser precision and recall", "analysis/parser_precision_table.py",
        "Precision = TP/(TP+FP), recall = TP/(TP+FN) over expected test identifiers; classification accuracy "
        "= fixtures whose log class matches the hand label. **No figure on this page is independent of "
        "development**, so none is a held-out precision claim.")
    text += "\n" + paper_md.table(
        ["corpus", "fixtures", "expected ids", "precision (n/d)", "recall (n/d)",
         "classification accuracy (n/d)", "TP / FP / FN", "independent of development?"],
        [_row("fixture corpus (`tests/fixtures/logs/`)", fixture, FIXTURE_INDEPENDENCE),
         _row("holdout v1 (`tests/fixtures/holdout/`)", holdout, HOLDOUT_V1_INDEPENDENCE),
         [V5_ROW[0] + ": NOT SCORED, " + V5_ROW[2], "n/a", "n/a", "n/a", "n/a", "n/a", "n/a",
          "Independent figure NOT MEASURED (D-53)."]])
    rows = [[h.harness, h.fixtures_count, h.expected_ids_count, rate(h.tp, h.tp + h.fp),
             rate(h.tp, h.tp + h.fn), rate(h.class_correct, h.fixtures_count)]
            for h in holdout.harness_breakdown.values()]
    text += "\n## Holdout v1 by harness\n\n" + paper_md.table(
        ["harness", "fixtures", "expected ids", "precision (n/d)", "recall (n/d)", "classification (n/d)"], rows)
    text += (f"\nCross-firing fixtures (more than one parser extracted ids): "
             f"{rate(holdout.cross_firing_count, holdout.total_fixtures)}.\n")
    path = paper_md.write("parser_precision.md", text)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
