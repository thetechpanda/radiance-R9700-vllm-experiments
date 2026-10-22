---
layout: default
title: "ROCm 10.1 repeat campaign — 18 October 2026"
---

# ROCm 10.1 repeat campaign — 18 October 2026

This ledger distinguishes the earlier seven-cell dual-card campaign from eight completed follow-up cases. The earlier 150k four-agent case remains partial. Follow-up GPU A and dual-card text-growth cases at 1–4 agents have returned successful process status and zero reported client errors; the [campaign report](FINAL-REPORT-20261018.md) now records pressure telemetry, serving profiles and both first coding fleets. The raised-budget single-card retry completed with four clean deliveries in 75:23.

## Earlier campaign: recorded profile

The service used the local `vllm-radiance:rocm10` image: ROCm 10.1, PyTorch 2.12.0+rocm10.1 and vLLM 0.30.0. The workload used TP=2, eight configured MTP draft tokens, and an 8 GiB CPU KV tier. All cases were text-only synthetic agent workloads. These values describe this campaign; they do not describe every ROCm 10.1 service profile in the archive.

## Earlier campaign: completed cases

The campaign identifier is `20261018T005648Z`. The table reports mean and maximum time to first non-empty streamed content (TTFT) from the final valid attempt for each completed case.

| Target context | Agents | Mean TTFT | Maximum TTFT | Client errors | Status |
|---:|---:|---:|---:|---:|---|
| 126k | 1 | 5.004 s | 13.035 s | 0 | Complete |
| 126k | 2 | 6.721 s | 21.081 s | 0 | Complete |
| 126k | 3 | 9.039 s | 26.422 s | 0 | Complete |
| 126k | 4 | 10.988 s | 35.952 s | 0 | Complete |
| 150k | 1 | 5.768 s | 19.207 s | 0 | Complete |
| 150k | 2 | 7.470 s | 28.783 s | 0 | Complete |
| 150k | 3 | 9.220 s | 37.327 s | 0 | Complete |
| 150k | 4 | — | — | — | Partial; stopped before completion |

The initial instrumentation campaign (`20261018T005540Z`) ignored streamed reasoning deltas and produced invalid zero-TTFT measurements; exclude it from performance conclusions. Separately, an earlier three-agent attempt stopped after 85 timed turns when an overly strict empty-response guard aborted it. The corrected rerun is the completed result shown above; retain the failed attempt as provenance, not as a performance sample. The four-agent 150k case is incomplete and has no performance result. No other planned compaction, image, or Falling Blocks workload is represented by this table.

These are single observations per cell, with no statistical replication. Zero client errors means the completed final attempts returned without client errors; it does not establish a TTFT service-level objective or a complete reliability qualification. See [versioned profile context](ROCM-VERSIONS.md) for the older-stack comparison and its limits.

## Follow-up results available

The follow-up completed records cover GPU A alone and dual-card operation at 1–4 agents, with a 126k growth target. See the [README comparison](../HISTORICAL-OVERVIEW.md#latest-rocm-101-results), [eight-cell CSV](../data/rocm-10.1/follow-up-single-vs-dual-text-growth-2026-10-18.csv) and [review limits](../data/rocm-10.1/follow-up-single-vs-dual-notes.json).

At four agents, mean/maximum TTFT was 101.38/654.91 seconds on GPU A, versus 10.85/27.23 seconds on dual. GPU A recorded 12 KV preemptions in that cell; dual recorded none. Both reported zero client errors. Do not merge these cells with the earlier 8 GiB campaign.

## Focused follow-up plan

The completed synthetic scope is GPU A and dual, each at 1/2/3/4 agents. GPU B alone is excluded because it lacks a historical baseline. GPU A uses TP=1, MTP=4, 131,070 context and four slots; dual uses TP=2, MTP=8, 168,000 context and eight slots. Both have a 10 GiB ARC CPU tier. These different settings prevent a controlled TP scaling claim.

The three/four-agent single-card cases mark the pressure boundary. Keep the CPU tier at 10 GiB: 16 GiB previously made the host crawl, and another tier-size sweep is not planned.

## Coding fleets and remaining work

The first GPU A fleet produced three games: one clean delivery, two agents timed out after producing files, and one agent exhausted its request budget without delivering files. The dual fleet completed all four cleanly in 30:10. All seven games passed reported headless probes; full browser qualification is not established.

The single-card retry raises the per-request token budget to 65,536 and the per-agent wall cap to 5,400 seconds. It completed in 75:23 with all four agents delivering every file and exiting cleanly. All eleven games across the three attempts are published in the [ROCm 10.1 gallery](../examples/rocm-10.1/falling-blocks/index.html). The retry also corrected client context to 131,070 and raised compaction reserve to 67,584. See [per-agent outcomes and accounting](FINAL-REPORT-20261018.md). No further server inspection or test execution was performed during this documentation review.

<!-- NAVIGATION START -->

[Home](../index.md) · [Compare](RADIANCE-VS-VLLM.md) · [vllm-radiance](VLLM-RADIANCE.md) · [radiance](RADIANCE.md) · [Charts](CHARTS.md) · [Stuff for nerds](CODE-CORNER.md) · [Disclosure](REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
