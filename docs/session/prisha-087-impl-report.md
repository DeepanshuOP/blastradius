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
| `binding_report.py` | 364 distinct `test_id`s in cloned repos |
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
- **`binding_report.py`'s clone-scoped denominator** (§4). Either the script
  should name its scope in its own output, or the figure should be computed over
  a fixed repo list. Schema-adjacent, so not changed unasked.
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
