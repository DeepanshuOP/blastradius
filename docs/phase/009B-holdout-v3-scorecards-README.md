# holdout_v3 raw scorecards — evidence for the paper's §III parser table

These three files are the raw scorer output behind the holdout_v3 numbers. They
were captured at the repository root as `holdout_v3_score*.txt` and moved here
unmodified. Produced by `analysis/holdout_eval.py`
(`print_holdout_scorecard`), which regenerates them via `make tables`.

> [!IMPORTANT]
> **The paper's honest held-out figure is 83.87% precision / 55.32% recall, and
> it is NOT in any of these files.** That is the *first* scoring of holdout_v3,
> taken before the parser fixes. Everything here is the *second* scoring, taken
> after fixes that were derived from auditing fixtures 14, 16 and 18 **of this
> very corpus**, so 95.74% / 97.83% is fitted and is not a generalisation
> claim. Report both, never one replacing the other. See `docs/HANDOFF.md`
> §3.5 and Architect ruling 6.

## What each file is

Precision, recall and F1 are identical across all three (95.74% / 97.83% /
0.9677 — 45 TP, 2 FP, 1 FN over 30 fixtures). Only **classification accuracy**
moves, and it moves because hand labels were corrected, not because the parser
changed:

| File | Class. accuracy | What changed |
|---|---:|---|
| `009B-holdout-v3-scorecard-run1-classacc-90.00pct.txt` | 90.00% (27/30) | Baseline. Fixtures 20 and 23 expected `NO_TEST_OUTPUT`. |
| `009B-holdout-v3-scorecard-run2-classacc-96.67pct.txt` | 96.67% (29/30) | Fixtures 20 and 23 corrected to `TEST_RAN_CLEAN`. These were a **scorer** bug, not a label bug — `fixture_score.py` tested for the literal substring `"passed clean"` in free prose and silently fell back. Architect ruling 8. |
| `009B-holdout-v3-scorecard-run3-fixture4-corrected-classacc-100.00pct.txt` | 100.00% (30/30) | Fixture 4 reverted from `NO_TEST_OUTPUT` back to `TEST_FAILURE`. The amendment to `NO_TEST_OUTPUT` had **exceeded authorisation**; Surefire printed `Tests run: 1, Failures: 0, Errors: 1, Skipped: 0 … <<< FAILURE!` at line 4538, so the log plainly has test output. |

Run 3 is the "Post-Fixture 4 Correction" column of the Corrected Holdout_v3
Table in `docs/phase/009B-REPORT.md`.

## Related

- `docs/phase/VOID-011B-holdout-v4-scorecards-README.md` — the holdout_v4
  scorecards, every number in which is VOID.
- Per invariant 9, a quarantined corpus is scored once. **holdout_v3 is
  CLOSED.** No further scoring events without explicit Architect approval.
