# `src/graph` — the graph layer

Commit-pinned code-property graphs over the stripped Graphify fork.

**Scope.** Out of the MSR 2027 paper, in scope as Prisha's BITE497J deliverable
(**D-48**). No number produced here reaches `make tables`, `release/` or the
paper. The graph-side binding measurement is reported as
`graph_node_binding_rate` in session records only; it is **not** Gate 1.5 and it
is not comparable with D-47's figure, which has a different denominator.

| Module | Role |
|---|---|
| `build.py` | Worktree at a SHA → stripped extractor → compressed node-link JSON (ROADMAP §10.2, §19) |
| `test_nodes.py` | Node typing, `test_id` binding, test→source edges (§10.3, §29.6) |
| `query.py` | The five §10.5 feature primitives with a per-(repo, sha) DuckDB cache |

Run everything with `uv run --extra graph`.

## On-disk format

One file per `(repo, sha)`:

```
data/graphs/graph_{owner}__{name}_{sha}.json.gz     the graph
data/graphs/graph_{owner}__{name}_{sha}.stats.json  the build record
data/graphs/cache/{owner}__{name}/                  Graphify's SHA-256 content cache
```

The graph is gzipped NetworkX node-link JSON holding a **`MultiDiGraph` keyed by
`edge_type`**. The graph file is byte-reproducible: every collection is sorted,
clustering and PageRank are seeded, the gzip mtime is pinned to 0, and no
timestamp enters the payload. `built_at` and the build timings live in the
sidecar `.stats.json` for exactly that reason.

### Why a multigraph

Strategy 1 of the §29.6 bridge re-expresses an existing `calls`/`imports` edge
as a `tests` edge, so the two share a `(source, target)` pair. Graphify
assembles into an `nx.DiGraph`, which holds one edge per pair, so emitting the
`tests` edge during extraction *overwrote* the structural edge it was derived
from — on the `minirepo` fixture that destroyed 7 of 29 edges, including every
`calls` edge. Graphify's own multigraph mode is upstream future work with no call
sites (`graphify/multigraph_compat.py`), so the parallel-edge capacity comes from
this layer. It is also what `docs/SCHEMAS.md`'s `(src, dst, edge_type)` edge rows
already describe.

## Field names

Fields `docs/SCHEMAS.md` defines are written under its names. The node-link wire
format keeps NetworkX's own `id` / `source` / `target` / `key` keys, which are
the same things as the schema's `node_id` / `src` / `dst` / `edge_type` columns:

| `docs/SCHEMAS.md` column | In the node-link payload |
|---|---|
| `node_id` | a node's `id` |
| `src`, `dst` | a link's `source`, `target` |
| `edge_type` | a link's `edge_type`, and its multigraph `key` |
| `repo`, `sha` | `meta.repo`, `meta.sha` (constant per file, not per row) |

Populated from `graph_nodes`: `node_type`, `source_file`, `test_id`,
`community_id`, `pagerank`, `degree`, `start_line`, `parse_status`, `label`.

Populated from `graph_edges`: `edge_type`, `confidence`, `confidence_score`,
`weight`.

Deliberately **not** populated, because they belong to T2.4, which stays CUT
under D-48: `loc`, `complexity`, `churn_90d`, `age_days`, `kind`, `fqn`,
`body_sha`, `content_sha`, `is_generated`, `is_vendored`, `annotations`,
`has_dynamic_boundary`, `n_dynamic_sites`, `end_line`. They are absent rather
than guessed.

## Graph-internal fields — for schema ratification

`docs/SCHEMAS.md` is frozen and was not edited. These fields are written by this
layer and have no column there, so they are graph-internal until ratified:

| Field | On | Meaning |
|---|---|---|
| `graph_binding_key` | node | D-25's lossy, many-to-one internal key, `derive_node_id(test_id)`. Exists so a CI `test_id` that lost its package (D-39's `fqcn_incomplete`, which is every Gradle id in this corpus) can still be matched against the graph. **Must never be published in place of `test_id`.** |
| `meta.format_version` | graph | Bumped when the payload shape changes; `2` is the multigraph format. An incremental build refuses to reuse across versions. |
| `meta.graphify_commit` | graph | The pinned upstream SHA from `vendor/GRAPHIFY_COMMIT.txt`. |
| `meta.n_nodes`, `meta.n_edges`, `meta.n_communities`, `meta.parse_failure_rate`, `meta.communities_inherited`, `meta.languages` | graph | The §19.1 step 5 build metadata, carried in the graph so a graph file is self-describing. |

Inherited from Graphify and passed through unchanged (its vocabulary, not ours):
`label`, `file_type`, `source_location`, `relation`, `context`, `_origin`,
`_callable`, `_callable_class`, `_src`, `_tgt`.

`BuildStats` (the `.stats.json` sidecar) is a build record rather than a dataset
table, and has no schema counterpart: `orphan_rate`, `per_language`, `flagged`,
`flag_reason`, `n_files_changed`, `n_files_reverse_hop`, `n_files_reextracted`,
`wall_seconds`, `extract_seconds`, `built_at`, `failed_source_files`.

## Deviations worth knowing

- **Louvain, not Leiden.** §10.5's `same_community` is specified over
  Graphify's Leiden partition. Leiden needs `graspologic`, which is outside the
  `graph` extra, so `graphify.cluster.cluster()` falls back to NetworkX's
  Louvain. That fallback is seeded (`seed=42`) and runs over a canonicalised
  sorted copy of the graph, so the partition is reproducible — which is what the
  determinism requirement actually needs.
- **PageRank is local.** `networkx.pagerank` dispatches to a SciPy sparse
  solver and SciPy is outside the `graph` extra, so `build.pagerank` is a
  textbook power iteration with nodes visited in sorted order. It runs on the
  simple projection of the multigraph: parallel edges are the same structural
  relation seen twice, so counting both would inflate exactly the test→source
  pairs this layer adds.
- **Java and Python only.** `SOURCE_SUFFIXES` dispatches `.java` and `.py`
  (D-03; TypeScript is an explicit non-goal). `build` and `config` node types
  are implemented and tested, but a `pom.xml` never becomes a node because its
  suffix is not dispatched.
- **Parse failures include recovered syntax errors.** tree-sitter is
  error-tolerant: a badly broken file still yields its file node and never
  reaches `failed_sources`. Counting only hard failures would report 0% on a
  corpus the parser is silently mangling, so the gate also reads the
  `parse_errors` marker out of the content-cache entry.
- **Incremental builds hand the extractor the full file list.** Narrowing it to
  the dirty set breaks Graphify's Java import resolution, which indexes only the
  files extracted in that call. See `build.build_graph_incremental` for the
  measured divergence and why equivalence has to hold by construction.
