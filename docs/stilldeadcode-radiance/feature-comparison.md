---
layout: default
title: "Feature comparison: vllm-radiance vs StillDeadcode radiance"
---

# Feature comparison: vllm-radiance vs StillDeadcode radiance

Both engines descend from the same RDNA4 effort by Deadcode (`StillDeadcode`):

- **`vllm-radiance`** ([Codeberg origin](https://codeberg.org/StillDeadcode/vllm-radiance), [continuation fork](https://github.com/magiccodingman/vllm-radiance)) — a pinned vLLM 0.30.0 ROCm stack with hand-written `libr4d` gfx1201 kernels and Radiance FP8/speculative paths, delivered as a Docker image. This repository's campaign ran it (engine string `1.1.0-rc1.vllm0.30.0`, ROCm 10.1; see [configuration record](../../data/rocm-10.1/single-card-gpu-a-configuration.json)).
- **`radiance`** ([Codeberg](https://codeberg.org/StillDeadcode/radiance)) — a from-scratch C++/HIP engine: no vLLM, no PyTorch, no Python at runtime. Model architectures, kernel libraries and quantisers are `.so` plugins; the bundled `libr4d` (the same kernel library the vLLM fork ports) is loaded exactly like a third-party plugin. Apache-2.0 with a NOTICE file.

The rewrite keeps the good parts of the vLLM line (libr4d kernels, FP8 paths, MTP/DFlash speculation, TP2 all-reduce) and drops the Python/vLLM dependency, then adds a much larger API and modality surface.

## Side-by-side (as documented 2026-10-19)

| Aspect | magiccodingman/vllm-radiance | StillDeadcode/radiance |
|---|---|---|
| Runtime | vLLM 0.30.0 + AMD PyTorch 2.12 + Triton 3.7.1 + AITER 0.1.20, patch overlays, Python | Single C++ binary + plugin `.so`s; vendored HTTP/JSON/llama.cpp pieces; ROCm 10.1 **driver** needed, no ROCm on host |
| Kernels | libr4d 0.5.0 (attention, GDN, vision, all-reduce, MXFP4, DFlash) + Radiance FP8 + AITER/Triton/RCCL fallbacks | libr4d 0.5.0 as a plugin, `libref` correctness oracle, `libavx` host (AVX-512/AVX2) backend; kernel replay tests (`rad-kbench`) |
| HTTP APIs | OpenAI chat/completions (vLLM surface) | OpenAI chat, completions, Responses (Codex), images, audio (transcriptions/speech/realtime), video jobs; **Anthropic Messages (Claude Code)**; llama-server native + infill; `/props`, `/server_info`, `/diagnostics`, `/sessions`, dashboard |
| Modalities (LLM) | Text + vision input | Text + vision + video input; also image **generation** (Qwen-Image 2.1), video generation (MiniMax-H3/FastH3), TTS/music (Breeze-TTS-2, MiniMax-Music3), ASR (Qwen3-ASR), embeddings (EmbeddingGemma 2) |
| Tensor parallel | TP2 qualified (dual R9700); TP1 | TP1/2/3/4/8 documented; lossy `wht6` wire at 2 ranks, tiered int8 at 3–4; P2P auto-detected with pinned-host-staged all-reduce fallback when peer access is absent |
| Weight formats | Native FP8; Quark MXFP4 W4A8 (native gfx1201); NVFP4→MXFP4 load-time conversion; W4 (draft linears) | Byte-for-byte imports: FP8, Quark MXFP4, ParoQuant int4/int5/MXFP4 (learned rotations), compressed-tensors AWQ/GPTQ/AutoRound int4 (Swift 1.5 named), NVFP4→MXFP4, ModelOpt; GGUF input; `.rad` containers bundling weights+tokeniser+template+drafter |
| KV cache | FP8 KV mandatory in the qualified profile; **calibrated Q/K/V sidecars** (opt-in lab) | `--kv-cache-dtype fp8`: E4M3 with per-(sequence, head) descales — no calibration manifest; explicitly a real quantisation |
| Host memory tier | `RADIANCE_KV_OFFLOADING_SIZE` mmap tier, pinned/pageable DMA, rank-sharded option; ARC-style offload used in this campaign | `--prefix-cache-mib` host tier for **finished conversations** (attention blocks) + pinned linear-state snapshot store (`--checkpoint-slots`, TTL) + weight host pool + disk tier (`--weights-disk-tier`) |
| Speculation | MTP (opt-in, K≤8), DFlash2 K5/K7 (experimental; strict greedy equivalence not passed), INT2 exact-rerank fast draft | MTP + DFlash2 + DSpark drafters merged into containers; depth auto-chosen from the drafter's operating point; 2-bit rescored draft head; adaptive draft window; "drafts are verified, so they change the speed and never the output" |
| Structured output / tools | XGrammar + Qwen tool-parser fixes (`qwen3_coder`, `qwen3` reasoning parser) | Grammar/JSON-schema/GBNF enforcement with refuse-don't-drop rule; grammar-shaped tool calls; reasoning in `reasoning_content`; `thinking_token_budget` |
| Prefix caching | Automatic, hybrid-GDN `mamba-cache-mode=align` | Prefix cache + linear-state snapshots (the GDN half is what makes a hybrid hit real); `/sessions` tab; `prefix_hit_cut_tokens_total` counters for cut hits |
| Observability | vLLM metrics/logs | `vllm:`-compatible Prometheus family **plus** `radiance:` counters (decode/prefill tok/s, draft acceptance by position, preemptions), web dashboard, `--live` terminal view, per-request `timings` (llama.cpp names + `ttft_ms`), startup hardware report |
| Bench/qualification culture | BetterBench v0.2.2 corpus v1, greedy cold nonce, strict gates, published negative results | Container speed cards (8 greedy prompts, 768 tokens), `rad-kbench` kernel replay vs oracle, `scripts/agentreplay.py` agent workload driver, `--kld-*` KL measurement modes |
| Deployment | Docker image `magiccodingman/vllm-radiance`; compose; ROCm 7.14 userspace in image | Docker image `stilldeadcode/radiance` (gfx1201); per-model compose; `seccomp=unconfined` + `memlock=-1` + host net; build from source with ROCm 10.1 or 7.2 `hipcc` |
| Licence | (fork of upstream radiance licence) | Apache-2.0 + NOTICE; model containers keep each model's licence |

## What the rewrite changes for an agent deployment

- **Anthropic Messages + OpenAI Responses endpoints.** Claude Code and Codex-style clients can point at one server without a translation proxy. vllm-radiance exposes the OpenAI surface only (as documented).
- **The GDN state problem is first-class.** radiance declares the 27B's 144 MiB-per-sequence f32 recurrent state, snapshots it to pinned host memory, and counts "prefix hits that reused nothing" (`prefix_hit_cut_tokens_total`). The vLLM line solves the same problem with `mamba-cache-mode=align`; radiance's version is visible per session and per tier.
- **No Python runtime, no AITER JIT.** Smaller image (`FROM scratch` rootfs), no first-use kernel compilation, deterministic startup plan. The trade-off: you lose vLLM's ecosystem (multi-model serving, sampling plugins, the huge flag surface) — radiance serves one model per server.
- **P2P is optional, not a kernel patch.** radiance asks the driver about peer access at launch and runs the same all-reduce kernels with exchange buffers in pinned host RAM where a pair cannot do P2P; it reports the choice in the startup report. This is directly relevant to the recorded host, which needed a custom [P2PDMA whitelist kernel patch](../../patches/) for vLLM TP2.
- **Speculation is presented as verified-by-construction** ("drafts never change the output"), while the vllm-radiance fork keeps its speculative modes opt-in because its strict cross-mode output-equivalence gate has not passed. These are different claims from different test cultures; treat each as the authors state it, not as an equivalence.

## What vllm-radiance still has that radiance does not (as documented)

- **Live KV offload for running requests.** The ARC tier in this campaign offloaded KV of in-flight conversations (preempt-to-CPU). radiance's host tier stores **finished** conversations; a full VRAM pool mid-generation preempts and re-prefills/restores per its prefix-cache rules.
- **Calibrated FP8 KV.** The FP8-KV [calibration guide](../FP8-KV-CALIBRATION.md) workload (model-matched Q/K/V scales + manifest) has no radiance counterpart; radiance's fp8 KV uses per-(sequence, head) dynamic descales instead.
- **Qualified-mode discipline of the fork.** The magiccodingman fork publishes per-mode qualification (non-spec recommended; MTP/DFlash gated; negative results kept). radiance publishes speed cards and kernel-level correctness, not per-mode serving qualification with the same gate vocabulary.

## Migration friction to expect

- Containers are version-pinned: "a ParoQuant container made before 1.5.0 is refused at startup"; plugin ABI 22 (1.8.1) breaks out-of-tree plugins. Pin a tag, convert once.
- Flags do not map 1:1; the semantics of `--max-num-seqs`, context, KV pool and snapshot store are radiance's own (see GUIDE §4.3–4.8).
- Your FP8 KV calibration sidecars, TunableOp profiles, AITER gates and `RADIANCE_*` vLLM knobs do not transfer.

<!-- NAVIGATION START -->

[Home](../../index.md) · [Overview](../../README.md) · [ROCm 10.1 results](../FINAL-REPORT-20261018.md) · [Charts](../CHARTS.md)
