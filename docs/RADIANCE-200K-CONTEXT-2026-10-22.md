---
layout: default
title: "From 131k to 200k: what the bigger memory pool proves"
---

# From 131k to 200k: what the bigger memory pool proves

The original radiance TP2 campaign allocated about 524k GPU KV tokens. A later boot allocated **1,228,816** on the same cards: **134.4% more**. The key change was the allocation target—more slots and a longer configured context—not more hardware.

That result answers a capacity question. It does not yet answer how quickly six agents can work at 200k each.

## Four measured boots

The [pool-ladder CSV](../data/rocm-10.1/radiance-pool-ceiling-2026-10-22.csv) contains these recorded boot allocations. Context uses exact token counts; “131k” and “200k” are shorthand.

| Configuration | KV GiB per card | GPU pool tokens | Full-depth allocation equivalents | Approx. KiB per token per card |
|---|---:|---:|---:|---:|
| TP1, 4 slots, 131,072 context | 14.27 | 404,608 | 3.1 | 36.98 |
| TP2, 4 slots, 131,072 context | 9.74 | 524,304 | 4.0 | 19.48 |
| TP2, 6 slots, 131,072 context | 13.61 | 786,448 | 6.0 | 18.15 |
| TP2, 6 slots, 204,800 context | 20.79 | 1,228,816 | 6.0 | 17.74 |

Per-card density = **GiB on one card × 1,048,576 KiB/GiB ÷ shared pool tokens**. Each shared token requires a KV shard on each TP2 card; dividing the token count by two would double the reported cost incorrectly. Total two-card storage per token is twice the per-card value. Rounded GiB values and fixed per-session overhead mean this is an allocation ratio, not one universal marginal KV cost.

![Measured GPU pool allocation across slot and context settings](../graphs/rocm-10.1/memory-allocation.svg)

[Open full-size chart](../graphs/rocm-10.1/memory-allocation.svg).

## Why two cards initially looked like one

A useful approximation is **pool = min(available KV capacity, slots × configured context)**, with small engine rounding overhead. Four × 131,072 targets 524,288 tokens; the recorded TP2 pool is 524,304. Its slot target binds before the available cards do.

The TP1 pool, by contrast, is **404,608**, about **77.2%** of that four-slot target. It is VRAM-limited in this profile. Those two numbers were sized by different constraints.

Increasing TP2 to six slots allocates 786,448 tokens at 131k; increasing context to 204,800 produces 1,228,816. Six × 204,800 is **1,228,800**; the boot allocation is 16 tokens above that target. None of these divisions is a throughput prediction.

## Model context, deployment context, observed depth

The recorded conversion/model inspection reports **262,144** for `n_ctx_train` / `max_position_embeddings`. The earlier radiance deployment used **131,072**; the later one used **204,800**. Model metadata describes an intended context range, not a quality guarantee at every depth. The [model inventory](MODELS.md) separates the conversion source and serving alias.

The operator recorded a **165,075-token needle prompt** with the expected answer and repeated TTFT of 0.3–0.4 s, plus a clean rejection of an over-cap request. These are **reported acceptance probes** from the prior campaign record. Their raw timing and response receipts are **not included in the public pool CSV**, so they remain separate from the exported allocation measurements. Fast repeats alone do not isolate whether reuse came from GPU or host caching.

There is **no 165–200k depth/concurrency performance grid** in this release, and no six-agent 200k workload qualification. The measured TP1/TP2 campaign depths and counts remain in the [single-card](RADIANCE-SINGLE-CARD-2026-10-22.md) and [dual-card](RADIANCE-CAMPAIGN-2026-10-21.md) reports.

## The projections stay projections

| Quantity | Token estimate | Status / interpretation |
|---|---:|---|
| TP2 elastic ceiling | ~1,284,500 | Projection from 22.23 GiB/card and selected allocation density; not a boot result |
| Host prefix tier, 13 GiB | 400,912 | Recorded tier print; completed-conversation state, not live GPU KV |
| Driver-cap host tier, 15.29 GiB | ~471,400 | Projection before vision/other pinned reservations; not an available usable prefix budget |

Source: the same [capacity CSV](../data/rocm-10.1/radiance-pool-ceiling-2026-10-22.csv), with its `kind` column retained. The GPU and host tiers hold different forms of state. Adding their tokens does not establish extra live-agent concurrency.

For scale, four 262,144-token allocations require **1,048,576** tokens, within the later measured GPU pool by arithmetic. That does not demonstrate four 256k requests running successfully. Five equal shares of the elastic projection would be about 256,900 tokens each; both the ceiling and that division remain unvalidated.

The capacity improvement is useful without upgrading it into a performance claim: a larger allocation target fit. The next unanswered question is its latency under simultaneous long-context work.

<!-- NAVIGATION START -->

[Home](../index.md) · [Compare](RADIANCE-VS-VLLM.md) · [vllm-radiance](VLLM-RADIANCE.md) · [radiance](RADIANCE.md) · [Charts](CHARTS.md) · [Stuff for nerds](CODE-CORNER.md) · [Disclosure](REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
