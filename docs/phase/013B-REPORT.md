# Phase 013-B REPORT

## 1. Full Schema Divergence Table (docs/SCHEMAS.md vs On-Disk Parquets)

### Table: `instances.parquet` (Declared: 34 columns | Interim: `data/interim/instances_raw.parquet` | Release: `release/v0.1/instances.parquet`)
| Column Name | Declared Type | Actual Type | Verdict | Notes / On-Disk Data Location |
| :--- | :--- | :--- | :--- | :--- |
| `instance_id` | `string` | `string` | **MATCH** | Hash `sha256(repo\|head_sha\|run_id)` |
| `repo` | `string` | `string` | **MATCH** | Repository slug |
| `language` | `string` | `string` | **MATCH** | Language (`Java` / `Python`) |
| `pr_number` | `int64` | `int64` | **MATCH** | Pull request number |
| `head_sha` | `string` | `string` | **MATCH** | Commit SHA at PR head |
| `base_sha` | `string` | `string` | **MATCH** | Target branch base SHA |
| `base_run_id` | `int64` | `int64` (Arrow) / `float64` (Pandas) | **TYPE MISMATCH** | 100% null in table; populated as `float64`/`double` in `base_resolution*.parquet` |
| `base_run_distance` | `int32` | *(None)* | **ABSENT** | In `base_resolution.parquet` & `base_resolution_new.parquet` as `float64` |
| `run_id` | `int64` | `int64` | **MATCH** | Workflow run ID |
| `workflow_id` | `int64` | `int64` | **MATCH** | Workflow ID |
| `workflow_name` | `string` | `string` | **MATCH** | Workflow name |
| `run_conclusion` | `string` | `string` | **MATCH** | Run conclusion (`failure`, `success`, etc.) |
| `run_started_at` | `timestamp` | `string` | **TYPE MISMATCH** | Stored as ISO-8601 string, not PyArrow timestamp |
| `changed_files` | `list<struct<...>>` | *(None)* | **ABSENT** | In `changesets.parquet` without parsed line hunks |
| `changed_symbols` | `list<string>` | *(None)* | **ABSENT** | Not measured / Never computed (tree-sitter symbol diff cut) |
| `n_files_changed` | `int32` | *(None)* | **ABSENT** | Computable from `changesets.parquet`, never aggregated |
| `n_lines_changed` | `int32` | *(None)* | **ABSENT** | Computable from `changesets.parquet`, never aggregated |
| `touches_test_file` | `bool` | *(None)* | **ABSENT** | Present per-file in `changesets.parquet`, not aggregated |
| `touches_build_config` | `bool` | *(None)* | **ABSENT** | Present per-file in `changesets.parquet`, not aggregated |
| `touches_ci_config` | `bool` | *(None)* | **ABSENT** | Present per-file in `changesets.parquet`, not aggregated |
| `is_dependency_bump` | `bool` | *(None)* | **ABSENT** | Not measured / Never computed |
| `is_docs_only` | `bool` | *(None)* | **ABSENT** | Present per-file in `changesets.parquet`, not aggregated |
| `is_formatting_only` | `bool` | *(None)* | **ABSENT** | Not measured / Never computed |
| `author_login` | `string` | `string` | **MATCH** | Author GitHub username |
| `n_matrix_legs` | `int32` | `int32` | **MATCH** | Matrix build leg count |
| `frontier_truncated` | `bool` | *(None)* | **ABSENT** | Proposed in 012-A; never computed/populated |
| `is_bot_pr` | `bool` | `bool` | **MATCH** | Bot flag (Dependabot / Renovate) |
| `bot_name` | `string` | `string` | **MATCH** | Bot name |
| `event_type` | `string` | `string` | **MATCH** | Event type (`pull_request`, etc.) |
| `is_default_branch` | `bool` | *(None)* | **ABSENT** | Not measured (raw `base_ref` present, not resolved) |
| `graph_sha` | `string` | *(None)* | **ABSENT** | Not measured (Graph layer cut) |
| `parse_failure_rate` | `float32` | *(None)* | **ABSENT** | Not measured (Graph layer cut) |
| `frame_version` | `string` | *(None)* | **ABSENT** | Not populated in table |
| `actual_changed_files` | `list<string>` | *(None)* | **ABSENT** | Exists as rows in `changesets.parquet`, not aggregated |
| *(Extra)* `repo_full` | *(None)* | `string` | **EXTRA** | Redundant copy of `repo` |
| *(Extra)* `base_ref` | *(None)* | `string` | **EXTRA** | Target branch name |
| *(Extra)* `created_at` | *(None)* | `string` | **EXTRA** | Creation timestamp string |
| *(Extra)* `job_ids` | *(None)* | `list<int64>` | **EXTRA** | List of workflow job IDs |
| *(Extra)* `job_conclusions` | *(None)* | `list<string>` | **EXTRA** | List of workflow job conclusions |

### Table: `outcomes.parquet` (Declared: 18 columns | Interim: `data/interim/outcomes.parquet` | Release: `release/v0.1/labels.parquet`)
| Column Name | Declared Type | Actual Type | Verdict | Notes / On-Disk Data Location |
| :--- | :--- | :--- | :--- | :--- |
| `instance_id` | `string` | *(None)* | **ABSENT** | Replaced with `run_id`; joinable from `instances_raw.parquet` |
| `test_id` | `string` | `large_string` / `string` | **MATCH** | Canonical test identifier |
| `test_file` | `string` | *(None)* | **ABSENT** | In `binding.parquet` as `resolved_path` |
| `status_head` | `string` | *(None)* | **ABSENT** | In `parsed_outcomes.parquet` as `status` |
| `status_base` | `string` | *(None)* | **ABSENT** | In `base_outcomes.parquet` or inferred green |
| `is_fault_revealing` | `bool` | *(None)* | **ABSENT** | Implicit: all rows in table are positive labels |
| `flakiness_score` | `float32` | *(None)* | **ABSENT** | Not measured / Never computed |
| `same_sha_flip` | `bool` | *(None)* | **ABSENT** | Not measured / Never computed |
| `label_source` | `string` | *(None)* | **ABSENT** | In `parsed_outcomes.parquet` as `'log'` |
| `parser_confidence` | `float32` | *(None)* | **ABSENT** | In `parsed_outcomes.parquet` |
| `duration_s` | `float32` | *(None)* | **ABSENT** | In `parsed_outcomes.parquet` |
| `failure_message_hash` | `string` | *(None)* | **ABSENT** | Raw message in `parsed_outcomes.parquet`, hash not computed |
| `split_strict` | `bool` | *(None)* | **ABSENT** | Encoded as `split == 'strict'` in `split` column |
| `split_permissive` | `bool` | *(None)* | **ABSENT** | Encoded as string in `split` column (`'relaxed'`) |
| `new_test` | `bool` | *(None)* | **ABSENT** | Not measured / Never computed |
| `suspect_unrelated` | `bool` | *(None)* | **ABSENT** | Not measured / Never computed |
| `excluded_own_file` | `bool` | *(None)* | **ABSENT** | Not measured / Never evaluated to column |
| `binding_strategy` | `string` | *(None)* | **ABSENT** | In `binding.parquet` as `status` |
| *(Extra)* `run_id` | *(None)* | `int64` | **EXTRA** | Used as foreign key instead of `instance_id` |
| *(Extra)* `split` | *(None)* | `large_string` | **EXTRA** | String column replacing boolean flags |
| *(Extra)* `__index_level_0__` | *(None)* | `int64` | **EXTRA** | Serialized Pandas default index artifact |

### Table: `graph_nodes.parquet` (Declared: 26 columns | On-Disk: None — Table Cut)
- All 26 declared columns (`repo`, `sha`, `node_id`, `label`, `node_type`, `source_file`, `test_id`, `loc`, `complexity`, `churn_90d`, `age_days`, `community_id`, `pagerank`, `degree`, `kind`, `fqn`, `body_sha`, `content_sha`, `parse_status`, `is_generated`, `is_vendored`, `annotations`, `has_dynamic_boundary`, `n_dynamic_sites`, `start_line`, `end_line`) are **ABSENT** (Never computed / Table never generated).

### Table: `graph_edges.parquet` (Declared: 8 columns | On-Disk: None — Table Cut)
- All 8 declared columns (`repo`, `sha`, `src`, `dst`, `edge_type`, `confidence`, `confidence_score`, `weight`) are **ABSENT** (Never computed / Table never generated).

### Table: `cochange.parquet` (Declared: 8 columns | Interim: `data/interim/cochange.parquet` | Release: None)
| Column Name | Declared Type | Actual Type | Verdict | Notes / On-Disk Data Location |
| :--- | :--- | :--- | :--- | :--- |
| `repo` | `string` | *(None)* | **ABSENT** | Stored on disk as `repo_full` |
| `window_end` | `timestamp`/`string` | *(None)* | **ABSENT** | Stored on disk as `as_of` |
| `file_a` | `string` | `string` | **MATCH** | File A relative path |
| `file_b` | `string` | `string` | **MATCH** | File B relative path |
| `support` | `int64` | `int64` | **MATCH** | Co-change support count |
| `confidence` | `float64` | *(None)* | **ABSENT** | Stored as `conf_a_to_b` and `conf_b_to_a` |
| `lift` | `float64` | `double` (`float64`) | **MATCH** | Lift metric |
| `n_cochanges` | `int64` | *(None)* | **ABSENT** | Stored on disk as `support` |
| *(Extra)* `repo_full` | *(None)* | `string` | **EXTRA** | Declared `repo` |
| *(Extra)* `conf_a_to_b` | *(None)* | `double` | **EXTRA** | Directional confidence A -> B |
| *(Extra)* `conf_b_to_a` | *(None)* | `double` | **EXTRA** | Directional confidence B -> A |
| *(Extra)* `n_commits_a` | *(None)* | `int64` | **EXTRA** | Commits modifying file A |
| *(Extra)* `n_commits_b` | *(None)* | `int64` | **EXTRA** | Commits modifying file B |
| *(Extra)* `n_commits_total` | *(None)* | `int64` | **EXTRA** | Total commits mined |
| *(Extra)* `window_days` | *(None)* | `int32` | **EXTRA** | 365 days window |
| *(Extra)* `as_of` | *(None)* | `string` | **EXTRA** | Declared `window_end` |

### Table: `gold.parquet` (Declared: 9 columns | On-Disk: None — Table Cut)
- All 9 declared columns (`instance_id`, `test_id`, `verdict_base_run1`, `verdict_base_run2`, `verdict_head_run1`, `verdict_head_run2`, `causal_label`, `env_digest`, `notes`) are **ABSENT** (Never computed / Table never generated).

### Table: `identity_map.parquet` (Declared: 8 columns | On-Disk: None — Table Cut)
- All 8 declared columns (`repo`, `from_sha`, `to_sha`, `old_node_id`, `new_node_id`, `kind`, `confidence`, `evidence`) are **ABSENT** (Never computed / Table never generated).

### Table: `graph_index.parquet` (Declared: 10 columns | On-Disk: None — Table Cut)
- All 10 declared columns (`repo`, `sha`, `snapshot_path`, `delta_paths`, `n_nodes`, `n_edges`, `built_at`, `incremental_from`, `communities_inherited`, `graphify_commit`) are **ABSENT** (Never computed / Table never generated).

---

## 2. Per-Table Divergence Totals

| Table | Declared | MATCH | TYPE MISMATCH | ABSENT | EXTRA | Total Divergences | Status on Disk |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `instances.parquet` | 34 | 14 | 2 | 18 | 5 | **25** | Present (`data/interim/instances_raw.parquet`) |
| `outcomes.parquet` | 18 | 1 | 0 | 17 | 3 | **20** | Present (`data/interim/outcomes.parquet`) |
| `graph_nodes.parquet` | 26 | 0 | 0 | 26 | 0 | **26** | Cut / Never generated |
| `graph_edges.parquet` | 8 | 0 | 0 | 8 | 0 | **8** | Cut / Never generated |
| `cochange.parquet` | 8 | 4 | 0 | 4 | 8 | **12** | Present (`data/interim/cochange.parquet`) |
| `gold.parquet` | 9 | 0 | 0 | 9 | 0 | **9** | Cut / Never generated |
| `identity_map.parquet` | 8 | 0 | 0 | 8 | 0 | **8** | Cut / Never generated |
| `graph_index.parquet` | 10 | 0 | 0 | 10 | 0 | **10** | Cut / Never generated |
| **TOTAL** | **121** | **19** | **2** | **100** | **16** | **118** | — |

---

## 3. Release Flags (`release/v0.1/`)

1. **`release/v0.1/instances.parquet`**: Identical to `instances_raw.parquet`. Missing 18 columns, `base_run_id` is 100% null, `base_run_distance` is absent, and 5 extra un-declared columns are present.
2. **`release/v0.1/labels.parquet`**: Non-standard filename (`labels.parquet` instead of `outcomes.parquet`). Missing 17 columns, keyed by `run_id` instead of `instance_id`, lacks `test_file` and boolean split flags, and carries Pandas artifact `__index_level_0__`.
3. **`release/v0.1/bindings.parquet` & `release/v0.1/changesets.parquet`**: Shipped as un-declared standalone release tables rather than merged into `outcomes.parquet` and `instances.parquet`.

---

## 4. Decision Records Assigned (Appended to `docs/DECISIONS.md`)

- **D-39**: Java test identifier convention
  ```markdown
  ### D-39: Java test identifier convention
  **Context**: Disambiguating Java test identifiers across Surefire, Maven, and Gradle outputs when package prefixes are omitted in console lines.
  **Decision**: (Architect ruling, verbatim):
  "The canonical Java test_id is the fully-qualified class name, plus '::', plus the method name. The parser recovers the package from, in order: the surefire report header, the 'Running <FQCN>' line, any 'at' stack frame. If all three fail it emits the simple class name and sets fqcn_incomplete=True. It never infers or guesses a package."
  ```
- **D-40**: Language-ordered sweep
  ```markdown
  ### D-40: Language-ordered sweep
  **Context**: `data/frame/frame_v1.csv` is block-ordered (all Java repos followed by all Python repos). Under sequential frame execution, Python repos were never reached while logs aged against the 90-day retention clock.
  **Decision**: The harvester sweeps by language via `--lang` rather than in frame CSV order, because block-ordered CSV meant Python repos were never reached. Python log expiry at 90 days is irreversible, so Python is swept first.
  ```
- **D-41**: Artifact retention cadence
  ```markdown
  ### D-41: Artifact retention cadence
  **Context**: Managing disk footprint, reproducible builds, and transfer requirements across local data tiers.
  **Decision**: Explicit retention policy across data directories:
  - `data/raw/` (4.6 GB): Irreplaceable. Retained permanently. Cannot be regenerated because GitHub Actions job logs expire at 90 days.
  - `data/state/` (`cursor.db`, 131 MB): Irreplaceable cursor state required for `--as-of` reproduction. Retained permanently.
  - `data/interim/` (~31 MB): Regenerable from `data/raw/` via pipeline scripts, but retained to avoid expensive re-parse runs.
  - `data/clones/` (1.7 GB): Ephemeral blobless git clones. Regenerable on demand via `git clone --filter=blob:none`.
  - `release/`: Staged/published release distribution artifacts (v0.1, etc.). Retained permanently for benchmark distribution.
  ```
- **Confirmation**: D-21 preserved as RESERVED; zero existing records modified or renumbered.

---

## 5. Root Directory Classification Table

| Untracked Path | Classification | Produced Artifact / Description |
| :--- | :--- | :--- |
| `package_release.py` | **LOAD-BEARING** | Built `release/v0.1/` parquets (`instances.parquet`, `labels.parquet`, `bindings.parquet`, `changesets.parquet`). Must be promoted to `analysis/` and wired to `make tables` by CLI-1. |
| `patch_holdout_eval.py` | **PATCH-SCRIPT** | One-off patch script that updated `analysis/holdout_eval.py` to parse explicit `Expected Class:` headers. |
| `phase3.py` | **LOAD-BEARING** | Exploratory probe script measuring targeted base resolution yield over GitHub API for Phase 010-A. |
| `tmp_add.py` | **PATCH-SCRIPT** | One-off patch script injecting `Expected Class` headers into `tests/fixtures/logs/EXPECTED.md` and `tests/fixtures/holdout/EXPECTED.md`. |
| `tmp_amend.py` | **PATCH-SCRIPT** | One-off patch script appending D-27 amendment blocks to `tests/fixtures/holdout_v3/EXPECTED.md`. |
| `tmp_eval.py` | **THROWAWAY** | 10-line runner script invoking `evaluate_holdout()` on `holdout_v3`. |
| `holdout_v3_score.txt` | **LOAD-BEARING** | First raw scorecard output for holdout_v3 (83.87% precision / 55.32% recall). |
| `holdout_v3_score2.txt` | **LOAD-BEARING** | Second raw scorecard output for holdout_v3 post-amendments (95.74% precision / 97.83% recall). |
| `holdout_v3_score_corrected.txt` | **LOAD-BEARING** | Corrected raw scorecard output verifying D-32 parameterisation and fixture 4/20/23 amendments. |
| `release/` | **LOAD-BEARING** | Directory holding the v0.1 released benchmark parquet distribution. |

---

## 6. Sampling Confirmation

- **CONFIRMED**: Zero sampling was executed in this round.
- `docs/phase/013B-holdout-v5-protocol.md` was created with deterministic seed `20261111` and the clean-log test summary verification guard.
- Sampling remains deferred until CLI-1 lands parser fixes.
