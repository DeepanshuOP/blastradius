# Phase 018 Report — inclusion filter, fresh-clone green, sweep continuation

## Rulings applied

- **R1.** INVARIANT-6 is the headline; EVIDENCE-ONLY is retained only as the
  upper bound. `analysis/corpus_delta.py` prints both, INVARIANT-6 labelled as
  what the code produces.
- **R2.** Inclusion filter added — **but the evidence contradicts its premise,
  and it removes none of the 11.** See below.
- **R3.** `release/v0.1` untouched, still withdrawn.

---

## R2 — correction with evidence

**All 11 test-free-workflow instances in strict have `head_ran_tests == True`.**
The filter removes zero of them. Measured:

```
test-free workflow instances surviving into strict: 11
of those, head_ran_tests == True:  11
of those, head_ran_tests == False: 0
```

All 11 are **CodeQL** workflows, and their extracted identifiers are ordinary,
well-formed Java tests, not parser noise:

```
org.fife.ui.rsyntaxtextarea.HtmlUtilTest#testGetTextAsHtml_happyPath
com.thealgorithms.datastructures.caches.FIFOCacheTest#testEvictionListenerExceptionDoesNotCrash
com.webauthn4j.data.attestation.authenticator.EC2COSEKeyTest#json_serialize_deserialize_test
```

CodeQL's Java analysis **builds the project, and a Gradle or Maven build runs
the test suite.** Those heads really did execute tests. The defect was my
name-based census calling `CodeQL` "visibly test-free", not the corpus.

The ruling's principle — a run that executed no tests cannot yield a
fault-revealing label — is correct and is now enforced. It simply does not reach
these 11, because they executed tests. **Removing them would delete valid data.**
Awaiting your ruling; they remain in place.

---

## Phase 1 — Java sweep: INCOMPLETE, and here is the arithmetic

| | |
|---|---:|
| Base runs verified | **236 / 1,732 (13.6%)** |
| Instances covered | **796 / 4,245 (18.8%)** |
| Python | **167 / 167 (100.0%)** |
| Java | **69 / 1,565 (4.4%)** |

**Segment accounting (predicted failure 4, asserted before reporting):**

```
distinct verified base runs in checkpoint: 236
sum of per-segment counts:                 236  [47, 22, 31, 39, 39, 20, 22, 16]
ASSERT OK: cumulative == sum of segments (no boundary double-count or skip)
```

Resumption is sound. **The problem is throughput, not correctness.**

Measured Java rate: **16 base runs in 8.3 minutes = 1.9 runs/min**, against
Python's ~5. Java runs carry ~11 jobs each and their logs are large and mostly
retrievable, so the sweep is download-bound, not request-bound (189 requests in
8.3 min = 23 req/min, against a 250/min ceiling).

**1,496 base runs remain ≈ 13 hours of continuous fetching**, or roughly 85
further 10-minute segments. I did not spend that unattended. Options, your call:

1. **Grind it.** Correct, and it is the only thing that makes Phase 3 final.
2. **Probe-then-infer for expired runs.** If one job log of a run 410s, the whole
   run's logs are gone — retention is per-run. Probing one job instead of all
   ~11 would cut the ~35% of Java runs that are >90d to a single request each.
   Cheaper and defensible, but it makes `base_jobs_retrieved` an inference for
   those runs, so it would need its own `base_parse_status` value.
3. **Stop at Python + a Java sample** and publish Java as an extrapolation with
   a stated CI, as 016-A did.

I recommend 2, then 1 for the remainder.

### Predicted vs actual, Java-only (run-weighted, n=69)

Pre-registered before starting. Java is still only 4.4% swept, so treat as early.

| Java bucket | Predicted | Actual so far | Verdict |
|---|---:|---:|---|
| all jobs 410 → UNVERIFIABLE | ~45% | **too few to state** | pending |
| partial + no tests → UNVERIFIABLE | ~25% | rising: corpus-wide `no_tests_unverifiable` went 157 → **183** on 16 Java runs | **directionally confirmed** |
| retrievable + NO_TEST_OUTPUT → CONFIRMED | ~20% | 346 → **354** | pending |
| stays exact_green | ~10% | 210 → **210** (unchanged) | **directionally confirmed** |
| TEST_FAILURE | ~0.5% | 1 → **1** | pending |

The signal is real: of the 16 Java runs added, **26 instances went
UNVERIFIABLE and 8 CONFIRMED, and zero stayed green.** Predicted failure 1 is
tracking as stated, but I will not put a rate on 4.4%.

### Six fractions over the 796 instances verified so far

| Bucket | Fraction |
|---|---:|
| retrievable(all jobs) + TEST_RAN_CLEAN → stays | **163 / 796** |
| partial + tests found → stays | **47 / 796** |
| retrievable + TEST_FAILURE → `exact` | **1 / 796** |
| retrievable(all jobs) + NO_TEST_OUTPUT → demote, **CONFIRMED** | **354 / 796** |
| partial + no tests → demote, **UNVERIFIABLE** | **183 / 796** |
| all jobs 410 → demote, **UNVERIFIABLE** | **48 / 796** |

CONFIRMED **354 / 796**; UNVERIFIABLE **231 / 796**. Never summed.

---

## Phase 2 — inclusion filter

**2a.** `compute_labels` now excludes any instance whose head run parsed no
tests, counted as `head_no_tests_count`. It is a corpus-inclusion rule, distinct
from invariant 6, which governs the base side.

**2b. Instances removed corpus-wide: 5,684 / 12,581 (45.2%)** — well above the
620 the workflow-name census found, confirming your predicted failure 2. **The
three splits are unchanged (778 / 4,194):** none of the 5,684 ever produced a
label, so the filter is a no-op on the corpus and a correctness guard going
forward.

Top 10 workflow names among the removed:

| Workflow name | Removed |
|---|---:|
| PR Check | 320 |
| Validation | 222 |
| ci | 205 |
| Yetus JDK17 Hadoop3 Unit Check | 191 |
| Docs | 188 |
| Build | 173 |
| Java CI with Gradle | 166 |
| frontend | 162 |
| PR Lint | 147 |
| Clang format linter | 145 |

**Six of the top ten have test-suggesting names**, including `Yetus JDK17
Hadoop3 Unit Check` — the words "Unit Check" in the name of a workflow that
emitted no parseable test output. Written up in
`docs/phase/018-mining-pitfalls.md` as a §V finding: **a workflow's name
predicts nothing about whether it ran tests, in either direction.** That is a
sharper claim than "lint workflows pollute the corpus", and it is the one the
data supports.

**2c.** `tests/test_head_inclusion.py`, 3 tests against the real checked-in
`agno-agi/agno` log. Per the new AGENT_RULES rule, the zero is proved to be
measured: one test asserts the log genuinely parses to NO_TEST_OUTPUT, one
asserts the instance emits zero labels, and a third feeds the *same frames* with
one parsed test and asserts labels DO appear — so the zero cannot be an artifact
of the frame shape.

---

## Phase 3 — final numbers, INVARIANT-6 basis

**These are not final: the sweep is 13.6% complete.** Every INVARIANT-6 figure
is a floor that rises as Java completes. Stated with that caveat rather than
withheld.

| | INVARIANT-6 (headline) | EVIDENCE-ONLY (upper bound) | Supersedes |
|---|---:|---:|---|
| no_base rate | **9,554 / 12,581 (75.94%)** | 6,105 / 12,581 (48.53%) | 43.88% (014-A) |
| exact_green | **210** | 3,659 | 4,245 (016-A) |
| strict instances | **122** | 725 | 778 (014-A) |
| strict labels | **423** | 4,100 | 4,194 (D-44) |
| Gate 1 (labels, D-44) | **423 / 5,000 — NOT MET** | 4,100 / 5,000 — NOT MET | 4,194 / 5,000 |
| vs published 524 | **SMALLER by 402** (122 vs 524) | LARGER by 201 (725 vs 524) | 524 (007-B) |

One instance reclassified `exact_green` → `exact`: its base was never green.

---

## Phase 4 — fresh clone is green

**4b, done before the commit this time**, on an rsync of the working tree with
`data/` absent:

```
382 passed, 23 skipped in 50.07s
```

**Zero failures, zero errors.**

**4c. Skip reason distribution (23):**

| Reason | n |
|---|---:|
| `data/clones` (test_test_files) | 8 |
| four `data/interim/*.parquet` (test_fault_revealing) | 4 |
| `data/clones/castorini__anserini` (pre-existing skip) | 3 |
| `data/raw`, `data/clones` (test_base_resolve) | 2 |
| `data/interim/base_resolution_new.parquet` (+`instances_raw`) (test_promoted) | 2 |
| `data/raw` (test_changeset) | 2 |
| `data/interim` (test_scaffold) | 1 |
| `data/state` (test_promoted) | 1 |
| No GitHub PAT (pre-existing skip) | 1 |

Every message names the missing path and points at
`docs/DATA_DEPENDENCIES.md`. With `data/` present the suite is **405 passed, 0
skipped from these markers** — the markers are inert, not permanent.

**Predicted failure 3 — CONFIRMED, and it was worth checking.** One failure on my
first data-less run was *not* missing data:
`test_scaffold.py::test_env_file_is_gitignored_and_untracked` failed with
`git check-ignore exit 128: not a git repository`. That was an artifact of
copying the tree without `.git`, not a bug and not a data dependency — it passes
in a real `git clone`. **It is not marked skipif**, which would have hidden a
genuine gitignore regression.

---

## Phase 5 — AGENT_RULES

Appended, directly under Scope: **"A zero is not evidence until the counter has
been seen to increment."** Names all three defects — `created` with
`params=None`, the base-side conclusion filter, and the 410 counter behind an
unreachable branch — and requires proving the non-zero path is reachable before
reporting a zero.

---

## Hypothesis verdicts

1. **Java UNVERIFIABLE rate lands well above Python's.** — **DIRECTIONALLY
   CONFIRMED, rate withheld.** 16 Java runs produced 26 UNVERIFIABLE, 8
   CONFIRMED, 0 green. I will not quote a rate off 4.4% coverage.
2. **The filter removes more than 620.** — **CONFIRMED. 5,684**, 9× the census.
   And it removes them from the frame only: the splits do not move.
3. **Some fresh-clone failures are not missing data.** — **CONFIRMED, 1**, and
   deliberately left unmarked. Details above.
4. **Resumption double-counts or skips at boundaries.** — **REFUTED, asserted
   in code before reporting.** 236 == 47+22+31+39+39+20+22+16.
5. **(added) The head_ran_tests filter cannot remove the 11.** — **CONFIRMED.**
   All 11 have `head_ran_tests == True` because CodeQL builds run the suite. The
   ruling needs a different mechanism, or none.

---

## Git

Recorded below after the push.
