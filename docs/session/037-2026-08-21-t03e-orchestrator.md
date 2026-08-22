# Session Report: 037-2026-08-21-t03e-orchestrator

**Date:** 2026-08-21 (Session timestamp: 2026-08-21T17:15Z)  
**Task ID:** T0.3e Orchestrator (`capture_job_logs`)  
**Model:** Gemini 3.7 Flash  
**Topic:** Implement `capture_job_logs()` in `src/harvest/daemon.py` and add 5 comprehensive unit tests in `tests/test_daemon.py`  

---

## 1. Task Statement
Implement `capture_job_logs()` in `src/harvest/daemon.py` — the Stage 4 fetch loop over `_build_log_worklist()`.
No CLI wiring, no `_summary` changes. Follow reading discipline, guard check, and conservation laws.

---

## 2. STEP 0 — Guard Output

```
Linux
/home/shree/blastradius
Python 3.11.15
```

---

## 3. STEP 1 — Approved Signature & Counter Dict

### Signature
```python
def capture_job_logs(
    repo_fulls: list[str],
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    governor: TransientGovernor | None = None,
    now: datetime | None = None,
    max_logs: int | None = None,
    skip_expired: bool = True,
) -> dict[str, int]:
```

### Counter Dictionary
```python
    stats = {
        "n_worklist_total": len(worklist),
        "n_logs_captured": 0,
        "n_logs_dedup_skipped": 0,
        "n_logs_skipped_expired": 0,
        "n_logs_expired": 0,
        "n_logs_failed_terminal": 0,
        "n_logs_transient": 0,
        "n_logs_capped": 0,
        "n_logs_unknown_status": 0,
        "total_log_bytes": 0,
    }
```

### Conservation Invariant Assertion
```python
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
    if accounted != stats["n_worklist_total"]:
        raise AssertionError(
            f"capture_job_logs: conservation check failed — "
            f"n_worklist_total={stats['n_worklist_total']} accounted={accounted}"
        )
```

---

## 4. STEP 1 — Question Answers with Quoted Evidence

### a) How does `capture_checkruns` structure its loop — where does it call the governor, where does it break on `AbortRun`, and does it re-raise `AllTokensDead`?
- **Governor calls**:
  - On `PR_UNIT_TRANSIENT`: increments counter, calls `governor.record_transient(status=status_code, token_idx=None)`, and does `continue`.
  - On non-transient status: calls `governor.record_success()`.
- **`AbortRun`**: `capture_checkruns` does not catch `AbortRun`; `governor.record_transient` raises `AbortRun` when the pause ladder is exhausted, allowing it to propagate.
- **`AllTokensDead`**: `_fetch_*` helpers let `AllTokensDead` escape (`except AllTokensDead: raise`), and `capture_checkruns` allows it to bubble up uncaught.

**Quoted loop body from `src/harvest/daemon.py`:**
```python
    for repo_full, owner, repo, sha, run_ages in entries:
        cr_status, check_runs, cr_status_code = _fetch_checkruns_for_sha(
            owner, repo, sha, pool=pool, store=store, cursor=cursor, repo_full=repo_full
        )

        if cr_status == PR_UNIT_TRANSIENT:
            stats["n_transient_checkruns"] += 1
            governor.record_transient(status=cr_status_code, token_idx=None)
            continue
        governor.record_success()

        if cr_status == PR_UNIT_FAILED:
            stats["n_checkruns_failed_terminal"] += 1
            continue
        if check_runs is None:
            continue  # already-terminal non-complete unit from an earlier run — no data
        if cr_status == PR_UNIT_SKIPPED_ALREADY_DONE:
            stats["n_checkruns_dedup_skipped"] += 1
        else:
            stats["n_checkruns_fetched_fresh"] += 1
        stats["n_checkruns_discovered"] += len(check_runs)
```

### b) `_fetch_job_log` returns `(status, bytes_or_None, status_code)`. Which `PR_UNIT_*` constant does a dedup skip return, and how does that differ from a fresh complete?
- **Dedup skip**: returns `(PR_UNIT_SKIPPED_ALREADY_DONE, None, None)`. No request issued, no disk uncompression.
- **Fresh complete**: returns `(PR_UNIT_COMPLETE, len(response.content), None)`. Transferred payload size returned as integer.

**Quoted branches from `src/harvest/daemon.py`:**
```python
    existing = cursor.get_capture_unit(repo_full, "logs", job_id)
    if existing is not None and existing.status != "in_flight":
        return PR_UNIT_SKIPPED_ALREADY_DONE, None, None
```
```python
    store.write_records(repo_full, "logs", job_id, [_record_from_response(response)])
    cursor.mark_unit_complete(repo_full, "logs", job_id)
    return PR_UNIT_COMPLETE, len(response.content), None
```

### c) Does `capture_checkruns` return a flat dict of ints, or nested?
`capture_checkruns` returns a flat dict (`dict[str, int | list[int]]`). `capture_job_logs` returns a flat dict of ints (`dict[str, int]`).

---

## 5. Code Diff

### `git diff src/harvest/daemon.py`
```diff
diff --git a/src/harvest/daemon.py b/src/harvest/daemon.py
index 51a1eed..4992f48 100644
--- a/src/harvest/daemon.py
+++ b/src/harvest/daemon.py
@@ -1017,6 +1017,105 @@ def _build_log_worklist(
     return items
 
 
+def capture_job_logs(
+    repo_fulls: list[str],
+    *,
+    pool: TokenPool,
+    store: RawStore,
+    cursor: CursorStore,
+    governor: TransientGovernor | None = None,
+    now: datetime | None = None,
+    max_logs: int | None = None,
+    skip_expired: bool = True,
+) -> dict[str, int]:
+    """Stage 4: job log capture (endpoint 9) for failed workflow jobs
+    discovered in Stage 2, prioritized by run age (recoverable runs under
+    90 days first)."""
+    now = now or datetime.now(timezone.utc)
+    governor = governor if governor is not None else TransientGovernor(pool)
+
+    worklist = _build_log_worklist(repo_fulls, store=store, cursor=cursor, now=now)
+
+    stats = {
+        "n_worklist_total": len(worklist),
+        "n_logs_captured": 0,
+        "n_logs_dedup_skipped": 0,
+        "n_logs_skipped_expired": 0,
+        "n_logs_expired": 0,
+        "n_logs_failed_terminal": 0,
+        "n_logs_transient": 0,
+        "n_logs_capped": 0,
+        "n_logs_unknown_status": 0,
+        "total_log_bytes": 0,
+    }
+
+    n_attempted = 0
+    for repo_full, job_id, parent_run_id, run_age_days in worklist:
+        if max_logs is not None and n_attempted >= max_logs:
+            stats["n_logs_capped"] += 1
+            continue
+
+        if skip_expired and run_age_days is not None and run_age_days > LOG_RETENTION_DAYS:
+            stats["n_logs_skipped_expired"] += 1
+            continue
+
+        owner, repo = repo_full.split("/", 1)
+        status, log_bytes, status_code = _fetch_job_log(
+            owner,
+            repo,
+            job_id,
+            pool=pool,
+            store=store,
+            cursor=cursor,
+            repo_full=repo_full,
+            parent_run_id=parent_run_id,
+        )
+
+        if status == PR_UNIT_SKIPPED_ALREADY_DONE:
+            stats["n_logs_dedup_skipped"] += 1
+            governor.record_success()
+            continue
+
+        n_attempted += 1
+
+        if status == PR_UNIT_TRANSIENT:
+            stats["n_logs_transient"] += 1
+            governor.record_transient(status=status_code, token_idx=None)
+            continue
+
+        governor.record_success()
+
+        if status == PR_UNIT_COMPLETE:
+            stats["n_logs_captured"] += 1
+            if log_bytes is not None:
+                stats["total_log_bytes"] += log_bytes
+        elif status == PR_UNIT_FAILED:
+            if status_code in (404, 410):
+                stats["n_logs_expired"] += 1
+            else:
+                stats["n_logs_failed_terminal"] += 1
+        else:
+            stats["n_logs_unknown_status"] += 1
+
+    accounted = (
+        stats["n_logs_captured"]
+        + stats["n_logs_dedup_skipped"]
+        + stats["n_logs_skipped_expired"]
+        + stats["n_logs_expired"]
+        + stats["n_logs_failed_terminal"]
+        + stats["n_logs_transient"]
+        + stats["n_logs_capped"]
+        + stats["n_logs_unknown_status"]
+    )
+    if accounted != stats["n_worklist_total"]:
+        raise AssertionError(
+            f"capture_job_logs: conservation check failed — "
+            f"n_worklist_total={stats['n_worklist_total']} accounted={accounted}"
+        )
+
+    return stats
+
+
 def _summary(pages_fetched, window_stopped, n_prs_captured, n_prs_failed_terminal, n_transient) -> dict:
     return {
         "pages_fetched": pages_fetched,
```

---

## 6. Full Text of All Five Tests

```python
@responses.activate
def test_conservation_holds_across_mixed_job_log_outcomes(tmp_path):
    """1. Conservation: buckets sum to n_worklist_total on a mixed fixture."""
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()
    now = datetime(2026, 8, 20, 12, 0, 0, tzinfo=timezone.utc)

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])
    _seed_runs_unit(
        store, cursor, "owner/repo", SHA_A,
        [
            _run_obj(101, (now - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ")),
            _run_obj(102, (now - timedelta(days=20)).strftime("%Y-%m-%dT%H:%M:%SZ")),
            _run_obj(103, (now - timedelta(days=120)).strftime("%Y-%m-%dT%H:%M:%SZ")),
            _run_obj(104, (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")),
            _run_obj(105, (now - timedelta(days=40)).strftime("%Y-%m-%dT%H:%M:%SZ")),
            _run_obj(106, (now - timedelta(days=50)).strftime("%Y-%m-%dT%H:%M:%SZ")),
        ],
    )
    _seed_jobs_unit(store, cursor, "owner/repo", 101, [{"id": 1001, "conclusion": "failure"}])
    _seed_jobs_unit(store, cursor, "owner/repo", 102, [{"id": 1002, "conclusion": "failure"}])
    _seed_jobs_unit(store, cursor, "owner/repo", 103, [{"id": 1003, "conclusion": "failure"}])
    _seed_jobs_unit(store, cursor, "owner/repo", 104, [{"id": 1004, "conclusion": "failure"}])
    _seed_jobs_unit(store, cursor, "owner/repo", 105, [{"id": 1005, "conclusion": "failure"}])
    _seed_jobs_unit(store, cursor, "owner/repo", 106, [{"id": 1006, "conclusion": "failure"}])

    # 1001: fresh capture
    log_content = b"2026-08-10 log output\n"
    responses.add(responses.GET, _job_log_url("owner", "repo", 1001), body=log_content, status=200)

    # 1002: dedup skip (already complete)
    cursor.mark_unit_started("owner/repo", "logs", 1002, parent_run_id=102)
    store.write_records(
        "owner/repo", "logs", 1002,
        [RawRecord(url=_job_log_url("owner", "repo", 1002), status=200,
                   fetched_at="2026-08-01T00:00:00+00:00", etag=None, body=b"existing log")],
    )
    cursor.mark_unit_complete("owner/repo", "logs", 1002)

    # 1003: 120-day item -> skipped expired with skip_expired=True (no request)

    # 1004: 404 -> expired
    responses.add(responses.GET, _job_log_url("owner", "repo", 1004), status=404)

    # 1005: 451 -> non-expired terminal failure (451 in TERMINAL_STATUSES)
    responses.add(responses.GET, _job_log_url("owner", "repo", 1005), status=451)

    # 1006: 503 -> transient failure (6 retries)
    for _ in range(6):
        responses.add(responses.GET, _job_log_url("owner", "repo", 1006), status=503)

    stats = daemon.capture_job_logs(
        ["owner/repo"],
        pool=pool,
        store=store,
        cursor=cursor,
        now=now,
        skip_expired=True,
    )

    assert stats["n_worklist_total"] == 6
    assert stats["n_logs_captured"] == 1
    assert stats["n_logs_dedup_skipped"] == 1
    assert stats["n_logs_skipped_expired"] == 1
    assert stats["n_logs_expired"] == 1
    assert stats["n_logs_failed_terminal"] == 1
    assert stats["n_logs_transient"] == 1
    assert stats["n_logs_capped"] == 0
    assert stats["n_logs_unknown_status"] == 0
    assert stats["total_log_bytes"] == len(log_content)
    assert (
        stats["n_logs_captured"]
        + stats["n_logs_dedup_skipped"]
        + stats["n_logs_skipped_expired"]
        + stats["n_logs_expired"]
        + stats["n_logs_failed_terminal"]
        + stats["n_logs_transient"]
        + stats["n_logs_capped"]
        + stats["n_logs_unknown_status"]
    ) == stats["n_worklist_total"]
    cursor.close()


@responses.activate
def test_skip_expired_true_issues_zero_requests_for_old_item(tmp_path):
    """2. skip_expired=True issues ZERO requests for a 120-day item and counts it as n_logs_skipped_expired."""
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()
    now = datetime(2026, 8, 20, 12, 0, 0, tzinfo=timezone.utc)

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])
    _seed_runs_unit(
        store, cursor, "owner/repo", SHA_A,
        [_run_obj(201, (now - timedelta(days=120)).strftime("%Y-%m-%dT%H:%M:%SZ"))],
    )
    _seed_jobs_unit(store, cursor, "owner/repo", 201, [{"id": 2001, "conclusion": "failure"}])

    stats = daemon.capture_job_logs(
        ["owner/repo"],
        pool=pool,
        store=store,
        cursor=cursor,
        now=now,
        skip_expired=True,
    )

    assert stats["n_worklist_total"] == 1
    assert stats["n_logs_skipped_expired"] == 1
    assert stats["n_logs_captured"] == 0
    assert stats["n_logs_expired"] == 0
    assert stats["n_logs_failed_terminal"] == 0
    assert len(responses.calls) == 0
    assert cursor.get_capture_unit("owner/repo", "logs", 2001) is None
    cursor.close()


@responses.activate
def test_skip_expired_false_attempts_old_item_and_404_lands_in_expired(tmp_path):
    """3. skip_expired=False attempts it, and a 404 lands in n_logs_expired, NOT n_logs_failed_terminal."""
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()
    now = datetime(2026, 8, 20, 12, 0, 0, tzinfo=timezone.utc)

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])
    _seed_runs_unit(
        store, cursor, "owner/repo", SHA_A,
        [_run_obj(301, (now - timedelta(days=120)).strftime("%Y-%m-%dT%H:%M:%SZ"))],
    )
    _seed_jobs_unit(store, cursor, "owner/repo", 301, [{"id": 3001, "conclusion": "failure"}])

    responses.add(responses.GET, _job_log_url("owner", "repo", 3001), status=404)

    stats = daemon.capture_job_logs(
        ["owner/repo"],
        pool=pool,
        store=store,
        cursor=cursor,
        now=now,
        skip_expired=False,
    )

    assert stats["n_worklist_total"] == 1
    assert stats["n_logs_skipped_expired"] == 0
    assert stats["n_logs_expired"] == 1
    assert stats["n_logs_failed_terminal"] == 0
    assert len(responses.calls) == 1
    assert cursor.get_capture_unit("owner/repo", "logs", 3001).status == "failed"
    cursor.close()


@responses.activate
def test_max_logs_attempts_capped_count_and_caps_remainder(tmp_path):
    """4. max_logs=1 attempts exactly one and puts the rest in n_logs_capped."""
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()
    now = datetime(2026, 8, 20, 12, 0, 0, tzinfo=timezone.utc)

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])
    _seed_runs_unit(
        store, cursor, "owner/repo", SHA_A,
        [_run_obj(401, (now - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ"))],
    )
    _seed_jobs_unit(
        store, cursor, "owner/repo", 401,
        [
            {"id": 4001, "conclusion": "failure"},
            {"id": 4002, "conclusion": "failure"},
            {"id": 4003, "conclusion": "failure"},
        ],
    )

    responses.add(responses.GET, _job_log_url("owner", "repo", 4001), body=b"log 4001", status=200)

    stats = daemon.capture_job_logs(
        ["owner/repo"],
        pool=pool,
        store=store,
        cursor=cursor,
        now=now,
        max_logs=1,
    )

    assert stats["n_worklist_total"] == 3
    assert stats["n_logs_captured"] == 1
    assert stats["n_logs_capped"] == 2
    assert len(responses.calls) == 1
    cursor.close()


@responses.activate
def test_already_complete_logs_unit_counts_as_dedup_skipped_without_request(tmp_path):
    """5. An already-complete logs unit counts as n_logs_dedup_skipped with no request."""
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    pool = _pool()
    now = datetime(2026, 8, 20, 12, 0, 0, tzinfo=timezone.utc)

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])
    _seed_runs_unit(
        store, cursor, "owner/repo", SHA_A,
        [_run_obj(501, (now - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ"))],
    )
    _seed_jobs_unit(store, cursor, "owner/repo", 501, [{"id": 5001, "conclusion": "failure"}])

    cursor.mark_unit_started("owner/repo", "logs", 5001, parent_run_id=501)
    store.write_records(
        "owner/repo", "logs", 5001,
        [RawRecord(url=_job_log_url("owner", "repo", 5001), status=200,
                   fetched_at="2026-08-01T00:00:00+00:00", etag=None, body=b"persisted log")],
    )
    cursor.mark_unit_complete("owner/repo", "logs", 5001)

    stats = daemon.capture_job_logs(
        ["owner/repo"],
        pool=pool,
        store=store,
        cursor=cursor,
        now=now,
    )

    assert stats["n_worklist_total"] == 1
    assert stats["n_logs_dedup_skipped"] == 1
    assert stats["n_logs_captured"] == 0
    assert stats["total_log_bytes"] == 0
    assert len(responses.calls) == 0
    cursor.close()
```

---

## 7. Raw Test Output (Predicted vs Actual)

- **Predicted count:** 214
- **Actual count:** 214

```
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/shree/blastradius
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.14.2
collecting ... collected 214 items

tests/test_cursor.py ...................                                 [  8%]
tests/test_daemon.py ................................................... [ 32%]
....................                                                     [ 42%]
tests/test_frame.py ...........                                          [ 47%]
tests/test_ratelimit.py ......................                           [ 57%]
tests/test_rawstore.py ........................                          [ 68%]
tests/test_sample_frame.py .........                                     [ 72%]
tests/test_scaffold.py ...                                               [ 74%]
tests/test_test_ids.py ................................................. [ 97%]
.                                                                        [ 97%]
tests/test_transient_governor.py .....                                   [100%]

============================= 214 passed in 7.18s ==============================
```

---

## 8. Files Changed with Line Counts

```
+99  lines in src/harvest/daemon.py
+241 lines in tests/test_daemon.py
```

---

## 9. Non-Goals Honoured
- No changes to `parse_args`, `--stage`, `run()`, or `_summary` (deferred to next task).
- Did not modify `_build_log_worklist`, `_fetch_job_log`, `capture_checkruns`, `discover_repo`, `sweep_repo`.
- Did not touch `cursor.py`, `rawstore.py`, `ratelimit.py`, `frame.py`, or `analysis/`.
- Did not touch `blastradius_pipeline_explorer.jsx` or any data under `data/` or `logs/`.
- Did not read, edit, or print `.env`.
- Did not commit or run writing git commands.

---

## 10. Contradictions & Findings
- **`TERMINAL_STATUSES`**: Per `src/harvest/frame.py:78`, `TERMINAL_STATUSES = frozenset({404, 410, 451})`. HTTP 500 is treated as a transient (retryable) failure. For testing non-expired terminal failure branches (`n_logs_failed_terminal`), HTTP 451 is used.
