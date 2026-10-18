#!/usr/bin/env bash
# Run one seeded Falling Blocks task in a preconfigured Pi coding-agent container.
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: PI_IMAGE=... PI_MODEL=... PI_PROVIDER=... $0 AGENT_ID SEED [TIMEOUT_SECONDS]" >&2
  exit 2
fi
: "${PI_IMAGE:?Set PI_IMAGE to a container image with pi-coding-agent installed}"
: "${PI_MODEL:?Set PI_MODEL to the served model ID}"
: "${PI_PROVIDER:?Set PI_PROVIDER to the configured Pi provider name}"

AGENT_ID=$1
SEED=$2
TIMEOUT_SECONDS=${3:-3600}
WORK_ROOT=${WORK_ROOT:-results/falling_blocks}
PODMAN=${PODMAN:-podman}
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
mkdir -p "$WORK_ROOT"
WORK_ROOT=$(cd -- "$WORK_ROOT" && pwd)
WORK_DIR="$WORK_ROOT/agent-$AGENT_ID"
mkdir -p "$WORK_DIR" "$WORK_DIR/.sessions"
python3 "$SCRIPT_DIR/falling_blocks_prompt.py" --seed "$SEED" --output "$WORK_DIR/prompt.txt"
PROMPT=$(<"$WORK_DIR/prompt.txt")

set +e
timeout "$TIMEOUT_SECONDS" "$PODMAN" run --rm \
  --name "falling_blocks-agent-$AGENT_ID" \
  --volume "$WORK_DIR:/work:Z" \
  --workdir /work \
  --env PI_CODING_AGENT_SESSION_DIR=/work/.sessions \
  "$PI_IMAGE" \
  pi --mode json --provider "$PI_PROVIDER" --model "$PI_MODEL" \
     --session-dir /work/.sessions "$PROMPT" \
  >"$WORK_DIR/events.jsonl" 2>"$WORK_DIR/agent.log"
status=$?
set -e
printf '%s\n' "$status" > "$WORK_DIR/exit-status.txt"
printf 'agent=%s seed=%s status=%s output=%s\n' "$AGENT_ID" "$SEED" "$status" "$WORK_DIR"
exit "$status"
