---
layout: default
title: "FP8 KV cache: memory, coding-agent calibration and reproduction"
---

# FP8 KV cache: memory, coding-agent calibration and reproduction

For several agents with roughly 131k tokens of history each, **KV cache is a central memory and bandwidth cost**. Weight quantisation and KV quantisation are separate: the INT4 model still needs an explicit FP8 cache configuration. The setting is **FP8 KV**, not “FPV8”.

## Why FP8 matters for capacity

A BF16 K or V element uses two bytes; FP8 uses one, plus scale/metadata overhead. With compact storage, the attention KV payload is therefore roughly half the size. This can leave more room in VRAM and a host-RAM offload tier, or fit more cached context in the same budget. It does not halve model weights, hybrid recurrent state, graph buffers or total process RAM. The [vLLM KV-cache documentation](https://docs.vllm.ai/en/stable/features/quantization/quantized_kvcache/) describes the general mechanism.

**The later deployment was reported to approximately double KV-cache capacity with FP8.** That is the benefit this guide aims to reproduce: more cached tokens per GiB, or less memory for a fixed amount of attention history. The exact BF16/FP8 startup pair for that observation is not included here, so it should not be turned into a precise benchmark ratio for every current profile.

An **earlier** R9700 comparison recorded 164,850 versus 167,553 logical GPU KV tokens and attributed the near-flat capacity to BF16-sized padded pages. That finding describes that older allocation path only; it does not override the later doubling observation. The archived runtime guide also describes FP8 as packing more KV per GiB. Padding, hybrid-state alignment and speculative reservations can change the total engine capacity ratio, even when attention K/V storage is halved.

A fixed CPU tier remains fixed: configuring 10 GiB does not automatically release 5 GiB when FP8 is enabled. With compact offload blocks, that budget could hold more tokens; to reclaim host RAM itself, establish the reduced working-set requirement and lower the tier budget in a separate measured trial. Compare bytes per block, token capacity and actual host/shared-memory use, not the dtype label alone.

In the historical four-agent test at about 126k context, FP8 KV increased repeat per-agent decode from 32.9 to 41.8 tokens/s and reduced mean TTFT from 58.7 to 45.9 seconds. At 32k it was about 10% slower. Those are bounded results for that model/backend; they are neither universal speedups nor evidence that calibration by itself creates a speedup. Enabling FP8 changes storage/attention behaviour; calibration supplies representative numerical scales.

## How the recorded calibration worked

The workflow reconstructed coding-agent conversations from an OpenCode session database, retaining user/assistant text and tool-output content. It bounded record and tool-output sizes to fit a short calibration window. The original session exports and calibration artefacts are private and are not distributed here.

The Radiance calibrator runs the **exact target checkpoint** eagerly with full-precision KV, prefix caching disabled, and hooks immediately before full-attention layers. It observes BF16 Q/K/V activation maxima and combines observations across tensor-parallel ranks. For its default OCP E4M3 convention it writes positive per-layer scales with 5% headroom:

```text
scale = max(observed_absolute_max × 1.05 / 448, 1e-12)
```

The runtime handles its expected ROCm FP8 representation. Do not substitute another format's maximum or convert scales twice. The sidecar's sibling `.manifest.json` binds its checksum to the source checkpoint and records corpus hash, observations, calibration settings and software versions.

The recorded Swift INT4 deployment used a **Q/K/V-only** sidecar: its compressed-tensors KV method did not expose `prob_scale`. Other attention/checkpoint paths can accept probability scales. This is a backend compatibility distinction, not permission to reuse another model's calibration.

## 1. Build a representative corpus from your own agent history

Export a representative selection of sessions from your coding agent. Use the agent's supported export or a read-only database copy; database schemas vary. Convert the result into JSONL, one independent example per line. The calibrator accepts either rendered `text`, or `messages` with optional top-level `tools`:

```json
{"id":"code-review-01","messages":[{"role":"system","content":"You are a coding assistant."},{"role":"user","content":"Review this function and its test failure."},{"role":"assistant","content":"I will inspect the code and traceback."},{"role":"user","content":"Tool output: assertion failed at test_parser.py:42 ..."}]}
{"id":"rendered-session-02","text":"A representative conversation rendered with the deployment chat template ..."}
```

These two lines illustrate the format, **not an adequate calibration corpus**. Include real code, diffs, tracebacks, terminal output, repository instructions, JSON, reasoning text where actually replayed, and the languages and tool schemas your agents use. Preserve real tool-call structure and matching tool-call IDs when exporting structured tool messages. Do not invent orphan `tool` messages; use correctly templated text if the exporter cannot preserve that structure. Replayed tool output matters because it often dominates long coding histories.

Remove credentials and content you cannot use. Keep the corpus private; synthetic placeholders alone will not reproduce your traffic's activation ranges. Split by **whole session** into calibration and held-out validation sets so overlapping prefixes from the same session do not leak between them. Include several projects and task types rather than only the longest or most repetitive sessions.

Bound each rendered record using the exact model tokenizer and chat template, including tool definitions and the generation prompt. Stay below the calibration `--max-model-len` with room for the generated token. Character count is only a rough prefilter; the archived exporter used a character cap, so it was not a general token-limit guarantee. Do not split JSON/tool messages or blindly repeat one session to simulate long-context coverage.

The original calibration used a roughly 13k effective window within a 16,384-token limit. That was shorter than serving histories near 126k. Longer representative calibration records are a sensible follow-up, not an already proven improvement: compare per-layer `observed_amax` and held-out quality. On one 32 GiB card, begin conservatively; BF16 calibration KV can require substantially more memory than FP8 serving. Do not attempt four 131k calibration sequences simultaneously.

## 2. Calibrate in an explicit maintenance window

These commands **stop inference** and consume the selected GPU. They document reproduction; they were not run as part of this documentation update. Run them on the GPU host after active workloads have finished. Use a Radiance image containing `radiance_kv_calibration`; these commands are fork-specific, not stock vLLM commands. Keep the serving image's required model/kernel environment settings when creating the calibration container.

Set operator-owned paths. `MODEL_DIR` must be the exact pinned local checkpoint, with all symlink targets available under the same container path; do not select an arbitrary cached snapshot. `CORPUS` must be the prepared private JSONL. `TOOLS_DIR` points to this release's `scripts` directory.

```bash
IMAGE=localhost/vllm-radiance:rocm10
MODEL_DIR=/path/to/pinned-checkpoint
CORPUS=/path/to/private-agent-calibration.jsonl
CALIB_DIR=/path/to/new-calibration-output
TOOLS_DIR=/path/to/release/scripts
GPU_UUID=GPU-your-selected-card-uuid  # Replace with the UUID reported by rocminfo.
mkdir -p "$CALIB_DIR"

# Inspect the installed CLI before choosing memory/window settings.
podman exec vllm-radiance.1 python -m radiance_kv_calibration calibrate --help

# Stop clients first, then stop the serving service and release its GPU memory.
systemctl stop radiance-vllm.service
podman stop --ignore --time 120 vllm-radiance.1

podman run --rm --ipc=host \
  --device=/dev/kfd --device=/dev/dri/card1 --device=/dev/dri/renderD129 \
  --security-opt=seccomp=unconfined --group-add=video \
  -e "ROCR_VISIBLE_DEVICES=$GPU_UUID" -e HIP_VISIBLE_DEVICES=0 \
  -e RADIANCE_USE_R4D=1 \
  -v "$MODEL_DIR:$MODEL_DIR:ro" \
  -v "$CORPUS:/fixtures/agent-history.jsonl:ro" \
  -v "$CALIB_DIR:/calibration:rw" \
  --entrypoint python "$IMAGE" \
  -m radiance_kv_calibration calibrate \
  --model "$MODEL_DIR" --quantization auto \
  --corpus /fixtures/agent-history.jsonl \
  --output /calibration/candidate-full.safetensors \
  --tensor-parallel-size 1 --attention-backend R4D \
  --max-model-len 16384 --max-num-batched-tokens 256 \
  --batch-size 1 --gpu-memory-utilization 0.85 --seed 17
```

The device nodes above are the recorded **GPU A** mapping; supply that card’s actual UUID and replace both nodes and UUID together for another host/card. Explicit TP=1 matters: the inspected calibrator defaults to TP=2. Batch size 1 and batched-token limit 256 are a conservative starting proposal, not the original batch-four recipe or a newly qualified throughput profile. If calibration cannot fit, lower its batch/window or resolve model-loading overhead; do not silently switch checkpoints. Use a fresh output name for every attempt; the calibrator refuses overwrites.

## 3. Verify and, where required, derive a Q/K/V-only sidecar

First verify the full output against the checkpoint, without loading an inference engine:

```bash
podman run --rm \
  -v "$MODEL_DIR:$MODEL_DIR:ro" -v "$CALIB_DIR:/calibration:ro" \
  --entrypoint python "$IMAGE" \
  -m radiance_kv_calibration verify /calibration/candidate-full.safetensors \
  --model "$MODEL_DIR"
```

For the recorded compressed-tensors Q/K/V-only path, use the supplied CPU-only derivation helper. It verifies the source, retains complete Q/K/V triplets, preserves the model/corpus/observation provenance, and writes a **new** sidecar and checksum manifest. It does not perform calibration or modify model weights.

```bash
podman run --rm \
  -v "$MODEL_DIR:$MODEL_DIR:ro" -v "$CALIB_DIR:/calibration:rw" \
  -v "$TOOLS_DIR:/release-scripts:ro" \
  --entrypoint python "$IMAGE" \
  /release-scripts/make_qkv_sidecar.py \
  /calibration/candidate-full.safetensors /calibration/candidate-qkv.safetensors \
  --model "$MODEL_DIR"

podman run --rm \
  -v "$MODEL_DIR:$MODEL_DIR:ro" -v "$CALIB_DIR:/calibration:ro" \
  --entrypoint python "$IMAGE" \
  -m radiance_kv_calibration verify /calibration/candidate-qkv.safetensors \
  --model "$MODEL_DIR"
```

For another backend, retain its supported full artefact instead. Check the model's attention parameter names before filtering. Do not edit an existing sidecar in place or disable checksum/model verification to conceal incompatibility. The manifest filename replaces `.safetensors` with `.manifest.json`.

## 4. Enable both the dtype and the verified scales

The serving container needs the pair mounted together and both settings:

```bash
-e RADIANCE_FP8_KV_SCALES=/calibration/candidate-qkv.safetensors \
-e RADIANCE_FP8_KV_SCALES_VERIFY=1 \
-v "$CALIB_DIR:/calibration:ro"
# Alongside the normal model/server arguments:
--kv-cache-dtype fp8
```

A scale file does not enable FP8 by itself, and `--kv-cache-dtype fp8` does not establish that your calibrated file was loaded. Confirm the startup log reports calibration loading with verification, the expected dtype and logical cache capacity. The installed service launcher selects a fixed scale basename; explicitly update its configured selection to the **new verified pair** rather than relying on a “newest file” glob. Keep the previous pair and exact startup command for rollback. Until the candidate passes validation, restore the previous service configuration when returning to serving.

## 5. Validate quality, capacity and pressure separately

Compare BF16 KV, FP8 with the backend's documented default scales, and calibrated FP8 where those modes are supported. Hold the checkpoint, image, TP, speculation, scheduling, CPU-tier budget, prompts, cache state and sampling fixed. Do not attribute all BF16-to-FP8 gains to calibration.

Use held-out coding tasks and actual tool-call schemas, deterministic correctness checks, long-context retrieval, and all deployed input types. Record malformed tool calls, NaN/Inf failures, task completion and output quality as well as TTFT and decode rate. Short numerical calibration does not validate 131k-context fidelity.

For memory, record startup logical tokens, allocated attention/state block sizes, GPU memory, host MemAvailable, shared-memory use, swap activity, and CPU KV occupancy. Preallocated pools may keep the same byte budget while token capacity changes. Compare per-agent context/completion and CPU offload allocation failures at the intended concurrency. If padded pages remain, say so; do not promise reclaimed RAM from FP8 alone.

Retain image digest, exact model revision, corpus hash/split, tokenizer/template version, CLI settings, sidecar/manifest hashes and held-out results. This makes a calibration reproducible without publishing your private conversations. Recalibrate when the target checkpoint or activation path changes; reverify compatibility and quality after runtime/backend changes.

<!-- NAVIGATION START -->

[Home](../index.md) · [Compare](RADIANCE-VS-VLLM.md) · [vllm-radiance](VLLM-RADIANCE.md) · [radiance](RADIANCE.md) · [Charts](CHARTS.md) · [Stuff for nerds](CODE-CORNER.md) · [Disclosure](REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
