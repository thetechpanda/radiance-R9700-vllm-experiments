---
layout: default
title: "The Swift 1.5 Qwen model in radiance"
---

# The Swift 1.5 Qwen model in radiance

## The recorded checkpoint

The campaign's primary checkpoint is [`ukisai/Swift-1.5-Qwen3.8-27b-INT4`](https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-27b-INT4) (see [Model inventory](../MODELS.md)) — a hybrid GDN Qwen3.8 27B, AWQ+GPTQ INT4. Its `config.json`, verified on 2026-10-19, states:

| Field | Value |
|---|---|
| `architectures` | `Qwen3_5ForConditionalGeneration` (`model_type: qwen3_5`) |
| `quantization_config` | compressed-tensors, `format: pack-quantized`, weights `int`, 4-bit, `strategy: group`, `group_size: 128`, `symmetric: true`, `actorder: "static"`, `dynamic: false`, no `input_activations` |
| `ignore` list | the whole `model.visual.*` tower (bf16), plus per-layer `linear_attn.in_proj_a/b` (bf16) |
| `image_token_id` | present — the release is multimodal |

## radiance names this release, by name

radiance's checkpoint-import table (GUIDE §3.2) explicitly lists:

> compressed-tensors, `format: pack-quantized` with every config group 4-bit `int` weights, `strategy: group`, not `dynamic`, no `input_activations`, actorder none, `static` or `weight` (e.g. Google's Gemma 4 QAT w4a16-ct, **ukisai's Swift 1.5 27B INT4**) → imported as `i4*<scale>[1xG]`, "as shipped"

and the serving recipe header (`data/recipes/q38-27b-w4a16.recipe`) reads:

> an int4 W4A16 release of Qwen3.8-27B (or a finetune of it, such as **ukisai's Swift 1.5 W4A16-AWQ, INT4 and W4A16-AutoRound**), served at the 4-bit weights it ships.

The recorded config matches the accepted form on every field (act-order `static` is in the accepted set; an act-order that *reorders groups* would be refused by name). Served by the family's quantised plugin `qwen35_fp8`:

- **decode:** `w4a16_asym` — int4 weights over f16 activations, up to 64 rows a step;
- **prefill/batch:** `w4a8i8_asym` — int4 weights over int8 activations with a scale per (row, 128).

This is the same W4A16-decode / W4A8-prefill split the vllm-radiance W4A8 work uses; the numbers are preserved exactly: "every code and zero point as shipped, every f16 scale as shipped", bf16 scales widened to f16 (exact), with rounding counts reported.

## Conversion command

There is **no published `.rad` container for the Swift releases** — you convert locally (this matches how the published containers are made: each HF repo carries the exact recipe and command).

```sh
# one-time: fetch the checkpoint
scripts/hfget.sh ukisai/Swift-1.5-Qwen3.8-27b-INT4 /srv/models/hf/ukisai/Swift-1.5-Qwen3.8-27b-INT4

# convert (plan-only dry run first is cheap insurance on a large checkpoint)
rad-convert /srv/models/hf/ukisai/Swift-1.5-Qwen3.8-27b-INT4 \
    -o /srv/models/rad/swift15-27b-int4.rad \
    --recipe data/recipes/q38-27b-w4a16.recipe
# add: --plan-only -v   to check the declare phase without I/O
```

With the container image, the recipes live at `/opt/radiance/share/radiance/recipes/`:

```sh
docker run --rm -v /srv/models:/models --entrypoint rad-convert \
    stilldeadcode/radiance /models/hf/ukisai/Swift-1.5-Qwen3.8-27b-INT4 \
    -o /models/rad/swift15-27b-int4.rad \
    --recipe /opt/radiance/share/radiance/recipes/q38-27b-w4a16.recipe
```

What the recipe keeps/changes, per its header:

- **Kept bf16:** delta-net `a/b` projections, norms, embedding, **vision tower**, **MTP head** — the container remains multimodal and MTP-speculative.
- **lm_head → block FP8** (128×128) — the widest per-step GEMM at half the bytes.
- **MTP draft head → 2-bit** (u2, least-squares clip search) whose top candidates the engine **rescores against the fp8 head** — the same fast-draft design the vllm-radiance fork ships as `RADIANCE_FAST_DRAFT`.

## Sibling Swift releases

| Release | radiance path |
|---|---|
| `ukisai/Swift-1.5-Qwen3.8-27b-W4A16-AWQ` (asymmetric llm-compressor AWQ) | imported as `u4*scale−zero` bit-for-bit; same `q38-27b-w4a16.recipe`; the README's own worked example converts exactly this repo |
| `ukisai/Swift-1.5-Qwen3.8-27b` (bf16 base/finetune) | `q38-27b-fp8block-df2.recipe` + `--draft-model z-lab/Qwen3.8-27B-DFlash2` → FP8 container with DFlash2 drafter (GUIDE §3.2 uses this exact repo in its example) |
| `ethanwtodd/Swift-1.5-Qwen3.8-27b-Quark-RTN-MXFP4` (campaign arm E/S/T/U) | Quark MXFP4 form is imported byte-for-byte (the `q38-27b-quark-mxfp4-df2.recipe` pattern used for the published MXFP4 container) |
| `ukisai/Swift-1.5-Qwen3.8-27b-NVFP4` (ModelOpt) | named in the import table; NVFP4 has **no kernel** and must be re-quantised to MXFP4 by recipe (`q38-27b-modelopt-nvfp4.recipe`) — a second quantisation, expect quality work |

## Published containers (for reference runs)

| Container | Size | Notes |
|---|---|---|
| [`qwen3.8-27b-mxfp4.rad`](https://huggingface.co/StillDeadcode/qwen3.8-27b-mxfp4) | 18.05 GiB | AMD Quark AWQ-MXFP4 trunk + DFlash2 drafter + vision; needs radiance ≥ 1.2.3; TP1 fits one 32 GiB card |
| [`qwen3.8-27b-fp8.rad`](https://huggingface.co/StillDeadcode/qwen3.8-27b-fp8) | 28.67 GiB | Qwen's FP8 as shipped + DFlash2 + vision; TP2 |
| ParoQuant int4/int5/MXFP4 | 19/22 GiB | Convert from `z-lab/Qwen3.8-27B-PARO`, `Launch80/...-int5`, `MisterSnrub/...-MXFP4-v2` with `q38-27b-paro-mxfp4-df2.recipe` |

## Caveats for a Swift-1.5 migration

1. **No published Swift container** — you own the conversion, and `.rad` files are engine-version pinned (pre-1.5.0 ParoQuant containers are refused; ABI churn is real: 1.8.1 bumped plugin ABI 22). Pin a tag and record the conversion command with it.
2. **FP8 KV calibration does not transfer.** radiance's `--kv-cache-dtype fp8` is E4M3 with per-(sequence, head) descales — no model-matched scale manifest (see [FP8 KV calibration](../FP8-KV-CALIBRATION.md) for the vllm-radiance procedure). Quality claims for radiance fp8 KV on the Swift checkpoint are upstream's general statement ("a real quantisation that changes the output slightly"), not a Swift-specific measurement.
3. **The INT4 container's serving shape differs.** The recorded campaign served Swift INT4 through vllm-radiance's W4A8 path with the MTP head at the checkpoint's own precision; radiance replaces the draft head with a 2-bit rescored copy. Speeds are not assumed equal — measure (see [performance-standards.md](performance-standards.md)).
4. **Container size estimate.** The recipe preserves int4 trunk codes + bf16 tower/MTP + fp8 head: roughly 14–15 GiB, below the published MXFP4 (18.05 GiB) and FP8 (28.67 GiB) containers. Verify with `rad-info` after conversion; do not plan capacity from this estimate.

<!-- NAVIGATION START -->

[Home](../../index.md) · [Overview](../../README.md) · [ROCm 10.1 results](../FINAL-REPORT-20261018.md) · [Charts](../CHARTS.md)
