#!/usr/bin/env bash
# Generic, editable Podman example. Set IMAGE and MODEL_PATH for your machine.
set -euo pipefail
: "${IMAGE:?Set IMAGE to a compatible Radiance image tag}"
: "${MODEL_PATH:?Set MODEL_PATH to the model directory mounted inside the container}"
MODEL_ID="${MODEL_ID:-local-model}"
PORT="${PORT:-8000}"
GPU_DEVICES=(--device=/dev/kfd --device=/dev/dri --group-add=video)
# Add your own model/cache volume mounts and model-specific vLLM arguments.
exec podman run --rm --name radiance-example \
  "${GPU_DEVICES[@]}" --security-opt=seccomp=unconfined --ipc=host \
  -p "127.0.0.1:${PORT}:8000" \
  -v "${MODEL_PATH}:/models/model:ro" \
  "${IMAGE}" /models/model \
  --served-model-name "${MODEL_ID}" --max-model-len 32768 \
  --gpu-memory-utilization 0.90
