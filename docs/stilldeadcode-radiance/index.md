---
layout: default
title: "StillDeadcode radiance: evaluation for the dual R9700"
---

# StillDeadcode radiance: evaluation for the dual R9700

This is a desk evaluation of [`StillDeadcode/radiance`](https://codeberg.org/StillDeadcode/radiance) — a from-scratch C++/HIP inference engine for AMD GPUs — against the `vllm-radiance` deployment and measured data recorded in this repository, and against the dual R9700 host described in [Hardware](../HARDWARE.md). It is a pre-trial review: everything here was read from upstream documentation, container cards and checkpoint configs on **2026-10-19** (radiance `1.8.1`, commit `816e24bd46`; `magiccodingman/vllm-radiance` main at `1d2e24849c`). No radiance engine has been run on the recorded hardware; nothing here is a measured result of this research.

## Sources reviewed

| Source | What it establishes |
|---|---|
| [radiance README](https://codeberg.org/StillDeadcode/radiance) | Model/container catalogue, serve flags for two R9700s, build and Docker path, licence |
| [radiance GUIDE.md](https://codeberg.org/StillDeadcode/radiance/src/branch/main/docs/GUIDE.md) | Memory model, long context, TP/P2P behaviour, host prefix tier, API surface, metrics, troubleshooting |
| [radiance ARCHITECTURES.md](https://codeberg.org/StillDeadcode/radiance/src/branch/main/docs/ARCHITECTURES.md) | `qwen35` geometry (the Qwen3.8-27B family), FP8/int4 import paths, vision tower, GDN state cost |
| [radiance DOCKER.md + compose](https://codeberg.org/StillDeadcode/radiance/src/branch/main/docs/DOCKER.md) | Container requirements, per-model compose files |
| [q38-27b-w4a16.recipe](https://codeberg.org/StillDeadcode/radiance/raw/branch/main/data/recipes/q38-27b-w4a16.recipe) | The Swift 1.5 INT4/W4A16 conversion path, by name |
| [qwen3.8-27b-mxfp4 container card](https://huggingface.co/StillDeadcode/qwen3.8-27b-mxfp4), [qwen3.8-27b-fp8 card](https://huggingface.co/StillDeadcode/qwen3.8-27b-fp8) | Official decode-speed cards on 1 and 2 R9700s |
| [`ukisai/Swift-1.5-Qwen3.8-27b-INT4` config.json](https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-27b-INT4) | The recorded primary checkpoint's format: compressed-tensors pack-quantized int4, group 128, symmetric, act-order `static`, bf16 vision tower |
| [magiccodingman/vllm-radiance](https://github.com/magiccodingman/vllm-radiance) | The engine this repository's data was collected on (continuation fork of `StillDeadcode/vllm-radiance`) |

## Headline findings

1. **Same author, new engine.** `radiance` is Deadcode's standalone rewrite (C++/HIP, no vLLM, no Python runtime) of the same effort that produced `vllm-radiance` and `libr4d`. The `magiccodingman` GitHub fork continues the vLLM-based line and credits `StillDeadcode/vllm-radiance` and `libr4d` upstream. Feature comparison: [feature-comparison.md](feature-comparison.md).
2. **Vision is first-class.** The Qwen3.8-27B containers carry the 27-block vision tower; chat accepts `image_url`/`video_url` parts. Each image is one encoder pass; the docs state no fixed per-turn image count — the bounds are request body size, per-pass patch cap, pixel band and context. Encoder towers run only on new media, never on text steps, so multi-image session history is KV-only. Details: [vision.md](vision.md).
3. **The exact Swift 1.5 model is named as supported.** radiance's import table and `q38-27b-w4a16.recipe` name `ukisai`'s Swift 1.5 INT4 / W4A16-AWQ / W4A16-AutoRound releases and convert them at their shipped numbers; the checkpoint's `config.json` (verified 2026-10-19) matches the accepted form exactly. The vision tower and MTP head survive conversion. Details: [swift-models.md](swift-models.md).
4. **Published speed is shallow-context; your data is deep-context.** radiance's official cards (204 tok/s one-stream, 438 tok/s four-stream on TP2 MXFP4 with DFlash2) use 768-token prompts; the collected dual-card data in [the spec campaign](../DUAL-R9700-SPEC-CAMPAIGN.md) runs at 126k depth. Aligning the standards (pp vs pp, tg vs tg) shows the two engines are broadly comparable at comparable depth, with context depth dominating tg. Details: [performance-standards.md](performance-standards.md).

## Pages

- [Feature comparison: vllm-radiance vs radiance](feature-comparison.md)
- [Vision support: images per turn and per session](vision.md)
- [The Swift 1.5 Qwen model and conversion](swift-models.md)
- [Performance standards: pp and tg against collected data](performance-standards.md)
- [Startup guide for the dual R9700](startup-guide.md)
- [Server runbook: repo checkout, model downloads, campaign re-run](SERVER-RUNBOOK.md)

## Scope and honesty limits

- Upstream numbers are the authors' own measurements on their own two R9700s, with their prompts and flags; this repository's numbers are one run per cell on the recorded MS-01 host. Neither validates the other.
- The recorded host (32 GiB RAM, GPU B on a PCIe 4.0 ×4 link, P2PDMA kernel patch) is unusual; radiance's documented behaviour on narrower-than-peer links and pinned-memory caps is reproduced in the startup guide, with the costs it states, not measured here.
- radiance moves fast (1.7.0 → 1.8.1 in three days as of the review date; plugin ABI 22 requires out-of-tree plugin rebuilds). Pin an exact commit/tag before converting containers — a container is tied to the engine version that wrote it.

<!-- NAVIGATION START -->

[Home](../../index.md) · [Overview](../../README.md) · [ROCm 10.1 results](../FINAL-REPORT-20261018.md) · [Charts](../CHARTS.md)
