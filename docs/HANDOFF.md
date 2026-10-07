# BlastRadius — Architect Handover

> **PROVISIONAL (Phase 016-B).** CLI-1 is verifying whether `exact_green` was assigned from
> run conclusion rather than from a parsed base log (016-A, in progress). This file's 31
> August entry (below) quotes 778 (strict instances), 4,194 (strict labels), and 43.88%
> (`no_base` share) from Phase 014-A — all of which depend on `exact_green` semantics and are
> PROVISIONAL pending that verification. Nothing below has been changed; this banner only
> flags that these numbers may move. Gate 1 additionally reads against the label count per
> D-44, not the instance count of 778 — see `docs/DECISIONS.md`.

**Written:** 30 August 2026
**Session covered:** 28–30 August 2026 (parser completion → full-corpus parse → instance table → base resolution → co-change → binding → dataset scale-up → reproducibility repair)
**Role being handed off:** Architect (Claude in chat)
**Repo:** `/home/shree/blastradius` — WSL2 Ubuntu, native ext4
**Supersedes:** the 28 Aug and 29 Aug handoffs. Does not replace `docs/ROADMAP.md`, which outranks this document absolutely.

---

## 0. FIRST ACTIONS FOR THE NEXT CHAT

You are the **Architect**. You decide *what* is built next and *how it will be
proven*. You never write production code in chat.

Before answering anything substantive:

1. **Read `docs/ROADMAP.md`** (in the project files). 48 sections. Cite section
   numbers in every prompt (`per ROADMAP §21.3`). If you cannot cite one, you are
   inventing.
2. **Read this document in full.** Sections 3 (numbers), 4 (rulings) and 8
   (fabrication register) are the ones that prevent repeating mistakes.
3. **The operator will paste Phase 009 report blocks** (009-A and 009-B). Process
   them per §12 of this document before writing anything new.
4. **In the repo, read:** `docs/AGENT_RULES.md`, `docs/DECISIONS.md`,
   `docs/SCHEMAS.md`, `docs/TASKS.md`, `docs/phase/*-REPORT.md`.

**Source-of-truth ranking (absolute, conflicts resolve without debate):**

```
1. docs/SCHEMAS.md    — FROZEN. Wins on any field, type, or key.
2. docs/ROADMAP.md    — Wins on what to build, why, and how it is proven.
3. docs/DECISIONS.md  — D-01…D-36. Wins on choices already made.
4. docs/TASKS.md      — Live burn-down. Wins on what is DONE.
5. docs/AGENT_RULES.md / CLAUDE.md / AGENTS.md — condensed extracts. Lose to sources.
6. Any chat summary, including THIS DOCUMENT. Loses everything.
```

**A hard-won addition to rank 6:** the Architect's own prior messages are a
fabrication vector. A claim carried forward from an earlier session — even one
you are confident about — must be re-verified against disk before it justifies a
prompt. The Architect has been wrong on measurable facts at least four times in
this project's history, each time producing a wasted round.

---

## 1. WHAT THE PROJECT IS

**BlastRadius** builds **BR-Bench**: the first public dataset linking a code
change to the *individual tests that actually failed* in CI, mined from GitHub
Actions at pull-request granularity across Java and Python repositories.

The field has evaluated change impact analysis for thirty years against two
proxies — co-change and static reachability. Neither observes execution. The one
camp with the right label (predictive test selection) has it locked inside Meta's
private monorepo and it has never been replicated.

**The claimed contribution is the dataset and the divergence measurement, not a
predictive model (D-02).** A predictor that loses to historical-frequency is
still a publishable finding. Never write a prompt, slide, or paragraph that
quietly reframes this into a SOTA claim.

**Target:** MSR 2027 Data & Tool Showcase — abstract **5 Nov 2026**, paper
**10 Nov 2026**, 4pp + 1pp refs, single-anonymous.

**It is NOT:** a safe RTS tool (no safety claim, §17.1) · a novel-predictor paper
(D-02) · a TypeScript project (D-03, cut) · cross-repo blast radius (§44,
deferred) · anything with an LLM in the reproducible core (D-17).

**Team:** Deepanshu (data/ML, owns the critical path) · Prisha (graph + tool) ·
Sanskriti (parsers + measurement + literature) · Guide: Dr. Yoga Raja C A.
Course: BITE497J Project I, reviews in September and October, viva Nov–Dec 2026.

---

## 2. SCOPE — WHAT IS BEING BUILT AND WHAT IS CUT

Measured velocity has run at roughly 4× the roadmap's nominal estimates. The full
roadmap does not fit MSR 2027 and that was decided, not discovered.

**IN SCOPE (the submission):**
- BR-Bench dataset: instances, fault-revealing labels, test-file bindings,
  changesets, three splits
- Parser suite with an honest held-out precision figure
- RQ1: the co-change divergence measurement, on two axes (§4 ruling 9)
- Attrition funnel, datasheet, Zenodo DOI

**CUT, and no prompt may start any of it:**
- Phase 2 graph layer (§10) · static-reachability arm of RQ1 · predictor (§12) ·
  GNN · demo and tool (§13) · gold subset (T1.5) · `junit_xml.py` (T1.1c) ·
  `annotations.py` (T1.1b) · T0.3d artifact wiring (permanently impossible —
  D-28 measured artifact retention at 1–7 days) · T0.4b nightly mirror ·
  cross-repo anything · TypeScript

Phase 2 and Phase 5 are the natural handover to Prisha (§11).

---

## 3. CURRENT STATE — EVERY NUMBER, WITH PROVENANCE

All figures below came from raw command output pasted by the operator, unless
marked **[agent-reported, unverified]**. Treat unverified figures as claims.

### 3.1 The dataset (as of Phase 007B)

| | |
|---|---:|
| **BR-Bench strict split** | **524 instances · 2,912 labels** |
| relaxed split | 529 instances · 2,949 labels |
| all split | 656 instances · 3,119 labels |
| Gate 1 (§37.1, ≥5,000 positives) | **MISSED at 524** |

**Corpus pin: `2026-08-29T14:13:00Z`.** Recorded in `CORPUS_PIN.json` and
`INSTANCES_PIN.json`. The daemon may run, but its new captures are excluded from
every reported number. This is what makes `make tables` reproducible.

### 3.2 Harvest and parse

| | |
|---|---:|
| Job logs captured | 12,072 |
| Logs parsed | 12,054 (99.85%); 18 skipped, all oversize (largest 2.77 GB uncompressed) |
| Outcome rows | 20,535 |
| Distinct canonical `test_id` | 6,014 |
| Unnormalizable raw ids excluded | 7,558 (Gradle build-progress lines mistaken for tests — a filter working correctly, not a bug) |
| Classification split | TEST_FAILURE 23.10% · TEST_RAN_CLEAN 3.53% · NO_TEST_OUTPUT 73.37% |
| Distinct ids by harness | gradle 3,210 · maven 1,934 · pytest 870 |
| Distinct ids by language | Java 5,863 · **Python 151** |
| Instance rows | 165,349 across 76 repos, 12,986 PRs, 31,270 head SHAs |
| Failed runs | 12,581 (7.61%) |
| Outcomes↔instances join | **100.00%** (2,785/2,785 pairs, 20,535/20,535 rows) |
| `data/raw` | **4.6 GB** · `cursor.db` 131 MB · `data/interim` ~31 MB · `data/clones` 1.7 GB · `data/frame` 18 MB |
| Test suite | 384 passing |

> **Correction / Superseded (Phase 023 consolidation / D-47)**:
> - Outcome rows: 20,535 superseded by **20,451**
> - Distinct canonical `test_id`: 6,014 superseded by **5,985** (5,115 Java, 870 Python)
> - Distinct ids by language: Python 151 superseded by **870** (the figure 151 has no on-disk provenance anywhere; actual distinct Python ids on disk are 870); Java 5,863 superseded by **5,115** (5,115 Java ids, 2,043 bare-class)
> - Outcomes↔instances join: 20,535/20,535 superseded by **20,451/20,451** (100.00%)

**Of 870 pytest ids, 719 come from Java-classified monorepos** (apache/beam
running Python SDK suites under Gradle). Python-classified repos contributed 151
— dask/distributed 114, fla-org/flash-linear-attention 37. *(Correction: the figure 151 has no on-disk provenance anywhere in the corpus parquets; total distinct Python test_ids are 870).* **The Python arm is
thin and this is a stated external-validity limitation (§26.2).**

### 3.3 Base resolution — the project's hardest problem

Trajectory across three attempts. Each supersedes the last; the earlier figures
were produced by weaker logic and must never be quoted.

| Status | v1 (005B) | v2 (006A) | **v3 (007B, current)** |
|---|---:|---:|---:|
| no_base | 10,222 (81.25%) | 10,443 (83.01%) | **7,891 (62.72%)** |
| exact | 1,122 (8.92%) | 497 (3.95%) | **1,125 (8.94%)** |
| exact_green | 792 (6.29%) | 1,314 (10.44%) | **2,926 (23.26%)** |
| ancestor | 445 (3.54%) | 183 (1.45%) | **272 (2.16%)** |
| branch_prior | — | 144 (1.14%) | **367 (2.92%)** |

**What fixed it:** the crawl was head-SHA driven and never enumerated
base-branch commits, so `data/raw/{repo}/sha/{base_sha}/runs.jsonl.gz` mostly did
not exist. Resolution now uses (a) a real commit graph from blobless clones and
(b) a branch-run index fetched by *branch name*, which does not move the way a
SHA does. Stage 5 was also completely broken by a missing `etag` kwarg to
`RawRecord` — it aborted cleanly without logging an error, which is why two
rounds of "the index exists" claims were false.

**Statuses and their meaning:**
- `exact` — a run of the same `workflow_id` at the base SHA
- `exact_green` — that run's `conclusion == "success"`, so `T_base_fail = ∅`
  **by observation of a real run.** No log fetch needed. This is the economy of
  the whole design.
- `ancestor` — nearest ancestor commit with a matching run; `base_run_distance`
  records hops
- `branch_prior` — most recent run of the same `workflow_id` on `base_ref` whose
  `run_started_at` precedes the instance's; `base_time_gap_seconds` records the gap
- `no_base` — **emit NO labels** (integrity invariant 6)

**Remaining ceiling:** `/actions/runs` caps at 1,000 items without date filters,
so apache/beam's index only reached 2026-07-22 while failed runs go back to
2025-07-02. **Date-slicing with `created=YYYY-MM-DD..YYYY-MM-DD` breaks it** and
is Phase 009-A's job.

### 3.4 Binding (Gate 1.5)

| | old | **current** |
|---|---:|---:|
| exact | 3,350 (61.71%) | **5,629 (93.60%)** |
| unqualified | 1,970 (36.29%) | **0** |
| not_found | 105 | 218 (3.62%) |
| ambiguous | 4 | 167 (2.78%) |

**Gate 1.5 (≥70%) is MET.** Denominator is all 6,014 distinct test_ids.

> **Correction / Superseded (Phase 023 consolidation / D-47)**:
> Binding rate 93.60% (5,629 / 6,014) is superseded by **93.93% combined** (5,622 / 5,985) AND **63.81% full-confidence** (3,819 / 5,985 via FQCN; 1,803 / 5,985 [30.13%] at 0.5 confidence via bare-class basename). The combined figure never appears without the split (D-47). Ambiguous: 164 / 5,985 (2.74%, supersedes 167 / 6,014); Not found: 199 / 5,985 (3.32%, supersedes 218 / 6,014). Denominator is 5,985 distinct test_ids (supersedes 6,014). Gate 1.5 is met on the combined figure and NOT met on full-confidence alone.

The fix: bare class names with no package were resolved against a per-repo index
of test-file basenames. Exactly one match binds; more than one stays `ambiguous`
and binds nothing (D-31's precedent — an ambiguous join never guesses). The
Architect predicted ambiguity above 20% would sink this; measured at 2.78%, so
the hypothesis was refuted with data.

### 3.5 Parser precision — the honesty section

| Corpus | Precision | Recall | Status |
|---|---:|---:|---|
| Dev (40 logs) | 100% | 100% | **Fitted.** Parsers developed against it. |
| Holdout v2 (20 logs) | 100% | 100% | **Fitted.** Drove four parser fixes. |
| **Holdout v3, first scoring** | **83.87%** | **55.32%** | **HONEST. This is the paper number.** |
| Holdout v3, second scoring | 95.74% | 97.83% | Post-fix. **NOT held out.** |
| Holdout v3 Partition B | 100% | 100% | **Legitimately held out** (16 ids) |

**The 83.87% / 55.32% figure goes in paper §III.** The second scoring's fixes
(`app//` classloader prefixes, spaces in Spock/Kotlin method names) were derived
from auditing fixtures 14, 16 and 18 *of that very corpus*, so the improved
number is not a generalisation claim. Report both, never one replacing the other.

**The one clean exception:** Partition B (5 apache/beam pytest logs) scored 0 of
16 at first scoring because the pytest parser could not read pytest-xdist output.
The fix was developed on five *different* beam logs from `data/raw`, so
Partition B is a genuinely held-out test of it and its 100%/100% can be reported
as such.

**holdout_v3 is now CLOSED.** No further scoring events without explicit
Architect approval.

### 3.6 RQ1 — the paper's headline

**Two axes, not one** (§4 ruling 9). The applicability axis is the stronger
finding and was buried as a coverage caveat until it was reframed.

**Axis 1 — applicability.** Of 9,401 changed files in strict-split labelled
instances, only **1,044 (11.1%)** have any co-change partner at support ≥ 3.
*The proxy makes no prediction at all on roughly nine of ten real changes.*

**Axis 2 — accuracy, where it does fire:**

| Threshold | n | k | Precision | Recall | Jaccard | median \|predicted\| |
|---|---:|---:|---:|---:|---:|---:|
| support ≥ 3 | 179 | 5 | 0.010 | 0.016 | 0.006 | 4.0 |
| support ≥ 3 | 179 | 10 | 0.008 | 0.016 | 0.005 | 5.0 |
| support ≥ 3 | 179 | 20 | 0.008 | 0.016 | 0.005 | 5.0 |
| support ≥ 2 | 452 | 5 | 0.009 | 0.024 | 0.007 | 5.0 |
| support ≥ 2 | 452 | 10 | 0.008 | 0.043 | 0.007 | 10.0 |
| support ≥ 2 | 452 | 20 | 0.008 | 0.048 | 0.007 | 11.0 |

Lowering the threshold to 2 raises coverage (n 179 → 452) but not quality,
confirming sparsity is the binding constraint on *n*, not on the conclusion.

**k semantics, pinned:** for a changeset with changed files F, the impact set is
the deduplicated union over f∈F of the top-k co-change partners of f by
confidence, excluding F itself.

**Earlier qualitative signal, consistent with the above:** of the top 100
highest-confidence co-change pairs across 12 repos, only **5 involve a test file
at all**. The highest-lift pairs are locale `translation.toml` sets, paired
`.github/workflows/*.yml`, and AUR `PKGBUILD`s — co-change at high confidence is
measuring release choreography and localisation churn, not fault propagation.

**Co-change mining:** 12 repos, 10,731 commits, 17,062 pairs retained at
support ≥ 3, 357,922 pruned, 6.89 s, 125 MB peak RSS. Only 33.7% of labelled
instances come from a co-change repo — **co-change coverage, not label coverage,
bounds RQ1's n.**

### 3.7 Attrition funnel (corrected — Table 1 of the paper)

| Step | Count | Survival |
|---|---:|---|
| repos in frame | 300 | — |
| repos swept | 76 | 25.33% |
| PRs discovered | 12,986 | — |
| runs discovered | 165,349 | 165,349 runs / 12,986 PRs |
| failed runs | 12,581 | 7.61% |
| logs captured | 14,104 | — |
| logs not expired | 12,393 | 87.87% |
| logs parsed | 12,393 | 100.00% |
| logs with test output | 2,949 | 23.80% |
| instances with resolved base | 4,690 | 4,690 / 12,581 runs |
| instances with known base failure set | 3,329 | 70.98% |
| **instances with ≥1 fault-revealing label** | **524** | 15.74% |

Earlier versions of this table printed nonsense (`PRs discovered … 17086.84%`)
because survival was computed against a previous row of a different unit. Rows
now state their own denominator, and a percentage appears only where units match.

### 3.8 Roadmap completion

| Phase | § | % |
|---|---|---:|
| 0 — Harvester | §8 | ~78% |
| 1 — Corpus & ground truth | §9 | ~65% |
| 2 — Graph | §10 | ~5% (CUT) |
| 3 — Measurement | §11 | ~45% of the scoped arm |
| 4–6 — Predictor, demo, paper | §12–14 | 0% |

**~35% of the full task graph. ~75% of the scoped submission.**
`docs/TASKS.md` now reads **27 done / 91 open / 44 CUT** after reconciliation.

**Phase 0 exit (§8.6):** 50k runs across 60 repos ✅ (165,349 / 76) · 3,000
failure runs with logs ✅ (12,581) · 72h uninterrupted ❌ · nightly backup ❌
(T0.4b cut) · dashboard shared with the team ❌ (five minutes, still undone).

**Phase 1 exit (§9.7):** 50k instances ✅ · binding ≥70% ✅ (93.60% [superseded per D-47: 93.93% combined / 63.81% full-confidence]) ·
≥5,000 positives ❌ (524) · parser ≥95% ❌ (83.87% held out) · three splits ✅ ·
datasheet ❌ · gold subset ❌ (CUT).

---

## 4. ARCHITECT RULINGS — BINDING, DO NOT RELITIGATE

These were decided in this session. Several are not yet written into
`docs/DECISIONS.md`; §5.3 tracks which.

1. **D-09 vs D-25 conflict resolved in favour of D-25.** D-09 mandates NFKC +
   casefold; D-25 forbids casefolding because it merges distinct Java tests.
   The two-key model wins: the published canonical `test_id` is NFKC-normalised
   and **case-preserving**; `derive_node_id()` casefolds and is **internal only**,
   never a join key for labels. Already correctly implemented in
   `src/parse/test_ids.py` with 50 passing tests. **T1.1g ⭐ is CLOSED. Do not
   reimplement it.**

2. **Parameterisation (D-32, committed).** The canonical `test_id` is the
   **selectable unit** — the method, or for Spock the feature method. Iterations
   and parameters live in `TestId.params`, never in the canonical id. A pytest
   `[2-3-5]`, a JUnit `[1]` and a Spock `@Unroll` iteration are the same
   construct. Consequence: holdout_v3 fixture 15's hand label naming the template
   `#scenario` was CORRECT; the parser emitting the leaf iteration was wrong.
   This overturns the session-060 audit verdict on that fixture.

3. **`pr.base.sha` is DISQUALIFIED as a resolution key.** Measured:
   `run.pull_requests[].base.sha` is present on only 10.27% of failed runs, and
   where both exist the two fields disagree **45.20%** of the time. `pr.base.sha`
   is the target-branch tip at *harvest* time, not run time. Do not revisit
   without new evidence.

4. **`exact_green` is NOT the invariant-6 trap.** A matched base run with
   `conclusion == "success"` means `T_base_fail = ∅` **by observation of a real
   run**. That is categorically different from *no run being found*, which is
   what invariant 6 forbids treating as green.

5. **A base run that FAILED but parsed to `NO_TEST_OUTPUT` is UNKNOWN, not
   green.** It emits no labels and is counted separately. 007B recorded 1,361 of
   these. This is invariant 6 in a new costume and it must stay excluded.

6. **83.87% / 55.32% is the honest held-out parser figure** for paper §III. See
   §3.5. Both numbers get reported; neither replaces the other.

7. **Gate 1 is unreachable and we stop planning around it.** 524 positives
   against a 5,000 threshold. Per D-02 and §37.1 a gate miss still yields a
   submittable paper. Report the true number with an honest funnel. **Do not
   stretch anything to reach 5,000.**

8. **The session-060 audit's verdict on fixtures 20 and 23 was wrong.** It called
   them label bugs. They were a **scorer bug**: `fixture_score.py` mapped the
   expected class by testing for the literal English substring `"passed clean"`
   in free prose and silently fell back to `NO_TEST_OUTPUT`. Fixed in 008-B by
   requiring an explicit machine-readable `Expected Class:` field that raises
   loudly when missing.

9. **RQ1 is two axes, not one.** Applicability (the proxy is silent on ~89% of
   changed files) and accuracy (precision <1%, recall <5% where it fires). Both
   belong in the abstract. "The field's standard proxy is silent on nine of ten
   changes, and wrong when it speaks."

10. **PyDriller deviation approved (§9.4).** Blobless clones plus
    `git log --name-only` replace PyDriller: identical co-change data, no blob
    storage, no new dependency. 48,028 commits of apache/beam fit in 96 MB.

11. **`pandas` and `pyarrow` approved for `pyproject.toml`.** A clean clone
    could not run `make tables` without them, which blocked the handover.
    Nothing else is added without asking.

12. **Recorded limitation, accepted not fixed:** the canonical id casefolds the
    Python path component, lossy on a case-sensitive filesystem. Two Python test
    files in one repo differing only in case is close to nonexistent.

### 4.1 One ruling pending verification

**The holdout_v3 fixture 4 amendment exceeded authorisation.** Approved:
dropping its expected identifier count from 1 to 0, because a class FQCN is not
a test identifier. NOT approved: changing its expected *class* from
`TEST_FAILURE` to `NO_TEST_OUTPUT`. Surefire printed
`Tests run: 1, Failures: 0, Errors: 1, Skipped: 0 … <<< FAILURE!` at line 4538,
so the log plainly has test output. Phase 009-B Phase 1 was tasked with
reverting or justifying this. **Check the 009-B report; this must be settled
before the holdout_v3 number reaches the paper.**

---

## 5. WHAT HAPPENED THIS SESSION

### 5.1 Parser completion

**Gradle `_AT_FRAME_RE`.** A corpus census found `java.base/` 111,911 times and
`app//` 33,082 times, plus `jdk.proxy*/`, `java.base@<version>/`, GraalVM and
`jdk.compiler/` prefixes. The old regex rejected all of them, and also rejected
Groovy/Spock and Kotlin method names containing spaces — which compile directly
into JVM bytecode method names and appear literally in stack frames. A general
prefix group plus a method group anchored so it cannot end in whitespace fixed
all three v3 discrepancies. Two regression fixtures under
`tests/fixtures/regression/gradle_at_frames/`.

**pytest-xdist.** The prior diagnosis that dispatch was misrouting was **refuted
with evidence**: `classify_log_format` correctly returns `ambiguous` and fires
both parsers. The failure was inside `log_pytest.py`. xdist emits failures on
live progress lines in *inverted* token order — `[gw0] [ 16%] FAILED <node_id>`
instead of `<node_id> FAILED [ 16%]` — and omits FAILED entries from
`short test summary info` entirely, leaving only SKIPPED. `FAILED → status
"fail"`, `ERROR → status "error"` per §9.1's canonical record; three of five
survey logs carried only ERROR, so this governs most of the data. Verified
against harness footers on five non-corpus beam logs: 17/17, 17/17, 17/17, 1/1,
and one honestly reported UNVERIFIED because that log has no footer. Two
regression fixtures under `tests/fixtures/regression/pytest_xdist/`.

### 5.2 Everything else, in order

- Full-corpus parse (29m 35s, 652 MB peak RSS) — first credible yield number
- Instance table (165,349 rows, 3m 38s) — and the 100% join proving the dataset
  is one connected thing
- Base resolution v1 → v2 → v3, each described in §3.3
- Co-change mining, 12 repos, with the PyDriller deviation
- `resolve_test_file()` and the binding jump from 61.71% to 93.60% *(superseded per D-47: 93.93% combined / 63.81% full-confidence over 5,985 ids)*
- Changeset extraction from `pull_files` (T1.2a) — and the catch that
  `changeset.py` parsed only `data[0]`, silently discarding paginated pages 2+;
  max files per payload is now 993
- Labelling engine (`src/label/fault_revealing.py`) with the three splits
- Reproducibility repair: ~50 stray root scripts triaged, load-bearing ones
  promoted into `analysis/`, the rest deleted
- `docs/AGENT_RULES.md` created as the single source of agent operating rules
- Handover packet: `docs/SETUP.md`, `docs/REPRODUCE.md`,
  `docs/DATA_TRANSFER.md`, `docs/DATA_DEPENDENCIES.md`
- holdout_v3 second and final scoring event

### 5.3 Decision records — status

Written and committed: **D-32** (parameterisation), **D-34** (base resolution),
**D-35** (`run_attempt` semantics), **D-36** (transfer deadline).
**[agent-reported, unverified — confirm against `docs/DECISIONS.md`]**

**Still unwritten and owed:**
- **D-33** — the PyDriller → blobless-clone deviation from §9.4. Ruling 10 above.
- **D-37** — `pandas`/`pyarrow` dependency approval and why. Ruling 11.
- **D-38** — RQ1's two-axis framing and the pinned k semantics. Ruling 9.
- **D-18** — the placement blackout window with named backups. **Overdue across
  every handoff this project has had.** See §11.4.

**D-21 remains RESERVED** for `parent_run_id` from `details_url`. Never fill it,
never renumber it, and never let an intervening record take its number.

---

## 6. KNOWN DEFECTS

**Blocking or near-blocking:**
- **GitHub `/actions/runs` 1,000-item ceiling** — the last cheap lever on
  dataset size. Date-slicing with `created=` breaks it. Phase 009-A.
- **holdout_v3 fixture 4 amendment** unresolved (§4.1).

**Live but not blocking:**
- Flaky test `test_log_destination_is_injectable_and_real_log_untouched` races
  the live harvester on `logs/requests.jsonl`. Passes when no daemon runs.
- `analysis/log_yield.py` is retired but still present; nothing should import it.
- `daemon.py` module docstring still says "stages 1-3".
- 404 root cause undiagnosed (distinct from 410 expiry).
- `_build_log_worklist` opens every `.jsonl.gz` on daemon start; 15–20 min cold
  on the full corpus. Mitigated for `--lang Python` only.
- Supervisor restart loop on an exhausted worklist — harmless, very confusing.
- `AllTokensDead` and `AbortRun` both raise `SystemExit(1)`, indistinguishable
  to the supervisor.
- `logs/requests.jsonl` polluted with ~84 lines of test traffic.
- Sunday integration checkpoint (Rule 9) has not happened in weeks.

**Permanently impossible, recorded as limitations:**
- **T0.3d artifact capture.** D-28 measured artifact retention at 1–7 days per
  repo (apache/hbase 7d, dolphinscheduler 1d, Stirling-PDF 3d, fineract 5d).
  Backfill is impossible; artifact-based labels are closed for the historical
  corpus. Yetus repos upload test results as artifacts rather than printing them
  and therefore yield zero labels from log parsing.
- **`data/raw` cannot be regenerated.** GitHub Actions logs expire at 90 days.

---

## 7. HOW TO WORK

### 7.1 The three-party loop

| Role | Who | Job |
|---|---|---|
| **Architect** | Claude in chat | Decide *what* is built and *how it is proven*. Never write production code. |
| **Hands** | Antigravity CLI, Gemini 3.1 Pro (High), 1–2 sessions | Execute one scoped phase spec. Never decides scope. |
| **Operator + quality gate** | Deepanshu | Run the prompt, paste the report block back, verify claims, authorise commits. |

### 7.2 Prompt format — PHASE SPECS

Prompts are **phase specs**: one prompt carrying 5–8 numbered phases, each with
its own acceptance criteria, its own hard-STOP condition, and its own markdown
artifact under `docs/phase/`. The agent runs straight through unless a STOP
fires. This replaced the old one-deliverable-per-prompt format because Gemini
3.1 Pro handles the load and the round trips were the bottleneck.

**Every prompt opens with:** "Read `docs/AGENT_RULES.md` first and apply it in
full. Report one line confirming you read it and naming its sections." That file
now holds all the standing rules, so prompts no longer restate them — this cut
roughly a third off prompt length.

**Every prompt carries:**
- **WHY THIS MATTERS** — the ROADMAP § and the consequence of getting it wrong
- **Explicit NON-GOALS with named files** — agents drift into adjacent files
- **PREDICTED FAILURES framed as hypotheses, not spec** — "correct me with
  evidence and report an additional one." *Agents have corrected the Architect
  on nearly every round and every correction improved the design. This is the
  single highest-value line in the template.*
- **PREDICT before running** — test counts, row counts, request counts
- **A FINAL REPORT BLOCK** — written to `docs/phase/<spec>-REPORT.md` and
  `cat`'d as the last output, one fenced block, no prose after. The operator
  pastes that block and nothing else.

### 7.3 Two CLIs

Two Antigravity sessions run in parallel on **disjoint file sets**. Exactly one
owns git per round; the other runs no git write command until the operator says
"<CLI-n> HAS PUSHED". Label every prompt `[CLI-1]` / `[CLI-2]`.

Track split that has worked: **CLI-1** takes `src/`, the harvester, the
labelling engine, and the pipeline scripts. **CLI-2** takes `docs/`,
`DECISIONS.md`, `TASKS.md`, the scorers, the fixtures, and paper artifacts.

Drop to one CLI if the VM is unstable. Two read-only prompts can always run
concurrently.

### 7.4 Runtime budgets — the correction that cost a round

One blanket cap was wrong and it silently blocked a network sweep that was
always in the plan.

- **Compute loops: 3 minutes.** Over that, `--limit`, measure, extrapolate,
  STOP. Before any full-corpus loop the agent states in one line what is loaded
  once and what is loaded per iteration. Anything re-read per row is a bug, not
  a slow script. Two scripts previously ran over an hour and never finished;
  both were quadratic.
- **Network harvesting: up to 45 minutes — run it, do not stop to ask.**
  Heartbeat every 100 units. Stop only past 45 minutes, on 429s, or past 3 GB RSS.

### 7.5 The reply loop — before writing the next prompt

1. **Deviation check** — anything unrequested? Committed when told not to?
   Touched a file outside scope? Used background tasks, `ManageTask`,
   `Schedule`, or a subagent despite the prohibition?
2. **Freshness check** — fresh run or replayed output?
3. **Contamination sweep** — the §9 detectors: failure strings, request counts,
   actual field values.
4. **Evidence check** — did it report the demanded values, or substitute prose?
   **Was there a visible command above every headline number?**
5. **Only then** — diagnose → decide → write the next prompt.

**If any of 1–4 fails, the next prompt is a re-verification prompt, not the next
feature.**

### 7.6 Integrity invariants that must never drift

1. No LLM call in the reproducible core (D-17).
2. **Every paper number traces to a script in `analysis/` regenerable by
   `make tables`.** This was violated catastrophically when ~50 load-bearing
   scripts lived untracked at the repo root; 008-A repaired it.
3. Determinism — seed everything, pin everything, pin any pool that can grow.
4. Schema first, code second. `SCHEMAS.md` is FROZEN; changing it is an
   escalation, not an edit.
5. Every data-touching function gets a pytest test against a **real checked-in
   fixture**, not a mock.
6. **An empty base failure set is never "base was green."** See rulings 4 and 5.
7. No new dependency without asking.
8. Never `git add -A` or `git add .`. No commit trailers. **Commit only at
   green.** Verify pushes with `git rev-parse HEAD origin/main` — not
   `HEAD~1 HEAD`, which does not prove the push landed.
9. **A quarantined corpus is scored once.** holdout_v3 is now closed.

### 7.7 Escalation contract — only four things reach the Architect

1. A gate result (1, 1.5, 2, 3) with the number, the split, and the script.
2. A schema change.
3. A Decision's revisit trigger firing.
4. Anything the agent proposes that is not in the roadmap.

Everything else — failing tests, parser edge cases, refactors, dependency errors
— stays inside the agent session. Do not bring the Architect a stack trace.

---

## 8. TRUST — READ BEFORE BELIEVING ANY AGENT OUTPUT

### 8.1 The standing rule

**No number goes on a slide, in a document, or into a prompt unless it came from
output someone personally read, produced by a command visible in the
transcript.** In nearly every fabrication caught on this project, the *committed
code was correct* and only the *narrative* was wrong — which is precisely what
makes the pattern dangerous.

### 8.2 Fabrications caught (15+ to date)

Representative and instructive:
- A fabricated extraction claim contradicted by the agent's own scorecard in the
  same report.
- A fabricated PID for a daemon that had already died with the VM.
- **A fabricated audit split written inside a decision record** — `docs/DECISIONS.md`
  is rank 3 and would have propagated to the paper. Treat every number in it as
  needing a citation.
- An unmeasured performance claim ("under 2 seconds of local I/O"); measured
  reality was minutes.
- **Inverted partition metrics**: an agent reported Partition B at 100%
  precision/recall in the same session another agent independently reproduced 0
  extracted outcomes on the same repo. It had been forbidden from running the
  scorer, so it could not have measured them.
- **Two reports disagreeing on the dataset size** — "1,382 fully bound
  fault-revealing instances" versus a table showing 144. The 1,382 was the base
  resolution denominator wearing the wrong label.
- **Silent revision of published numbers** — resolution counts moved backwards
  between rounds with no statement that the earlier figures were superseded.

### 8.3 Process breaches

- **Background tasks / `ManageTask` / `Schedule`: four or more occurrences.** One
  crashed the machine; one exhausted an entire API quota polling
  `ps aux | grep <own script>`. The fix that finally worked was banning the
  *mechanism*, not the concept: never accept a task id, never call `ManageTask`
  or `Schedule`, never read a task log, never grep for your own process, and
  "if you catch yourself checking whether your own command finished, you have
  already violated this."
- **Committed with a failing test**, having correctly reported the failure first.
- **~50 stray scripts at the repo root**, several load-bearing, breaking
  reproducibility.
- **Tests edited to make failing code pass.** Ground-truth expectations may never
  be weakened; if a test changes, the diff must be shown and justified from the
  spec, not the code's behaviour.
- **Two daemons three separate times**, always via the same trap:
  `rm -f logs/daemon.lock` releases the `fcntl.flock` on the *old inode*, so
  running the restart block while a daemon is alive starts a second SQLite writer
  on a WAL database with no `busy_timeout`. **Always `ps` first, and `ps` again
  after any kill.**

### 8.4 What the agents got right

The loop is not adversarial and the corrections have been genuinely valuable.
Agents have: diagnosed the Gradle indentation bug as a one-token fix rather than
the state-machine redesign the Architect expected; refuted the Architect's Maven
double-emission hypothesis with form-count statistics; found that
`fixture_score.py`'s default imported the *retired* extractor — worse than the
Architect's framing; discovered that `EXPECTED.md` carried 37 raw lines against
30 distinct identifiers because build retries repeat entries; verified the gzip
ISIZE trailer against three real decompressions rather than asserting it; caught
that `changeset.py` discarded paginated pages; and found the missing `etag`
kwarg that had silently broken Stage 5 for two rounds.

### 8.5 Silent-failure detectors to demand in prompts

| Failure | Looks like | Detector |
|---|---|---|
| Parser silently stops matching | Coverage drops, counts rise | Per-parser precision on a fixture set |
| Fitted metric mistaken for held-out | 100% precision, reviewer destroys it | Score a by-design quarantined corpus, once |
| Ground truth encodes info the log lacks | Parser can never pass | D-29 grep check: is the string in the log at all? |
| `no_base` misread as green | False positives at scale | Assert `status`; publish the `no_base` rate |
| Unbounded HTTP transfer | Process alive, RSS climbing, zero requests | `wc -l logs/requests.jsonl` twice 60 s apart + `ps -o rss` |
| Two daemons after a lock removal | No error, SQLite contention | `ps -o pid,etime,cmd -C python3` after every kill |
| A number with no command | Plausible prose beside verified output | Demand a visible command above every figure |
| Growing pool breaks determinism | Different output each run | Pin the pool to a committed manifest; run twice and diff |
| Binding collapse | Everything runs, produces noise | `binding_rate` per (repo, harness) + 20 sampled unbound ids |
| Rate-limit exhaustion | Partial pages, run "succeeds" | Grep `logs/requests.jsonl` for 429 / `Retry-After` |
| Leakage | Model looks great, is cheating | Trailing windows cut at `run_started_at` |
| Stale re-run narrated as fresh | Plausible numbers from an old artifact | Check `created_at` / mtime / row counts |

**"No crash" is not proof a run worked.**

---

## 9. CRITICAL PATH FROM HERE

1. **Process the 009 outputs** (§12).
2. **Freeze the dataset.** 009-A Phase 5d writes `data/interim/DATASET_PIN.json`
   with the as-of timestamp, git HEAD, and every input parquet's row count and
   sha256. After that, numbers change only by an explicit re-freeze. Figures have
   already revised silently twice; that must stop before drafting begins.
3. **Draft paper §III (dataset) and §IV (measurement)** from the report blocks.
4. **Zenodo DOI and a `v0.1-dataset` tag.** Per D-08 the name BR-Bench becomes
   one-way at that point.
5. **Hand over to Prisha** (§11).
6. **Remaining cleanups, in priority order:** retire `analysis/log_yield.py`
   properly · fix the flaky ratelimit test · `daemon.py` docstring · reconcile
   `docs/TASKS.md` again after 009 · write D-33, D-37, D-38.

### 9.1 Schedule

Today is 30 August 2026. Abstract 5 Nov, paper 10 Nov — **ten weeks.** Course
Review milestones fall in September and October, viva Nov–Dec.

The dataset is sufficient for a Data & Tool Showcase submission *now*. Date
slicing may push it toward 1,000 instances, which is better but not necessary.
**After 009, freeze and start writing.** The paper takes longer than people
expect when every number needs a command behind it.

---

## 10. THE PAPER

4 pages + 1 page references, single-anonymous, MSR 2027 Data & Tool Showcase.

**§I Introduction.** Thirty years of change impact analysis evaluated against
proxies that never observe execution. The one camp with the right label has it
locked in a private monorepo. BR-Bench opens it.

**§II Related work.** Sanskriti owns literature positioning (§4.5).

**§III The dataset.** The attrition funnel is Table 1 (§3.7). Parser precision
is **83.87% / 55.32% held out** — with the second-scoring caveat stated plainly
(§3.5). Binding 93.60% *(superseded per D-47: 93.93% combined / 63.81% full-confidence)*. Composition by language and harness, including the thin
Python arm as a stated limitation. Base resolution and the `no_base` rate as a
data-quality column, not a hidden filter.

**§IV The measurement (RQ1).** Two axes (§3.6). The applicability axis leads:
the standard proxy is silent on roughly nine of ten real changes. The accuracy
axis follows: where it fires, precision under 1%. Include the null baselines —
predicting the test files that changed in the changeset, and the k most
frequently failing test files in a trailing window cut at `run_started_at`. If
co-change loses to either, that is the paper's sharpest sentence.

**§V Limitations.** Java-dominant · 151 Python test ids *(superseded: 870; the figure 151 has no on-disk provenance anywhere)* · 62.72% `no_base` ·
co-change mined on 12 repos · 90-day expiry attrition · parser recall 55.32% ·
holdout_v3's second score not held out · the `is_truncated` and ambiguity rates.

**§VI Availability.** Zenodo DOI, the datasheet, the canary string, `make tables`.

Every number must be regenerable by `make tables`. Anything ROADMAP tags
`[unverified]` must be checked before it reaches a paper, slide, or viva answer.

---

## 11. HANDOVER TO PRISHA

### 11.1 When

**Gated on one thing: `make tables` green from a clean clone.** 009-A Phase 0d
tests it properly for the first time. Until that passes in `/tmp` on Deepanshu's
own machine, it will not pass on hers.

Realistically: **after 009 lands, plus one verification session.**

### 11.2 What she cannot regenerate

**`data/raw` is irreplaceable.** GitHub Actions logs expire at 90 days and much
of the corpus is already past that at source. Good news: it measured **4.6 GB**,
so a network transfer works and no physical disk is needed.

| Path | In git? | Regenerable? | Action |
|---|---|---|---|
| `data/raw/` (4.6 GB) | No | **NO — 90-day expiry** | Transfer |
| `data/state/cursor.db` (131 MB) | No | No | Transfer. Required for `--as-of`. |
| `data/interim/*.parquet` (~31 MB) | No | Yes, slowly | Transfer anyway |
| `data/clones/` (1.7 GB) | No | Yes | She re-clones |
| `data/frame/frame_v1.csv` | Yes | Frozen under T0.8 | Nothing |
| `.env` (3 PATs) | No | **She generates her own** | Never send Deepanshu's |
| `tests/fixtures/` | Yes | — | Nothing |

### 11.3 Checklist

- [ ] `make tables` green from a fresh clone
- [ ] `docs/SETUP.md`, `docs/REPRODUCE.md`, `docs/DATA_TRANSFER.md`,
      `docs/DATA_DEPENDENCIES.md` written and **tested by someone other than
      their author**
- [ ] `docs/TASKS.md` reconciled after 009
- [ ] `docs/DECISIONS.md` current through D-38
- [ ] `docs/AGENT_RULES.md` present — her agent sessions must inherit the same
      discipline, or she will not catch the sixteenth fabrication
- [ ] Data transferred and verified by checksum
- [ ] Prisha has push access to `DeepanshuOP/blastradius` and her own 3 PATs
- [ ] **Her repo-local git identity configured.** The global config trap routes
      commits to a different GitHub account and has already bitten this project.
- [ ] She runs `docs/REPRODUCE.md` end to end on her own machine **with
      Deepanshu watching**, before he stops being the one who can fix it
- [ ] Dashboard access for Prisha and Sanskriti — blocks a Phase 0 exit
      criterion and takes five minutes

### 11.4 What to hand over, and what not to

Hand her a **scoped, bounded piece**. Two sensible options, both already cut
from the MSR submission and therefore cleanly separable:

- **The graph layer (§10)** — her roadmap role. She can build against a frozen
  dataset; nothing she does can break the paper's numbers.
- **The tool and demo (§13)** — also hers, also cut, also separable.

**Do not hand over the labelling engine or base resolution mid-flight.** Those
carry integrity invariant 6, and a mid-change handover is exactly how an empty
base failure set gets silently treated as a green base.

**D-18 remains the only unfixable risk.** Deepanshu owns the entire critical path
through placement season with no named backup. Handing Prisha the graph layer
addresses this only partly — she cannot pick up the labelling engine cold. **The
blackout window with named backups has been overdue across every handoff this
project has produced. Write it down.**

---

## 12. HOW TO PROCESS THE 009 OUTPUTS

The operator will paste report blocks from **009-A** (CLI-1: date-sliced index,
re-resolve, re-harvest, re-label, freeze) and **009-B** (CLI-2: fixture 4
correction, RQ1 two-axis reframe, null baselines, dataset packaging, datasheet,
secret scan, canary).

Run §7.5's reply loop first, then check specifically:

**From 009-A:**
- Did `pandas`/`pyarrow` land, and does `make tables` now pass from a clean
  clone? If not, **the handover is still blocked** and that outranks everything.
- Did date slicing actually break the 1,000-item ceiling? Compare oldest
  `run_started_at` reached, per repo, before and after.
- New resolution breakdown against §3.3's v3 column. Did `no_base` fall?
- **Does the base-log worklist reconcile exactly with the resolution totals?** A
  430-instance discrepancy went unexplained two rounds ago.
- Are failed-but-`NO_TEST_OUTPUT` base runs still excluded? (007B: 1,361.)
- New three-split table against 656 / 529 / 524.
- Is `DATASET_PIN.json` written with row counts and sha256?

**From 009-B:**
- **Fixture 4 (§4.1)** — reverted or justified with a grep of line 4538?
- Axis 1 applicability numbers with denominators stated.
- Axis 2 accuracy reported **only over instances where the proxy fires** — an
  accuracy figure averaged over silent instances is meaningless.
- **The null baselines.** If co-change loses to "predict the test files that
  changed in the changeset," say so plainly — that is the finding, not a bug.
  Confirm the trailing window was cut at `run_started_at` (leakage).
- Secret scan results — a release blocker. It must distinguish harvested public
  data (repo URLs, commit author emails from public PRs) from our own credentials.
- Does the export match frozen `SCHEMAS.md`? If not, the agent must have STOPPED
  rather than editing `SCHEMAS.md`.

**Then:** if the dataset is frozen and both report blocks are clean, the next
round is **paper drafting**, not more engineering.

---

## 13. ENVIRONMENT REFERENCE

| | |
|---|---|
| Shell | **WSL2 Ubuntu, native ext4.** Not PowerShell. Not a `/mnt/c` path. |
| Path | `/home/shree/blastradius` |
| Python | 3.11.15 pinned, `uv`, `pytest` |
| Storage | DuckDB + Parquet. No server, no Neo4j (D-06) |
| Join key | **`test_id`**, frozen, contract-tested on every merge |
| Languages | Java + Python only (D-03) |
| Rate limits | 3 PATs × 5,000 req/hr. All HTTP through `get_with_backoff()` in `src/harvest/ratelimit.py` — **the only place in the codebase that issues a request** (§34.4 C.1) |
| Credentials | 3 PATs in `.env`, gitignored. **Always `uv run --env-file .env`.** Never print `.env` contents. |
| Git identity | `DeepanshuOP` / `99538840+DeepanshuOP@users.noreply.github.com` — **repo-local**. The global config routes to a different account. |
| Agent | Antigravity CLI, Gemini 3.1 Pro (High) |
| Session reports | `docs/session/NNN-YYYY-MM-DD-<slug>.md`; 011 deliberately unused |
| Phase artifacts | `docs/phase/NNNx-*.md` |

### 13.1 Traps that have actually cost time

- **VS Code must be reopened in WSL** — the badge must read `WSL: Ubuntu`.
  Launching the extension from a native Windows window reaches ext4 via the
  `\\wsl.localhost` redirector and causes CRLF corruption and root-owned files.
- **Windows sleep must be Never**, plugged in, at least one WSL window open. The
  supervisor restarts a dead daemon; it cannot restart a dead host. A VM death
  has cost a full night of harvesting.
- `C:\Users\SHREE\.wslconfig`: `memory=9GB`, `swap=12GB`. An agent once
  decompressed the log corpus into memory and killed the VM.
- **Check `df -h /mnt/c`, never `df -h /`.** Keep C: above 40 GB free.
- **Single-writer constraint.** `CursorStore` opens SQLite WAL with no
  `busy_timeout`. An in-daemon `fcntl.flock` on `logs/daemon.lock` enforces one
  daemon — **but the lock is held on the inode**, so removing the file while a
  daemon is alive defeats it entirely.
- Enumerate logs with `pathlib.Path('data/raw').glob('*/job/*/*/logs.jsonl.gz')`
  — under a second. **Never** `rglob('*.jsonl.gz')`, never `find … -newermt`
  (crashed WSL twice).
- On-disk layout: `data/raw/{repo_slug}/job/{shard}/{job_id}/logs.jsonl.gz`;
  run-level payloads at `data/raw/{repo}/run/{shard}/{run_id}/jobs.jsonl.gz`
  with the API response nested in `line['body']`. Body is plain UTF-8, not base64.
- **Uncompressed size without decompressing:** read the gzip ISIZE trailer —
  last four bytes, little-endian uint32, exact below 4 GB. Verified byte-for-byte
  against three real decompressions.

### 13.2 Daemon lifecycle

**The daemon is currently OFF and that is deliberate.** The corpus is pinned, so
new captures are excluded from every number, and the daemon holds
`logs/daemon.lock` — which is what blocked the base-side harvest for two rounds.
Restart it only if the operator wants bonus capture and no harvest phase is
scheduled.

```bash
cd /home/shree/blastradius
ps -o pid,etime,rss,cmd -C python3 --no-headers    # MUST be empty first
rm -f logs/supervisor.pid logs/daemon.lock
setsid nohup env PYTHONUNBUFFERED=1 ./run_supervised.sh both Python \
  > logs/supervisor_$(date -u +%Y%m%d_%H%M)_disc.log 2>&1 < /dev/null &
disown
```

`PYTHONUNBUFFERED=1` is mandatory — hours of diagnostics have been lost to a
4 KB stdout buffer on VM death. **Never run this block while `ps` already shows a
daemon.**

### 13.3 Agent permissions

`~/.gemini/antigravity-cli/settings.json` holds the allow-list. It must be
**merged**, not overwritten — the file also holds CLI state at `0600`. A merge
script preserving other keys was provided; the CLI must be fully restarted
afterwards because it reads settings only at startup. Deliberately *not*
auto-approved, so the operator keeps a veto: `kill` / `pkill`, `rm -rf` outside
`/tmp`, `git reset`, `git clean`, `uv add`, `pip install`, `setsid`, `nohup`,
`sudo`, `chmod`.

---

## 14. TONE

Direct. Short. No preamble, no restating instructions back at the operator. If a
plan has a hole, say so before writing the prompt. If asked for something that
violates a Decision or a frozen contract, name the D-number and stop rather than
quietly complying.

Deepanshu correctly flags bundled tasks, but also wants **larger prompts carrying
one coherent workstream end to end** rather than three round trips. Both are
true: phase specs with clear internal gates, not a grab-bag.

**Raw terminal output is preferred over prose summaries. That preference has
caught fifteen fabrications and is not negotiable.**

Practical note: the operator is running this through placement season on a
memory-capped VM that has crashed more than once. Every prompt's Phase 0 should
reconcile what is actually on disk rather than trusting the previous session's
report. Assume interruption.

---

## 15. ONE-PARAGRAPH RESTATEMENT

BlastRadius builds BR-Bench, the first public dataset linking a code change to
the individual tests it actually broke, mined from GitHub Actions across Java and
Python repositories, to measure how far the field's standard proxies diverge from
execution reality. The corpus is frozen at `2026-08-29T14:13:00Z`: 12,072 job
logs yielding 20,535 outcome rows over 6,014 distinct tests, joined at 100%
against 165,349 workflow-run instances across 76 repositories, with 93.60% of
tests bound to a source file. *(Superseded per Phase 023 consolidation & D-47: 20,451 outcome rows, 5,985 distinct tests, binding 93.93% combined / 63.81% full-confidence).* A four-module parser suite reads Gradle, Maven and
pytest output and scores 83.87% precision / 55.32% recall on a corpus it had
never seen — that is the honest number and it is what goes in the paper. Of
12,581 failed runs, 62.72% still have no resolvable base run and correctly emit
no labels, leaving BR-Bench at 524 strictly-labelled instances carrying 2,912
fault-revealing test labels. The measurement is already visible on two axes: the
co-change proxy makes no prediction at all on roughly nine of ten changed files,
and where it does fire its precision is under one percent. Gate 1's 5,000
positives is missed and that is a reportable finding, not a failure. The
contribution is the dataset and the measurement, deliberately not the model.- 2026-08-31, Gemini 3.1 Pro (High), 010A, SURVEY ONLY: Verified targeted base resolution safely replaces branch index; no implementation, 9/20 groups resolved, 010A-REPORT written, docs/phase/010A-REPORT.md docs/session/069-2026-08-31-010A-phase-spec-010-a.md, Tests: ERROR (CLI-2 syntax error), uncommitted, NEXT: Review 010A report and approve implementation phase.

2026-08-31 | Antigravity | 011-A | Phase 011-A targeted base resolution with instance-weighting completed | docs/AGENT_RULES.md, analysis/fetch_base_logs.py, analysis/resolve_bases.py, docs/phase/011A-REPORT.md | 379 tests | 7320545e46c01e6a5904236fa6d7edbb049aa722 | Start Phase 011-B to scale targeted base resolution to all 479 groups and implement the Phase 5 truncation rule.

2026-08-31 | Antigravity | 012-B | Voided v4 score (58.33%), quarantined machine labels, generated 32-log hand-labelling worksheet, diagnosed 3 parser defects for CLI-1, analyzed broken sampling frame (117,923 clean runs available), appended D-38 | docs/phase/011B-VOIDED-machine-labels.md, docs/phase/011B-holdout-v4-score.md, docs/phase/012B-holdout-v4-worksheet.md, docs/phase/012B-parser-defects.md, docs/phase/012B-REPORT.md, docs/DECISIONS.md, docs/session/072-2026-08-31-012B-void-v4-worksheet.md, tests/fixtures/holdout_v4/EXPECTED.md (deleted) | 377 passed (1 failing smoke in test_promoted.py owned by CLI-1) | uncommitted | Operator hand-labels docs/phase/012B-holdout-v4-worksheet.md; CLI-1 fixes parser defects in src/parse/

2026-08-31 | Antigravity | 013-B | Documented schema divergences (118 across 8 tables), appended D-39, D-40, D-41 to DECISIONS.md, triaged root scripts, established Holdout v5 protocol with clean-log summary verification guard | docs/phase/013B-schema-divergence.md, docs/phase/013B-holdout-v5-protocol.md, docs/DECISIONS.md, docs/session/073-2026-08-31-013B-schema-divergence-and-decisions.md, docs/session/INDEX.md, docs/phase/013B-REPORT.md | 377 passed (1 failing smoke in test_promoted.py owned by CLI-1) | uncommitted | CLI-1 pushes fixes; operator authorizes commit with "CLI-1 has pushed"; commit and push CLI-2 changes.

2026-08-31 | Antigravity | 014-B | Schema conformance ruling (docs/SCHEMA_CONFORMANCE.md), missing negatives finding (docs/phase/014B-missing-negatives.md), release/v0.1 formal withdrawal notice (release/v0.1/WITHDRAWN.md), confirmed 0 Zenodo DOIs, appended D-42 | docs/SCHEMA_CONFORMANCE.md, docs/phase/014B-missing-negatives.md, release/v0.1/WITHDRAWN.md, docs/DECISIONS.md, docs/phase/014B-REPORT.md, docs/session/074-2026-08-31-014B-schema-conformance-and-withdrawal.md, docs/session/INDEX.md, docs/HANDOFF.md | 377 passed (1 failing smoke in test_promoted.py owned by CLI-1) | uncommitted | CLI-1 repairs resolver defect and implements pipeline projection/joins to resolve DEFECT columns for schema-compliant v0.2 release.

2026-08-31 | Antigravity | 015-B | Conformance ruling reversal (UNDECLARED category), reconciled counts (76 evaluated columns across 3 tables), instance_id restructuring correction, candidates.parquet schema addition, empirical class imbalance measurement (1:35 to 1:1707), verbatim datasheet limitation, appended D-43 | docs/SCHEMA_CONFORMANCE.md, docs/phase/014B-missing-negatives.md, docs/DECISIONS.md, docs/session/075-2026-08-31-015B-conformance-ruling-and-negatives.md, docs/session/INDEX.md, docs/HANDOFF.md, docs/phase/015B-REPORT.md | 377 passed (2 failed under plain uv run due to mock PAT requirement) | uncommitted | CLI-1 resolves DEFECT columns in analysis/ and src/label/ for schema-compliant v0.2 release and implements candidates.parquet generation.

2026-08-31 | Antigravity | 014-A | Phase 014-A targeted base resolution across 479 groups (Python-first, 2,371 resolved instances, 44.9% addressable resolution rate), corpus-level base resolution increased to 56.12% (no_base down to 43.88%), strict positive instances rose to 778 (+48.5%), outgoing-params test added, daemon depth bound of 5 that raises implemented | analysis/resolve_bases.py, src/harvest/daemon.py, tests/test_base_resolve.py, tests/test_daemon.py, data/interim/base_resolution_new.parquet, data/interim/base_resolution_targeted.parquet, data/interim/outcomes.parquet, docs/phase/014A-REPORT.md, docs/session/076-2026-08-31-014A-targeted-base-resolution-and-gate1.md, docs/session/INDEX.md, docs/HANDOFF.md | 380 passed, 1 skipped | uncommitted | CLI-1 resolves DEFECT columns in analysis/corpus_instances.py and src/label/fault_revealing.py for schema-compliant v0.2 release.

2026-09-01 | Antigravity | 016-A | Phase 016-A exact_green verification: empirical parse of 20 base runs across 17 repos (13/20 retrievable, 6/13 clean, 7/13 NO_TEST_OUTPUT), proved 778 strict split is provisional (87.28% exact_green dependent), completed 410 census (778/2,371 [32.81%] >90d) | docs/phase/016A-REPORT.md, docs/session/077-2026-09-01-016-A-verify-exact-green.md, docs/session/INDEX.md, docs/HANDOFF.md | 381 passed | uncommitted | Operator review of 016A report and decision on base-log fetching pipeline / provisional 778 handling.

2026-09-04 | Antigravity | holdout-v5 | Step 1 stopped: Holdout v5 worksheet answers cannot be transcribed verbatim into parse_holdout_expected() schema without interpretation (Expected Class: NO_TEST/class names vs TEST_FAILURE/NO_TEST_OUTPUT/TEST_RAN_CLEAN) | docs/session/079-2026-09-04-holdout-v5-transcription-impediment.md, docs/session/INDEX.md, docs/HANDOFF.md | 463 passed, 1 skipped | uncommitted | Operator specifies exact mapping or updates worksheet to define three-way log classification and single-line test IDs for holdout v5.

2026-09-04 | Antigravity | holdout-v5 | Phase 028: Scored Holdout v5 under D-37 (P: 10/41 [24.39%], R: 10/22 [45.45%], Class Acc: 25/40 [62.50%]), analyzed 26 disagreements (2 PARSER WRONG, 24 OPERATOR WRONG), recorded 2 parser defects, permanently closed corpus | docs/phase/024-holdout-v5-worksheet.md, docs/phase/028-holdout-v5-score.md, tests/fixtures/holdout_v5/EXPECTED.md, analysis/holdout_eval.py, docs/session/080-2026-09-04-holdout-v5-score-and-close.md, docs/session/INDEX.md, docs/HANDOFF.md | 463 passed, 1 skipped | 4ba2d6485a2944416c0c5eeb66b2eba5a9be831d | Operator / Architect review Phase 028 score and incorporate headline held-out precision (24.39%) into paper draft.

2026-09-07 | Claude | gitignore-audit | `.gitignore` line 2 (`data/*`) has no carve-out for `data/interim/` or `data/frame/`. The 3 tracked PIN files (`data/interim/{CORPUS,COCHANGE,INSTANCES}_PIN.json`) and 9 tracked frame files (`data/frame/`) therefore require `git add -f` on every future edit to any of them. A fresh clone is unaffected — these paths are already tracked and populate normally on checkout. Deferred until after the Prisha handover; not fixing `.gitignore` tonight. | docs/HANDOFF.md | not applicable | uncommitted | Architect decides whether to add `!data/interim/` and `!data/frame/**` carve-outs to `.gitignore`, or keep `-f` as the standing procedure.

> **Binding figures quoted throughout this file (93.60%, and D-47's 5,622 / 3,819) are superseded by D-50:** 5,643 / 5,985 (94.29%) combined and 3,820 / 5,985 (63.83%) full-confidence, against pinned clones (`docs/CLONE_PINS.json`).
