# Phase 016-B Report: Correct the Candidate Universe & Record the Gate 1 Reading

**Spec**: [CLI-2] — PHASE SPEC 016-B
**Date**: 2026-09-01
**Agent operating rules**: `docs/AGENT_RULES.md` read and applied in full. Session guard:
`Linux` / `/home/shree/blastradius` / `Python 3.11.15`. Git identity:
`DeepanshuOP` / `99538840+DeepanshuOP@users.noreply.github.com`.
**Scope honoured**: no subagents, no background tasks, no heredocs, no writes to `src/`,
`analysis/`, `tests/`, `Makefile`, `docs/SCHEMAS.md`, `docs/ROADMAP.md`, any parquet, or any
repo-root file. No git beyond read-only (`git status`/`config` only). No negatives generated,
no `candidates.parquet` built, no holdout v5 sampled.

---

## Phase 1 — Prove or Refute the Circularity

**Data source**: `data/interim/parsed_outcomes.parquet` (20,535 rows), joined against
`data/interim/instances_raw.parquet` (165,349 rows, one row per (repo, run) with
`run_conclusion` and `job_ids` populated for 100% of rows).

### 1a. Distinct test_ids with status NOT in ('fail', 'error')

Query:
```python
import pyarrow.parquet as pq
po = pq.read_table('data/interim/parsed_outcomes.parquet').to_pandas()
not_fail_error = po[~po['status'].isin(['fail', 'error'])]
print(not_fail_error['test_id'].nunique())
```
Raw count: **0**. `po['status'].unique()` returns exactly `['fail', 'error']` — the table has
zero rows of any other status. There is nothing to be non-failing about; the column is
degenerate.

### 1b. Parsed logs by run conclusion

Query:
```python
import pyarrow.parquet as pq
po = pq.read_table('data/interim/parsed_outcomes.parquet').to_pandas()
ir = pq.read_table('data/interim/instances_raw.parquet').to_pandas()
run_conc = ir[['run_id', 'run_conclusion']].drop_duplicates()
parsed_runs = po[['run_id']].drop_duplicates()
joined = parsed_runs.merge(run_conc, on='run_id', how='left')
print(joined['run_conclusion'].value_counts(dropna=False))
```
Raw output (distinct `run_id` in `parsed_outcomes`, 1,863 total):
```
run_conclusion
failure      1810
cancelled      43
success        10
```
All 1,863 parsed runs matched an `instances_raw` row (0 unmatched); no `run_id` carries more
than one distinct `run_conclusion`.

### 1c. Verdict

**No.** The candidate universe contains **0 of 6,014** distinct `test_id`s that were ever
observed with a non-failing status. Every candidate test exists in the universe *solely*
because it appeared in a `status in ('fail', 'error')` row — the table `parsed_outcomes.parquet`
was never populated with any other status to begin with (1a). The candidate pool and the
positive pool are drawn from the identical population by construction. The finding in the
task prompt is confirmed, not refuted.

### 1d. Top-5 candidate pools vs. a successful run's test count

Query:
```python
pool = po.groupby('repo')['test_id'].nunique().sort_values(ascending=False)
po2 = po.merge(run_conc, on='run_id', how='left')
for repo in pool.head(5).index:
    sub = po2[(po2['repo'] == repo) & (po2['run_conclusion'] == 'success')]
    ...
```
| Repo | Candidate pool | Successful runs parsed | Test count in those runs |
|---|---:|---:|---|
| `apache/beam` | 1,707 | 0 | none parsed |
| `sirixdb/sirix` | 1,309 | 10 | 1, 2, 4, 179, 180, 181, 182, 189, 1205, 1245 |
| `castorini/anserini` | 560 | 0 | none parsed |
| `floci-io/floci` | 449 | 0 | none parsed |
| `Stirling-Tools/Stirling-PDF` | 307 | 0 | none parsed |

4 of the 5 largest pools have **no parsed successful run at all** — "if none was parsed, say
so" applies to all four. `sirixdb/sirix` is the one exception: 10 runs that *concluded*
`success` at the workflow level nonetheless contain jobs with `fail`/`error` test outcomes
(matrix legs or steps that don't gate the overall run conclusion), ranging up to 1,245 distinct
failing/erroring tests in a single nominally-"successful" run — close to but under its
1,309-test pool. This is additional evidence for the same underlying fact: even the rare
"successful" runs that got parsed were only parsed because they contained failing jobs: no
run was ever parsed for the sole purpose of recording which tests passed.

---

## Phase 2 — Withdraw the Imbalance Figure

**2a.** `docs/phase/015B-REPORT.md` §5 marked `WITHDRAWN` in place, with the circularity
reasoning and a pointer to this report's §1. Nothing in that section was deleted — the
original query, range, and median remain on the page under the withdrawal notice.

**2b.** §6's verbatim datasheet limitation rewritten in place (original text preserved in git
history / superseded-inline). New text does not quote 1:35 or 1:1,707 as class imbalance:

> *"BR-Bench ships exclusively positive fault-revealing test execution outcomes (`status in
> ('fail', 'error')`), derived from parsing only the workflow runs that concluded with a
> failure or produced failing/erroring test jobs. The observed test universe
> (`candidates.parquet`, per repository and trailing observation window) is therefore built
> from the same failure-only slice as the positive labels: it contains no test ever observed
> passing, because passing-run logs were never parsed for test-level outcomes (of 117,923
> successful workflow runs in the harvested frame, job logs survive on disk for 10).
> Consequently, true class imbalance — the ratio of failing to passing test executions per
> candidate pool — is UNMEASURED by this project. ROADMAP §9.3 anticipates an expected
> imbalance on the order of 1:200–2,000 based on prior RTS literature, but BlastRadius has not
> parsed a corpus of passing runs sufficient to confirm, refute, or refine that figure, and no
> number purporting to state the imbalance should be read from this dataset as measured.
> Negative examples remain derivable rather than materialised: consumers reconstruct negative
> instances by taking the set difference between the full observed candidate test set in
> `candidates.parquet` and the positive failure set in `outcomes.parquet`, but should not
> assume the resulting ratio reflects the true skew of executed-test outcomes without
> independently sampling and parsing passing-run logs."*

---

## Phase 3 — What Would candidates.parquet Actually Cost? (Diagnosis Only)

**3a.** Of the 117,923 `run_conclusion == 'success'` runs recorded in `instances_raw.parquet`,
job-log files (`logs.jsonl.gz`) survive on disk in `data/raw/` for exactly **10** — all in
`sirixdb/sirix`, all Gradle. Breakdown by harness (harness inferred per-repo from
`parsed_outcomes.harness`; 17,999 success runs belong to repos with no parsed harness on
record at all):

| Harness | Success runs (distinct) | Have >=1 job log on disk |
|---|---:|---:|
| gradle | 33,021 | 10 |
| maven | 24,630 | 0 |
| pytest | 42,273 | 0 |
| unknown (repo never parsed) | 17,999 | 0 |
| **Total** | **117,923** | **10** |

**3b.** `candidates.parquet`, as specified in `docs/phase/015B-REPORT.md` §4 (a real
per-repo/per-window observed-test universe distinct from the failure set), **cannot be built
from what is on disk.** 10/117,923 (0.008%) is not a usable sample. It requires a new harvest:
fetching job logs for the successful runs' jobs that are not currently captured. Distinct
`job_id`s across all 117,923 success runs: **428,122** (mean 3.63 jobs/run). At one HTTP
request per job log (the only endpoint for job log bodies, per `get_with_backoff()`'s single
chokepoint) and the project's 3-token, 5,000 req/hr/token ceiling (15,000 req/hr pooled):
428,122 requests / 15,000 per hr ≈ **28.5 hours of pure request throughput**, before any
backoff, retry, or pagination overhead — realistically multiple days under D-22's transient
ladder and hostel-wifi conditions. This also **ignores an unrecoverable floor**: 24,490 of the
117,923 success runs (20.77%) already have `run_started_at` more than 90 days in the past as
of today (2026-09-01) — their job logs are permanently gone to the 90-day retention wall
(D-23/D-26) regardless of harvest speed, so even an immediate full-speed harvest cannot recover
more than ~79% of the success-run population. Separately, no parser in this codebase currently
extracts a "test ran / passed" record from a clean log — the parser suite was built and tuned
against failure extraction only (D-24); a pass-detecting parser is unbuilt work not included in
the above estimate.

**3c.** The honest alternative: define the candidate universe as the tests observed across all
*parsed* runs for a repo in the trailing window — i.e., exactly what `parsed_outcomes.parquet`
already contains, with no new harvest. This is cheap (it already exists) but it is **provably
identical in composition to the positive set** per Phase 1: it excludes every test that has
never failed in a parsed run, which for most repos is the overwhelming majority of the real
suite (§1d: `apache/beam`'s candidate pool tops out at 1,707 "tests" — all of them tests that
failed at least once — against a codebase whose real suite is certainly much larger). Any
negative set sampled from this universe is biased toward tests that are already known to be
flaky or fault-prone; it systematically excludes stable, reliably-passing tests, which is
exactly the population that should dominate a real negative set. A model or metric trained or
evaluated against negatives drawn this way will overstate performance relative to the true
candidate universe, because it never has to distinguish a genuine one-off failure from a
consistently-passing test — only from other tests that have also failed before.

**3d. Recommendation: ship without `candidates.parquet` as originally scoped, and document the
gap.** Reasoning: (1) disk cannot supply it (3a); (2) a harvest sufficient to supply it is a
new, multi-day-to-multi-week undertaking — new HTTP volume against a rate-limited pool, a
20.77%-and-growing floor of permanently-expired data, and an unbuilt "test passed" parser — that
was not scoped or budgeted anywhere in the current roadmap, and committing to it now risks the
5 Nov abstract / 10 Nov paper deadline (D-01) for a table whose only purpose was to support a
class-imbalance claim already withdrawn in Phase 2; (3) the D-43 negatives architecture
("consumers derive negatives from the observed universe") does not fail without it — it
degrades honestly to "derivable negatives are drawn from the fail-only observed universe,
explicitly flagged as biased," which is exactly what §6's rewritten datasheet paragraph and
§3c above already state in the datasheet. This recommendation changes nothing already built
and proposes no code. **STOPPING for approval — no further Phase 3 action taken.**

---

## Phase 4 — The Gate 1 Reading

Decision **D-44** appended to `docs/DECISIONS.md` (next free number — D-21 remains RESERVED
per prior rulings; D-33 is not free, it is an existing decision, referenced in
`docs/HANDOFF.md:432` and `docs/SCHEMA_CONFORMANCE.md:21`, simply absent from the condensed
table). Verbatim entry:

> ### D-44: Gate 1 reads against the label count, not the instance count
> **Context**: ROADMAP §37.1 states Gate 1 as ">=5,000 positives." Phase 014-A reported this
> against the strict-split instance count (778), reading Gate 1 as MISSED at 778/5,000.
> ROADMAP §9.3 step 6 defines the labelling grain explicitly: one row is emitted per
> (instance, candidate test) pair, label 1 if the test is in T_reveal. A positive, under that
> definition, is a (change, test) pair — a label — not an instance.
> **Decision** (Architect ruling, verbatim): "Gate 1's >=5,000 positives therefore reads
> against the label count, currently 4,194, not the instance count of 778. Gate 1 stands at
> 4,194/5,000, not met."

Documents corrected (non-destructively — original text preserved, correction appended
immediately below it) because they stated Gate 1 as 778:
- `docs/phase/014A-REPORT.md` (§5c)
- `docs/session/076-2026-08-31-014A-targeted-base-resolution-and-gate1.md`

No other document was found to state a Gate 1 *reading* of 778 (a `git status`-adjacent
false-positive check on `778` elsewhere in `docs/session/031-...md` and
`docs/session/032-...md` matched unrelated byte-rate and line-number text, not Gate 1).

---

## Phase 5 — Mark the Provisionals

PROVISIONAL banners added to the head of every document found quoting 778, 4,194, or 43.88%
(the Phase 014-A base-resolution / Gate 1 figures depending on `exact_green` semantics
currently under verification in 016-A). Nothing removed, no number changed:
- `docs/phase/014A-REPORT.md`
- `docs/HANDOFF.md`
- `docs/session/076-2026-08-31-014A-targeted-base-resolution-and-gate1.md`
- `docs/session/INDEX.md` (row 076's summary)

---

## Non-Goals Honoured

`src/`, `analysis/`, `tests/`, `Makefile`, `docs/SCHEMAS.md`, `docs/ROADMAP.md`, all parquet
files, and all repo-root files were not touched. No negatives were generated, no
`candidates.parquet` was built, no holdout v5 was sampled. No subagents, background tasks, or
heredocs were used. No git command beyond `git status`/`git config` (read-only) was run.
