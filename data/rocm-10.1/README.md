---
layout: default
title: "ROCm 10.1 data"
---

# ROCm 10.1 data

This folder contains the selected results only. Version assignment follows the reviewed [catalogue](../../data/telemetry-catalog.json); older traces use profile/date evidence, not per-run immutable image IDs.

- [ROCm base-image four-agent stress run](rocm-base-image-four-agent-stress-run.csv)
- [Retained historical agent workloads](historical-agent-workloads.csv)
- [Seven completed dual-card text-growth cells, 18 October 2026](dual-card-text-growth-2026-10-18.csv)

[What was excluded and why](../../docs/EXCLUDED-TESTS.md). Different workload/configuration histories are not a controlled ROCm A/B.

[Four completed GPU A single-card cases](single-card-gpu-a-text-growth-2026-10-18.csv) · [Configuration](single-card-gpu-a-configuration.json) · [Side-by-side requirements and conclusions](../../README.md#best-recorded-single-card-setup-for-34-deep-context-agents)

[Eight completed follow-up cases: single vs dual](follow-up-single-vs-dual-text-growth-2026-10-18.csv) · [Review limits](follow-up-single-vs-dual-notes.json)

[Eight-cell dual R9700 model & spec-decode campaign, 19 October 2026](dual-r9700-spec-campaign-2026-10-19.csv) · [Campaign write-up, including the published-fast-lane contradiction](../../docs/DUAL-R9700-SPEC-CAMPAIGN.md)

[41-cell agent-count sweep — eight setups, 1–4 agents, vision input, 19 October 2026](dual-r9700-agent-count-sweep-2026-10-19.csv) · [16K fast-lane repro (two cells; cancelled arms recorded)](dual-r9700-8k-repro-2026-10-19.csv)

[Ten-row radiance 1.9.0 campaign — non-spec and MTP-4 lanes, 21 October 2026](radiance-campaign-2026-10-21.csv) · [Four-agent Pi fleet acceptance, 21 October 2026](radiance-falling-blocks-fleet-2026-10-21.csv) · [Campaign write-up](../../docs/RADIANCE-CAMPAIGN-2026-10-21.md) · [Engine comparison: radiance vs radiance-vllm](../../docs/RADIANCE-VS-VLLM.md)

[Four-cell radiance single-card grid — TP1, pool-derived depth caps, 22 October 2026](radiance-single-card-2026-10-22.csv) · [Single-card comparison: old engine vs radiance TP1 vs TP2](radiance-single-card-comparison-2026-10-22.csv) · [Pool ceiling ladder — measured boots and marked projections](radiance-pool-ceiling-2026-10-22.csv)

## Campaigns and counting

The seven-cell dual export uses an **8 GiB** tier. The eight-cell GPU A/dual follow-up uses **10 GiB** and is a separate campaign. [The report](../../docs/FINAL-REPORT-20261018.md) contains serving settings, preemption counts and first coding-fleet outcomes.

The follow-up CSV counts timed turns: GPU A four-agent = 114; dual two-agent = 63. Including one empty completion in each gives 115/64 completed responses in the acceptance ledger. TTFT excludes those empty completions. Earlier review-notes JSON records the scope of the original export; the later report adds handover evidence without changing the exported data.

The [eleven ROCm 10.1 games](../../examples/rocm-10.1/falling-blocks/index.html) are published separately; raw session transcripts remain private. The raised-budget single-card retry completed with four clean deliveries in 75:23.

## Completed coding fleets

[Per-agent fleet outcomes](falling-blocks-fleet-outcomes-2026-10-18.csv) records all twelve agent attempts, including the missing first-attempt game. It is transcribed from the completed local campaign report, not a new session parse. Blank usage/timing fields were not available precisely in that report; they are not zero. Eleven games are linked by fleet and agent.

## Radiance engine campaign (21 October 2026)

The radiance campaign runs the recovered `bench_agents4.py` harness — byte-identical to the file that produced the old campaign's arms — under the radiance 1.9.0 engine on the M2 checkpoint (`awq-int4-rad` bundle, TP2). Ten cells: the n=1–4 non-spec deep grid, the n=1–4 MTP-4 lane, the n=4 vision cell, and the 13 GiB tier A/B at n=4 MTP-4. Columns: arm, model, target revision, quantization, spec mode/depth, agents, images, depth cap, turns, errors, wall seconds, max depth, decode and aggregate tokens/s, TTFT averages by depth band, TP99 ITL, KV pool tokens, prefix-tier size, max sequences, engine, status. KV pool 524,304–524,336 tokens (fp8, 4×131k); prefix tier 10 GiB on all arms, 13 GiB on the A/B row.

The fleet CSV records the radiance Pi acceptance: four agents, seeds 100–103, 60-minute cap. Columns: fleet, agent, seed, turns, exit status, deliverables complete, clean delivery, output tokens, cache-read tokens, cache-hit share, timeout, reported syntax, game file. 4/4 delivered, 4/4 syntax PASS; agents 2–3 exited clean (`clean_delivery` true), agents 0–1 timed out at the cap after delivering complete games (exit 124, `clean_delivery` false by definition) — per-agent exit codes from the fleet receipts (`exit-status.txt`), which corrected an all-124 derivation slip on 22 Oct. Prefix-cache hit share 80.1–94.3% of fleet prompt volume.

Caveats: baseline re-validation on the old engine was not run (user decision, recorded) — comparisons are workload-to-workload on the same client, not a fresh baseline. The 13 GiB tier A/B is within seed noise; the tier increase is justified by fleet pressure (`store_full` refusals at 10 GiB), not by the single-cell grid. Vision and falling-blocks cells are seed-sensitive. Single host, 2× R9700 32 GiB, 30 GiB RAM, custom kernel; numbers do not generalize silently.

## Radiance single-card + 200k context (22 October 2026)

The single-card grid runs the same harness at TP=1, MTP-4, 4 slots: the KV pool (404,608 tokens, fp8) is measured at boot, depth caps derived from pool arithmetic (pool ÷ agents minus 12,239 lockstep overshoot → 126,000 / 126,000 / 122,630 / 88,913). The comparison CSV puts per-turn price, TTFT and per-request decode side by side: vllm-radiance single-card (27-turn family — s/turn normalizes turn count, not the lane), radiance TP1, radiance TP2. The ceiling CSV records the pool ladder: four measured boot prints (404,608 / 524,304 / 786,448 / 1,228,816 tokens), the elastic ceiling (~1,284,500) and TTM tier max (~471,400) as marked projections. The 1,228,816-token row is the current service default: 6 slots × 204,800 context, backed 100%; the checkpoint's trained context is 262,144. Deep-band (165–200k) performance grids are not yet run; the needle probe at 165,075 tokens is the only >131k measurement published.

<!-- NAVIGATION START -->

[Home](../../index.md) · [Overview](../../README.md) · [Latest campaign](../../docs/RADIANCE-CAMPAIGN-2026-10-21.md) · [Charts](../../docs/CHARTS.md)
