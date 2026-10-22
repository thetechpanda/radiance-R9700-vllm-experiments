---
layout: default
title: "ROCm 7.14 vs ROCm 10.1 with vllm-radiance on R9700"
permalink: /
---

# ROCm 7.14 vs ROCm 10.1 with vllm-radiance on R9700

This research compares **ROCm 7.14 and ROCm 10.1 using the `vllm-radiance` repository** on Radeon AI PRO R9700 hardware, serving the Swift-1.5 Qwen3.8 27B INT4 checkpoint for coding agents.

A central workload asks how many concurrent agents can each sustain roughly **131k tokens of context on one R9700 plus host RAM**, with useful latency and successful completion. Single-card and dual-card configurations are reported separately. The ROCm 10.1 eight-cell matrix and all three fleet attempts are complete. Dual delivered four games in 30:10; the revised-budget single-card retry delivered four in 75:23. Configuration differences prevent an isolated ROCm-version conclusion.

## Start here

- [Research overview and findings](README.md)
- [Hardware and PCIe topology](docs/HARDWARE.md)
- [Podman operation and startup profiles](PODMAN.md)
- [Benchmark design and interpretation](docs/BENCHMARKS.md)
- [FP8 KV cache: memory savings and calibration from agent histories](docs/FP8-KV-CALIBRATION.md)
- [Scripts and radiance-top monitor](docs/SCRIPTS.md)

## Results

### Latest: dual-card model and speculation sweep — 19 October

The completed **41-cell / 1,160-turn** sweep recommends Swift-Quark RTN MXFP4 with speculation off for four-agent load. The measured profile uses TP=2, context 131070, four slots, BF16 KV and a 10 GiB CPU tier; it is a recommendation, not an applied service change. Speculative lanes are candidates at 1–2 agents; small gaps below the ≈15% repeat-spread floor remain unresolved.

[Campaign and limits](docs/DUAL-R9700-SPEC-CAMPAIGN.md) · [Sweep CSV: S1–Z5](data/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.csv) · [All current charts](docs/CHARTS.md)

![Eight setups across 1–4 agents](graphs/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.svg)

### Earlier: single-card capacity and coding fleets — 18 October

The measured ROCm 10.1 single-card 10 GiB-tier profile supported 1–2 deep agents with useful latency, then saturated at 3–4. The dual deployment completed the four-agent matrix and coding fleet with substantially better latency and completion.

- [18 October INT4 matrix and per-agent fleet report](docs/FINAL-REPORT-20261018.md)

- [ROCm 7.14 and ROCm 10.1 evidence](docs/ROCM-VERSIONS.md)
- [Chart gallery](docs/CHARTS.md)
- [ROCm 10.1 repeat-campaign ledger](docs/REPEAT-CAMPAIGN.md)
- [Research journal](docs/RESEARCH-JOURNAL.md)

The recorded campaigns use different settings. Read the configuration and provenance before comparing results; a configured 131k ceiling alone does not establish sustained simultaneous operation at that depth.

## Generated games

Play the [fifteen ROCm 10.1 games](examples/rocm-10.1/falling-blocks/index.html), grouped by fleet and attempt — the 21 October radiance-engine fleet is the newest set — or browse the historical collection. Explore the [Falling Blocks game gallery](examples/rocm-7.14/falling-blocks/index.html), the [real-agent task record](docs/REAL-AGENT-TEST.md) and the [artefact provenance](examples/rocm-7.14/falling-blocks/README.md).
