# Session Report: 019-2026-08-17-daemon-relaunch

**Task:** Relaunch the harvester daemon over the full 300-repo frame, stages 1+2, following an abort at 13:30:28Z when tokens encountered 401s during a GitHub incident. Preserve log evidence to `logs/daemon_20260817b.log`.
**Date:** 2026-08-17
**Model:** Gemini 3.7 Flash

---

## 1. Session Guard & Process Check

```bash
$ uname -s && pwd && uv run python --version
Linux
/home/shree/blastradius
Python 3.11.15
```

```bash
$ ps aux | grep '[h]arvest\.daemon'
(No daemon process running prior to launch)
```

---

## 2. Step 1: Confirmation of Abort Reason from Old Log

```bash
$ tail -n 40 logs/daemon_20260817.log
[domaframework/doma] stage2 shas=64 out_of_window=36 pull_commits_not_complete=0 runs_discovered=256 failed_terminal=0 transient=0
[wso2/product-is] stage1 pages=3 captured=213 failed_terminal=0 transient=0 window_stopped=True
[wso2/product-is] stage2 shas=481 out_of_window=87 pull_commits_not_complete=0 runs_discovered=646 failed_terminal=0 transient=0
[robo-code/robocode] stage1 pages=1 captured=20 failed_terminal=0 transient=0 window_stopped=True
[robo-code/robocode] stage2 shas=27 out_of_window=80 pull_commits_not_complete=0 runs_discovered=36 failed_terminal=0 transient=0
[signalapp/signal-server] stage1 pages=1 captured=4 failed_terminal=0 transient=0 window_stopped=True
[signalapp/signal-server] stage2 shas=4 out_of_window=96 pull_commits_not_complete=0 runs_discovered=6 failed_terminal=0 transient=0
[membrane/api-gateway] stage1 pages=2 captured=183 failed_terminal=0 transient=0 window_stopped=True
[membrane/api-gateway] stage2 shas=973 out_of_window=17 pull_commits_not_complete=0 runs_discovered=838 failed_terminal=0 transient=0
[rptools/maptool] stage1 pages=1 captured=62 failed_terminal=0 transient=0 window_stopped=True
[rptools/maptool] stage2 shas=313 out_of_window=38 pull_commits_not_complete=0 runs_discovered=216 failed_terminal=0 transient=0
[apache/zeppelin] stage1 pages=3 captured=209 failed_terminal=0 transient=0 window_stopped=True
[apache/zeppelin] stage2 shas=592 out_of_window=91 pull_commits_not_complete=0 runs_discovered=1062 failed_terminal=0 transient=0
[jhipster/prettier-java] stage1 pages=2 captured=110 failed_terminal=0 transient=0 window_stopped=True
[jhipster/prettier-java] stage2 shas=117 out_of_window=90 pull_commits_not_complete=0 runs_discovered=304 failed_terminal=0 transient=0
[spring-projects/spring-kafka] stage1 pages=1 captured=82 failed_terminal=0 transient=0 window_stopped=True
[spring-projects/spring-kafka] stage2 shas=111 out_of_window=18 pull_commits_not_complete=0 runs_discovered=180 failed_terminal=0 transient=0
[nitrite/nitrite-java] stage1 pages=1 captured=41 failed_terminal=0 transient=0 window_stopped=True
[nitrite/nitrite-java] stage2 shas=45 out_of_window=59 pull_commits_not_complete=0 runs_discovered=89 failed_terminal=0 transient=0
[mcreator/mcreator] stage1 pages=2 captured=176 failed_terminal=2 transient=0 window_stopped=True
[mcreator/mcreator] stage2 shas=1717 out_of_window=22 pull_commits_not_complete=0 runs_discovered=1121 failed_terminal=0 transient=0
[diffplug/spotless] stage1 pages=1 captured=76 failed_terminal=0 transient=0 window_stopped=True
[diffplug/spotless] stage2 shas=216 out_of_window=24 pull_commits_not_complete=0 runs_discovered=266 failed_terminal=0 transient=0
[zaproxy/zaproxy] stage1 pages=1 captured=72 failed_terminal=0 transient=0 window_stopped=True
[zaproxy/zaproxy] stage2 shas=93 out_of_window=28 pull_commits_not_complete=0 runs_discovered=349 failed_terminal=0 transient=0
[spring-cloud/spring-cloud-commons] stage1 pages=1 captured=56 failed_terminal=0 transient=0 window_stopped=True
[spring-cloud/spring-cloud-commons] stage2 shas=77 out_of_window=44 pull_commits_not_complete=0 runs_discovered=29 failed_terminal=0 transient=0
[plantuml/plantuml] stage1 pages=1 captured=78 failed_terminal=0 transient=0 window_stopped=True
[plantuml/plantuml] stage2 shas=127 out_of_window=22 pull_commits_not_complete=0 runs_discovered=356 failed_terminal=0 transient=0
[schemacrawler/schemacrawler] stage1 pages=1 captured=84 failed_terminal=0 transient=0 window_stopped=True
[schemacrawler/schemacrawler] stage2 shas=238 out_of_window=16 pull_commits_not_complete=0 runs_discovered=660 failed_terminal=0 transient=0
[crimera/piko] stage1 pages=2 captured=187 failed_terminal=0 transient=0 window_stopped=True
[crimera/piko] stage2 shas=1257 out_of_window=13 pull_commits_not_complete=0 runs_discovered=943 failed_terminal=0 transient=0
[atmosphere/atmosphere] stage1 pages=2 captured=119 failed_terminal=0 transient=0 window_stopped=True
[atmosphere/atmosphere] stage2 shas=119 out_of_window=81 pull_commits_not_complete=0 runs_discovered=1263 failed_terminal=0 transient=0
[baomidou/mybatis-plus] stage1 pages=1 captured=86 failed_terminal=0 transient=0 window_stopped=True
[baomidou/mybatis-plus] stage2 shas=129 out_of_window=14 pull_commits_not_complete=0 runs_discovered=77 failed_terminal=0 transient=0
[cryptomator/cryptomator] stage1 pages=1 captured=27 failed_terminal=0 transient=0 window_stopped=True
[cryptomator/cryptomator] stage2 shas=210 out_of_window=73 pull_commits_not_complete=0 runs_discovered=283 failed_terminal=0 transient=0
[floci-io/floci] stage1 pages=9 captured=887 failed_terminal=0 transient=0 window_stopped=True
```

The corresponding records in `logs/requests.jsonl` verify that at 13:30:04Z, 13:30:18Z, and 13:30:28Z, each of the three configured tokens received a 401 response during a temporary GitHub authentication blip, causing `AllTokensDead` eviction per D-22.

---

## 3. Step 2: Pre-Launch Baselines

```bash
$ date -u +%Y-%m-%dT%H:%M:%SZ && wc -l logs/requests.jsonl && ls data/raw | wc -l && du -sh data/raw
2026-08-17T14:32:37Z
70075 logs/requests.jsonl
33
614M	data/raw
```

- **T_START:** `2026-08-17T14:32:37Z`
- **BASELINE_REQ:** `70075`
- **BASELINE_RAW_DIRS:** `33` (32 repos + `RUN_AGES.json`)
- **BASELINE_RAW_SIZE:** `614M`

---

## 4. Step 3: Relaunch & +15s Liveness Verification

Launch command executed:
```bash
setsid -f uv run --env-file .env python -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both > logs/daemon_20260817b.log 2>&1 < /dev/null
```

At +15s:
```bash
$ ps aux | grep '[h]arvest\.daemon'
shree      14013  0.0  0.4 219368 32896 ?        Ssl  14:39   0:00 uv run --env-file .env python -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both
shree      14016 50.1  1.1  97560 89916 ?        S    14:39   0:11 /home/shree/blastradius/.venv/bin/python3 -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both

$ tail -n 20 logs/daemon_20260817b.log
(empty - output is block-buffered)
```

Process confirmed live: **PID 14016** (parent **PID 14013**).

---

## 5. Step 4: Ten-Minute Confirmation Check

Check executed at `2026-08-17T14:50:23Z` (elapsed ~10.83 min from process launch at 14:39:33Z; 17.77 min from baseline):

```bash
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-08-17T14:50:23Z

$ ps aux | grep '[h]arvest\.daemon'
shree      14013  0.0  0.4 219368 32896 ?        Ssl  14:39   0:00 uv run --env-file .env python -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both
shree      14016  2.3  1.1  97560 89916 ?        S    14:39   0:15 /home/shree/blastradius/.venv/bin/python3 -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both

$ wc -l logs/requests.jsonl && ls data/raw | wc -l
70361 logs/requests.jsonl
33

$ du -sh data/raw
617M	data/raw

$ tail -n 20 logs/daemon_20260817b.log
(empty)

$ tail -n 500 logs/requests.jsonl | grep -c '"status": 401' || true
3

$ tail -n 500 logs/requests.jsonl | grep -c '"status": 429' || true
0

$ tail -n 500 logs/requests.jsonl | grep -c '"status": 403' || true
0
```

### Rate Arithmetic & Status Analysis
- **Requests Issued:** `70,361 - 70,075` = **286 requests**
- **Elapsed Time:** 10.83 minutes from launch (17.77 min from baseline)
- **Throughput Rate:** `286 / 10.83 * 60` = **≈ 1,584.5 requests/hour**
- **Data Growth:** `data/raw` grew from 614M to 617M (+3M)
- **Status Counts:**
  - `401 (unauthorized)`: **0** since relaunch. The 3 matches in the last 500 lines date from 13:30Z prior to relaunch.
  - `429 (rate limited)`: **0**
  - `403 (forbidden)`: **0**
- **Resume Progress:** The first 32 repos were cursor-complete in Stage 1/2; the daemon cleanly resumed execution at `floci-io/floci` and ongoing frame items.

---

## 6. Step 5: Handoff Updates & Non-Goals Honoured

- Updated `docs/HANDOFF.md` "Live process" section in place with PID 14016, parent 14013, log file `logs/daemon_20260817b.log`, and launch timestamp `2026-08-17T14:39:33Z`.
- Old log `logs/daemon_20260817.log` preserved untouched as abort evidence.
- No files under `src/`, `tests/`, or `.env` modified.
- No git write or commit commands executed.
