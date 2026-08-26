# Session Report: 047-2026-08-26-rawstore-write-race

**Date:** 2026-08-26  
**Task ID:** Stage 4 `os.replace` crash diagnosis and fix in `rawstore.write_records`  
**Model:** Gemini 3.7 Flash  

---

## 1. Task Statement

Diagnose and resolve the Stage 4 daemon crash on 2026-08-25:
```
daemon.py:1063 capture_job_logs -> daemon.py:788 _fetch_job_log
-> rawstore.py:180 write_records -> os.replace(tmp_path, path)
FileNotFoundError: [Errno 2] No such file or directory:
'data/raw/baomidou__mybatis-plus/job/796/085340217796/logs.jsonl.gz.tmp'
-> 'data/raw/baomidou__mybatis-plus/job/796/085340217796/logs.jsonl.gz'
```
Prove the concurrency empirically from `logs/requests.jsonl`, make temporary file paths unique per process and call, wrap atomic write/replace operations in `RawStore` with `try...finally` cleanup and raise `RawStoreWriteError`, catch `RawStoreWriteError` and `OSError` per unit in `capture_job_logs`, track `n_logs_write_error`, preserve atomic rename guarantees and conservation checks, add real filesystem tests, and verify the test suite.

---

## 2. Guard Commands and Raw Output

```bash
$ uname -s && pwd && uv run python --version
Linux
/home/shree/blastradius
Python 3.11.15

$ git log -1 --format='%H %s'
2955b00d34e5c619b6636eaf0a7de925d891438b test: add the hand-labelled forty-log fixture corpus

$ git config user.name && git config user.email
DeepanshuOP
99538840+DeepanshuOP@users.noreply.github.com

$ git status --short
 M .gitignore
?? analysis/fixture_score.py
?? vendor/graphify-br/

$ ps aux | grep '[h]arvest\.daemon'
(exit code 1 - no running daemon)

$ git diff .gitignore
diff --git a/.gitignore b/.gitignore
index f634cf5..39cc8ce 100644
--- a/.gitignore
+++ b/.gitignore
@@ -1,7 +1,7 @@
 .env
 data/*
 corpus/
-logs/
+/logs/
 worktrees/
 paper/generated/
 __pycache__/
```

---

## 3. Evidence for Duplicate Concurrent Writers (STEP 1)

```bash
$ grep -n '85340217796' logs/requests.jsonl
235429:{"ts": "2026-08-25T09:48:33.557415+00:00", "url": "https://api.github.com/repos/baomidou/mybatis-plus/actions/jobs/85340217796/logs", "status": null, "token_idx": 1, "remaining": null, "duration_ms": 31989.02028900011, "attempt": 1, "error": "ConnectionError"}
235430:{"ts": "2026-08-25T09:48:38.785464+00:00", "url": "https://api.github.com/repos/baomidou/mybatis-plus/actions/jobs/85340217796/logs", "status": null, "token_idx": 2, "remaining": null, "duration_ms": 5021.221207999588, "attempt": 2, "error": "ConnectTimeout"}
235431:{"ts": "2026-08-25T09:48:45.180787+00:00", "url": "https://api.github.com/repos/baomidou/mybatis-plus/actions/jobs/85340217796/logs", "status": null, "token_idx": 1, "remaining": null, "duration_ms": 5058.718967999994, "attempt": 3, "error": "ConnectTimeout"}
235432:{"ts": "2026-08-25T09:48:53.672464+00:00", "url": "https://api.github.com/repos/baomidou/mybatis-plus/actions/jobs/85340217796/logs", "status": null, "token_idx": 2, "remaining": null, "duration_ms": 5049.159285000314, "attempt": 4, "error": "ConnectTimeout"}
235433:{"ts": "2026-08-25T09:49:02.984525+00:00", "url": "https://api.github.com/repos/baomidou/mybatis-plus/actions/jobs/85340217796/logs", "status": null, "token_idx": 1, "remaining": null, "duration_ms": 8096.328108999842, "attempt": 5, "error": "ConnectTimeout"}
235434:{"ts": "2026-08-25T09:49:11.701987+00:00", "url": "https://api.github.com/repos/baomidou/mybatis-plus/actions/jobs/85340217796/logs", "status": null, "token_idx": 2, "remaining": null, "duration_ms": 5803.0026320002435, "attempt": 6, "error": "ConnectionError"}
236208:{"ts": "2026-08-25T18:13:30.420150+00:00", "url": "https://api.github.com/repos/baomidou/mybatis-plus/actions/jobs/85340217796/logs", "status": 200, "token_idx": 0, "remaining": null, "duration_ms": 2181.3748659997145, "attempt": 1}
236209:{"ts": "2026-08-25T18:13:30.426073+00:00", "url": "https://api.github.com/repos/baomidou/mybatis-plus/actions/jobs/85340217796/logs", "status": 200, "token_idx": 0, "remaining": null, "duration_ms": 2209.317372999976, "attempt": 1}

$ grep -n '2026-08-25T18:13:3' logs/requests.jsonl | head -40
236208:{"ts": "2026-08-25T18:13:30.420150+00:00", "url": "https://api.github.com/repos/baomidou/mybatis-plus/actions/jobs/85340217796/logs", "status": 200, "token_idx": 0, "remaining": null, "duration_ms": 2181.3748659997145, "attempt": 1}
236209:{"ts": "2026-08-25T18:13:30.426073+00:00", "url": "https://api.github.com/repos/baomidou/mybatis-plus/actions/jobs/85340217796/logs", "status": 200, "token_idx": 0, "remaining": null, "duration_ms": 2209.317372999976, "attempt": 1}

$ grep -c '' logs/requests.jsonl
236230
```

### Analysis of Evidence:
- **(a) Request Count & Timestamps:** Job `85340217796` had 8 total requests recorded: 6 timeout/connection errors between 09:48:33 and 09:49:11 UTC, and exactly 2 successful HTTP 200 requests completed at `2026-08-25T18:13:30.420150+00:00` (duration: 2181.4 ms) and `2026-08-25T18:13:30.426073+00:00` (duration: 2209.3 ms).
- **(b) Concurrent Execution Proof:** The two requests logged completion only 5.9 ms apart, but had individual latencies of 2.18s and 2.21s. A single sequential thread or process cannot complete two 2.2-second network requests 6 ms apart. Both requests were in flight simultaneously, having started at ~18:13:28.238 UTC.
- **(c) SQLite Lock Check:**
```bash
$ grep -rn "database is locked" logs/
(no matches)
```
No `database is locked` error occurred because SQLite transactions in `cursor.py` (`mark_unit_started` and `mark_unit_complete`) are point-in-time statements that commit immediately; no transaction is held during the 2.2-second HTTP fetch or `write_records`.

**Verdict:** **CONFIRMED two writers**.

---

## 4. Crash Event Reconstruction (Labelled Reconstruction)

*(Note: The exact millisecond timing of `os.replace` calls is a plausible reconstruction from log artifacts, file mtimes, and traceback records, not direct timestamp measurements).*

1. **~18:13:28 UTC:** Two daemon processes (Writer 1 and Writer 2) both select failed job `85340217796` from the Stage 4 worklist.
2. Both execute `mark_unit_started()` in `cursor.db` and initiate parallel HTTP GET requests to GitHub endpoint 9.
3. **18:13:30.420 UTC:** Writer 1 receives the HTTP response payload and begins `store.write_records()`. It writes gzip bytes to `data/raw/baomidou__mybatis-plus/job/796/085340217796/logs.jsonl.gz.tmp`.
4. **18:13:30.426 UTC:** Writer 2 receives its HTTP response payload and begins `store.write_records()`, writing to the identical `logs.jsonl.gz.tmp` path.
5. Writer 1 finishes writing, closes its file handle, and executes `os.replace(tmp_path, path)`. The file `logs.jsonl.gz.tmp` is atomically renamed to `logs.jsonl.gz`. Writer 1 marks the unit complete in `cursor.db`.
6. Writer 2 finishes writing and calls `os.replace(tmp_path, path)`. Because Writer 1 has already moved `logs.jsonl.gz.tmp`, Writer 2's source path no longer exists, raising `FileNotFoundError: [Errno 2] No such file or directory: '...logs.jsonl.gz.tmp' -> '...logs.jsonl.gz'`.
7. Because `write_records` was unhandled in `_fetch_job_log`, the exception escaped to `capture_job_logs` and killed Writer 2's daemon process, dumping the traceback to `logs/stage4.log`.

---

## 5. Changes Implemented

### 1. `src/harvest/rawstore.py`
- Defined `RawStoreWriteError(Exception)` wrapping underlying `OSError`s.
- Made `tmp_path` unique per write call using PID and a 32-character hexadecimal UUID token:
  ```python
  tmp_path = path.parent / f"{path.name}.{os.getpid()}.{token}.tmp"
  ```
- Added cleanup for legacy unadorned `.tmp` files.
- Enclosed write and atomic replacement in `try...except OSError as exc: raise RawStoreWriteError(...) from exc`.
- Added `finally:` block with `tmp_path.unlink(missing_ok=True)` to prevent orphan `.tmp` accumulation on any failure.
- Preserved all fsync and atomic rename guarantees.

### 2. `src/harvest/daemon.py`
- Imported `RawStoreWriteError`.
- Added `n_logs_write_error` to Stage 4 stats dictionary initialized to 0.
- Wrapped `_fetch_job_log` call inside `capture_job_logs` with `try...except (RawStoreWriteError, OSError) as exc:`.
- On write error, marks unit failed via `cursor.mark_unit_failed(repo_full, "logs", job_id, f"write_error: {exc}")`, increments `stats["n_logs_write_error"] += 1` and `n_attempted += 1`, and continues the worklist loop.
- Updated conservation assertion:
  ```python
  # Before:
  accounted = (
      stats["n_logs_captured"]
      + stats["n_logs_dedup_skipped"]
      + stats["n_logs_skipped_expired"]
      + stats["n_logs_expired"]
      + stats["n_logs_failed_terminal"]
      + stats["n_logs_transient"]
      + stats["n_logs_capped"]
      + stats["n_logs_unknown_status"]
  )
  # After:
  accounted = (
      stats["n_logs_captured"]
      + stats["n_logs_dedup_skipped"]
      + stats["n_logs_skipped_expired"]
      + stats["n_logs_expired"]
      + stats["n_logs_failed_terminal"]
      + stats["n_logs_write_error"]
      + stats["n_logs_transient"]
      + stats["n_logs_capped"]
      + stats["n_logs_unknown_status"]
  )
  ```
- Surfaced `write_error={stage4_stats.get('n_logs_write_error', 0)}` in the `STAGE4:` logging output.

### 3. Exceptions Handled vs Escaping in `capture_job_logs`
- **Handled:** `RawStoreWriteError`, `OSError` (and subclasses like `FileNotFoundError`, `PermissionError`, `ENOSPC`).
- **Still Escaping (by design):** `AllTokensDead`, `KeyboardInterrupt`, `SystemExit`, cursor SQLite errors, assertion errors.

---

## 6. Verification and Test Results

### Tests Added:
1. `test_two_writes_to_same_key_from_different_tmp_paths_both_succeed` in `tests/test_rawstore.py`.
2. `test_deleting_tmp_file_mid_write_raises_rawstore_write_error` in `tests/test_rawstore.py` (simulates mid-write ENOENT on real filesystem).
3. `test_capture_job_logs_handles_rawstore_write_error_without_escaping` in `tests/test_daemon.py` (verifies `n_logs_write_error` increments, unit is marked failed in cursor, no exception escapes, conservation check holds).

### Test Prediction vs Actual:
- **Baseline passing:** 219
- **Tests added:** 3
- **Predicted passing:** 222
- **Actual passing:** 222

```bash
$ uv run pytest -q
........................................................................ [ 32%]
........................................................................ [ 64%]
........................................................................ [ 97%]
......                                                                   [100%]
222 passed in 4.05s
```

---

## 7. Files Changed and Line Counts

```bash
$ git diff --stat src/ tests/
 src/harvest/daemon.py   | 33 ++++++++++++++++++++-------------
 src/harvest/rawstore.py | 46 +++++++++++++++++++++++++++++-----------------
 tests/test_daemon.py    | 61 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-
 tests/test_rawstore.py  | 36 +++++++++++++++++++++++++++++++++---
 4 files changed, 142 insertions(+), 34 deletions(-)
```

---

## 8. Non-Goals Honoured

- Did NOT touch `analysis/log_yield.py` or any files under `analysis/`.
- Did NOT touch `tests/fixtures/logs/`.
- Did NOT touch `_build_log_worklist`, `TransientGovernor`, or `TokenPool`.
- Did NOT touch `docs/DECISIONS.md`.
- Did NOT touch `docs/HANDOFF.md`.
- Did NOT touch `cursor.db` or anything under `data/` or `logs/`.
- Did NOT weaken atomic rename guarantees or remove directory fsync.
