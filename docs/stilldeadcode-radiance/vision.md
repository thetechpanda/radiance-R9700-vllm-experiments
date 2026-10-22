---
layout: default
title: "Vision in radiance: images per turn and per session"
---

# Vision in radiance: images per turn and per session

All statements are from the radiance docs (GUIDE §4.3, §4.10, §5.1, §5.6; ARCHITECTURES.md; container cards) as read on 2026-10-19.

## What the Qwen3.8-27B containers carry

The Qwen3.8-27B family is natively multimodal at the architecture level: `Qwen3_5ForConditionalGeneration`, 27-block vision tower (hidden 1152, 16 heads → head_dim 72, patch 16, out 5120), M-RoPE with interleaved sections `[11, 11, 10]`. The shipped `.rad` containers include it:

- `qwen3.8-27b-fp8.rad` — "the 27-block vision tower, bf16: images and video in chat requests"
- `qwen3.8-27b-mxfp4.rad` — same
- `qwen3.8-27b-paro-int4.rad` — same
- Converted Swift 1.5 int4 containers — the recipe keeps the vision tower bf16 (it is in the checkpoint's `ignore` list, so it ships unquantised)

The vision tower is **declared** when the container carries one and `--mm-max-patches` is not 0. `--mm-max-patches 0` serves text only and keeps the tower off the card.

## Accepted media

Chat messages take OpenAI content parts. Media arrives as base64 `data:` URLs only — the server **never fetches URLs**.

| Part | Formats | Sizing |
|---|---|---|
| `image_url` | PNG, JPEG, WebP, GIF, BMP, TIFF, AVIF | Resized into the container's pixel band (`--image-min-pixels` / `--image-max-pixels`); one encoder pass bounds the top at `--mm-max-patches` (auto 16384, a patch is 16×16 px) |
| `video_url` | MP4, WebM, MKV, MPEG-TS, AVI with H.264/HEVC/VP8/VP9/AV1 | Qwen-VL container defaults (when the container states none): 2 frames/s, 4–768 frames, 768 tokens per frame |
| `input_audio` / `audio_url` | wav, mp3, flac, ogg, opus, m4a, aac, webm, aiff | 25 tokens/s, cut at 30 s (ASR models) |

**Two sizing paths exist and Qwen3.8-27B is not the token-budget one.** The `--image-tokens` / request `image_tokens` knob (70/140/280/560/1120) belongs to *token-budget processors* (Gemma 4's tower); the pixel-band flags are refused on such models. Qwen3.8-27B's tower is the pixel-band kind: image size is set by the pixel band and patch cap, and the docs do not state a fixed per-image token count for it.

Request bodies (which carry the base64) are bounded by `--max-body-mib` (default 512 MiB); decoder input is bounded by `--max-source-pixels` (default 67,108,864 px before resize).

## Multiple images per turn

**The docs state no fixed per-turn image count.** The practical bounds are:

1. **Encoder pass width.** `--mm-max-patches` (auto = 16384 when a tower is present) bounds patches **one vision-encoder pass** carries — it bounds the largest image, and each image is one pass.
2. **Pixel band.** `--image-min-pixels` / `--image-max-pixels` override the container's resize band per image.
3. **Pixel budget.** Each image is resized into the pixel band; its resulting vision tokens plus text must fit `--max-model-len`; N large images multiply that cost.
4. **Body size.** All base64 images share the `--max-body-mib` body.

So: many images in one turn are supported in principle, bounded by tokens, pixels, encoder patch width and body size — not by a documented hard count. **This is a documentation reading, not a measured limit; verify the count you need with a real request.**

## Multiple images per session

The vision tower is read **once per image, clip or recording, never on a text step**. That has two consequences for long agent sessions:

- Under `--vision-tower-placement vram` (default), the tower occupies VRAM permanently: Qwen3.8-27B's is 0.86 GiB per card ≈ **24,000 tokens of fp8 context** given up.
- Under `--vision-tower-placement ram`, the tower is pinned in host memory and read over the PCIe link once per image (~55 ms for 0.86 GiB on PCIe 4.0 ×16). VRAM goes to the KV cache; images cost link traffic. It is refused where the host cannot pin.

Images already in the conversation are ordinary prompt tokens on later turns: the tower runs only for **new** media. Session history with many screenshots therefore costs KV tokens and prefix-cache bytes, not repeated encoding. The prefix-cache host tier and snapshot store (§4.8, feature-comparison) treat those tokens like any other.

## Practical notes for the dual R9700

- On the recorded host, GPU A is PCIe 4.0 ×8 and GPU B ×4; the ~55 ms tower read is quoted at ×16, so expect proportionally more on the narrower links with `--vision-tower-placement ram`.
- The recorded image workload (`S5-n4-fallingblocks-images` in [the agent-count sweep](../../data/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.csv)) shows the cost on vllm-radiance: images dropped effective ingest from 3386 to 2294 tok/s at four agents. A radiance comparison must use the same image workload to be pp-vs-pp.
- Vision input is inference input; the image **generation** endpoints (`/v1/images/generations`, `/v1/images/edits`) require a Qwen-Image container and answer 501 on LLM containers. Do not confuse the two in agent configs.

## Parity with vllm-radiance vision

vllm-radiance retains vision for the same checkpoint family (the primary INT4 checkpoint is `Qwen3_5ForConditionalGeneration` with the same tower, and the campaign ran image workloads). The radiance-specific gains are operational: tower placement in RAM (frees ~24k fp8 KV tokens), explicit pixel-band and patch-cap flags, video/audio in the same chat endpoint, and refusal-with-reason behaviour. No parity claim is made about image **quality** between engines — that requires running the same corpus through both.

<!-- NAVIGATION START -->

[Home](../../index.md) · [Overview](../../README.md) · [ROCm 10.1 results](../FINAL-REPORT-20261018.md) · [Charts](../CHARTS.md)
