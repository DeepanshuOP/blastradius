# Session Report: 013 — Attrition Funnel Generator (T0.7 / ROADMAP §23.3)

**Task**: Implement `analysis/attrition_funnel.py` to regenerate the BlastRadius attrition funnel table from artefacts on disk, per ROADMAP §23.3 and T0.7, outputting the markdown table to `paper/generated/attrition_funnel.md` and stdout.  
**Date**: 2026-08-17  
**Model**: Gemini 3.7 Flash  

---

## 1. Guard & Daemon Verification

```bash
uname -s && pwd && uv run python --version
```
```
Linux
/home/shree/blastradius
Python 3.11.15
```

```bash
ps aux | grep '[h]arvest\.daemon'
```
```
shree       7214  0.0  0.4 219364 33152 ?        Ssl  06:50   0:00 uv run --env-file .env python -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both
shree       7217  2.4  0.9  85896 78232 ?        S    06:50   5:09 /home/shree/blastradius/.venv/bin/python3 -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both
```

---

## 2. Survey & Analysis Commands

```bash
ls -la data/frame/
```
```
total 18296
drwxr-xr-x 2 shree shree    4096 Aug  7 11:43 .
drwxrwxrwx 9 shree shree    4096 Aug  8 13:48 ..
-rw-r--r-- 1 shree shree    2383 Aug  7 11:43 ATTRITION.json
-rw-r--r-- 1 shree shree    9946 Aug  5 16:57 QUERY.md
-rw-r--r-- 1 shree shree  169519 Aug  7 08:56 attrition_stage.csv
-rw-r--r-- 1 shree shree   31277 Aug  7 11:43 frame_v1.csv
-rw-r--r-- 1 shree shree  206799 Aug  7 11:43 frame_v1_reserve.csv
-rw-r--r-- 1 shree shree  228570 Aug  7 08:56 repos.csv
-rw-r--r-- 1 shree shree  377954 Aug  7 08:56 repos.partial.csv
-rw-r--r-- 1 shree shree 8857455 Aug  5 16:56 repos_raw.csv
-rwxr-xr-x 1 shree shree 3060860 Aug  5 16:55 seart_a.csv
-rwxr-xr-x 1 shree shree 5754941 Aug  5 16:55 seart_b.csv
```

```bash
head -n 1 data/frame/*.csv
```
```
==> data/frame/attrition_stage.csv <==
owner,repo,lang,n_runs_90d,n_workflows,n_test_workflows,verdict,failing_call,status,exception_class

==> data/frame/frame_v1.csv <==
owner,repo,lang,stars,commits,default_branch,n_runs_90d,test_workflow_ids,license,sample_rank

==> data/frame/frame_v1_reserve.csv <==
owner,repo,lang,stars,commits,default_branch,n_runs_90d,test_workflow_ids,license,reserve_rank

==> data/frame/repos.csv <==
owner,repo,lang,stars,commits,default_branch,n_runs_90d,test_workflow_ids,license

==> data/frame/repos.partial.csv <==
owner,repo,lang,stars,commits,default_branch,license,n_runs_90d,n_workflows,n_test_workflows,test_workflow_ids,verdict,failing_call,status,exception_class

==> data/frame/repos_raw.csv <==
"id","name","isFork","commits","branches","releases","forks","mainLanguage","defaultBranch","license","homepage","watchers","stargazers","contributors","size","createdAt","pushedAt","updatedAt","totalIssues","openIssues","totalPullRequests","openPullRequests","blankLines","codeLines","commentLines","metrics","lastCommit","lastCommitSHA","hasWiki","isArchived","isDisabled","isLocked","languages","labels","topics"

==> data/frame/seart_a.csv <==
"id","name","isFork","commits","branches","releases","forks","mainLanguage","defaultBranch","license","homepage","watchers","stargazers","contributors","size","createdAt","pushedAt","updatedAt","totalIssues","openIssues","totalPullRequests","openPullRequests","blankLines","codeLines","commentLines","metrics","lastCommit","lastCommitSHA","hasWiki","isArchived","isDisabled","isLocked","languages","labels","topics"

==> data/frame/seart_b.csv <==
"id","name","isFork","commits","branches","releases","forks","mainLanguage","defaultBranch","license","homepage","watchers","stargazers","contributors","size","createdAt","pushedAt","updatedAt","totalIssues","openIssues","totalPullRequests","openPullRequests","blankLines","codeLines","commentLines","metrics","lastCommit","lastCommitSHA","hasWiki","isArchived","isDisabled","isLocked","languages","labels","topics"
```

```bash
wc -l data/frame/*.csv
```
```
    3672 data/frame/attrition_stage.csv
     301 data/frame/frame_v1.csv
    2034 data/frame/frame_v1_reserve.csv
    2334 data/frame/repos.csv
    3672 data/frame/repos.partial.csv
    3672 data/frame/repos_raw.csv
    1124 data/frame/seart_a.csv
    2549 data/frame/seart_b.csv
   19358 total
```

---

## 3. Implementation and Execution

Implemented `analysis/attrition_funnel.py` (148 lines).

```bash
uv run python analysis/attrition_funnel.py
```
```
# BlastRadius Repository Frame Attrition Funnel

Per ROADMAP §23.3 and T0.7. Generated deterministically by `analysis/attrition_funnel.py`.

| Stage | Filter | Input | Removed | Survivors | Java | Python | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **0. SEART Export** | Stars ≥500, Commits ≥1000, not a fork, pushed in last 60d, has license[^1] | — | — | **3,671** | 1,123 | 2,548 | Measured |
| **1. CI Liveness** | ≥100 GitHub Actions workflow runs in trailing 90 days | 3,671 | 1,025 (1,024 no_ci, 1 api_error) | **2,646** | 769 | 1,877 | Measured |
| **2. Test Intent** | ≥1 workflow classified as test-intent (`test|ci|build|pytest|mvn|gradle`) | 2,646 | 313 | **2,333** | 686 | 1,647 | Measured |
| **3. Sample Draw** | Seeded language-stratified draw (150 Java + 150 Python; Seed 20261110)[^2] | 2,333 | 2,033 | **300** | 150 | 150 | Measured |
| **4. Parseable Outcomes** | Produces parseable test outcomes (ROADMAP §23.3 stage 5)[^3] | 300 | not yet measured | not yet measured | not yet measured | not yet measured | Pending harvest |
| **5. Fault-Revealing** | Produces ≥1 fault-revealing instance (ROADMAP §23.3 stage 6)[^4] | not yet measured | not yet measured | not yet measured | not yet measured | not yet measured | Pending curation |
| **6. Graph Budget** | Graph builds within time and memory budget (ROADMAP §23.3 stage 7)[^5] | not yet measured | not yet measured | not yet measured | not yet measured | not yet measured | Pending graph build |
| **7. Test-Node Binding** | Test-node binding rate ≥70% (ROADMAP §23.3 stage 8, T8)[^6] | not yet measured | not yet measured | not yet measured | not yet measured | not yet measured | Pending evaluation |

### Footnotes & Explanatory Notes

[^1]: **SEART Export**: Java (1,123) and Python (2,548) candidate queries merged from `data/frame/seart_a.csv` and `data/frame/seart_b.csv`. Criterion 7 (≥50 PRs in 90 days) was deferred because SEART only indexes lifetime PR counts (`data/frame/QUERY.md` §2 row 7).
[^2]: **Reserve Pool**: The 2,033 remaining eligible repositories (536 Java, 1,497 Python) are retained in `data/frame/frame_v1_reserve.csv` for replacement and widening under T14.
[^3]: **Stage 5 (Parseable Outcomes)**: Measured during Stage 1 harvest and log-parsing phase (T1).
[^4]: **Stage 6 (Fault-Revealing Instances)**: Measured during instance curation and flaky-test filtering (T2).
[^5]: **Stage 7 (Graph Build Budget)**: Measured during code graph construction under time and memory caps (§19.4, T4).
[^6]: **Stage 8 (Test-Node Binding Rate)**: Measured during static test binding evaluation against ground-truth suites (T8).
```

---

## 4. Cross-Checks

1. **Stage 0 Total vs `repos_raw.csv` line count minus 1**:
   - `wc -l data/frame/repos_raw.csv` = 3672 lines.
   - `3672 - 1 = 3671`. Stage 0 survivors = 3,671.
   - **Result**: Match.

2. **Frame v1 Language Balance**:
   - `frame_v1.csv`: 150 Java + 150 Python = 300 total.
   - **Result**: Match.

3. **Frame + Reserve vs Kept Repos (Stage 2 Survivors)**:
   - `frame_v1.csv` = 300 repos (150 Java, 150 Python).
   - `frame_v1_reserve.csv` = 2,033 repos (536 Java, 1,497 Python).
   - Total = 2,333 repos (686 Java, 1,647 Python), matching exactly `verdict == 'kept'` in `attrition_stage.csv` (2,333).
   - **Result**: Match.

4. **Agreement with `ATTRITION.json`**:
   - `ATTRITION.json` stages match recomputed values from `attrition_stage.csv` exactly:
     - `seart_export`: 3,671 output.
     - `ci_live`: 3,671 input, 1,025 removed, 2,646 output.
     - `has_test_workflow`: 2,646 input, 313 removed, 2,333 output.
     - `sampled`: 2,333 input, 2,033 removed, 300 output.
   - **Result**: Match.

---

## 5. Test Suite Verification

- **Predicted**: 152 passed.
- **Actual**: 152 passed in 32.53s.

```bash
uv run pytest
```
```
collected 152 items
============================= 152 passed in 32.53s =============================
```

---

## 6. Non-Goals Honoured

- No edits to `src/`, `tests/`, `docs/DECISIONS.md`, or `dashboard.py`.
- No modification, overwrite, or deletion of any CSV or JSON under `data/frame/`.
- No external web requests issued.
- Daemon undisturbed (PID 7217 running).
- No Git write commands or unauthorized commits.
- Zero inferred, interpolated, or estimated counts for unmeasured pipeline stages.
