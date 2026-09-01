# BlastRadius — Schema Conformance Document

**Governing Authority**: `docs/SCHEMAS.md` (FROZEN, Rank 1).  
**Architect Ruling (Phases 014-B & 015-B)**: `docs/SCHEMAS.md` describes the full project scope including tables later cut. It is frozen and will NOT be edited to match what was built. An extra column on disk that carries data the pipeline needs is NOT a defect; it means `SCHEMAS.md` was written before the pipeline existed. Every column evaluated against disk falls into one of six categories:
- **MATCH**: Declared in `SCHEMAS.md`, present on disk with identical semantics and matching type.
- **CUT**: The entire table was cut from scope per an architectural decision. (61 columns across 5 cut tables).
- **DEFECT**: Declared in `SCHEMAS.md`, data exists or is computable, but the emitted schema/values are wrong, null, or fixable. Names the file that must change.
- **NOT MEASURED**: Declared in `SCHEMAS.md`, but field was never computed or evaluated in the pipeline; goes in the datasheet limitations verbatim.
- **RENAMED**: Identical data exists under a different column name; provides the explicit mapping.
- **RESTRUCTURED**: Same information represented in a different shape; provides the structural mapping.
- **UNDECLARED**: Present on disk, absent from `SCHEMAS.md`, retained because the pipeline or a decision record requires it. Documented, never deleted.

---

## 1. Table Scope & Status Summary

| Table | Status | Governing Decision / Reference | Description |
| :--- | :---: | :--- | :--- |
| `instances.parquet` | **IN SCOPE** | ROADMAP §31 / SCHEMAS.md | Core instance dataset (workflow run & PR changesets) |
| `outcomes.parquet` | **IN SCOPE** | ROADMAP §31 / SCHEMAS.md | Core test execution labels and fault-revealing outcomes |
| `cochange.parquet` | **IN SCOPE** | ROADMAP §31 / SCHEMAS.md / D-33 | Evolutionary coupling comparison arm for RQ1 |
| `candidates.parquet` | **ADDITION** | D-43 / PHASE 015-B | Candidate test universe per repo and trailing window for deriving negatives |
| `graph_nodes.parquet` | **CUT** | D-05 / ROADMAP §10 / HANDOFF §2 | Cut, never generated, not a defect. |
| `graph_edges.parquet` | **CUT** | D-05 / ROADMAP §10 / HANDOFF §2 | Cut, never generated, not a defect. |
| `gold.parquet` | **CUT** | D-07 / ROADMAP §35 (T1.5) / HANDOFF §2 | Cut, never generated, not a defect. |
| `identity_map.parquet` | **CUT** | D-05 / ROADMAP §10 / HANDOFF §2 | Cut, never generated, not a defect. |
| `graph_index.parquet` | **CUT** | D-05 / ROADMAP §10 / HANDOFF §2 | Cut, never generated, not a defect. |

---

## 2. In-Scope Table Conformance

### 2.1 Table: `instances.parquet`
- **Total Declared Columns**: 34
- **Extra Columns on Disk**: 5 (`repo_full`, `base_ref`, `created_at`, `job_ids`, `job_conclusions`)
- **Total Evaluated Columns**: 39
- **Matching Columns on Disk**: 15 (`instance_id`, `repo`, `language`, `pr_number`, `head_sha`, `base_sha`, `run_id`, `workflow_id`, `workflow_name`, `run_conclusion`, `author_login`, `n_matrix_legs`, `is_bot_pr`, `bot_name`, `event_type`)
- **Divergent Rows in Table**: 24 (19 declared divergent + 5 extra on disk)

| column | declared | actual | category | resolution |
| :--- | :--- | :--- | :--- | :--- |
| `base_run_id` | `int64` | `int64` (100% null) | DEFECT | Join populated `base_run_id` from `data/interim/base_resolution.parquet`. File to change: `analysis/corpus_instances.py` |
| `base_run_distance` | `int32` | *(None)* | DEFECT | Join `base_run_distance` from `data/interim/base_resolution.parquet` cast to `int32`. File to change: `analysis/corpus_instances.py` |
| `run_started_at` | `timestamp` | `string` | DEFECT | Parse ISO-8601 string to PyArrow timestamp (`timestamp[us, tz=UTC]`). File to change: `analysis/corpus_instances.py` |
| `changed_files` | `list<struct<...>>` | *(None)* | NOT MEASURED | Line-level hunk ranges were not parsed from git patch text. Goes in datasheet limitations verbatim: *"Hunk-level line ranges were not parsed from git patches into the instances table."* |
| `changed_symbols` | `list<string>` | *(None)* | NOT MEASURED | Tree-sitter symbol AST diffing was not executed. Goes in datasheet limitations verbatim: *"Function- and class-level changed symbols were not extracted via tree-sitter diffing."* |
| `n_files_changed` | `int32` | *(None)* | DEFECT | Aggregate file count from `changesets.parquet` (`count(filename)` per `head_sha`). File to change: `analysis/corpus_instances.py` |
| `n_lines_changed` | `int32` | *(None)* | DEFECT | Aggregate lines changed from `changesets.parquet` (`sum(additions + deletions)` per `head_sha`). File to change: `analysis/corpus_instances.py` |
| `touches_test_file` | `bool` | *(None)* | DEFECT | Aggregate boolean `any(touches_test_file)` from `changesets.parquet` per `head_sha`. File to change: `analysis/corpus_instances.py` |
| `touches_build_config` | `bool` | *(None)* | DEFECT | Aggregate boolean `any(touches_build_config)` from `changesets.parquet` per `head_sha`. File to change: `analysis/corpus_instances.py` |
| `touches_ci_config` | `bool` | *(None)* | DEFECT | Aggregate boolean `any(touches_ci_config)` from `changesets.parquet` per `head_sha`. File to change: `analysis/corpus_instances.py` |
| `is_dependency_bump` | `bool` | *(None)* | NOT MEASURED | Automated dependency bump classifier was not evaluated. Goes in datasheet limitations verbatim: *"Automated dependency bump classification was not evaluated."* |
| `is_docs_only` | `bool` | *(None)* | DEFECT | Aggregate boolean `all(is_docs_only)` from `changesets.parquet` per `head_sha`. File to change: `analysis/corpus_instances.py` |
| `is_formatting_only` | `bool` | *(None)* | NOT MEASURED | Formatting-only classifier was not evaluated. Goes in datasheet limitations verbatim: *"Formatting-only change classification was not evaluated."* |
| `frontier_truncated` | `bool` | *(None)* | NOT MEASURED | Explosion guard flag proposed in 012-A; not yet populated in parquet. Goes in datasheet limitations verbatim: *"Frontier truncation explosion guard flag was not populated in parquet."* |
| `is_default_branch` | `bool` | *(None)* | NOT MEASURED | Default branch status was not resolved against repo metadata. Goes in datasheet limitations verbatim: *"Survivorship default branch status was not resolved from repo metadata."* |
| `graph_sha` | `string` | *(None)* | NOT MEASURED | Phase 2 graph layer cut per D-05 / HANDOFF §2. Goes in datasheet limitations verbatim: *"Graph SHA was not computed due to graph layer cut."* |
| `parse_failure_rate` | `float32` | *(None)* | NOT MEASURED | Phase 2 graph layer cut per D-05 / HANDOFF §2. Goes in datasheet limitations verbatim: *"Parse failure rate at graph build time was not computed due to graph layer cut."* |
| `frame_version` | `string` | *(None)* | DEFECT | Populate constant string `'v1'` across all instances. File to change: `analysis/corpus_instances.py` |
| `actual_changed_files` | `list<string>` | *(None)* | DEFECT | Group row-level filenames from `changesets.parquet` into `list<string>` per `head_sha`. File to change: `analysis/corpus_instances.py` |
| `repo_full` *(extra on disk)* | *(None)* | `string` | RENAMED | Redundant duplicate of `repo`; mapping: `repo = repo_full`. Omit extra column. |
| `base_ref` *(extra on disk)* | *(None)* | `string` | UNDECLARED | Required by base resolution; it is in the query CLI-1 runs today. Retain on disk. |
| `created_at` *(extra on disk)* | *(None)* | `string` | UNDECLARED | Run provenance. Retain on disk. |
| `job_ids` *(extra on disk)* | *(None)* | `list<int64>` | UNDECLARED | Matrix-leg evidence, required to verify D-12. Retain on disk. |
| `job_conclusions` *(extra on disk)* | *(None)* | `list<string>` | UNDECLARED | Matrix-leg evidence, required to verify D-12. Retain on disk. |

**`instances.parquet` Category Counts**:
- **MATCH**: 15
- **DEFECT**: 11 (10 declared missing/wrong-type + 1 declared missing constant `frame_version`)
- **NOT MEASURED**: 8
- **RENAMED**: 1
- **RESTRUCTURED**: 0
- **UNDECLARED**: 4 (`base_ref`, `created_at`, `job_ids`, `job_conclusions`)
- **Reconciliation**: `MATCH (15) + DEFECT (11) + NOT MEASURED (8) + RENAMED (1) + RESTRUCTURED (0) + UNDECLARED (4) = 39 = Declared (34) + Extra (5)`

---

### 2.2 Table: `outcomes.parquet`
- **Total Declared Columns**: 18
- **Extra Columns on Disk**: 3 (`run_id`, `split`, `__index_level_0__`)
- **Total Evaluated Columns**: 21
- **Matching Columns on Disk**: 1 (`test_id`)
- **Divergent Rows in Table**: 20 (17 declared divergent + 3 extra on disk)

| column | declared | actual | category | resolution |
| :--- | :--- | :--- | :--- | :--- |
| `instance_id` | `string` | *(None)* | RESTRUCTURED | Stored on disk as foreign key `run_id`. `instance_id` is deterministically derivable via `sha256(repo|head_sha|run_id)`. |
| `test_file` | `string` | *(None)* | DEFECT | Join `resolved_path` from `data/interim/binding.parquet` via `(repo, test_id)`. File to change: `src/label/fault_revealing.py` |
| `status_head` | `string` | *(None)* | DEFECT | Carry `status` from `data/interim/parsed_outcomes.parquet` (`fail` / `error`). File to change: `src/label/fault_revealing.py` |
| `status_base` | `string` | *(None)* | DEFECT | Populate base status from `data/interim/base_outcomes.parquet` or infer `'pass'` on `exact_green`. File to change: `src/label/fault_revealing.py` |
| `is_fault_revealing` | `bool` | *(None)* | DEFECT | Explicit boolean flag (`True` for fault-revealing positives, `False` for negatives). File to change: `src/label/fault_revealing.py` |
| `flakiness_score` | `float32` | *(None)* | NOT MEASURED | Trailing 30-day flip rate was not computed. Goes in datasheet limitations verbatim: *"Trailing 30-day flakiness score was not computed."* |
| `same_sha_flip` | `bool` | *(None)* | NOT MEASURED | Multi-run same-SHA flip rate was not evaluated. Goes in datasheet limitations verbatim: *"Same-SHA multi-run flip rate was not evaluated."* |
| `label_source` | `string` | *(None)* | DEFECT | Populate label source (`'log'`) from `data/interim/parsed_outcomes.parquet`. File to change: `src/label/fault_revealing.py` |
| `parser_confidence` | `float32` | *(None)* | DEFECT | Carry `parser_confidence` from `data/interim/parsed_outcomes.parquet`. File to change: `src/label/fault_revealing.py` |
| `duration_s` | `float32` | *(None)* | DEFECT | Carry `duration_s` from `data/interim/parsed_outcomes.parquet`. File to change: `src/label/fault_revealing.py` |
| `failure_message_hash` | `string` | *(None)* | DEFECT | Compute `sha256(failure_message)` from `data/interim/parsed_outcomes.parquet`. File to change: `src/label/fault_revealing.py` |
| `split_strict` | `bool` | *(None)* | RESTRUCTURED | Stored on disk as string enum `split == 'strict'`. Mapping: `split_strict = (split == 'strict')`. |
| `split_permissive` | `bool` | *(None)* | RESTRUCTURED | Stored on disk as string enum `split in ('strict', 'relaxed')`. Mapping: `split_permissive = (split in ['strict', 'relaxed'])`. |
| `new_test` | `bool` | *(None)* | NOT MEASURED | Test appearance delta between head and base was not computed. Goes in datasheet limitations verbatim: *"New-test emergence flag was not computed."* |
| `suspect_unrelated` | `bool` | *(None)* | NOT MEASURED | DeFlaker heuristic was not implemented. Goes in datasheet limitations verbatim: *"DeFlaker suspect-unrelated heuristic was not evaluated."* |
| `excluded_own_file` | `bool` | *(None)* | NOT MEASURED | Leakage guard was not written to parquet. Goes in datasheet limitations verbatim: *"Leakage guard excluded_own_file flag was not evaluated into the table."* |
| `binding_strategy` | `string` | *(None)* | DEFECT | Join `status` from `data/interim/binding.parquet` (`exact`, `ambiguous`, `not_found`). File to change: `src/label/fault_revealing.py` |
| `__index_level_0__` *(extra on disk)* | *(None)* | `int64` | DEFECT | Pandas default index leaked into Parquet. File to change: `src/label/fault_revealing.py` (write with `index=False`). |
| `run_id` *(extra on disk)* | *(None)* | `int64` | RESTRUCTURED | Foreign key used instead of `instance_id`. Mapping: `instance_id = sha256(repo|head_sha|run_id)`. |
| `split` *(extra on disk)* | *(None)* | `large_string` | RESTRUCTURED | String partition enum replacing boolean flags. Mapping: derive `split_strict` and `split_permissive` booleans. |

**`outcomes.parquet` Category Counts**:
- **MATCH**: 1 (`test_id`)
- **DEFECT**: 10 (9 declared missing/joinable + 1 pandas index artifact `__index_level_0__`)
- **NOT MEASURED**: 5
- **RENAMED**: 0
- **RESTRUCTURED**: 5 (3 declared: `instance_id`, `split_strict`, `split_permissive` + 2 extra: `run_id`, `split`)
- **UNDECLARED**: 0
- **Reconciliation**: `MATCH (1) + DEFECT (10) + NOT MEASURED (5) + RENAMED (0) + RESTRUCTURED (5) + UNDECLARED (0) = 21 = Declared (18) + Extra (3)`

---

### 2.3 Table: `cochange.parquet`
- **Total Declared Columns**: 8
- **Extra Columns on Disk**: 8 (`repo_full`, `as_of`, `conf_a_to_b`, `conf_b_to_a`, `n_commits_a`, `n_commits_b`, `n_commits_total`, `window_days`)
- **Total Evaluated Columns**: 16
- **Matching Columns on Disk**: 4 (`file_a`, `file_b`, `support`, `lift`)
- **Divergent Rows in Table**: 12 (4 declared divergent + 8 extra on disk)

| column | declared | actual | category | resolution |
| :--- | :--- | :--- | :--- | :--- |
| `repo` | `string` | *(None)* | RENAMED | Stored as `repo_full` on disk. Mapping: `repo = repo_full`. |
| `window_end` | `timestamp`/`string` | *(None)* | RENAMED | Stored as `as_of` on disk. Mapping: `window_end = as_of`. |
| `confidence` | `float64` | *(None)* | RESTRUCTURED | Stored as directional pair `conf_a_to_b` and `conf_b_to_a`. Mapping: `confidence = conf_a_to_b`. |
| `n_cochanges` | `int64` | *(None)* | RENAMED | Stored as `support` on disk. Mapping: `n_cochanges = support`. |
| `repo_full` *(extra on disk)* | *(None)* | `string` | RENAMED | Maps to declared `repo`. Mapping: `repo = repo_full`. |
| `as_of` *(extra on disk)* | *(None)* | `string` | RENAMED | Maps to declared `window_end`. Mapping: `window_end = as_of`. |
| `conf_a_to_b` *(extra on disk)* | *(None)* | `double` | RESTRUCTURED | Maps to declared `confidence`. Mapping: `confidence = conf_a_to_b`. |
| `conf_b_to_a` *(extra on disk)* | *(None)* | `double` | UNDECLARED | Directional pair; retain both directions. |
| `n_commits_a` *(extra on disk)* | *(None)* | `int64` | UNDECLARED | The provenance of support and lift; without them the co-change arm of RQ1 is uncheckable. Retain on disk. |
| `n_commits_b` *(extra on disk)* | *(None)* | `int64` | UNDECLARED | The provenance of support and lift; without them the co-change arm of RQ1 is uncheckable. Retain on disk. |
| `n_commits_total` *(extra on disk)* | *(None)* | `int64` | UNDECLARED | The provenance of support and lift; without them the co-change arm of RQ1 is uncheckable. Retain on disk. |
| `window_days` *(extra on disk)* | *(None)* | `int32` | UNDECLARED | The provenance of support and lift; without them the co-change arm of RQ1 is uncheckable. Retain on disk. |

**`cochange.parquet` Category Counts**:
- **MATCH**: 4 (`file_a`, `file_b`, `support`, `lift`)
- **DEFECT**: 0
- **NOT MEASURED**: 0
- **RENAMED**: 5 (3 declared: `repo`, `window_end`, `n_cochanges` + 2 extra: `repo_full`, `as_of`)
- **RESTRUCTURED**: 2 (1 declared: `confidence` + 1 extra: `conf_a_to_b`)
- **UNDECLARED**: 5 (`conf_b_to_a`, `n_commits_a`, `n_commits_b`, `n_commits_total`, `window_days`)
- **Reconciliation**: `MATCH (4) + DEFECT (0) + NOT MEASURED (0) + RENAMED (5) + RESTRUCTURED (2) + UNDECLARED (5) = 16 = Declared (8) + Extra (8)`

---

## 3. Conformance Summary Across In-Scope Tables

| Table | Declared Columns | Extra on Disk | Total Evaluated | MATCH | DEFECT | NOT MEASURED | RENAMED | RESTRUCTURED | UNDECLARED | Total Discrepancies (Table Rows) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `instances.parquet` | 34 | 5 | 39 | 15 | 11 | 8 | 1 | 0 | 4 | 24 |
| `outcomes.parquet` | 18 | 3 | 21 | 1 | 10 | 5 | 0 | 5 | 0 | 20 |
| `cochange.parquet` | 8 | 8 | 16 | 4 | 0 | 0 | 5 | 2 | 5 | 12 |
| **TOTAL** | **60** | **16** | **76** | **20** | **21** | **13** | **6** | **7** | **9** | **56** |

*(Note: Every column evaluated on disk satisfies `MATCH + DEFECT + NOT MEASURED + RENAMED + RESTRUCTURED + UNDECLARED = Declared + Extra`. Total discrepancies equals the sum of rows across the three tables: 24 + 20 + 12 = 56. The 5 cut tables account for 61 columns, all categorized as CUT / Not a defect).*

---

## 4. Benchmark Addition: `candidates.parquet` Schema Specification

**Authority**: Architect Ruling (Phase 015-B) & Decision Record D-43. Recorded here as an ADDITION, not an edit to frozen `SCHEMAS.md`.

### 4.1 Specification
- **Grain**: One row per `(repo, window_end, test_id)` observation.
- **Window Definition**: Trailing observation window (e.g. 30-day or 90-day window preceding an instance's `run_started_at`), bounding the universe of active candidate tests for that repository at that point in time.

| Column | Type | Nullable | Description |
| :--- | :--- | :---: | :--- |
| `repo` | `string` | No | Repository slug (`"owner/name"`). |
| `test_id` | `string` | No | Canonical test identifier (`{package}.{Class}#{method}` or `{path}::{Class}::{func}`). |
| `test_file` | `string` | Yes | Repository-relative path to the test file if bound (`resolve_test_file`). |
| `window_start` | `timestamp[us, tz=UTC]` | No | Start timestamp of the trailing observation window. |
| `window_end` | `timestamp[us, tz=UTC]` | No | End timestamp of the trailing observation window (as-of instance cutoff). |
| `first_seen_at` | `timestamp[us, tz=UTC]` | No | Earliest execution timestamp of the test within the observation window. |
| `last_seen_at` | `timestamp[us, tz=UTC]` | No | Most recent execution timestamp of the test within the observation window. |
| `execution_count` | `int32` | No | Number of workflow runs in the trailing window in which the test was observed. |
| `harness` | `string` | No | Test harness / framework (`maven`, `gradle`, `pytest`). |
