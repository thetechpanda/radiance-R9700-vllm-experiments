#!/usr/bin/env bash
# Adapted M2 recipe; creates model output and does not replace a service.
set -euo pipefail
: "${RADIANCE_IMAGE:?Set the recorded radiance image by digest}"
: "${MODEL_DIR:?Set the local model snapshot directory}"
: "${RAD_OUTPUT:?Set a new .rad output path in an existing directory}"
MODEL_DIR=$(cd -- "$MODEL_DIR" && pwd)
OUTPUT_DIR=$(cd -- "$(dirname -- "$RAD_OUTPUT")" && pwd)
OUTPUT_NAME=$(basename -- "$RAD_OUTPUT")
[[ ! -e "$OUTPUT_DIR/$OUTPUT_NAME" ]] || { echo "Refusing to overwrite model" >&2; exit 2; }
podman run --rm -v "$MODEL_DIR:/input:ro" -v "$OUTPUT_DIR:/output" \
 --security-opt seccomp=unconfined --entrypoint rad-convert "$RADIANCE_IMAGE" \
 /input -o "/output/$OUTPUT_NAME" --recipe /opt/radiance/share/radiance/recipes/q38-27b-w4a16.recipe -v
podman run --rm -v "$OUTPUT_DIR:/output:ro" --entrypoint rad-info "$RADIANCE_IMAGE" "/output/$OUTPUT_NAME"
