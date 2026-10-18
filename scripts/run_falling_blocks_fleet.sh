#!/usr/bin/env bash
# Launch a local fleet of Falling Blocks coding tasks against an already running server.
set -uo pipefail

if [[ $# -gt 4 ]]; then
  echo "Usage: PI_IMAGE=... PI_MODEL=... PI_PROVIDER=... $0 [AGENTS=4] [SEED_BASE=100] [TIMEOUT_SECONDS=3600] [HEALTH_URL=http://127.0.0.1:8000/health]" >&2
  exit 2
fi
: "${PI_IMAGE:?Set PI_IMAGE to a container image with pi-coding-agent installed}"
: "${PI_MODEL:?Set PI_MODEL to the served model ID}"
: "${PI_PROVIDER:?Set PI_PROVIDER to the configured Pi provider name}"

AGENTS=${1:-4}
SEED_BASE=${2:-100}
TIMEOUT_SECONDS=${3:-3600}
HEALTH_URL=${4:-http://127.0.0.1:8000/health}
WORK_ROOT=${WORK_ROOT:-"results/falling_blocks-$(date -u +%Y%m%dT%H%M%SZ)"}
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

if ! command -v curl >/dev/null 2>&1 || ! curl --fail --silent --show-error "$HEALTH_URL" >/dev/null; then
  echo "Server health check failed: $HEALTH_URL" >&2
  exit 1
fi
mkdir -p "$WORK_ROOT"
WORK_ROOT=$(cd -- "$WORK_ROOT" && pwd)
export WORK_ROOT PI_IMAGE PI_MODEL PI_PROVIDER

pids=()
ids=()
for ((i=0; i<AGENTS; i++)); do
  "$SCRIPT_DIR/run_falling_blocks_agent.sh" "$i" "$((SEED_BASE+i))" "$TIMEOUT_SECONDS" &
  pids+=("$!")
  ids+=("$i")
done

failed=0
for i in "${!pids[@]}"; do
  if wait "${pids[$i]}"; then
    :
  else
    status=$?
    printf 'agent=%s failed with status %s\n' "${ids[$i]}" "$status" >&2
    failed=1
  fi
done
printf 'work_root=%s agents=%s seed_base=%s\n' "$WORK_ROOT" "$AGENTS" "$SEED_BASE"
exit "$failed"
