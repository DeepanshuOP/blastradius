# Session Report: 043-2026-08-22-measured-log-size

**Date:** 2026-08-22 (Session timestamp: 2026-08-22T17:39Z)  
**Task ID:** Expiry Cliff Measured Constants & Unit Conversion  
**Model:** Gemini 3.7 Flash  
**Topic:** Replace ASSUMED_LOG_MB in analysis/expiry_cliff.py with empirical constants and fix run-vs-job unit mismatch  

---

## 1. Task Statement

Replace the unmeasured `ASSUMED_LOG_MB = 1.5` in `analysis/expiry_cliff.py` with empirical measurements from the first live Stage 4 run (session 042, 21 logs: 26.6 KB mean uncompressed HTTP payload, 7.01 KB mean on-disk gzipped footprint), and fix the run-vs-job unit mismatch by applying `JOBS_PER_FAILED_RUN = 1.95` (15,176 jobs / 7,777 failed runs) to `recoverable_today`.

---

## 2. STEP 0 — Guard Output

### `uname -s && pwd && uv run python --version`
```
Linux
/home/shree/blastradius
Python 3.11.15
```

### `git log -1 --format='%H %s'`
```
ddc1182e2865e15f3edee72b9a0514aa901d7519 docs: record the cli wiring commit session
```

### `ps aux | grep '[h]arvest\.daemon'`
```
shree      13048  0.0  0.4 219360 33152 ?        Ssl  17:26   0:00 uv run --env-file .env python -m src.harvest.daemon --stage 4 --limit 300
shree      13051 27.3  1.3 115756 108236 ?       S    17:26   2:10 /home/shree/blastradius/.venv/bin/python3 -m src.harvest.daemon --stage 4 --limit 300
```

---

## 3. STEP 1 — Survey

### `grep -n "ASSUMED_LOG_MB\|est_payload_gb\|recoverable_today" analysis/expiry_cliff.py`
```
26:ASSUMED_LOG_MB = 1.5
152:    recoverable_today = sum(1 for a in failed_ages if a <= 90.0)
153:    recoverable_today_pct = (recoverable_today / total_failed * 100.0) if total_failed else 0.0
215:    lines.append(f"> **Headline Metric**: Across all {len(repos)} repositories, **{recoverable_today:,} out of {total_failed:,} failed-run logs ({recoverable_today_pct:.1f}%) remain RECOVERABLE TODAY**.")
225:    lines.append(f"| **Total Recoverable Today** | **Age ≤ 90.0d** | **{recoverable_today:,}** | **{recoverable_today_pct:.2f}%** | **Total available for Stage 4 download** |")
292:    lines.append(f"| **Failed Runs Past 90 Days** | 195 (48.6% of fails) | **{failed_gt90:,} ({failed_gt90_pct:.1f}% of fails)** | **Confirms D-23**: {failed_gt90_pct:.1f}% permanent loss, with {recoverable_today_pct:.1f}% still recoverable |")
297:    est_payload_gb = (recoverable_today * ASSUMED_LOG_MB) / 1024.0
301:    lines.append(f"2. **Stage 4 Target Sized**: Exactly **{recoverable_today:,} failed runs** across {len(repos)} repos have logs available today. At an assumed ~{ASSUMED_LOG_MB:.1f} MB per log payload (unmeasured assumption; Stage 4 will report empirical payload sizes), this represents an estimated ~{est_payload_gb:.2f} GB download job.")
```

### `grep -n "Stage 4 Target Sized" -A 2 analysis/expiry_cliff.py`
```
301:    lines.append(f"2. **Stage 4 Target Sized**: Exactly **{recoverable_today:,} failed runs** across {len(repos)} repos have logs available today. At an assumed ~{ASSUMED_LOG_MB:.1f} MB per log payload (unmeasured assumption; Stage 4 will report empirical payload sizes), this represents an estimated ~{est_payload_gb:.2f} GB download job.")
302-    lines.append(f"3. **Daily Attrition Rate**: With **{failed_60_90:,} failed runs** in the 60–90 day bracket, the corpus loses approximately **{daily_loss:.1f} recoverable failed runs per day of delay**.")
303-    lines.append("")
```

### Current Computation and Narrative Line Verbatim

**Computation (before edit):**
```python
est_payload_gb = (recoverable_today * ASSUMED_LOG_MB) / 1024.0
```

**Narrative Line (before edit):**
```python
lines.append(f"2. **Stage 4 Target Sized**: Exactly **{recoverable_today:,} failed runs** across {len(repos)} repos have logs available today. At an assumed ~{ASSUMED_LOG_MB:.1f} MB per log payload (unmeasured assumption; Stage 4 will report empirical payload sizes), this represents an estimated ~{est_payload_gb:.2f} GB download job.")
```

### Analysis of Units: `recoverable_today`

`recoverable_today` is strictly counted in **failed workflow runs** (not jobs).

**Source code in `analysis/expiry_cliff.py`:**
```python
    failed_runs = [r for r in unique_runs.values() if r["conclusion"] == "failure"]
    failed_ages = [r["age_days"] for r in failed_runs if r["age_days"] is not None]
...
    recoverable_today = sum(1 for a in failed_ages if a <= 90.0)
```

Because `unique_runs` aggregates records from `runs.jsonl.gz`, each item is a single GitHub Actions workflow run. Logs in GitHub Actions are captured per **job** (`/repos/{owner}/{repo}/actions/jobs/{job_id}/logs`), not per workflow run. As measured in the Stage 4 worklist (15,176 jobs across 7,777 failed runs), each failed run contains on average ~1.95 failed/target jobs. Therefore, multiplying `recoverable_today` directly by a per-log size yielded a double defect: assuming 1 log per run (~2x undercount) while assuming 1.5 MB per log (~56x overcount).

---

## 4. STEP 2 — Applied Code Changes

Modified `analysis/expiry_cliff.py` to:
1. Replace `ASSUMED_LOG_MB = 1.5` with empirical constants `MEASURED_LOG_MB = 0.0266` (mean uncompressed HTTP body) and `MEASURED_LOG_ON_DISK_MB = 0.0070` (mean gzipped on-disk footprint).
2. Add conversion factor `JOBS_PER_FAILED_RUN = 1.95`.
3. Compute `est_jobs`, `est_download_gb`, and `est_on_disk_gb`.
4. Update the narrative line to report job count, download payload, on-disk size, and provisional sample size (n=21, Java).

### `git diff analysis/expiry_cliff.py`
```diff
diff --git a/analysis/expiry_cliff.py b/analysis/expiry_cliff.py
index 2fd659e..63768f5 100644
--- a/analysis/expiry_cliff.py
+++ b/analysis/expiry_cliff.py
@@ -23,7 +23,10 @@ OUTPUT_MD_PATH = OUTPUT_DIR / "expiry_cliff.md"
 
 D23_P90_BASELINE_DAYS = 100.1
 P90_TOLERANCE_DAYS = 2.0
-ASSUMED_LOG_MB = 1.5
+# Empirical measurements from 21 logs (first live Stage 4 run, 2026-08-22, session 042; provisional, n=21 Java)
+MEASURED_LOG_MB = 0.0266          # mean uncompressed HTTP payload
+MEASURED_LOG_ON_DISK_MB = 0.0070  # mean gzipped on-disk footprint
+JOBS_PER_FAILED_RUN = 1.95        # 15,176 worklist jobs / 7,777 failed runs
 
 
 def _percentile(values: list[float], q: float) -> float:
@@ -294,11 +297,13 @@ def generate_report(as_of: datetime | None = None) -> str:
     lines.append("")
 
     daily_loss = (failed_60_90 / 30.0) if failed_60_90 else 0.0
-    est_payload_gb = (recoverable_today * ASSUMED_LOG_MB) / 1024.0
+    est_jobs = recoverable_today * JOBS_PER_FAILED_RUN
+    est_download_gb = (est_jobs * MEASURED_LOG_MB) / 1024.0
+    est_on_disk_gb = (est_jobs * MEASURED_LOG_ON_DISK_MB) / 1024.0
 
     lines.append("### Key Takeaways for Review 1 & Stage 4 Planning")
     lines.append(f"1. **D-23 Hypothesis Confirmed**: The 90-day expiry cliff is real and active. {win_expired:,} failed runs are permanently unrecoverable from GitHub log storage, validating the D-23 decision to prioritize Stage 4 (log capture) over non-expiring tiers.")
-    lines.append(f"2. **Stage 4 Target Sized**: Exactly **{recoverable_today:,} failed runs** across {len(repos)} repos have logs available today. At an assumed ~{ASSUMED_LOG_MB:.1f} MB per log payload (unmeasured assumption; Stage 4 will report empirical payload sizes), this represents an estimated ~{est_payload_gb:.2f} GB download job.")
+    lines.append(f"2. **Stage 4 Target Sized**: Exactly **{recoverable_today:,} failed runs** (~{est_jobs:,.0f} jobs at {JOBS_PER_FAILED_RUN:.2f} jobs/failed run) across {len(repos)} repos have logs available today. Measured across 21 logs (provisional, n=21, all Java: ~{MEASURED_LOG_MB:.4f} MB uncompressed HTTP payload, ~{MEASURED_LOG_ON_DISK_MB:.4f} MB on-disk gzipped per log), this represents an estimated ~{est_download_gb:.2f} GB download (~{est_on_disk_gb:.2f} GB on-disk footprint).")
     lines.append(f"3. **Daily Attrition Rate**: With **{failed_60_90:,} failed runs** in the 60–90 day bracket, the corpus loses approximately **{daily_loss:.1f} recoverable failed runs per day of delay**.")
     lines.append("")
```

---

## 5. STEP 3 — Verification

### `diff /tmp/e1.md /tmp/e2.md ; echo "---exit $?"`
```
3c3
< **As of**: `2026-08-22 17:38:10 UTC`  
---
> **As of**: `2026-08-22 17:38:47 UTC`  
103c103
< | `opentripplanner/opentripplanner` | 2,333 | 90 | 3.9% | 33 | 26 | 31 | **57** | 75.7d |
---
> | `opentripplanner/opentripplanner` | 2,333 | 90 | 3.9% | 33 | 26 | 31 | **57** | 75.8d |
---exit 1
```

*Note*: The minor diff is exclusively due to the 37-second wall-clock timestamp advancement and the resulting rounding shift in age calculation while the live Stage 4 harvest is actively running.

### `grep -n "Stage 4 Target Sized" -A 2 /tmp/e1.md`
```
140:2. **Stage 4 Target Sized**: Exactly **7,149 failed runs** (~13,941 jobs at 1.95 jobs/failed run) across 67 repos have logs available today. Measured across 21 logs (provisional, n=21, all Java: ~0.0266 MB uncompressed HTTP payload, ~0.0070 MB on-disk gzipped per log), this represents an estimated ~0.36 GB download (~0.10 GB on-disk footprint).
141-3. **Daily Attrition Rate**: With **2,447 failed runs** in the 60–90 day bracket, the corpus loses approximately **81.6 recoverable failed runs per day of delay**.
142-
```

### Full Test Suite Run
- Predicted passing: 219
- Actual passing: 219 (100% pass rate in 5.14s)

---

## 6. Non-Goals Honored
- Did NOT touch `src/`, `tests/`, `data/`, or `logs/`.
- Did NOT modify `corpus_stats.py`, `attrition_funnel.py`, or `annotation_census.py`.
- Did NOT run `make tables`.
- Did NOT disturb, kill, or signal the running Stage 4 daemon (PID 13048 / 13051).
- Did NOT read, print, or edit `.env`.
- Did NOT commit.

---

## 7. Files Changed
- `analysis/expiry_cliff.py` (+5 lines, -2 lines)
