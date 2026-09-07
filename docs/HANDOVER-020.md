# BlastRadius — Handover to a New Architect Chat (HANDOVER-020)

**ERRATA (verified against disk, 2026-09-07):**
a. §13's commit table is not chronological and its HEAD line is wrong. Reflog order is
   495e23f2 → db19c577 → 4ba2d648. HEAD is 4ba2d648.
b. §7's vendor/graphify-br box is CONFIRMED correct: 803/803 files tracked flat, no gitlink,
   VENDORED.md records upstream SHA 0738af373af9cf5c95f862cc5f3327fd96b4ea23. A fresh clone
   reproduces it with no network access to upstream.
c. data/interim/CORPUS_PIN.json records git_head_sha 22de7a30 and a 2026-09-02 run window,
   superseding 86043aee and the 2026-08-29 window. as_of (2026-08-29T14:13:00Z) and file_count
   (12,072/12,072) are unchanged — the corpus did not move, only the code provenance did.

**Written:** 6 September 2026
**Operator:** Deepanshu (23BIT0264, GitHub `DeepanshuOP`) · **Repo:** `/home/shree/blastradius` (WSL2 Ubuntu)
**Repo HEAD at writing:** `db19c577a2ddad92b29cfed9a7d11ef17d8d864d`

Read this whole document before writing a prompt. It is written so a chat with no prior
context can take over mid-flight. **Every number here carries a status. Take none of them as
settled unless it says so.**

This document is **rank 6** in the source-of-truth hierarchy (§9). It loses to every governance
file in the repo, including where it contradicts them. The previous handover document was wrong
twice on figures that were then quoted forward for weeks — assume the same of this one and
verify against disk before shaping any prompt.

---

## 0. IMMEDIATE STATE — read this first

There is **one live blocker** and it is an instrument defect, not a data problem.

Holdout v5 was scored on 4 September and returned **precision 10/41 (24.39%), recall 10/22
(45.45%)**. **That number is not a parser precision measurement and must not enter the paper,
a slide, or a viva answer.**

Why: the blind worksheet showed the operator an *excerpt* of each log, while the parser read the
*whole* log. The two sides were given different inputs, so the disagreements measure the excerpt
window, not parser accuracy. The scoring agent's own report states it: *"Operator blind worksheet
excerpts omitted preceding failure lines for #1, 3, 15, 16, 17, 19, 20, 29, 35."*

Three separate contaminations stack in that score:

1. **Clipped excerpts** — 9 sections where the operator wrote `NO_TEST - failure count only, no
   test named`, correctly for what he was shown, while the parser found failure lines elsewhere
   in the log.
2. **A wrong mapping rule from the Architect** — Rule A forced `NO_TEST_OUTPUT` on sections
   36–40, which had actually run clean (`TEST_RAN_CLEAN`). The operator had even noted "zero
   failures/errors". This alone produced 5 false classification failures.
3. **A D-32 inversion** — rows 2, 4 and 6 were ruled OPERATOR WRONG for writing `test_modeling`
   where the extractor emitted `test_modeling[...]`. **D-32 says the canonical id strips the
   parameter set.** The operator was right; the ruling was backwards.

**Ruling in force: no measurement occurred.** This is the same category as holdout_v4's void
under D-38 — an instrument that never measured, not a disappointing result. **D-37 is therefore
NOT breached and v5 is NOT burned.** D-37 protects against a corpus being scored, used to tune
the parser, then re-scored. Nothing was tuned. The corpus may be re-scored once the instrument
is rebuilt.

**Two genuine parser findings survive the score and should be kept:**

| Finding | Evidence |
|---|---|
| Flink syslog prefix (`Jun 08 13:56:54 FAILED …`) masks the failure from the pytest parser | v5 section 8, L18187 |
| sirixdb FQCN appears only on a `FAILED-TEST:` line, which is not one of D-39's three package sources | v5 section 18, L19160 |

Neither has been fixed. Both are recorded, not repaired — fixing a parser on evidence drawn
from v5 *would* convert it to a development set and destroy it permanently.

**First action for the new chat:** rebuild the v5 worksheet so each fixture's excerpt contains
every failure line in that log, have the operator complete the ~15 affected sections, then
re-score once. Detail in §10 Step 1.

---

## 1. What this project is

**BR-Bench** is an execution-grounded dataset linking code changes to the individual tests that
*actually failed* in GitHub Actions CI, plus a measurement of how far co-change and
static-reachability proxies diverge from that reality.

**Course:** BITE497J Project I, School of Computer Science Engineering and Information Systems,
VIT, Fall 2026–27. Approved title at Zeroth Review (16-07-2026): *BlastRadius: Graph-Based
Change Impact Prediction and Dependency Analysis for Software Repositories*.

**Target venue:** MSR 2027 Data & Tool Showcase — abstract 5 Nov 2026, paper 10 Nov 2026,
4pp + 1pp refs, single-anonymous, Dublin, co-located with ICSE 2027.

**The contribution is the dataset and the measurement, not a model (D-02).** A predictor that
loses to historical-frequency is still a publishable finding. Never let a prompt, a slide or a
paragraph quietly re-frame this into a SOTA claim.

**Explicitly not:** a safe RTS tool (no safety claim, §17.1), a TypeScript project (D-03, cut),
a cross-repo tool (§44, deferred), or anything with an LLM in the reproducible core (D-17).

### Team

| Person | Owns |
|---|---|
| **Deepanshu** (23BIT0264) | Phases 0, 1, 4 — the entire critical path |
| **Prisha Vadhavkar** (23BIT0010) | Graph layer (§10) and tool/demo (§13) — **both cut from this submission**, handover pending |
| **Sanskriti Singh** (23BIT0256) | Parsers, measurement, literature |
| **Dr. Yoga Raja C A** | Faculty guide — **briefing overdue by many weeks** |

### Two deadlines, and they are different deliverables

- **VIT submission: ~10–12 days out.** A report and a viva. This is the binding near-term
  constraint.
- **MSR: 5 November abstract, 10 November paper.** Two months out. Not urgent.

Do not compress the MSR work to fit the VIT date. They are separate artifacts.

---

## 2. Roles and the loop

| Role | Who | Job |
|---|---|---|
| **Architect** | The chat (you) | Decide *what* is built next and *how it will be proven*. Never write production code. |
| **Hands** | Claude Code / Antigravity CLI (WSL2) | Execute one scoped, testable spec. Never decides scope. |
| **Operator + quality gate** | Deepanshu | Run the prompt, paste RAW output, verify personally, authorise commits. |

**The loop:** Architect plans → Operator pastes → agent builds → Operator pastes raw output →
Architect reviews and rules → next prompt.

The failure this structure exists to prevent: an agent fully *capable* of the task but
*unscoped*, producing plausible output nobody verified. **Roughly twenty fabrications and
instrument defects have been caught this way.** Prose summaries have repeatedly let fabrications
through. Raw output is non-negotiable.

### Tooling as of this handover

- **Claude Code** (Opus 5 / Sonnet 5) in WSL2. Launch:
  `cd /home/shree/blastradius && claude --permission-mode acceptEdits`
  `acceptEdits` is correct — file writes are automatic, bash still prompts, so `git commit`
  stays an operator gate. Set `"includeCoAuthoredBy": false` in `.claude/settings.json`.
- **Antigravity CLI** (Gemini Flash). Thinner reporter: cites line numbers instead of function
  names, summarises where raw output was demanded. Its harness **auto-backgrounds commands past
  a ~10 s tool timeout** — this is not a deliberate background invocation but must be disclosed
  in every report. Prefer Claude Code for anything irreversible.
- **Antigravity remote control: tested and rejected.** It cannot reach `uv` on its PATH and did
  not respect working-tree isolation. Terminal only.
- If Claude Code is launched from a Windows-side VS Code window it inherits a Git Bash shell
  reaching WSL2 ext4 over `\\wsl.localhost`, causing CRLF corruption and root-owned files. The
  badge must read **`WSL: Ubuntu`**.

### Parallel sessions

Two CLI sessions may run **only** on strictly disjoint file sets, with one designated git owner
per round. This has already produced one near-miss: two sessions held different snapshots of
`src/` and `tests/`, so one reported `XPASS(strict)` while the other reported `AttributeError`
for the same field. **Never run a second session against a tree where another is mid-edit.**

---

## 3. Where the project stands

### 3.1 Corpus

| Figure | Value | Status |
|---|---|---|
| Failed runs in frame | 12,581 | settled |
| `exact_green` instances under verification | 4,245 over 1,732 distinct base runs | settled |
| **Base runs verified** | **265 / 1,732** | settled, post-quarantine |
| **Instances verified** | **859 / 4,245** | settled, post-quarantine |
| Python arm | 167 / 167 base runs | complete |
| Java arm | ~108 / 200 sample target | **incomplete, and I recommend leaving it so — see §10** |

Post-quarantine status distribution (859 verified instances):

```
no_tests_confirmed       360
no_tests_unverifiable    184
green_verified           178
unretrievable             77
green_verified_partial    53
inferred_expired           6
base_failed                1
```

**Quarantine record.** Two rounds of unattended verdicts were removed. Total quarantined:
**550 instances over 370 base runs** — this **supersedes `HANDOFF-019.md`'s "375"**, which was
never correct. The second round removed 19 instances over 10 base runs written *after* the first
quarantine by a killed background process. Evidence preserved at:

- `data/interim/exact_green_verification_unattended_backup.parquet` (pre-round-1 state)
- `data/interim/exact_green_verification_pre019b_snapshot.parquet` (pre-round-2 state)
- `data/interim/exact_green_verification_unattended_round2_removed.parquet` (the 19 rows)

RawStore log bytes were **kept** in all cases — a 200 with a body is a real log; only the
classification was in doubt.

### 3.2 The two scenarios

| | **INVARIANT-6 (headline)** | EVIDENCE-ONLY (upper bound) |
|---|---:|---:|
| `no_base` rate | 9,554 / 12,581 (75.94%) | 6,105 / 12,581 (48.53%) |
| `exact_green` | 210 | 3,659 |
| **strict instances** | **122** | 725 |
| **strict labels** | **423** | 4,100 |
| Gate 1 (labels, D-44) | 423 / 5,000 NOT MET | 4,100 / 5,000 NOT MET |

**INVARIANT-6 is what gets reported.** EVIDENCE-ONLY leaves 3,483 unswept instances sitting at
`exact_green` on run conclusion alone, which is precisely the assumption ROADMAP §21.3 forbids.
It is not a scenario; it is the old bug wearing a label. Keep it only as a stated upper bound.

**Unresolved and needs an Architect ruling: `778` vs `122`.** The figure 778 still appears in
`CURRENT-STATE.md`, `DECISIONS.md`, `HANDOFF.md`, `HANDOFF-019.md`, `009B-REPORT.md`,
`014A-REPORT.md`, `016A-REPORT.md`. It was deliberately left untouched during the stale-figure
sweep because it turns on the INVARIANT-6 ruling, not on a find-and-replace. **Rule on it before
§III is drafted.**

### 3.3 Parsers — all four defects fixed

| # | Defect | State |
|---|---|---|
| D1 | pytest retains the parameter set in the canonical id | **Not a dataset defect.** `normalize_test_id()` already strips params — 0 / 20,451 stored ids contain `[`. Exposure was confined to the holdout-scoring path, which bypasses the normalizer. |
| D2 | Gradle `Gradle suite` chevron mis-segmentation; `normalize_test_id` returned `None` and the outcome was **deleted** | **FIXED.** Wrapper segments stripped from the front by exact string equality; single remaining segment split at the last dot with a three-condition guard. |
| D3 | Java package dropped | **FIXED.** Three-source recovery per D-39: report header / `Running <FQCN>` line → `at` stack frame → bare. Never guesses. |
| D4 | Maven FORM A splits a class-level failure at the last dot, producing package-as-class | **FIXED** under D-46, via a structural `--` separator rule plus `at`-frame corroboration. |
| — | JUnit4 synthetic `classMethod` descriptor emitted as a test id | **FIXED** under D-46, exact string equality. |

**A rule I got wrong, recorded so it is not reintroduced.** The first D4 fix used
"a method name starts lowercase" as the guard. That is a convention, not a rule — it suppressed
`org.unicode.cldr.unittest.TestShim#TestAll`, a real method with a stack frame at
`TestShim.java:41`. **Capitalisation is never evidence.** The replacement uses Surefire's own
formatting (`--` separator present = method-level) plus `at`-frame corroboration, and positive
evidence of a method always wins over an inference of absence.

Post-fix corpus figures, measured over all 12,072 logs in five foreground segments:

| Figure | Value | Supersedes |
|---|---|---|
| Distinct `test_id` total | **5,985** | 6,014 |
| Distinct Java | **5,115** | 5,144 |
| Distinct Python | **870** | **151 — which has NO on-disk provenance anywhere and must never be quoted again** |
| Outcome rows | **20,451** | 20,535 |
| Bare-class Java ids | **2,043 / 5,115 (39.94%)** | 2,067 / 5,144 |
| `fqcn_recovered_count` | 6,230 | — |
| `fqcn_incomplete_count` | 13,182 | — |
| `class_level_events_suppressed` | 137 | — |
| `chevron_unsegmentable_count` | 0 | — |

The distinct-id *drop* is D3 working as intended: previously-split bare/qualified pairs collapsed
onto one real id.

**A paper finding, not a defect:** `fqcn_incomplete` exceeds `fqcn_recovered` by roughly 2:1.
Residual fragmentation is an **absence of package evidence in the logs**, not a parser
limitation. Say so in §V.

### 3.4 Binding rate — D-47, two numbers, never one

| Figure | Value | Supersedes |
|---|---|---|
| Combined binding | **5,622 / 5,985 (93.93%)** | 5,629 / 6,014 (93.60%) |
| Full confidence (FQCN) | **3,819 / 5,985 (63.81%)** | — |
| 0.5 confidence (basename-only) | **1,803 / 5,985 (30.13%)** | — |
| `not_found` | 199 / 5,985 (3.32%) | 218 / 6,014 |
| `ambiguous` | 164 / 5,985 (2.74%) | 167 / 6,014 |

**Gate 1.5 (binding ≥70%, ROADMAP §37.1) is met on the combined figure and NOT met on the
full-confidence subset alone.** Report both, always, in exactly those terms. This is a material
caveat and must not be smoothed over.

### 3.5 Holdout corpora — there is still no valid held-out precision figure

| Corpus | Figure | Status |
|---|---|---|
| `tests/fixtures/holdout/` (20 logs) | 100.00% / 100.00% | Ground truth **hand-written and valid**, but the corpus drove three parser fixes diagnosed from its own failures and `test_holdout_eval.py` pins parsers to its ids. **Permanently a development set under D-37.** The 100% is a fit number. Trajectory: 29.73% → 45.95% → 100.00%. |
| `holdout_v3` first scoring | 83.87% / 55.32% | Honest and held out, but **measures a parser that no longer exists** after the September fixes. |
| `holdout_v3` second scoring | 95.74% | NOT held out — the fixes were informed by auditing it. |
| `holdout_v4` | 58.33% | **VOID (D-38)** — ground truth machine-derived by `build_holdout_v4.py`. |
| **`holdout_v5`** | 24.39% / 45.45% | **INSTRUMENT DEFECT — no measurement occurred.** See §0. Corpus not burned; re-scorable once rebuilt. |

**`HANDOFF.md` recommends 83.87% for paper §III in four separate places (lines 208, 212, 344,
712). `DECISIONS.md` D-31 says no precision claim may reach §III until a fresh quarantined
corpus is scored. DECISIONS.md is rank 3 and HANDOFF.md is rank 6 — D-31 wins.** No precision
figure enters the paper until v5 is rebuilt and re-scored.

### 3.6 Health

| | |
|---|---|
| Test suite | **463 passed, 1 skipped, 0 failed** |
| `tests/test_parser_regression.py` | 47 passed, `KNOWN_DEFECTS` empty (all pinned defects fixed and unpinned) |
| `tests/test_test_ids.py` (frozen contract) | 50 passed |
| HTTP | 325,065 / 326,279 requests returned 200 (99.63%). Rate limiting has never been a real constraint |
| `data/raw` | **2.73 GB apparent content / 4.9 GiB on disk**, 304,534 files — irreplaceable, 90-day expiry |
| `data/state/cursor.db` | 131 MB, irreplaceable |
| `data/interim` | 33 MB, regenerable from `data/raw` |
| `vendor/graphify-br/` | 31 MB, **now committed** at upstream SHA `0738af373af9cf5c95f862cc5f3327fd96b4ea23` |
| `tests/fixtures/` | 147 MB, tracked |

**The two size figures are both correct and measure different things.** 2.73 GB is apparent
content (use for transfer sizing); 4.9 GiB is disk-block usage inflated by 304,534 small gzipped
files (use for destination free space). One report paired them as a single figure; they differ
by nearly 2×. Never quote one alone.

---

## 4. Rulings in force

1. **INVARIANT-6 is the headline scenario.** EVIDENCE-ONLY is a stated upper bound only.
2. **The 11 CodeQL instances stay in strict.** CodeQL's Java analysis builds the project and a
   Gradle/Maven build runs the suite. All 11 have `head_ran_tests == True`.
3. **The 5,684 `head_ran_tests` removals are a correctness guard, not a corpus correction.** None
   ever produced a label. Never write it up as shrinking the dataset.
4. **`release/v0.1` remains WITHDRAWN.** No Zenodo DOI minted, so D-08's one-way naming
   constraint has not fired.
5. **Negatives are derivable, not materialised (D-43).** `candidates.parquet` is blocked — only
   10 of 117,923 successful runs have logs on disk. **Ship without it and document the gap.**
6. **True class imbalance is UNMEASURED.** The earlier 1:82.5 and 1:35 figures were circular and
   are withdrawn. Do not resurrect them.
7. **`SCHEMAS.md` is frozen (D-42)** and never edited to match what was built. Divergences go in
   `SCHEMA_CONFORMANCE.md`.
8. **Gate 1 reads the label count, not the instance count (D-44).** 423 / 5,000 under INVARIANT-6.
9. **The canonical Java separator is `#`, not `::`.** `SCHEMAS.md`'s `"module::class::method"` is
   a description-column gloss that matches no Java id and is internally inconsistent. ROADMAP
   §9.1 T1.1 subtask 3 gives `com.foo.BarTest#testBaz` in prose, and the frozen contract test
   asserts `#` in every Java case. **D-39's `'::'` is amended to `'#'`; the rest of D-39 stands
   verbatim.** Recorded as a divergence in `SCHEMA_CONFORMANCE.md`; `SCHEMAS.md` not edited.
10. **`fqcn_incomplete` is NOT added as a field.** The existing `is_fqcn_qualified` serves as its
    logical inverse. A new column would carry zero information beyond a negation and would force
    an edit to a frozen schema.
11. **Class-level events are counted, never silently dropped (D-46).**
12. **The binding rate is two numbers, never one (D-47).**

### Decision records

**D-01 … D-47.** `D-21` is **RESERVED** for `parent_run_id`-from-`details_url` and must never be
filled or renumbered. `D-33` is absent from `DECISIONS.md` and exists only by reference in
`HANDOFF.md:440` (PyDriller → blobless clone deviation).

Recent: D-45 secret-scan tiering · **D-46** class-level events · **D-47** binding rate split.

**Note for the next chat:** `HANDOFF-019.md` claimed the last record was D-44. It was D-45. An
agent correctly stopped rather than renumbering. Verify the highest record on disk before
appending anything.

---

## 5. Known failure modes — the catalogue

This is the most valuable section. Every entry was found in production code, and most produced
numbers that were reported before being caught.

### 5.1 The signature failure: a zero produced by unreachable code

`AGENT_RULES.md` states it as **"a zero is not evidence until the counter has been seen to
increment."** Six instances now:

| Defect | Effect |
|---|---|
| `params if 'created' in url else None` — always False on a bare endpoint | Every first request sent `params=None`, fabricating a 3.9% resolution rate that was reported as a finding |
| Base-side `if job.get("conclusion") != "failure": continue` | An `exact_green` base has `conclusion == "success"`, so **zero jobs were ever parsed** for all 4,245. Would have demoted 27.7% of the corpus on an artifact |
| `get_with_backoff()` raises on non-retryable 4xx | Every `status_code == 410` branch was dead code; the 410 counter read zero by construction |
| `per_page=100` with no page turn | Any run with >100 jobs silently truncated |
| **`secret_scan.py` reads only `.parquet` / `.csv`** | Scanning 32 `.txt` fixtures reported `BLOCKER: 0, REVIEW: 0` — scanning nothing. Extended for `.txt` later; **still returns 0 files on `vendor/`** |
| **`chevron_unsegmentable_count == 0` corpus-wide** | Branch unproven by real data; a synthetic test now drives it |

### 5.2 Silent semantic errors

- **`exact_green` from `conclusion == "success"` alone**, never parsing a base log. ROADMAP
  §21.3's "single most dangerous bug in the labelling engine."
- **A workflow's name predicts nothing about whether it ran tests, in either direction.**
  `Yetus JDK17 Hadoop3 Unit Check` emitted no parseable test output; CodeQL runs a full Java
  build including the suite. **This is a genuine paper finding for §V**, written up in
  `docs/phase/018-mining-pitfalls.md`.
- **A third log category beyond clean-vs-miss:** a runner-provisioning log that never reaches a
  test framework at all. Also §V material.
- **Circular measurement.** Class imbalance was measured against a candidate universe built from
  failing runs only. Always ask what the denominator was built from.
- **Capitalisation is not evidence.** See §3.3.
- **`secret_scan.py`'s `bearer_token` pattern matches the English phrase "Bearer token"** in
  documentation and would fire a false BLOCKER on any prose file. Unfixed.

### 5.3 Agent behaviours to watch for

- **Group-weighted fractions presented as headline rates.** 20% of groups was 3.9% of instances.
- **Prose substitution** — "the fractions are detailed in the report" instead of the numbers.
- **Unrequested scope.** An agent filled all 47 rows of a worksheet the operator was to fill
  blind — and disclosed it, which is the only reason the round was salvageable.
- **Self-agreement presented as validation.** That same agent's 45 agreements were worthless; only
  its 2 disagreements were evidence.
- **Silent truncation proposed three separate times** in base resolution. Never approve.
- **Background execution.** Prohibited, violated twice, crashed the VM once. Name `nohup`,
  `setsid`, `&` and async subagents explicitly in every prompt.
- **Amending a fixture to make a parser pass.** D-27: amendments require evidence independent of
  any BlastRadius extractor.

### 5.4 Architect failure modes — mine, recorded so they are not repeated

- **Anchoring the instrument.** I asked for a diff script to be run against an unfilled blind
  worksheet, which printed the parser's answer for all 47 rows to the operator before he filled
  it. Mitigated by re-keying and shuffling; the corpus is labelled FITTED, not blind.
- **The v5 excerpt window.** My worksheet spec said "raw evidence lines verbatim" and never
  required the excerpt to contain every failure line in the log. This is the §0 blocker.
- **A wrong rule from convention.** The lowercase-method guard (§3.3).
- **A placeholder left unfilled in a pasted prompt.** An agent correctly stopped rather than
  guessing, preserving the corpus.
- **Bad predictions stated as fact.** I predicted a quarantine count that was arithmetically
  impossible, and a `git status` of exactly one line when three directories were already
  untracked.

**Pattern:** every one of these produced a plausible number rather than an error. Predict before
measuring, and check the prediction's arithmetic before running.

### 5.5 Environment traps

- Windows sleep must be **Never** (`powercfg /change standby-timeout-ac 0` — already set).
- Never `rm -f logs/daemon.lock` while a daemon is alive; the flock is on the inode.
- `.gitattributes` enforces LF on source and pins all CSVs as binary (`*.csv -text`) to preserve
  `frame_v1` sha256 determinism.
- Check `df -h /mnt/c`, never `df -h /`.

---

## 6. The daemon

**It is off, and it should stay off.** Three reasons: it holds `logs/daemon.lock` via
`fcntl.flock` and two SQLite writers on one WAL cost a session; it runs `stage="all"` which
includes the cancelled `capture_branch_runs()`; and the corpus is pinned at
`2026-08-29T14:13:00Z`, so fresh captures are excluded from every paper number.

**§6.2 of the previous handover — "Python is thin because D-32 was never implemented" — is
FALSIFIED.** Distinct Python ids are 870, not 151, and params were already stripped in storage.
**No re-harvest is justified on that rationale.**

Safe read-only check:

```bash
cd /home/shree/blastradius
ps -eo pid,etime,rss,cmd | grep -E 'harvest.daemon|run_supervised' | grep -v grep || echo "(no daemon — correct)"
ls -la logs/daemon.lock logs/supervisor.pid 2>/dev/null || echo "(no lockfiles — correct)"
```

---

## 7. Prisha's handover

### What she gets

**The graph layer (ROADMAP §10).** It is her roadmap role, it is cut from this submission, and it
is cleanly separable — she builds against a frozen dataset while Deepanshu finishes the paper,
and nothing she does can break the numbers. The tool/demo (§13) is the alternative.

**Do not hand over the labelling engine or base resolution.** Those carry integrity invariant 6,
and a handover mid-change is exactly how an empty base failure set gets silently treated as a
green base.

### Transfer

| Path | In git? | Regenerable? | Action |
|---|---|---|---|
| `data/raw/` (2.73 GB apparent / 4.9 GiB disk) | No | **NO — 90-day expiry** | Physical copy |
| `data/state/cursor.db` (131 MB) | No | No | Copy — required for `--as-of` |
| `data/interim/*.parquet` (33 MB) | 3 PIN files tracked | Yes | Copy anyway, saves an hour |
| `data/clones/` | No | Yes | She re-clones |
| `data/frame/` (9 files) | Yes | Frozen under T0.8 | Nothing |
| `vendor/graphify-br/` (31 MB) | **Yes, now** | Yes | Nothing |
| `.env` (3 PATs) | No | **She generates her own** | Never send Deepanshu's |

### Status

- [x] `vendor/graphify-br/` committed at pinned SHA — the artifact is now reproducible from a clone
- [x] `tests/fixtures/holdout_v4/` committed (secret-scanned, 0 BLOCKER)
- [x] All four parser defects fixed — she inherits a correct `test_id`
- [x] `docs/HANDOVER-PRISHA.md` and `docs/phase/025-transfer-manifest.md` written from measurement
- [x] `REPRODUCE.md` blockers fixed and re-walked (missing `--env-file`, inverted step order,
      unstated data prerequisites)
- [ ] **Physical data transfer — not started. This is wall-clock time that cannot be compressed.**
- [ ] Prisha has push access and her own three PATs
- [ ] **Her repo-local git identity configured** — the global config routes commits to a
      different GitHub account ("deepanshupatel") and has already bitten this project
- [ ] She runs `docs/REPRODUCE.md` end to end with Deepanshu watching
- [ ] `docs/TASKS.md` reconciled — rank 4 and **materially misleading**; see §8

---

## 8. TASKS.md is stale and misleading

Reported in `docs/phase/022-REPORT.md`, not yet fixed. Five divergences:

1. `T1.1e` and `T1.1f` ticked `[x]` while carrying confirmed defects (now fixed, but the ticks
   predate the fixes).
2. `T1.1a` claims a "40-log fixture corpus with hand-labelled expected output." The corpus is
   32 fixtures / 47 rows and its labels were **agent-filled**, not hand-written.
3. `T1.1b` (`annotations.py`) and `T1.1c` (`junit_xml.py`) are ticked but **neither file exists**.
4. `T1.1i` is `[ ]` for the wrong reason — the blocker is corpus provenance, not effort.
5. `src/parse/dispatch.py` — the cascade the whole parser layer routes through — **has no subtask
   line at all.**

---

## 9. Source-of-truth hierarchy

Rank is absolute. Conflicts resolve without debate.

```
1. docs/SCHEMAS.md    — FROZEN. Wins on any field, type or key. Changing it is an escalation.
2. docs/ROADMAP.md    — 48 sections. Wins on what to build, why, and how it is proven.
3. docs/DECISIONS.md  — D-01…D-47. Wins on choices already made.
4. docs/TASKS.md      — live burn-down. Wins on what is DONE. Currently stale (§8).
5. CLAUDE.md / docs/AGENT_RULES.md / AGENTS.md — condensed extracts. Lose to their sources.
6. Any chat summary, including this document and docs/CURRENT-STATE.md. Loses to everything.
```

**Cite ROADMAP section numbers in prompts. If you cannot cite one, you are inventing.** Re-read
the section rather than working from a summary — including this one.

### Where things live

| | |
|---|---|
| Governance | `docs/ROADMAP.md`, `SCHEMAS.md`, `DECISIONS.md`, `AGENT_RULES.md`, `AGENTS.md`, `SCHEMA_CONFORMANCE.md` |
| Consolidated map | `docs/CURRENT-STATE.md` — rank 6, generated 4 Sept, already partly stale |
| Phase reports | `docs/phase/NNN-REPORT.md` — 009B through 028 |
| Parser defects | `docs/phase/012B-parser-defects.md` (D1–D4) |
| Findings for §V | `docs/phase/018-mining-pitfalls.md` |
| Scorer provenance | `docs/phase/027-scorer-provenance.md` |
| v5 score (defective) | `docs/phase/028-holdout-v5-score.md` |
| v5 worksheet | `docs/phase/024-holdout-v5-worksheet.md` |
| Void evidence | `docs/phase/VOID-011B-*` — never quote as measurement |

---

## 10. The critical path

In order. Nothing later is unblocked by skipping something earlier.

### Step 1 — Rebuild the v5 instrument and re-score ← **THE BLOCKER**

1. Regenerate `024-holdout-v5-worksheet.md` so each fixture's excerpt contains **every failure
   line in that log**, not a window. Preserve the existing content-hash keys so completed
   sections carry forward.
2. Operator completes only the affected sections (~15, chiefly 1, 3, 15, 16, 17, 19, 20, 29, 35,
   plus 36–40's classification). **Operator-filled, blind, no agent.**
3. Fix the mapping rules before re-scoring: `TEST_RAN_CLEAN` where tests ran and none failed
   (36–40 included), and **D-32 governs parameter stripping — a hand answer without `[params]`
   is correct, not wrong.**
4. Re-score once. Record the two genuine parser findings from §0 as defects; **fix neither until
   after the score.**

### Step 2 — Re-derive RQ1

`docs/phase/009B-REPORT.md`'s Axis-1 and Axis-2 tables are marked STALE. RQ1 runs **last**, after
labels stop moving. Predict every figure before running.

### Step 3 — Paper §III

With: corpus size, `no_base` rate with the CONFIRMED/UNVERIFIABLE split (**never summed** —
they are different epistemic claims), a genuinely held-out post-fix precision figure, the D-47
binding split, and the RQ1 divergence measurement.

### Deliberately cut, and why

- **The gold subset (§21.5).** 72–120 machine-hours of Docker re-execution. It is the strongest
  answer to "your labels are observational" and it does not fit. Report the limitation in §VI.
- **Completing the Java sample.** 92 base runs of attended sittings to confirm a directionally
  certain result — 16 Java runs produced zero green bases. Report Python as measured in full,
  Java as a partial sample with Wilson 95% CIs and a stated n.

### Standing operator items, no agent needed

- **Message Dr. Yoga Raja C A.** Overdue by weeks. The update is genuinely good.
- **Start the physical data transfer.** Wall-clock that cannot be compressed.
- **D-18: blackout window with named backups.** Still open, still the only unfixable risk.
- **Author order (Q14).** Unsettled.

---

## 11. How to write prompts for this project

Constants live in `CLAUDE.md`, `AGENTS.md` and `docs/AGENT_RULES.md` and are auto-loaded. **Do
not restate the shell, the Python version, the secrets policy or the test norms.**

### Shape

```
CONTEXT: <what was found, and why this task exists>
OUTPUT CONTRACT: <function names not line numbers; raw output; fractions both terms;
                  every figure names what it supersedes; predict before measuring>
STEP 0 — GUARDS: environment + git identity + suite baseline. STOP on any failure.
<numbered steps, each with a STOP where a wrong turn is irreversible>
NON-GOALS: <files that must not be touched>
PREDICTED FAILURES — hypotheses, not spec. Correct me with evidence and add one more.
FINAL REPORT: <N lines max, in chat, no file>
```

### The demands that have caught everything

1. **Fractions with both numerator and denominator.** Caught a group-weighted 20% that was
   really an instance-weighted 3.9%.
2. **Every figure names the number it supersedes.** A superseded number is announced, never
   quietly replaced.
3. **Predict before measuring.** `~1232` is not a prediction.
4. **"Catching an error in this prompt is a success, not a deviation."** Include this line. It
   has preserved the v5 corpus once and stopped a renumbering of `DECISIONS.md`.
5. **Cap the report length.** One report ran 577 lines and required a chunked paste.

### Commit hygiene — mandatory in every commit phase

```
git config user.name && git config user.email
  → STOP unless DeepanshuOP / 99538840+DeepanshuOP@users.noreply.github.com
```

Never `git add -A` or `git add .` — explicit paths only. One plain human-sounding line with a
conventional prefix. **No trailers of any kind.** Verify with `git log -1 --format=%B`. Push and
paste both `git rev-parse HEAD origin/main` hashes.

---

## 12. First message to the new chat, suggested

> Read this handover. Do not write a prompt yet. First tell me, in your own words: what the v5
> instrument defect was, why 24.39% is not a parser precision figure, and what has to be true of
> the rebuilt worksheet before it can be re-scored. Then propose the rebuild prompt.

---

## 13. Recent commits

| Hash | Message |
|---|---|
| `0e1af4f2` | fix: correct Gradle chevron segmentation and suppress class-level failures |
| `b6439bc7` | fix: recover Java package from report header and stack frames |
| `22de7a30` | fix: update fixture-score corpus for recovered Java packages |
| `6c4ad166` | data: sample holdout v5 and record binding-rate decision |
| `0962fb27` | docs: correct holdout precision framing and handover docs |
| `4ba2d648` | data: score holdout v5 and close the corpus — **the score is defective; see §0** |
| `495e23f0` | docs: vendor graphify-br at pinned upstream SHA |
| `db19c577` | docs: correct superseded figures across documentation |

**`028-holdout-v5-score.md` states the corpus is CLOSED under D-37. That closing line is
superseded by this handover's §0 ruling: no measurement occurred, so the corpus is re-scorable.
Correct that file when the rebuild lands.**