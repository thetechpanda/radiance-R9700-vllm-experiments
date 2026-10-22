#!/usr/bin/env bash
# Adapted from recovered campaign wrappers; server configuration is supplied separately.
set -euo pipefail
PROFILE=${1:?Usage: run_grid.sh dual-nospec|dual-mtp4|single-mtp4}
case "$PROFILE" in dual-nospec|dual-mtp4|single-mtp4) ;; *) echo "Unknown profile" >&2; exit 2;; esac
: "${BASE_URL:?Set the already running API base URL without /v1}"
: "${MODEL:?Set its API model ID}"
: "${RESULTS_DIR:?Set a fresh private result directory, e.g. src/reproductions/run-1}"
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
CONTEXT_LIMIT=${CONTEXT_LIMIT:-131070}
CONTAINER=${CONTAINER:-radiance}
mkdir -p "$RESULTS_DIR"
RESULTS_DIR=$(cd -- "$RESULTS_DIR" && pwd)
CSV="$RESULTS_DIR/bench-results.csv"
[[ ! -e "$CSV" ]] || { echo "Choose fresh RESULTS_DIR" >&2; exit 2; }
for N in 1 2 3 4; do
  CAP=126000
  if [[ "$PROFILE" == single-mtp4 ]]; then case "$N" in 3) CAP=122630;; 4) CAP=88913;; esac; fi
  python3 "$SCRIPT_DIR/bench_agents4.py" --base-url "$BASE_URL" --model "$MODEL" \
    -n "$N" --max-tokens "$CAP" --max-model-len "$CONTEXT_LIMIT" \
    --label "$PROFILE-n$N" --csv-append "$CSV" --container "$CONTAINER" > "$RESULTS_DIR/n$N.log" 2>&1
 done
if [[ "$PROFILE" == dual-nospec ]]; then
  python3 "$SCRIPT_DIR/bench_agents4.py" --base-url "$BASE_URL" --model "$MODEL" \
    -n 4 --images --max-tokens 126000 --max-model-len "$CONTEXT_LIMIT" \
    --label "$PROFILE-n4-images" --csv-append "$CSV" --container "$CONTAINER" > "$RESULTS_DIR/n4-images.log" 2>&1
fi
python3 - "$CSV" <<'PY'
import csv,sys
with open(sys.argv[1],newline='') as f: rows=list(csv.DictReader(f))
if not rows or any(int(r['errors']) for r in rows):raise SystemExit('Recorded request errors: inspect private logs')
print(f'{len(rows)} cells without recorded request errors; review depth and latency separately')
PY
