#!/usr/bin/env bash
# Refresh E3 results from the live runner (~/br-e3) without touching it and without committing anything.
#   1. copy its append-only LLM caches and usage ledger into this checkout (read-only on ~/br-e3)
#   2. replay them offline (BR_OFFLINE=1, replay mode: no network, no model call): make repair-eval
#   3. repair-eval and figures run against a scratch copy of data/seeded, so they never queue behind the live run's lock
#   4. make demo-data, python -m analysis.cost_report
#   5. print the primary-test block and n per model/variant
# The operator reviews `git status` and commits.
set -euo pipefail
SRC="${BR_E3_DIR:-$HOME/br-e3}"
cd "$(dirname "$0")/.."
REPO="$PWD"

[ -d "$SRC/eval/llm_cache" ] || { echo "e3-sync: $SRC/eval/llm_cache not found (set BR_E3_DIR)" >&2; exit 1; }
echo "== copy caches from $SRC/eval/llm_cache"
shopt -s nullglob
for f in "$SRC"/eval/llm_cache/*.jsonl; do
  cp -f "$f" "$REPO/eval/llm_cache/$(basename "$f")"
  echo "   $(basename "$f"): $(wc -l < "$f") records"
done

SCRATCH="$(mktemp -d "${TMPDIR:-/tmp}/br-seeded-XXXXXX")"
trap 'rm -rf "$SCRATCH"' EXIT
echo "== scratch copy of data/seeded -> $SCRATCH (the live run's repo locks are never taken)"
cp -a "$REPO/data/seeded/." "$SCRATCH/"
# editable installs and script shebangs hold absolute paths: point them at the copy
find "$SCRATCH/venvs" -type f \( -name '*.pth' -o -path '*/bin/*' -o -name '*.cfg' -o -name 'direct_url.json' \) -print0 \
  | xargs -0 sed -i "s#$REPO/data/seeded#$SCRATCH#g" 2>/dev/null || true
# the copy may have caught the live run with a diff applied: restore each working tree (in the copy only)
for r in "$SCRATCH"/repos/*/; do git -C "$r" checkout -q -- . ; done

echo "== make repair-eval (BR_OFFLINE=1, replay mode, scratch seeded dir)"
BR_OFFLINE=1 BR_SEEDED_DIR="$SCRATCH" make repair-eval
echo "== make figures"
BR_SEEDED_DIR="$SCRATCH" make figures

echo "== make demo-data"
make demo-data
echo "== cost report"
BR_OFFLINE=1 uv run python -m analysis.cost_report

echo "== primary test and n per model/variant (paper/generated/rq4_repair.md)"
uv run python - <<'PY'
import re
from pathlib import Path
t = Path("paper/generated/rq4_repair.md").read_text(encoding="utf-8").splitlines()
for i, line in enumerate(t):
    if line.startswith("### Primary test"):
        j = i + 1
        while j < len(t) and not t[j].startswith("### "):
            j += 1
        print("\n".join(t[i:j]).strip())
for line in t:
    m = re.match(r"#+ (.*, (?:standard|hard) variant \(n = \d+ tasks\))", line)
    if m:
        print(m.group(1))
PY
echo
echo "e3-sync done. Nothing was committed; review 'git status' and commit the synced caches and outputs."
