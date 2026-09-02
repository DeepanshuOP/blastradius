# Phase 027: Holdout Scorer Provenance Verdict

**Date**: 2026-09-02 · **Scope**: `analysis/holdout_eval.py`, `tests/fixtures/holdout/` · **Decisions**: D-27, D-29, D-37, D-38

## Verdict: ground truth VALID (not void under D-38); the 100.00% is VOID as a held-out claim (D-37)

`evaluate_holdout()` scores `tests/fixtures/holdout/` — 20 fixtures, 30 expected identifiers.
`parse_holdout_expected()` reads expected values from `tests/fixtures/holdout/EXPECTED.md`.
Those values are hand-written from raw log bytes, not machine-derived:

- Header: "All labels were identified **by eye directly from raw log text** without consulting or running any BlastRadius extractor or classifier."
- Sessions 053 and 054: "Did NOT run `log_yield.py`, `fixture_score.py`, `log_gradle.py`, `log_maven.py`, `log_pytest.py`, or any parser against the holdout set."
- Four commits touch `EXPECTED.md`; only value edit is `50b3aa1` (fixtures 14, 15: FQCN -> bare class, per D-29). `aea1feb` added `Expected Class` lines only. No script writes this file — unlike `build_holdout_v4.py`, which wrote holdout_v4's EXPECTED.md and voided it.
- Positive evidence of a human hand: fixtures 14 and 15 originally carried package prefixes appearing **0 times** in their logs (session 060 audit). No extractor can emit a package absent from the log; only an external repo lookup by a person can.

**But the score is not a held-out measurement.** Under D-37 this corpus became a development set on 2026-08-27: session 060 §5 filed three parser defects diagnosed by inspecting per-fixture holdout failures — `log_maven` Surefire method-before-class (fixtures 6, 7), `log_gradle` S1 state reset (fixture 9), `log_pytest` timeout interleaving (fixture 1). All three were fixed; all four fixtures now score OK. `tests/test_holdout_eval.py` further pins the parsers to these exact identifiers as regression assertions.

Trajectory on this one corpus: 29.73% / 36.67% -> 45.95% / 56.67% (session 060) -> 100.00% / 100.00% today (TP 30, FP 0, FN 30-30=0; 20/20 fixtures classified). Today's figure supersedes session 060's 45.95% / 56.67% as a development-set fit number and nothing more.

**Ruling**: 100.00% may never be reported as held-out parser performance in any paper section, slide, or report. `docs/REPRODUCE.md` §6 presents `analysis/holdout_eval.py` as "held-out dataset" evaluation; that framing is wrong.

**The scorer itself is sound** — it does not score the parser against its own output. Two operator notes before v5: `HOLDOUT_DIR` and `EXPECTED_MD` are module constants pinned to `tests/fixtures/holdout`, so v5 needs a path argument; and v5's EXPECTED.md must be transcribed from the blind worksheet.

## Worksheet check

`docs/phase/024-holdout-v5-worksheet.md`: 40 sections × 4 expected fields. Filled 0/160, empty 160/160 (0/40 fixtures labelled). Zero occurrences of `normalize_test_id`, `Canonical`, `TEST_FAILURE`, `TEST_RAN_CLEAN`, `NO_TEST_OUTPUT`, `fqcn_incomplete`, `extract_`. Clean for blind filling.

## data/raw size contradiction

```
$ du -sb data/raw
2734020926	data/raw
$ du -sh data/raw
4.9G	data/raw
```

Both correct, measuring different quantities: 2,734,020,926 B (2.55 GiB) is apparent content size; 4.9 GiB is disk-block usage, inflated by 4 KiB block granularity across 304,534 small gzipped logs. The error is combining them in one cell. `docs/phase/025-transfer-manifest.md` §1 pairs the byte count with "4.9 GB" in a Human column that is otherwise a correct bytes/1024^n conversion; `docs/HANDOVER-PRISHA.md` and `docs/CURRENT-STATE.md` repeat "4.9 GB / 2,734,020,926 B"; `docs/REPRODUCE.md`, `docs/DATA_TRANSFER.md`, `docs/DATA_DEPENDENCIES.md` carry "4.9 GB" alone. Use 2.73 GB for transfer sizing, 4.9 GiB for destination free space. Not edited here.
