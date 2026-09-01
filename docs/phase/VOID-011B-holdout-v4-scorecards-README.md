# VOID — holdout_v4 raw scorecards (011-B)

> [!CAUTION]
> **Every number in the three `VOID-011B-holdout-v4-scorecard-*.txt` files is
> VOID, not superseded.** No valid measurement occurred. They are retained as
> evidence for the voiding ruling and for nothing else.
>
> Do not quote them in the paper, a slide, a report, or a prompt. Do not use any
> identifier in them as an EXPECTED value in any test.

## Why they are void

The ground truth these runs scored against (formerly
`tests/fixtures/holdout_v4/EXPECTED.md`) was produced by running
`normalize_test_id()` over raw log lines — the extractor under evaluation. That
is circular, and it violates D-27 and Phase 3 of 011-B. See
`docs/phase/011B-holdout-v4-score.md` for the ruling, D-38 in
`docs/DECISIONS.md` for the void-versus-superseded distinction, and
`docs/phase/011B-VOIDED-machine-labels.md` for the machine labels themselves.

A valid measurement requires the hand-labelling worksheet at
`docs/phase/012B-holdout-v4-worksheet.md`.

## What each file is

These were captured at the repository root as `scratch_score*.txt` and moved
here under a `VOID-` prefix so they can never be mistaken for a measurement.
Contents are unmodified from the scorer's output.

| File | Fixtures | Precision | Recall | Class. accuracy |
|---|---:|---:|---:|---:|
| `VOID-011B-holdout-v4-scorecard-run1-45.83pct.txt` | 32 | 45.83% (22/48) | 48.89% (22/45) | 78.12% (25/32) |
| `VOID-011B-holdout-v4-scorecard-run2-empty.txt` | 0 | — | — | — |
| `VOID-011B-holdout-v4-scorecard-run3-58.33pct.txt` | 32 | 58.33% (28/48) | 59.57% (28/47) | 84.38% (27/32) |

Run 2 scored zero fixtures and produced no rows at all; it is kept only so the
sequence of three runs is complete.

Run 3 is the raw scorer output behind the 58.33% figure quoted in
`docs/phase/011B-holdout-v4-score.md`. That is the figure D-38 voids.
