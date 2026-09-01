# Session 078 — 2026-09-01 — Phase 017: root cleanup, exact_green verification, label rebuild

**Task:** Finish the repository-root cleanup; verify every `exact_green` base run
against parsed logs rather than run conclusion; rewrite the assignment to require
log evidence; report what moved.

**Operator:** Deepanshu. **Agent:** Claude Opus 5 (Claude Code).

---

## 1. Rulings applied

- **matplotlib: NO.** `analysis/rq1_divergence.py` now imports it lazily inside
  `write_figures()`, which warns and skips on `ImportError`. Every number the
  script prints regenerates on a fresh clone with no plotting stack.
- **Secret-scan tiering RATIFIED** as written → **D-45** appended. D-21 untouched.
- **`docs/phase/009B-REPORT.md`** Axis-1 and Axis-2 tables marked **STALE**, with
  the reason named: 014-A rewrote `outcomes.parquet` and the strict split moved
  524 → 778. RQ1 deliberately not re-derived; labels move again this round.

## 2. Phase 1 — root cleanup

49 untracked files at the repository root → **0**. Three moved as evidence
(`holdout_v3_score*.txt` → `docs/phase/009B-holdout-v3-scorecard-*`), 46 deleted.
Every file was inspected before deletion; the classification is in
`docs/phase/017-REPORT.md`.

Findings from the inspection:

- `scratch_eval.py` differed from `analysis/holdout_eval.py` by **one line** — a
  changed `HOLDOUT_DIR` constant. Someone copied a 444-line file to change a
  default because `holdout_eval.py`'s `main()` has no `--holdout-dir` flag.
  Reported, not fixed (out of scope).
- `package_release.py` **does not build the release**. It prints schema
  mismatches and writes nothing. `release/v0.1/` therefore has **no regenerating
  script at all**.
- `tmp_test.py`'s three tests were already promoted into
  `tests/test_fixture_score.py:85-106`.

## 3. Phase 2 — the base-side defect

Both `analysis/fetch_base_logs.py` and `analysis/parse_base_logs.py` filtered
base-run jobs with `if job.get("conclusion") != "failure": continue`. An
`exact_green` base concludes `success`, so **no job of it is ever `failure`** —
the pipeline parsed zero jobs for all 4,245 and `NO_TEST_OUTPUT` was its
guaranteed verdict. Fixed on the base side only; the head-side filter is
untouched.

Two further defects found in the same path and fixed:

1. **Pagination.** `per_page=100` with no page turn silently truncated any run
   with more than 100 jobs. Now paginates to `total_count`.
2. **Dead status accounting.** `get_with_backoff()` *raises* `requests.HTTPError`
   on non-retryable 4xx rather than returning the response, so every
   `resp.status_code == 410` branch in `fetch_base_logs.py` was unreachable and
   its 410 counter read zero by construction.

**2c: 211 of 762 verified instances (27.7%) would have been demoted by the old
path and are kept by the fix.** All 220 verified base runs contain zero
`conclusion == "failure"` jobs, measured from the stored payloads.

## 4. Phase 3 — the invariant in the type

`BaseResolution.__post_init__` now rejects `status == "exact_green"` unless
`base_parse_status` is `green_verified` or `green_verified_partial`. New
`_resolve_successful_base()` routes every successful base through log evidence;
`unverified` demotes.

`tests/test_base_resolve.py::test_base_resolve_ancestor_real_payload` failed, as
predicted — it asserted `exact_green` from conclusion alone. **The ground truth
was not weakened.** Its ancestor-traversal assertions are unchanged; the
successful-base expectation was strengthened into two cases (demote without
evidence, `exact_green` with it) and the amendment is justified in the docstring.

Suite: **predicted 402, actual 402.**

## 5. Commands

Every command and its raw output is in the phase report,
`docs/phase/017-REPORT.md`.

## 6. Non-goals honoured

`docs/SCHEMAS.md` untouched · `tests/fixtures/holdout_v3/` and `holdout_v4/`
untouched · parsers untouched · `candidates.parquet` not built · daemon not
started (confirmed no `python3` process before writing under `data/`) · no new
dependency.

## 7. Open questions for the operator

1. The sweep covered **220 / 1,732 base runs (12.7%)** in the 45-minute cap —
   Python complete at 167/167, Java at 53/1,565. Completing Java is ~4 more hours
   at the measured throughput.
2. **11 of 620** instances in visibly test-free workflows survive into strict
   under evidence-only. That is a corpus-inclusion defect and awaits a ruling.
3. `release/v0.1/` has no regenerating script.
