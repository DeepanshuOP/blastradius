# Phase 020 — `test_id` Parser Survey & Blast Radius (READ-ONLY)

**Scope**: Read-only survey. No file under `src/`, `tests/`, or `docs/` was modified
except the creation of this report. `docs/SCHEMAS.md` was not edited. No defect was
fixed. No harvest, sweep, or HTTP request was issued. No background execution.

**Headline**: All three defects reproduce from bytes on disk. But the blast radius is
not what the 012B write-up implies — the parser layer and the *stored dataset* diverge,
because `normalize_test_id()` sits between them and silently repairs two of the three
defects while **deleting** the outcome for the third. The escalation gate in Phase 4
fires: `fqcn_incomplete` is **NOT DECLARED** in `docs/SCHEMAS.md`.

---

## PHASE 1 — How `test_id` is constructed today

### 1. The construction site in each parser (by function name)

| Module | Function that builds the emitted `test_id` | Literal separator / prefix strings |
|---|---|---|
| `src/parse/log_pytest.py` | `parse_pytest_log_with_stats()` | **None.** No separator is ever composed. |
| `src/parse/log_maven.py` | `_reconcile_maven_outcomes()` | `"#"` only, via `f"{cls}#{meth}"` and `f"{fqn_cls}#{meth}"` |
| `src/parse/log_gradle.py` | `parse_gradle_log_with_stats()` | `"#"` only, via `f"{current_class}#{method_raw}"`, `f"{cls_name}#{method_raw}"`, `f"{joined_fqcn}#{meth_part}"` |

**`log_pytest.py` composes nothing.** `parse_pytest_log_with_stats()` assigns
`test_id=raw_node_id` — the regex capture group, verbatim, after `_clean_line()` has
stripped ANSI escapes, ISO-8601 timestamps, and channel prefixes. There is no
`test_id = f"..."` statement anywhere in the module. The `::` in a pytest id is the
separator pytest itself printed; the parser never writes one. The capture groups come
from `_SUMMARY_LINE_RE`, `_PROGRESS_LINE_RE`, `_XDIST_PROGRESS_LINE_RE`, and
`_PYTEST_TIMEOUT_LINE_RE`; the only gate on them is `_is_valid_pytest_node_id()`.

**`log_maven.py`** builds ids in `_reconcile_maven_outcomes()` at four sites, all `#`.
A fifth site emits a bare `test_id = meth` (method with no class) for unreconciled
FORM D matches.

**`log_gradle.py`** builds ids in `parse_gradle_log_with_stats()` at three sites in the
scan loop (S1 indented-method, S2 single-line, S3/S4 chevron) plus one in the Pass-1
suffix-reconciliation block, all `#`. Gradle's own `" > "` chevron is split on, never
emitted.

**No parser emits `::` for a Java test.** The `::` shown for Java in the 012B report is
not parser output — see Phase 2, D2/D3.

### 2. Does a `TestId` dataclass with `.canonical()`, `.params`, `.raw`, `.lang` exist?

**PARTIALLY — and the specified `.canonical()` is NOT PRESENT.**

ROADMAP §34.4 C.2 specifies: *"Return a TestId dataclass with `.canonical()`, `.params`,
`.raw`, `.lang`."* What exists in `src/parse/test_ids.py`:

```python
@dataclass(frozen=True)
class TestId:
    lang: str
    raw: str
    canonical: str
    params: str | None = None
    class_name: str | None = None
    method_name: str | None = None
    path: str | None = None

    __test__ = False
```

`.params`, `.raw`, `.lang` are present as specified. **`.canonical()` as a method is NOT
PRESENT** — `canonical` is a plain `str` field, accessed as `tid.canonical`, never
called. Every call site in the repo (`analysis/corpus_parse.py`,
`analysis/parse_base_logs.py`) uses the attribute form, so the divergence is internally
consistent and is a documentation drift, not a live bug. Three fields beyond the spec
(`class_name`, `method_name`, `path`) were added; `resolve_test_file()` depends on all
three.

### 3. How each parser reaches `vendor/graphify-br/graphify/ids.py`

**None of them do. There is no import path from any parser to the vendored module.**

A repo-wide grep for `from graphify`, `import graphify`, and `graphify.` outside
`vendor/` returns exactly two hits, both **docstring prose** in
`src/parse/test_ids.py` inside `derive_node_id()`:

```
src/parse/test_ids.py:428:    This function mirrors the normalization recipe in vendor/graphify-br/graphify/ids.py
src/parse/test_ids.py:445:    Must be re-verified if vendor/graphify-br is updated.
```

`derive_node_id()` **re-implements** the five-step recipe (`NFKC` → `NFKC(casefold)` →
`[^\w]+`→`_` → `_+`→`_` → `strip("_")`) inline rather than importing `normalize_id`.
The docstring states this explicitly and flags the manual-sync obligation. So
ROADMAP §34.4 C.2's *"Reuse the … recipe from `vendor/graphify-br/graphify/ids.py`"* was
satisfied by copy, not by call — the exact ID-drift failure mode the vendored module's
own docstring was written to prevent. This is a standing risk, not one of the three
defects.

---

## PHASE 2 — Reproduction against real bytes

**Hypothesis (a) is FALSIFIED.** All three raw logs are present on disk:

| File | Bytes |
|---|---|
| `tests/fixtures/holdout_v4/dask__distributed__084757793457.txt` | 1,322,948 |
| `tests/fixtures/holdout_v4/linkedin__brooklin__077863844421.txt` | 395,685 |
| `tests/fixtures/holdout_v4/sirixdb__sirix__092352347826.txt` | 80,122 |

All three defects **REPRODUCE**. Two reproduce in a form that differs from the 012B
quoted output.

### D1 — pytest params retained: **REPRODUCES EXACTLY**

`classify_log_format` → `pytest`; direct parser and dispatch agree, 1 outcome.

```
'distributed/tests/test_active_memory_manager.py::test_RetireWorker_stress[False-17-100]'
```

Matches the 012B quoted output byte for byte. `[False-17-100]` is retained in the
canonical position, violating D-32.

### D2 — Gradle suite prefix: **REPRODUCES, but the quoted separator is wrong**

`classify_log_format` → `gradle`; 1 outcome.

```
'Gradle suite#com.linkedin.datastream.server.TestCoordinator.testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation'
```

012B quotes the emitted identifier as `Gradle suite::com...` and calls
`Gradle suite#com...` the "internal intermediate". **This is inverted.** The `#` form is
what the parser emits and what any consumer receives; the `::` form is produced only by
`_normalize_comparison_key()` in `src/parse/dispatch.py`, which exists solely to build a
throwaway dedup key for the `ambiguous` merge branch and never touches
`TestOutcome.test_id`. No `::` Java identifier is emitted anywhere in the pipeline.

Both halves of the defect are real: `"Gradle suite"` is taken as the class, and the
`<fqcn>.<method>` tail is taken whole as the method with the `.` unsplit.

### D3 — Java package dropped: **REPRODUCES, but the quoted form is wrong twice**

`classify_log_format` → `gradle`; 2 outcomes.

```
'RegionOnlyPredicateCountTest#negationConjoinedWithAnAnchoringLeafIsRepresentable()'
'RegionOnlyPredicateCountTest#numericAndBooleanFuseIntoOnePass()'
```

012B quotes `RegionOnlyPredicateCountTest::negationConjoined...`. Two divergences:
the separator is `#`, not `::` (as in D2); and the **trailing `()` is retained** in the
raw parser output, which 012B omits. The package drop itself — the substance of the
defect — is confirmed: `io.sirix.query.scan.` is absent, and the diagnosed cause holds
(`stack_fqcns` is populated only by `_AT_FRAME_RE`, and this log's JUnit 5 assertion
traces carry no `at io.sirix...` frame, so `candidates` is empty and the Pass-1 suffix
join does not fire).

---

## PHASE 3 — Blast radius

### 4. Every consumer of `test_id`

105 `test_id` references across 18 files. By consumer:

| File | Function / site | How it consumes `test_id` |
|---|---|---|
| `src/parse/test_files.py` | `resolve_test_file()` | **Binding.** Consumes the parsed `TestId` *object*, not the string — branches on `.lang`, then on `.class_name` (Java) or `.path` (Python). Java with no `.` in `class_name` falls to a basename-only match at `confidence=0.5`; empty `class_name` returns `status="unqualified"`. |
| `analysis/corpus_parse.py` | main parse loop | **The choke point.** Calls `normalize_test_id(o.test_id)`; drops the outcome if `None`; writes `tid.canonical` to `test_id` and `tid.params` to a separate `params` column. Also derives `is_fqcn_qualified` by testing for `.` in the pre-`#` segment. Writes `data/interim/parsed_outcomes.parquet`. |
| `analysis/parse_base_logs.py` | base-log parse loop | Same normalize-then-write pattern for base runs; writes `data/interim/base_outcomes.parquet`. |
| `analysis/binding_report.py` | binding driver | Groups `(repo, test_id)` distinct, re-runs `normalize_test_id`, calls `resolve_test_file()`, writes `binding.parquet`. |
| `analysis/rq1_divergence.py` | `main()` | **RQ1 Axis 2.** Builds `bound = binding[status=='exact'].set_index(['repo','test_id'])['resolved_path']`, then maps every outcome row to a file path via `bound.get((repo, test_id))`. A `test_id` that fails to bind is `dropna`'d out of the accuracy denominator entirely. |
| `analysis/rq1_divergence.py` | `main()` | **The co-change join.** `run_to_gt[(repo, run_id)]` is a set of *resolved paths*, reached only through the `(repo, test_id)` → path lookup above. The co-change proxy is scored against that set. `test_id` is the sole bridge from a CI failure to a file, and therefore to the co-change table. Axis 1 (applicability) does not touch `test_id`; Axis 2 depends on it completely. |
| `src/label/fault_revealing.py` | label computation | Groups and set-joins on `(run_id, test_id)` for head-vs-base differencing, and on `(head_sha, workflow_id, test_id)` for same-SHA flip detection. Reads `parsed_outcomes.parquet`. |
| `analysis/corpus_delta.py`, `analysis/corpus_instances.py`, `analysis/attrition_funnel.py`, `analysis/verify_exact_green.py` | various | Read `parsed_outcomes.parquet`; count distinct `test_id` or join on it. |
| `analysis/log_yield.py` | `extract_failing_test_ids()` | Corpus-wide distinct-failing-id counts for the yield table. Uses the `extract_*_failing_test_ids` shortcuts, bypassing `normalize_test_id`. |
| `analysis/fixture_score.py`, `analysis/holdout_eval.py`, `analysis/expected_audit.py` | scoring | Parse the `Canonical \`normalize_test_id()\`: \`...\`` line out of hand-written holdout worksheets and compare against parser output. |
| `src/parse/dispatch.py` | `_normalize_comparison_key()` | Dedup key for the `ambiguous` branch only. Rewrites `#`→`::` and `" > "`→`::`. **Never written to any output.** |
| `src/parse/outcome.py` | `TestOutcome` | Carries the field. |

**One grep hit is a false positive.** `src/harvest/frame.py` uses the name `test_ids`
for a list of *workflow* IDs returned by `classify_workflows()`. It has nothing to do
with test identifiers and is not a consumer.

### 5. The contract test (§29.6)

The contract test is **`tests/test_test_ids.py`**. ROADMAP line 3201: *"`test_id` is the
join key for the entire project… It has its own contract test, inherited from Graphify
(§29.6), and that test must pass on every merge (T12)."*

```
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0 -- /home/shree/blastradius/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/shree/blastradius
configfile: pyproject.toml
plugins: anyio-4.14.2
collecting ... collected 50 items

tests/test_test_ids.py::test_normalize_test_id_table[<testcase classname="com.example.FooTest" name="testBar"/>-com.example.FooTest#testBar] PASSED [  2%]
tests/test_test_ids.py::test_normalize_test_id_table[<testcase classname="com.example.FooTest" name="testBar[0]"/>-com.example.FooTest#testBar] PASSED [  4%]
...
tests/test_test_ids.py::test_normalize_test_id_table[tests/test_calc.py::test_add[2-3-5]-tests/test_calc.py::test_add] PASSED [ 48%]
...
tests/test_test_ids.py::test_derive_node_id_round_trip_from_raw_xml PASSED [100%]

============================== 50 passed in 0.14s ==============================
```

**50 passed in 0.14s.**

**Hypothesis (b) is CONFIRMED, and it is worse than stated.** The module's only import
from the codebase is `from src.parse.test_ids import TestId, derive_node_id,
normalize_test_id`. It never imports `log_pytest`, `log_maven`, `log_gradle`, or
`dispatch`; it never opens a fixture log; every input is a hand-written string literal.
It cannot see parser output and would not have caught any of the three defects.

The sharper point: **the contract test proves the normalizer is already correct on all
three defects.** Case 48% asserts `tests/test_calc.py::test_add[2-3-5]` →
`tests/test_calc.py::test_add` — D-32 compliance, passing. Another case asserts
`com.example.FooTest > testBar FAILED` → `com.example.FooTest#testBar`, and another
handles the 3-segment `:core:test > com.example.FooTest > testBar FAILED`. D-32 is
**implemented and tested in `normalize_test_id()`**; 012B's claim that "D-32 was never
implemented" is true of `log_pytest.py` specifically and false of the codebase. The
defect is that the parsers do not route through the normalizer, not that the rule is
missing.

### 6. Counts — predicted vs actual

Predictions were recorded before `parsed_outcomes.parquet` was opened.

| Quantity | Predicted | Actual | Verdict |
|---|---|---|---|
| Rows in `parsed_outcomes.parquet` | 3,000 | **20,535** | under by 6.8× |
| Distinct `test_id` total | 1,200 | **6,014 / 20,535** | under by 5.0× |
| Distinct Python `test_id` | 151 | **870 / 6,014** | under by 5.8× |
| Distinct Java `test_id` | 1,049 | **5,144 / 6,014** | under by 4.9× |

All four predictions were low by roughly the same factor — a systematic
underestimate of corpus scale, not four independent misses.

Language split computed two independent ways, which agree exactly:

- by `harness` column: pytest **5,450 / 20,535** rows → 870 distinct;
  maven + gradle **3,450 + 11,635 = 15,085 / 20,535** rows → 5,144 distinct.
- by canonical shape: ids containing `::` → **870 / 6,014**; ids containing `#` →
  **5,144 / 6,014**; neither → **0 / 6,014**.

**Hypothesis (c) is FALSIFIED — on its premise, not its arithmetic.**

- The figure 151 does not appear in any table. Distinct Python ids are 870 in
  `parsed_outcomes.parquet` and 870 in `binding.parquet`; downstream they fall to
  **438 / 2,519** in `outcomes.parquet` and **126 / 1,706** in
  `release/v0.1/labels.parquet` (attrition through labelling, not parsing). 126 is the
  nearest value to 151 anywhere on disk, and it is not a parser quantity.
- More importantly, **params are already collapsed in the stored dataset.**
  `test_id` values containing `[`: **0 / 20,535**. Distinct such ids: **0 / 6,014**.
  Non-null `params`: **696 / 20,535**. `analysis/corpus_parse.py` routes every outcome
  through `normalize_test_id()`, which strips the bracket into the `params` column
  exactly as D-32 requires.
- Therefore collapsing params **in the parser** will change the distinct count in
  `parsed_outcomes.parquet` by **zero**, and will not raise per-id row counts. Current
  ratios are already post-collapse: **5,450 / 870 = 6.26** rows per Python id,
  **15,085 / 5,144 = 2.93** rows per Java id.

**D1's true blast radius is narrow.** The parquet is already compliant. Exposure is
limited to consumers that read parser output *without* normalizing — chiefly
`analysis/log_yield.py`'s `extract_failing_test_ids()` and the
`extract_*_failing_test_ids` shortcuts used by `holdout_eval.py` and `fixture_score.py`,
i.e. the holdout-scoring path. That is why the defect surfaced in a holdout audit and
not in the dataset.

### D2's true blast radius: silent data loss, not a corrupt key

`normalize_test_id('Gradle suite#com.linkedin...')` returns **`None`**. The id is not
written wrong — the outcome is **discarded**. `test_id` values containing
`"Gradle suite"` in `parsed_outcomes.parquet`: **0 / 20,535**. Rows matching
`testLeaderDoAssignmentForNewlyElected`: **0**. The `corpus_parse.py` `None` branch
increments `unnormalizable_count` and drops the record.

Measured across all 30 `holdout_v4` fixtures: parsers emit **47** outcomes, of which
**1 / 47** is dropped by `normalize_test_id()` — the `Gradle suite` id. This is a
recall defect in the labels, invisible in the dataset because the evidence is deleted
rather than stored.

### D3's true blast radius: key fragmentation — the largest of the three

The bare-class form **is** written to the parquet, and coexists with the qualified form
as a *distinct key*. Both appear for the sirix example:

```
io.sirix.query.scan.RegionOnlyPredicateCountTest#negationConjoinedWithAnAnchoringLeafIsRepresentable
                    RegionOnlyPredicateCountTest#negationConjoinedWithAnAnchoringLeafIsRepresentable
```

(`normalize_test_id` strips the trailing `()` but cannot invent a package, so the bare
form survives normalization intact.)

- Distinct Java ids whose class part has no `.` (bare, D-39 `fqcn_incomplete` shape):
  **2,067 / 5,144** — 40.2% of the Java key space.
- Bare ids that **also** exist as a qualified id for the same `(repo, simple_class,
  method)`: **57 / 2,067**. These 57 are confirmed split keys — one real test counted
  twice, on both sides of every join in Phase 3.4.

Confirmed fragmented pairs include:

```
apache/beam        DeltaIOIT#testReadChangesDeltaLake
                <-> org.apache.beam.sdk.io.delta.DeltaIOIT#testReadChangesDeltaLake
grobidOrg/grobid   GrobidRestServiceTest#initializationError
                <-> org.grobid.service.tests.GrobidRestServiceTest#initializationError
mcreator/mcreator  DialogsTest#testGeneralTextureSelector
                <-> net.mcreator.integration.ui.DialogsTest#testGeneralTextureSelector
sirixdb/sirix      XmlResourceSessionTest#testFetchingRevisionValidAtPointInTime
                <-> io.sirix.access.node.xml.XmlResourceSessionTest#testFetchingRevisionValidAtPointInTime
```

The remaining **2,010 / 2,067** bare ids have no qualified counterpart on disk. Whether
they are unfragmented or merely never observed qualified is not determinable from the
parquet alone. They still bind at `confidence=0.5` through the basename-only branch of
`resolve_test_file()`, and `binding.parquet` currently reports **5,629 / 6,014 exact**,
**167 / 6,014 ambiguous**, **218 / 6,014 not_found** — so a share of the 167 ambiguous
bindings is the expected signature of a bare class name matching several files.

---

## PHASE 4 — Schema check (ESCALATION GATE)

### 7. What `docs/SCHEMAS.md` declares

`test_id` is declared in three places:

```
## `outcomes.parquet` — one row per (instance, test) observation

instance_id            string   FK
test_id                string   canonical "module::class::method"
test_file              string   repo-relative, null if unresolved
status_head            string   pass | fail | error | skip | absent
status_base            string   pass | fail | error | skip | absent
is_fault_revealing     bool     status_base != fail AND status_head in (fail, error)
flakiness_score        float32  trailing 30d flip rate
same_sha_flip          bool
label_source           string   annotation | artifact | log | reexec
parser_confidence      float32
duration_s             float32
failure_message_hash   string   sha256, message stored separately
split_strict           bool
split_permissive       bool
new_test               bool     exists at head, not at base
suspect_unrelated      bool     coverage-free DeFlaker heuristic
excluded_own_file      bool     test's own file was in the changed set — LEAKAGE RULE
binding_strategy       string   tests | tests_by_convention | tests_by_layout | unbound
```

Plus `graph_nodes.parquet`: `test_id (nullable)`, and `gold.parquet`:
`instance_id, test_id, verdict_base_run1, verdict_base_run2, …`.

That is the complete `test_id` surface in `SCHEMAS.md`. The header states
*"Frozen Week 2."*

### 8. `fqcn_incomplete` — **NOT DECLARED. STOPPING.**

**`fqcn_incomplete` is NOT DECLARED in `docs/SCHEMAS.md`.** It appears nowhere in the
file — not in the `outcomes.parquet` field list, not in any other table, not in prose.

Repo-wide, `fqcn_incomplete` occurs only in four places, all narrative, none normative
schema:

```
docs/DECISIONS.md:80                      (D-39, the Architect ruling text)
docs/HANDOFF-019.md:211
docs/phase/013B-REPORT.md:141
docs/session/073-2026-08-31-013B-schema-divergence-and-decisions.md:111
```

It is declared in **no** schema and exists in **no** on-disk table.

Per **D-42**: *"`SCHEMAS.md` is frozen and describes the full project scope… `SCHEMAS.md`
is never edited to match what was built."* Adding a field is an Architect decision. Per
this task's non-goals, `SCHEMAS.md` was not edited and no wording is proposed.

**Consequence for D-39, stated plainly and not resolved here:** D-39 cannot be
implemented as written. It requires the parser to *set* `fqcn_incomplete=True`, and
there is no declared column to set. The nearest existing column is
`is_fqcn_qualified` in `parsed_outcomes.parquet` — which is itself undeclared in
`SCHEMAS.md`, is derived post-hoc in `analysis/corpus_parse.py` rather than set by the
parser, and is the logical inverse. Whether `fqcn_incomplete` is a new field, a rename
of `is_fqcn_qualified`, or already satisfied by it is an Architect call. **This blocks
the D-39 half of the work; D-32 and the D2 Gradle-prefix fix are not blocked by it.**

---

## PREDICTED FAILURES — scored

| # | Hypothesis | Verdict |
|---|---|---|
| a | The raw log behind at least one example is not on disk | **FALSIFIED.** All three present; all three defects reproduce from bytes. |
| b | The contract test passes and never sees parser output | **CONFIRMED**, and stronger than stated — it also proves the normalizer *already* implements D-32, so the rule is not missing, only unrouted. |
| c | Python distinct ≈151 is inflated by params; collapsing will reduce distinct count | **FALSIFIED.** Actual 870, not 151. Params are already stripped in the parquet (0 / 20,535 ids contain `[`). Collapsing in the parser changes the distinct count by zero. |

### (d) My own — the D-39 separator conflict

**D-39 as worded contradicts the frozen contract test, and implementing it literally
would break all 50 cases.**

D-39 states verbatim: *"The canonical Java test_id is the fully-qualified class name,
plus **'::'**, plus the method name."* `SCHEMAS.md` agrees: `canonical
"module::class::method"`.

But every parser emits `#`, `normalize_test_id()` produces `#`, and
`tests/test_test_ids.py` — the contract test that CLAUDE.md says *"must pass on every
merge"* and that *"If a change would alter `test_id` output for any existing input, stop
and flag it"* — asserts `#` in every Java case (`com.example.FooTest#testBar`,
`com.example.FooTest$NestedTest#testNested`). All **5,144 / 6,014** Java ids on disk use
`#`.

So `SCHEMAS.md` and D-39 say `::`; the frozen contract test, the code, and the shipped
`release/v0.1` data say `#`. Two of the three defects (D2, D3) are Java-identifier
defects, so any fix touches exactly the code where this conflict lives. This is not
covered by `docs/phase/013B-schema-divergence.md`, which analyses column presence and
never examines the separator.

**This is a second escalation, independent of `fqcn_incomplete`.** It is not resolved
here and no change is proposed.

---

## Summary of findings

1. All three defects reproduce from real bytes. **Hypothesis (a) falsified.**
2. 012B's quoted output for D2 and D3 is wrong on the separator — it quotes `::` where
   the parsers emit `#`. The `::` form is a dispatch-internal dedup key that is never
   written anywhere.
3. `log_pytest.py` composes no separator at all; it passes the regex capture through
   verbatim.
4. No parser imports `vendor/graphify-br/graphify/ids.py`. The recipe is duplicated by
   hand in `derive_node_id()` with a manual-sync warning in its docstring.
5. `TestId.canonical` is a field, not the `.canonical()` method ROADMAP §34.4 C.2
   specifies.
6. **The contract test passes (50 / 50) and cannot fail on any of these defects** — it
   never sees parser output. **Hypothesis (b) confirmed.** It also demonstrates that
   `normalize_test_id()` already satisfies D-32.
7. **D1 does not reach the dataset.** 0 / 20,535 stored ids retain params.
   **Hypothesis (c) falsified.** Exposure is confined to the holdout-scoring path, which
   bypasses the normalizer.
8. **D2 is silent data loss, not a corrupt key.** `normalize_test_id` returns `None` and
   the outcome is dropped: 1 / 47 outcomes across `holdout_v4`, 0 rows surviving in the
   parquet.
9. **D3 is the largest defect.** 2,067 / 5,144 distinct Java ids are bare-class; 57 are
   confirmed split keys with a qualified twin in the same repo, each counted twice
   across binding, the co-change join, RQ1 Axis 2, and `fault_revealing`.
10. **ESCALATION 1:** `fqcn_incomplete` is NOT DECLARED in `SCHEMAS.md`. D-39 is blocked.
11. **ESCALATION 2 (new):** D-39 and `SCHEMAS.md` mandate `::` for Java; the frozen
    contract test, the code, and shipped data all use `#`. Unresolved.

**Nothing was changed. Nothing was committed.**
