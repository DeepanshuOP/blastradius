# Session Report: 031-2026-08-20-commit-backlog

**Date:** 2026-08-20  
**Task ID:** commit-backlog  
**Model:** Gemini 3.7 Flash  
**Topic:** Land outstanding working-tree changes in three logical commits and push to origin/main  

---

## 1. Task Statement
Commit the outstanding working-tree changes in three logical groups:
1. Analysis fixes (`analysis/corpus_stats.py`, `analysis/expiry_cliff.py`)
2. Supervisor restart wrapper (`run_supervised.sh`)
3. Session records (`docs/HANDOFF.md`, `docs/session/INDEX.md`, `docs/session/029-2026-08-18-stale-constants.md`, `docs/session/030-2026-08-19-daemon-census.md`)

Leave untracked: `vendor/graphify-br/` and `blastradius_pipeline_explorer.jsx`.

---

## 2. Commands Run and Verbatim Output

### STEP 0 — Guard
Command:
```bash
uname -s && pwd && uv run python --version && ps aux | grep '[h]arvest\.daemon'
```
Output:
```
Linux
/home/shree/blastradius
Python 3.11.15
shree       3050  0.0  0.4 219364 33152 ?        Sl   11:28   0:00 uv run --env-file .env python -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both
shree       3053  5.3  1.1  99440 91644 ?        S    11:28   1:18 /home/shree/blastradius/.venv/bin/python3 -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both
```

### STEP 0b — Identity Gate
Command:
```bash
git config user.name && git config user.email
```
Output:
```
DeepanshuOP
99538840+DeepanshuOP@users.noreply.github.com
```

### STEP 1 — Survey (Pre-Approval)

Command 1:
```bash
git status --porcelain
```
Output:
```
 M analysis/corpus_stats.py
 M analysis/expiry_cliff.py
 M docs/HANDOFF.md
 M docs/session/INDEX.md
?? blastradius_pipeline_explorer.jsx
?? docs/session/029-2026-08-18-stale-constants.md
?? docs/session/030-2026-08-19-daemon-census.md
?? run_supervised.sh
?? vendor/graphify-br/
```

Command 2:
```bash
git log -1 --format='%H %s'
```
Output:
```
40c797fc26a79cb7e83f0ba0d07a4edebb05c20e docs: record the two key model for test identity
```

Command 3:
```bash
git rev-parse HEAD origin/main
```
Output:
```
40c797fc26a79cb7e83f0ba0d07a4edebb05c20e
40c797fc26a79cb7e83f0ba0d07a4edebb05c20e
```

Command 4:
```bash
git diff --stat
```
Output:
```
 analysis/corpus_stats.py |  2 +-
 analysis/expiry_cliff.py | 39 ++++++++++++++++++++++++++-------------
 docs/HANDOFF.md          |  2 ++
 docs/session/INDEX.md    |  1 +
 4 files changed, 30 insertions(+), 14 deletions(-)
```

Command 5:
```bash
git diff analysis/corpus_stats.py analysis/expiry_cliff.py
```
Output:
```
diff --git a/analysis/corpus_stats.py b/analysis/corpus_stats.py
index 6b1ef6a..62c1928 100644
--- a/analysis/corpus_stats.py
+++ b/analysis/corpus_stats.py
@@ -438,7 +438,7 @@ def generate_stats() -> str:
     # ---------------------------------------------------------
     lines.append("## 4. Test Suite")
     lines.append("")
-    lines.append("- **Test Suite Baseline**: **152 passed unit tests** (`tests/test_*.py`)")
+    lines.append("- **Test Suite**: Verified passing via `make test` and `make check-log-isolation` (`tests/test_*.py`).")
     lines.append("- **Log Isolation Guard**: Invoking `pytest` dynamically inside `corpus_stats.py` is omitted to guarantee request log isolation against `logs/requests.jsonl` per ROADMAP §8.2, §34.1 Rule 6, and `make check-log-isolation`.")
     lines.append("- **Manual Verification**: Run `make test` or `uv run pytest tests/ -q` independently to verify test suite status.")
     lines.append("")
diff --git a/analysis/expiry_cliff.py b/analysis/expiry_cliff.py
index 717c5c9..2236008 100644
--- a/analysis/expiry_cliff.py
+++ b/analysis/expiry_cliff.py
@@ -208,7 +208,7 @@ def generate_report(as_of: datetime | None = None) -> str:
     # Section 1: Headline Recoverable Window
     lines.append("## 1. Recoverable Window for Failed Runs")
     lines.append("")
-    lines.append(f"> **Headline Metric**: Across all 32 repositories, **{recoverable_today:,} out of {total_failed:,} failed-run logs ({recoverable_today_pct:.1f}%) remain RECOVERABLE TODAY**.")
+    lines.append(f"> **Headline Metric**: Across all {len(repos)} repositories, **{recoverable_today:,} out of {total_failed:,} failed-run logs ({recoverable_today_pct:.1f}%) remain RECOVERABLE TODAY**.")
     lines.append(f"> Exactly **{win_expired:,} failed runs ({win_expired_pct:.1f}%) are already >90 days old** and their logs are permanently expired from GitHub Actions storage.")
     lines.append("")
     lines.append("| Window Band | Remaining Log Lifetime | Failed Runs | % of Failed Runs | Operational Urgency |")
@@ -250,8 +250,8 @@ def generate_report(as_of: datetime | None = None) -> str:
         )
     lines.append("")
 
-    # Section 4: Comprehensive 32-Repository Breakdown
-    lines.append("## 4. Comprehensive Repository Breakdown (32 Repositories)")
+    # Section 4: Comprehensive Repository Breakdown
+    lines.append(f"## 4. Comprehensive Repository Breakdown ({len(repos)} Repositories)")
     lines.append("")
     lines.append("| Repository | Total Runs | Failed Runs | Fail Rate | Expired (>90d) | Expiring (60–90d) | Safe (<60d) | Recoverable (≤90d) | Median Fail Age |")
     lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
@@ -262,24 +262,37 @@ def generate_report(as_of: datetime | None = None) -> str:
     lines.append("")
 
     # Section 5: Comparison against D-23 baseline
+    scale_runs = (total_unique / 6212.0) if total_unique else 0.0
+    scale_fails = (total_failed / 401.0) if total_failed else 0.0
+    fail_rate_pct = (total_failed / total_unique * 100.0) if total_unique else 0.0
+    age_delta = 68.3 - all_med
+    age_trend_str = f"Fresher corpus ({age_delta:.1f} days lower median age)" if age_delta >= 0 else f"Older corpus ({-age_delta:.1f} days higher median age)"
+    p90_trend_str = f"Consistent tail distribution ({all_p90:.1f}d vs 100.1d baseline)"
+    exp_trend_str = f"Slightly lower overall expiration rate ({all_gt90_pct:.1f}% vs 19.0%)" if all_gt90_pct <= 19.0 else f"Higher overall expiration rate ({all_gt90_pct:.1f}% vs 19.0%)"
+
     lines.append("## 5. Comparison Against Decision D-23 Baseline")
     lines.append("")
-    lines.append("| Metric | D-23 Smoke Corpus (10 Repos) | Full Measured Corpus (32 Repos) | Trend / Finding |")
+    lines.append(f"| Metric | D-23 Smoke Corpus (10 Repos) | Full Measured Corpus ({len(repos)} Repos) | Trend / Finding |")
     lines.append("| :--- | :---: | :---: | :--- |")
-    lines.append(f"| **Total Workflow Runs** | 6,212 | **{total_unique:,}** | 3.3× scale increase |")
-    lines.append(f"| **Total Failed Runs** | 401 | **{total_failed:,}** | 5.3× scale increase (failure rate rose from 6.5% to {total_failed/total_unique*100:.1f}%) |")
-    lines.append(f"| **Overall Median Run Age** | 68.3 days | **{all_med:.1f} days** | Fresher corpus (18.9 days lower median age) |")
-    lines.append(f"| **Overall P90 Run Age** | 100.1 days | **{all_p90:.1f} days** | Consistent tail distribution |")
-    lines.append(f"| **Runs Past 90 Days** | 1,180 (19.0%) | **{all_gt90:,} ({all_gt90_pct:.1f}%)** | Slightly lower overall expiration rate |")
-    lines.append(f"| **Failed Runs Past 90 Days** | 195 (48.6% of fails) | **{failed_gt90:,} ({failed_gt90_pct:.1f}% of fails)** | **Confirms D-23**: ~23.5% permanent loss, with 76.5% still recoverable |")
+    lines.append(f"| **Total Workflow Runs** | 6,212 | **{total_unique:,}** | {scale_runs:.1f}× scale increase |")
+    lines.append(f"| **Total Failed Runs** | 401 | **{total_failed:,}** | {scale_fails:.1f}× scale increase (failure rate rose from 6.5% to {fail_rate_pct:.1f}%) |")
+    lines.append(f"| **Overall Median Run Age** | 68.3 days | **{all_med:.1f} days** | {age_trend_str} |")
+    lines.append(f"| **Overall P90 Run Age** | 100.1 days | **{all_p90:.1f} days** | {p90_trend_str} |")
+    lines.append(f"| **Runs Past 90 Days** | 1,180 (19.0%) | **{all_gt90:,} ({all_gt90_pct:.1f}%)** | {exp_trend_str} |")
+    lines.append(f"| **Failed Runs Past 90 Days** | 195 (48.6% of fails) | **{failed_gt90:,} ({failed_gt90_pct:.1f}% of fails)** | **Confirms D-23**: {failed_gt90_pct:.1f}% permanent loss, with {recoverable_today_pct:.1f}% still recoverable |")
     lines.append(f"| **Failed Runs in 60–90d Band** | 206 (51.4% of fails) | **{failed_60_90:,} ({failed_60_90_pct:.1f}% of fails)** | **Confirms D-23 urgency**: {failed_60_90:,} failed runs face expiry within 30 days |")
     lines.append("")
+
     daily_loss = (failed_60_90 / 30.0) if failed_60_90 else 0.0
     est_payload_gb = (recoverable_today * 1.5) / 1024.0
 
     lines.append("### Key Takeaways for Review 1 & Stage 4 Planning")
-    lines.append("1. **D-23 Hypothesis Confirmed**: The 90-day expiry cliff is real and active. 501 failed runs are permanently unrecoverable from GitHub log storage, validating the D-23 decision to prioritize Stage 4 (log capture) over non-expiring tiers.")
-    lines.append(f"2. **Stage 4 Target Sized**: Exactly **{recoverable_today:,} failed runs** across 32 repos have logs available today. At ~1.5 MB per log payload, this represents a modest ~2.45 GB download job.")
-    lines.append(f"3. **Daily Attrition Rate**: With **{failed_60_90:,} failed runs** in the 60–90 day bracket, the corpus loses approximately **15 to 16 recoverable failed runs per day of delay**.")
+    lines.append(f"1. **D-23 Hypothesis Confirmed**: The 90-day expiry cliff is real and active. {win_expired:,} failed runs are permanently unrecoverable from GitHub log storage, validating the D-23 decision to prioritize Stage 4 (log capture) over non-expiring tiers.")
+    lines.append(f"2. **Stage 4 Target Sized**: Exactly **{recoverable_today:,} failed runs** across {len(repos)} repos have logs available today. At ~1.5 MB per log payload, this represents a modest ~{est_payload_gb:.2f} GB download job.")
+    lines.append(f"3. **Daily Attrition Rate**: With **{failed_60_90:,} failed runs** in the 60–90 day bracket, the corpus loses approximately **{daily_loss:.1f} recoverable failed runs per day of delay**.")
     lines.append("")
 
+
     return "\n".join(lines)
```

---

### STEP 2 — Staging and Commits (Post-Approval)

#### Commit 1 — The Analysis Fixes
Staging command:
```bash
git add analysis/corpus_stats.py analysis/expiry_cliff.py && git status --porcelain
```
Output:
```
M  analysis/corpus_stats.py
M  analysis/expiry_cliff.py
 M docs/HANDOFF.md
 M docs/session/INDEX.md
?? blastradius_pipeline_explorer.jsx
?? docs/session/029-2026-08-18-stale-constants.md
?? docs/session/030-2026-08-19-daemon-census.md
?? run_supervised.sh
?? vendor/graphify-br/
```

Commit command:
```bash
git commit -m "fix: compute the narrative figures instead of hardcoding them"
```
Output:
```
[main 05c765e] fix: compute the narrative figures instead of hardcoding them
 2 files changed, 27 insertions(+), 14 deletions(-)
```

#### Commit 2 — The Restart Wrapper
Staging command:
```bash
git add run_supervised.sh && git status --porcelain
```
Output:
```
 M docs/HANDOFF.md
 M docs/session/INDEX.md
A  run_supervised.sh
?? blastradius_pipeline_explorer.jsx
?? docs/session/029-2026-08-18-stale-constants.md
?? docs/session/030-2026-08-19-daemon-census.md
?? vendor/graphify-br/
```

Commit command:
```bash
git commit -m "feat: restart the harvester automatically when it exits"
```
Output:
```
[main 3f8ae0f] feat: restart the harvester automatically when it exits
 1 file changed, 8 insertions(+)
 create mode 100644 run_supervised.sh
```

#### Commit 3 — The Session Records
File check command:
```bash
ls docs/session/029* docs/session/030*
```
Output:
```
docs/session/029-2026-08-18-stale-constants.md
docs/session/030-2026-08-19-daemon-census.md
```

Staging command:
```bash
git add docs/HANDOFF.md docs/session/INDEX.md docs/session/029-2026-08-18-stale-constants.md docs/session/030-2026-08-19-daemon-census.md && git status --porcelain
```
Output:
```
M  docs/HANDOFF.md
A  docs/session/029-2026-08-18-stale-constants.md
A  docs/session/030-2026-08-19-daemon-census.md
M  docs/session/INDEX.md
?? blastradius_pipeline_explorer.jsx
?? vendor/graphify-br/
```

Commit command:
```bash
git commit -m "docs: record the stale-constants and daemon-census sessions"
```
Output:
```
[main b41228a] docs: record the stale-constants and daemon-census sessions
 4 files changed, 651 insertions(+)
 create mode 100644 docs/session/029-2026-08-18-stale-constants.md
 create mode 100644 docs/session/030-2026-08-19-daemon-census.md
```

---

### STEP 3 — Push and Verification

Command:
```bash
git push origin main && git rev-parse HEAD origin/main
```
Output:
```
Enumerating objects: 24, done.
Counting objects: 100% (24/24), done.
Delta compression using up to 12 threads
Compressing objects: 100% (16/16), done.
Writing objects: 100% (16/16), 12.92 KiB | 778.00 KiB/s, done.
Total 16 (delta 10), reused 0 (delta 0), pack-reused 0 (from 0)
remote: Resolving deltas: 100% (10/10), completed with 8 local objects.
To https://github.com/DeepanshuOP/blastradius.git
   40c797f..b41228a  main -> main
b41228a902d1bb538a325bae8735139eb4b278e7
b41228a902d1bb538a325bae8735139eb4b278e7
```

Closing status command:
```bash
git status --porcelain
```
Output:
```
?? blastradius_pipeline_explorer.jsx
?? vendor/graphify-br/
```

---

## 3. Commit Summary
- **Commit 1:** `05c765ea9bfa24d156fc20ef1350a4fa43431102` (`fix: compute the narrative figures instead of hardcoding them`)
- **Commit 2:** `3f8ae0fcad80ffba3a79dcf794a32e1eb1fe4d98` (`feat: restart the harvester automatically when it exits`)
- **Commit 3:** `b41228a902d1bb538a325bae8735139eb4b278e7` (`docs: record the stale-constants and daemon-census sessions`)
- **Remote Sync:** `b41228a902d1bb538a325bae8735139eb4b278e7` (HEAD == origin/main)
- **Deliberately Excluded Untracked Paths:** `blastradius_pipeline_explorer.jsx`, `vendor/graphify-br/`

---

## 4. Non-Goals Honoured
- Did NOT modify the content of any file during staging/committing.
- Did NOT run pytest, make tables, or any analysis script.
- Did NOT read, edit, print, or reformat `.env`.
- Did NOT touch anything under `src/`, `tests/`, `data/`, or `logs/`.
- Did NOT amend, rebase, reset, stash, or force-push.
- Did NOT stop, signal, or restart the daemon.
- Did NOT run `uv add` or `uv sync`.
