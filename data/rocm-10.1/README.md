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

[Four completed GPU A single-card cases](single-card-gpu-a-text-growth-2026-10-18.csv) · [Configuration](single-card-gpu-a-configuration.json) · [Side-by-side requirements and conclusions](../../HISTORICAL-OVERVIEW.md#best-recorded-single-card-setup-for-34-deep-context-agents)

[Eight completed follow-up cases: single vs dual](follow-up-single-vs-dual-text-growth-2026-10-18.csv) · [Review limits](follow-up-single-vs-dual-notes.json)

[Eight-cell dual R9700 model & spec-decode campaign, 19 October 2026](dual-r9700-spec-campaign-2026-10-19.csv) · [Campaign write-up, including the published-fast-lane contradiction](../../docs/DUAL-R9700-SPEC-CAMPAIGN.md)

[41-cell agent-count sweep — eight setups, 1–4 agents, vision input, 19 October 2026](dual-r9700-agent-count-sweep-2026-10-19.csv) · [16K fast-lane repro (two cells; cancelled arms recorded)](dual-r9700-8k-repro-2026-10-19.csv)

[Ten-row radiance 1.9.0 campaign — non-spec and MTP-4 lanes, 21 October 2026](radiance-campaign-2026-10-21.csv) · [Four-agent Pi fleet acceptance, 21 October 2026](radiance-falling-blocks-fleet-2026-10-21.csv) · [Campaign write-up](../../docs/RADIANCE-CAMPAIGN-2026-10-21.md) · [Engine comparison: radiance vs vllm-radiance](../../docs/RADIANCE-VS-VLLM.md)

[Four-cell radiance single-card grid — TP1, pool-derived depth caps, 22 October 2026](radiance-single-card-2026-10-22.csv) · [Single-card comparison: old engine vs radiance TP1 vs TP2](radiance-single-card-comparison-2026-10-22.csv) · [Pool ceiling ladder — measured boots and marked projections](radiance-pool-ceiling-2026-10-22.csv)

## Campaigns and counting

The seven-cell dual export uses an **8 GiB** tier. The eight-cell GPU A/dual follow-up uses **10 GiB** and is a separate campaign. [The report](../../docs/FINAL-REPORT-20261018.md) contains serving settings, preemption counts and first coding-fleet outcomes.

The follow-up CSV counts timed turns: GPU A four-agent = 114; dual two-agent = 63. Including one empty completion in each gives 115/64 completed responses in the acceptance ledger. TTFT excludes those empty completions. Earlier review-notes JSON records the scope of the original export; the later report adds handover evidence without changing the exported data.

The [fifteen ROCm 10.1 games](../../examples/rocm-10.1/falling-blocks/index.html) are published separately; raw session transcripts remain private. The raised-budget single-card retry completed with four clean deliveries in 75:23.

## Completed coding fleets

[Per-agent fleet outcomes](falling-blocks-fleet-outcomes-2026-10-18.csv) records all twelve agent attempts, including the missing first-attempt game. It is transcribed from the completed local campaign report, not a new session parse. Blank usage/timing fields were not available precisely in that report; they are not zero. Eleven games are linked by fleet and agent.

## Radiance engine campaign (21 October 2026)

[Dual-card grid](radiance-campaign-2026-10-21.csv): ten cells / 280 turns / zero reported errors, radiance 1.9.0, TP2, FP8 KV. n1–4 non-spec and MTP-4, n4 images, and R9 with a 13 GiB tier rather than 10 GiB. Historical Y/Z references use a different revision and BF16 KV. Read the [comparison contract](../../docs/RADIANCE-VS-VLLM.md) before treating the deltas as an engine ranking.

`decode_tokens_s` is total output / whole-cell wall; `tg_avg_tokens_s` is the mean valid per-turn generation estimate. The [dictionary](../../docs/DATA-DICTIONARY.md) gives formulas and missing-value rules. There is no matched raw-kernel PP series.

[Fleet CSV](radiance-falling-blocks-fleet-2026-10-21.csv): four agents, seeds 100–103, 3,600 s limit. **4/4 deliveries, 4/4 reported syntax passes, 2/4 clean deliveries**; agents 0–1 later time out; agents 2–3 exit cleanly. `cache_hit_pct` is the released fleet metric and is not interchangeable with the historical sweep’s zero-TTFT cache proxy. Released game paths point to `index.html`.

## Radiance single-card and capacity (22 October 2026)

[TP1 grid](radiance-single-card-2026-10-22.csv): four cells / 92 turns / zero reported errors, MTP-4, FP8 KV, four slots, 13 GiB tier. The measured boot pool is 404,608 tokens. n1–4 growth targets are 126,000 / 126,000 / 122,630 / 88,913; these are pre-turn stopping targets and actual final prompts can exceed them.

[Derived comparison](radiance-single-card-comparison-2026-10-22.csv) is rebuilt by `tools/build_comparison_data.py` from the original source exports. It includes actual maximum prompt depths and tier sizes. Historical GPU A uses **MTP-4**, not non-speculation. Whole-cell wall per timed turn normalizes the count only; different depths, run lengths and model representations remain.

[Capacity ladder](radiance-pool-ceiling-2026-10-22.csv) retains four measured GPU boot allocations, finished-conversation tier storage and marked projections. The six-slot 204,800-context row allocates 1,228,816 tokens; that is not a sustained six-agent performance test. A reported 165,075-token needle probe is discussed separately in the [capacity report](../../docs/RADIANCE-200K-CONTEXT-2026-10-22.md); its raw timing receipt is not part of this CSV.

<!-- NAVIGATION START -->

[Home](../../index.md) · [Compare](../../docs/RADIANCE-VS-VLLM.md) · [vllm-radiance](../../docs/VLLM-RADIANCE.md) · [radiance](../../docs/RADIANCE.md) · [Charts](../../docs/CHARTS.md) · [Stuff for nerds](../../docs/CODE-CORNER.md) · [Disclosure](../../docs/REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
