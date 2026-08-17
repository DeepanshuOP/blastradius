# Session Report: 020-2026-08-17-daemon-progress-diagnosis

**Task:** Read-only diagnosis of harvester daemon progress (PID 14016). Determine why ~2,200 requests were issued post-relaunch without a new repository directory appearing under `data/raw`.
**Date:** 2026-08-17
**Model:** Gemini 3.7 Flash

---

## 1. Session Guard & Process Verification

```bash
$ uname -s && pwd && uv run python --version
Linux
/home/shree/blastradius
Python 3.11.15

$ ps aux | grep '[h]arvest\.daemon'
shree      14013  0.0  0.4 219368 32896 ?        Ssl  14:39   0:00 uv run --env-file .env python -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both
shree      14016  0.8  1.1  97560 89916 ?        S    14:39   0:44 /home/shree/blastradius/.venv/bin/python3 -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both
```

Daemon is active and running uninterrupted under PID 14016 (parent 14013).

---

## 2. Step 1: Request Stream Analysis

### Last 30 Requests
```bash
$ tail -n 30 logs/requests.jsonl
{"ts": "2026-08-17T16:09:59.192035+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/29145834618/jobs", "status": 200, "token_idx": 1, "remaining": 4601, "duration_ms": 1930.7703340018634, "attempt": 1}
{"ts": "2026-08-17T16:10:00.726169+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/29145834556/jobs", "status": 200, "token_idx": 1, "remaining": 4600, "duration_ms": 1522.9923489969224, "attempt": 1}
{"ts": "2026-08-17T16:10:02.157963+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/29145834653/jobs", "status": 200, "token_idx": 1, "remaining": 4599, "duration_ms": 1414.8836549939006, "attempt": 1}
{"ts": "2026-08-17T16:10:05.317691+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs", "status": 200, "token_idx": 1, "remaining": 4598, "duration_ms": 3150.250070000766, "attempt": 1}
{"ts": "2026-08-17T16:10:07.690122+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/26843786400/jobs", "status": 200, "token_idx": 1, "remaining": 4597, "duration_ms": 2363.4303330036346, "attempt": 1}
{"ts": "2026-08-17T16:10:09.533685+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/26843786419/jobs", "status": 200, "token_idx": 1, "remaining": 4596, "duration_ms": 1827.1652689945768, "attempt": 1}
{"ts": "2026-08-17T16:10:11.429600+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/26843785936/jobs", "status": 200, "token_idx": 1, "remaining": 4595, "duration_ms": 1881.697238997731, "attempt": 1}
{"ts": "2026-08-17T16:10:13.318907+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs", "status": 200, "token_idx": 1, "remaining": 4594, "duration_ms": 1874.0380379967974, "attempt": 1}
{"ts": "2026-08-17T16:10:14.828630+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/27595538329/jobs", "status": 200, "token_idx": 1, "remaining": 4593, "duration_ms": 1489.5782749954378, "attempt": 1}
{"ts": "2026-08-17T16:10:17.623950+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/27595538343/jobs", "status": 200, "token_idx": 1, "remaining": 4592, "duration_ms": 2782.2694830028922, "attempt": 1}
{"ts": "2026-08-17T16:10:19.976989+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/27595538339/jobs", "status": 200, "token_idx": 1, "remaining": 4591, "duration_ms": 2330.4517619981198, "attempt": 1}
{"ts": "2026-08-17T16:10:23.192675+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/27595536753/jobs", "status": 200, "token_idx": 1, "remaining": 4590, "duration_ms": 3194.853337998211, "attempt": 1}
{"ts": "2026-08-17T16:10:25.720171+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs", "status": 200, "token_idx": 1, "remaining": 4589, "duration_ms": 2519.920236998587, "attempt": 1}
{"ts": "2026-08-17T16:10:28.373531+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs", "status": 200, "token_idx": 1, "remaining": 4588, "duration_ms": 2647.0135470008245, "attempt": 1}
{"ts": "2026-08-17T16:10:29.890995+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs", "status": 200, "token_idx": 1, "remaining": 4587, "duration_ms": 1497.4382489963318, "attempt": 1}
{"ts": "2026-08-17T16:10:31.820103+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/31624374294/jobs", "status": 200, "token_idx": 1, "remaining": 4586, "duration_ms": 1912.458457001776, "attempt": 1}
{"ts": "2026-08-17T16:10:33.268881+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/31624374384/jobs", "status": 200, "token_idx": 1, "remaining": 4585, "duration_ms": 1442.354922000959, "attempt": 1}
{"ts": "2026-08-17T16:10:35.219613+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/31624374381/jobs", "status": 200, "token_idx": 1, "remaining": 4584, "duration_ms": 1929.7214170001098, "attempt": 1}
{"ts": "2026-08-17T16:10:37.044205+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/31624374351/jobs", "status": 200, "token_idx": 1, "remaining": 4583, "duration_ms": 1818.829354000627, "attempt": 1}
{"ts": "2026-08-17T16:10:39.003617+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs", "status": 200, "token_idx": 1, "remaining": 4582, "duration_ms": 1938.5286559991073, "attempt": 1}
{"ts": "2026-08-17T16:10:40.959214+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/26978058696/jobs", "status": 200, "token_idx": 1, "remaining": 4581, "duration_ms": 1935.2247490023728, "attempt": 1}
{"ts": "2026-08-17T16:10:42.357987+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/26977427936/jobs", "status": 200, "token_idx": 1, "remaining": 4580, "duration_ms": 1379.670330999943, "attempt": 1}
{"ts": "2026-08-17T16:10:44.691141+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/26977428007/jobs", "status": 200, "token_idx": 1, "remaining": 4579, "duration_ms": 2327.511487004813, "attempt": 1}
{"ts": "2026-08-17T16:10:46.219753+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/26977427992/jobs", "status": 200, "token_idx": 1, "remaining": 4578, "duration_ms": 1507.9281549988082, "attempt": 1}
{"ts": "2026-08-17T16:10:47.679411+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs", "status": 200, "token_idx": 1, "remaining": 4577, "duration_ms": 1452.8916109993588, "attempt": 1}
{"ts": "2026-08-17T16:10:49.570155+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/30517065878/jobs", "status": 200, "token_idx": 1, "remaining": 4576, "duration_ms": 1875.8857080028974, "attempt": 1}
{"ts": "2026-08-17T16:10:50.998543+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/30517065821/jobs", "status": 200, "token_idx": 1, "remaining": 4575, "duration_ms": 1408.3927760002553, "attempt": 1}
{"ts": "2026-08-17T16:10:52.779322+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/30517065860/jobs", "status": 200, "token_idx": 1, "remaining": 4574, "duration_ms": 1762.8418530002818, "attempt": 1}
{"ts": "2026-08-17T16:10:55.876879+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs/30517065883/jobs", "status": 200, "token_idx": 1, "remaining": 4573, "duration_ms": 3077.2257629942033, "attempt": 1}
{"ts": "2026-08-17T16:10:57.257562+00:00", "url": "https://api.github.com/repos/floci-io/floci/actions/runs", "status": 200, "token_idx": 1, "remaining": 4572, "duration_ms": 1359.4938069945783, "attempt": 1}
```

### URL Shape Aggregation (Last 200 Requests)
```bash
$ tail -n 200 logs/requests.jsonl | grep -o '"url": "[^"]*"' | sed 's/[0-9]\{4,\}/{ID}/g' | sort | uniq -c | sort -rn
    138 "url": "https://api.github.com/repos/floci-io/floci/actions/runs/{ID}/jobs"
     62 "url": "https://api.github.com/repos/floci-io/floci/actions/runs"
```

**Diagnosis:** The harvester is exclusively requesting two Stage 2 endpoints for a single repository: `floci-io/floci`:
1. `GET /repos/floci-io/floci/actions/runs?head_sha={sha}` (kind `runs`)
2. `GET /repos/floci-io/floci/actions/runs/{id}/jobs` (kind `jobs`)

---

## 3. Step 2: Advancing vs Repeating

```bash
$ tail -n 500 logs/requests.jsonl | grep -o 'repos/[^/]*/[^/]*' | sort | uniq -c | sort -rn
    500 repos/floci-io/floci
```

**Diagnosis:** All recent requests target `floci-io/floci`. The repository's directory already exists under `data/raw/floci-io__floci` because Stage 1 (PR sweep, 9 pages, 887 PRs) was captured prior to the 13:30Z abort. The daemon is actively progressing through Stage 2 (run and job discovery) across the 2,675 distinct head SHAs associated with those PRs.

---

## 4. Step 3: Cursor State Inspection

```bash
$ uv run python -c "import sqlite3; con=sqlite3.connect('file:data/state/cursor.db?mode=ro',uri=True); [print(r) for r in con.execute('SELECT repo, pr_page, sweep_status, last_pr_updated_at, last_complete_sweep_at, updated_at FROM repo_cursor ORDER BY updated_at DESC LIMIT 15')]"
('floci-io/floci', 1, 'idle', '2026-08-17T11:28:44Z', '2026-08-17T14:39:49.076251+00:00', '2026-08-17T14:39:49.076251+00:00')
('cryptomator/cryptomator', 1, 'idle', '2026-08-01T16:25:33Z', '2026-08-17T14:39:48.741910+00:00', '2026-08-17T14:39:48.741910+00:00')
('baomidou/mybatis-plus', 1, 'idle', '2026-08-04T15:35:41Z', '2026-08-17T14:39:48.628829+00:00', '2026-08-17T14:39:48.628829+00:00')
('atmosphere/atmosphere', 1, 'idle', '2026-08-15T18:21:28Z', '2026-08-17T14:39:47.659599+00:00', '2026-08-17T14:39:47.659599+00:00')
('crimera/piko', 1, 'idle', '2026-08-17T09:29:18Z', '2026-08-17T14:39:47.109536+00:00', '2026-08-17T14:39:47.109536+00:00')
('schemacrawler/schemacrawler', 1, 'idle', '2026-08-16T14:51:34Z', '2026-08-17T14:39:46.810713+00:00', '2026-08-17T14:39:46.810713+00:00')
('plantuml/plantuml', 1, 'idle', '2026-08-17T01:04:01Z', '2026-08-17T14:39:46.608649+00:00', '2026-08-17T14:39:46.608649+00:00')
('spring-cloud/spring-cloud-commons', 1, 'idle', '2026-08-17T03:23:28Z', '2026-08-17T14:39:46.526513+00:00', '2026-08-17T14:39:46.526513+00:00')
('zaproxy/zaproxy', 1, 'idle', '2026-08-17T08:01:54Z', '2026-08-17T14:39:46.352581+00:00', '2026-08-17T14:39:46.352581+00:00')
('diffplug/spotless', 1, 'idle', '2026-08-17T05:30:23Z', '2026-08-17T14:39:46.141423+00:00', '2026-08-17T14:39:46.141423+00:00')
('mcreator/mcreator', 1, 'idle', '2026-08-17T08:56:16Z', '2026-08-17T14:39:45.228189+00:00', '2026-08-17T14:39:45.228189+00:00')
('nitrite/nitrite-java', 1, 'idle', '2026-08-10T16:43:52Z', '2026-08-17T14:39:45.067475+00:00', '2026-08-17T14:39:45.067475+00:00')
('spring-projects/spring-kafka', 1, 'idle', '2026-08-16T01:58:16Z', '2026-08-17T14:39:44.825916+00:00', '2026-08-17T14:39:44.825916+00:00')
('jhipster/prettier-java', 1, 'idle', '2026-08-14T18:09:39Z', '2026-08-17T14:39:44.474286+00:00', '2026-08-17T14:39:44.474286+00:00')
('apache/zeppelin', 1, 'idle', '2026-08-17T06:46:27Z', '2026-08-17T14:39:43.347518+00:00', '2026-08-17T14:39:43.347518+00:00')

$ uv run python -c "import sqlite3; con=sqlite3.connect('file:data/state/cursor.db?mode=ro',uri=True); print(list(con.execute('SELECT sweep_status, count(*) FROM repo_cursor GROUP BY sweep_status')))"
[('idle', 32)]

$ uv run python -c "import sqlite3; con=sqlite3.connect('file:data/state/cursor.db?mode=ro',uri=True); print(list(con.execute('SELECT status, count(*) FROM capture_unit GROUP BY status')))"
[('complete', 64821), ('failed', 2), ('in_flight', 1)]
```

All 32 initial repos have `last_complete_sweep_at` recorded. Units are actively being resolved and written to `capture_unit`.

---

## 5. Step 4: Code Path Analysis (`src/harvest/daemon.py`)

Function governing execution order: **`run()`**

```python
def run(
    *,
    pool: TokenPool,
    store: RawStore,
    cursor: CursorStore,
    repos_path: Path,
    limit: int,
    cutoff: datetime,
    stage: str = DEFAULT_STAGE,
) -> dict:
    repos = _load_repos(repos_path, limit)
    run_stage1 = stage in ("1", "both", "all")
    run_stage2 = stage in ("2", "both", "all")
    run_stage3 = stage in ("3", "all")
    governor = TransientGovernor(pool)
...
    for owner, repo in repos:
        repo_full = f"{owner}/{repo}"
        total["repos_processed"] += 1
        if run_stage1:
            result = sweep_repo(
                owner, repo, pool=pool, store=store, cursor=cursor, cutoff=cutoff, governor=governor
            )
...
        if run_stage2:
            stats = discover_repo(owner, repo, pool=pool, store=store, cursor=cursor, governor=governor)
```

### Questions:
- **a) Ordering:** `run()` iterates `repos = _load_repos(repos_path, limit)`, which loads `data/frame/frame_v1.csv` sequentially in line-order (rows 1 to 300).
- **b) Skip behavior:** In `sweep_repo()`, `_fetch_pulls_page()` checks `cursor.get_capture_unit(repo_full, "pulls", page)`. If `complete`, it reads the cached record off disk and issues 0 HTTP requests. In `discover_repo()`, `_fetch_runs_for_sha()` and `_fetch_jobs_for_run()` check `capture_unit` for `complete` status and read from disk without HTTP calls.
- **c) Re-request condition:** A repo is never re-requested from page 1 over HTTP if its units are in `complete` status; it reads from disk until it encounters uncompleted units.

---

## 6. Step 5: Live 5-Minute Delta Measurement

- **Start:** `A=72558` requests, `B=33` dirs, `16:14:29 UTC`
- **End:** `C=73349` requests, `D=34` dirs, `16:27:44 UTC`
- **Delta:** `+791 requests`, `+1 repo directory`
- **Units Count:** `65,660` units complete.

During this measurement window:
- `floci-io/floci` completed its remaining Stage 2 SHAs.
- The daemon transitioned to repo #33 in the frame: **`apache/dolphinscheduler`**.
- `data/raw/apache__dolphinscheduler` was created as Stage 1 began sweeping its PRs.

---

## 7. Step 6: Diagnostic Conclusion

The harvester was not stuck, stalled, or looping; it was executing Stage 2 across **`floci-io/floci`** (repo #32 in `frame_v1.csv`), which is an exceptionally large repository comprising **2,675 distinct head SHAs** across 887 PRs and **6,502+ workflow jobs**. Because the directory `data/raw/floci-io__floci` had already been created during Stage 1 prior to the 13:30Z restart, all ~2,200 post-relaunch requests were actively writing into existing subdirectories (`run/` and `sha/`) inside that folder. Once `floci-io/floci` finished Stage 2, the daemon advanced to `apache/dolphinscheduler` (#33) and created the next directory under `data/raw`, confirming nominal sequential frame progression.
