# Session Report: 048-2026-08-26-daemon-single-instance

**Date:** 2026-08-26  
**Task ID:** Parameterise supervisor, in-daemon flock single-instance lock, and land pending work  
**Model:** Gemini 3.7 Flash  

---

## 1. Task Statement

1. Resolve the `.gitignore` pattern change (`logs/` -> `/logs/`) uncommitted across four rounds and document the §9 deviation-check miss.
2. Parameterise `run_supervised.sh` with `STAGE="${1:-4}"`, echoing the resolved stage and retaining the global supervisor lock.
3. Move the duplicate-daemon lock directly into `src/harvest/daemon.py` using non-blocking advisory kernel flock (`fcntl.flock`) on `logs/daemon.lock` inside `main()`, exiting cleanly (0) if another instance is running.
4. Add unit tests for flock mutual exclusion, kernel release on SIGKILL, clean exit 0 on duplicate start, and `run_supervised.sh` argument resolution.
5. Report on `AllTokensDead` exit code distinction and in-flight sirix capture units.
6. Land changes across three clean logical commits without touching non-goals or `docs/HANDOFF.md`.

---

## 2. Guard Commands and Raw Output

```bash
$ uname -s && pwd && uv run python --version
Linux
/home/shree/blastradius
Python 3.11.15

$ git log -1 --format='%H %s'
7050023babcd846b8adc94026b4e9ee8f2b0acec fix: stop one bad log write from killing the capture daemon

$ git config user.name && git config user.email
DeepanshuOP
99538840+DeepanshuOP@users.noreply.github.com

$ git status --short
 M .gitignore
 M analysis/log_yield.py
?? analysis/fixture_score.py
?? docs/session/049-2026-08-26-extractor-precision.md
?? tests/test_log_yield.py
?? vendor/graphify-br/

$ ps aux | grep '[h]arvest\.daemon'
(exit code 1 - no running daemon)
```

---

## 3. `.gitignore` Resolution & §9 Deviation Record (STEP 1)

### (a) Root Cause & Provenance of Change
During task T1.1a (session 046, commit `2955b00`), the fixture corpus was added under `tests/fixtures/logs/`. The repository's unanchored `.gitignore` rule `logs/` matched any directory named `logs`, inadvertently ignoring `tests/fixtures/logs/`. An agent modified `.gitignore` from `logs/` to `/logs/` to unblock staging `tests/fixtures/logs/`, but failed to disclose this modification or stage it with commit `2955b00`. It sat uncommitted across sessions 046 and 047 while appearing in every guard output.

Per ROADMAP §9, this was an undisclosed deviation-check miss. The change is formally documented here and committed in this round.

```bash
$ git log --oneline -1 -- tests/fixtures/logs/
2955b00 test: add the hand-labelled forty-log fixture corpus
```

### (b) Visibility Verification
```bash
$ git ls-files --others --exclude-standard | head -40
analysis/fixture_score.py
docs/session/049-2026-08-26-extractor-precision.md
tests/test_log_yield.py
vendor/graphify-br/

$ find . \( -path './.git' -o -path './data' -o -path './logs' \) -prune -o -type d -name logs -print
./tests/fixtures/logs
./vendor/graphify-br/.git/logs
```
No data files or credential-bearing files became visible.

### (c) Root Logs Directory Ignore Confirmation
```bash
$ git check-ignore -v logs/requests.jsonl logs/stage4.log
.gitignore:4:/logs/	logs/requests.jsonl
.gitignore:4:/logs/	logs/stage4.log
```
Root-level log files remain strictly ignored by line 4 (`/logs/`).

---

## 4. Supervisor Parameterisation & Exit Code Analysis (STEP 2)

### (a) `run_supervised.sh` Updates
- Added `STAGE="${1:-4}"` to default execution to Stage 4 (log capture).
- Passed `--stage "$STAGE"` to the daemon invocation.
- Updated logging line to:
  `echo "[supervisor] $(date -u +%FT%TZ) starting daemon (stage $STAGE)"`
- Preserved single global lockfile `logs/supervisor.pid`.

### (b) `AllTokensDead` Exit Code Analysis
In `src/harvest/daemon.py`:
```python
    except AbortRun as exc:
        print(f"ABORTED: {exc}")
        raise SystemExit(1) from exc
    except AllTokensDead as exc:
        print("ABORTED: dead credentials — every token evicted, check .env", file=sys.stderr)
        raise SystemExit(1) from exc
```
- **Finding:** The daemon currently exits with code `1` on `AllTokensDead`, which is identical to `AbortRun` or unhandled exceptions.
- **Impact on Supervisor:** Because exit code 1 is not differentiated, `run_supervised.sh` treats `AllTokensDead` as a general exit and sleeps 120 seconds before attempting to relaunch against exhausted credentials. (Per instructions, backoff logic is deferred to a separate deliverable).

---

## 5. In-Daemon Single-Instance Lock (STEP 3)

### Implementation in `src/harvest/daemon.py`:
- Defined `DEFAULT_LOCK_PATH = Path("logs/daemon.lock")`.
- Implemented `acquire_daemon_lock(lock_path)` using `fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)`:
  - Ensures `logs/` directory exists (`path.parent.mkdir(parents=True, exist_ok=True)`).
  - Writes PID to the file for operator diagnostics, but relies exclusively on the kernel-held `flock` descriptor.
- Implemented `read_lock_holder(lock_path)` to extract PID of the active process.
- Implemented `release_daemon_lock(fd)` for clean unlocked close.
- Integrated into `main()`:
  - Executes inside `main()` prior to initializing `TokenPool`, `RawStore`, or `CursorStore`.
  - If lock is held, prints `[daemon] another daemon instance is already running (PID ...); exiting cleanly (0)` and returns immediately with exit code 0.
  - Automatically cleaned up in `finally:` block and by the OS kernel on termination/SIGKILL.

---

## 6. Verification and Test Results (STEP 4)

### New Unit Tests in `tests/test_daemon.py`:
1. `test_daemon_flock_mutual_exclusion_and_release`: Proves subprocess lock acquisition blocks parent, and parent succeeds once subprocess terminates.
2. `test_daemon_flock_released_on_sigkill`: Proves that killing the lock holder with `SIGKILL` causes the kernel to immediately release the flock, allowing immediate acquisition.
3. `test_daemon_main_exits_cleanly_when_lock_already_held`: Proves `main()` exits 0 with a clear log message when the lock is occupied.
4. `test_run_supervised_argument_resolution`: Validates bash syntax (`bash -n`) and verifies argument resolution defaults to "4" while passing explicit arguments ("both", "1").

### In-Flight Sirix Units Check:
```bash
$ uv run python -c "import sqlite3; c=sqlite3.connect('file:data/state/cursor.db?mode=ro',uri=True); [print(r) for r in c.execute("SELECT * FROM capture_unit WHERE kind='logs' AND status='in_flight'")]"
('sirixdb/sirix', 'logs', '86522325214', 'in_flight', 29143964837, '2026-08-25T18:18:30.002414+00:00', None, None)
('sirixdb/sirix', 'logs', '86526226143', 'in_flight', 29145434199, '2026-08-25T21:22:06.466686+00:00', None, None)
```
Status: Both units remain in `in_flight` state and will be retried on next Stage 4 run.

### Test Prediction vs Actual:
- **Baseline passing:** 229 (222 from 047 + 7 from Terminal B's uncommitted `test_log_yield.py`)
- **Tests added:** 4
- **Predicted passing:** 233
- **Actual passing:** 233

```bash
$ uv run pytest -q
........................................................................ [ 30%]
........................................................................ [ 61%]
........................................................................ [ 92%]
.................                                                        [100%]
233 passed in 2.73s
```

---

## 7. Files Changed and Line Counts

```bash
$ git diff --stat run_supervised.sh src/harvest/daemon.py tests/test_daemon.py
 run_supervised.sh    |   7 +--
 src/harvest/daemon.py |  51 +++++++++++++++++++++-
 tests/test_daemon.py  |  91 +++++++++++++++++++++++++++++++++++++++
 3 files changed, 143 insertions(+), 6 deletions(-)
```

---

## 8. Non-Goals Honoured

- Did NOT modify the contents of `analysis/log_yield.py`, `analysis/fixture_score.py`, `tests/test_log_yield.py`, or `docs/session/049-2026-08-26-extractor-precision.md` (only staged in commit 3).
- Did NOT touch `tests/fixtures/logs/`.
- Did NOT touch `rawstore.py`, `_build_log_worklist`, `TransientGovernor`, or `TokenPool`.
- Did NOT touch `docs/DECISIONS.md`.
- Did NOT touch `docs/HANDOFF.md`.
- Did NOT touch `cursor.db` or anything under `data/`.
