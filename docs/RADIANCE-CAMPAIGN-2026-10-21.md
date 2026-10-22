---
layout: default
title: "The radiance campaign: same agents, new engine (21 October 2026)"
---

# The radiance campaign: same agents, new engine (21 October 2026)

## What ran

The same four-agent deep-context workload as the 19 October campaign, new engine. `stilldeadcode/radiance` 1.9.0, digest-pinned, loading the converted M2 checkpoint (`ukisai/Swift-1.5-Qwen3.8-27b-W4A16-AWQ`, rev `81a28ee7`, `.rad` bundle). Fixed knobs: TP=2, 131,072-token context, fp8 KV, 4 sequence slots, MTP-4 speculative lane. The harness is byte-identical to the one that produced the old campaign's S/Y/Z arms: `bench_agents4.py`, sha256 `ab17f129…` — ~7.9k-token system prompt, +11,983 tokens per turn, cap checked before the turn on previous prompt tokens, temperature 0.7, streaming, procedural 512×512 PNGs with `--images` on the vision cell.

One number to keep in view. Baseline re-validation on the old engine was NOT run (user decision, recorded). What that licenses: comparing the new engine to the old campaign's measurements, workload-to-workload, same client, same checkpoint. What it does not license: claiming the old engine would reproduce those numbers today, or attributing every delta to the engine alone.

## Deep-context grid

Wall seconds, 10 turns per agent, 126k harness depth cap. Radiance cells (R1–R4, R4-vision, R6-n1..n4, R9): [data/rocm-10.1/radiance-campaign-2026-10-21.csv](../data/rocm-10.1/radiance-campaign-2026-10-21.csv); old-engine twins (Y/Z arms): [data/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.csv](../data/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.csv). Ten radiance cells, 280 turns, zero errors.

| Cell | radiance non-spec | Y-arm (old, non-spec) | radiance MTP-4 | Z-arm (old, MTP-4) |
|---|---:|---:|---:|---:|
| n=1 | 130.6 | 126.7 | 102.3 | 115.1 |
| n=2 | 232.1 | 212.1 | 204.7 | 231.6 |
| n=3 | 327.0 | 306.4 | 300.5 | 323.1 |
| n=4 | 429.3 | 401.8 | 402.7 | 488.7 |
| n=4 vision | 685.7 | 651.9 | — | — |

## Where the wins live

Per-agent decode at n=1 goes 54.4 → 137.9 t/s with MTP-4, a 2.5× (R1 vs R6-n1); aggregate decode at n=1 is 10.33 vs 19.61 t/s, +90%. TTFT by depth band drops across the board: n=1 60–90k, 8.32 s vs 11.79 s old (−30%); n=2 90–120k, 10.19 s vs 22.77 s (−55%); n=3, 10.37 s vs 29.08 s (−64%). Draft acceptance measured live on the campaign workload: 0.657 mid-run, 0.679 final. MTP-4 beats the old engine's own MTP arm at every n (−7% to −18%) and beats radiance non-spec at every n; at n=4 the MTP wall (402.7 s) lands on the old engine's non-spec wall (401.8 s). The prefix cache does the prefill work: under n=4 load, intake 8,648 t/s = 1,690 t/s GPU recompute + 6,958 t/s cache-served — 80% of prompt volume served from cache.

## What the old engine kept

Two things. First, shallow-band TTFT on warm initial prompts: radiance measures 11.97–14.32 s where the old engine measured 0.0–1.78 s — a prefix-cache admission effect, not compute (R2/R3 `ttft_0_30k`). Second, the 13 GiB tier A/B (R9, 402.0 s against R6-n4's 402.7) is inside seed noise. The caveat list stays visible: single host (2× R9700 32 GiB, 30 GiB RAM, custom kernel) — no silent generalization; no baseline re-validation on the old engine; the engine reports 1.9.0 at the pinned digest while the onboarding docs reviewed were 1.8.1-era; FB/vision cells are seed-sensitive; tier growth is justified by fleet pressure (570 `store_full` refusals at 10 GiB), not by the single-cell grid.

## Fleet acceptance

Four Pi coding agents, real Falling Blocks builds, 60-minute cap, seeds 100–103: **4/4 games delivered, 4/4 node-syntax PASS**. Agents 2–3 exited clean (0); agents 0–1 timed out at the 60-minute cap after delivering complete games (exit 124 — the campaign's delivered-then-timeout pattern; per-agent exit codes from the fleet receipts). Prefix-cache hit share ran 80.1–94.3% of fleet prompt volume. The games are published under [examples/rocm-10.1/falling-blocks/radiance-20261021/](../examples/rocm-10.1/falling-blocks/radiance-20261021/), with per-file sha256 in [manifest.json](../examples/rocm-10.1/falling-blocks/radiance-20261021/manifest.json); fleet numbers in [data/rocm-10.1/radiance-falling-blocks-fleet-2026-10-21.csv](../data/rocm-10.1/radiance-falling-blocks-fleet-2026-10-21.csv). Campaign baselines for reference: 3/4 delivered on the first single-card attempt; dual-card best 4/4 with clean exits for 2.

## Concurrency physics

The fp8 KV pool is 524,304–524,336 tokens at TP2 — 4×131k, 18.6 KiB/token. The depth cap is arithmetic: pool ÷ agents. Four agents get 131k; five get 104.8k; six get 87.4k. Six agents at full 131k depth is impossible on this box: 14.5 GiB of KV against a 9.74 GiB pool. The pinned host tier tops out at ~13 GiB (driver page limit 15.29 GiB on this 30 GiB host; a 16 GiB boot ABORTED with exact arithmetic), and the RAM tier is the deepest published tier — no disk tier exists in the engine.

## Verdict

The engine change bought exactly what the old campaign's physics said it should buy: MTP-4 is now the default lane for deep-context agent service, beating the old engine's MTP arm at every agent count and its non-spec twin at n=1–3 (a 0.2% tie at n=4), with decode +90% at n=1 and TTFT down 30–64% in the bands that matter. The old engine keeps its warm-prefix shallow-band edge and the 13 GiB tier tie. The honest shape of the win is a fleet win: 4/4 delivered with 80–94% of prompt volume cache-served, on a box whose hard ceiling is four 131k agents. Past four, depth falls by the arithmetic above — that is a pool-size statement, not an engine limitation, and it applies to both engines.

<!-- NAVIGATION START -->

[Home](../index.md) · [Overview](../README.md) · [Charts](CHARTS.md)
