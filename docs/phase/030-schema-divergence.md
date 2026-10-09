# 030 — SCHEMAS.md vs release/v0.1 divergence (read-only)

**Date**: 2026-10-09. **Mode**: read-only, `BR_OFFLINE=1`, no network, nothing rebuilt, no table/script/doc edited. Produced to unblock T1.6a and scope v0.2.
**Authority**: `docs/SCHEMAS.md` (frozen, rank 1). **Compared against**: `release/v0.1/{instances,outcomes,cochange,failure_messages}.parquet` (DuckDB `DESCRIBE`, raw output in §6).
**Source tables checked for fillability**: `data/interim/*.parquet` (types and null rates measured today).
**Unit note**: "null rate" is over the release table's rows. Prior diagnostic `013B-schema-divergence.md` (2026-08-31) is stale (cites `labels.parquet`, 8,980 outcome rows, and a `release/` that did not yet exist); this report supersedes it for counts.

## 0. Headline

| Table | Declared in SCHEMAS.md | On disk | Declared-and-absent | TYPE_MISMATCH | EXTRA on disk |
|---|---|---|---|---|---|
| instances | 34 | 22 | 17 | 1 (`run_started_at`) | 5 |
| outcomes | 18 | 4 | 17 | 0 | 3 (incl. `__index_level_0__`) |
| cochange | 8 | 12 | 4 | 0 (types undeclared) | 8 |
| failure_messages | no section (only `failure_message_hash` in outcomes) | 5 | n/a | n/a | 5 (whole table undeclared) |

**(a) Real total of divergent declared columns: 39** (17 + 1 + 17 + 4), plus 21 EXTRA on-disk columns (16 excluding the undeclared `failure_messages`). **I cannot reproduce "19".** The only scoping that reaches 19 is *instances alone, counting `base_run_id` as divergent because it is 100% null*: 17 absent + 1 type mismatch + 1 all-null = 19. I did not find where the handoff's figure was derived, so treat that reading as a guess. Whichever it is, `DATASHEET.md:279` ("19 declared columns") understates the divergence if it means all tables.

Two further divergences are not column-level:
- **Row grain.** outcomes is *long by split*: 12,766 rows = 4,384 distinct (run_id, test_id) pairs × {`all` 4,384, `strict` 4,168, `relaxed` 4,214}. SCHEMAS.md grain is one row per (instance, test) with `split_strict`/`split_permissive` booleans.
- **Population.** SCHEMAS.md says "one row per (head_sha, workflow_run)", and `is_fault_revealing`-bearing outcomes. On disk instances has all 165,349 runs (12,581 are `failure`); outcomes covers only 897 runs of failing instances, all positive-labelled (`parsed_outcomes.status` ∈ {fail, error}).

## 1. instances.parquet (165,349 rows; on-disk is byte-for-source `data/interim/instances_raw.parquet`)

Fillable sources: `changesets` (688,273 rows; 30,656 distinct (repo, pr_number, head_sha); `is_truncated` = 0 everywhere) joins to 147,985 / 165,349 runs (89.5%). The 17,364 runs left have no changeset in the interim store. `pr_number` in `changesets` is VARCHAR. `base_resolution_new` has 12,581 rows, exactly the `failure` runs.

| column | SCHEMAS.md type | on-disk type | null rate | verdict | fillable from interim store? |
|---|---|---|---|---|---|
| instance_id | string | VARCHAR | 0% | MATCH | n/a |
| repo | string | VARCHAR | 0% | MATCH | n/a |
| language | string | VARCHAR | 0% | MATCH | n/a (values `Java`/`Python`, SCHEMAS says `java \| python`; case differs) |
| pr_number | int64 | BIGINT | 0% | MATCH (type) | n/a. Note: SCHEMAS says null for push events; on disk push rows (6,155) all carry a pr_number. Semantic divergence, not type |
| head_sha | string | VARCHAR | 0% | MATCH | n/a |
| base_sha | string | VARCHAR | 0% | MATCH | n/a |
| base_run_id | int64 | BIGINT | **100%** | MATCH (type), content gap | **partial**: `base_resolution_new.base_run_id` (DOUBLE, cast to int64) non-null for 7,061 runs (4,245 exact_green, 1,858 exact, 591 ancestor, 367 branch_prior) = 4.27% of rows. The other 158,288 are not resolvable: resolution was only run on failing runs |
| base_run_distance | int32 | MISSING | n/a | MISSING_ON_DISK | **partial**: `base_resolution_new.base_run_distance` (DOUBLE) non-null for 6,025 runs (3,576 exact_green, 1,858 exact, 591 ancestor). branch_prior (367) and 669 exact_green have no distance |
| run_id | int64 | BIGINT | 0% | MATCH | n/a |
| workflow_id | int64 | BIGINT | 0% | MATCH | n/a |
| workflow_name | string | VARCHAR | 0% | MATCH | n/a |
| run_conclusion | string | VARCHAR | 0.04% | MATCH | n/a |
| run_started_at | timestamp | VARCHAR | 0% | TYPE_MISMATCH | yes: cast `instances_raw.run_started_at` ISO-8601 `Z` string. Lossless |
| changed_files | list<struct<path,status,additions,deletions,hunks>> | MISSING | n/a | MISSING_ON_DISK | **partial**: path/status/additions/deletions from `changesets.filename/status/additions/deletions` (147,985 runs). **`hunks` not fillable**: no patch text is stored in `changesets`. Struct would need `hunks` empty/null, which is a schema decision |
| changed_symbols | list<string> | MISSING | n/a | MISSING_ON_DISK | no: never computed; needs the graph layer (D-48 cut) |
| n_files_changed | int32 | MISSING | n/a | MISSING_ON_DISK | yes (89.5% of runs): count of `changesets` rows |
| n_lines_changed | int32 | MISSING | n/a | MISSING_ON_DISK | yes (89.5%): sum(additions+deletions) |
| touches_test_file | bool | MISSING | n/a | MISSING_ON_DISK | yes (89.5%): any(`changesets.touches_test_file`) |
| touches_build_config | bool | MISSING | n/a | MISSING_ON_DISK | yes (89.5%): any(`changesets.touches_build_config`) |
| touches_ci_config | bool | MISSING | n/a | MISSING_ON_DISK | yes (89.5%): any(`changesets.touches_ci_config`) |
| is_dependency_bump | bool | MISSING | n/a | MISSING_ON_DISK | no: never computed (`is_bot_pr`/`bot_name` are a proxy, not the same thing; do not substitute silently) |
| is_docs_only | bool | MISSING | n/a | MISSING_ON_DISK | yes (89.5%): all(`changesets.is_docs_only`) (check aggregation rule against `src/parse/changeset.py`) |
| is_formatting_only | bool | MISSING | n/a | MISSING_ON_DISK | no: never computed |
| author_login | string | VARCHAR | 0% | MATCH | n/a (pseudonymised in release) |
| n_matrix_legs | int32 | INTEGER | 0.02% | MATCH | n/a |
| frontier_truncated | bool | MISSING | n/a | MISSING_ON_DISK | no: graph/explosion-guard, never computed |
| is_bot_pr | bool | BOOLEAN | 0% | MATCH | n/a |
| bot_name | string | VARCHAR | 90.87% | MATCH | n/a |
| event_type | string | VARCHAR | 0% | MATCH | n/a |
| is_default_branch | bool | MISSING | n/a | MISSING_ON_DISK | no: needs each repo's default branch; `base_ref` is present but default branch is not in the interim store. May exist in `data/raw` repo metadata, which I did not open |
| graph_sha | string | MISSING | n/a | MISSING_ON_DISK | no: graph layer (D-48) |
| parse_failure_rate | float32 | MISSING | n/a | MISSING_ON_DISK | no: graph layer |
| frame_version | string | MISSING | n/a | MISSING_ON_DISK | yes, but it is a constant, not data (value must be decided by the operator) |
| actual_changed_files | list<string> | MISSING | n/a | MISSING_ON_DISK | yes (89.5%): collect `changesets.filename` |
| repo_full | n/a | VARCHAR | 0% | EXTRA_ON_DISK | n/a (duplicate of `repo`) |
| base_ref | n/a | VARCHAR | 0% | EXTRA_ON_DISK | n/a |
| created_at | n/a | VARCHAR | 0% | EXTRA_ON_DISK | n/a |
| job_ids | n/a | BIGINT[] | 0% | EXTRA_ON_DISK | n/a |
| job_conclusions | n/a | VARCHAR[] | 0% | EXTRA_ON_DISK | n/a |

Instances tally of the 17 MISSING: 7 fillable at 89.5% (`n_files_changed`, `n_lines_changed`, `touches_*` x3, `is_docs_only`, `actual_changed_files`); 2 partial (`base_run_distance`, `changed_files` without hunks); 1 constant (`frame_version`); 7 not fillable (`changed_symbols`, `is_dependency_bump`, `is_formatting_only`, `frontier_truncated`, `is_default_branch`, `graph_sha`, `parse_failure_rate`).

## 2. outcomes.parquet (12,766 rows, 4,384 distinct (run_id, test_id))

Identical to `data/interim/outcomes.parquet` (EXCEPT both ways = 0 rows). All 4,384 pairs join to `instances` (via `run_id`) and to `parsed_outcomes` (via run_id, test_id). `parsed_outcomes` is job-grain: 690 of the 4,384 pairs have >1 row (matrix legs), 4 pairs have mixed status, 1 pair has >1 parser_confidence, so any fill needs a stated aggregation rule.

| column | SCHEMAS.md type | on-disk type | null rate | verdict | fillable from interim store? |
|---|---|---|---|---|---|
| instance_id | string | MISSING | n/a | MISSING_ON_DISK | yes: `sha256(repo\|head_sha\|run_id)` via join on run_id to instances (all 4,384 join); disk carries `run_id` instead |
| test_id | string | VARCHAR | 0% | MATCH | n/a |
| test_file | string | MISSING | n/a | MISSING_ON_DISK | partial: `binding.resolved_path` joined on (instances.repo, test_id): 4,229 / 4,384 pairs (96.5%). 155 are `ambiguous` or `not_found` and stay null (schema allows null). `parsed_outcomes.test_file` is 100% null |
| status_head | string | MISSING | n/a | MISSING_ON_DISK | yes: `parsed_outcomes.status` (fail/error only, so schema values pass/skip/absent never occur). Needs aggregation for 690 multi-row pairs |
| status_base | string | MISSING | n/a | MISSING_ON_DISK | **partial / needs derivation**: `base_outcomes` has no status column and holds failing base tests only (2,990 rows, 1,695 pairs; 175 intersect the 4,384). Everything else is inferred in `src/label/fault_revealing.py` (exact_green etc.). Reproducing that inference is code, not a lookup; I did not verify it yields pass vs absent per pair |
| is_fault_revealing | bool | MISSING | n/a | MISSING_ON_DISK | yes by construction: every shipped row is a positive label (`split` rows only exist for labelled pairs). Constant `true`; no negatives are shipped, which matters for any consumer expecting both classes |
| flakiness_score | float32 | MISSING | n/a | MISSING_ON_DISK | no for the declared definition (trailing 30d flip rate). A same-SHA flip rate exists in `labelling_run.md`/`flakiness.md` but not as a per-row score |
| same_sha_flip | bool | MISSING | n/a | MISSING_ON_DISK | partial: computed in `fault_revealing.compute_labels` (line ~68-72) in memory, not persisted. Recomputable offline from interim tables |
| label_source | string | MISSING | n/a | MISSING_ON_DISK | yes: `parsed_outcomes.label_source` = `log` for all 20,451 rows |
| parser_confidence | float32 | MISSING | n/a | MISSING_ON_DISK | yes: `parsed_outcomes.parser_confidence` FLOAT, 0% null (1 pair needs a rule) |
| duration_s | float32 | MISSING | n/a | MISSING_ON_DISK | partial: `parsed_outcomes.duration_s` non-null for 2,505 / 4,384 pairs (57.1%); 81.94% null at row level |
| failure_message_hash | string | MISSING | n/a | MISSING_ON_DISK | partial: sha256 of `parsed_outcomes.failure_message` (non-null for 2,111 / 4,384 pairs, 48.2%). Hash never computed. Must match the release `failure_messages` text exactly |
| split_strict | bool | MISSING | n/a | MISSING_ON_DISK | yes: derivable from `split` (`strict`) |
| split_permissive | bool | MISSING | n/a | MISSING_ON_DISK | yes: derivable from `split` (`relaxed`; name differs from "permissive") |
| new_test | bool | MISSING | n/a | MISSING_ON_DISK | no: never computed |
| suspect_unrelated | bool | MISSING | n/a | MISSING_ON_DISK | no: never computed |
| excluded_own_file | bool | MISSING | n/a | MISSING_ON_DISK | partial: needs `test_file` (96.5%) and changed file set (89.5% of runs); never computed. This is the schema's **leakage guard**, whose CI assertion therefore cannot run on the shipped table |
| binding_strategy | string | MISSING | n/a | MISSING_ON_DISK | partial: `binding.status` ∈ {exact, ambiguous, not_found}, whose domain is **not** the schema's {tests, tests_by_convention, tests_by_layout, unbound}. A mapping is a decision, not a lookup |
| run_id | n/a | BIGINT | 0% | EXTRA_ON_DISK | n/a |
| split | n/a | VARCHAR | 0% | EXTRA_ON_DISK | n/a (values all/strict/relaxed; long grain) |
| __index_level_0__ | n/a | BIGINT | 0% | EXTRA_ON_DISK | n/a (pandas index leaked by `to_parquet`) |

## 3. cochange.parquet (175,204 rows)

SCHEMAS.md gives column names only for this table, no types, so no TYPE_MISMATCH is assessable.

| column | SCHEMAS.md type | on-disk type | null rate | verdict | fillable from interim store? |
|---|---|---|---|---|---|
| repo | (undeclared) | MISSING | n/a | MISSING_ON_DISK | yes: `repo_full` (rename; the change protocol allows additive columns only, so an alias column would be added, not a rename) |
| window_end | (undeclared) | MISSING | n/a | MISSING_ON_DISK | yes: `as_of`, a single value `2026-08-29T14:13:00Z` on all rows. See D-52: this static table is mined to the corpus pin, i.e. after many runs started, which the paper no longer uses for RQ1 |
| file_a | (undeclared) | VARCHAR | 0% | MATCH | n/a |
| file_b | (undeclared) | VARCHAR | 0% | MATCH | n/a |
| support | (undeclared) | BIGINT | 0% | MATCH | n/a |
| confidence | (undeclared) | MISSING | n/a | MISSING_ON_DISK | yes but a choice: disk has directional `conf_a_to_b` and `conf_b_to_a`; which one is `confidence` is undefined |
| lift | (undeclared) | DOUBLE | 0% | MATCH | n/a |
| n_cochanges | (undeclared) | MISSING | n/a | MISSING_ON_DISK | yes but a choice: `support` is the only co-occurrence count on disk and is already matched to `support`. Two declared columns, one stored quantity |
| repo_full, conf_a_to_b, conf_b_to_a, n_commits_a, n_commits_b, n_commits_total, window_days, as_of | n/a | VARCHAR, DOUBLE, DOUBLE, BIGINT, BIGINT, BIGINT, INTEGER, VARCHAR | 0% each | EXTRA_ON_DISK (8) | n/a |

## 4. failure_messages.parquet (3,490 rows)

SCHEMAS.md has no section; it only says (Release hygiene) "store `failure_message` in a separate file". All five columns are EXTRA by definition: `repo` VARCHAR, `run_id` BIGINT, `job_id` BIGINT, `test_id` VARCHAR, `failure_message` VARCHAR, each 0% null, all messages non-empty. Keys are job-grain (run_id, job_id, test_id); outcomes is run-grain, so the hash link needs the same aggregation rule as §2. Not fillable/needed: nothing missing.

## 5. Questions asked

**(a)** 39 divergent declared columns (§0). Not 19.

**(b) Would populating `base_run_id` / `base_run_distance` / `status` / bound test file change any count in `paper/generated/*.md`?** From the code path, **no**, provided the fill is additive and happens only in `release/`:
- `grep` shows nothing under `analysis/` or `src/` reads `release/v0.1/*` except `build_release.py` (writer), `secret_scan.py`, and `tests/test_release_pseudonym.py`. `make tables` never reads the release bundle.
- `base_resolution.md` and `attrition_funnel.md` draw `status` / `base_run_id` / `base_run_distance` from `data/interim/base_resolution_new.parquet` (`paper_numbers.py:72-90`, `attrition_funnel.py:81-88`), not from instances. `binding.md`/`binding_run.md` draw from `binding.parquet`. `labelling_run.md` reads `instances_raw` only for `run_id, head_sha, workflow_id` (`fault_revealing.py:68`).
- `status` is not an instances column in SCHEMAS.md at all (it appears only as `changed_files[].status` and in outcomes `status_head/base`); adding the base-resolution `status` to instances would be EXTRA.
- **Caveat that does bite**: `build_release.py` sources instances from `data/interim/instances_raw.parquet`. If v0.2 fills columns by *rewriting `instances_raw.parquet`*, its mtime moves past `outcomes.parquet`, and `analysis/check_freshness.py` (first step of `make tables`, `DERIVATIONS["outcomes.parquet"]` lists `instances_raw.parquet`) will refuse to run until `fault_revealing.py` is re-executed. That is a gate, not a count change, but it blocks `make tables`. Filling into a new interim file or in `build_release.py` avoids this. Other readers of `instances_raw` (`resolve_bases.py`, `fetch_base_logs.py`, `verify_exact_green.py`, `demo_*`) select by named columns; none uses an instances `base_run_id`. I did not run anything to confirm no counts move; this is by reading only.
- `corpus_stats.md` `status` is `capture_unit.status` from the cursor DB, unrelated.

**(c) Does any fill need re-harvest or network?** For the fills marked "yes"/"partial" above: **no**; every source is already in `data/interim/`. Network/re-harvest *would* be needed to go beyond: `base_run_id`/`base_run_distance` for the 152,768 non-failing runs and the 5,520 `no_base` failing runs (resolution was never run; `resolve_bases.py` calls the API), `hunks` (patch text not stored; `changesets` has no patch), changesets for the 17,364 runs without one, and `is_default_branch` unless repo metadata is already in `data/raw` (unchecked). `changed_symbols`, `graph_sha`, `parse_failure_rate`, `frontier_truncated` need the graph layer, which D-48 cut from `release/`. `new_test`, `suspect_unrelated`, `is_dependency_bump`, `is_formatting_only`, `flakiness_score` have no source and need new code (and for some, more data), not just a join.

## 6. Raw `DESCRIBE` output (release/v0.1)

```
===== instances
        column_name column_type null   key default extra
0       instance_id     VARCHAR  YES  None    None  None
1              repo     VARCHAR  YES  None    None  None
2         repo_full     VARCHAR  YES  None    None  None
3          language     VARCHAR  YES  None    None  None
4         pr_number      BIGINT  YES  None    None  None
5          head_sha     VARCHAR  YES  None    None  None
6          base_sha     VARCHAR  YES  None    None  None
7          base_ref     VARCHAR  YES  None    None  None
8       base_run_id      BIGINT  YES  None    None  None
9            run_id      BIGINT  YES  None    None  None
10      workflow_id      BIGINT  YES  None    None  None
11    workflow_name     VARCHAR  YES  None    None  None
12   run_started_at     VARCHAR  YES  None    None  None
13       created_at     VARCHAR  YES  None    None  None
14   run_conclusion     VARCHAR  YES  None    None  None
15          job_ids    BIGINT[]  YES  None    None  None
16  job_conclusions   VARCHAR[]  YES  None    None  None
17    n_matrix_legs     INTEGER  YES  None    None  None
18        is_bot_pr     BOOLEAN  YES  None    None  None
19         bot_name     VARCHAR  YES  None    None  None
20     author_login     VARCHAR  YES  None    None  None
21       event_type     VARCHAR  YES  None    None  None
===== outcomes
         column_name column_type null   key default extra
0             run_id      BIGINT  YES  None    None  None
1            test_id     VARCHAR  YES  None    None  None
2              split     VARCHAR  YES  None    None  None
3  __index_level_0__      BIGINT  YES  None    None  None
===== cochange
        column_name column_type null   key default extra
0         repo_full     VARCHAR  YES  None    None  None
1            file_a     VARCHAR  YES  None    None  None
2            file_b     VARCHAR  YES  None    None  None
3           support      BIGINT  YES  None    None  None
4       conf_a_to_b      DOUBLE  YES  None    None  None
5       conf_b_to_a      DOUBLE  YES  None    None  None
6              lift      DOUBLE  YES  None    None  None
7       n_commits_a      BIGINT  YES  None    None  None
8       n_commits_b      BIGINT  YES  None    None  None
9   n_commits_total      BIGINT  YES  None    None  None
10      window_days     INTEGER  YES  None    None  None
11            as_of     VARCHAR  YES  None    None  None
===== failure_messages
       column_name column_type null   key default extra
0             repo     VARCHAR  YES  None    None  None
1           run_id      BIGINT  YES  None    None  None
2           job_id      BIGINT  YES  None    None  None
3          test_id     VARCHAR  YES  None    None  None
4  failure_message     VARCHAR  YES  None    None  None
```
