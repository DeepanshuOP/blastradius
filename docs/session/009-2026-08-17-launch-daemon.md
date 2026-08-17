# Launch — harvester daemon, full 300-repo frame, stages 1+2 (credentials fixed)

**Outcome: SUCCESS. Daemon launched, alive and making measured progress at +10
minutes. Process left running per instructions.**

This supersedes the prior same-day attempt in this file, which crashed at
`TokenPool.from_env()` because `.env` was never loaded into the process
environment. That failure mode is fixed here via `uv run --env-file .env`.

## STEP 1 — Recovering a known-good invocation (read-only)

```
$ ls Makefile justfile scripts/
Makefile

scripts/:
__pycache__
merge_frame.py
sample_frame.py
```

No `justfile`. `Makefile` exists but has no harvest-launch target (grep below).

```
$ grep -rn "harvest.daemon" --include="*.md" --include="Makefile" --include="*.sh" . | head -40
```

All hits were prior session-report markdown files under `docs/session/` (this
task's own trail, plus the earlier failed-launch report) and `docs/ROADMAP.md`
naming `src/harvest/daemon.py` as a design target. **No Makefile target, no
shell script, no other launcher exists** — the CLI invocation is the only
launch path.

```
$ grep -rl "GITHUB_PAT" . --exclude=.env --exclude-dir=.git | head -20
```
Filenames only (no content printed, per instructions):
```
.env.example
tests/test_scaffold.py
tests/test_frame.py
docs/session/launch_readiness.md
tests/test_daemon.py
src/harvest/ratelimit.py
docs/session/launch_20260817.md
```
None of these needed a value read from them — `ratelimit.py`'s own
`from_env()` already names the three key names in code, which is how the
prior report's diagnosis was made.

```
$ uv run --help 2>&1 | grep -i "env-file"
      --env-file <ENV_FILE>
      --no-env-file
```
`--env-file` **is supported** by this `uv` version.

## STEP 2 — Credential verification (branch a)

Branch **(a)** taken, since `--env-file` support was confirmed above.

```
$ uv run --env-file .env python -c "import os; ks=('GITHUB_PAT_1','GITHUB_PAT_2','GITHUB_PAT_3'); print([(k, bool(os.environ.get(k)), os.environ.get(k,'')!=os.environ.get(k,'').strip()) for k in ks])"
[('GITHUB_PAT_1', True, False), ('GITHUB_PAT_2', True, False), ('GITHUB_PAT_3', True, False)]
```

All three: present = `True`, whitespace/CRLF-corrupted = `False`. No stop
condition triggered. No value, fragment, or character of any PAT was printed
at any point.

## T_START, BASELINE_REQ, PID

- **T_START**: `2026-08-17T06:50:11Z`
- **BASELINE_REQ**: `40340`
- **PID**: `7217` (the actual `python3 -m src.harvest.daemon` process). PID
  `7214` is the `uv run --env-file .env` parent wrapper process — both are
  part of the same detached process group (`setsid`).

Pre-launch baselines, raw:

```
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-08-17T06:50:11Z

$ wc -l logs/requests.jsonl
40340 logs/requests.jsonl

$ du -sh data/raw
297M	data/raw

$ ls data/raw | wc -l
11
```

## Exact launch command

```
setsid nohup uv run --env-file .env python -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both > logs/daemon_20260817.log 2>&1 < /dev/null &
```

## Liveness at +10s: ALIVE

```
$ ps aux | grep '[h]arvest\.daemon'
shree       7214  0.0  0.4 219364 33152 ?        Ssl  06:50   0:00 uv run --env-file .env python -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both
shree       7217  0.0  0.8  72180 64732 ?        S    06:50   0:03 /home/shree/blastradius/.venv/bin/python3 -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both

$ tail -n 20 logs/daemon_20260817.log
(empty)
```

Both processes present, no exit. Log empty — see note on stdout buffering
below.

## Liveness at +60s: ALIVE

```
$ ps aux | grep '[h]arvest\.daemon'
shree       7214  0.0  0.4 219364 33152 ?        Ssl  06:50   0:00 uv run --env-file .env python -m src.harvest.daemon ...
shree       7217  6.0  0.8  72180 64732 ?        S    06:50   0:05 /home/shree/blastradius/.venv/bin/python3 -m src.harvest.daemon ...

$ wc -l logs/requests.jsonl
40449 logs/requests.jsonl

$ tail -n 30 logs/daemon_20260817.log
(empty)
```

`requests.jsonl` grew 40340 → 40449 (+109) in the first ~60s — real progress,
process is issuing requests. Log still empty.

## Liveness at +10min: ALIVE

Ran the `sleep 600` block; the tail end of the chained command (`grep -c
'"status": 429'` returning 0 matches) exits non-zero and short-circuited the
remaining `&&`-chained 403/401 checks, so those two were re-run separately
immediately after. Both checks land within the same ~30s window, at
`T ≈ 2026-08-17T07:02:23Z` (elapsed ≈ 12m12s from `T_START`, slightly over the
10-minute floor because of the extra investigation this required):

```
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-08-17T07:02:05Z   (first checkpoint, mid-chain)
...
2026-08-17T07:02:23Z   (403/401 checkpoint)

$ ps aux | grep '[h]arvest\.daemon'
shree       7214  0.0  0.4 219364 33152 ?        Ssl  06:50   0:00 uv run --env-file .env python -m src.harvest.daemon ...
shree       7217  2.4  0.9  81916 73852 ?        S    06:50   0:17 /home/shree/blastradius/.venv/bin/python3 -m src.harvest.daemon ...

$ wc -l logs/requests.jsonl
41121 logs/requests.jsonl   (first checkpoint)
41141 logs/requests.jsonl   (403/401 checkpoint, ~18s later)

$ du -sh data/raw
306M	data/raw

$ ls data/raw | wc -l
12

$ tail -n 20 logs/daemon_20260817.log
(empty)

$ tail -n 500 logs/requests.jsonl | grep -c '"status": 429'
0
$ tail -n 500 logs/requests.jsonl | grep -c '"status": 403'
0
$ tail -n 500 logs/requests.jsonl | grep -c '"status": 401'
0
```

Still alive under the same PID (`7217`), still growing `requests.jsonl`, still
zero rate-limit/forbidden/auth-failure responses in the most recent 500
requests. **No 401s — no evidence of a dead token or pool eviction.**

## Rate arithmetic

Using the final checkpoint (`T = 2026-08-17T07:02:23Z`, `requests.jsonl` =
`41141`):

- a) requests issued = `41141 - 40340` = **801**
- b) elapsed minutes = `06:50:11Z` → `07:02:23Z` = 12 min 12 s = **12.2 min**
- c) requests/hour = `801 / 12.2 * 60` = **≈ 3,939 requests/hour**
- d) repo directories added under `data/raw` = `12 - 11` = **1** (new repo
  directory created during this run; `data/raw` grew 297M → 306M, +9M)
- e) projected hours to reach 300 repos: **rough order of magnitude only.**
  Assumption named: if the observed pace of 1 new repo directory completed
  per ~12.2 minutes held uniformly across all 300 repos, `300 * 12.2 min ≈
  3,660 min ≈ 61 hours`. This assumption is almost certainly wrong in
  practice — historical request-log data mined in the prior readiness report
  showed wildly uneven per-repo cost (`spiculedata/saiku` alone accounted for
  over 4,000 stage-2 requests historically, vs. lower-hundreds for most other
  repos), so real wall-clock time will depend heavily on which large repos
  land early vs. late in the frame order. Treat 61 hours as an
  order-of-magnitude floor, not a forecast.

## 429 / 403 / 401 counts

All three explicitly zero in the most recent 500 `requests.jsonl` lines as of
the +10min checkpoint:
- 429 (rate limited): **0**
- 403 (forbidden): **0**
- 401 (unauthorized — would indicate a dead token / pool eviction per §8.1):
  **0**

## data/raw: before / after

| | Before (T_START) | After (+~12min) |
|---|---|---|
| Size | 297M | 306M |
| Repo directories | 11 | 12 |

## Last 20 lines of the daemon log

```
(empty at every checkpoint checked — +10s, +60s, +10min)
```

## Errors, warnings, stderr — and one non-error observation

**No error, exception, traceback, or warning was seen at any checkpoint.**
The daemon has been continuously alive since launch under PID 7217.

**Observation, not an error:** `logs/daemon_20260817.log` is empty at every
checkpoint despite the process demonstrably working (growing
`requests.jsonl`, growing `data/raw`, a new repo directory created). This is
consistent with Python's stdout being fully block-buffered when redirected to
a file rather than a TTY (`> logs/daemon_20260817.log`) — `run()`'s own
docstring says it prints "a one-line summary per repo," but with per-repo
work apparently taking well over a minute each (see rate arithmetic), the
buffer may simply not have flushed yet at any of the three checkpoints taken
so far. This did not block any liveness or progress check, since `ps`,
`requests.jsonl`, and `data/raw` all gave independent, unambiguous evidence
of a live, working process. Not investigated further, since predicted-failure
handling explicitly says not to diagnose or work around anything once the
process is confirmed alive.

Failure-mode #4 partially applies in spirit but isn't an exact match: this
run is not resuming into mostly-already-cursor-complete repos (only 1 new
repo directory in ~12 minutes suggests the daemon is doing substantial
per-repo work, not skipping quickly past completed cursors) — reported here
plainly rather than forced into that bucket.

## What was NOT done, per non-goals

- Daemon was not killed, restarted, or signaled — it is still running as PID
  7217 (parent 7214) after this report.
- No file under `src/` or `tests/` was modified. `load_dotenv()` was not
  added to `daemon.py`.
- `.env` was not edited, reformatted, or read for its values — only key
  presence/whitespace were checked, and no value or fragment was ever
  printed.
- No token was regenerated or replaced.
- `dry_run_estimate()` was not touched.
- Stage 3/4 were not run; no `MANIFEST.json`/`CHECKSUMS` created.
- No commit was made. `docs/session/` remains untracked.
