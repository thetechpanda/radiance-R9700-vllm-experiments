---
layout: default
title: "The radiance campaign: same agents, new engine (21 October 2026)"
---

# The radiance campaign: same agents, new engine (21 October 2026)

## What ran

Ten radiance cells, 280 total timed turns, zero errors. Engine: `stilldeadcode/radiance` 1.9.0, digest-pinned. Model: `ukisai/Swift-1.5-Qwen3.8-27b-W4A16-AWQ` (API id W4A16-AWQ; the conversion record names the source INT4 `.rad`), revision `81a28ee7`, FP8 KV. Historical references (Y/Z arms): same model family, revision `9dba8a05`, BF16 KV, vllm 1.1.0-rc1. Harness: `bench_agents4.py`, sha256 `ab17f129b9571a0bac353801669b853a039da2fa1834a20e675b469f409f741b`. Fixed knobs: TP=2, 131 072-token context, 4 sequence slots (a configuration allocation, not a hardware ceiling), MTP-4 speculative lane where marked. Depth cap checked before each turn on previous prompt tokens (preturn); overshoot is expected.

No baseline re-validation on the old engine was run (user decision). This licenses workload-to-workload comparison, the recovered client and related model family. Different revisions and KV formats prevent an isolated engine effect. It does not license claiming the old engine would reproduce those numbers today.

![Dual-engine wall-time comparison](../graphs/rocm-10.1/engine-wall-comparison.svg)

[Open full-size chart](../graphs/rocm-10.1/engine-wall-comparison.svg).

## Wall table

Whole-cell wall seconds, 126,000-token growth target, ten turns per agent (10/20/30/40 total at n1–4). Every row here is **TP2**; the smaller TP1 n4 target belongs to the [separate single-card report](RADIANCE-SINGLE-CARD-2026-10-22.md).

| Cell | Radiance (FP8 KV) | Y/Z historical reference (BF16 KV) |
|---|---:|---:|
| n=1 non-spec | 130.6 | 126.7 (Y1) |
| n=2 non-spec | 232.1 | 212.1 (Y2) |
| n=3 non-spec | 327.0 | 306.4 (Y3) |
| n=4 non-spec | 429.3 | 401.8 (Y4) |
| n=4 vision | 685.7 | 651.9 (Y5) |
| n=1 MTP-4 | 102.3 | 115.1 (Z1) |
| n=2 MTP-4 | 204.7 | 231.6 (Z2) |
| n=3 MTP-4 | 300.5 | 323.1 (Z3) |
| n=4 MTP-4 | 402.7 | 488.7 (Z4) |
| n=4 MTP-4, 13 GiB tier | 402.0 | — |

Data: [radiance-campaign-2026-10-21.csv](../data/rocm-10.1/radiance-campaign-2026-10-21.csv) · [dual-r9700-agent-count-sweep-2026-10-19.csv](../data/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.csv)

## Throughput

Two metrics with distinct denominators:

- **Aggregate end-to-end output** (`decode_tokens_s`): sum of successful output tokens ÷ whole-cell wall. End-to-end rate including prefill and queueing. Not a per-request steady-state figure.
- **Per-turn TG** (`tg_avg` / `turn_tg_avg`): arithmetic mean of completion_tokens ÷ (request wall − TTFT) over valid turns with duration > 0.5 s. Not all turns qualify.

At n=1 MTP-4: old engine (Z1) aggregate 12.94 t/s, per-turn TG 185.7 t/s. New engine (R6-n1) aggregate 24.79 t/s, per-turn TG 137.9 t/s. Radiance records **91.6% higher aggregate end-to-end output**, **25.7% lower mean turn TG**, and **11.1% shorter wall** for these n1 MTP cells. Prompt work, output quantity, stream timing and waiting contribute differently to those metrics; the export does not isolate the cause of the wall-time difference.

## TTFT

Mean TTFT, MTP-4, all n:

| n | Radiance | Old (Z) |
|---|---:|---:|
| 1 | 8.37 s | 10.82 s |
| 2 | 10.72 s | 5.69 s |
| 3 | 12.85 s | 16.65 s |
| 4 | 17.10 s | 20.67 s |

Depth-band comparison, non-spec radiance vs Y-arm (old non-spec):

| Band | n=1 Rad | n=1 Y | n=2 Rad | n=2 Y | n=3 Rad | n=3 Y |
|---|---:|---:|---:|---:|---:|---:|
| 0–30 k | 7.48 | 3.59 | 11.97 | 0.0* | 14.32 | 1.78 |
| 30–60 k | 7.72 | 11.76 | 8.80 | 7.43 | 10.90 | 8.78 |
| 60–90 k | 8.32 | 11.79 | 9.19 | 19.45 | 9.32 | 18.22 |
| 90–120 k | 9.16 | 13.52 | 10.19 | 22.77 | 10.37 | 29.08 |

\* 0 or blank in the sweep CSV means no turns fell in that depth band; it does not indicate zero TTFT.

The valid shallow-band observations favour the older engine; several deeper bands favour radiance. Cache admission, prompt work and other effects are not isolated by the export. Do not turn the missing Y2 shallow sample into a zero-latency claim.

## Fleet

Four Pi coding agents, real Falling Blocks builds, 60-minute cap, seeds 100–103: **4/4 games delivered, 2/4 clean exits** (agents 0–1 exit 124 after delivery; agents 2–3 exit 0). The released per-agent `cache_hit_pct` spans 80.1–94.3%. Fleet `cache_hit_pct` is a separate metric from the sweep's `prefix_cache_hit_frac`; one is not a proxy for the other. Games published under [the game gallery](../examples/rocm-10.1/falling-blocks/index.html); fleet data in [radiance-falling-blocks-fleet-2026-10-21.csv](../data/rocm-10.1/radiance-falling-blocks-fleet-2026-10-21.csv). Campaign baseline: vllm dual fleet 4/4 delivered, 4/4 clean.

## Caveats

- Single host (2× R9700 32 GiB, 30 GiB RAM, custom kernel). No universal winner; results do not generalize silently.
- 4 sequence slots is a configuration allocation, not a hardware ceiling.
- TP1 vs TP2 gaps of 4–6 % do not isolate allreduce cost.
- The 6×200 k context run was a boot-allocation test only.
- A 15 % repeat spread observed on a different model is not a significance threshold for this campaign.
- Private probes referenced in discussion are not CSV-exported; only public CSV data is cited here.

## What this campaign establishes

All ten radiance cells complete **280 turns with zero reported errors**. Historical non-speculative walls are shorter; radiance MTP-4 walls are shorter than the historical MTP lane by **7.0–17.6%**. Mean MTP TTFT is lower at n1, n3 and n4, higher at n2. The aggregate-output and turn-TG metrics favour different deployments at n1. These are useful measurements with different strengths, not one engine winning every column.

The campaign's four-slot pool is an allocation choice, not a hardware ceiling. The later [six-slot capacity ladder](RADIANCE-200K-CONTEXT-2026-10-22.md) supersedes that allocation without retroactively qualifying six-agent performance. For all percentages, model identities, side-by-side generation columns and source cells, read the [full engine comparison](RADIANCE-VS-VLLM.md).

<!-- NAVIGATION START -->

[Home](../index.md) · [Compare](RADIANCE-VS-VLLM.md) · [vllm-radiance](VLLM-RADIANCE.md) · [radiance](RADIANCE.md) · [Charts](CHARTS.md) · [Stuff for nerds](CODE-CORNER.md) · [Disclosure](REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
