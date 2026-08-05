# BlastRadius — Data Schemas

> Extracted from `ROADMAP.md` §31. **Frozen Week 2.** Schema churn after Phase 1 costs a week (risk T18).
>
> **Change protocol:** additive columns only, agreed by all three, recorded in the table at the bottom. Renames and type changes require a new `frame_version`.

## `instances.parquet` — one row per (head_sha, workflow_run)

```
instance_id            string   PK, sha256(repo|head_sha|run_id)
repo                   string   "owner/name"
language               string   java | python
pr_number              int64    null for push events
head_sha               string
base_sha               string
base_run_id            int64    null if no base run found
base_run_distance      int32    commits between base_sha and the run actually used
run_id                 int64
workflow_id            int64
workflow_name          string
run_conclusion         string   success | failure | cancelled | ...
run_started_at         timestamp
changed_files          list<struct<path:string, status:string, additions:int32,
                                   deletions:int32, hunks:list<struct<start:int32,end:int32>>>>
changed_symbols        list<string>
n_files_changed        int32
n_lines_changed        int32
touches_test_file      bool
touches_build_config   bool
touches_ci_config      bool
is_dependency_bump     bool
is_docs_only           bool
is_formatting_only     bool
author_login           string   pseudonymised on release
n_matrix_legs          int32    matrix-build aggregation (D-12)
frontier_truncated     bool     explosion guard fired
is_bot_pr              bool     Dependabot / Renovate
bot_name               string   null unless is_bot_pr
event_type             string   pull_request | push | pull_request_target
is_default_branch      bool     survivorship analysis
graph_sha              string   the SHA the graph was built at (= base_sha normally)
parse_failure_rate     float32  per (repo, sha) at graph build time
frame_version          string   which frozen frame this instance belongs to
actual_changed_files   list<string>   file-level ground truth
```

## `outcomes.parquet` — one row per (instance, test) observation

```
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

**`is_fault_revealing` is the label.** **`excluded_own_file` is the leakage guard** — a CI assertion must fail if any training instance violates it.

## `graph_nodes.parquet` / `graph_edges.parquet` — per (repo, sha)

```
# nodes
repo, sha, node_id, label, node_type {source|test|config|build},
source_file, test_id (nullable), loc, complexity, churn_90d, age_days,
community_id, pagerank, degree,
kind, fqn, body_sha, content_sha, parse_status, is_generated, is_vendored,
annotations, has_dynamic_boundary, n_dynamic_sites, start_line, end_line
```

```
# edges
repo, sha, src, dst, edge_type, confidence, confidence_score, weight

edge_type domain (CORE marked *):
  imports*, calls*, inherits*, tests*, tests_by_convention*, co_changes*, config_of*,
  contains, implements, overrides, instantiates, reads_field, writes_field, throws,
  tests_by_layout, co_fails, covered_by, configured_by, depends_on, wires, runs_in
```

**Build CORE types only unless a task names otherwise** (ROADMAP §16.2–16.3).

## `cochange.parquet` — the comparison arm

```
repo, window_end, file_a, file_b, support, confidence, lift, n_cochanges
```

## `gold.parquet` — causal subset

```
instance_id, test_id, verdict_base_run1, verdict_base_run2,
verdict_head_run1, verdict_head_run2, causal_label, env_digest, notes
```

## `identity_map.parquet` — node identity across SHAs

```
repo, from_sha, to_sha, old_node_id, new_node_id,
kind {renamed|moved|split|merged}, confidence, evidence
```

## `graph_index.parquet` — snapshot/delta index

```
repo, sha, snapshot_path, delta_paths list<string>, n_nodes, n_edges,
built_at, incremental_from, communities_inherited, graphify_commit
```

## Release hygiene

- Pseudonymise `author_login` with a salted hash; publish the salt separately or not at all, and document the choice.
- Store `failure_message` in a separate file — it can contain absolute paths and environment detail. Scan with `gitleaks` before release.
- Ship `schema.json` and `validate.py` that check any Parquet file against this document.

## Evaluation protocol (frozen before Phase 4)

- **Splits are time-based, never random.** Train ≤ 2026-08-31 · validate 2026-09-01→09-30 · test ≥ 2026-10-01. Plus leave-one-project-out for cross-project.
- **Primary metric:** Recall@k, k ∈ {1%, 5%, 10%, 20%}.
- **Statistics:** 5 seeds, Wilcoxon signed-rank on paired per-instance scores, Holm–Bonferroni across the baseline family, Cliff's delta, bootstrap 95% CIs.
- **Headline results use `strict`.** If a finding flips between splits, that is the finding — report it.
- **Hyperparameters tuned on validation only, never on test.**

## Change log

| Date | Change | Agreed by |
|---|---|---|
| _(Week 2)_ | Initial freeze | _pending_ |
