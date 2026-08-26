# Session Report: Fix Artifact Size Cap and Isolate Daemon Lock in Tests

**Task ID:** Post-T0.3d Defect Remediation & T1.1b Commit
**Date:** 2026-08-26
**Author:** Terminal A
**Target File:** docs/session/052-2026-08-26-artifact-cap-and-lock-isolation.md

---

## 1. Task Statement & Defect Post-Mortem

### Task Statement
Fix the artifact download size cap in `src/harvest/artifacts.py` to 300 MB based on measured corpus data; make the daemon lock path cleanly injectable and dynamically resolved so that tests run isolated from the live harvester daemon; ensure the test suite is 100% green while the Stage 4 daemon is actively running; and land Terminal A's fixes and Terminal B's completed Gradle build log parser in two separate commits.

### Prior Interruption Reconciliation
The previous session was killed mid-task by a WSL2 VM teardown while writing the session report. On resumption:
- Files modified on disk: `src/harvest/artifacts.py`, `src/harvest/daemon.py`, `tests/test_artifacts.py`, `tests/test_daemon.py`, and `src/parse/__init__.py` (from Terminal B).
- Untracked files on disk: `src/parse/log_gradle.py`, `src/parse/outcome.py`, `tests/test_log_gradle.py`.
- All modifications were examined via `git diff` and confirmed COMPLETE and syntactically sound, with successful module imports.

### Defect 1: Artifact Size Cap Rejected Target Artifact (240.6 MB vs 150 MB Cap)
- **Defect:** In session 051, `DEFAULT_MAX_ARTIFACT_SIZE_BYTES` was set to 150 MB based on an unsourced "~90 MB" estimate from an earlier log inspection without measuring the exact uploaded byte count. In reality, the largest observed HBase artifact in `tests/fixtures/logs/apache__hbase__082907939305.txt:4681` was:
  ```
  2026-06-23T10:02:17.6947779Z Artifact yetus-jdk17-hadoop3-unit-check-large-wave-3 has been successfully uploaded! Final size is 252250140 bytes. Artifact ID is 7817569118
  ```
  `252,250,140 bytes` = `240.56 MB`. Under the 150 MB cap, T0.3d would have silently skipped the largest of the four HBase test artifacts it was built to rescue. The "~90 MB" figure from session 051 was never measured.
- **Remediation:** Raised `DEFAULT_MAX_ARTIFACT_SIZE_BYTES` to 300 MB (`300 * 1024 * 1024` bytes). Documented the measured justification citing the exact fixture and line number (`apache__hbase__082907939305.txt:4681`). Added code comments explicitly clarifying that this cap bounds temporary download bandwidth and in-memory extraction cost—not persistent disk storage—because raw zip archives are discarded immediately after selective test result extraction. Added unit test asserting that all 4 measured HBase sizes pass under the default filter.

### Defect 2: Committed and Pushed with Red Test Suite (Unisolated Daemon Lock)
- **Defect:** `test_main_exits_cleanly_on_all_tokens_dead` and `test_main_all_tokens_dead_leaves_units_in_flight` invoked `daemon.main()` without overriding `lock_path`. `daemon.main()` attempted to acquire `logs/daemon.lock`, which is held by the live Stage 4 harvester daemon process (PID 1679). The flock failed as expected, causing `main()` to exit early with code 0 ("another daemon instance is already running"), failing pytest assertions.
- **Remediation:** Updated `acquire_daemon_lock`, `read_lock_holder`, and `main` in `src/harvest/daemon.py` to accept `lock_path: Path | str | None = None` and resolve dynamically to `DEFAULT_LOCK_PATH` when None. Updated `_setup_all_tokens_dead_run` in `tests/test_daemon.py` to monkeypatch `DEFAULT_LOCK_PATH` to `tmp_path / "daemon.lock"` and passed `lock_path=tmp_path / "daemon.lock"` explicitly in the test calls. Confirmed all tests run completely isolated and green while the live daemon runs.

---

## 2. Guard & Environment Verification

### Commands & Raw Output:
```bash
uname -s && pwd && uv run python --version
```
```
Linux
/home/shree/blastradius
Python 3.11.15
```

```bash
git log -1 --format='%H %s' && git config user.name && git config user.email && git status --short && ps aux | grep '[h]arvest\.daemon'
```
```
86725673b2e1a16f2e764df7bbd97f47ebd66b70 feat: fetch the test result files that ci uploads as artifacts
DeepanshuOP
99538840+DeepanshuOP@users.noreply.github.com
 M src/harvest/artifacts.py
 M src/harvest/daemon.py
 M src/parse/__init__.py
 M tests/test_artifacts.py
 M tests/test_daemon.py
?? src/parse/log_gradle.py
?? src/parse/outcome.py
?? tests/test_log_gradle.py
?? vendor/graphify-br/
shree       1676  0.0  0.4 219360 33408 ?        Sl   17:43   0:00 uv run --env-file .env python -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage 4
shree       1679 46.2  1.1 107144 92168 ?        D    17:43   0:40 /home/shree/blastradius/.venv/bin/python3 -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage 4
```

---

## 3. Measured Artifact Sizing

Empirical size measurements across all four HBase fixtures in `tests/fixtures/logs/`:
1. `tests/fixtures/logs/apache__hbase__078892029185.txt:4636`: `yetus-jdk17-hadoop3-unit-check-large-wave-2` -> `102597177 bytes` (~97.8 MB)
2. `tests/fixtures/logs/apache__hbase__082907939305.txt:4681`: `yetus-jdk17-hadoop3-unit-check-large-wave-3` -> `252250140 bytes` (~240.6 MB)
3. `tests/fixtures/logs/apache__hbase__083382132597.txt:1801`: `yetus-jdk8-hadoop2-unit-check-small` -> `7526 bytes` (~7.4 KB)
4. `tests/fixtures/logs/apache__hbase__084057821217.txt:3847`: `yetus-jdk11-hadoop3-unit-check-large-wave-1` -> `43053738 bytes` (~41.1 MB)

Under `DEFAULT_MAX_ARTIFACT_SIZE_BYTES = 300 * 1024 * 1024` (300 MB / 314,572,800 bytes), all four measured HBase artifacts pass the size filter.

---

## 4. Test Verification & Predictions

### Pre-test Prediction:
- Baseline: 255 collected (including Terminal B's 10 Gradle parser tests and 8 artifact tests).
- Added 1 unit test in `tests/test_artifacts.py` (`test_filter_test_artifacts_measured_hbase_sizes_pass_default_cap`).
- Predicted Total: 256 passed, 0 failed.

### Command:
```bash
uv run python -c "import src.harvest.daemon; print('daemon imports')" && uv run pytest -q
```

### Raw Output:
```
daemon imports
........................................................................ [ 28%]
........................................................................ [ 56%]
........................................................................ [ 84%]
........................................                                 [100%]
256 passed in 4.89s
```

### Daemon Process Status Check:
```bash
ps aux | grep '[h]arvest\.daemon'
```
```
shree       1676  0.0  0.4 219360 33408 ?        Sl   17:43   0:00 uv run --env-file .env python -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage 4
shree       1679 48.6  0.8  76564 68044 ?        R    17:43   1:01 /home/shree/blastradius/.venv/bin/python3 -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage 4
```

---

## 5. Changes Summary

### Files Touched (Terminal A Remediation):
- `src/harvest/artifacts.py`: Raised `DEFAULT_MAX_ARTIFACT_SIZE_BYTES` to 300 MB with measured justification and storage budget comment.
- `src/harvest/daemon.py`: Made `lock_path` dynamically resolved to `DEFAULT_LOCK_PATH` when None.
- `tests/test_artifacts.py`: Updated tests for 300 MB cap and added `test_filter_test_artifacts_measured_hbase_sizes_pass_default_cap`.
- `tests/test_daemon.py`: Isolated daemon lock to `tmp_path` in `test_main_exits_cleanly_on_all_tokens_dead` and `test_main_all_tokens_dead_leaves_units_in_flight`.
- `docs/session/052-2026-08-26-artifact-cap-and-lock-isolation.md`: Session report.
- `docs/session/INDEX.md`: Updated index table.

### Files Touched (Terminal B Staging):
- `src/parse/outcome.py`: Structured test outcome dataclass.
- `src/parse/log_gradle.py`: Gradle test failure parser.
- `src/parse/__init__.py`: Package export updates.
- `tests/test_log_gradle.py`: Contract tests against real log fixtures.

### Non-Goals Honoured:
- Contents of `src/parse/` and `tests/test_log_gradle.py` were not modified.
- `docs/DECISIONS.md`, `docs/HANDOFF.md`, `ROADMAP.md`, `data/`, `logs/`, and `cursor.db` were not touched.
- No HTTP calls outside `get_with_backoff`.
- Running daemon process was not interrupted or signaled.
