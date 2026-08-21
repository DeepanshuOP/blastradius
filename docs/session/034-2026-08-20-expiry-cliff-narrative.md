# Session Report 034 — Fix Unfalsifiable Narrative Claims in Expiry Cliff

**Date**: 2026-08-20  
**Model**: Gemini 3.7 Flash  
**Task**: Fix two unfalsifiable narrative claims in `analysis/expiry_cliff.py` (P90 trend branch and assumed log payload size).

---

## 1. Task Statement

Fix two narrative claims in `analysis/expiry_cliff.py` that could not previously be falsified by the underlying data:
1. `p90_trend_str` was an unconditional static string (`"Consistent tail distribution ({all_p90:.1f}d vs 100.1d baseline)"`). Replace with a 3-way branch comparing against the D-23 baseline (`100.1` days) within a tolerance band (`±2.0` days), using named module constants (`D23_P90_BASELINE_DAYS`, `P90_TOLERANCE_DAYS`).
2. `est_payload_gb` multiplied `recoverable_today` by a hardcoded inline `1.5` MB. Hoist `ASSUMED_LOG_MB = 1.5` to a module constant and update the narrative takeaway text to explicitly flag the figure as an unmeasured planning assumption awaiting empirical Stage 4 measurement.

---

## 2. Guard Check (Step 0)

Command:
```bash
uname -s && pwd && uv run python --version
```
Output:
```
Linux
/home/shree/blastradius
Python 3.11.15
```

---

## 3. Read-Only Survey (Step 1)

Command:
```bash
grep -n "p90_trend_str" -B 3 -A 3 analysis/expiry_cliff.py
```
Output:
```
267-    fail_rate_pct = (total_failed / total_unique * 100.0) if total_unique else 0.0
268-    age_delta = 68.3 - all_med
269-    age_trend_str = f"Fresher corpus ({age_delta:.1f} days lower median age)" if age_delta >= 0 else f"Older corpus ({-age_delta:.1f} days higher median age)"
270:    p90_trend_str = f"Consistent tail distribution ({all_p90:.1f}d vs 100.1d baseline)"
271-    exp_trend_str = f"Slightly lower overall expiration rate ({all_gt90_pct:.1f}% vs 19.0%)" if all_gt90_pct <= 19.0 else f"Higher overall expiration rate ({all_gt90_pct:.1f}% vs 19.0%)"
272-
273-    lines.append("## 5. Comparison Against Decision D-23 Baseline")
--
277-    lines.append(f"| **Total Workflow Runs** | 6,212 | **{total_unique:,}** | {scale_runs:.1f}× scale increase |")
278-    lines.append(f"| **Total Failed Runs** | 401 | **{total_failed:,}** | {scale_fails:.1f}× scale increase (failure rate rose from 6.5% to {fail_rate_pct:.1f}%) |")
279-    lines.append(f"| **Overall Median Run Age** | 68.3 days | **{all_med:.1f} days** | {age_trend_str} |")
280:    lines.append(f"| **Overall P90 Run Age** | 100.1 days | **{all_p90:.1f} days** | {p90_trend_str} |")
281-    lines.append(f"| **Runs Past 90 Days** | 1,180 (19.0%) | **{all_gt90:,} ({all_gt90_pct:.1f}%)** | {exp_trend_str} |")
282-    lines.append(f"| **Failed Runs Past 90 Days** | 195 (48.6% of fails) | **{failed_gt90:,} ({failed_gt90_pct:.1f}% of fails)** | **Confirms D-23**: {failed_gt90_pct:.1f}% permanent loss, with {recoverable_today_pct:.1f}% still recoverable |")
283-    lines.append(f"| **Failed Runs in 60–90d Band** | 206 (51.4% of fails) | **{failed_60_90:,} ({failed_60_90_pct:.1f}% of fails)** | **Confirms D-23 urgency**: {failed_60_90:,} failed runs face expiry within 30 days |")
```

Command:
```bash
grep -n "est_payload_gb" -B 3 -A 3 analysis/expiry_cliff.py
```
Output:
```
284-    lines.append("")
285-
286-    daily_loss = (failed_60_90 / 30.0) if failed_60_90 else 0.0
287:    est_payload_gb = (recoverable_today * 1.5) / 1024.0
288-
289-    lines.append("### Key Takeaways for Review 1 & Stage 4 Planning")
290-    lines.append(f"1. **D-23 Hypothesis Confirmed**: The 90-day expiry cliff is real and active. {win_expired:,} failed runs are permanently unrecoverable from GitHub log storage, validating the D-23 decision to prioritize Stage 4 (log capture) over non-expiring tiers.")
291:    lines.append(f"2. **Stage 4 Target Sized**: Exactly **{recoverable_today:,} failed runs** across {len(repos)} repos have logs available today. At ~1.5 MB per log payload, this represents a modest ~{est_payload_gb:.2f} GB download job.")
292-    lines.append(f"3. **Daily Attrition Rate**: With **{failed_60_90:,} failed runs** in the 60–90 day bracket, the corpus loses approximately **{daily_loss:.1f} recoverable failed runs per day of delay**.")
293-    lines.append("")
```

---

## 4. Git Diff (`analysis/expiry_cliff.py`)

Command:
```bash
git diff analysis/expiry_cliff.py
```
Output:
```diff
diff --git a/analysis/expiry_cliff.py b/analysis/expiry_cliff.py
index 2236008..2fd659e 100644
--- a/analysis/expiry_cliff.py
+++ b/analysis/expiry_cliff.py
@@ -21,6 +21,10 @@ RAW_DIR = Path("data/raw")
 OUTPUT_DIR = Path("paper/generated")
 OUTPUT_MD_PATH = OUTPUT_DIR / "expiry_cliff.md"
 
+D23_P90_BASELINE_DAYS = 100.1
+P90_TOLERANCE_DAYS = 2.0
+ASSUMED_LOG_MB = 1.5
+
 
 def _percentile(values: list[float], q: float) -> float:
     """Compute percentile using linear interpolation between closest ranks."""
@@ -267,7 +271,13 @@ def generate_report(as_of: datetime | None = None) -> str:
     fail_rate_pct = (total_failed / total_unique * 100.0) if total_unique else 0.0
     age_delta = 68.3 - all_med
     age_trend_str = f"Fresher corpus ({age_delta:.1f} days lower median age)" if age_delta >= 0 else f"Older corpus ({-age_delta:.1f} days higher median age)"
-    p90_trend_str = f"Consistent tail distribution ({all_p90:.1f}d vs 100.1d baseline)"
+    p90_delta = all_p90 - D23_P90_BASELINE_DAYS
+    if abs(p90_delta) <= P90_TOLERANCE_DAYS:
+        p90_trend_str = f"Consistent tail distribution ({all_p90:.1f}d vs {D23_P90_BASELINE_DAYS:.1f}d baseline)"
+    elif p90_delta < 0:
+        p90_trend_str = f"Shorter tail distribution ({all_p90:.1f}d vs {D23_P90_BASELINE_DAYS:.1f}d baseline)"
+    else:
+        p90_trend_str = f"Longer tail distribution ({all_p90:.1f}d vs {D23_P90_BASELINE_DAYS:.1f}d baseline)"
     exp_trend_str = f"Slightly lower overall expiration rate ({all_gt90_pct:.1f}% vs 19.0%)" if all_gt90_pct <= 19.0 else f"Higher overall expiration rate ({all_gt90_pct:.1f}% vs 19.0%)"
 
     lines.append("## 5. Comparison Against Decision D-23 Baseline")
@@ -284,11 +294,11 @@ def generate_report(as_of: datetime | None = None) -> str:
     lines.append("")
 
     daily_loss = (failed_60_90 / 30.0) if failed_60_90 else 0.0
-    est_payload_gb = (recoverable_today * 1.5) / 1024.0
+    est_payload_gb = (recoverable_today * ASSUMED_LOG_MB) / 1024.0
 
     lines.append("### Key Takeaways for Review 1 & Stage 4 Planning")
     lines.append(f"1. **D-23 Hypothesis Confirmed**: The 90-day expiry cliff is real and active. {win_expired:,} failed runs are permanently unrecoverable from GitHub log storage, validating the D-23 decision to prioritize Stage 4 (log capture) over non-expiring tiers.")
-    lines.append(f"2. **Stage 4 Target Sized**: Exactly **{recoverable_today:,} failed runs** across {len(repos)} repos have logs available today. At ~1.5 MB per log payload, this represents a modest ~{est_payload_gb:.2f} GB download job.")
+    lines.append(f"2. **Stage 4 Target Sized**: Exactly **{recoverable_today:,} failed runs** across {len(repos)} repos have logs available today. At an assumed ~{ASSUMED_LOG_MB:.1f} MB per log payload (unmeasured assumption; Stage 4 will report empirical payload sizes), this represents an estimated ~{est_payload_gb:.2f} GB download job.")
     lines.append(f"3. **Daily Attrition Rate**: With **{failed_60_90:,} failed runs** in the 60–90 day bracket, the corpus loses approximately **{daily_loss:.1f} recoverable failed runs per day of delay**.")
     lines.append("")
```

---

## 5. Execution and Determinism Check (Step 2)

Commands run:
```bash
uv run python analysis/expiry_cliff.py > /tmp/run1.md
uv run python analysis/expiry_cliff.py > /tmp/run2.md
md5sum /tmp/run1.md /tmp/run2.md
```
Output:
```
9274b39baa40d0904b530b1aa4186d05  /tmp/run1.md
552edf9d84dcbecd59e932b310ccb26e  /tmp/run2.md
```

Diff output between run 1 and run 2:
Command:
```bash
diff /tmp/run1.md /tmp/run2.md
```
Output:
```diff
3,4c3,4
< **As of**: `2026-08-21 09:30:28 UTC`  
< **Corpus Scope**: 46 repositories, 102,042 unique workflow runs (102,042 raw records).  
---
> **As of**: `2026-08-21 09:31:00 UTC`  
> **Corpus Scope**: 46 repositories, 102,051 unique workflow runs (102,051 raw records).  
11,12c11,12
< > **Headline Metric**: Across all 46 repositories, **5,401 out of 7,777 failed-run logs (69.4%) remain RECOVERABLE TODAY**.
< > Exactly **2,376 failed runs (30.6%) are already >90 days old** and their logs are permanently expired from GitHub Actions storage.
---
> > **Headline Metric**: Across all 46 repositories, **5,402 out of 7,782 failed-run logs (69.4%) remain RECOVERABLE TODAY**.
> > Exactly **2,380 failed runs (30.6%) are already >90 days old** and their logs are permanently expired from GitHub Actions storage.
16,21c16,21
< | **Critical (≤ 7 days left)** | Age 83.0d – 90.0d | **513** | 6.60% | **Imminent permanent loss** — capture immediately |
< | **High (8 – 30 days left)** | Age 60.0d – 82.9d | **1,390** | 17.87% | **Expiring this month** — Stage 4 priority target |
< | **Medium (31 – 60 days left)** | Age 30.0d – 59.9d | **1,639** | 21.07% | Safe for 1 month |
< | **Low (> 60 days left)** | Age < 30.0d | **1,859** | 23.90% | Safe for 2 months |
< | **Permanently Expired** | Age > 90.0d | **2,376** | 30.55% | **Lost** (unrecoverable from GitHub API) |
< | **Total Recoverable Today** | **Age ≤ 90.0d** | **5,401** | **69.45%** | **Total available for Stage 4 download** |
---
> | **Critical (≤ 7 days left)** | Age 83.0d – 90.0d | **513** | 6.59% | **Imminent permanent loss** — capture immediately |
> | **High (8 – 30 days left)** | Age 60.0d – 82.9d | **1,390** | 17.86% | **Expiring this month** — Stage 4 priority target |
> | **Medium (31 – 60 days left)** | Age 30.0d – 59.9d | **1,639** | 21.06% | Safe for 1 month |
> | **Low (> 60 days left)** | Age < 30.0d | **1,860** | 23.90% | Safe for 2 months |
> | **Permanently Expired** | Age > 90.0d | **2,380** | 30.58% | **Lost** (unrecoverable from GitHub API) |
> | **Total Recoverable Today** | **Age ≤ 90.0d** | **5,402** | **69.42%** | **Total available for Stage 4 download** |
27,28c27,28
< | **Total Count** | **102,042** (100.0%) | **7,777** (100.0%) |
< | **Failure Rate** | — | **7.62%** |
---
> | **Total Count** | **102,051** (100.0%) | **7,782** (100.0%) |
> | **Failure Rate** | — | **7.63%** |
30,31c30,31
< | **Median (P50) Age** | 50.59 days | 66.24 days |
< | **P90 Age** | 107.89 days | 176.66 days |
---
> | **Median (P50) Age** | 50.60 days | 66.25 days |
> | **P90 Age** | 107.90 days | 177.99 days |
33,35c33,35
< | **Past 90 Days (Expired)** | 18,553 (18.18%) | 2,376 (30.55%) |
< | **60 – 90 Day Band (Expiring in 30d)** | 24,211 (23.73%) | 1,903 (24.47%) |
< | **Under 60 Days (Safe)** | 59,278 (58.09%) | 3,498 (44.98%) |
---
> | **Past 90 Days (Expired)** | 18,558 (18.19%) | 2,380 (30.58%) |
> | **60 – 90 Day Band (Expiring in 30d)** | 24,212 (23.73%) | 1,903 (24.45%) |
> | **Under 60 Days (Safe)** | 59,281 (58.09%) | 3,499 (44.96%) |
95c95
< | `sirixdb/sirix` | 201 | 68 | 33.8% | 28 | 10 | 30 | **40** | 70.5d |
---
> | `sirixdb/sirix` | 210 | 73 | 34.8% | 32 | 10 | 31 | **41** | 70.6d |
109,110c109,110
< | **Total Workflow Runs** | 6,212 | **102,042** | 16.4× scale increase |
< | **Total Failed Runs** | 401 | **7,777** | 19.4× scale increase (failure rate rose from 6.5% to 7.6%) |
---
> | **Total Workflow Runs** | 6,212 | **102,051** | 16.4× scale increase |
> | **Total Failed Runs** | 401 | **7,782** | 19.4× scale increase (failure rate rose from 6.5% to 7.6%) |
113,114c113,114
< | **Runs Past 90 Days** | 1,180 (19.0%) | **18,553 (18.2%)** | Slightly lower overall expiration rate (18.2% vs 19.0%) |
< | **Failed Runs Past 90 Days** | 195 (48.6% of fails) | **2,376 (30.6% of fails)** | **Confirms D-23**: 30.6% permanent loss, with 69.4% still recoverable |
---
> | **Runs Past 90 Days** | 1,180 (19.0%) | **18,558 (18.2%)** | Slightly lower overall expiration rate (18.2% vs 19.0%) |
> | **Failed Runs Past 90 Days** | 195 (48.6% of fails) | **2,380 (30.6% of fails)** | **Confirms D-23**: 30.6% permanent loss, with 69.4% still recoverable |
118,119c118,119
< 1. **D-23 Hypothesis Confirmed**: The 90-day expiry cliff is real and active. 2,376 failed runs are permanently unrecoverable from GitHub log storage, validating the D-23 decision to prioritize Stage 4 (log capture) over non-expiring tiers.
< 2. **Stage 4 Target Sized**: Exactly **5,401 failed runs** across 46 repos have logs available today. At an assumed ~1.5 MB per log payload (unmeasured assumption; Stage 4 will report empirical payload sizes), this represents an estimated ~7.91 GB download job.
---
> 1. **D-23 Hypothesis Confirmed**: The 90-day expiry cliff is real and active. 2,380 failed runs are permanently unrecoverable from GitHub log storage, validating the D-23 decision to prioritize Stage 4 (log capture) over non-expiring tiers.
> 2. **Stage 4 Target Sized**: Exactly **5,402 failed runs** across 46 repos have logs available today. At an assumed ~1.5 MB per log payload (unmeasured assumption; Stage 4 will report empirical payload sizes), this represents an estimated ~7.91 GB download job.
```

**Diff Explanation**:
The diff between `run1.md` and `run2.md` stems from two factors:
1. Expected wall-clock timestamp embedding (`2026-08-21 09:30:28 UTC` vs `2026-08-21 09:31:00 UTC`), matching Predicted Failure 3.
2. Background live capture: during the 32 seconds between runs, the running harvester daemon (PID 14016) appended 9 new workflow runs to `sirixdb/sirix` (total count rose from 102,042 to 102,051). All calculation logic and narrative formatting are completely deterministic.

---

## 6. Changed Output Sections

Command:
```bash
grep -n "P90 Run Age\|Stage 4 Target Sized" -A 2 /tmp/run1.md
```
Output:
```
112:| **Overall P90 Run Age** | 100.1 days | **107.9 days** | Longer tail distribution (107.9d vs 100.1d baseline) |
113-| **Runs Past 90 Days** | 1,180 (19.0%) | **18,553 (18.2%)** | Slightly lower overall expiration rate (18.2% vs 19.0%) |
114-| **Failed Runs Past 90 Days** | 195 (48.6% of fails) | **2,376 (30.6% of fails)** | **Confirms D-23**: 30.6% permanent loss, with 69.4% still recoverable |
--
119:2. **Stage 4 Target Sized**: Exactly **5,401 failed runs** across 46 repos have logs available today. At an assumed ~1.5 MB per log payload (unmeasured assumption; Stage 4 will report empirical payload sizes), this represents an estimated ~7.91 GB download job.
120-3. **Daily Attrition Rate**: With **1,903 failed runs** in the 60–90 day bracket, the corpus loses approximately **63.4 recoverable failed runs per day of delay**.
121-
```

Command:
```bash
grep -n "P90 Run Age\|Stage 4 Target Sized" -A 2 /tmp/run2.md
```
Output:
```
112:| **Overall P90 Run Age** | 100.1 days | **107.9 days** | Longer tail distribution (107.9d vs 100.1d baseline) |
113-| **Runs Past 90 Days** | 1,180 (19.0%) | **18,558 (18.2%)** | Slightly lower overall expiration rate (18.2% vs 19.0%) |
114-| **Failed Runs Past 90 Days** | 195 (48.6% of fails) | **2,380 (30.6% of fails)** | **Confirms D-23**: 30.6% permanent loss, with 69.4% still recoverable |
--
119:2. **Stage 4 Target Sized**: Exactly **5,402 failed runs** across 46 repos have logs available today. At an assumed ~1.5 MB per log payload (unmeasured assumption; Stage 4 will report empirical payload sizes), this represents an estimated ~7.91 GB download job.
120-3. **Daily Attrition Rate**: With **1,903 failed runs** in the 60–90 day bracket, the corpus loses approximately **63.4 recoverable failed runs per day of delay**.
121-
```

---

## 7. Files Changed and Test Counts

**Files Changed**:
- `analysis/expiry_cliff.py` (+10, -4 lines)

**Test Suite Verification**:
- Predicted test count: **202**
- Actual test count: **202 passed in 2.94s**

---

## 8. Non-Goals Honoured

- Did NOT touch anything under `src/` or `tests/`.
- Did NOT modify `analysis/corpus_stats.py`, `attrition_funnel.py`, or `annotation_census.py`.
- Did NOT run `make tables`.
- Did NOT change any computed values or arithmetic.
- Did NOT read, edit, or print `.env`.
- Did NOT run git write commands or make commits.
- Did NOT disturb, signal, or restart the harvester daemon.

---

## 9. Open Questions & Contradictions

- None. The findings and behavior matched Predicted Failure 3 (wall-clock timestamp delta in header) and confirmed real-time capture advancement by the background daemon.
