# BlastRadius — Data Schemas

> **Released tables: the binding contract is the appended section ["Release schema v0.2 (D-54)"](#release-schema-v02-d-54) at the bottom of this file; the design sections below stay as historical design.**

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

---

## Release schema v0.2 (D-54)

> **Binding contract for released tables (`release/v0.2/*`) and the T1.6a validator.** The sections above are the historical design; 030 (`docs/phase/030-schema-divergence.md`) measured 39 divergent declared columns. v0.2 fills only columns derivable offline from `data/interim/*` at release-build time, by joins in `analysis/build_release.py`. No interim table is rewritten. Row grain and row counts equal v0.1: instances 165,349 · outcomes 12,766 · cochange 175,204 · failure_messages 3,490.
> Coverage = non-null share of the release table's rows, from 030 measurements unless noted; the build report (h) re-measures it.
> All parquet types below are the physical types written. Every column is declared nullable in parquet; "Nullable" here is the contract (`no` = validator fails on any null).

### instances.parquet (165,349 rows, one per workflow run)

Columns carried unchanged from v0.1, values and order untouched except `author_login`, which is pseudonymised with the same `BR_PSEUDONYM_KEY` as v0.1. `repo_full` stays (duplicate of `repo`; v0.2 does no renames and drops nothing).

| column | type | nullable | expected coverage | source table.column |
|---|---|---|---|---|
| instance_id | VARCHAR | no | 100% | instances_raw.instance_id |
| repo | VARCHAR | no | 100% | instances_raw.repo |
| repo_full | VARCHAR | no | 100% | instances_raw.repo_full |
| language | VARCHAR | no | 100% | instances_raw.language (`Java` / `Python`, case as shipped) |
| pr_number | BIGINT | no | 100% | instances_raw.pr_number |
| head_sha | VARCHAR | no | 100% | instances_raw.head_sha |
| base_sha | VARCHAR | no | 100% | instances_raw.base_sha |
| base_ref | VARCHAR | no | 100% | instances_raw.base_ref |
| run_id | BIGINT | no | 100% | instances_raw.run_id |
| workflow_id | BIGINT | no | 100% | instances_raw.workflow_id |
| workflow_name | VARCHAR | no | 100% | instances_raw.workflow_name |
| created_at | VARCHAR | no | 100% | instances_raw.created_at |
| run_conclusion | VARCHAR | yes | 99.96% | instances_raw.run_conclusion |
| job_ids | BIGINT[] | no | 100% | instances_raw.job_ids |
| job_conclusions | VARCHAR[] | no | 100% | instances_raw.job_conclusions |
| n_matrix_legs | INTEGER | yes | 99.98% | instances_raw.n_matrix_legs |
| is_bot_pr | BOOLEAN | no | 100% | instances_raw.is_bot_pr |
| bot_name | VARCHAR | yes | 9.13% | instances_raw.bot_name |
| author_login | VARCHAR | no | 100% | instances_raw.author_login, replaced by 16-hex HMAC-SHA256 pseudonym |
| event_type | VARCHAR | no | 100% | instances_raw.event_type |

Changed and added columns (column positions in the file: the unchanged block keeps v0.1 order with `run_started_at` and `base_run_id` in their v0.1 positions, new columns follow):

| column | type | nullable | expected coverage | source table.column |
|---|---|---|---|---|
| run_started_at (CAST) | TIMESTAMP (UTC, no tz offset stored) | no | 100% | instances_raw.run_started_at (ISO-8601 `Z` string, lossless cast) |
| base_run_id (FILLED) | BIGINT | yes | 7,061 / 165,349 = 4.27% | base_resolution_new.base_run_id (DOUBLE cast to BIGINT), join on run_id |
| base_status (NEW) | VARCHAR, enum `exact_green`/`exact`/`ancestor`/`branch_prior`/`no_base`/`not_attempted` | no | 100% | base_resolution_new.status verbatim: `exact_green`, `exact`, `ancestor`, `branch_prior`, `no_base`; `not_attempted` for runs absent from base_resolution_new |
| base_run_distance (NEW) | INTEGER | yes | 6,025 / 165,349 = 3.64% | base_resolution_new.base_run_distance (DOUBLE cast to INTEGER); null for `branch_prior` and 669 `exact_green` |
| n_files_changed (NEW) | INTEGER | yes | 147,985 / 165,349 = 89.5% | count(*) of changesets rows per (repo, pr_number, head_sha) |
| n_lines_changed (NEW) | BIGINT | yes | 89.5% | sum(changesets.additions + changesets.deletions) |
| touches_test_file (NEW) | BOOLEAN | yes | 89.5% | bool_or(changesets.touches_test_file) |
| touches_build_config (NEW) | BOOLEAN | yes | 89.5% | bool_or(changesets.touches_build_config) |
| touches_ci_config (NEW) | BOOLEAN | yes | 89.5% | bool_or(changesets.touches_ci_config) |
| is_docs_only (NEW) | BOOLEAN | yes | 89.5% | bool_and(changesets.is_docs_only). Definition is `src/parse/changeset.py`'s `all_docs`: true iff every changed file's lowercase name ends `.md`, `.txt` or `.rst` or its path contains `docs/` |
| changed_files (NEW) | VARCHAR[] | yes | 89.5% | list(changesets.filename), sorted ascending. **Paths only, no hunks, no status/additions/deletions struct** (the design's `list<struct>` is not shipped) |

- changesets join key: `(instances.repo = changesets.repo, CAST(instances.pr_number AS VARCHAR) = changesets.pr_number, instances.head_sha = changesets.head_sha)`. The 17,364 runs with no changeset get null in all changeset-derived columns (never 0 / false / empty list).
- **Null rule:** every changeset-derived column (`n_files_changed`, `n_lines_changed`, the three `touches_*`, `is_docs_only`, `changed_files`) is NULL, never 0 / false / `[]`, for a run with no changeset. Their null counts are therefore equal.
- The design's `actual_changed_files` is not shipped (see Not shipped).
- `is_default_branch`: **not shipped** (see below). 030 left `data/raw` repo metadata unchecked; checked now: no `default_branch` found in the sampled raw files (runs/jobs/pages; the raw store holds API response pages, not repo metadata objects), and fetching it needs network.
- Invariant: `base_status = 'no_base'` ⇒ `base_run_id` null ⇒ no row in outcomes.

### outcomes.parquet (12,766 rows)

**Grain (kept, documented):** long by split. One row per (run_id, test_id, split) with `split` in {`all`, `strict`, `relaxed`}: 4,384 distinct (run_id, test_id) pairs × `all` 4,384 + `strict` 4,168 + `relaxed` 4,214. Every row is a positive (fault-revealing) label; the design's `split_strict` / `split_permissive` booleans are expressed by `split` membership. All added columns are properties of the (run_id, test_id) pair and repeat identically across its split rows.

| column | type | nullable | expected coverage | source table.column |
|---|---|---|---|---|
| run_id | BIGINT | no | 100% | outcomes.run_id (unchanged) |
| test_id | VARCHAR | no | 100% | outcomes.test_id (unchanged) |
| split | VARCHAR, enum `all`/`strict`/`relaxed` | no | 100% | outcomes.split (unchanged) |
| test_file (NEW) | VARCHAR | yes | 4,229 / 4,384 pairs = 96.5% | binding.resolved_path where binding.status = `exact`, join (instances.repo via run_id, test_id) |
| label_source (NEW) | VARCHAR, enum `log` | no | 100% | parsed_outcomes.label_source (`log` for all rows today) |
| parser_confidence (NEW) | FLOAT | no | 100% | parsed_outcomes.parser_confidence; min over job rows of the pair |
| status_head (NEW) | VARCHAR, enum `fail`/`error` | no | 100% | parsed_outcomes.status; `fail` if any job row of the pair is `fail`, else `error` |
| n_job_rows (NEW) | INTEGER | no | 100% | count(*) of parsed_outcomes rows (job rows, i.e. matrix legs, D-12) aggregated into the (run_id, test_id) pair; 690 pairs > 1 |
| binding_status (NEW) | VARCHAR, enum `exact`/`ambiguous`/`not_found` | yes | 100% of pairs expected (join miss ⇒ null, reported) | binding.status verbatim, **not mapped** to the design's `binding_strategy` |
| binding_confidence (NEW) | FLOAT | yes | null unless binding_status = `exact` | binding.parquet carries no confidence column; derived by the rule `analysis/paper_numbers.py` `binding()` uses for binding.md: 1.0 if status = `exact` and is_fqcn_qualified (full confidence, D-47), 0.5 if `exact` and not fully qualified (basename-only), null otherwise. Together with binding_status reproduces both D-47 figures (combined = non-null; full = 1.0) |
| duration_s (NEW) | FLOAT | yes | 2,505 / 4,384 pairs = 57.1% | parsed_outcomes.duration_s; max over non-null job rows |
| failure_message_hash (NEW) | VARCHAR (64 hex) | yes | 2,111 / 4,384 pairs = 48.2% | sha256(UTF-8 bytes of parsed_outcomes.failure_message); for pairs with several job rows, the lexicographically smallest non-null message. Must equal sha256 of the matching `failure_messages.failure_message` text |

- `__index_level_0__` is **dropped** (pandas index leak).
- Aggregation rules above resolve 030's multi-row pairs (690 with >1 job row, 4 with mixed status, 1 with >1 confidence). They are deterministic and are the contract.
- Coverage is per pair; row-level rates differ because split rows repeat pairs (030: `duration_s` 81.94% null at row level).
- Invariant: every outcomes `run_id` belongs to an instance with non-null `base_run_id` (no_base ⇒ no labels). Violation is a labelling bug, not a release bug.

### cochange.parquet (175,204 rows) — as shipped, no renames, no duplicate columns

| column | type | nullable | coverage | source |
|---|---|---|---|---|
| repo_full | VARCHAR | no | 100% | cochange.repo_full (the design's `repo` is not added) |
| file_a | VARCHAR | no | 100% | cochange.file_a |
| file_b | VARCHAR | no | 100% | cochange.file_b |
| support | BIGINT | no | 100% | cochange.support (the single co-occurrence count; the design's `n_cochanges` is not added) |
| conf_a_to_b | DOUBLE | no | 100% | cochange.conf_a_to_b (P(b changes given a changes)) |
| conf_b_to_a | DOUBLE | no | 100% | cochange.conf_b_to_a |
| lift | DOUBLE | no | 100% | cochange.lift |
| n_commits_a | BIGINT | no | 100% | cochange.n_commits_a |
| n_commits_b | BIGINT | no | 100% | cochange.n_commits_b |
| n_commits_total | BIGINT | no | 100% | cochange.n_commits_total |
| window_days | INTEGER | no | 100% | cochange.window_days |
| as_of | VARCHAR (ISO-8601 `Z`) | no | 100%, single value `2026-08-29T14:13:00Z` | cochange.as_of (kept VARCHAR; ISO-8601 UTC with literal `Z`, second precision, pattern `YYYY-MM-DDTHH:MM:SSZ`; not cast, to keep v0.1 byte-comparable). Static table mined to the corpus pin (D-52); the design's `window_end` is not added |

### failure_messages.parquet (3,490 rows) — as shipped

Grain: one row per (run_id, job_id, test_id).

| column | type | nullable | coverage | source |
|---|---|---|---|---|
| repo | VARCHAR | no | 100% | parsed_outcomes.repo |
| run_id | BIGINT | no | 100% | parsed_outcomes.run_id |
| job_id | BIGINT | no | 100% | parsed_outcomes.job_id |
| test_id | VARCHAR | no | 100% | parsed_outcomes.test_id |
| failure_message | VARCHAR (non-empty) | no | 100% | parsed_outcomes.failure_message |

### Not shipped in v0.2

| column(s) | reason |
|---|---|
| graph-derived: `changed_symbols`, `frontier_truncated`, `graph_sha`, `parse_failure_rate`, `graph_nodes`, `graph_edges` | graph layer excluded from `release/` (D-48) |
| hunks (inside `changed_files`) | no patch text stored in `changesets`; `changed_files` ships paths only |
| `status_base` (outcomes) | never computed; base_outcomes holds failing base tests only and the rest is inference code, not a lookup |
| `excluded_own_file` (outcomes) | never computed; the leakage guard cannot run on the shipped table |
| `base_run_id` / `base_run_distance` / `base_status` values for non-failing runs | resolution was run on failing runs only; filling needs a re-harvest (network). Shipped as null / `not_attempted` |
| negatives (`is_fault_revealing` = false rows, `new_test`, `suspect_unrelated`) | release is positives only; `is_fault_revealing` would be a constant `true` |
| `is_default_branch` | no repo metadata in `data/raw` (checked, sampled); needs network |
| `is_dependency_bump`, `is_formatting_only` | never computed, no source |
| `flakiness_score`, `same_sha_flip` | not persisted at row level; declared definition (trailing 30d flip rate) has no source |
| `actual_changed_files` (instances) | identical to `changed_files` because no hunks are stored |
| `frame_version` | a constant, not data; operator has not decided its value |
| `split_strict`, `split_permissive`, `binding_strategy`, `instance_id` in outcomes | not added: split expressed by `split`; binding domain differs (`binding_status` ships verbatim); outcomes joins to instances via `run_id` |
| design names `repo`/`window_end`/`confidence`/`n_cochanges` (cochange) | real names documented above; no renames or alias columns |
