# Phase 014-B Final Report: Schema Conformance Ruling & Withdrawal of release/v0.1

**Spec**: [CLI-2] — PHASE SPEC 014-B: Schema conformance ruling. Withdraw release/v0.1.  
**Date**: 2026-08-31  
**Status**: COMPLETE  
**Governing Authority**: `docs/SCHEMAS.md` (FROZEN, Rank 1). Rank-1 authority upheld; SCHEMAS.md was NOT edited.

---

## 1. Schema Conformance per In-Scope Table & Category Counts

### 1.1 `instances.parquet` Conformance Table
- **Declared Columns**: 34 | **Matching Columns**: 14 | **Divergent Columns**: 20 declared + 5 extra on disk

| column | declared | actual | category | resolution |
| :--- | :--- | :--- | :--- | :--- |
| `base_run_id` | `int64` | `int64` (100% null) | DEFECT | Join populated `base_run_id` from `data/interim/base_resolution.parquet`. File to change: `analysis/corpus_instances.py` |
| `base_run_distance` | `int32` | *(None)* | DEFECT | Join `base_run_distance` from `data/interim/base_resolution.parquet` cast to `int32`. File to change: `analysis/corpus_instances.py` |
| `run_started_at` | `timestamp` | `string` | DEFECT | Parse ISO-8601 string to PyArrow timestamp (`timestamp[us, tz=UTC]`). File to change: `analysis/corpus_instances.py` |
| `changed_files` | `list<struct<...>>` | *(None)* | NOT MEASURED | Line-level hunk ranges not parsed from patch text. Verbatim datasheet limitation: *"Hunk-level line ranges were not parsed from git patches into the instances table."* |
| `changed_symbols` | `list<string>` | *(None)* | NOT MEASURED | Tree-sitter symbol AST diffing was not executed. Verbatim datasheet limitation: *"Function- and class-level changed symbols were not extracted via tree-sitter diffing."* |
| `n_files_changed` | `int32` | *(None)* | DEFECT | Aggregate file count from `changesets.parquet` (`count(filename)` per `head_sha`). File to change: `analysis/corpus_instances.py` |
| `n_lines_changed` | `int32` | *(None)* | DEFECT | Aggregate lines changed from `changesets.parquet` (`sum(additions + deletions)` per `head_sha`). File to change: `analysis/corpus_instances.py` |
| `touches_test_file` | `bool` | *(None)* | DEFECT | Aggregate boolean `any(touches_test_file)` from `changesets.parquet` per `head_sha`. File to change: `analysis/corpus_instances.py` |
| `touches_build_config` | `bool` | *(None)* | DEFECT | Aggregate boolean `any(touches_build_config)` from `changesets.parquet` per `head_sha`. File to change: `analysis/corpus_instances.py` |
| `touches_ci_config` | `bool` | *(None)* | DEFECT | Aggregate boolean `any(touches_ci_config)` from `changesets.parquet` per `head_sha`. File to change: `analysis/corpus_instances.py` |
| `is_dependency_bump` | `bool` | *(None)* | NOT MEASURED | Automated dependency bump classifier was not evaluated. Verbatim datasheet limitation: *"Automated dependency bump classification was not evaluated."* |
| `is_docs_only` | `bool` | *(None)* | DEFECT | Aggregate boolean `all(is_docs_only)` from `changesets.parquet` per `head_sha`. File to change: `analysis/corpus_instances.py` |
| `is_formatting_only` | `bool` | *(None)* | NOT MEASURED | Formatting-only classifier was not evaluated. Verbatim datasheet limitation: *"Formatting-only change classification was not evaluated."* |
| `frontier_truncated` | `bool` | *(None)* | NOT MEASURED | Explosion guard flag proposed in 012-A; not yet populated in parquet. Verbatim datasheet limitation: *"Frontier truncation explosion guard flag was not populated in parquet."* |
| `is_default_branch` | `bool` | *(None)* | NOT MEASURED | Default branch status was not resolved against repo metadata. Verbatim datasheet limitation: *"Survivorship default branch status was not resolved from repo metadata."* |
| `graph_sha` | `string` | *(None)* | NOT MEASURED | Phase 2 graph layer cut per D-05 / HANDOFF §2. Verbatim datasheet limitation: *"Graph SHA was not computed due to graph layer cut."* |
| `parse_failure_rate` | `float32` | *(None)* | NOT MEASURED | Phase 2 graph layer cut per D-05 / HANDOFF §2. Goes in datasheet limitations verbatim: *"Parse failure rate at graph build time was not computed due to graph layer cut."* |
| `frame_version` | `string` | *(None)* | DEFECT | Populate constant string `'v1'` across all instances. File to change: `analysis/corpus_instances.py` |
| `actual_changed_files` | `list<string>` | *(None)* | DEFECT | Group row-level filenames from `changesets.parquet` into `list<string>` per `head_sha`. File to change: `analysis/corpus_instances.py` |
| `repo_full` *(extra on disk)* | *(None)* | `string` | RENAMED | Redundant duplicate of `repo`; mapping: `repo = repo_full`. Omit extra column. |
| `base_ref` *(extra on disk)* | *(None)* | `string` | DEFECT | Undeclared extra column on disk. File to change: `analysis/corpus_instances.py` (omit). |
| `created_at` *(extra on disk)* | *(None)* | `string` | DEFECT | Undeclared extra column on disk. File to change: `analysis/corpus_instances.py` (omit). |
| `job_ids` *(extra on disk)* | *(None)* | `list<int64>` | DEFECT | Undeclared extra column on disk. File to change: `analysis/corpus_instances.py` (omit). |
| `job_conclusions` *(extra on disk)* | *(None)* | `list<string>` | DEFECT | Undeclared extra column on disk. File to change: `analysis/corpus_instances.py` (omit). |

- **Category Counts for `instances.parquet`**: **DEFECT**: 14, **NOT MEASURED**: 8, **RENAMED**: 1, **RESTRUCTURED**: 0

---

### 1.2 `outcomes.parquet` Conformance Table
- **Declared Columns**: 18 | **Matching Columns**: 1 | **Divergent Columns**: 17 declared + 3 extra on disk

| column | declared | actual | category | resolution |
| :--- | :--- | :--- | :--- | :--- |
| `instance_id` | `string` | *(None)* | DEFECT | Replaced on disk with `run_id`. Join `instance_id` from `instances_raw.parquet` via `run_id`. File to change: `src/label/fault_revealing.py` |
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
| `run_id` *(extra on disk)* | *(None)* | `int64` | RESTRUCTURED | Foreign key used instead of `instance_id`. Mapping: join `instance_id` on `run_id` and omit raw `run_id`. |
| `split` *(extra on disk)* | *(None)* | `large_string` | RESTRUCTURED | String partition enum replacing boolean flags. Mapping: derive `split_strict` and `split_permissive` booleans. |

- **Category Counts for `outcomes.parquet`**: **DEFECT**: 11, **NOT MEASURED**: 5, **RENAMED**: 0, **RESTRUCTURED**: 4

---

### 1.3 `cochange.parquet` Conformance Table
- **Total Declared Columns**: 8 | **Matching Columns**: 4 | **Divergent Columns**: 4 declared + 8 extra on disk

| column | declared | actual | category | resolution |
| :--- | :--- | :--- | :--- | :--- |
| `repo` | `string` | *(None)* | RENAMED | Stored as `repo_full` on disk. Mapping: `repo = repo_full`. |
| `window_end` | `timestamp`/`string` | *(None)* | RENAMED | Stored as `as_of` on disk. Mapping: `window_end = as_of`. |
| `confidence` | `float64` | *(None)* | RESTRUCTURED | Stored as directional pair `conf_a_to_b` and `conf_b_to_a`. Mapping: `confidence = conf_a_to_b`. |
| `n_cochanges` | `int64` | *(None)* | RENAMED | Stored as `support` on disk. Mapping: `n_cochanges = support`. |
| `repo_full` *(extra on disk)* | *(None)* | `string` | RENAMED | Maps to declared `repo`. Mapping: `repo = repo_full`. |
| `as_of` *(extra on disk)* | *(None)* | `string` | RENAMED | Maps to declared `window_end`. Mapping: `window_end = as_of`. |
| `conf_a_to_b` *(extra on disk)* | *(None)* | `double` | RESTRUCTURED | Maps to declared `confidence`. Mapping: `confidence = conf_a_to_b`. |
| `conf_b_to_a` *(extra on disk)* | *(None)* | `double` | RESTRUCTURED | Directional reverse confidence. Omit or preserve under structured view. |
| `n_commits_a` *(extra on disk)* | *(None)* | `int64` | DEFECT | Undeclared extra column on disk. File to change: `analysis/cochange_mine.py` (omit). |
| `n_commits_b` *(extra on disk)* | *(None)* | `int64` | DEFECT | Undeclared extra column on disk. File to change: `analysis/cochange_mine.py` (omit). |
| `n_commits_total` *(extra on disk)* | *(None)* | `int64` | DEFECT | Undeclared extra column on disk. File to change: `analysis/cochange_mine.py` (omit). |
| `window_days` *(extra on disk)* | *(None)* | `int32` | DEFECT | Undeclared extra column on disk. File to change: `analysis/cochange_mine.py` (omit). |

- **Category Counts for `cochange.parquet`**: **DEFECT**: 4, **NOT MEASURED**: 0, **RENAMED**: 5, **RESTRUCTURED**: 3

---

### 1.4 CUT Tables (Not Defects)
Per Architect ruling, 61 columns belong to tables cut from this submission:
- `graph_nodes.parquet` (26 columns): CUT per D-05 / ROADMAP §10 / HANDOFF §2. Cut, never generated, not a defect.
- `graph_edges.parquet` (8 columns): CUT per D-05 / ROADMAP §10 / HANDOFF §2. Cut, never generated, not a defect.
- `gold.parquet` (9 columns): CUT per D-07 / ROADMAP §35 (T1.5) / HANDOFF §2. Cut, never generated, not a defect.
- `identity_map.parquet` (8 columns): CUT per D-05 / ROADMAP §10 / HANDOFF §2. Cut, never generated, not a defect.
- `graph_index.parquet` (10 columns): CUT per D-05 / ROADMAP §10 / HANDOFF §2. Cut, never generated, not a defect.

---

## 2. The Missing Negatives Finding

### 2.1 Verification Query & Output
An exhaustive audit across all interim and release parquets confirmed that **zero negative examples (`label = 0` or `is_fault_revealing = False`) exist anywhere on disk**:

```python
# Executed verification query over data/ and release/:
# Result: parsed_outcomes.parquet: 19,441 'fail', 1,094 'error' (0 non-fails)
# Result: outcomes.parquet (8,980 rows): Contains negative test instances: False
# Result: base_outcomes.parquet (2,990 rows): Contains negative test instances: False
# Result: release/v0.1/labels.parquet (8,980 rows): Contains negative test instances: False
```

### 2.2 Finding & Significance
- **Positives Only**: The released dataset contains exclusively positive failure observations (`status in ('fail', 'error')`).
- **Unmeasured Class Imbalance**: `docs/ROADMAP.md` §9.3 step 6 requires emitting one row per `(instance, candidate test)` pair where candidates are the full test set observed for that repo in a trailing window. `ROADMAP.md` §9.3 item 4 explicitly expects extreme class imbalance (1 positive per 200–2,000 candidate tests, or ~0.05%–0.5% positive rate). This class imbalance has **never been measured or reported**.
- **Action**: In accordance with the phase instructions, no negatives were generated. Recorded as a primary finding in `docs/phase/014B-missing-negatives.md`.

---

## 3. List of Reasons for Withdrawal of `release/v0.1`

Documented in `release/v0.1/WITHDRAWN.md`:
1. **`instances.parquet` Defect**: `base_run_id` is 100% null across all 165,349 rows, preventing linkage to base workflow executions. *(Discovered in `docs/phase/013B-schema-divergence.md`)*
2. **`instances.parquet` Defect**: `base_run_distance` is completely absent from the table. *(Discovered in `docs/phase/013B-schema-divergence.md`)*
3. **`labels.parquet` Defect**: Keyed by raw integer `run_id` instead of canonical `instance_id` join key (`sha256(repo|head_sha|run_id)`). *(Discovered in `docs/phase/013B-schema-divergence.md`)*
4. **`labels.parquet` Defect**: Serialized with a leaked Pandas default index artifact (`__index_level_0__`). *(Discovered in `docs/phase/013B-schema-divergence.md`)*
5. **Missing Negatives**: The release ships positives only; candidate negative test sets were never constructed, leaving class imbalance unmeasured. *(Discovered in `docs/phase/014B-missing-negatives.md`)*
6. **Upstream Resolver Bug**: CLI-1 discovered a base resolution resolver bug that may invalidate the 62.72% `no_base` rate upon which the release rests. *(Discovered in CLI-1 Phase 014-A diagnosis)*
7. **Undeclared Satellite Packaging**: Shipped `bindings.parquet` and `changesets.parquet` as separate satellite files rather than projecting attributes into canonical tables per `docs/SCHEMAS.md`. *(Discovered in `docs/phase/013B-schema-divergence.md`)*

---

## 4. Zenodo DOI & External Publication Confirmation

- **Zenodo DOI**: **NO Zenodo DOI was minted or reserved.**
- **External Distribution**: **NO dataset or artifact was published to HuggingFace, Zenodo, GitHub Releases, or any external repository.**
- **Git Tags**: Verified: only `frame_v1` exists in git history. No release tags (`v0.1` or `v0.1-dataset`) exist.
- **Preservation**: All files in `release/v0.1/` remain preserved on disk (withdrawn, not erased).

---

## 5. Decision Record Appended

- **Assigned Decision Number**: **D-42**
- **Appended to**: `docs/DECISIONS.md`
- **Verbatim Text**:
```markdown
### D-42: Schema conformance
**Context**: Reconciling on-disk Parquet datasets and release artifacts with frozen `docs/SCHEMAS.md`.
**Decision**: `SCHEMAS.md` is frozen and describes the full project scope including tables later cut. A column absent from disk is one of: CUT (its table is out of scope), DEFECT (fixable), NOT MEASURED (goes in datasheet limitations verbatim), RENAMED, or RESTRUCTURED. `SCHEMAS.md` is never edited to match what was built. No release ships with an unresolved DEFECT.
```
