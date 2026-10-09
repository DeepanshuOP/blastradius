# `release_v02/` fixtures

`interim/*.parquet` is a verbatim row slice of the real `data/interim/` tables
(9 workflow runs, 5 labelled test pairs, 30 changeset rows), taken with plain
`semi join`s on run_id and (run_id, test_id). Nothing was edited except
`instances_raw.author_login`, replaced by `user-N` so that no corpus login is
checked in (see `../release/README.md`).

The slice was picked to hit every branch of the v0.2 build:

| run_id | what it exercises |
|---|---|
| 16250928760 | `no_base` (null base fields), changeset present, no labels |
| 22419331298 | success run absent from base resolution -> `not_attempted` |
| 27210554856 | pair with 2 job rows and 2 distinct failure messages |
| 27573755985 | docs-only changeset (`is_docs_only` true) |
| 27810859844 | single job row, fully-qualified exact binding, message + duration |
| 28766919851 | exact binding, not fully qualified (confidence 0.5), no message |
| 29752097395 | 20 job rows, mixed `fail`/`error`, `not_found` binding |
| 31218903455 | `ambiguous` binding |
| 31495838733 | success run with no changeset -> every changeset column NULL |

Expected values in `tests/test_release_v02.py` were derived by hand from these
files (sums of additions + deletions, sorted paths, byte-order minimum message),
not by running the code under test.
