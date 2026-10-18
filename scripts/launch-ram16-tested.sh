#!/usr/bin/env bash
# Rewritten single-R9700 launch profile for the 16 GiB shared-memory tests.
# Supply a compatible Radiance image and local model directory at invocation.
set -euo pipefail

: "${IMAGE:?Set IMAGE to the compatible Radiance container image}"
: "${MODEL_PATH:?Set MODEL_PATH to the local model directory}"
MODEL_ID="${MODEL_ID:-local-model}"
PORT="${PORT:-8000}"
GPU_ARCH="${GPU_ARCH:-gfx1201}"
GPU_CARD_DEVICE="${GPU_CARD_DEVICE:-/dev/dri/card1}"
GPU_RENDER_DEVICE="${GPU_RENDER_DEVICE:-/dev/dri/renderD129}"
GPU_UUID="${GPU_UUID:-}"
KV_SCALE_FILE="${KV_SCALE_FILE:-}"
CACHE_PATH="${CACHE_PATH:-}"

mounts=(-v "${MODEL_PATH}:/models/model:ro")
if [[ -n "$CACHE_PATH" ]]; then
  mounts+=(-v "${CACHE_PATH}:/root/.cache/vllm")
fi
extra_env=()
if [[ -n "$GPU_UUID" ]]; then
  extra_env+=(-e "ROCR_VISIBLE_DEVICES=$GPU_UUID" -e HIP_VISIBLE_DEVICES=0)
fi
kv_args=()
if [[ -n "$KV_SCALE_FILE" ]]; then
  manifest="${KV_SCALE_FILE%.safetensors}.manifest.json"
  [[ -f "$KV_SCALE_FILE" && -f "$manifest" ]] || { echo "Scale sidecar and matching manifest are required" >&2; exit 2; }
  mounts+=(-v "${KV_SCALE_FILE}:/run/kv-scales.safetensors:ro" -v "${manifest}:/run/kv-scales.manifest.json:ro")
  extra_env+=(-e RADIANCE_FP8_KV_SCALES=/run/kv-scales.safetensors -e RADIANCE_FP8_KV_SCALES_VERIFY=1)
  kv_args+=(--kv-cache-dtype fp8)
fi

exec podman run --rm --name radiance-ram16-tested \
  --device=/dev/kfd --device="$GPU_CARD_DEVICE" --device="$GPU_RENDER_DEVICE" \
  --security-opt=seccomp=unconfined --group-add=video --ipc=host \
  -p "127.0.0.1:${PORT}:8000" \
  "${mounts[@]}" \
  -e PYTHONHASHSEED=0 -e VLLM_LOG_STATS_INTERVAL=1 \
  -e GPU_ARCHS="$GPU_ARCH" -e AITER_ROCM_ARCH="$GPU_ARCH" \
  -e AMDGPU_TARGETS="$GPU_ARCH" -e HIP_ARCHITECTURES="$GPU_ARCH" \
  -e PYTORCH_ROCM_ARCH="$GPU_ARCH" \
  -e VLLM_ROCM_USE_AITER=1 \
  -e VLLM_ROCM_USE_AITER_MHA=0 -e VLLM_ROCM_USE_AITER_PAGED_ATTN=0 \
  -e VLLM_ROCM_USE_AITER_MOE=0 -e VLLM_ROCM_USE_AITER_LINEAR=0 \
  -e VLLM_ROCM_USE_AITER_RMSNORM=0 -e VLLM_ROCM_USE_AITER_FP8BMM=0 \
  -e VLLM_ROCM_USE_AITER_FP4BMM=0 -e VLLM_ROCM_USE_AITER_TRITON_ROPE=0 \
  -e RADIANCE_USE_R4D=1 -e RADIANCE_USE_R4D_GDN=1 \
  -e RADIANCE_R4D_REPORT=1 -e RADIANCE_FAST_DRAFT=1 \
  -e RADIANCE_SKINNY_GEMM=1 -e RADIANCE_GDN_META=1 \
  -e RADIANCE_GDN_MERGE_INPROJ=1 -e RADIANCE_GDN_FUSED_UPDATE=1 \
  -e RADIANCE_GDN_FUSED_MAX_ITEMS=32 -e RADIANCE_GDN_SHARED_BUILD=1 \
  -e RADIANCE_TOPK_TRITON_MIN_ROWS=1 -e RADIANCE_TOPK_COMPOSITE=1 \
  "${extra_env[@]}" \
  "$IMAGE" /models/model \
  --tensor-parallel-size 1 --served-model-name "$MODEL_ID" \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3 \
  --max-model-len 131070 --gpu-memory-utilization 0.995 --max-num-seqs 4 \
  --max-num-batched-tokens 16384 --enable-prefix-caching \
  --enable-logging-iteration-details --kv-cache-metrics --cudagraph-metrics \
  --per-request-spec-decode-metrics summary \
  --compilation-config '{"max_cudagraph_capture_size":64,"pass_config":{"fuse_norm_quant":false}}' \
  --speculative-config '{"method":"mtp","num_speculative_tokens":4,"attention_backend":"R4D","disable_padded_drafter_batch":true}' \
  --kv-transfer-config '{"kv_connector":"OffloadingConnector","kv_role":"kv_both","kv_connector_extra_config":{"spec_name":"TieringOffloadingSpec","cpu_bytes_to_use":17179869184,"blocks_per_chunk":1,"eviction_policy":"arc"}}' \
  --long-prefill-token-threshold 2048 \
  "${kv_args[@]}"
