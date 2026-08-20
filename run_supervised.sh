#!/usr/bin/env bash
while true; do
  echo "[supervisor] $(date -u +%FT%TZ) starting daemon"
  uv run --env-file .env python -m src.harvest.daemon \
    --repos data/frame/frame_v1.csv --limit 300 --stage both
  echo "[supervisor] $(date -u +%FT%TZ) daemon exited, sleeping 120s"
  sleep 120
done
