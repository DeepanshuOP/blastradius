> **SUPERSEDED by `030-schema-divergence.md`**

# Schema Divergence Diagnostic Report (Phase 013-B)

**Date**: 2026-08-31  
**Status**: DIAGNOSTIC ONLY — NO DATA OR SCHEMAS MUTATED  
**Governing Authority**: `docs/SCHEMAS.md` (FROZEN, Rank 1). Parquets on disk diverge and must be corrected by downstream pipeline repairs.

---

## 1. Table-by-Table Column Divergence Analysis

### Table 1: `instances.parquet`
- **Corresponding on-disk artifact**: `data/interim/instances_raw.parquet` (165,349 rows, 22 columns)
- **Shipped release artifact**: `release/v0.1/instances.parquet` (identical schema and rows to interim)

| Column Name | Declared Type (`docs/SCHEMAS.md`) | Actual Type (`instances_raw.parquet`) | Verdict | Notes / On-Disk Data Location |
| :--- | :--- | :--- | :--- | :--- |
| `instance_id` | `string` | `string` | **MATCH** | Hash `sha256(repo\|head_sha\|run_id)` |
| `repo` | `string` | `string` | **MATCH** | Repository slug |
| `language` | `string` | `string` | **MATCH** | Language (`Java` / `Python`) |
| `pr_number` | `int64` | `int64` | **MATCH** | Pull request number |
| `head_sha` | `string` | `string` | **MATCH** | Commit SHA at PR head |
| `base_sha` | `string` | `string` | **MATCH** | Target branch base SHA |
| `base_run_id` | `int64` | `int64` (Arrow) / `float64` (Pandas) | **TYPE MISMATCH** | 100% null (165,349/165,349 null) in `instances_raw.parquet`. Populated as `float64`/`double` in `base_resolution*.parquet`. |
| `base_run_distance` | `int32` | *(None)* | **ABSENT** | Computed and stored as `float64`/`double` in `data/interim/base_resolution.parquet` & `base_resolution_new.parquet`. Never merged into instances table. |
| `run_id` | `int64` | `int64` | **MATCH** | Workflow run ID |
| `workflow_id` | `int64` | `int64` | **MATCH** | Workflow ID |
| `workflow_name` | `string` | `string` | **MATCH** | Workflow name |
| `run_conclusion` | `string` | `string` | **MATCH** | Conclusion string (`failure`, `success`, etc.) |
| `run_started_at` | `timestamp` | `string` | **TYPE MISMATCH** | Stored as ISO-8601 string (`YYYY-MM-DDTHH:MM:SSZ`), not PyArrow timestamp. |
| `changed_files` | `list<struct<...>>` | *(None)* | **ABSENT** | File-level metadata exists in `data/interim/changesets.parquet`, but line hunks (`hunks: list<struct<start:int32,end:int32>>`) were never parsed from patch text. |
| `changed_symbols` | `list<string>` | *(None)* | **ABSENT** | Not measured / Never computed (tree-sitter symbol diff was not run). |
| `n_files_changed` | `int32` | *(None)* | **ABSENT** | Computable by aggregating `changesets.parquet` / `pull_files`, but never aggregated into instances. |
| `n_lines_changed` | `int32` | *(None)* | **ABSENT** | Computable by summing `additions + deletions` in `changesets.parquet`, but never aggregated into instances. |
| `touches_test_file` | `bool` | *(None)* | **ABSENT** | Computed per-file in `changesets.parquet`, never aggregated to instance level. |
| `touches_build_config` | `bool` | *(None)* | **ABSENT** | Computed per-file in `changesets.parquet`, never aggregated to instance level. |
| `touches_ci_config` | `bool` | *(None)* | **ABSENT** | Computed per-file in `changesets.parquet`, never aggregated to instance level. |
| `is_dependency_bump` | `bool` | *(None)* | **ABSENT** | Not measured / Never computed. |
| `is_docs_only` | `bool` | *(None)* | **ABSENT** | Computed per-file in `changesets.parquet`, never aggregated to instance level. |
| `is_formatting_only` | `bool` | *(None)* | **ABSENT** | Not measured / Never computed. |
| `author_login` | `string` | `string` | **MATCH** | Author GitHub username |
| `n_matrix_legs` | `int32` | `int32` | **MATCH** | Matrix build leg count |
| `frontier_truncated` | `bool` | *(None)* | **ABSENT** | Proposed in Phase 012-A; never computed/populated in parquet. |
| `is_bot_pr` | `bool` | `bool` | **MATCH** | Bot flag (Dependabot / Renovate) |
| `bot_name` | `string` | `string` | **MATCH** | Bot name |
| `event_type` | `string` | `string` | **MATCH** | Event type (`pull_request`, etc.) |
| `is_default_branch` | `bool` | *(None)* | **ABSENT** | Not measured (raw `base_ref` is present, but default branch status was not resolved from repo metadata). |
| `graph_sha` | `string` | *(None)* | **ABSENT** | Not measured (Phase 2 graph layer cut per ROADMAP §10 / D-05 / HANDOFF §2). |
| `parse_failure_rate` | `float32` | *(None)* | **ABSENT** | Not measured (Graph build parse failure rate; graph layer cut). |
| `frame_version` | `string` | *(None)* | **ABSENT** | Not populated (fixed frame constant `'v1'` exists in config/docs, omitted from table). |
| `actual_changed_files` | `list<string>` | *(None)* | **ABSENT** | Exists as individual rows in `data/interim/changesets.parquet`, never collected into `list<string>` on instances. |
| *(Extra on disk)* `repo_full` | *(None)* | `string` | **EXTRA** | Redundant copy of `repo`. |
| *(Extra on disk)* `base_ref` | *(None)* | `string` | **EXTRA** | Target branch name from GitHub API. |
| *(Extra on disk)* `created_at` | *(None)* | `string` | **EXTRA** | Redundant ISO-8601 run creation timestamp string. |
| *(Extra on disk)* `job_ids` | *(None)* | `list<int64>` | **EXTRA** | List of workflow job IDs. |
| *(Extra on disk)* `job_conclusions` | *(None)* | `list<string>` | **EXTRA** | List of workflow job conclusions. |

---

### Table 2: `outcomes.parquet`
- **Corresponding on-disk artifact**: `data/interim/outcomes.parquet` (8,980 rows, 4 columns) & `data/interim/parsed_outcomes.parquet` (20,535 rows, 14 columns)
  *(Correction: `parsed_outcomes.parquet` row count 20,535 is superseded by **20,451** post-fix per Phase 023 consolidation).*
- **Shipped release artifact**: `release/v0.1/labels.parquet` (8,980 rows, identical schema and data to `data/interim/outcomes.parquet`)

| Column Name | Declared Type (`docs/SCHEMAS.md`) | Actual Type (`outcomes.parquet` / `labels.parquet`) | Verdict | Notes / On-Disk Data Location |
| :--- | :--- | :--- | :--- | :--- |
| `instance_id` | `string` | *(None)* | **ABSENT** | Replaced on disk with `run_id`. Joinable from `instances_raw.parquet` via `run_id`. |
| `test_id` | `string` | `large_string` / `string` | **MATCH** | Canonical test identifier |
| `test_file` | `string` | *(None)* | **ABSENT** | Exists in `data/interim/binding.parquet` and `release/v0.1/bindings.parquet` (`resolved_path`). All-null in `parsed_outcomes.parquet`. |
| `status_head` | `string` | *(None)* | **ABSENT** | Exists in `data/interim/parsed_outcomes.parquet` (`status` column, e.g. `'fail'`). |
| `status_base` | `string` | *(None)* | **ABSENT** | Exists in `data/interim/base_outcomes.parquet` or inferred green via `base_resolution.parquet` (`exact_green`). |
| `is_fault_revealing` | `bool` | *(None)* | **ABSENT** | Implicit: all rows in `outcomes.parquet` are positive labels (`split` filter). Explicit boolean column is absent. |
| `flakiness_score` | `float32` | *(None)* | **ABSENT** | Not measured / Never computed (trailing 30d flip rate). |
| `same_sha_flip` | `bool` | *(None)* | **ABSENT** | Not measured / Never computed. |
| `label_source` | `string` | *(None)* | **ABSENT** | Exists in `data/interim/parsed_outcomes.parquet` (`'log'`). |
| `parser_confidence` | `float32` | *(None)* | **ABSENT** | Exists in `data/interim/parsed_outcomes.parquet` (`float32`). |
| `duration_s` | `float32` | *(None)* | **ABSENT** | Exists in `data/interim/parsed_outcomes.parquet` (`float32`). |
| `failure_message_hash` | `string` | *(None)* | **ABSENT** | Raw message exists in `data/interim/parsed_outcomes.parquet` (`failure_message`); SHA-256 hash was never computed. |
| `split_strict` | `bool` | *(None)* | **ABSENT** | Serialized as string value `split == 'strict'` in `split` column rather than boolean flag. |
| `split_permissive` | `bool` | *(None)* | **ABSENT** | Serialized as string value in `split` column (`'relaxed'`) rather than boolean flag. |
| `new_test` | `bool` | *(None)* | **ABSENT** | Not measured / Never computed. |
| `suspect_unrelated` | `bool` | *(None)* | **ABSENT** | Not measured / Never computed. |
| `excluded_own_file` | `bool` | *(None)* | **ABSENT** | Not measured / Never computed (leakage guard column not evaluated into table). |
| `binding_strategy` | `string` | *(None)* | **ABSENT** | Exists in `data/interim/binding.parquet` (`status` column: `exact`, `ambiguous`, `not_found`). |
| *(Extra on disk)* `run_id` | *(None)* | `int64` | **EXTRA** | Used as instance foreign key instead of declared `instance_id`. |
| *(Extra on disk)* `split` | *(None)* | `large_string` | **EXTRA** | String enum (`'strict'`, `'relaxed'`, `'all'`) replacing boolean split columns. |
| *(Extra on disk)* `__index_level_0__` | *(None)* | `int64` | **EXTRA** | Pandas default DataFrame index artifact serialized to Parquet. |

---

### Table 3: `graph_nodes.parquet`
- **Corresponding on-disk artifact**: *(None — Table absent)*
- **Status**: Phase 2 graph layer cut per ROADMAP §10, DECISIONS D-05, and HANDOFF §2.

| Total Declared Columns | Present on Disk | Verdict | Notes |
| :--- | :--- | :--- | :--- |
| 26 columns (`repo`, `sha`, `node_id`, `label`, `node_type`, `source_file`, `test_id`, `loc`, `complexity`, `churn_90d`, `age_days`, `community_id`, `pagerank`, `degree`, `kind`, `fqn`, `body_sha`, `content_sha`, `parse_status`, `is_generated`, `is_vendored`, `annotations`, `has_dynamic_boundary`, `n_dynamic_sites`, `start_line`, `end_line`) | 0 / 26 | **ALL ABSENT** | Never computed / Table never generated (Cut). |

---

### Table 4: `graph_edges.parquet`
- **Corresponding on-disk artifact**: *(None — Table absent)*
- **Status**: Phase 2 graph layer cut per ROADMAP §10, DECISIONS D-05, and HANDOFF §2.

| Total Declared Columns | Present on Disk | Verdict | Notes |
| :--- | :--- | :--- | :--- |
| 8 columns (`repo`, `sha`, `src`, `dst`, `edge_type`, `confidence`, `confidence_score`, `weight`) | 0 / 8 | **ALL ABSENT** | Never computed / Table never generated (Cut). |

---

### Table 5: `cochange.parquet`
- **Corresponding on-disk artifact**: `data/interim/cochange.parquet` (175,204 rows, 12 columns)
- **Shipped release artifact**: *(None)*

| Column Name | Declared Type (`docs/SCHEMAS.md`) | Actual Type (`cochange.parquet`) | Verdict | Notes / On-Disk Data Location |
| :--- | :--- | :--- | :--- | :--- |
| `repo` | `string` | *(None)* | **ABSENT** | Stored on disk as `repo_full`. |
| `window_end` | `timestamp`/`string` | *(None)* | **ABSENT** | Stored on disk as `as_of`. |
| `file_a` | `string` | `string` | **MATCH** | File A relative path |
| `file_b` | `string` | `string` | **MATCH** | File B relative path |
| `support` | `int64` | `int64` | **MATCH** | Co-change support count |
| `confidence` | `float64` | *(None)* | **ABSENT** | Stored as directional pairs `conf_a_to_b` and `conf_b_to_a`. |
| `lift` | `float64` | `double` (`float64`) | **MATCH** | Lift metric |
| `n_cochanges` | `int64` | *(None)* | **ABSENT** | Stored on disk as `support`. |
| *(Extra on disk)* `repo_full` | *(None)* | `string` | **EXTRA** | Corresponds to declared `repo`. |
| *(Extra on disk)* `conf_a_to_b` | *(None)* | `double` | **EXTRA** | Directional confidence A -> B. |
| *(Extra on disk)* `conf_b_to_a` | *(None)* | `double` | **EXTRA** | Directional confidence B -> A. |
| *(Extra on disk)* `n_commits_a` | *(None)* | `int64` | **EXTRA** | Number of commits modifying file A. |
| *(Extra on disk)* `n_commits_b` | *(None)* | `int64` | **EXTRA** | Number of commits modifying file B. |
| *(Extra on disk)* `n_commits_total` | *(None)* | `int64` | **EXTRA** | Total commits mined in window. |
| *(Extra on disk)* `window_days` | *(None)* | `int32` | **EXTRA** | Time window parameter (365 days). |
| *(Extra on disk)* `as_of` | *(None)* | `string` | **EXTRA** | Corresponds to declared `window_end`. |

---

### Table 6: `gold.parquet`
- **Corresponding on-disk artifact**: *(None — Table absent)*
- **Status**: Causal re-execution gold subset cut per ROADMAP §35 (T1.5) and HANDOFF §2.

| Total Declared Columns | Present on Disk | Verdict | Notes |
| :--- | :--- | :--- | :--- |
| 9 columns (`instance_id`, `test_id`, `verdict_base_run1`, `verdict_base_run2`, `verdict_head_run1`, `verdict_head_run2`, `causal_label`, `env_digest`, `notes`) | 0 / 9 | **ALL ABSENT** | Never computed / Table never generated (Cut). |

---

### Table 7: `identity_map.parquet`
- **Corresponding on-disk artifact**: *(None — Table absent)*
- **Status**: Graph node cross-SHA identity mapping cut per ROADMAP §10 and HANDOFF §2.

| Total Declared Columns | Present on Disk | Verdict | Notes |
| :--- | :--- | :--- | :--- |
| 8 columns (`repo`, `from_sha`, `to_sha`, `old_node_id`, `new_node_id`, `kind`, `confidence`, `evidence`) | 0 / 8 | **ALL ABSENT** | Never computed / Table never generated (Cut). |

---

### Table 8: `graph_index.parquet`
- **Corresponding on-disk artifact**: *(None — Table absent)*
- **Status**: Graph snapshot index cut per ROADMAP §10 and HANDOFF §2.

| Total Declared Columns | Present on Disk | Verdict | Notes |
| :--- | :--- | :--- | :--- |
| 10 columns (`repo`, `sha`, `snapshot_path`, `delta_paths`, `n_nodes`, `n_edges`, `built_at`, `incremental_from`, `communities_inherited`, `graphify_commit`) | 0 / 10 | **ALL ABSENT** | Never computed / Table never generated (Cut). |

---

## 2. Divergence Totals per Table

| Table | Declared Columns | MATCH | TYPE MISMATCH | ABSENT Columns | EXTRA Columns | Total Divergences | Table Status on Disk |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`instances.parquet`** | 34 | 14 | 2 | 18 | 5 | **25** | Present (`data/interim/instances_raw.parquet`) |
| **`outcomes.parquet`** | 18 | 1 | 0 | 17 | 3 | **20** | Present (`data/interim/outcomes.parquet`) |
| **`graph_nodes.parquet`** | 26 | 0 | 0 | 26 | 0 | **26** | Cut / Never generated |
| **`graph_edges.parquet`** | 8 | 0 | 0 | 8 | 0 | **8** | Cut / Never generated |
| **`cochange.parquet`** | 8 | 4 | 0 | 4 | 8 | **12** | Present (`data/interim/cochange.parquet`) |
| **`gold.parquet`** | 9 | 0 | 0 | 9 | 0 | **9** | Cut / Never generated |
| **`identity_map.parquet`** | 8 | 0 | 0 | 8 | 0 | **8** | Cut / Never generated |
| **`graph_index.parquet`** | 10 | 0 | 0 | 10 | 0 | **10** | Cut / Never generated |
| **TOTAL** | **121** | **19** | **2** | **100** | **16** | **118** | — |

---

## 3. Absent Column Inventory & Provenance

For every ABSENT column across the tables, its empirical status on disk is categorized below:

### 3.1 Exists in Interim Scratch / Satellite Parquets on Disk (Joinable / Mergeable)
1. **`instances.base_run_distance`**: Computed as `double`/`float64` in `data/interim/base_resolution.parquet` & `base_resolution_new.parquet`. Needs cast to `int32` and join on `run_id`.
2. **`instances.actual_changed_files`**: Present as row-level filenames in `data/interim/changesets.parquet`. Needs `list<string>` aggregation grouped by `head_sha`.
3. **`outcomes.instance_id`**: Present in `data/interim/instances_raw.parquet`. Needs join on `run_id`.
4. **`outcomes.test_file`**: Present as `resolved_path` in `data/interim/binding.parquet`. Needs join on `(repo, test_id)`.
5. **`outcomes.status_head`**: Present as `status` in `data/interim/parsed_outcomes.parquet`. Needs join on `(run_id, test_id)`.
6. **`outcomes.status_base`**: Present in `data/interim/base_outcomes.parquet` (or inferred green from `base_resolution.status == 'exact_green'`).
7. **`outcomes.label_source`**: Present as `'log'` in `data/interim/parsed_outcomes.parquet`.
8. **`outcomes.parser_confidence`**: Present in `data/interim/parsed_outcomes.parquet` (`float32`).
9. **`outcomes.duration_s`**: Present in `data/interim/parsed_outcomes.parquet` (`float32`).
10. **`outcomes.binding_strategy`**: Present as `status` in `data/interim/binding.parquet`.
11. **`cochange.repo`**: Stored as `repo_full` in `data/interim/cochange.parquet`.
12. **`cochange.window_end`**: Stored as `as_of` in `data/interim/cochange.parquet`.
13. **`cochange.confidence`**: Stored as `conf_a_to_b` and `conf_b_to_a` in `data/interim/cochange.parquet`.
14. **`cochange.n_cochanges`**: Stored as `support` in `data/interim/cochange.parquet`.

### 3.2 Computable from Existing Disk Artifacts (Never Aggregated)
1. **`instances.n_files_changed`**: Computable via `count(filename)` from `data/interim/changesets.parquet`.
2. **`instances.n_lines_changed`**: Computable via `sum(additions + deletions)` from `data/interim/changesets.parquet`.
3. **`instances.touches_test_file`**: Computable via `any(touches_test_file)` from `changesets.parquet`.
4. **`instances.touches_build_config`**: Computable via `any(touches_build_config)` from `changesets.parquet`.
5. **`instances.touches_ci_config`**: Computable via `any(touches_ci_config)` from `changesets.parquet`.
6. **`instances.is_docs_only`**: Computable via `all(is_docs_only)` from `changesets.parquet`.
7. **`outcomes.is_fault_revealing`**: Computable by assigning `True` to all rows satisfying split criteria.
8. **`outcomes.split_strict`**: Computable from `split == 'strict'`.
9. **`outcomes.split_permissive`**: Computable from `split in ('strict', 'relaxed')`.
10. **`outcomes.failure_message_hash`**: Computable via `sha256(failure_message)` from `data/interim/parsed_outcomes.parquet`.

### 3.3 Not Measured / Never Computed in Pipeline
1. **`instances.changed_files` (hunks struct)**: Line-level hunk ranges (`start`, `end`) were never parsed from raw unified diffs.
2. **`instances.changed_symbols`**: Tree-sitter symbol AST diffing was not executed.
3. **`instances.is_dependency_bump`**: No automated dependency bump classifier was run.
4. **`instances.is_formatting_only`**: No formatting diff classifier was run.
5. **`instances.frontier_truncated`**: Proposed in 012-A; no column exists in any parquet.
6. **`instances.is_default_branch`**: Never queried or resolved from repository metadata.
7. **`instances.frame_version`**: Never populated in parquet.
8. **`outcomes.flakiness_score`**: Trailing 30-day flip rate was not computed.
9. **`outcomes.same_sha_flip`**: Same-SHA multi-run flip rate was not computed.
10. **`outcomes.new_test`**: Head vs. base test existence delta was not computed.
11. **`outcomes.suspect_unrelated`**: DeFlaker heuristic was not implemented.
12. **`outcomes.excluded_own_file`**: Leakage guard was not written to parquet.
13. **`graph_nodes.*` (26 columns)**, **`graph_edges.*` (8 columns)**, **`identity_map.*` (8 columns)**, **`graph_index.*` (10 columns)**: Phase 2 Graph layer cut.
14. **`gold.*` (9 columns)**: Causal re-execution gold subset cut (T1.5).

---

## 4. Release Flags: `release/v0.1/` Impact Analysis

`package_release.py` exported raw interim tables directly to `release/v0.1/` without schema reconciliation:
1. **`release/v0.1/instances.parquet`**:
   - Suffers from all 25 divergences identified in `instances.parquet`.
   - `base_run_id` is 100% null.
   - `base_run_distance` is completely absent.
   - Carries 5 un-declared extra columns (`repo_full`, `base_ref`, `created_at`, `job_ids`, `job_conclusions`).
2. **`release/v0.1/labels.parquet`**:
   - Shipped under the non-standard filename `labels.parquet` instead of `outcomes.parquet`.
   - Suffers from all 20 divergences identified in `outcomes.parquet`.
   - Keyed by `run_id` rather than canonical `instance_id`.
   - Lacks `test_file`, `status_head`, `status_base`, `is_fault_revealing`, `binding_strategy`, and boolean split flags.
   - Leaks the internal Pandas indexing column `__index_level_0__`.
3. **`release/v0.1/bindings.parquet` & `release/v0.1/changesets.parquet`**:
   - Shipped as separate satellite tables that are not declared in `docs/SCHEMAS.md`.
   - Their fields belong inside `outcomes.parquet` (`test_file`, `binding_strategy`) and `instances.parquet` (`changed_files`, `touches_*` flags).

**Conclusion**: `release/v0.1/` was cut directly from un-reconciled interim data and diverges substantially from `docs/SCHEMAS.md`. Promoting `package_release.py` to `analysis/` and wiring it into `make tables` (CLI-1 task) must include an explicit projection and join step to emit schema-compliant parquets matching `docs/SCHEMAS.md`.
