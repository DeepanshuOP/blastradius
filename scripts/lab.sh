#!/usr/bin/env bash
# Start the Live Lab for live use: build the site, serve it on 127.0.0.1:3000, print the URL once it answers.
# Ctrl-C stops it. Needs Node >= 18 and `npm ci` in demo-web/ once.
set -euo pipefail
cd "$(dirname "$0")/../demo-web"
URL="http://127.0.0.1:3000"
[ -d node_modules ] || { echo "demo-web/node_modules is missing: run 'cd demo-web && npm ci' once" >&2; exit 1; }
npm run build
npm start &
PID=$!
trap 'kill "$PID" 2>/dev/null || true' EXIT INT TERM
for _ in $(seq 1 60); do
  if curl -fsS -o /dev/null "$URL/api/lab/repos"; then
    echo
    echo "Live Lab ready: $URL  (Ctrl-C to stop)"
    wait "$PID"
    exit 0
  fi
  kill -0 "$PID" 2>/dev/null || { echo "the site exited before it was ready" >&2; exit 1; }
  sleep 1
done
echo "the site did not answer on $URL within 60 s" >&2
exit 1
