# Datasheet for BR-Bench

> **DRAFT — for human review.** Every figure below names the command and table it
> came from. Nothing here has been checked by a second pair of eyes, and the
> dataset is **not publishable in its current state** (see §6).

Structure follows Gebru et al., *Datasheets for Datasets* (CACM 64(12), 2021).

Dataset name **BR-Bench**; project name **BlastRadius** (D-08). Naming becomes
one-way only once a DOI is minted, which has not happened.

**Provenance of every figure.** All figures regenerate from the chain fixed by
D-49, run at commit `34aec6d` or later:

```
uv run python analysis/corpus_parse.py --as-of 2026-08-29T14:13:00Z --overwrite
uv run python analysis/parse_base_logs.py
uv run python src/label/fault_revealing.py
make tables
```

Sources are cited as either a generated table (`paper/generated/<file>.md §<n>`)
or the `make tables` step whose stdout carries the number. Figures from the
first three commands are cited as "rebuild chain, `<script>`" because
`analysis/corpus_parse.py` is deliberately **not** part of `make tables` — the
corpus is pinned by `data/interim/CORPUS_PIN.json` and re-parsing is an explicit
act, not a side effect of regenerating tables.

---

## 1. Motivation

**For what purpose was the dataset created?** To measure change-impact
prediction against execution-grounded ground truth. Existing CIA datasets label
a change with the files or tests a *static analysis* believes it affects.
BR-Bench labels a change with the individual tests that *actually failed* in CI,
mined from GitHub Actions runs, so a predictor can be scored against observed
execution rather than against another tool's opinion.

**Who created it and who funded it?** Prisha Vadhavkar (23BIT0010), Sanskriti
Singh (23BIT0256) and Deepanshu (23BIT0264), VIT, course BITE497J Project I,
guide Dr. Yoga Raja C A. No external funding. Target venue: MSR 2027 Data & Tool
Showcase.

**What is the contribution?** The dataset and the honest measurement, not a
novel predictor. A negative model result is a publishable outcome for this
track.

---

## 2. Composition

**What do the instances represent?** Two grains:

- an **instance** — one (head SHA, workflow run) pair for a pull request;
- an **outcome/label** — one (instance, test) pair, labelled 1 when that test is
  in the fault-revealing set for that change.

**How many instances are there?**

| Table | Rows | Source |
|---|---|---|
| `instances.parquet` | 165,349 | release bundle, `analysis/build_release.py` |
| `outcomes.parquet` | 12,766 | release bundle, `analysis/build_release.py` |
| `cochange.parquet` | 175,204 | release bundle, `analysis/build_release.py` |
| `failure_messages.parquet` | 3,490 | release bundle, `analysis/build_release.py` |

Label counts by split, and the run-level resolution frame:

| Figure | Value | Source |
|---|---|---|
| labels, `all` split | 4,384 | rebuild chain, `src/label/fault_revealing.py` |
| labels, `relaxed` split | 4,214 | rebuild chain, `src/label/fault_revealing.py` |
| labels, `strict` split | 4,168 | rebuild chain, `src/label/fault_revealing.py` |
| instances with ≥1 strict label | 762 | rebuild chain, `src/label/fault_revealing.py` |
| distinct tests, strict split | 2,466 | rebuild chain, `src/label/fault_revealing.py` |
| run-level rows | 12,581 | `make tables`, `analysis/corpus_delta.py` |
| `no_base` rate | 5,520/12,581 (43.88%) | `make tables`, `analysis/corpus_delta.py` |
| same-SHA flip rate | 62 (0.54%) | rebuild chain, `src/label/fault_revealing.py` |

**What data does each instance consist of?** Repository, PR number, head and
base SHA, base ref, workflow run and job identifiers, workflow name, run
conclusion, matrix-leg count, bot flags, author login, event type. Test
outcomes carry the canonical `test_id`, parser confidence, harness, status,
duration, FQCN-qualification flag and parameter signature.

**Is there a label?** Yes. Fault-revealing status per (instance, test), in three
splits: `all`, `relaxed` (test failed at head and not at base), `strict`
(`relaxed` minus tests scored as flaky by same-SHA flip detection).

**What is the corpus drawn from?**

| Figure | Value | Source |
|---|---|---|
| repositories active | 77 / 300 (25.7%) | `paper/generated/corpus_stats.md` §1 |
| language split | 71 Java, 6 Python | `paper/generated/corpus_stats.md` §1 |
| unique workflow runs | 175,038 | `paper/generated/corpus_stats.md` §1 |
| unique jobs | 667,398 | `paper/generated/corpus_stats.md` §1 |
| job logs captured | 13,710 | `paper/generated/corpus_stats.md` §1 |
| failed runs with logs/annotations | 13,422 | `paper/generated/corpus_stats.md` §3 |
| logs in the pinned parse | 12,072 | `data/interim/CORPUS_PIN.json` |
| parsed outcome rows | 20,451 | rebuild chain, `analysis/corpus_parse.py` |
| distinct canonical `test_id` | 5,985 | rebuild chain, `analysis/corpus_parse.py` |

**Is any information missing?** Yes, and it is load-bearing:

- **No causal/gold subset.** Docker re-execution of base and head (ROADMAP
  §21.5) was cut for cost (72–120 machine-hours). Every label is observational.
- **No graph tables.** `graph_nodes` / `graph_edges` are excluded from the
  release by D-48; the graph layer is a course deliverable, not part of the
  paper or the release.
- **No `identity_map.parquet`** (node renames between SHAs) — never built.
- **`no_base` is large.** 5,520 of 12,581 run-level rows have no resolvable
  base, so no fault-revealing label can be computed for them at all.

**Are there errors or redundancies?** Known and documented:

- A parser defect read a JUnit 5 **parameter type** as the declaring class,
  producing identifiers such as `Path#someTest` that name no source symbol.
  Fixed at `34aec6d`; it had affected 60 outcome rows across 21 distinct
  identifiers in four repositories, and zero labels.
- Bare class names without a recoverable package are emitted as the simple name
  with `is_fqcn_qualified = false` (D-39). The parser never guesses a package.
- Class-level failure events (Maven `<<< ERROR!`, JUnit 4 `classMethod`) are
  counted, never emitted as test identifiers (D-46).

---

## 3. Collection Process

**How was the data acquired?** Observed, not reported or inferred: harvested
from the public GitHub REST API (Actions runs, jobs, job logs, check-run
annotations, pull requests, pull files and commits). All HTTP goes through one
backoff-governed client against a three-token pool.

**Over what timeframe?**

| Figure | Value | Source |
|---|---|---|
| earliest run started | 2026-08-08T13:48:20Z | `paper/generated/corpus_stats.md` §1 |
| latest run updated | 2026-08-29T21:09:27Z | `paper/generated/corpus_stats.md` §1 |
| harvest wall-clock | 21d 7h 21m | `paper/generated/corpus_stats.md` §1 |
| corpus pin `as_of` | 2026-08-29T14:13:00Z | `data/interim/CORPUS_PIN.json` |

The corpus is **pinned**: `CORPUS_PIN.json` fixes `as_of` and the file count, so
every figure describes one frozen capture rather than a moving target.

**Sampling strategy.** A 300-repository frame (`data/frame/frame_v1.csv`) built
from public repositories meeting activity and language criteria; 77 reached
active capture. Attrition compounds across CI liveness, log availability,
parseability and presence of failures, and is reported per stage rather than
hidden.

**Were individuals notified or did they consent?** No. The data is public
repository activity under each project's own licence, collected within GitHub's
Terms of Service. No private repositories, no private user data.

**Does the dataset contain personal data?** Not in the shipped bundle.
`author_login` is present on every instance but holds a keyed pseudonym, not a
login: the real usernames are recoverable only by whoever holds
`BR_PSEUDONYM_KEY`, which is never committed, printed or shipped. See §4 for the
scheme and §6 for the verification. The underlying `data/interim/` tables, which
are not distributed, do hold live logins.

**Ethical review?** None sought; no human subjects research. GitHub ToS honoured;
public repositories only.

---

## 4. Preprocessing, Cleaning and Labelling

**What preprocessing was done?**

1. **Parsing.** Raw job logs → `TestOutcome` records by harness-specific parsers
   (Maven/Surefire, Gradle, pytest), then canonicalised to a single `test_id`
   format which is the join key for the whole dataset.
2. **Base resolution.** Each head run matched to a base run (`exact`,
   `exact_green`, `ancestor`, `branch_prior`), or marked `no_base`.
3. **Labelling.** A test is fault-revealing for a change when it failed at head
   and did not fail at base. Matrix legs are unioned, with `n_matrix_legs`
   recorded (D-12). Runs with `no_base` emit no labels at all.
4. **Flakiness.** Same-SHA flip detection removes tests observed both passing
   and failing at the identical SHA; this is the `relaxed` → `strict` step.

**Was the raw data saved?** Yes — `data/raw/` holds the captured API responses
and job logs, so every derived table is re-derivable. Success-run logs are
pruned after parsing to stay inside the storage budget; failure logs are kept.

**Pseudonymisation.** `author_login` **is pseudonymised** in the shipped
bundle. Each login is replaced by HMAC-SHA256 over the login keyed by an
operator-held secret (`BR_PSEUDONYM_KEY`), truncated to 16 hex characters;
values only change, column names and types are untouched, and a null login stays
null rather than becoming the hash of the empty string.

The mapping is deterministic for a fixed key, so one author is one pseudonym
across every table and every rebuild, and it is not invertible without the key.
Rotating the key renames every author, which makes two bundles built under
different keys non-joinable — intentionally.

Measured on this bundle (`analysis/build_release.py`): 165,349 instance rows,
1,791 distinct logins in, 1,791 distinct pseudonyms out (no collisions), 0 rows
whose `author_login` is not 16 lowercase hex characters, and 0 rows whose value
matches any login in `data/interim/instances_raw.parquet`. Pinned by
`tests/test_release_pseudonym.py`, whose expected digests were computed with
`openssl dgst -sha256 -hmac`, independently of the implementation.

**Canary string.** The bundle ships `CANARY.txt` containing one fixed,
high-entropy string that appears nowhere else. If a future language model can
reproduce it, BR-Bench is in that model's training data and any evaluation of
that model on BR-Bench is invalid (ROADMAP T1.7, risk T11).

---

## 5. Uses

**What has it been used for?** Nothing published yet. Internally: baseline
change-impact measurements and the gate readings below.

**Current gate readings.**

| Gate | Threshold | Reading | Status | Source |
|---|---|---|---|---|
| Gate 1 | ≥5,000 positives (labels, per D-44) | 4,168/5,000 | **NOT MET** | rebuild chain, `src/label/fault_revealing.py` |

D-44 fixes the reading against the **label** count, not the instance count: a
positive is a (change, test) pair. The instance-based reading (762) is not the
gate.

**What should it not be used for?**

- **Not a safety-critical regression-test-selection oracle.** Labels are
  observational: they record what CI happened to run and report, not what a
  change could have broken. A test absent from the labels may still be affected.
- **Not a flakiness benchmark.** Flakiness is removed by a same-SHA heuristic,
  not adjudicated by re-execution.
- **Not a cross-repository blast-radius dataset.** Impact is within-repository
  only, by construction.
- **Not comparable to causal RTS results.** There is no gold re-executed subset
  to calibrate against.

**Anything that might cause unfair treatment?** The corpus is overwhelmingly
Java (71 of 77 repositories) and skewed towards a few very active projects — the
top repository alone contributes 59,143 of 175,038 runs
(`paper/generated/corpus_stats.md` §5). Any aggregate figure is dominated by
those projects, and a per-repository random-effects treatment is the honest
analysis. Python results rest on 6 repositories and should not be read as a
general statement about Python.

---

## 6. Distribution

**How will it be distributed?** Intended: partitioned Parquet with a documented
schema, plus a HuggingFace `datasets` loader, deposited on Zenodo with a DOI.

**Has it been distributed yet? No.** The current bundle is a **local build
only**. It no longer carries `NOT_PUBLISHABLE.md` — the pseudonymisation blocker
that file existed to record is cleared — but the blockers below are not, so the
bundle still must not be uploaded. `release/` is git-ignored build output and is
regenerated by `uv run --env-file .env python analysis/build_release.py`.

**Open release blockers.**

| Blocker | Status |
|---|---|
| `author_login` pseudonymisation | **PASS** — HMAC-SHA256 applied under `BR_PSEUDONYM_KEY`; 1,791/1,791 logins replaced, 0 raw logins survive (§4) |
| Secret scan (T1.6b) | **PASS** — re-run on *this* pseudonymised bundle: 4 files, 0 BLOCKER findings, 5 REVIEW findings, `analysis/secret_scan.py --root release` |
| Canary string (T1.7) | **PASS** — `release/v0.1/CANARY.txt`, documented constant present verbatim and covered by the checksum manifest |
| SHA-256 checksum manifest | **PASS** — `release/v0.1/CHECKSUMS.sha256` |
| Zenodo deposit | **NOT STARTED — ONE-WAY** |
| DOI mint | **NOT STARTED — ONE-WAY** (fires D-08's one-way naming constraint) |
| HuggingFace dataset card + loader | **NOT STARTED — ONE-WAY** to publish |
| `schema.json` + validator (T1.6a) | **BLOCKED** — frozen `SCHEMAS.md` diverges from on-disk tables in 19 declared columns |

The five REVIEW findings from the secret scan are, per D-45, printed for human
triage and are never fatal: `email`-shaped matches in `cochange.file_a`/`file_b`
(Apple asset filenames of the `AppIcon-20x20@2x.png` form) and in
`failure_message`, plus `internal_host`-shaped matches that are Java package
fragments. These five were produced by re-running the scan on this bundle after
pseudonymisation, not inherited from D-45's earlier run. **A reviewer should
still confirm the redacted samples before any upload.**

A byte-level grep of `release/` for the 1,791 raw logins returns 12 substring
hits across the compressed parquet files. All 12 are accounted for: 7 are logins
of four characters or fewer matching incidentally inside zstd-compressed bytes,
and 5 are longer logins that are substrings of values the bundle ships on
purpose — a repository owner, workflow or bot name that happens to coincide with
a username. Zero hits are unexplained, and the authoritative column-level check
(§4) finds no raw login at all.

**Licence.** To be decided before release. Underlying repository content remains
under each project's own licence; permissive-only selection is intended.

---

## 7. Maintenance

**Who maintains it?** The three authors above, for the duration of the course and
the MSR submission. No long-term maintenance commitment is made, and the
datasheet should say so rather than imply one.

**How can it be updated?** Every table re-derives from `data/raw/` through the
D-49 chain. The corpus pin makes a refresh an explicit act: bump `as_of`,
re-harvest, re-parse, relabel, regenerate.

**Will older versions be supported?** No version has been distributed, so there
is nothing to support. `release/v0.1` was built and formally withdrawn once
before (Phase 014-B) with no DOI minted.

**Known integrity history.** Recorded because a datasheet that hides its own
corrections is not a datasheet:

- **D-49 (2026-10-03).** `outcomes.parquet` on disk predated
  `parsed_outcomes.parquet`, one of its own inputs, by two days. 33 identifiers
  existed only in a parse generation that was no longer on disk, and every
  figure drawn from that file described inputs that had vanished. All earlier
  interim-derived figures are superseded by the rebuild at `34aec6d`.
  `make tables` now refuses to run against a stale artifact
  (`analysis/check_freshness.py`).
- **D-38 / Holdout v5.** The 2026-09-04 held-out scoring was **void**: expected
  classes were derived by rule rather than hand-labelled. No held-out precision
  figure for the parsers is currently defensible; the instrument has been
  regenerated blank for a hand re-label.
- **D-47 binding figure is not currently regenerable.** The published
  5,622/5,985 was measured when 43 repositories were cloned locally. Only the 3
  mini-corpus clones remain, so `analysis/binding_report.py` now covers a
  364-identifier key space. The figure is not wrong; it is not reproducible at
  this commit, which for a Data & Tool Showcase submission is a defect that must
  be fixed before the paper cites it.
