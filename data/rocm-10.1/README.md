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

## Campaigns and counting

The seven-cell dual export uses an **8 GiB** tier. The eight-cell GPU A/dual follow-up uses **10 GiB** and is a separate campaign. [The report](../../docs/FINAL-REPORT-20261018.md) contains serving settings, preemption counts and first coding-fleet outcomes.

The follow-up CSV counts timed turns: GPU A four-agent = 114; dual two-agent = 63. Including one empty completion in each gives 115/64 completed responses in the acceptance ledger. TTFT excludes those empty completions. Earlier review-notes JSON records the scope of the original export; the later report adds handover evidence without changing the exported data.

The [eleven ROCm 10.1 games](../../examples/rocm-10.1/falling-blocks/index.html) are published separately; raw session transcripts remain private. The raised-budget single-card retry completed with four clean deliveries in 75:23.

## Completed coding fleets

[Per-agent fleet outcomes](falling-blocks-fleet-outcomes-2026-10-18.csv) records all twelve agent attempts, including the missing first-attempt game. It is transcribed from the completed local campaign report, not a new session parse. Blank usage/timing fields were not available precisely in that report; they are not zero. Eleven games are linked by fleet and agent.

<!-- NAVIGATION START -->

[Home](../../index.md) · [Overview](../../README.md) · [ROCm 10.1 results](../../docs/FINAL-REPORT-20261018.md) · [Charts](../../docs/CHARTS.md)
