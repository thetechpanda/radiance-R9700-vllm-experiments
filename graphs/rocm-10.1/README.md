---
layout: default
title: "ROCm 10.1 graphs"
---

# ROCm 10.1 graphs

This folder contains the selected results only. Version assignment follows the reviewed [catalogue](../../data/telemetry-catalog.json); older traces use profile/date evidence, not per-run immutable image IDs.

- [ROCm base-image four-agent stress run](rocm-base-image-four-agent-stress-run.svg)
- [Retained historical agent workloads](historical-agent-workloads.svg)
- [Seven completed dual-card text-growth cells, 18 October 2026](dual-card-text-growth-2026-10-18.svg)

[What was excluded and why](../../docs/EXCLUDED-TESTS.md). Different workload/configuration histories are not a controlled ROCm A/B.

## Latest model and speculation campaign — 19 October

- [Initial eight-cell campaign](dual-r9700-spec-campaign-2026-10-19.svg)
- [All eight setups at 1–4 agents: wall time and effective ingest](dual-r9700-agent-count-sweep-2026-10-19.svg)
- [Vision-input increment within each target and lane](dual-r9700-vision-increment-2026-10-19.svg)
- [Mean TTFT by depth band: all 41 sweep cells](dual-r9700-depth-band-ttft-2026-10-19.svg)
- [Two completed shallow reproduction cells](dual-r9700-8k-repro-2026-10-19.svg)
- [Observed lane ordering at 16K versus deep load](dual-r9700-lane-transfer-16k-vs-126k.svg)
- [CSV hashes and chart provenance](dual-r9700-spec-chart-sources.json)

Read the [campaign limits](../../docs/DUAL-R9700-SPEC-CAMPAIGN.md): ≈15% repeat-spread floor, boot-pool variation, seed-sensitive vision histories, and effective ingest distinct from kernel prefill speed. These charts do not claim a new game-building fleet.

## Completed coding fleets

[Per-agent model time: dual and successful single-card retry](falling-blocks-completed-fleet-model-time-2026-10-18.svg) · [Play the eleven games](../../examples/rocm-10.1/falling-blocks/index.html). Budget, client context and reserve changed; this is not an isolated hardware speed comparison.

## Context-growth reports

- [Single-card GPU A context-growth summary](single-card-gpu-a-text-growth-2026-10-18.svg)
- [Single versus dual: mean TTFT](follow-up-single-vs-dual-mean-ttft-2026-10-18.svg)
- [Single versus dual: maximum TTFT](follow-up-single-vs-dual-maximum-ttft-2026-10-18.svg)
- [Single versus dual: request decode estimate](follow-up-single-vs-dual-request-decode-rate-2026-10-18.svg)
- [Historical ROCm 7.14/RAM16 versus ROCm 10.1/RAM10](single-card-rocm-7.14-ram16-vs-rocm-10.1-ram10.svg)

## Campaigns and counting

The seven-cell dual chart uses an 8 GiB CPU tier. The later GPU A/dual comparison uses 10 GiB; its shared GPU A rows are also shown in the single-card chart. These are not independent repeat samples. Charts use timed-turn exports; the [campaign report](../../docs/FINAL-REPORT-20261018.md) explains empty completions, pressure, fleet outcomes and comparison limits.

<!-- NAVIGATION START -->

[Home](../../index.md) · [Compare](../../docs/RADIANCE-VS-VLLM.md) · [vllm-radiance](../../docs/VLLM-RADIANCE.md) · [radiance](../../docs/RADIANCE.md) · [Charts](../../docs/CHARTS.md) · [Stuff for nerds](../../docs/CODE-CORNER.md) · [Disclosure](../../docs/REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
