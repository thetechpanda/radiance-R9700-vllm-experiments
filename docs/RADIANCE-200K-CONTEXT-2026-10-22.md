---
layout: default
title: "200k by default: the model was always 256k (22 October 2026)"
---

# 200k by default: the model was always 256k (22 October 2026)

## The model fact

The checkpoint says 262144. `n_ctx_train` is 262144, `max_position_embeddings` is 262144, `rope_theta` 1e7 with default rope — no scaling needed to reach it. The 131k ceiling this deployment carried was a choice, not the model's wall. Every page of this campaign ran at 131072; the checkpoint never said that. The model was always 256k. I just never asked for it.

## The promotion

One flag. The quadlet Exec changed `--max-model-len` from 131072 to 204800. Six slots kept, MTP-4 kept, the 13 GiB host tier kept, engine 1.9.0 at the pinned digest. The boot print:

> kv cache 20.79 GiB a card: 1228816 tokens, 6.0 sessions at 204800

That is 100% backing of the 6×204800 worst case and 94% of the card's elastic VRAM. Every number on this page traces to [data/rocm-10.1/radiance-pool-ceiling-2026-10-22.csv](../data/rocm-10.1/radiance-pool-ceiling-2026-10-22.csv).

## Acceptance probes

Three checks, all passed.

**Over-cap arithmetic.** A request at 330,075 tokens gets a clean 400 with exact arithmetic, not a crash: "request 330075 tokens exceeds 204800; shorten by at least 125276 tokens." The raw excess is 125,275; the engine asks for 125,276 — the extra one is the reply slot. The engine does the subtraction for you.

**Needle.** 165,075 prompt tokens, needle buried at about 150k depth. Answer: ORCHID. Correct. Repeats: TTFT 0.3–0.4 s. That speed is the 13 GiB host tier doing its job — 165k-token conversations cache in finished form and come back from RAM, not recompute.

**Service state.** `/server_info` confirms the new contract: `max_model_len 204800`, drafter `mtp`, serial depth 4, tp 2.

## The pool rule

The engine's rule: pool = min(what fits, slots × context). "What fits" comes from measured KV density — 18.2 KiB/token/card on this fp8 hybrid model, where only about a quarter of the 64 layers carry growing KV and the linear layers keep a fixed ~150 MiB of per-session state. One slot is 131,104 tokens — exactly 1.0 session — even with idle VRAM. KV beyond slots × context is dead memory.

The ladder, with the measured-vs-projection column kept visible:

| Config | Pool tokens | Full sessions | Kind |
|---|---:|---:|---|
| TP1, 4 slots, 131k | 404,608 | 3.1 | measured |
| TP2, 4 slots, 131k | 524,304 | 4.0 | measured |
| TP2, 6 slots, 131k | 786,448 | 6.0 | measured |
| TP2, 6 slots, 200k — current default | 1,228,816 | 6.0 | measured |
| TP2 elastic ceiling (slots ignored) | ~1,284,500 | ~9.8 | projection |

Elastic VRAM is 22.23 GiB per card from the service boot print; the top row divides that by measured density. It is a ceiling, not a measurement.

## What changed operationally

Before: four agents at 131k each. Now: six agents × 204,800 at full depth, backed by construction — the pool was sized for the worst case, not the average. No new hardware, no new tier, no config rewrite; one flag, and the pool arithmetic carried it. And the model's native ceiling is in reach on this same hardware: 256k-class context gives 4 slots full (1,048,576 tokens), 5 at 256,900 each at 98% backing.

## Caveats

- The deep-band 165–200k performance grids are not yet run. The needle probe is the only >131k measurement so far; every grid in the campaign ran at ≤126k caps.
- Single host: 2× R9700 32 GiB, 30 GiB RAM, custom kernel. Numbers do not generalize silently.
- Engine 1.9.0 at the pinned digest; baseline re-validation on the old engine was not run (user decision, recorded).
- The projection row in the ladder is elastic GiB over measured density. It is marked because it is not a measurement.

<!-- NAVIGATION START -->

[Home](../index.md) · [Overview](../README.md) · [Latest campaign](RADIANCE-CAMPAIGN-2026-10-21.md) · [Charts](CHARTS.md)
