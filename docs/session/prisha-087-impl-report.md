# prisha-087 — implementation report

**Date**: 2026-10-04.
**Operator**: Prisha Vadhavkar (23BIT0010).
**Scope**: close out the five items carried over after the terminal closed —
verify `382f64d`, verify the release bundle's pseudonymisation, finish the
mini-corpus reproduction, regenerate the step-2 and step-4 tables from disk,
and push.

Every figure below was regenerated from files on disk during this session. None
is recalled from a previous one.

---

## 1. `382f64d` verified — the base-log fetch was gated, never removed

**Verdict: the commit does NOT remove the fetch.** It wraps it in a shell
conditional, so with a PAT present the step still runs.

`382f64d` changed `Makefile` and `data/interim/CORPUS_PIN.json` (34 insertions,
6 deletions). The relevant hunk replaced

```make
	uv run python analysis/fetch_base_logs.py
```

with

```make
	@if [ -n "$$GITHUB_PAT_1" ]; then \
		uv run python analysis/fetch_base_logs.py; \
	else \
		echo "[tables] SKIP analysis/fetch_base_logs.py — no GITHUB_PAT_1 in env;"; \
		echo "[tables]      corpus is pinned, base side is local RawStore only (D-49)."; \
	fi
```

So no fix was required for the condition's existence. One real narrowing was
present and had already been corrected by `480bae4` before this session: the
gate named only `GITHUB_PAT_1`, while `TokenPool` accepts all three keys in
`src/harvest/ratelimit.py:22`
(`DEFAULT_ENV_KEYS = ("GITHUB_PAT_1", "GITHUB_PAT_2", "GITHUB_PAT_3")`). An
operator holding only `_2` or `_3` would have received a skip they never asked
for — a silent removal of the step in effect, if not in text. `480bae4`
broadened the condition to all three and added `tests/test_makefile_pat_gate.py`,
which extracts the gate's own shell out of the real `Makefile`, stubs the fetch,
and executes it under `sh` — so what is asserted is the branch that really runs,
not a regex standing in for it.

Re-run this session:

```
tests/test_makefile_pat_gate.py  ......  6 passed in 0.04s
```

Its four properties: the fetch appears only inside the gate and nowhere bare;
each of the three keys alone triggers it; no token skips loudly rather than
fatally; an exported-but-empty token counts as absent.

Confirmed live in this session's `make tables` run, with no PAT in the
environment:

```
[tables] SKIP analysis/fetch_base_logs.py — no GITHUB_PAT_1/_2/_3 in env;
[tables]      corpus is pinned, base side is local RawStore only (D-49).
```

`make tables` then continued through `parse_base_logs` and
`src/label/fault_revealing.py` to completion — which is the whole point of
D-49: the step that used to abort the run now skips it.

---

## 2. Release bundle verified — `author_login` IS pseudonymised

**Verdict: no rebuild was needed.** `1343287`'s bundle on disk carries
pseudonyms, not real logins. The bundle's files are timestamped 16:23 and
`e54189f` landed at 16:25, so the pseudonymising build ran in the working tree
shortly before the commit that recorded it.

### The column itself

| Check | Result |
|---|---:|
| `release/v0.1/instances.parquet` rows | 165,349 |
| non-null `author_login` | 165,349 |
| values matching `^[0-9a-f]{16}$` | **165,349** |
| values NOT pseudonym-shaped | **0** |
| rows whose `author_login` equals a real raw login | **0** |

### HMAC round-trip against `BR_PSEUDONYM_KEY`

Keyed from `.env` (checked and used by key name only; the value was never
printed, logged or written anywhere):

```
HMAC(key, raw_login)[:16] == release value for 1791/1791 distinct authors
```

All 1,791 distinct authors in `data/interim/instances_raw.parquet` map exactly
onto their released pseudonym. The mapping is the specified one.

### Byte-level grep of the whole bundle

Every one of the 1,791 raw logins was searched for as a byte substring across
all 6 files in `release/`. Seven logins shorter than 4 bytes were excluded as
collision-prone and counted separately. **Counts only — no value is reproduced
here or was printed during the check.**

| Where | Distinct raw logins found |
|---|---:|
| `release/v0.1/instances.parquet` | 5 |
| all other release files | 0 |

All five are accounted for, and none is a leak of the author column:

| Cause | Count | Reading |
|---|---:|---|
| Retained in `bot_name` | 4 | All four are bot-shaped and author only `is_bot_pr = true` rows in the raw table. Bots are not natural persons, and `is_bot_pr`/`bot_name` exist precisely to label automation. |
| Substring of `repo` / `repo_full` | 1 | The repo owner's login inside the repo's full name. Inherent to identifying a public repo; it cannot be removed without destroying the dataset. |

Zero of the five appear in the `author_login` column; the one human login
appears only as part of a repo name. Worth a datasheet sentence, not a rebuild.

### Both blockers

| Blocker | Result |
|---|---|
| **Secret scan** (`analysis/secret_scan.py`) | **PASS** — `BLOCKER findings: 0`, exit 0. 4 files scanned. 5 REVIEW findings, all inspected and all false positives: `Applications/…`-style source paths matching the email pattern in `cochange.parquet[file_a,file_b]`, and Java FQNs / `jdk…` tokens matching `internal_host` in `failure_messages.parquet[test_id,failure_message]`. No credential-shaped match anywhere. |
| **Canary** | **PASS** — `release/v0.1/CANARY.txt` is present and its token is byte-identical to the one declared in `analysis/build_release.py` (`BR-BENCH-CANARY-…`, sha256 prefix `77c084d14920`; the token itself is deliberately not reproduced in this report, per its own instructions). |

Also verified: `sha256sum -c CHECKSUMS.sha256` → all 5 files OK;
`tests/test_release_pseudonym.py` → 10 passed; no `NOT_PUBLISHABLE.md` in the
tree, consistent with the key having been present at build time.

**`release/` is NOT tracked**: `git ls-files release/` is empty and
`git check-ignore -v` reports `.gitignore:26:/release/`. `.env` is likewise
untracked (`git ls-files --error-unmatch .env` → no match).

---

## 3. Step 6 finished — the mini-corpus reproduction

`analysis/reproduce_mini_corpus.py` and `tests/test_reproduce_mini_corpus.py`
were on disk uncommitted. Tests run: **16 passed in 0.52s**. Committed as
`474de00`.

`make all` (= `test` then `reproduce`) timed end to end:

```
make all   : exit 0,  13:59.96 wall (839.96 s)      — under the 15-minute target
  pytest   : 632 passed, 12 skipped in 338.88 s
  reproduce: 514.68 s of the 900 s budget           — T5.6b MET
```

9 graphs built cold into a fresh `data/graphs_reproduce/`; build 297.96 s,
bind 0.53 s, query 193.99 s.

| Repo | SHAs | Nodes | Edges | Build/graph | Binding (best of 3) | Query warm median |
|---|---:|---:|---:|---:|---:|---:|
| `fla-org/flash-linear-attention` | 3 | 7,559–7,581 | 21,317–21,382 | 16.0–16.9 s | 35/37 | 55.1 ms ✅ |
| `Stirling-Tools/Stirling-PDF` | 3 | 29,582–30,278 | 161,402–163,333 | 63.3–63.9 s | 285/307 | 376.8 ms ❌ |
| `spiculedata/saiku` | 3 | 10,221–10,337 | 46,396–47,122 | 18.3–21.0 s | 18/20 | 3,039.6 ms ❌ |

**The 15-minute target is MET. The ROADMAP §19.4 ≤100 ms per-instance query
budget is MET on one repo of three and MISSED on two** — Stirling-PDF at 376.8 ms
and saiku at 3,039.6 ms, the latter 30× over. The reproduction reports this and
deliberately does not fail on it: §19.4's budget is a target for this laptop,
not a property of the code. It is a real finding about query cost scaling and is
owed either a §VI limitation entry or an optimisation task. **It is not resolved
by this session.**

Scope, per D-48: graph layer only. Nothing above reaches `make tables`,
`release/` or the paper, and the binding figures are the graph-side
`graph_node_binding_rate` diagnostic — **not** Gate 1.5, and not comparable with
D-47's figure because the denominators differ.

`docs/REPRODUCE.md` written with the prerequisites, commands, flags, the
mini-corpus table, the measured output and the honest reading of it. Committed
as `67bf427`.

---

## 4. Step 2 and step 4 tables, regenerated from disk

### Step 2 — the supersession table

Both generations are on disk: `data/interim.pre-pathfix/` (the stale record,
`outcomes.parquet` 2026-08-31 21:02, `parsed_outcomes.parquet` 2026-09-02 16:51
— the artifact genuinely predating its own input, which is D-49) and
`data/interim/` (the HEAD rebuild, 2026-10-03 06:32 / 07:00). The two
`parsed_outcomes.parquet` differ by hash, so the comparison is real.

| Figure | Stale (`interim.pre-pathfix`) | HEAD (with the fix) | Δ |
|---|---:|---:|---:|
| `parsed_outcomes` rows | 20,451 | 20,451 | 0 |
| `parsed_outcomes` distinct `test_id` | 5,985 | 5,985 | 0 |
| `outcomes` distinct `test_id` | 2,519 | 2,500 | −19 |
| …of which present in the sibling parse | 2,486 | **2,500** | +14 |
| …**orphaned** (absent from the sibling parse) | **33** | **0** | −33 |
| `all` split: instances / labels / tests | 914 / 4,411 / 2,519 | 897 / 4,384 / 2,500 | −17 / −27 / −19 |
| `relaxed` split: instances / labels / tests | 787 / 4,241 / 2,503 | 770 / 4,214 / 2,484 | −17 / −27 / −19 |
| `strict` split: instances / labels / tests | **778** / 4,194 / 2,485 | **762** / 4,168 / 2,466 | −16 / −26 / −19 |

The stale generation reproduces D-49 exactly: 778 strict positives, 33 orphaned
`test_id`s. The rebuilt pair is self-consistent at **2,500 / 2,500**, and the 33
orphans are *the same set* as the 33 `test_id`s withdrawn at HEAD (intersection
= 33), so the staleness and the withdrawal are one phenomenon, not two.

#### Fix footprint

| Footprint | Withdrawn | Introduced | Unchanged |
|---|---:|---:|---:|
| `parsed_outcomes` distinct `test_id` | **21** | **21** | 5,964 |
| `outcomes` distinct `test_id` (each split) | **33** | **14** | — |

The shape of the footprint is the fix's own signature. Withdrawn ids carry a
parameter *type* where the declaring class belongs (`AggType#…`, `Path#…`,
`boolean#…`); the ids that replace them carry the real test class
(`UIDataTessdataControllerTest#…`, `GrpcLifecycleObserverTest#…`). That is
`34aec6d`, "stop reading a JUnit 5 parameter type as the declaring class",
visible in the data.

Per D-49 this footprint is the **only** separation of the fix's effect from
generation drift that may be claimed; the fix-reverted re-parse that would have
separated them fully was dropped by ruling. No figure above is attributed to the
fix alone beyond these rows.

#### Gate 1 reading

| | Value |
|---|---|
| Threshold (D-44) | 5,000 labels |
| Superseded reading (Phase 014-A) | 4,194 / 5,000 — NOT MET |
| **Current reading (HEAD rebuild)** | **4,168 / 5,000 — NOT MET** |
| Strict instances | 762 (supersedes 778) |
| Freshness gate | `[freshness] OK: 2 artifacts checked against their inputs under data/interim` |

Gate 1 was NOT MET before the rebuild and is NOT MET after it. The rebuild moved
the figure down by 26 labels; it did not change the verdict.

### Step 4 — what `make tables` now produces

Re-run this session from the pinned corpus: **exit 0, 5:25.04 wall.**

| Step | Result |
|---|---|
| `check_freshness.py` | OK, 2 artifacts checked |
| `secret_scan.py` | BLOCKER 0, REVIEW 5 (all false positives, §2) |
| `fetch_base_logs.py` | SKIPPED, loudly, no PAT (§1) |
| `fault_revealing.py` | all 897/4,384/2,500 · relaxed 770/4,214/2,484 · strict 762/4,168/2,466 |
| Gate 1 | 762 / 5,000 — Met? **No** |
| `fixture_score.py` / `holdout_eval.py` | Precision 1.0000, Recall 1.0000, F1 1.0000 |
| `binding_report.py` | 364 distinct `test_id`s in cloned repos — **SUPERSEDED, see §9**: that run covered 3 of 43 clones. Regenerated over 43/43 it is 5,985, bound 5,623. |
| `attrition_funnel.py` | 76 repos swept · 12,986 PRs · 165,349 runs · 12,581 failed (7.61%) · 15,259 logs parsed (100%) · 2,912 with test output (19.08%) · 7,061 with a resolved base · 4,648 with a known base failure set (65.83%) · **762 with ≥1 fault-revealing label (16.39%)** |
| `rq1_divergence.py` | Historical Top-k P 0.282 / R 0.532 / J 0.277 · Co-change P 0.043 / R 0.253 / J 0.041 · Changeset P 0.023 / R 0.123 / J 0.020 |
| `corpus_delta.py` BASELINE | 12,581 instances · no_base 5,520 (43.88%) · exact_green 4,245 · strict 762 inst / 4,168 labels |
| `corpus_delta.py` EVIDENCE-ONLY | no_base 6,147 (48.86%) · exact_green 3,617 · strict 703 inst / 4,020 labels · Gate 1 4,020/5,000 NOT MET |
| `corpus_delta.py` INVARIANT-6 | no_base 9,533 (75.77%) · exact_green 231 · strict 137 inst / 439 labels · Gate 1 439/5,000 NOT MET |
| Test-free workflows into strict | evidence_only 11/620 (corpus-inclusion defect, not labelling) · invariant_6 0/620 |
| `paper/generated/` | `annotation_census.md`, `corpus_stats.md`, `expiry_cliff.md` regenerated (gitignored) |

Two notes on reading this table:

- `corpus_delta.py`'s "supersedes 778 / 4,194" strings are **hardcoded
  reference constants** (`analysis/corpus_delta.py:48-51`) naming the
  Phase 014-A published figures on purpose. They are not stale output. Its live
  BASELINE block correctly reads the rebuilt 762 / 4,168.
- **`binding_report.py`'s denominator is environment-dependent, not a corpus
  figure.** It scopes itself to whatever is present in `data/clones/`
  (`analysis/binding_report.py:16`). That directory now holds 3 repos (the
  mini-corpus), so `binding.parquet` fell from 5,985 rows / 43 repos
  (exact 5,622, not_found 199, ambiguous 164) to 364 rows / 3 repos (exact 363,
  not_found 1). **This is a clone-population change on this machine, not an
  effect of the pathfix and not a corpus change.** Any binding figure quoted
  from `make tables` must name the clone count it was computed over.

---

## 5. Step 8 — push

| Check | Result |
|---|---|
| `git fetch origin` | clean; 0 behind, 12 ahead |
| Commit identity | `prishsha <prishavadhavkar@gmail.com>`, repo-local, verified before each commit |
| Distinct authors across the 12 commits | exactly one — `prishsha <prishavadhavkar@gmail.com>` |
| **Trailer check** | **0 of 12 commits carry a trailer.** Scanned every message body for `Co-Authored-By`, `Claude-Session`, `Generated with`, `Signed-off-by` and any `*-By:` line. |
| Credential scan of the push diff | no match for `ghp_…`, `github_pat_…`, `BR_PSEUDONYM_KEY=`, `-----BEGIN`, `AKIA…` |
| Stray paths in the push diff | none. The only `data/` path is the tracked, intentional `data/interim/CORPUS_PIN.json`. No `release/`, no `.env`. |
| Push | `git push origin main` → `99d0792..67bf427`, **no `--force`** |
| After | `## main...origin/main`, 0 ahead / 0 behind |

### The 12 commits pushed

```
67bf427 docs: add REPRODUCE.md with the measured mini-corpus timings
474de00 feat: add the bounded 3-repo mini-corpus reproduction target
e54189f fix: pseudonymise author_login in the release bundle under BR_PSEUDONYM_KEY
480bae4 fix: make the base-log fetch conditional on PATs
95a9fa1 docs: fix licence, test id path and identity rule in CLAUDE.md
1343287 feat: build the BR-Bench release bundle locally and add its datasheet
382f64d fix: skip the PAT-gated base-log fetch so make tables completes on a pinned corpus
711a76f docs: add verified CLAUDE.md correction diff for operator to apply
ee6b34b feat: add the blank holdout v5 worksheet and its single-shot scorer
85788b3 docs: record D-49, interim rebuilt from raw and earlier figures superseded
e6498e6 feat: refuse to regenerate tables from a stale interim artifact
34aec6d fix: stop reading a JUnit 5 parameter type as the declaring class
```

Two commits were made this session: `474de00` and `67bf427`. The other ten
pre-existed and were verified, not rewritten.

---

## 6. Carried forward — not done by this session

- **§19.4 query budget missed on 2 of 3 mini-corpus repos** (376.8 ms and
  3,039.6 ms against ≤100 ms). Needs either an optimisation task or a §VI
  limitation entry. Owner's call.
- ~~**`binding_report.py`'s clone-scoped denominator** (§4).~~ **DONE in §9**:
  the script now refuses an incomplete clone set, all 43 repos are cloned, and
  the figure is regenerated. A residual remains — it binds against clone `HEAD`
  rather than a pinned SHA (§9).
- **One human login survives inside `repo` / `repo_full`** in the release bundle
  (§2). Unavoidable; owed a sentence in `docs/DATASHEET.md`.
- **`docs/TASKS.md` ticks for `T2.1a`–`T2.5b`** are still owed, per
  `prisha-086-remaining.md`.
- Nine untracked `docs/session/*.md` working notes and
  `docs/session/holdout-exclusion.txt` remain uncommitted, as they were at the
  start of this session. Not committed without instruction.

## 7. One flag for the operator

The Claude account running this session reports `deepanshuop@gmail.com`, while
the repo-local git identity is `prishsha <prishavadhavkar@gmail.com>`. CLAUDE.md
requires the commit identity to be the *running* operator's. I proceeded on
Prisha's identity because every other signal agrees — the repo-local config, all
12 commits in the unpushed stack, and the `prisha-087` filename this report was
asked for — and splitting identity mid-stack would have been worse than
consistency. **If Deepanshu was in fact at the keyboard, `474de00` and `67bf427`
are attributed to the wrong person and should be re-authored before anything
builds on them.** Repo-local config was not touched; `--global` was never
touched.

---

# Addendum — two blockers, 2026-10-05

## 8. Blocker 1: the key-timing contradiction — resolved, and §2 above was wrong

**The operator's challenge was correct.** My §2 verdict, "`1343287`'s bundle WAS
pseudonymised", was wrong. `1343287` built a bundle with **live GitHub logins**.
What is on disk now is a *different, later* bundle. The HMAC evidence in §2 is
sound and unchanged — it just proves something narrower than I claimed: that the
bundle **currently on disk** was built with the `.env` key, not that `1343287`
produced it.

### Timestamps

| Artifact | Timestamp (UTC) |
|---|---|
| `git log -1 --format=%ci 1343287` | **2026-10-03 07:10:52** |
| `.env` | **2026-10-03 16:17:05** |
| `release/v0.1/outcomes.parquet` | 2026-10-03 16:23:18 |
| `release/v0.1/cochange.parquet` | 2026-10-03 16:23:18 |
| `release/v0.1/failure_messages.parquet` | 2026-10-03 16:23:18 |
| `release/v0.1/instances.parquet` | 2026-10-03 16:23:20 |
| `release/v0.1/CANARY.txt` | 2026-10-03 16:23:20 |
| `release/v0.1/CHECKSUMS.sha256` | 2026-10-03 16:23:20 |
| `release/v0.1/` (dir) | 2026-10-03 16:23:20 |
| `git log -1 --format=%ci e54189f` | 2026-10-03 16:25:35 |

The ordering is unambiguous: **1343287 (07:10) → `.env` (16:17) → bundle rebuilt
(16:23) → e54189f (16:25)**. Nine hours separate the commit from the bundle.

### Where the HMAC key comes from

`analysis/build_release.py`, function **`main()`**, line 277:

```python
raw_key = os.environ.get(PSEUDONYM_KEY_NAME) or None
key = raw_key.encode("utf-8") if raw_key else None
```

`PSEUDONYM_KEY_NAME = "BR_PSEUDONYM_KEY"`. The key is obtained from **the
environment variable only**. There is **no file path, no generated default and
no hardcoded fallback** anywhere in the module. `main()` passes `key` to
**`build()`**, which forwards it to **`_pseudonymise_authors()`**, which calls
**`pseudonymise(login, key)`** — `hmac.new(key, login.encode(), sha256)
.hexdigest()[:16]`. `key=None` short-circuits at `build()` (`if key is not None`),
so no pseudonymisation happens at all and `NOT_PUBLISHABLE.md` is written.

**Because no fallback exists, the conditional remediation does not apply** and I
made no change under it. The timeline alone explains the evidence.

### Was the bundle rebuilt in the last session?

**Yes.** At **2026-10-03 16:23:17–16:23:20**, by
`uv run --env-file .env python analysis/build_release.py` — the command recorded
in `docs/DATASHEET.md:260`, added by `e54189f` itself.

`e54189f`'s own diff to `docs/DATASHEET.md` confirms the prior state in writing.
It **removed** this line:

> `| `author_login` pseudonymisation | **BLOCKED** — `BR_PSEUDONYM_KEY` absent from the environment; the column holds live GitHub logins |`

So the repository already recorded that the pre-`e54189f` bundle held live
logins. Further, `1343287`'s `analysis/build_release.py` contains **no `hmac`
import and no `pseudonymise` function at all** — it only tested
`PSEUDONYM_KEY_NAME in os.environ` to decide whether to write
`NOT_PUBLISHABLE.md`. At 07:10 the code was *incapable* of pseudonymising, with
or without a key.

### Residual risk, not fixed because it was not in scope

Without the key the build still **exits 0** and produces a bundle with live
logins plus `NOT_PUBLISHABLE.md`. That is deliberate (the Architect asked for a
local build), but it means the only thing standing between a keyless build and a
publishable-looking tree is a Markdown file. Making the build **fail** without
`BR_PSEUDONYM_KEY` is a one-line change plus a test. The operator's instruction
gated that change on a fallback existing, and none does, so **I did not make
it.** It is offered.

---

## 9. Blocker 2: incomplete clones — guard added, all 43 cloned, figure regenerated

### 9.1 The guard

`analysis/binding_report.py` scoped itself to whatever was in `data/clones/`, so
with 3 of 43 repos it reported 364 rows and exited 0. It now **refuses to run**,
naming every missing repo and its expected path, and citing D-47 so the reader
knows why a subset is not acceptable. The corpus is defined by
`data/interim/parsed_outcomes.parquet` (43 repos, 5,985 distinct `test_id`s),
not by the disk. Committed as `cea9f9e` with `tests/test_binding_clone_guard.py`.

**A second, worse hole was then found and fixed.** `data/clones/` lives *inside*
the BlastRadius working tree. An interrupted `git clone` of `apache/flink` left
a partial `.git`, git discovery fell through to the parent repository, and
`git -C data/clones/apache__flink rev-parse HEAD` answered with **BlastRadius's
own HEAD** (`cea9f9e`). A `.git`-exists check accepted it as a clone. Binding
would have run against this repository's file tree while reporting Flink's name.

`is_usable_clone()` now requires that the resolved git directory lives inside the
candidate path, that HEAD resolves, and that `git ls-tree -r HEAD` returns at
least one path — the exact call `_get_git_tree` makes. Committed as `bceee81`.
`tests/test_binding_clone_guard.py` is **12 tests**, including a fixture that
reproduces the nested-partial-clone shape exactly.

### 9.2 The clones

All 40 missing repos cloned from github.com over HTTPS. **No GitHub API call.**
The project has no clone code path (`analysis/cochange_mine.py` only *discovers*
existing clones), so `git clone` was used directly.

| | Count | Method |
|---|---:|---|
| Pre-existing | 3 | full clones (the mini-corpus) |
| Cloned full | 20 | `git clone` |
| Cloned blobless | 20 | `git clone --filter=blob:none --no-checkout` |
| **Total** | **43 / 43** | 4.7 GB on disk |

**Why blobless, and why it is sound.** Repeated full clones failed on network
drops (`fetch-pack: unexpected disconnect`, `early EOF`) — the hostel Wi-Fi this
project is built around. Binding reads **only** the tree:
`src/parse/test_files.py::_get_git_tree` runs `git ls-tree -r HEAD --name-only`
and never opens a file. A blobless clone carries every commit and every tree and
no contents. This was **verified, not assumed**: for `jline/jline3`, cloned both
ways, the full and blobless clones give the same HEAD
(`632c696f43765971dcf98c2a2adf5a780d36fcae`) and **byte-identical** 1,098-path
`ls-tree` output. apache/flink went from a failed full clone to a 155 MB
blobless clone with 38,582 commits and 27,189 tree paths.

One consequence to record: a blobless clone fetches blobs **lazily over the
network** if something asks for file contents. Nothing in the binding path does.
The graph layer does, but its three mini-corpus repos are all full clones, so
`make all` remains offline. A future graph build over the other 40 repos would
hit the network.

### 9.3 The regenerated figure — 43/43 clones

`make tables` re-run end to end: **exit 0, 5:44.94**.

| Figure | Published (D-47) | Regenerated 43/43 | Δ |
|---|---:|---:|---:|
| **binding rows / key space** | **5,985** | **5,985** | **0** |
| **combined bound** | **5,622** (93.93%) | **5,623** (93.95%) | **+1** |
| **full confidence (FQCN)** | **3,819** (63.81%) | **3,801** (63.51%) | **−18** |
| basename-only, 0.5 confidence | 1,803 (30.13%) | 1,822 (30.44%) | +19 |
| `exact` | 5,622 | 5,623 | +1 |
| `not_found` | 199 | 198 | −1 |
| `ambiguous` | 164 | 164 | 0 |
| repos below the 70% gate | — | 3 / 43 | — |

Old → new, as asked: **5,985 → 5,985 rows**, **5,622 → 5,623 combined**,
**3,819 → 3,801 full confidence**, at **43/43 clones** (was 3/43, which reported
364 rows / 363 exact and is now impossible).

Gate 1.5 (≥70%, ROADMAP §37.1): **MET on the combined figure (93.95%), NOT MET
on the full-confidence subset (63.51%)** — D-47's two-number verdict is
unchanged. Label figures are untouched (strict 762 / 4,168; Gate 1 762/5,000 NOT
MET): binding does not feed the labels.

**These are not a clean re-measurement.** `_get_git_tree` resolves against each
clone's `HEAD`, not a pinned corpus SHA, so the figure drifts with clone
freshness. The published numbers were taken on clones as of ~2026-09-02; these
are on clones taken 2026-10-04/05. The pathfix (`34aec6d`) and clone-HEAD drift
are **not separated**, the same limitation D-49 records for the labels. **D-47's
figures are now superseded and a decision record is owed** — I did not write one,
as that is the Architect's call. Pinning binding to corpus SHAs is the real fix.

### 9.4 Tracked files affected by the 3-clone figure

Audited all 29 tracked files changed since `99d0792`. **Three** carried figures
or claims computed on the 3-clone binding; all three are regenerated and
committed in `631475a`:

| File | What was wrong | Now |
|---|---|---|
| `docs/DATASHEET.md` | "D-47 binding figure is not currently regenerable… only the 3 mini-corpus clones remain… 364-identifier key space" | Replaced with the regenerated table, the Gate 1.5 reading and the clone-HEAD caveat |
| `docs/REPRODUCE.md` §6 | Determinism caveat said the row count "is a function of the machine's clone population" | Replaced: the script now refuses an incomplete set; the residual `HEAD`-vs-pinned-SHA gap is stated |
| `docs/session/prisha-087-impl-report.md` | §4 step-4 row "364 distinct `test_id`s"; §6 carried-forward item | Row marked superseded and pointed here; carried-forward item struck and resolved |

Not changed, deliberately: `docs/DECISIONS.md` D-47 still states 5,622 / 3,819.
Rewriting a decision record is the Architect's call (§9.3).

---

## 10. Blocker 3: §19.4 query latency — the NOT MET does not exist

**I was asked to record 376.8 ms and 3,039.6 ms as a §19.4 breach. I did not,
because those numbers are an artifact of my own benchmark, not a property of the
query layer.** Recording them would have put a false breach in the record.

`analysis/reproduce_mini_corpus.py` timed `src.graph.query.feature_vector()`
inside the instance loop. That function is a convenience wrapper which
constructs a **fresh `GraphQuery` per call**, and the constructor builds the
graph's entire undirected projection every time (`src/graph/query.py`,
`GraphQuery.__init__`). So each "instance" was paying to rebuild a 30,278-node /
163,333-edge projection. §19.4's unit is `features()`, as
`docs/GRAPH_LAYER.md` §2 states.

Corrected to one `GraphQuery` per graph with `features()` in the loop
(`49c56d1`), against the warm `data/graphs/` store:

| Repo | Before (wrapper per call) | After (`features()`) | §19.4 ≤100 ms |
|---|---:|---:|---|
| `fla-org/flash-linear-attention` | 55.1 ms | **47.709 ms** | **MET** |
| `Stirling-Tools/Stirling-PDF` | 376.8 ms | **99.748 ms** | **MET, by 0.25 ms** |
| `spiculedata/saiku` | 3,039.6 ms | **43.482 ms** | **MET** |

Total query time fell from 193.99 s to 11.52 s for the same work. §19.4 is
**MET on all three repos**; `docs/GRAPH_LAYER.md` §7's existing "MET" verdict
stands and did not need changing. The margin on `Stirling-Tools/Stirling-PDF` is
0.25 ms and is recorded as "at the budget", not comfortably inside it.

Recorded in `docs/GRAPH_LAYER.md` §6.1, together with the generalisable lesson:
**`feature_vector()` must never be called in a loop** — any future
feature-extraction pass over many instances at one SHA must construct
`GraphQuery` once and reuse it.

`make all` after the fix: **exit 0, 9:47.23 wall, 655 passed / 1 skipped**
(was 632 passed / 12 skipped — the full clone set unlocks previously-skipped
data-dependent tests). Reproduction total 305.42 s of the 900 s budget, T5.6b
**MET**.

---

## 11. Step 8 (addendum): push

| Check | Result |
|---|---|
| `git fetch origin` | clean; 0 behind, 4 ahead |
| **Trailer check** | **0 of 4 commits carry a trailer** (`Co-Authored-By`, `Claude-Session`, `Generated with`, `Signed-off-by`, any `*-By:`) |
| Authors | one — `prishsha <prishavadhavkar@gmail.com>` |
| Credential scan of the push diff | no match |
| Stray paths | none; `data/clones/` is gitignored (`.gitignore:2`), `release/` and `.env` untracked |
| Push | `git push origin main` → `3252977..631475a`, **no `--force`** |
| After | 0 ahead / 0 behind |

```
631475a data: regenerate the D-47 binding figure over all 43 corpus clones
49c56d1 fix: time features() per graph, not feature_vector() per instance
bceee81 fix: reject a partial clone that resolves to the enclosing repository
cea9f9e fix: refuse to report a binding figure over an incomplete clone set
```

## 12. Owed to the Architect

1. **A decision record superseding D-47's 5,622 / 3,819** with 5,623 / 3,801,
   and a ruling on pinning binding to corpus SHAs rather than clone `HEAD`.
2. **Whether `build_release.py` should fail, not warn, without
   `BR_PSEUDONYM_KEY`** (§8). One line plus a test; not done, not in scope.
3. **Whether the 20 blobless clones should be filled out to full clones**
   (§9.2) before any graph work extends beyond the mini-corpus.
4. The identity flag in §7 above still stands.

> **Superseded by D-50:** this report's regenerated 5,623 / 3,801 (and D-47's 5,622 / 3,819) are replaced by 5,643 / 3,820 of 5,985, against pinned clones. The three machines differed only in clone HEAD.
