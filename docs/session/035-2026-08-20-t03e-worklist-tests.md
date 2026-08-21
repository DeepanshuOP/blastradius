# Session Report: 035-2026-08-20-t03e-worklist-tests

**Date:** 2026-08-20 (Session timestamp: 2026-08-21T09:30Z)  
**Task ID:** T0.3e / worklist-tests  
**Model:** Gemini 3.7 Flash  
**Topic:** Add unit tests for `_build_log_worklist()` to `tests/test_daemon.py`  

---

## 1. Task Statement
Add unit tests for `_build_log_worklist()` in `tests/test_daemon.py` covering:
1. Success filtering within the same run as a failure.
2. Exclusion of non-failure conclusions (`cancelled`, `skipped`, `timed_out`, missing/None).
3. Cross-repo interleaving (oldest-first across multiple repos, proving sort is post-loop).
4. Partition sorting (120-day expired job sorts AFTER 80-day unexpired job by index position).
5. Retention of expired jobs in the queue (deprioritised, never dropped).
6. Determinism across multiple calls on identical input.
7. Graceful empty list return for repos with only non-failure jobs without raising.

No production code changes (`src/harvest/daemon.py` remains untouched). Explicit fixed `now` injected in every test.

---

## 2. STEP 0b — `LOG_RETENTION_DAYS` Grep and Call Site Analysis

### Command
```bash
grep -n "LOG_RETENTION_DAYS" src/harvest/daemon.py analysis/*.py
```

### Output
```
src/harvest/daemon.py:126:LOG_RETENTION_DAYS = 90.0
src/harvest/daemon.py:935:            stats["recovered_runs_over_90d"] += sum(1 for a in run_ages if a > LOG_RETENTION_DAYS)
src/harvest/daemon.py:1015:        else ((0, -e[3]) if e[3] <= LOG_RETENTION_DAYS else (1, -e[3]))
src/harvest/daemon.py:1145:    n_expired = sum(1 for a in run_ages if a > LOG_RETENTION_DAYS)
src/harvest/daemon.py:1185:    n_expired = sum(1 for a in all_run_ages if a > LOG_RETENTION_DAYS)
src/harvest/daemon.py:1213:        "log_retention_days": LOG_RETENTION_DAYS,
src/harvest/daemon.py:1236:        "log_retention_days": LOG_RETENTION_DAYS,
```

### Call Site Audit
1. `src/harvest/daemon.py:126`: Definition `LOG_RETENTION_DAYS = 90.0`.
2. `src/harvest/daemon.py:935`: Float comparison (`a > LOG_RETENTION_DAYS`). Safe.
3. `src/harvest/daemon.py:1015`: Float comparison (`e[3] <= LOG_RETENTION_DAYS`) in `_build_log_worklist` sort key. Safe.
4. `src/harvest/daemon.py:1145`: Float comparison (`a > LOG_RETENTION_DAYS`). Safe.
5. `src/harvest/daemon.py:1185`: Float comparison (`a > LOG_RETENTION_DAYS`). Safe.
6. `src/harvest/daemon.py:1213`: Value passed as float to summary dictionary (`"log_retention_days"`). Safe.
7. `src/harvest/daemon.py:1236`: Value passed as float to summary dictionary (`"log_retention_days"`). Safe.
8. `analysis/*.py`: 0 references found.

No site uses identity comparison (`is`) or type-sensitive operations incompatible with `float`.

---

## 3. Full Text of the Seven New Tests (`tests/test_daemon.py`)

```python
# ---------------------------------------------------------------------------
# T0.3e stage 4 — _build_log_worklist tests
# ---------------------------------------------------------------------------

def _seed_jobs_unit(store, cursor, repo, run_id, jobs):
    cursor.mark_unit_started(repo, "jobs", run_id)
    store.write_records(
        repo, "jobs", run_id,
        [RawRecord(url="seed", status=200, fetched_at="2020-01-01T00:00:00+00:00", etag=None,
                   body=json.dumps({"jobs": jobs}).encode())],
    )
    cursor.mark_unit_complete(repo, "jobs", run_id)


def test_worklist_filters_success_and_keeps_failure_in_same_run(tmp_path):
    """1. A 'success' job in the SAME run as a 'failure' job: failure is in the list, success is not."""
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    now = datetime(2026, 8, 20, 12, 0, 0, tzinfo=timezone.utc)

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])
    run_ts = (now - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _seed_runs_unit(store, cursor, "owner/repo", SHA_A, [_run_obj(100, run_ts)])
    _seed_jobs_unit(
        store, cursor, "owner/repo", 100,
        [
            {"id": 1001, "conclusion": "failure"},
            {"id": 1002, "conclusion": "success"},
        ],
    )

    worklist = daemon._build_log_worklist(["owner/repo"], store=store, cursor=cursor, now=now)

    assert worklist == [("owner/repo", 1001, 100, 10.0)]
    cursor.close()


def test_worklist_excludes_non_failure_conclusions(tmp_path):
    """2. Conclusions 'cancelled', 'skipped', 'timed_out', and missing/None are each excluded."""
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    now = datetime(2026, 8, 20, 12, 0, 0, tzinfo=timezone.utc)

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])
    run_ts = (now - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _seed_runs_unit(store, cursor, "owner/repo", SHA_A, [_run_obj(200, run_ts)])
    _seed_jobs_unit(
        store, cursor, "owner/repo", 200,
        [
            {"id": 2001, "conclusion": "cancelled"},
            {"id": 2002, "conclusion": "skipped"},
            {"id": 2003, "conclusion": "timed_out"},
            {"id": 2004, "conclusion": None},
            {"id": 2005},  # missing conclusion key
        ],
    )

    worklist = daemon._build_log_worklist(["owner/repo"], store=store, cursor=cursor, now=now)

    assert worklist == []
    cursor.close()


def test_worklist_interleaves_two_repos_oldest_first(tmp_path):
    """3. Oldest-first across TWO repos: jobs from repo A and repo B interleave by age."""
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    now = datetime(2026, 8, 20, 12, 0, 0, tzinfo=timezone.utc)

    # Repo A: run 1 (70d ago), run 2 (20d ago)
    _seed_pulls_page(store, cursor, "org/repo-a", 1, [_pr(1, RECENT), _pr(2, RECENT)])
    _seed_pull_commits(store, cursor, "org/repo-a", 1, [SHA_A])
    _seed_pull_commits(store, cursor, "org/repo-a", 2, [SHA_B])
    _seed_runs_unit(store, cursor, "org/repo-a", SHA_A, [_run_obj(1, (now - timedelta(days=70)).strftime("%Y-%m-%dT%H:%M:%SZ"))])
    _seed_runs_unit(store, cursor, "org/repo-a", SHA_B, [_run_obj(2, (now - timedelta(days=20)).strftime("%Y-%m-%dT%H:%M:%SZ"))])
    _seed_jobs_unit(store, cursor, "org/repo-a", 1, [{"id": 101, "conclusion": "failure"}])
    _seed_jobs_unit(store, cursor, "org/repo-a", 2, [{"id": 102, "conclusion": "failure"}])

    # Repo B: run 3 (50d ago), run 4 (10d ago)
    _seed_pulls_page(store, cursor, "org/repo-b", 1, [_pr(1, RECENT), _pr(2, RECENT)])
    _seed_pull_commits(store, cursor, "org/repo-b", 1, [SHA_C])
    _seed_pull_commits(store, cursor, "org/repo-b", 2, ["d" * 40])
    _seed_runs_unit(store, cursor, "org/repo-b", SHA_C, [_run_obj(3, (now - timedelta(days=50)).strftime("%Y-%m-%dT%H:%M:%SZ"))])
    _seed_runs_unit(store, cursor, "org/repo-b", "d" * 40, [_run_obj(4, (now - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ"))])
    _seed_jobs_unit(store, cursor, "org/repo-b", 3, [{"id": 201, "conclusion": "failure"}])
    _seed_jobs_unit(store, cursor, "org/repo-b", 4, [{"id": 202, "conclusion": "failure"}])

    worklist = daemon._build_log_worklist(["org/repo-a", "org/repo-b"], store=store, cursor=cursor, now=now)

    # Hand-computed expected order:
    # 1. repo-a job 101 (70d)
    # 2. repo-b job 201 (50d)
    # 3. repo-a job 102 (20d)
    # 4. repo-b job 202 (10d)
    assert worklist == [
        ("org/repo-a", 101, 1, 70.0),
        ("org/repo-b", 201, 3, 50.0),
        ("org/repo-a", 102, 2, 20.0),
        ("org/repo-b", 202, 4, 10.0),
    ]
    cursor.close()


def test_worklist_partition_120d_sorts_after_80d(tmp_path):
    """4. PARTITION: a job whose run is 120 days old sorts AFTER a job whose run is 80 days old."""
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    now = datetime(2026, 8, 20, 12, 0, 0, tzinfo=timezone.utc)

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT), _pr(2, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])
    _seed_pull_commits(store, cursor, "owner/repo", 2, [SHA_B])

    run_120d = (now - timedelta(days=120)).strftime("%Y-%m-%dT%H:%M:%SZ")
    run_80d = (now - timedelta(days=80)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _seed_runs_unit(store, cursor, "owner/repo", SHA_A, [_run_obj(301, run_120d)])
    _seed_runs_unit(store, cursor, "owner/repo", SHA_B, [_run_obj(302, run_80d)])
    _seed_jobs_unit(store, cursor, "owner/repo", 301, [{"id": 3001, "conclusion": "failure"}])
    _seed_jobs_unit(store, cursor, "owner/repo", 302, [{"id": 3002, "conclusion": "failure"}])

    worklist = daemon._build_log_worklist(["owner/repo"], store=store, cursor=cursor, now=now)

    assert len(worklist) == 2
    # 80d job is partition 0 (urgent within 90d retention), 120d is partition 1 (expired cliff)
    assert worklist[0] == ("owner/repo", 3002, 302, 80.0)
    assert worklist[1] == ("owner/repo", 3001, 301, 120.0)
    assert worklist.index(("owner/repo", 3002, 302, 80.0)) < worklist.index(("owner/repo", 3001, 301, 120.0))
    cursor.close()


def test_worklist_retains_120d_expired_job(tmp_path):
    """5. The 120-day job is PRESENT in the returned list (deprioritised, never dropped)."""
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    now = datetime(2026, 8, 20, 12, 0, 0, tzinfo=timezone.utc)

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])
    run_120d = (now - timedelta(days=120)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _seed_runs_unit(store, cursor, "owner/repo", SHA_A, [_run_obj(401, run_120d)])
    _seed_jobs_unit(store, cursor, "owner/repo", 401, [{"id": 4001, "conclusion": "failure"}])

    worklist = daemon._build_log_worklist(["owner/repo"], store=store, cursor=cursor, now=now)

    assert len(worklist) == 1
    assert worklist == [("owner/repo", 4001, 401, 120.0)]
    assert worklist[0][3] == 120.0
    assert worklist[0][3] > daemon.LOG_RETENTION_DAYS
    cursor.close()


def test_worklist_deterministic_on_identical_input(tmp_path):
    """6. Determinism: two calls on identical input return identical lists."""
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    now = datetime(2026, 8, 20, 12, 0, 0, tzinfo=timezone.utc)

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT), _pr(2, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])
    _seed_pull_commits(store, cursor, "owner/repo", 2, [SHA_B])
    _seed_runs_unit(
        store, cursor, "owner/repo", SHA_A,
        [_run_obj(501, (now - timedelta(days=40)).strftime("%Y-%m-%dT%H:%M:%SZ"))],
    )
    _seed_runs_unit(
        store, cursor, "owner/repo", SHA_B,
        [_run_obj(502, (now - timedelta(days=110)).strftime("%Y-%m-%dT%H:%M:%SZ"))],
    )
    _seed_jobs_unit(store, cursor, "owner/repo", 501, [{"id": 5001, "conclusion": "failure"}])
    _seed_jobs_unit(store, cursor, "owner/repo", 502, [{"id": 5002, "conclusion": "failure"}])

    worklist_1 = daemon._build_log_worklist(["owner/repo"], store=store, cursor=cursor, now=now)
    worklist_2 = daemon._build_log_worklist(["owner/repo"], store=store, cursor=cursor, now=now)

    assert len(worklist_1) == 2
    assert worklist_1 == worklist_2
    cursor.close()


def test_worklist_all_non_failure_jobs_returns_empty(tmp_path):
    """7. A repo whose jobs are all non-failure returns [] and does not raise."""
    store = RawStore(tmp_path / "raw")
    cursor = CursorStore(tmp_path / "cursor.db")
    now = datetime(2026, 8, 20, 12, 0, 0, tzinfo=timezone.utc)

    _seed_pulls_page(store, cursor, "owner/repo", 1, [_pr(1, RECENT)])
    _seed_pull_commits(store, cursor, "owner/repo", 1, [SHA_A])
    _seed_runs_unit(
        store, cursor, "owner/repo", SHA_A,
        [_run_obj(601, (now - timedelta(days=15)).strftime("%Y-%m-%dT%H:%M:%SZ"))],
    )
    _seed_jobs_unit(
        store, cursor, "owner/repo", 601,
        [
            {"id": 6001, "conclusion": "success"},
            {"id": 6002, "conclusion": "skipped"},
        ],
    )

    worklist = daemon._build_log_worklist(["owner/repo"], store=store, cursor=cursor, now=now)

    assert worklist == []
    cursor.close()
```

---

## 4. Test Suite Execution and Verification

### Single File Run: `tests/test_daemon.py`
- **Command:**
```bash
uv run pytest tests/test_daemon.py -q
```
- **Output:**
```
..................................................................       [100%]
66 passed in 2.91s
```

### Full Repository Test Suite Run
- **Predicted:** 209 passed (202 baseline + 7 new worklist tests)
- **Command:**
```bash
uv run pytest -q
```
- **Output:**
```
........................................................................ [ 34%]
........................................................................ [ 68%]
.................................................................        [100%]
209 passed in 3.20s
```
- **Actual:** 209 passed in 3.20s (0 failures, 0 warnings). Deviation: 0.

---

## 5. Files Changed and Line Counts
- `tests/test_daemon.py`: +208 lines (added `_seed_jobs_unit` helper and 7 unit tests)
- `docs/session/INDEX.md`: +1 line (registered session 035)
- `docs/HANDOFF.md`: +1 line (appended session 035 handoff entry)
- `docs/session/035-2026-08-20-t03e-worklist-tests.md`: created session report

---

## 6. Non-Goals Honoured
- Did NOT modify `src/harvest/daemon.py` or any production code.
- Did NOT modify `analysis/expiry_cliff.py` (owned by Terminal B).
- Did NOT modify or reformat any existing tests in `tests/test_daemon.py`.
- Did NOT touch `cursor.py`, `rawstore.py`, `ratelimit.py`, `frame.py`, or `analysis/`.
- Did NOT read, edit, or print `.env`.
- Did NOT run `make tables` or analysis scripts.
- Did NOT run git write commands or make any commit.
- Did NOT signal, kill, or disturb background daemon (PID 3748 / 3745).

---

## 7. Open Questions
- None. `_build_log_worklist()` is fully specified, verified, and protected by unit tests. Next step: Stage 4 log capture orchestrator implementation (`capture_job_logs()` / `--stage logs`).
