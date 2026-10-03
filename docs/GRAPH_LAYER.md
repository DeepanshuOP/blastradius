# The graph layer (ROADMAP §10)

Commit-pinned code-property graphs over a stripped Graphify fork, with test nodes
bound to canonical `test_id`s and five query primitives over the result.

## Scope

**Out of the MSR 2027 paper (D-48), in scope as the BITE497J deliverable.** No
number in this document reaches `make tables`, `release/` or the paper. The
graph-side binding measurement is reported as `graph_node_binding_rate` here and
in session records only; it is **not Gate 1.5** and it is not comparable with
D-47's figure, which has a different denominator.

Every figure below is written as numerator/denominator and comes from raw command
output. The commit that produced each is named so any figure can be traced.

| Commit | What it produced |
|---|---|
| `6b39df3` | D-48 amended to cover T2.5b (the DuckDB query cache and benchmark) |
| `4922cf0` | the `graph` extra: vendored `graphifyy`, `duckdb`, 25 tree-sitter grammars |
| `bed146e` | the strip (§7.1) |
| `4964611` | `docs/MINI_CORPUS.md` (§7.2) |
| `5c94ffe` | the commit-pinned builder and the per-repo graph statistics (§7.3) |
| `99377a5` | the incremental build and the equivalence result (§7.4) |
| `b5544f2` | test-node typing, `test_id` binding, binding edges (§7.5) |
| `71c0a64` | the query API, its DuckDB cache and the benchmark (§7.6) |
| `9fc4722` | the regression tests pinning the binding denominator (§7.5) |

---

## 1. Architecture

```
data/clones/<owner>__<name>/            blob:none clone, one per repo
        │
        │  git worktree add --detach <sha>
        ▼
   stripped extractor  ──────────────▶  data/graphs/cache/<repo>/   (SHA-256 content cache)
   (.java and .py only)                        │
        │                                      │ replayed on the next SHA
        ▼                                      ▼
   assemble ─▶ cluster ─▶ type test nodes ─▶ bind test_id ─▶ add binding edges
        │
        ▼
data/graphs/graph_<owner>__<name>_<sha>.json.gz    MultiDiGraph, node-link, gzipped
data/graphs/graph_<owner>__<name>_<sha>.stats.json build record
        │
        ▼
   src/graph/query.py  ──▶  data/graphs/query_cache.duckdb   (per-(repo, sha))
```

### 1.1 The strip — `vendor/graphify-br/`, commit `bed146e`

Upstream Graphify at `0738af373af9cf5c95f862cc5f3327fd96b4ea23`
(`vendor/GRAPHIFY_COMMIT.txt`), Apache-2.0 with older MIT portions; attribution
in `NOTICE` and `vendor/graphify-br/NOTICE`.

Deleted, per ROADMAP §29.4 plus `prs.py`: `llm.py`, `transcribe.py`, `ingest.py`,
`file_slice.py`, `semantic_cleanup.py`, `reflect.py`, `mcp_ingest.py`,
`pg_introspect.py`, `prs.py`, `wiki.py`, `querylog.py`, `exporters/graphdb.py` —
12 modules and 33 vendor test files. The Obsidian, wiki, SVG, GraphML and Cypher
exporters came out of `export.py`; the LLM semantic-extraction pass, every cloud
backend and the `--dedup-llm` tiebreaker came out of `cli.py`. Community naming is
now deterministic: each community is named after its highest-degree hub.

Net `-20,142 / +5,074` lines across the 101 files of the whole layer;
`-20,158 / +253` across the 77 files of the strip commit alone.

The gate: `grep -rn -iE "anthropic|openai" vendor/graphify-br/graphify
--include=*.py` returns nothing. Extraction is the deterministic tree-sitter AST
path only, so every graph is exactly reproducible from source (D-17).

### 1.2 Commit-pinned builder — `src/graph/build.py`, commit `5c94ffe`

`build_graph_at(repo, sha)`: `git worktree add --detach` at the SHA, the stripped
extractor over `.java`/`.py` only (D-03; TypeScript is an explicit non-goal),
then assemble, cluster, type and write.

Determinism is a requirement, not a nicety: every collection written is sorted,
clustering and PageRank are seeded, the gzip mtime is pinned to 0, and no
timestamp enters the payload — so two builds of one commit are byte-identical.
`built_at` and the timings live in the `.stats.json` sidecar for that reason.

`PARSE_FAILURE_CEILING = 0.20` (§19.4). A file counts as a parse failure when the
extractor reports it, when it produced no node, **or when tree-sitter recovered
from a syntax error in it** — tree-sitter is error-tolerant, so a badly broken
file still yields its file node and never reaches `failed_sources`. Counting only
hard failures would report 0/63,260 on a corpus the parser is silently mangling,
so the gate also reads the `parse_errors` marker out of the content-cache entry.

### 1.3 Incremental build — same module, commit `99377a5`

`build_graph_incremental(repo, sha, prev_sha)`. Incrementality comes from
Graphify's SHA-256 content cache, which §19.1 names explicitly ("reuse
Graphify's content cache rather than adding a second caching layer"): both SHAs
share one `cache_root`, so an unchanged file is replayed and only changed files
are parsed. The `git diff` dirty set and its reverse relation hop are computed
and recorded as `n_files_changed` and `n_files_reverse_hop`.

The extractor is handed the **full file list**, not the dirty set. Narrowing it
breaks Graphify's Java import resolution — see §8.2 for the measured divergence
and why equivalence has to hold by construction.

### 1.4 Test-node typing and binding — `src/graph/test_nodes.py`, commit `b5544f2`

Registered as a `LanguageResolver` in Graphify's own `resolver_registry` (D-10),
from `src/graph` so the dependency direction stays `src/graph → vendor`:

1. **Classification** — every node becomes `test | source | config | build` from
   path heuristics plus AST signals. Graphify models `@Test` as a `references`
   edge to the annotation symbol rather than a node attribute, so that edge is
   the signal. `build` and `config` are implemented and tested but never appear
   in a built graph, because only `.java`/`.py` are dispatched.
2. **Binding** — each individual test case gets its canonical `test_id` from
   `src.parse.test_ids.normalize_test_id()`, the frozen Week-1 contract, imported
   and never reimplemented. Shapes: `{package}.{Class}#{method}` for Java,
   `{module_path}::{Class}::{func}` for Python. Test files and test classes are
   containers, not cases, and deliberately get no id.
   `derive_node_id()` supplies `graph_binding_key`, D-25's lossy internal key.
3. **Test→source edges** — all three §29.6 strategies, each with its own
   confidence so a model can learn which to trust:

| Strategy | `edge_type` | confidence |
|---|---|---|
| direct dependency | `tests` | `EXTRACTED` @ 1.00 |
| naming convention | `tests_by_convention` | `INFERRED` @ 0.85 |
| directory mirroring | `tests_by_layout` | `INFERRED` @ 0.65 |

The stored graph is a **`MultiDiGraph` keyed by `edge_type`**, because a `tests`
edge must coexist with the `calls` edge it derives from. See §8.3.

### 1.5 Query API — `src/graph/query.py`, commit `71c0a64`

The five §10.5 primitives: `shortest_path_length`,
`min_distance_to_any_changed`, `k_hop_neighborhood`, `same_community`,
`pagerank_delta`, plus `features()`, which is the unit §19.4's latency budget is
written against.

Distances are measured on the **undirected projection**: impact propagation is
not one-way, so a directed traversal from the changed set would miss exactly the
tests that call into a changed callee. Cached per `(repo, sha, seed)` in DuckDB
(D-06, §19.2) — only the two expensive instance-independent things are cached,
the BFS distance layers and the partition, so two instances touching the same
file reuse one BFS.

`with_cochange=True` raises `NotImplementedError` rather than silently returning
the without-`co_changes` number: `co_changes` edges are T2.4, which stays CUT
under D-48.

---

## 2. Mini-corpus

Three repos, one per build system, chosen by the most instances with a resolved
base SHA. Full derivation, ranking tables and the base-SHA accounting are in
**[`docs/MINI_CORPUS.md`](MINI_CORPUS.md)** (commit `4964611`).

| Group | Repo | Base SHAs |
|---|---|---|
| pytest (Python) | `fla-org/flash-linear-attention` | 107/107 in clone |
| Gradle (Java) | `Stirling-Tools/Stirling-PDF` | 140/140 in clone |
| Maven (Java) | `spiculedata/saiku` | 180/180 in clone |

---

## 3. Per-repo graph statistics

**427/427 base SHAs built, 0/427 failures.** `data/graphs` is 907 MB over 427
`*.json.gz` files plus sidecars and the shared content cache.

The format changed in `b5544f2` (`meta.format_version` 1 → 2: typed nodes,
`test_id`, binding edges, `MultiDiGraph`). The rebuild was stopped by operator
instruction at each repo's 20 most recent base SHAs, so the corpus is mixed and
**v1 and v2 edge counts are not comparable** — v2 counts binding edges alongside
the structural edges they derive from. Everything is therefore split by version.

### 3.1 `fla-org/flash-linear-attention` — 107/107 typed

| Metric | v2 (107 graphs) |
|---|---|
| Nodes (min / median / max) | 4,208 / 6,317 / 7,581 |
| Edges (min / median / max) | 10,807 / 17,434 / 21,382 |
| Orphan nodes | 328/692,872 |
| Parse failures, all | 107/63,260 |
| Parse failures, Java | 0/0 |
| Parse failures, Python | 107/63,260 |
| Flagged above the 20% ceiling | 0/107 |
| Cold build seconds (min / median / max) | 7.52 / 12.08 / 15.94 |
| Communities (median) | 309 |

### 3.2 `Stirling-Tools/Stirling-PDF` — 35/140 typed

| Metric | v2 (35 graphs) | v1 (105 graphs) |
|---|---|---|
| Nodes (min / median / max) | 13,503 / 29,412 / 30,278 | 16,270 / 26,280 / 29,582 |
| Edges (min / median / max) | 65,757 / 160,587 / 163,333 | 59,313 / 101,767 / 161,402 |
| Orphan nodes | 175/800,895 | 525/2,451,439 |
| Parse failures, all | 0/65,871 | 0/199,275 |
| Parse failures, Java | 0/60,065 | 0/182,071 |
| Parse failures, Python | 0/5,806 | 0/17,204 |
| Flagged above the 20% ceiling | 0/35 | 0/105 |
| Cold build seconds (min / median / max) | 19.91 / 50.29 / 53.55 | 25.74 / 48.28 / 85.49 |
| Communities (median) | 613 | 582 |

### 3.3 `spiculedata/saiku` — 20/180 typed

| Metric | v2 (20 graphs) | v1 (160 graphs) |
|---|---|---|
| Nodes (min / median / max) | 9,048 / 9,961 / 10,337 | 2,882 / 5,438 / 8,599 |
| Edges (min / median / max) | 38,561 / 44,602 / 47,122 | 7,366 / 16,923 / 26,951 |
| Orphan nodes | 20/195,637 | 161/829,391 |
| Parse failures, all | 40/14,828 | 0/66,547 |
| Parse failures, Java | 40/14,788 | 0/66,385 |
| Parse failures, Python | 0/40 | 0/162 |
| Flagged above the 20% ceiling | 0/20 | 0/160 |
| Cold build seconds (min / median / max) | 11.79 / 13.17 / 14.95 | 3.07 / 7.58 / 33.9 |
| Communities (median) | 297 | 177 |

The v2 node range is narrower than v1's because the typed graphs are the most
recent base SHAs, not a sample across history.

**0/3 repos flagged, 0/427 graphs flagged**, so there is no drop reason to
record. The 107 Python and 40 Java failures are recovered syntax errors, not
crashes (§1.2).

**One slow build.** `spiculedata/saiku` at `95cfe25bb6` took 983.477 s wall with
only 5.675 s of extraction over 435 files. Rebuilt to attribute the cost: 6.13 s
wall, identical graph (5,434 nodes, 16,906 edges both times). The 977 s was a
one-off lazy-blob-fetch stall against GitHub during the worktree checkout, not
build cost. Corpus-wide: 1/427 builds over 600 s, 1/427 over 900 s, the same SHA.

---

## 4. Incremental-vs-cold equivalence

ROADMAP §10.2 step 6 / §19.1, the blocking assertion: an incremental build at SHA
*X* must produce the same graph as a cold build at *X*. Measured on five real
consecutive first-parent commits of `spiculedata/saiku`, the smallest
mini-corpus repo, each step touching at least one `.java`/`.py` file.

**Result: 4/4 transitions equal — node sets 4/4, edge sets 4/4.** Compared over
`graph.edges(keys=True)`, so a `tests` edge cannot stand in for the `calls` edge
it derives from. Hermetic fixture coverage additionally asserts full attribute
and partition equality, 1/1.

| # | SHA | Cold s | Incremental s | Nodes | Edges | Changed | Reverse hop | Re-extracted | Considered |
|---|---|---|---|---|---|---|---|---|---|
| 0 | `e3dec93372` | 23.449 | — (seed) | 12,463 | 58,761 | — | — | 947 | 947 |
| 1 | `36a1fd4ea0` | 26.624 | 25.582 | 12,500 | 58,963 | 4 | 0 | 4/951 | 951 |
| 2 | `99fd60a39f` | 27.925 | 26.977 | 12,507 | 59,004 | 3 | 4 | 3/951 | 951 |
| 3 | `7c4776612c` | 29.530 | 29.083 | 12,523 | 59,066 | 7 | 14 | 7/952 | 952 |
| 4 | `18a5bb8444` | 30.332 | 28.624 | 12,554 | 59,254 | 6 | 12 | 6/953 | 953 |

The parsing saving is real — 4/951, 3/951, 7/952, 6/953 files re-extracted. The
wall-clock saving is not, and §5 says why.

---

## 5. `graph_node_binding_rate`

**Denominator** — distinct `test_id` strings observed in CI outcomes for the
repo, from `data/interim/parsed_outcomes.parquet` where `repo = ?` and
`test_id is not null`, de-duplicated (CI reports a test once per matrix leg).

**Numerator** — how many of those match a graph node with `node_type == "test"`
carrying a `test_id`, over the union of that repo's typed (v2) graphs. Two tiers,
never merged:

- **exact** — the observed `test_id` equals a node's canonical `test_id`.
- **loose** — `derive_node_id(observed)` equals, or is a `_`-suffix of, a node's
  `graph_binding_key`. A Gradle corpus reports bare class names with no package,
  so an exact match is structurally impossible however good the graph is (D-39's
  `fqcn_incomplete`). A suffix can collide, which is why this tier is reported
  apart. The code field is `n_bound_lossy`.

Denominator source rows:

| Repo | `parsed_outcomes` rows | Distinct `test_id`s = denominator |
|---|---|---|
| `fla-org/flash-linear-attention` | 186 | 37 |
| `Stirling-Tools/Stirling-PDF` | 1,147 | 307 |
| `spiculedata/saiku` | 122 | 20 |

Results — **exact, loose and total; the total is never quoted alone**:

| Repo | Typed graphs | exact | loose | **total** | unbound |
|---|---|---|---|---|---|
| `fla-org/flash-linear-attention` | 107/107 | 36/37 | 0/37 | **36/37** | 1/37 |
| `Stirling-Tools/Stirling-PDF` | 35/140 | 4/307 | 271/307 | **275/307** | 32/307 |
| `spiculedata/saiku` | 20/180 | 20/20 | 0/20 | **20/20** | 0/20 |

`Stirling-Tools/Stirling-PDF` is the repo where the loose tier carries the
result: 271 of its 275 bound ids rest on a suffix match that can collide.
Quoting 275/307 alone would hide that.

**`spiculedata/saiku`'s 20/20 against 20 typed graphs is a coincidence, not a
graph count.** Its 122 outcome rows hold exactly 20 distinct `test_id`s, and it
has 20 typed graphs only because the rebuild stopped at the 20 most recent base
SHAs. Varying the union width leaves the denominator fixed while the numerator
moves:

```
 graphs_used  denominator  exact  loose  total
           1           20     18      0     18
           2           20     20      0     20
           5           20     20      0     20
          10           20     20      0     20
          20           20     20      0     20
```

A denominator counting graphs would track column 1. No computation was changed
and no figure moved; commit `9fc4722` adds three regression tests
(`..._counts_distinct_test_ids_not_graphs_or_nodes`,
`..._deduplicates_the_observed_ids`,
`..._is_unchanged_by_how_many_test_nodes_the_graph_has`) so the question cannot
recur.

---

## 6. Query benchmark

Full feature set per instance, on the 5 most recent typed graphs of each repo,
200 instances timed per graph, 5 changed nodes per instance, `random.Random(42)`.
Budget: §19.4, ≤100 ms per instance.

| Repo | Graphs | Warm per-instance ms (median / max) | First instance, cold cache | First instance, warm DuckDB cache |
|---|---|---|---|---|
| `fla-org/flash-linear-attention` | 5/5 | **0.499 / 0.546** | 105.034 / 363.969 | 19.117 / 268.152 |
| `Stirling-Tools/Stirling-PDF` | 5/5 | **3.659 / 3.909** | 868.066 / 963.445 | 118.005 / 126.577 |
| `spiculedata/saiku` | 5/5 | **0.958 / 1.319** | 466.531 / 521.530 | 37.597 / 42.102 |

**The DuckDB cache (T2.5b) works**: pass 1 over a deleted database, 0 hits /
105 misses; pass 2 over the same database, **105 hits / 0 misses**, with the
first-instance cost down 5–7× (105→19, 868→118, 467→38 ms median). The database
was 294,924,288 bytes after pass 1, because an entry is a full single-source
distance map per seed; it lives under `data/graphs/`, which is git-ignored.

The per-instance figure — what §19.4 measures — is met everywhere by a wide
margin. The *first* instance at a SHA pays for the BFS layers; with a warm cache
that is within budget on 2/3 repos and over it on `Stirling-Tools/Stirling-PDF`.

---

## 7. ROADMAP §10.6 exit criteria

| Criterion | Verdict | Evidence |
|---|---|---|
| Graph builds for all corpus repos, <10 min cold | **MET for the mini-corpus; NOT MEASURED corpus-wide** | 427/427 base SHAs of 3/3 mini-corpus repos, 0/427 failures; 426/427 under 600 s, the exception attributed to a network stall (§3). D-48 scopes this layer to the mini-corpus, so the other ~43 corpus repos were not built. `5c94ffe` |
| …<10 s incremental | **NOT MET** | 25.582 / 26.977 / 29.083 / 28.624 s (§4). See §8.1. `99377a5` |
| Test-node binding rate ≥80%, ≥70% hard floor | **MET on the typed subset** | 36/37, 275/307, 20/20 — all clear 80% (§5). Coverage 107/107, 35/140, 20/180. Not Gate 1.5; not compared with D-47. `b5544f2` |
| Query API benchmarked: <100 ms per instance | **MET** | Warm per-instance medians 0.499 / 3.659 / 0.958 ms (§6). First instance at a SHA is 118.005 ms median on Stirling-PDF even warm. `71c0a64` |
| Graph statistics table drafted for the paper | **MET as a document table; the paper destination is void** | §3. D-48 removes the layer from the paper, so there is no paper table and `make tables` is untouched. `5c94ffe` |
| Incremental-vs-cold equivalence on 5 real commits | **MET** | 4/4 transitions, node and edge sets equal with multigraph keys (§4). `99377a5` |
| Parse-failure rate per language; every dropped repo has a reason | **MET** | Per-language rates for all 427 graphs (§3). 0/3 repos dropped, 0/427 flagged, so no reason to record; the flagging path is covered by `test_build_graph_at_flags_a_repo_above_the_ceiling_with_a_reason`. `5c94ffe` |

---

## 8. Limitations

### 8.1 The incremental build misses its target by 2.5–3×

25.582–29.083 s against §19.4's ≤10 s. The parsing *is* incremental — 4/951 to
7/952 files re-extracted — but what remains is whole-corpus work that no caching
at this level removes: Graphify's Java import resolver re-parses every `.java`
file for its package declaration, and assembly, clustering and PageRank all run
over the full graph. Closing this needs either a package cache inside the vendor
resolver or an incremental clustering pass; neither is in scope here.

### 8.2 Narrowing the file list breaks Java import resolution

The first implementation followed §19.1 step 3 literally and **diverged on 4/4
transitions**:

| SHA | Cold-only nodes | Incremental-only nodes | Cold-only edges | Incremental-only edges |
|---|---|---|---|---|
| `36a1fd4e` | 0 | 2 | 5 | 6 |
| `99fd60a3` | 0 | 34 | 136 | 129 |
| `7c477661` | 0 | 128 | 739 | 461 |
| `18a5bb84` | 1 | 207 | 1,443 | 778 |

`graphify/extractors/resolution.py::_resolve_cross_file_java_imports` builds its
`{ClassName: [(node_id, package)]}` index only from the files extracted in that
call, and `resolution_context_nodes` does not reach it. Every `imports` edge of a
re-extracted Java file pointed at an unresolved placeholder instead of the
defining class node. Hence §1.3's full file list.

### 8.3 Partial typed coverage

Only 162/427 graphs carry test nodes: 107/107, 35/140 and 20/180. The rebuild
after the step-6 format change was stopped by operator instruction. Binding
figures are over the typed union only, and §3 splits every statistic by version
because v1 and v2 edge counts mean different things.

### 8.4 `tests_by_layout` is a within-file cross product

Measured on the newest typed graph of each repo:

| Repo | `tests` | `tests_by_convention` | `tests_by_layout` | layout targets/source (min/med/max) | distinct target **files**/source |
|---|---|---|---|---|---|
| `spiculedata/saiku` | 5,064 | 119 | 4,778 | 2 / 2 / 6 | 1 / 1 / 1 |
| `Stirling-Tools/Stirling-PDF` | 19,177 | 679 | 26,782 | 2 / 2 / 17 | 1 / 1 / 1 |
| `fla-org/flash-linear-attention` | 1,133 | 29 | **0** | — | — |

Two things to know, and the first is narrower than it may appear:

- A layout edge targets exactly **1 distinct file** per source node
  (min/median/max 1/1/1) — the one mirrored path the test's own name implies, not
  every file in the mirrored folder. The imprecision is *within* that file pair:
  the test file node, the test class node and every test method each get their own
  edge to the mirrored file's file node and class node, so a test class with *N*
  methods emits roughly 2(*N*+2) edges for one subject. That is why
  `tests_by_layout` outnumbers `tests` on Stirling-PDF (26,782 vs 19,177) while
  carrying the lowest confidence of the three strategies, 0.65.
- **`tests_by_layout` fires 0 times on the Python repo.** `_LAYOUT_MIRRORS` only
  knows the Maven/Gradle `src/test/` ↔ `src/main/` convention, which pytest
  corpora do not use. Strategy 3 contributes nothing to a Python repo, so its
  binding rests on strategies 1 and 2 alone.

### 8.5 An upstream `test_id` truncation, reported not fixed

11/20 of Stirling-PDF's sampled unbound ids have class name `Path`
(`Path#tessdataLanguages_emptyDirectory` and nine siblings), which is not a
plausible test class. This looks like a truncation artefact in the log parser in
`src/parse/`, upstream of this layer and outside this work's scope. **Reported to
Deepanshu; not fixed here.** If it is a parser bug, those ids are unbindable for a
reason that has nothing to do with the graph, and the binding figure understates
the graph's real coverage.

A further 9/20 are `FileRunEventHttpIntegrationTest`, one class. If its file was
absent at all 35 typed SHAs the whole class is unbindable from this subset, and
wider SHA coverage would improve the figure.

### 8.6 Smaller deviations

- **Louvain, not Leiden.** `same_community` is specified over Graphify's Leiden
  partition; Leiden needs `graspologic`, outside the `graph` extra, so
  `graphify.cluster.cluster()` falls back to NetworkX Louvain — seeded
  (`seed=42`) over a canonicalised sorted copy, so reproducible.
- **PageRank is local.** `networkx.pagerank` dispatches to SciPy, also outside
  the extra, so `build.pagerank` is a power iteration over sorted nodes, run on
  the simple projection of the multigraph (parallel edges are the same relation
  seen twice).
- **`co_changes` absent.** T2.4 stays CUT, so `with_cochange=True` raises.
- **No `graph_index.parquet`.** T2.2f stays CUT: one full graph per `(repo, sha)`,
  no snapshot/delta compaction.
- **`graph_nodes` columns left empty** rather than guessed, all T2.4: `loc`,
  `complexity`, `churn_90d`, `age_days`, `kind`, `fqn`, `body_sha`, `content_sha`,
  `is_generated`, `is_vendored`, `annotations`, `has_dynamic_boundary`,
  `n_dynamic_sites`, `end_line`.

---

## 9. How to reproduce

Everything runs on a laptop under WSL2. `data/clones/` and `data/graphs/` are
git-ignored and unshippable; the clones are re-creatable, the graphs are
re-derivable from them.

```bash
# 0. environment — pinned versions are recorded in ENVIRONMENT.md
uv sync --extra graph
uv lock --check                       # must report the lock up to date

# 1. the strip gate: must print nothing
grep -rn -iE "anthropic|openai" vendor/graphify-br/graphify --include=*.py

# 2. the suites
uv run --extra graph pytest -q                                   # main
uv run --extra graph pytest vendor/graphify-br/tests -q \
    --tb=no -rfE -p no:cacheprovider                             # vendor

# 3. the graph-layer tests alone
uv run --extra graph pytest tests/graph -q

# 4. the clones (sizes and the Stirling-PDF PR-ref fetch: docs/MINI_CORPUS.md)
git clone --filter=blob:none https://github.com/fla-org/flash-linear-attention.git \
    data/clones/fla-org__flash-linear-attention
git clone --filter=blob:none https://github.com/Stirling-Tools/Stirling-PDF.git \
    data/clones/Stirling-Tools__Stirling-PDF
git -C data/clones/Stirling-Tools__Stirling-PDF fetch --filter=blob:none origin \
    '+refs/pull/*/head:refs/remotes/origin/pr/*'
git clone --filter=blob:none https://github.com/spiculedata/saiku.git \
    data/clones/spiculedata__saiku

# 5. build one graph at a SHA
uv run --extra graph python -c "
import sys; sys.path.insert(0, '.')
from src.graph.build import build_graph_at
s = build_graph_at('spiculedata/saiku', '<base-sha>')
print(s.n_nodes, s.n_edges, s.parse_failure_rate, s.flagged)
"

# 6. the equivalence assertion on 5 real commits (needs data/clones/spiculedata__saiku)
uv run --extra graph pytest \
    tests/graph/test_incremental_equivalence.py -q -k saiku -s

# 7. the query primitives on a built graph
uv run --extra graph python -c "
import sys; sys.path.insert(0, '.')
from src.graph.build import load_graph, graph_path
from src.graph.query import GraphQuery, QueryCache
G = load_graph(graph_path('spiculedata/saiku', '<base-sha>'))
with QueryCache() as cache:
    q = GraphQuery(G, cache=cache)
    print(q.features('<test-node-id>', ['<changed-node-id>']))
"
```

Base SHAs are re-derivable from `data/interim` with the query in
`docs/MINI_CORPUS.md`. The binding denominator is re-derivable with:

```bash
uv run --extra graph python -c "
import duckdb
print(duckdb.connect().sql(\"\"\"
select repo, count(*) rows, count(distinct test_id) distinct_test_ids
from 'data/interim/parsed_outcomes.parquet'
where repo in ('fla-org/flash-linear-attention',
               'Stirling-Tools/Stirling-PDF','spiculedata/saiku')
group by 1 order by 1\"\"\").df().to_string(index=False))
"
```

---

## 10. Suite state

| Suite | Result | Baseline at `4cc2929` |
|---|---|---|
| Main | `577 passed, 12 skipped` | `451 passed, 13 skipped` |
| Vendor | `19 failed, 3550 passed, 178 skipped` | `23 failed, 4216 passed, 184 skipped` |

The main floor of 451 holds: 577 ≥ 451, 0 failed. The 126 extra passing tests
are 125 in `tests/graph/` (`test_build.py` 25,
`test_incremental_equivalence.py` 10, `test_test_nodes.py` 49,
`test_query.py` 41) plus
`tests/test_base_resolve.py::test_base_resolve_ancestor_real_payload`, which
flipped from skip to pass because `data/clones/` now exists. Skips went 13 → 12
for the same reason.

On the vendor suite, **0 tests that passed at baseline now fail**, verified by
intersecting the 4,216 baseline passing node ids with the current failure set.
The 19 remaining failures are the baseline set minus `test_ollama_retry_cap.py`
(deleted with the LLM backends): `test_skillgen.py` 11, `test_terraform.py` 7,
`test_install_references.py` 1 — all pre-existing, all from missing optional
extras. ROADMAP §29.5's keep-list is intact: `test_phantom_cross_package_call.py`,
`test_id_normalization_contract.py`, `test_java_type_resolution.py`,
`test_python_import_resolution.py`, `test_symbol_resolution.py` → `67 passed,
1 skipped`.

---

## 11. Field names and schema status

`docs/SCHEMAS.md` was not edited. Fields it defines are written under its names;
fields this layer needs beyond them are graph-internal until ratified, and are
listed with their rationale in **[`src/graph/README.md`](../src/graph/README.md)**.

The three open questions for ratification:

1. **`graph_binding_key`** (node) — D-25's lossy key. It carries 271/307 of
   Stirling-PDF's binding, so the layer cannot work without it, but it must never
   be published in place of `test_id`.
2. **The multigraph.** `tests`, `tests_by_convention` and `tests_by_layout` are
   emitted as `edge_type` values, which is what forces parallel edges. If SCHEMAS
   intends one edge per `(src, dst)` pair, that needs a ruling — the structural
   relation and the binding relation would then have to share a row.
3. **`meta.*`** — `format_version`, `graphify_commit`, `repo`, `sha`, `n_nodes`,
   `n_edges`, `n_communities`, `parse_failure_rate`, `communities_inherited`,
   `languages`: the §19.1 step 5 build metadata, carried once per graph file
   rather than per row.
