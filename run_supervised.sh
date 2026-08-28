#!/usr/bin/env bash
STAGE="${1:-4}"
LANG_ARG="${2:-}"
LOCKFILE="logs/supervisor.pid"

if [ -f "$LOCKFILE" ]; then
  PID=$(cat "$LOCKFILE" 2>/dev/null)
  if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
    echo "[supervisor] $(date -u +%FT%TZ) supervisor already running (PID $PID); exiting"
    exit 0
  else
    echo "[supervisor] $(date -u +%FT%TZ) stale lockfile found (PID ${PID:-empty} is dead); continuing"
  fi
fi

mkdir -p "$(dirname "$LOCKFILE")"
echo $$ > "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT

EXTRA_ARGS=()
[ -n "$LANG_ARG" ] && EXTRA_ARGS+=(--lang "$LANG_ARG")

while true; do
  echo "[supervisor] $(date -u +%FT%TZ) starting daemon (stage $STAGE${LANG_ARG:+ lang $LANG_ARG})"
  uv run --env-file .env python -m src.harvest.daemon \
    --repos data/frame/frame_v1.csv --limit 300 --stage "$STAGE" "${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}"
  echo "[supervisor] $(date -u +%FT%TZ) daemon exited, sleeping 120s"
  sleep 120
done
