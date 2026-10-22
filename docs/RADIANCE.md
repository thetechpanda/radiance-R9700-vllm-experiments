---
layout: default
title: "radiance: long-context agents, one card or two"
---

# radiance: long-context agents, one card or two

The standalone engine changes how this small host serves long conversations. The interesting result is the combination of first-token latency, generation and allocated context—not a single throughput score. This page collects the recorded 21–22 October settings and results; the [head-to-head comparison](RADIANCE-VS-VLLM.md) keeps the earlier vllm-radiance measurements beside them.

## Identity

- **Engine:** `stilldeadcode/radiance` **1.9.0**, digest-pinned.
- **Serving alias (API `target_model`):** `ukisai/Swift-1.5-Qwen3.8-27b-W4A16-AWQ`.
- **`.rad` source:** the conversion record names an **INT4** source, `ukisai/Swift-1.5-Qwen3.8-27b-INT4`, revision **`81a28ee7`** (radiance rows). The old-engine Y/Z reference records the W4A16-AWQ alias at **`9dba8a05`**.
- **Weights / KV:** 4-bit AWQ (`awq-int4-rad`), **FP8** KV.
- **Harness:** byte-identical `bench_agents4.py`, SHA-256 `ab17f129…f409f741b` (verified).

## Reading the numbers

- **`decode_tokens_s`** = successful output tokens ÷ whole-cell wall: an **aggregate end-to-end** rate including prefill and queueing, **not** per-request steady-state decode.
- **`tg_avg` / `turn_tg_avg`** = arithmetic mean of `completion_tokens ÷ (request wall − TTFT)` over **valid turns with decode interval > 0.5 s**, not all turns.
- **Fleet `cache_hit_pct`** is the released per-agent cache metric, **separate** from the sweep's `prefix_cache_hit_frac` (a zero-TTFT proxy); do not call the fleet number a zero-TTFT proxy.
- **Sweep TTFT bands:** 0 / blank means **no sample**, not zero latency.
- **Turns** are total across the cell: radiance TP1 has 10/20/30/32 at n=1–4; TP2 R6 has 10/20/30/40. TP1 n4 is eight per agent, not ten.
- The earlier ~15% repeat spread came from a **different model** and is **not** a significance threshold.

## n1–4, TP1 vs TP2, MTP-4

TTFT (mean s) · per-turn TG (t/s) · aggregate output (t/s). Sources: [TP1 grid](../data/rocm-10.1/radiance-single-card-2026-10-22.csv), R1x n1–4; [TP2 grid](../data/rocm-10.1/radiance-campaign-2026-10-21.csv), R6 n1–4. All cells in these two lanes use MTP-4. The wider dual grid includes non-speculative rows too.

| n | TP1 TTFT | TP1 TG | TP1 agg | TP2 TTFT | TP2 TG | TP2 agg |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 7.07 | 84.4 | 22.60 | 8.37 | 137.9 | 24.79 |
| 2 | 8.87 | 26.6 | 23.63 | 10.72 | 41.0 | 24.97 |
| 3 | 11.34 | 23.3 | 26.44 | 12.85 | 25.9 | 24.29 |
| 4 | 14.34 | 17.4 | 27.85 | 17.10 | 16.8 | 24.56 |

TP1 records shorter walls at n=1–3; the 4–6% TP1/TP2 gaps **do not isolate all-reduce** (tier, depth and run length also differ). The larger TP2 allocation supports the deeper four-agent growth target used in this campaign.

## Depth and tier

- **TP1:** pool **404,608** tokens, **13 GiB** host tier; n4 cap **88,913** (observed max **99,075**).
- **TP2:** pool **524,304** tokens, **10 GiB** tier (campaign); n4 cap **126,000** (observed **123,710**).
- Old engine n4: cap 126,000, observed **126,691** — **unequal depths** to radiance TP1.
- The cap is checked **pre-turn** on previous prompt tokens; a final growth step can **overshoot**, so observed > cap is expected.


## 6×200k is allocation only

Raising `--max-model-len` to 204,800 (TP2, 6 slots) boots a **1,228,816-token** pool — 100% backing of the 6×200k worst case. This is a **boot allocation**, not simultaneous full-depth performance; the deep-band grids were not run. Acceptance *probes* (over-cap 400, 165k needle, `/server_info`) are **not CSV-exported**.

## Prompt processing (PP)

There is **no matched validated raw-kernel PP benchmark** between the engines; `pp_effective_ingest_tok_s` and prompt-credit traces must not be used to manufacture one.

## Fleet: the files arrived, the processes timed out

Radiance: **4/4 games delivered, 2/4 clean** (agents 0–1 exit 124 after delivery; agents 2–3 exit 0). vLLM dual fleet: **4/4 clean**. `reported_syntax` is the campaign check, not a fresh browser qualification.

Source: [radiance fleet CSV](../data/rocm-10.1/radiance-falling-blocks-fleet-2026-10-21.csv), agents 0–3. [Play the released games](../examples/rocm-10.1/falling-blocks/index.html). The released `cache_hit_pct` values span **80.1–94.3%**, with no common definition established against the older sweep proxy.

## Which configuration answers which question?

| Need | Recorded evidence | Limit |
|---|---|---|
| One agent, generation estimate | TP2 MTP-4: 137.9 tok/s turn TG; 8.37 s mean TTFT | Short-response estimate, not real-agent productivity |
| Several agents on one card | TP1 completed four cells, 92 turns, zero errors | At n4 the growth target falls to 88.9k |
| Four agents near the 126k growth target | TP2 R6-n4: 402.7 s, 17.10 s mean TTFT | Actual max prompt 123,710; not sustained full-131k qualification |
| Larger history allocation | Six-slot 200k boot: 1,228,816 GPU tokens | No corresponding six-agent throughput grid |
| A host tier change | R9 13 GiB vs R6-n4 10 GiB: 402.0 vs 402.7 s | No repeat distribution to resolve the 0.7 s gap |

[Dual-card campaign](RADIANCE-CAMPAIGN-2026-10-21.md) · [Single-card campaign](RADIANCE-SINGLE-CARD-2026-10-22.md) · [Capacity ladder](RADIANCE-200K-CONTEXT-2026-10-22.md) · [Model identities](MODELS.md).

## Scope

Single host (2× R9700 32 GiB, 30 GiB RAM, custom kernel). **No universal winner**; numbers do not generalize silently. Baseline re-validation on the old engine was not run (recorded).

<!-- NAVIGATION START -->

[Home](../index.md) · [Compare](RADIANCE-VS-VLLM.md) · [vllm-radiance](VLLM-RADIANCE.md) · [Charts](CHARTS.md) · [Stuff for nerds](CODE-CORNER.md) · [Disclosure](REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
