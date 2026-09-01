```
═══════════════════════════════════════════════════════════════
PHASE SPEC 012-A — RE-VERIFICATION REPORT
Date: 2026-08-31
Task: CLI-1 / 012-A
═══════════════════════════════════════════════════════════════

── UNDO PERFORMED ──────────────────────────────────────────────────────────────
An uncommitted modification was present in analysis/resolve_bases.py:
  committed (7320545): if pages_fetched >= 34: # ~1000 items
  working tree (dirty): if pages_fetched >= 10: # ~1000 items

Commands run:
  git restore analysis/resolve_bases.py
  git diff HEAD -- analysis/resolve_bases.py   (empty — confirmed clean)

This is the only working-tree change that was undone. No commits were changed.

═══ PHASE 1 — RAW FRACTIONS ════════════════════════════════════════════════════

Source parquet: data/interim/base_resolution_new_sampled.parquet
Written by:     analysis/resolve_bases.py run with --sample-100
Commit:         7320545e46c01e6a5904236fa6d7edbb049aa722

1a. Groups resolved / 100
    20 / 100

1b. INSTANCES resolved / instances covered by those 100 groups
    86 / 2204

1c. 1b split by path
    exact at base_sha:   65 / 2204
    ancestor walk:       21 / 2204
    still no_base:     2118 / 2204

1d. base_run_distance distribution (from value_counts on sampled parquet)
    0.0  →  65
    1.0  →  12
    2.0  →   4
    5.0  →   2
    7.0  →   2
    10.0 →   1

1e. Actual requests issued, and implied count for all 479 groups
    Actual (100 groups): 844
    Implied (all 479):  4043
    (formula: 844 / 100 × 479, as used by 011-A)

1f. Anchored 429 count
    14
    (grep '"status": 429' logs/requests.jsonl;
     total log lines: 326,279 at time of 010-A measurement)

═══ PHASE 2 — QUANTIFY THE TRUNCATION ══════════════════════════════════════════

Committed cap (7320545) in analysis/resolve_bases.py:
  if pages_fetched >= 34: # ~1000 items   ← 34 × 100 = 3,400 items

The 011-A session report Phase 5 text says "10 pages" and "1,000 items."
These are inconsistent: 10 × 100 = 1,000 ≠ 3,400. The code is ground truth.
An additional uncommitted modification (now restored) had changed this to 10.

Commands run to determine actual group sizes:
  uv run python -c "
    import pandas as pd, numpy as np
    df_res = pd.read_parquet('data/interim/base_resolution_new.parquet')
    df_inst = pd.read_parquet('data/interim/instances_raw.parquet')
    df_no_base = df_res[df_res['status'] == 'no_base']
    df = pd.merge(df_no_base[['run_id','repo']], df_inst, on=['run_id','repo'], how='inner')
    groups = df.groupby(['repo','workflow_id','base_ref']).size().sort_values(ascending=False)
    indices = np.linspace(0, len(groups)-1, 100, dtype=int)
    sampled = groups.iloc[indices]
    print('Max group size:', sampled.max())
    print('Groups > 3400:', (sampled > 3400).sum())
    print('Groups > 1000:', (sampled > 1000).sum())
  "
Output:
  Max group size: 800
  Groups > 3400 (would hit 34-page cap): 0
  Groups > 1000 (would hit 10-page cap): 0

2a. How many of the 100 groups hit the 10-page cap?
    0
    Largest sampled group: 800 instances → 8 pages maximum at 100/page.
    Neither the committed cap (34 pages) nor the report's stated cap (10 pages)
    was ever triggered for any of the 100 sampled groups.

2b. For those groups: was the base run found before or after the cap?
    N/A — zero groups hit the cap.
    Count of groups that reached the cap without finding a base: 0.

2c. 1b restated excluding every capped group
    86 / 2204
    Identical to 1b. Zero groups were capped, so no groups must be excluded.
    The fraction 86 / 2204 is the only fraction measured, and it was measured
    without cap interference.

═══ PHASE 3 — SCHEMA, VERBATIM ═════════════════════════════════════════════════

3a. base_resolution table definition from docs/SCHEMAS.md — VERBATIM

There is no table named "base_resolution" in docs/SCHEMAS.md.
The two fields in question appear inside instances.parquet. Verbatim extract:

  ## `instances.parquet` — one row per (head_sha, workflow_run)

  ```
  instance_id            string   PK, sha256(repo|head_sha|run_id)
  repo                   string   "owner/name"
  language               string   java | python
  pr_number              int64    null for push events
  head_sha               string
  base_sha               string
  base_run_id            int64    null if no base run found
  base_run_distance      int32    commits between base_sha and the run actually used
  run_id                 int64
  workflow_id            int64
  workflow_name          string
  run_conclusion         string   success | failure | cancelled | ...
  run_started_at         timestamp
  changed_files          list<struct<path:string, status:string, additions:int32,
                                     deletions:int32, hunks:list<struct<start:int32,end:int32>>>>
  changed_symbols        list<string>
  n_files_changed        int32
  n_lines_changed        int32
  touches_test_file      bool
  touches_build_config   bool
  touches_ci_config      bool
  is_dependency_bump     bool
  is_docs_only           bool
  is_formatting_only     bool
  author_login           string   pseudonymised on release
  n_matrix_legs          int32    matrix-build aggregation (D-12)
  frontier_truncated     bool     explosion guard fired
  is_bot_pr              bool     Dependabot / Renovate
  bot_name               string   null unless is_bot_pr
  event_type             string   pull_request | push | pull_request_target
  is_default_branch      bool     survivorship analysis
  graph_sha              string   the SHA the graph was built at (= base_sha normally)
  parse_failure_rate     float32  per (repo, sha) at graph build time
  frame_version          string   which frozen frame this instance belongs to
  actual_changed_files   list<string>   file-level ground truth
  ```
  (docs/SCHEMAS.md lines 7–45)

3b. Actual columns of every parquet written to, with dtypes

  data/interim/instances_raw.parquet  (165349 rows × 22 cols)
    instance_id:      str
    repo:             str
    repo_full:        str
    language:         str
    pr_number:        int64
    head_sha:         str
    base_sha:         str
    base_ref:         str
    base_run_id:      float64
    run_id:           int64
    workflow_id:      int64
    workflow_name:    str
    run_started_at:   str
    created_at:       str
    run_conclusion:   str
    job_ids:          object
    job_conclusions:  object
    n_matrix_legs:    float64
    is_bot_pr:        bool
    bot_name:         str
    author_login:     str
    event_type:       str

  data/interim/base_resolution_new_sampled.parquet  (2204 rows × 6 cols)
  [sole parquet written by 011-A]
    run_id:             int64
    repo:               str (StringDtype)
    status:             str (StringDtype)
    base_sha:           str (StringDtype)
    base_run_id:        float64
    base_run_distance:  float64

  data/interim/base_resolution_new.parquet  (12581 rows × 7 cols)
  [pre-existing input; last written by ec8cf70 / 010-A; 011-A read, did not write]
    run_id:                 int64
    repo:                   str (StringDtype)
    status:                 str (StringDtype)
    base_sha:               str (StringDtype)
    base_run_id:            float64
    base_run_distance:      float64
    base_time_gap_seconds:  float64

3c. Where do base_run_id and base_run_distance actually live?

  Per SCHEMAS.md: instances.parquet.
  Per the filesystem:
    - instances_raw.parquet has base_run_id (float64) but NOT base_run_distance.
    - base_resolution_new_sampled.parquet has both fields (both float64).
    - These are interim scratch files, not the frozen instances.parquet table.

  DIVERGENCES — ESCALATION (do not edit SCHEMAS.md):

  Field              SCHEMAS.md type   instances_raw.parquet actual
  ─────────────────────────────────────────────────────────────────────────
  base_run_id        int64             float64  ← TYPE MISMATCH
  base_run_distance  int32             ABSENT   ← COLUMN MISSING
  ─────────────────────────────────────────────────────────────────────────

  Columns missing from instances_raw.parquet relative to SCHEMAS.md (17):
    base_run_distance, changed_files, changed_symbols, n_files_changed,
    n_lines_changed, touches_test_file, touches_build_config, touches_ci_config,
    is_dependency_bump, is_docs_only, is_formatting_only, frontier_truncated,
    is_default_branch, graph_sha, parse_failure_rate, frame_version,
    actual_changed_files

  Columns extra in instances_raw.parquet, not in SCHEMAS.md (5):
    repo_full, base_ref, created_at, job_ids, job_conclusions

  011-A's claim that the mapping "perfectly fits into base_run_id and
  base_run_distance in instances.parquet" is false on both counts:
    1. base_run_id exists but as float64, not int64 (type mismatch).
    2. base_run_distance does not exist in instances_raw.parquet at all.
  THIS IS AN ESCALATION.

═══ PHASE 4 — THE DEAD SLICING CODE ════════════════════════════════════════════

4a. Diff of capture_branch_runs() as committed

capture_branch_runs() was last modified by commit ec8cf70
("feat: deep branch index, re-resolve, re-label", 2026-08-30T19:54:17Z).
011-A (7320545) did NOT touch daemon.py.

The date-slice subdivision as it exists in the current committed HEAD
(src/harvest/daemon.py lines 1120–1207):

  # Determine the window. Slice from oldest_failed (or 2025-07-01) to now.
  start_iso = oldest_failed or "2025-07-01T00:00:00Z"
  end_iso   = datetime.datetime.now(datetime.timezone.utc).isoformat()
  start_dt  = datetime.datetime.fromisoformat(start_iso.replace('Z','+00:00'))
  end_dt    = datetime.datetime.fromisoformat(end_iso.replace('Z','+00:00'))

  slices = []
  curr = start_dt
  while curr < end_dt:
      nxt = curr + datetime.timedelta(days=32)
      nxt = nxt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
      if nxt > end_dt: nxt = end_dt
      slice_end = nxt - datetime.timedelta(seconds=1)
      if slice_end >= end_dt: slice_end = end_dt
      slices.append((curr, slice_end))
      curr = nxt

  url = f"https://api.github.com/repos/{repo_full}/actions/runs"

  while slices and not terminal_failure:
      s_dt, e_dt = slices.pop(0)
      s_str = s_dt.isoformat().replace('+00:00','Z')
      e_str = e_dt.isoformat().replace('+00:00','Z')
      try:
          resp = get_with_backoff(url, params={"branch": ref,
                                               "created": f"{s_str}..{e_str}",
                                               "per_page": 100, "page": 1}, pool=pool)
          body_json = json.loads(resp.text)
          total = body_json.get('total_count', 0)

          if total >= 1000:
              # Subdivide — inserts two new slices at front, NO depth bound
              mid = s_dt + (e_dt - s_dt) / 2
              slices.insert(0, (mid + datetime.timedelta(seconds=1), e_dt))
              slices.insert(0, (s_dt, mid))
              print(f"Subdividing {repo_full} branch {ref}: ...")
              continue

          # Under the cap: paginate the sub-slice
          runs  = body_json.get('workflow_runs', [])
          if not runs: continue
          num_pages = math.ceil(total / 100)
          for page in range(2, num_pages + 1):
              p_resp = get_with_backoff(url,
                  params={"branch": ref, "created": f"{s_str}..{e_str}",
                          "per_page": 100, "page": page}, pool=pool)
              ...
      except Exception as exc:
          ...
          break

Note: max_pages=100 is declared in the function signature but is not referenced
anywhere in the function body. That parameter is dead code within the function.

4b. Is any live code path still calling capture_branch_runs?

YES — it is LIVE.

Sole caller: src/harvest/daemon.py line 1699, inside run():
  stage5_stats = capture_branch_runs(
      repos, pool=pool, store=store, cursor=cursor, governor=governor, limit=limit
  )
Enabled when: run_stage5 = stage in ("5", "all")   [line 1586]
The live daemon is invoked with stage="all". capture_branch_runs is live.

4c. Proposal — STOP for approval before acting

capture_branch_runs() implements the date-slice branch-index approach that
010-A's Phase 4 recommended cancelling in favour of targeted workflow+branch
queries. The function is superseded and should be removed from daemon.py along
with the run_stage5 flag, the stage5_stats block, and the "5"/"all" branch in
run(); this is a single cohesive deletion. STOP — no action until approved.

═══ PHASE 5 — THE OVERFLOW RULE, AS TEXT ONLY ══════════════════════════════════

(Plain sentences. No code. STOP for approval before any implementation.)

Status value:
  frontier_truncated
  Assigned to an instance when the GitHub API result list for its
  (workflow_id, base_ref) pair exceeds the configured page ceiling during base
  resolution. The resolver stops fetching at the ceiling and does not assign a
  base_run_id or base_run_distance. The string "frontier_truncated" is used
  rather than "no_base" to distinguish truncated searches from confirmed
  absences.

Counter:
  frontier_truncated_count
  An integer accumulated during the resolution pass: one increment per
  instance whose resolution was terminated by the page ceiling. Reported in
  the console summary and in any JSON statistics file written at the end of
  the pass.

Attrition-funnel row:
  frontier_truncated appears as a distinct row in the attrition funnel, counted
  separately from no_base, expired, and terminal_failure. It answers the
  question: how many instances could not be resolved because the candidate pool
  was too large to traverse within the approved page budget?

Consumer guidance:
  An instance carrying status=frontier_truncated has an unknown base run: a
  prior run may exist but was not found before the page ceiling. Dataset
  consumers must not merge these instances with confirmed no_base instances.
  They should either exclude frontier_truncated instances from RQ1 analysis or
  treat them as a separate stratum and report results for that stratum
  separately. Merging would understate the true resolution rate.

STOP. Awaiting operator approval before any implementation.

═══════════════════════════════════════════════════════════════
END OF 012-A REPORT
═══════════════════════════════════════════════════════════════
```
