# Session 074 — Phase 014-B: Schema Conformance Ruling & Withdrawal of release/v0.1

**Task Statement**: [CLI-2] — PHASE SPEC 014-B: Schema conformance ruling. Withdraw release/v0.1.
**Date**: 2026-08-31
**Model**: Gemini 3.7 Flash
**Status**: COMPLETE

---

## 1. Commands Run & Raw Output

### Guard Command
```
$ uname -s && pwd && uv run python --version
Linux
/home/shree/blastradius
Python 3.11.15
```

### Git Tag & Release Check
```
$ git tag -l && git log -n 5 --oneline
frame_v1
906c594 (HEAD -> main, origin/main, origin/HEAD) Add session report and handoff for Phase 011-A
7320545 Phase 011-A: Targeted base resolution with instance-weighting and overflow truncation
4d14d59 docs: Phase 011B protocol for holdout_v4
0ec48c8 Correct fixture 4 and reframe RQ1 as two axes
aea1feb Commit pending 008-B changes at green
```

### Missing Negatives Verification Query
```
$ uv run python -c "
import pyarrow.parquet as pq
import pyarrow.compute as pc

def check_file(path):
    print(f'=== Checking {path} ===')
    table = pq.read_table(path)
    print(f'Total rows: {table.num_rows}')
    print(f'Columns: {table.column_names}')
    for col in table.column_names:
        if col in ['status', 'is_fault_revealing', 'split', 'verdict', 'conclusion']:
            counts = pc.value_counts(table.column(col)).to_pylist()
            print(f'  Column \"{col}\" distribution: {counts}')
    has_negatives = False
    if 'is_fault_revealing' in table.column_names:
        f_count = pc.sum(pc.equal(table.column('is_fault_revealing'), False)).as_py()
        print(f'  Explicit False labels: {f_count}')
        if f_count > 0: has_negatives = True
    if 'status' in table.column_names:
        non_fails = pc.sum(pc.invert(pc.is_in(table.column('status'), pyarrow.array(['fail', 'error'])))).as_py()
        print(f'  Non-failing statuses: {non_fails}')
        if non_fails > 0: has_negatives = True
    print(f'  Contains negative test instances: {has_negatives}\n')

import pyarrow
for p in ['data/interim/parsed_outcomes.parquet', 'data/interim/outcomes.parquet', 'data/interim/base_outcomes.parquet', 'release/v0.1/labels.parquet']:
    check_file(p)
"
=== Checking data/interim/parsed_outcomes.parquet ===
Total rows: 20535
Columns: ['test_id', 'parser_confidence', 'run_id', 'job_id', 'repo', 'head_sha', 'test_file', 'status', 'duration_s', 'failure_message', 'label_source', 'harness', 'is_fqcn_qualified', 'params']
  Column "status" distribution: [{'values': 'fail', 'counts': 19441}, {'values': 'error', 'counts': 1094}]
  Non-failing statuses: 0
  Contains negative test instances: False

=== Checking data/interim/outcomes.parquet ===
Total rows: 8980
Columns: ['run_id', 'test_id', 'split', '__index_level_0__']
  Column "split" distribution: [{'values': 'all', 'counts': 3119}, {'values': 'relaxed', 'counts': 2949}, {'values': 'strict', 'counts': 2912}]
  Contains negative test instances: False

=== Checking data/interim/base_outcomes.parquet ===
Total rows: 2990
Columns: ['test_id', 'parser_confidence', 'run_id', 'job_id', 'repo', 'head_sha', 'test_file', 'base_run_id']
  Contains negative test instances: False

=== Checking release/v0.1/labels.parquet ===
Total rows: 8980
Columns: ['run_id', 'test_id', 'split', '__index_level_0__']
  Column "split" distribution: [{'values': 'all', 'counts': 3119}, {'values': 'relaxed', 'counts': 2949}, {'values': 'strict', 'counts': 2912}]
  Contains negative test instances: False
```

### Pytest Verification Suite
```
$ uv run pytest
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/shree/blastradius
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.14.2
collected 379 items

tests/test_artifacts.py ...........                                      [  2%]
tests/test_base_resolve.py .......                                       [  4%]
tests/test_changeset.py .                                                [  5%]
tests/test_cochange_mine.py ...                                          [  5%]
tests/test_cursor.py ...................                                 [ 10%]
tests/test_daemon.py ................................................... [ 24%]
..................................                                       [ 33%]
tests/test_dispatch.py ..............                                    [ 36%]
tests/test_fault_revealing.py .......                                    [ 38%]
tests/test_fixture_score.py ......                                       [ 40%]
tests/test_frame.py ...........                                          [ 43%]
tests/test_holdout_eval.py .......                                       [ 45%]
tests/test_holdout_integrity.py ....                                     [ 46%]
tests/test_log_gradle.py ..................                              [ 50%]
tests/test_log_gradle_at_frames.py .......                               [ 52%]
tests/test_log_maven.py ................                                 [ 56%]
tests/test_log_pytest.py ................                                [ 61%]
tests/test_log_pytest_xdist.py ......                                    [ 62%]
tests/test_log_yield.py .........                                        [ 65%]
tests/test_promoted.py Fs..                                              [ 66%]
tests/test_ratelimit.py ..........................                       [ 73%]
tests/test_rawstore.py ...........................                       [ 80%]
tests/test_sample_frame.py .........                                     [ 82%]
tests/test_scaffold.py ...                                               [ 83%]
tests/test_test_files.py ........                                        [ 85%]
tests/test_test_ids.py ................................................. [ 98%]
.                                                                        [ 98%]
tests/test_transient_governor.py .....                                   [100%]

=================================== FAILURES ===================================
______________________________ test_resolve_smoke ______________________________

mock_to_parquet = <MagicMock name='to_parquet' id='131096106185296'>

    @unittest.mock.patch('pandas.DataFrame.to_parquet')
    def test_resolve_smoke(mock_to_parquet):
>       df = run_resolve(limit=1)
             ^^^^^^^^^^^^^^^^^^^^
E       TypeError: run() got an unexpected keyword argument 'limit'

tests/test_promoted.py:11: TypeError
=========================== short test summary info ============================
FAILED tests/test_promoted.py::test_resolve_smoke - TypeError: run() got an u...
============= 1 failed, 377 passed, 1 skipped in 69.73s (0:01:09) ==============
```

---

## 2. Test Count Prediction & Actual

- **Predicted**: 377 passed, 1 failing smoke (`test_promoted.py::test_resolve_smoke`), 1 skipped
- **Actual**: 377 passed, 1 failing smoke (`test_promoted.py::test_resolve_smoke`), 1 skipped
- **Delta**: 0

---

## 3. Files Created / Modified & Line Counts

| File | Status | Line Count | Purpose |
| :--- | :---: | ---: | :--- |
| `docs/SCHEMA_CONFORMANCE.md` | Created | 134 | Phase 1 schema conformance document mapping all columns |
| `docs/phase/014B-missing-negatives.md` | Created | 97 | Phase 2 empirical report on missing negative outcomes |
| `release/v0.1/WITHDRAWN.md` | Created | 52 | Phase 3 formal withdrawal notice for `release/v0.1` |
| `docs/DECISIONS.md` | Modified | +5 lines | Phase 4 appended D-42 (schema conformance) |
| `docs/phase/014B-REPORT.md` | Created | 163 | Final report block artifact |
| `docs/session/074-2026-08-31-014B-schema-conformance-and-withdrawal.md` | Created | ~160 | Session 074 audit and history log |
| `docs/session/INDEX.md` | Modified | +1 line | Updated session registry |
| `docs/HANDOFF.md` | Modified | +1 line | Handover state append |

---

## 4. Non-Goals Honoured

- Touched NO code in `src/`, `analysis/`, `tests/`, or `Makefile`.
- Did NOT edit `docs/SCHEMAS.md` or `docs/ROADMAP.md`.
- Did NOT edit any Parquet files.
- Did NOT generate synthetic negatives.
- Did NOT sample Holdout v5.
- Did NOT run git write commands beyond local workspace file preparation.

---

## 5. Contradictions & Findings

- The 61 absent columns identified in 013-B were confirmed to belong entirely to 5 CUT tables (`graph_nodes`, `graph_edges`, `gold`, `identity_map`, `graph_index`) cut per D-05 and D-07, and are not pipeline defects.
- All 20,535 rows in `data/interim/parsed_outcomes.parquet` and 8,980 rows in `outcomes.parquet` / `labels.parquet` are positive failures; no negative candidate evaluations exist anywhere in the dataset.
- `release/v0.1` had no Zenodo DOI minted, no external release, and no git tags other than `frame_v1`.

---

## 6. Open Questions / Next Actions

- CLI-1 to implement pipeline schema repairs for DEFECT columns in `analysis/corpus_instances.py`, `src/label/fault_revealing.py`, and `analysis/cochange_mine.py`.
- CLI-1 to implement candidate negative test universe generation per `ROADMAP.md` §9.3 step 6.
