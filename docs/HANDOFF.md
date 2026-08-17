
# BlastRadius — rolling agent handoff

Read this first. Append newest entries at the bottom. Never rewrite history.

## Live process — do not stop it
Harvester daemon: PID 7217 (parent 7214), launched 2026-08-17T06:50:11Z.
    setsid nohup uv run --env-file .env python -m src.harvest.daemon \
      --repos data/frame/frame_v1.csv --limit 300 --stage both \
      > logs/daemon_20260817.log 2>&1 < /dev/null &
Stages 1+2 only (stage 3 deferred per D-23). Measured ~3,900 req/hr at launch.
The log file is block-buffered and will look empty even when healthy — verify
liveness with `ps aux | grep '[h]arvest\.daemon'`, not with the log.

## State at switchover to Antigravity
HEAD e711a6c · 152 tests passing · all pushed · docs/session/ untracked.
Review 1 is 2026-08-19. Priorities: T0.5a dashboard, T0.7 attrition funnel,
T1.1g normalize_test_id.

## Log

- 2026-08-17 · Gemini 3.7 Flash · T0.5a · Implemented read-only Streamlit corpus dashboard (dashboard.py) with 7 panels and lock-safe read-only queries · touched dashboard.py, docs/session/2026-08-17-t05a-dashboard.md, docs/HANDOFF.md · 152 tests passing (baseline) · uncommitted · Next: T0.7 attrition funnel or review dashboard demo.
- 2026-08-17 · Gemini 3.7 Flash · T0.5a storage fix · Corrected storage panel in dashboard.py to report on-disk block-allocated usage vs apparent size, file/dir counts, and on-disk 90-day projection with Stage 1+2 metadata caveats · touched dashboard.py, docs/session/012-2026-08-17-t05a-storage-fix.md, docs/HANDOFF.md · 152 tests passing (baseline) · uncommitted · Next: T0.7 attrition funnel.
- 2026-08-17 · Gemini 3.7 Flash · T0.7 · Implemented analysis/attrition_funnel.py to dynamically regenerate the language-stratified attrition funnel table from data/frame/ artefacts; emitted paper/generated/attrition_funnel.md · touched analysis/attrition_funnel.py, paper/generated/attrition_funnel.md, docs/session/013-2026-08-17-t07-attrition-funnel.md, docs/HANDOFF.md · 152 tests passing (predicted 152) · uncommitted · Next: T1.1g normalize_test_id.

