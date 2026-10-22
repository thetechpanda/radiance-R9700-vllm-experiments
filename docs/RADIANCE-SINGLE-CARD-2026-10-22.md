---
layout: default
title: "One card, four agents: the radiance single-card campaign (22 October 2026)"
---

# One card, four agents: the radiance single-card campaign (22 October 2026)

## What ran

One R9700 card, four agents, deep-context workload. `stilldeadcode/radiance` 1.9.0, digest-pinned. Model: `ukisai/Swift-1.5-Qwen3.8-27b-W4A16-AWQ`, revision `81a28ee7` (the W4A16-AWQ conversion record names the source INT4 `.rad` bundle; the historical Y/Z reference uses revision `9dba8a05`). Knobs: TP=1, 131,072-token context, fp8 KV, 4 sequence slots, MTP-4 speculative lane, 13 GiB host tier. Boot: weights 14.41 GiB, KV cache 14.27 GiB, pool 404,608 tokens (boot allocation, not simultaneous full-depth performance).

Growth stopping targets are min(126,000, pool ÷ agents − 12,239), with integer rounding: 126,000 / 126,000 / 122,630 / 88,913 at n=1/2/3/4. The cap is a pre-turn stopping target; `max_depth_tokens` can exceed it after a final growth step. Grid: 4/4 cells, 92 total timed turns, zero errors.

Source: [radiance-single-card-2026-10-22.csv](../data/rocm-10.1/radiance-single-card-2026-10-22.csv); the [historical config JSON](../data/rocm-10.1/single-card-gpu-a-configuration.json) describes vllm-radiance, not this radiance boot.

## Read the differences first

The historical GPU A reference used Swift-1.5 **INT4**, FP8 KV, MTP-4 and a **10 GiB** host tier. Radiance uses a converted `.rad` representation at the recorded revision, MTP-4 and **13 GiB**. Its n4 stopping target is **29.4% smaller**, and the older family has longer histories and more turns. Radiance TP2 uses a 10 GiB tier and retains the 126k target at four agents. The numbers below describe these operating points; they do not isolate an engine improvement at equal depth.

| Agents | Radiance TP1 stopping target | Radiance observed max | Historical GPU A observed max |
|---|---:|---:|---:|
| 1 | 126,000 | 120,325 | 123,462 |
| 2 | 126,000 | 123,515 | 127,278 |
| 3 | 122,630 | 123,710 | 127,658 |
| 4 | 88,913 | 99,075 | 126,691 |

Sources: [TP1 grid](../data/rocm-10.1/radiance-single-card-2026-10-22.csv), R1x n1–4; [original GPU A follow-up](../data/rocm-10.1/follow-up-single-vs-dual-text-growth-2026-10-18.csv), gpu-a n1–4. The historical stopping target is 126,000; neither target is a hard per-turn prompt limit.

## Per-turn price and total turns

Whole-cell wall divided by timed turns, by agent count. Under concurrency this is not the mean time an individual request spends waiting and generating. Turn counts in parentheses are **total timed turns** across all agents in the cell, not per-agent.

| n | radiance TP1 (turns) | vllm-radiance single-card, MTP-4 (turns) | radiance TP2 (turns) |
|---|---:|---:|---:|
| 1 | 9.68 (10) | 12.59 (27) | 10.23 (10) |
| 2 | 9.67 (20) | 9.74 (63) | 10.24 (20) |
| 3 | 9.60 (30) | 30.09 (94) | 10.02 (30) |
| 4 | 9.06 (32) | 34.65 (114) | 10.07 (40) |

Radiance TP1 n4 has 32 total turns (8 per agent). The old engine's per-turn cost rises from 12.59 to 34.65 s — a factor of 2.75 (34.65 / 12.59), not four.

Source: [radiance-single-card-comparison-2026-10-22.csv](../data/rocm-10.1/radiance-single-card-comparison-2026-10-22.csv)

## TTFT

| n | Old engine mean (s) | Old engine max (s) | Radiance TP1 mean (s) | Radiance TP1 max (s) |
|---|---:|---:|---:|---:|
| 1 | 7.46 | 18.78 | 7.07 | 9.54 |
| 2 | 11.92 | 40.64 | 8.87 | 12.53 |
| 3 | 71.46 | 456.19 | 11.34 | 16.38 |
| 4 | 101.38 | 654.91 | 14.34 | 22.02 |

At n4 the historical run records 12 preemptions alongside long waits; that observation alone does not isolate their contribution. Radiance has **85.9% lower mean TTFT** with **21.8% lower maximum observed depth**. Its 88,913-token target and 99,075-token observed maximum are different quantities.

![Single-card latency, depth and generation tradeoffs](../graphs/rocm-10.1/single-card-tradeoffs.svg)

[Open full-size chart](../graphs/rocm-10.1/single-card-tradeoffs.svg).

## Decode estimates

Two differently scoped metrics, presented as reported:

- **`decode_tokens_s`** — aggregate end-to-end output rate: total successful output tokens ÷ whole-cell wall seconds. Includes prefill, queueing, and idle gaps. Not per-request steady-state.
- **`tg_avg_tokens_s`** — arithmetic mean of per-turn rates (completion tokens ÷ (request wall − TTFT)) over valid turns with decode duration > 0.5 s. Excludes short and zero-token turns.

| n | Historical mean request decode | Radiance TP1 turn TG | Radiance TP2 turn TG |
|---|---:|---:|---:|
| 1 | 40.0 | 84.4 | 137.9 |
| 2 | 32.4 | 26.6 | 41.0 |
| 3 | 26.0 | 23.3 | 25.9 |
| 4 | 25.5 | 17.4 | 16.8 |

These are not kernel benchmarks. The historical column is `mean_request_decode_tokens_s` from the follow-up export, not the later sweep's aggregate `decode_tokens_s`. Radiance uses `tg_avg_tokens_s`. They are reported request/turn estimates; the release does not establish identical sampling filters across these two workload families. Historical estimates are higher at n2–4, and the radiance estimate is higher at n1.

## TP1 vs TP2

TP1 walls: 96.8 / 193.4 / 287.9 / 289.8 s. TP2 walls: 102.3 / 204.7 / 300.5 / 402.7 s. The 4–6% gaps at n=1–3 do not isolate all-reduce as the cause. TP2's pool is 524,304 tokens versus TP1's 404,608, which holds the n=4 cap at 126k instead of 88,913. The n4 wall gap also reflects fewer turns and a smaller history target on TP1; it cannot establish single-card superiority.

## Caveats

- The old-engine baseline is the 27/63/94/114 total-turn text-growth family, MTP-4 as its configuration JSON records. The radiance rows are 10/20/30/32 total turns. s/turn normalises turn count, not lane.
- The TP1 pool is boot-measured; the grid establishes the depths and counts above, not sustained simultaneous full-context performance.
- The earlier ~15% repeat spread came from a different model and is descriptive; it is not a significance threshold.
- Single host: 2× R9700 32 GiB, 30 GiB RAM, custom kernel. No universal winner.
- Fleet `cache_hit_pct` is a separate metric from the sweep's `prefix_cache_hit_frac`; they share no common definition. Sweep blank or 0 TTFT bands mean no sample, not zero latency.
- Private probes referenced in earlier prose are not CSV-exported and are not included here.


[All three configurations, per-turn wall and TTFT](../graphs/rocm-10.1/radiance-single-card-comparison-2026-10-22.svg) · [Full engine comparison](RADIANCE-VS-VLLM.md).

<!-- NAVIGATION START -->

[Home](../index.md) · [Compare](RADIANCE-VS-VLLM.md) · [vllm-radiance](VLLM-RADIANCE.md) · [radiance](RADIANCE.md) · [Charts](CHARTS.md) · [Stuff for nerds](CODE-CORNER.md) · [Disclosure](REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
