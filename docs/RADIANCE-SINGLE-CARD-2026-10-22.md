---
layout: default
title: "One card, four agents: the radiance single-card campaign (22 October 2026)"
---

# One card, four agents: the radiance single-card campaign (22 October 2026)

## What ran

One card, not two. The same four-agent deep-context workload as the 21 October campaign, `stilldeadcode/radiance` 1.9.0 digest-pinned, the M2 checkpoint (`ukisai/Swift-1.5-Qwen3.8-27b-W4A16-AWQ`, rev `81a28ee7`, `.rad` bundle). Fixed knobs: TP=1, 131,072-token context, fp8 KV, 4 sequence slots, MTP-4 speculative lane, 13 GiB host tier. Boot print: weights 14.41 GiB on the card, KV cache 14.27 GiB, pool 404,608 tokens — "3.1 sessions at 131072", 77% backing of the 4×131072 worst case. The depth caps are arithmetic: pool ÷ agents, minus a 12,239-token lockstep overshoot — 126,000 / 126,000 / 122,630 / 88,913 at n=1/2/3/4. Grid: 4/4 cells, 92 turns, zero errors. Numbers: [data/rocm-10.1/radiance-single-card-2026-10-22.csv](../data/rocm-10.1/radiance-single-card-2026-10-22.csv).

## The per-turn price

Seconds per turn by agent count, three engines:

| n | radiance TP1 (10-turn) | vllm-radiance single-card (27-turn) | radiance TP2 (10-turn) |
|---|---:|---:|---:|
| 1 | 9.68 | 12.59 | 10.23 |
| 2 | 9.67 | 9.74 | 10.23 |
| 3 | 9.60 | 30.09 | 10.02 |
| 4 | 9.06 | 34.65 | 10.07 |

Source: [data/rocm-10.1/radiance-single-card-comparison-2026-10-22.csv](../data/rocm-10.1/radiance-single-card-comparison-2026-10-22.csv).

The headline. Radiance TP1 goes 9.68 → 9.06 from n=1 to n=4 — flat. The old engine goes 12.59 → 34.65 — a 2.7× explosion. On the new engine, a turn costs the same with four agents as with one. On the old engine, four agents is nearly four times the price of one. That is not an optimization; that is the queue behaving differently.

## The TTFT bill

Old-engine mean TTFT: 7.46 / 11.92 / 71.46 / 101.38 s, max 654.91 s at n=4. Radiance TP1: 7.07 / 8.87 / 11.34 / 14.34 s mean, 22.02 s max — same comparison CSV. Stated plainly: the old engine's 126k depth at n=4 was achieved VIA PREEMPTION, and the TTFT is the bill. A 101.38 s mean to start a turn at four agents is preemption showing up on the clock. Radiance TP1 ran an honest 88.9k cap at n=4 — pool ÷ 4, no tricks — and its worst turn-start across the whole grid was 22.02 s, against 654.91 s. The cap is smaller; the start is honest.

## Per-agent decode

n=1: 84.4 t/s per agent on the MTP lane, 2.1× the old engine's 40.0 non-spec (comparison CSV, both columns). At n=2–3 the old non-spec lane keeps its edge, stated honestly: 32.4 / 26.0 t/s against radiance's 26.6 / 23.3 — a 10–20% decode advantage, steady non-spec decode against the speculative lane. If you measure only tokens per second at n=2–3, the old engine wins that column. What it pays for it is the TTFT and the per-turn price above, and that is where this campaign lives.

## TP1 vs TP2

Radiance against itself. TP1 is faster at n=1–3: walls 96.8 / 193.4 / 287.9 s against TP2's 102.3 / 204.7 / 300.5 s — no all-reduce tax on a single card, lower TTFT (comparison CSV, single-card CSV). TP1's per-agent decode is the weaker column (84.4 vs 137.9 t/s at n=1), and TP2's value is pool plus depth: 524,304 tokens against 404,608, which is what holds the n=4 cap at 126k instead of 88,913. One card is the faster engine; two cards are the bigger pool. Neither is a mistake.

## Caveats

- The old-engine baseline is the 27-turn text-growth family (27/63/94/114 turns at n=1–4); the radiance rows are the 10-turn family. s/turn normalizes turn count, not lane.
- The TP1 pool (404,608) is boot-measured, not formula-exported.
- Seed noise is ~15%; deltas under that are not claims.
- Single host: 2× R9700 32 GiB, 30 GiB RAM, custom kernel. No silent generalization.

<!-- NAVIGATION START -->

[Home](../index.md) · [Overview](../README.md) · [Latest campaign](RADIANCE-CAMPAIGN-2026-10-21.md) · [Charts](CHARTS.md)
