# Phase 014-A Final Report: Targeted Base Resolution & Gate 1 Impact

> **PROVISIONAL (Phase 016-B).** CLI-1 is verifying whether `exact_green` was assigned from
> run conclusion rather than from a parsed base log. 4,245 instances (60% of all resolved
> bases) depend on this semantic. Every figure in this report that depends on base-resolution
> status — including 778 (strict instances), 4,194 (strict labels), and 43.88% (`no_base`
> share) — is PROVISIONAL pending that verification (016-A). Nothing below has been changed;
> this banner only flags that these numbers may move. See also the D-44 correction on §5c
> (Gate 1 reads against the label count, not the instance count).

**Spec**: [CLI-1] — PHASE SPEC 014-A CONTINUED: Phases 2 through 7  
**Date**: 2026-08-31  
**Status**: COMPLETE  
**Governing Authority**: `docs/SCHEMAS.md` (FROZEN, Rank 1), `docs/ROADMAP.md` §21.3 & §37.1, `docs/AGENT_RULES.md`

---

## 1. Executive Summary & Verification Guard Confirmation
- **Agent Operating Rules**: Verified and applied in full (`docs/AGENT_RULES.md` sections: *STOP — a live process is running*, *Absolute prohibitions*, *Every session opens with this guard*, *Before any commit*, *HTTP*, *Running the harvester*, *Reporting — not optional*, *Documentation — write as you go, not at the end*, *Scope*, *When the instructions are wrong*, *No external sources*, *Session report naming*, *Delegation and Tool Usage*).
- **Session Guard Check**: `Linux` / `/home/shree/blastradius` / `Python 3.11.15`.
- **Git Identity Check**: `DeepanshuOP` / `99538840+DeepanshuOP@users.noreply.github.com`.

---

## 2. Phase 2: Restructure & Outgoing Parameters Test
- **Root Cause & Fix**: Restructured `analysis/resolve_bases.py` to correctly supply `params={"branch": branch, "created": f"<={day_str}", "per_page": 100}` on initial workflow run requests, and `params=None` on subsequent `Link` header pagination requests (preventing parameter duplication / omission). Added support for `limit`, `sample_100`, `python_first`, and graceful fallback.
- **Contract Test**: Added `test_resolve_bases_outgoing_params_and_pagination` in `tests/test_base_resolve.py` validating that outgoing query parameters and pagination link transitions match specification.

---

## 3. Phase 3: §21.3 Strict Commit Walk Survey & Bytechef Analysis
- **Bytechef Verdict**: Evaluated `bytechefhq/bytechef` candidate run (5 months older than head run). Candidate run is neither at `base_sha` nor reachable within the 10-ancestor commit graph walk. Result: **All 237 bytechef instances correctly resolved to `no_base` (NOT-A-BASE)**. Temporally prior runs without graph connectivity are strictly rejected per §21.3.
- **21-Group Sampled Survey Breakdown (1,255 instances, 99 requests)**:
  - `no_base`: 911 (72.59%)
  - `exact_green`: 208 (16.57%)
  - `exact`: 100 (7.97%)
  - `ancestor`: 36 (2.87%)
  - Distance distribution: d=0: 235, d=1: 34, d=2: 14, d=3: 15, d=4: 29, d=5: 3, d=6: 9, d=7: 1, d=8: 1, d=9: 2, d=10: 1.

---

## 4. Phase 4: Full Targeted Base Resolution (All 479 Groups, Python-First)
- **Ceiling & Prediction**:
  - Addressable Population: 5,281 of 7,891 unreached `no_base` instances (from 009-A).
  - **Predicted**: 27.0% of addressable (1,425 / 5,281) · 18.1% of total (1,425 / 7,891).
  - **Actual**: 2,371 resolved instances (**44.90% of addressable 5,281** · **30.05% of total 7,891**).
- **Execution Profile**:
  - Processed all 479 groups in Python-first order (25 Python groups, 454 Java groups).
  - Total requests: 1,353 requests.
  - Elapsed time: 4,203.68s (~70 min). Average rate: 19.3 RPM.
  - Output written to: `data/interim/base_resolution_targeted.parquet`.
- **Targeted Resolution Breakdown (7,891 instances)**:
  - `no_base`: 5,520 (69.95%)
  - `exact_green`: 1,319 (16.72%)
  - `exact`: 733 (9.29%)
  - `ancestor`: 319 (4.04%)
  - Distance distribution: d=0: 1,658, d=1: 263, d=2: 134, d=3: 68, d=4: 105, d=5: 34, d=6: 24, d=7: 21, d=8: 37, d=9: 17, d=10: 10.

---

## 5. Phase 5: Corpus-Level Re-resolution & Gate 1 Impact

### 5a. Updated Full Corpus Base Resolution (12,581 failed runs)
| Status | Before Targeted (007B) | After Targeted (014A) | Change (Instances) | Change (%) |
| :--- | :---: | :---: | :---: | :---: |
| `no_base` | 7,891 (62.72%) | **5,520 (43.88%)** | -2,371 | -18.84 pp |
| `exact_green` | 2,926 (23.26%) | **4,245 (33.74%)** | +1,319 | +10.48 pp |
| `exact` | 1,125 (8.94%) | **1,858 (14.77%)** | +733 | +5.83 pp |
| `ancestor` | 272 (2.16%) | **591 (4.70%)** | +319 | +2.54 pp |
| `branch_prior` | 367 (2.92%) | **367 (2.92%)** | 0 | 0.00 pp |
| **Total Resolved Bases** | **4,690 (37.28%)** | **7,061 (56.12%)** | **+2,371** | **+18.84 pp** |

### 5b. Dataset Split Trajectory
| Split | Instances (007B) | Labels (007B) | Instances (014A) | Labels (014A) | Distinct Tests (014A) | Growth |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **strict** | 524 | 2,912 | **778** | **4,194** | 2,485 | **+48.5% instances / +44.0% labels** |
| **relaxed** | 529 | 2,949 | **787** | **4,241** | 2,503 | **+48.8% instances / +43.8% labels** |
| **all** | 656 | 3,119 | **914** | **4,411** | 2,519 | **+39.3% instances / +41.4% labels** |

### 5c. Effect on Gate 1 (>=5,000 Positives, ROADMAP §37.1)
- **Gate 1 Status**: Gate 1 threshold of >=5,000 positive instances remains **MISSED at 778**.
  - **CORRECTION (Phase 016-B, D-44)**: This reads Gate 1 against the instance count. ROADMAP §9.3 step 6 defines the labelling grain as one row per (instance, candidate test) pair — a positive is a label, not an instance. Gate 1 correctly reads against the label count: **MISSED at 4,194 / 5,000**, not 778. See D-44 in `docs/DECISIONS.md`.
- **Impact Analysis**: The targeted base resolution increased strict positive instances from 524 to 778 (+254 instances / +48.5% increase) and fault-revealing labels from 2,912 to 4,194 (+1,282 labels / +44.0% increase). While Gate 1 is not met in absolute count, the effective statistical power of BR-Bench is increased by ~48.5% with zero degradation to integrity invariants.

---

## 6. Phase 6: Date-Slice Recursion Depth Bound
- **Recursion Guard**: Added an explicit recursion depth tracking `depth` to date-slice subdivision in `capture_branch_runs` in `src/harvest/daemon.py`. When subdivision reaches `depth >= 5` with `total >= 1000`, it explicitly RAISES a `RuntimeError`.
- **Unit Test**: Added `test_capture_branch_runs_depth_bound_raises` to `tests/test_daemon.py` verifying that depth overflow raises rather than subdividing infinitely.

---

## 7. Phase 7: Test Suite & Non-Goals Discipline
- **Non-Goals Honoured**:
  - `base_ref`, `job_ids`, and `job_conclusions` were NOT removed or modified in any parquet table.
  - No subagents or background tasks were used.
  - No heredocs used; throwaways confined to `/tmp`.
  - No modifications made to test fixtures to force pass.
- **Test Suite Results**:
  - Total collected: 381 items.
  - **Passed: 380 | Skipped: 1 (PAT integration) | Failed: 0**.
