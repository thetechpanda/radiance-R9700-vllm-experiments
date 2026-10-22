---
layout: default
title: "Rewritten scripts and launch instructions"
---

# Rewritten scripts and launch instructions

This release includes both compact replacement tools and explicitly labelled [recovered originals/adapters](../scripts/recovered/README.md). The [code corner](CODE-CORNER.md) inventories every shipped script and gives worked examples; the [disclosure](REPRODUCIBILITY.md) explains the remaining gaps. They preserve the useful workflows while avoiding captured host configuration, raw conversation fixtures, credentials, and machine-local paths.

The primary historical server runs studied the hybrid **Qwen3.8 27B** checkpoint [`ukisai/Swift-1.5-Qwen3.8-27b-INT4`](https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-27b-INT4). The checkpoint and calibration artifacts are not included. For comparable measurements, use the same model variant with the matching server configuration; another model is a separate experiment. See the [Hugging Face model inventory](MODELS.md) for related models and drafters.

## Choose the documented profile

| Purpose | Launcher / reference |
|---|---|
| ROCm 10.1 single GPU A, 10 GiB CPU tier, MTP=4 | [`launch-tp1-rocm10.sh`](../scripts/launch-tp1-rocm10.sh) |
| Historical ROCm 7.14 RAM16 reproduction | [`launch-ram16-tested.sh`](../scripts/launch-ram16-tested.sh); requires sufficient host headroom |
| Portable dual-card profile | [`launch-tp2-live.sh`](../scripts/launch-tp2-live.sh); compare its parameters with the intended campaign before use |

The [Podman guide](../PODMAN.md) explains installed service scripts and container lifecycle. The [latest results](FINAL-REPORT-20261018.md) distinguish the earlier 8 GiB dual campaign from the later 10 GiB comparison. A launcher file is not evidence of the current running configuration. The historical 16 GiB profile is not the remedy for this host's later slowdown.

## Synthetic agent benchmark

```bash
python3 scripts/agent_bench.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model YOUR_MODEL_ID --agents 4 --turns 24 \
  --max-tool-chars 12000 --output results/run.json
```

Options:

- `--agents`: concurrent synthetic agents.
- `--turns`: turns per agent.
- `--max-tool-chars`: generated tool-result text appended to each prompt.
- `--timeout`: HTTP request timeout in seconds.
- `--api-key-env`: environment variable name for an API key; the value is used only in the Authorisation header and never saved.
- `--output`: writes an aggregate JSON summary. The report omits prompts and model responses.

The benchmark uses deterministic generated records, not captured sessions. It requires a streaming `/chat/completions` endpoint. When the server does not report token usage, output token counts are approximated from generated response characters; the report does not claim exact counts in that case.

## `radiance-top` monitor

```bash
python3 scripts/radiance-top --url http://127.0.0.1:8000/metrics
python3 scripts/radiance-top --plain --url http://127.0.0.1:8000/metrics --interval 2
python3 scripts/radiance-top --url http://127.0.0.1:8001/metrics --api-key "$RADIANCE_API_KEY"
```

The TUI refreshes model request/KV counters and probes AMD GPU utilisation/VRAM through Linux DRM sysfs when available. `q` or Escape quits. `--plain` prints one line per interval for log capture. Metrics names vary across vLLM/Radiance versions; unknown fields remain labelled unavailable instead of being guessed.

**radiance engine.** The monitor auto-detects the radiance engine (the `radiance:` metric families) and remaps names. The PP and TG now-lanes read the engine's own steady-window gauges — `radiance:prefill_tokens_per_second` and `radiance:decode_tokens_per_second` — while the window columns credit counters: prompt intake (prefill credit plus cache-served tokens) for PP, `generation_tokens_total` for TG. Draft acceptance maps to `radiance:draft_*`, preemptions to `radiance:num_requests_preempted`, TPOT to the renamed `vllm:time_per_output_token_seconds`, e2e to `vllm:e2e_request_latency_seconds`. radiance gates `/metrics` and `/v1/models` behind a bearer key — pass `--api-key` or set `RADIANCE_TOP_API_KEY`. The CONFIG grid reads `/server_info` (version, TP, quant, prefix cache, speculation, KV capacity) and takes the boot epoch from `uptime_s`, so the lifetime columns are since-boot. radiance has no host-tier fill gauge, so its RAM lane reads the engine's own tier counters: RAM hits from `prefix_hit_cut_tokens_total` over prompt intake, and a RAM evict/s bar from `prefix_cache_evictions_total` (a `store_full` checkpoint eviction lights the `C` pressure flag — the tier refusing a store). The per-request queue/prefill rows and allocation-failure counts are not published by radiance: those lanes read `-`/n/a, never a guess.

![radiance-top displaying per-GPU hardware, server performance, and request flow](../scripts/radiance-top.png)

*The monitor presents GPU sensors alongside request, cache, and token-flow data.*

Use `w` to cycle **30s → 60s → 120s → 300s → 600s → since-start**. The release monitor also accepts `--window 300`, `--window 600` or `--window since-start`; its plain output includes all three new generated-token rate windows. The installed target monitor adds 300s, 600s and since-start columns to its existing performance tables.

The **PP** row reads local engine iteration logs and reports prompt tokens per second for the latest completed pure-prefill step. Its longer-window values divide total pure-prefill tokens by total pure-prefill step time within the window; idle/decode time is excluded. Mixed prefill/decode steps cannot isolate prefill time, so the current PP value is unavailable for those steps. Stale or inaccessible logs show a dash, not a fabricated zero. This requires running the monitor on the GPU host with permission to read Podman logs and iteration logging enabled. It does not change or restart the engine.

**P-CRED** remains the completion-credited prompt-compute counter rate. It can stay at zero while a long prompt is actively being processed. It is not the current PP measurement. `CTX IN` and `TOK OUT` use K/M suffixes in every statistics column; their underlying values remain token counts.

Since-start means the first successful sample in the current monitor process, rebased when server counters reset. It is a wall-time counter delta, distinct from an active-time mean. Rolling 300s/600s results remain unavailable until enough history has accumulated, whether or not that window was previously selected. GPU sparklines in the release monitor retain at most 600 seconds. Restart an already running monitor after upgrading its script; the inference server does not need a restart.

## Run the real-agent Falling Blocks task

Open the [historical game gallery](../examples/rocm-7.14/falling-blocks/index.html) directly in a browser. To generate a seeded coding task:

```bash
python3 scripts/falling_blocks_prompt.py --seed 100 --output /tmp/falling_blocks-prompt.txt
```

The agent runner and fleet launcher use an operator-supplied Podman image containing `pi-coding-agent`, configured with a provider that reaches the running Radiance server. Set the image, provider and served model ID, then run four agents with seeds 100–103:

```bash
WORK_ROOT=results/falling_blocks-run \
PI_IMAGE=your-pi-agent-image \
PI_PROVIDER=radiance \
PI_MODEL=ukisai/Swift-1.5-Qwen3.8-27b-INT4 \
bash scripts/run_falling_blocks_fleet.sh 4 100 3600
```

Run a single agent by replacing the fleet command with:

```bash
WORK_ROOT=results/falling_blocks-run \
PI_IMAGE=your-pi-agent-image \
PI_PROVIDER=radiance \
PI_MODEL=ukisai/Swift-1.5-Qwen3.8-27b-INT4 \
bash scripts/run_falling_blocks_agent.sh 0 100 3600
```

Summarise the session usage and timing fields without printing conversation text:

```bash
python3 scripts/parse_falling_blocks_events.py results/falling_blocks-run/agent-*
```

The runner writes prompts, model session JSONL, logs, and generated files below `WORK_ROOT`. Session files can contain prompts, tool calls, and generated code; review them before sharing. The [historical gallery](../examples/rocm-7.14/falling-blocks/index.html) contains the recovered agent outputs.

## Custom kernel installation and GRUB settings

The PCI P2PDMA whitelist patch was built as Ubuntu kernel ABI `7.0.0-999`. The recorded kernel packages were `linux-image-unsigned-7.0.0-999-generic`, `linux-modules-7.0.0-999-generic`, and `linux-headers-7.0.0-999-generic`. The kernel was installed, an initramfs was generated, GRUB was refreshed, and the machine was booted into the custom kernel. Secure Boot required signing the kernel with a locally managed key before it could be booted; signing keys and machine-specific enrollment material are not included here.

The recorded GRUB setting was:

```bash
# Earlier variant, retained here as history:
#GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=on iommu=pt amdgpu.runpm=0 pcie_aspm=force pcie_aspm.policy=performance pci=config_acs=xx00xxx@0000:00:01.0\;xx00xxx@0000:00:06.0"

# Active variant recorded with the custom P2P kernel:
GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=on amdgpu.runpm=0 pcie_aspm=force pcie_aspm.policy=performance pci=config_acs=xx00xxx@0000:00:01.0\;xx00xxx@0000:00:06.0"
```

The active value does not include `iommu=pt`. Keep the two variants distinct. The GRUB parameters configure the host boot environment; the kernel's `8086:4621` P2PDMA whitelist entry is a separate change. After installing the kernel packages, the recorded process generated its initramfs and ran `update-grub`, then rebooted and verified the running kernel and GPU peer access. Exact signing and key-enrollment commands were host-specific and are not reproduced.

## Server command used for the single-card RAM16 test profile

Compare the [side-by-side requirements and completed results](../HISTORICAL-OVERVIEW.md#best-recorded-single-card-setup-for-34-deep-context-agents) before choosing a profile. `launch-tp1-rocm10.sh` reproduces the measured ROCm 10.1 / 10 GiB configuration; it is not a qualified 3–4-agent recommendation. Both portable single-card launchers explicitly use TP=1 and expose one GPU’s DRM nodes. Set `GPU_CARD_DEVICE`, `GPU_RENDER_DEVICE` and optionally `GPU_UUID` together for another card. FP8 mode requires the scale sidecar and its sibling `.manifest.json`; both are mounted read-only with verification enabled.

The historical four-agent single-card milestone used one R9700, a 16 GiB RAM-only KV tier, a 131,070-token model limit, four scheduler slots, MTP with four draft tokens, R4D attention, and a 16 GiB host-memory tier. This rewritten launcher expresses that server configuration with user-supplied image/model paths and no saved credentials:

```bash
IMAGE=your-compatible-radiance-image \
MODEL_PATH=/path/to/local/model \
MODEL_ID=your-model-name \
KV_SCALE_FILE=/path/to/validated-fp8-kv-scales.safetensors \
bash scripts/launch-ram16-tested.sh
```

`KV_SCALE_FILE` is optional for startup. Set it to a valid model-matched calibration sidecar to enable the FP8 KV mode used by the reported RAM16 run; without it the server starts with its default KV dtype and is not a configuration-matched reproduction. `CACHE_PATH` can point to a writable host directory for the vLLM compilation cache. The host must expose `/dev/kfd` and `/dev/dri`, support `--ipc=host`, and have sufficient `/dev/shm` capacity for the 16 GiB tier. The script binds the API to localhost on port 8000 by default. Set `PORT` to change the host port.

After the server health endpoint responds, start the rewritten synthetic benchmark in another terminal:

```bash
python3 scripts/agent_bench.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model your-model-name --agents 4 --turns 24 \
  --max-tool-chars 12000 --output results/run.json
```

`scripts/agent_bench.py` is a clean synthetic replacement. The original v4 harness is now separately available at `scripts/recovered/bench_agents4.py`; they are not interchangeable. It does not exactly reproduce the historical prompt distribution or its run totals. See the [benchmark guide](BENCHMARKS.md) and [run index](RUN-INDEX.md) before comparing results.

## Build and run the ROCm 10.1 TP=2 profile

The later two-card stress work rebuilt the image on the ROCm 10.1 Ubuntu 24.04 development base for `gfx1201`. The published record reports this qualified component set: vLLM 0.30.0, AMD PyTorch 2.12.0 stamped `+rocm10.1`, Triton 3.7.1, torchvision 0.27.1, AITER 0.1.20, and libr4d 0.5.0. These pins were treated as one compiler/runtime unit; replacing only one with a generic upstream wheel was not considered equivalent.

The build was a multistage source build: compile component wheels against the ROCm 10.1 base, prune unused GPU architectures, assemble the patched vLLM/Radiance runtime and libr4d kernels, then emit a smaller runtime image. The recorded build used eight-way build orchestration and `BUILD_JOBS=16`; the running inference service was stopped during compilation because build and serve together exceeded the host resource budget.

The compile-specific lessons were:

- Build PyTorch, Triton, torchvision, AITER, and vLLM as a pinned set against the same ROCm base. The PyTorch wheel version was restamped `+rocm10.1` so package metadata matched the library stack it was built against.
- Disable AOTriton and MAGMA for this target. AOTriton's gfx1201 source configuration failed, and this serving path did not require it; the base did not provide MAGMA.
- Force torchvision's ROCm/CUDA-extension build path (`FORCE_CUDA=1`) because image builds have no GPU to satisfy torchvision's runtime availability check. Without that override it selected the wrong extension path and produced duplicate HIPified symbols.
- Install `setuptools-scm` before source builds, use existing pinned PyTorch when building vLLM, and explicitly stamp the vLLM version. Without the build metadata tools, wheels can be mislabelled even when the intended commit was checked out.
- Compile HIP/R4D extensions in a stage that still has the full ROCm compiler and headers; copy only the runtime environment and pruned device libraries into the final image.
- The ROCm bandwidth probe needed an explicit runtime search path for `libhsa-runtime64.so` because ROCm 10.1 placed it under the versioned `core` library tree.

From a maintained Radiance build checkout that contains the corresponding `Dockerfile.rocm10` and its referenced build inputs, the image build command is:

```bash
podman build \
  --build-arg BUILD_JOBS=16 \
  --file Dockerfile.rocm10 \
  --tag radiance-vllm:rocm10 .
```

**ROCm 10.1 `amdsmi` fix:** the base image provided `amdsmi` 27.1.0 as a bare Python package tree without packaging metadata, so installing that directory with `pip` failed. The build copied the provided `amdsmi` module into the runtime environment's Python `site-packages` and configured `AMDSMI_LIB_OVERRIDE=/opt/rocm/lib/libamd_smi.so`. Keep the ROCm-provided bindings; vLLM 0.30 imports them for platform detection. The override points the wrapper at the matching ROCm 10.1 shared library and avoids changing global loader configuration.

The recorded image check reported vLLM 0.30.0, PyTorch 2.12.0+rocm10.1, AITER 0.1.20, torchvision 0.27.1, Triton 3.7.1, and libr4d 0.5.0; the runtime JIT toolchain check also passed. This was an image/import/JIT check, not the physical-GPU upgrade qualification suite.

Launch the rewritten two-card profile with the locally built image and model:

```bash
IMAGE=radiance-vllm:rocm10 \
MODEL_PATH=/path/to/local/model \
MODEL_ID=your-model-name \
KV_SCALE_FILE=/path/to/validated-fp8-kv-scales.safetensors \
bash scripts/launch-rocm10-tp2.sh
```

This profile uses TP=2, model length 168,000, eight scheduler slots, four MTP tokens, a 4 GiB ARC RAM tier, and no filesystem tier. It defaults to the compressed R4D all-reduce path used in the recorded TP=2 launcher; that path changes numerical results relative to exact reduction. Set `USE_COMPRESSED_AR=0` to leave that path disabled and use the exact-kernel/RCCL behaviour supported by the image. `KV_SCALE_FILE` is optional but required to reproduce the FP8 KV mode; without it, the model's default KV dtype applies. The image build definition and calibration sidecar are not bundled in this documentation release, so the build command requires the compatible build checkout and the sidecar must be supplied separately.

The 2026-10-17 ROCm 10.1 stress run completed 116 four-agent turns without request errors, but its older comparison used a different image/configuration and is not a controlled A/B. The [journal summary](RESEARCH-JOURNAL.md#5-rocm-101-results-and-version-limits), [dual-GPU notes](DUAL-GPU.md), and [four-agent stress chart](../graphs/rocm-10.1/rocm-base-image-four-agent-stress-run.svg) give the limits and result context.

## Generic Podman launch template

```bash
IMAGE=your-radiance-image \
MODEL_PATH=/path/to/model \
MODEL_ID=your-model \
PORT=8000 \
bash scripts/launch-example.sh
```

The template binds the API to localhost, passes ROCm device nodes, and exposes a read-only model directory. Add cache volumes, memory settings, environment variables, and model arguments for the target host. It deliberately contains no original server paths, internal hostname/address, model snapshot hash, HF token handling, or live settings. Keep credentials outside the script and never place tokens in command-line arguments.

For model-matched FP8 cache scales, follow the [coding-agent history calibration guide](FP8-KV-CALIBRATION.md). It covers corpus preparation, maintenance commands, Q/K/V-only compatibility, verification, activation and held-out validation.

## Regenerate release data and graphs

Generate the current summary reports from existing local CSV exports with `python3 tools/render_follow_up.py`. Use `python3 tools/chart_theme.py` to apply the shared dark palette to all retained and archived SVGs. The navigation generator calls the editorial renderer; use the theme command explicitly when changing the older SVG families. These commands only write local artefacts and do not contact the inference server.

From the release package root, maintainers with access to the separately held source CSVs can rebuild the derived outputs:

```bash
python3 tools/build_release.py
python3 tools/build_run_index.py
python3 tools/render_csv.py data/rocm-7.14/*.csv data/rocm-10.1/*.csv --out graphs
python3 tools/build_navigation.py
```

The first tool derives transformed data and Markdown inventory; the second builds the detailed run index; the third renders SVGs from the derived tables; the fourth embeds those charts in a Markdown gallery and refreshes navigation links on every Markdown page. None copies source documents or CSVs into the release.

## Regenerate the game gallery

After importing games and their reviewed `manifest.json`, run `python3 tools/build_game_gallery.py`, then `python3 tools/build_navigation.py`. The gallery builder verifies the expected eleven files against their release sizes and hashes, preserves original provenance, and writes grouped links without changing game code. Functional checks belong to the target campaign; gallery generation does not rerun them.

<!-- NAVIGATION START -->

[Home](../index.md) · [Compare](RADIANCE-VS-VLLM.md) · [vllm-radiance](VLLM-RADIANCE.md) · [radiance](RADIANCE.md) · [Charts](CHARTS.md) · [Stuff for nerds](CODE-CORNER.md) · [Disclosure](REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
