# Session Report: 055-2026-08-26-stage4-stall-diagnosis

**Date:** 2026-08-26 / 2026-08-27 (Local timestamp: 2026-08-27T06:23Z)  
**Task ID:** `Stage 4 Stall Diagnosis` — Read-only diagnosis of Stage 4 harvester stall, disk/cursor gap reconciliation, bare exception analysis, and §26.1 correction  
**Model:** Gemini 3.7 Flash (High)  
**Topic:** Diagnose why Stage 4 log capture stalled for 65 minutes with high CPU consumption, reconcile on-disk log files vs `cursor.db` records, count jobs dropped by bare exception handlers in `_build_log_worklist`, correct the §26.1 holdout draft claim in session 054, and propose a design fix for Stage 4 without modifying source code.

---

## 1. Task Statement & Guard Outputs

Stage 4 cursor progress stalled at 5,874 from 16:53 to 17:58 (65 minutes) with the daemon consuming CPU and `logs/supervisor_*.log` remaining silent despite `PYTHONUNBUFFERED=1`. This session performed a strict read-only diagnosis without signaling or restarting the running daemon process.

### Guard Output

```bash
$ uname -s && pwd && uv run python --version
Linux
/home/shree/blastradius
Python 3.11.15

$ git log -1 --format='%H %s'
a90e36bbe8166142473965e4d6b207144c49f005 test: rebuild the holdout so most of its logs actually fail

$ git config user.name && git config user.email
DeepanshuOP
99538840+DeepanshuOP@users.noreply.github.com

$ git status --short
?? src/parse/log_maven.py
?? tests/test_log_maven.py
?? vendor/graphify-br/

$ ps aux | grep '[h]arvest\.daemon'
shree       1676  0.0  0.4 219360 33408 ?        Sl   02:11   0:00 uv run --env-file .env python -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage 4
shree       1679  2.1  1.4 123580 116236 ?       S    02:11   5:19 /home/shree/blastradius/.venv/bin/python3 -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage 4

$ ps -o pid,lstart,etime,cmd -p 1676,1679
    PID                  STARTED     ELAPSED CMD
   1676 Thu Aug 27 02:11:04 2026    04:02:35 uv run --env-file .env python -m sr
   1679 Thu Aug 27 02:11:04 2026    04:02:35 /home/shree/blastradius/.venv/bin/p
```

---

## 2. STEP 1 — Execution Path & Startup Cost Before First Capture

### Function Traversal
Before `capture_job_logs()` issues its first HTTP request via `_fetch_job_log()`:
1. `capture_job_logs()` invokes `_build_log_worklist(repo_fulls, store=store, cursor=cursor, now=now)`.
2. For each repository in the 300-repo frame, `_build_log_worklist()` calls `_collect_repo_shas()`.
3. `_collect_repo_shas()` calls `_iter_captured_pr_numbers()`, reading all `pulls` listing `.jsonl.gz` pages from disk and parsing JSON.
4. For every captured PR, `_collect_repo_shas()` queries `cursor.get_capture_unit(repo, 'pull_commits', pr_number)` and reads `pull_commits` `.jsonl.gz` files from disk, decompressing and JSON-decoding all commit records.
5. `_build_log_worklist()` then iterates over every discovered commit `sha`:
   - Queries `cursor.get_capture_unit(repo, 'runs', sha)`.
   - Reads `runs` `.jsonl.gz` records from disk and parses JSON.
   - For every workflow run, parses run timestamps.
   - Queries `cursor.get_capture_unit(repo, 'jobs', run_id)`.
   - Reads `jobs` `.jsonl.gz` records from disk, parses JSON, and filters for `job.get("conclusion") == "failure"`.
6. Finally, `_build_log_worklist()` executes two sorting passes over the entire aggregated list.

### Answers to Specific Questions

- **(a) Read sources and path counts:** `_build_log_worklist` reads from **both** `cursor.db` (via SQLite queries) and `data/raw/` files on disk. For the 300-repo frame, it touches, decompresses, and parses **188,141 `.jsonl.gz` files**:
  - `pulls`: 165 files read
  - `pull_commits`: 13,282 files read
  - `runs`: 42,874 files read
  - `jobs`: 131,820 files read
  - Total raw files opened: **188,141**
- **(b) Caching:** The worklist is **rebuilt completely from scratch** on every daemon startup. There is zero disk or database caching of the constructed worklist.
- **(c) Process silence:** Between process startup and the completion of all worklist units, **NOTHING is printed to stdout or stderr**. `_build_log_worklist` contains no log statements, and `capture_job_logs()` only emits a summary print (`STAGE4: worklist=...`) at the very end of its execution loop in `run()`.
- **(d) Benchmark Timing (without HTTP):**
  Measured via `/tmp/diagnose_stage4_full.py` with read-only SQLite URI (`mode=ro`):
  - **Elapsed time:** `204.08s` (~3.4 minutes of continuous CPU disk decompression / JSON parsing).
  - **Worklist length:** `18,269` failed job units.

---

## 3. STEP 2 — Disk vs Cursor Conservation Reconciliation

We conducted a full reconciliation comparing on-disk log files (`pathlib.Path('data/raw').glob('*/job/*/*/logs.jsonl.gz')`) against `cursor.db` rows for `kind='logs'`.

```
=== STEP 2: DISK / CURSOR GAP RECONCILIATION ===
Total log files on disk (glob '*/job/*/*/logs.jsonl.gz'): 8986
Cursor counts for kind='logs' by status:
  complete: 8986
  failed: 1377
  in_flight: 12

On-disk log files with NO cursor row: 0
On-disk log files with cursor status != 'complete': 0
Cursor 'complete' rows with NO on-disk file: 0
```

### Gap Analysis & Conservation Verification
- **Conservation Result:** Exact **1:1 match** between on-disk files (8,986) and cursor rows with `status = 'complete'` (8,986).
- **0 orphan files:** There are zero on-disk files without a corresponding cursor row, and zero on-disk files marked with non-complete status.
- **Explanation of Earlier Perceived Gap (6,259 on disk vs 5,874 cursor):**
  In earlier sessions, the pool scan counted on-disk files at a different point in time while the live background daemon was actively fetching and committing units. When `_fetch_job_log()` executes, `store.write_records()` writes the gzip file, immediately followed by `cursor.mark_unit_complete()`. Because SQLite WAL mode commits synchronously within the daemon, disk state and cursor state remain strictly synchronized.

---

## 4. STEP 3 — Bare Exception Handlers Audit in `_build_log_worklist`

We instrumented a verbatim diagnostic copy of `_build_log_worklist` in `/tmp/diagnose_steps2_and_3.py` to count dropped jobs across all 300 repositories:

```
=== STEP 3: BARE EXCEPT HANDLERS DROPPED JOBS COUNT ===
Runs JSON parse errors (Handler 1, line 984): 0
Timestamp parse errors (Handler 2, line 996): 0
Jobs JSON parse errors (Handler 3, line 1007): 0
Total failed jobs discovered in worklist: 18269
Total failed jobs dropped by corrupt JSON handlers: 0 (0.0%)
```

**Result:** Zero records in the dataset are corrupt, so zero jobs are dropped by the exception handlers.

---

## 5. Root Cause Analysis of the 65-Minute Stall

Two distinct factors combined to produce the observed stall from 16:53 to 17:58:

1. **Startup Overhead (3.4 minutes):**
   On startup, `_build_log_worklist` spent 204.08 seconds decompressing 188,141 `.jsonl.gz` files and performing cursor lookups at 100% CPU with zero terminal output.

2. **Massive Individual HTTP Downloads & Retry Loops (60+ minutes):**
   Inspection of `logs/requests.jsonl` revealed that downloading raw log payloads for certain large jobs encounters massive multi-gigabyte or streaming payloads from GitHub's Azure blob redirects:
   - **`sirixdb/sirix` job `86522325214`:**
     - Attempt 1 on 2026-08-26T17:28:59: duration **2,211,857 ms (36.86 minutes)** for a single HTTP 200 stream.
     - Follow-up attempt on 2026-08-26T17:58:39: duration **787,262 ms (13.12 minutes)** before throwing a `ConnectionError`.
     - Additional retry attempts (2 through 6) consumed further time before failing transiently.
   - Because `requests.get()` in `get_with_backoff` lacked a socket streaming timeout/size ceiling, a single giant log download stalled the single-threaded harvester for over 36 minutes per attempt.
   - Because Stage 4 lacked per-unit heartbeat logging, the daemon burned CPU decompressing / streaming while appearing completely hung to external supervisors.

---

## 6. STEP 4 — Corrected ROADMAP §26.1 Draft Claim

In `docs/session/054-2026-08-26-holdout-stratified-rebuild.md`, Section 7 has been updated to accurately reflect the timeline and quarantine status:

> To validate parser precision and recall on unseen executions without overfitting to the development corpus, we constructed an out-of-sample held-out fixture set of 20 raw GitHub Actions logs on 2026-08-26, drawn deterministically with failure stratification across 14 repositories (including 6 repositories absent from initial training fixtures). The set comprises 15 failure-bearing logs spanning Maven, Gradle, and Pytest harnesses (containing 30 canonical test identifiers and 37 harness-reported failure events) and 5 non-failing logs. Ground truth failure sets were hand-labelled by human inspection directly from raw log text before any held-out evaluation, and independently cross-checked against native harness summary outputs (`expected_audit.py`, achieving 75.0% summary checkability with zero ground-truth omissions). The set was constructed after the Gradle and Maven parsers were finalized, from logs no one had previously inspected during parser development, and was quarantined from the Pytest parser's development, which was ongoing at the time of construction.

---

## 7. Design Proposal for Stage 4 Optimization (No Code Changes)

To eliminate the startup stall and prevent single-download hangs:

1. **Incremental / Heartbeat Progress Logging:**
   - Add explicit logging during worklist construction (e.g. `[stage4] scanning rawstore: repo 50/300...`).
   - Add per-unit or periodic progress logging during log fetching (e.g. `[stage4] (120/18269) fetched job 91912888981 (apache/beam) 1.2MB in 1.4s (complete=115 failed=5)`).
2. **Per-Request Timeout & Size Guard on Log Downloads:**
   - In `_fetch_job_log`, configure streaming mode with a strict read timeout (e.g. 60s) and a maximum log byte ceiling (e.g. 50MB) to abort out-of-bounds streams rather than blocking for 36+ minutes.
3. **Cursor-Driven Worklist Construction:**
   - Rather than traversing 188,141 `.jsonl.gz` files from disk on every startup, index failed job IDs into a dedicated metadata table or query `cursor.db` directly, reducing startup time from 204 seconds to under 2 seconds.

---

## 8. Non-Goals Honored

- Strictly read-only diagnosis: no modifications to `src/harvest/`, `src/parse/`, `tests/`, or `analysis/`.
- Did NOT signal, kill, or restart background daemon PID 1676/1679.
- Did NOT modify `cursor.db`, `data/`, `logs/`, `docs/DECISIONS.md`, `docs/HANDOFF.md`, or `ROADMAP.md`.
- All temporary scripts were placed under `/tmp/` and executed in read-only mode (`mode=ro`).
- Preserved untracked work from Terminal B (`src/parse/log_maven.py`, `tests/test_log_maven.py`, `vendor/graphify-br/`).

---

## 9. Files Changed & Line Counts

- `docs/session/054-2026-08-26-holdout-stratified-rebuild.md` (220 lines): Corrected §26.1 holdout quarantine claim.
- `docs/session/055-2026-08-26-stage4-stall-diagnosis.md` (this file, 168 lines): Full diagnostic report.
- `docs/session/INDEX.md`: Added sequence row 055.
