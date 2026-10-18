---
layout: default
title: "Run index"
---

# Run index

Only selected results are published. [Excluded tests](EXCLUDED-TESTS.md) summarises other coverage without redistributing its performance tables; restored exploratory SVGs are retained in the secondary graph archive.

## Retained telemetry

| Experiment | Version and provenance | CSV |
|---|---|---|
| Single-card RAM16 tier, four agents at 131k target | rocm-7.14: ROCm 7.14 by recorded active profile and 6–8 October collection date; no immutable image ID captured per trace. | [CSV](../data/rocm-7.14/single-card-ram16-tier-four-agents-at-131k-target.csv) |
| Single-card RAM16 tier, three agents at 150k target | rocm-7.14: ROCm 7.14 by recorded active profile and 6–8 October collection date; no immutable image ID captured per trace. | [CSV](../data/rocm-7.14/single-card-ram16-tier-three-agents-at-150k-target.csv) |
| ROCm base-image four-agent stress run | rocm-10.1: The 17 October journal explicitly identifies this stress workload as ROCm 10.1. | [CSV](../data/rocm-10.1/rocm-base-image-four-agent-stress-run.csv) |
| Host-memory trace for the RAM16 four-agent milestone | rocm-7.14: ROCm 7.14 by recorded active profile and 6–8 October collection date; no immutable image ID captured per trace. | [CSV](../data/rocm-7.14/host-memory-trace-for-the-ram16-four-agent-milestone.csv) |
| Host-memory trace for the RAM16 three-agent follow-up | rocm-7.14: ROCm 7.14 by recorded active profile and 6–8 October collection date; no immutable image ID captured per trace. | [CSV](../data/rocm-7.14/host-memory-trace-for-the-ram16-three-agent-follow-up.csv) |

## Retained benchmark cases

| Experiment | Version | Agents | Completed turns | Mean TTFT |
|---|---|---:|---:|---:|
| Single-card RAM16, four agents | rocm-7.14 | 4 | 155 | 16.88 s |
| Single-card RAM16, three agents | rocm-7.14 | 3 | 124 | 13.34 s |
| Single-card one-agent context-growth reference | rocm-7.14 | 1 | 10 | 12.36 s |
| Single-card two-agent context-growth reference | rocm-7.14 | 2 | 20 | 17.54 s |
| Older-stack four-agent 100k reference; unmatched comparison | rocm-7.14 | 4 | 36 | 26.74 s |
| ROCm 10.1 four-agent stress reference | rocm-10.1 | 4 | 116 | 11.36 s |

These are representative operating points, not a matched scaling curve. Workload depth/history and settings differ. The older/newer stress pair is not a controlled ROCm A/B. See the [version evidence](ROCM-VERSIONS.md) and [seven completed ROCm 10.1 repeat cells](REPEAT-CAMPAIGN.md).

Prompt-credit rates are not measured prefill throughput. Companion resource traces are not independent benchmark runs.

## ROCm 10.1 follow-up campaigns

| Campaign | Completed synthetic cells | Profile / scope |
|---|---:|---|
| Earlier dual-card growth | 7 | TP=2, MTP=8, 8 GiB CPU tier; four-agent 150k cell partial |
| GPU A / dual comparison | 8 | Each profile at 1–4 agents; 10 GiB CPU tier; GPU A MTP=4, dual MTP=8 |

The [latest campaign report](FINAL-REPORT-20261018.md) includes TTFT tails, preemptions and the first coding fleets. The [eight-cell CSV](../data/rocm-10.1/follow-up-single-vs-dual-text-growth-2026-10-18.csv) already includes all four rows in the separate GPU A export; these are not independent additional cases. The report counts completed empty responses separately from timed turns. The single-card retry completed with all four agents delivering and exiting cleanly in 75:23.

<!-- NAVIGATION START -->

[Home](../index.md) · [Overview](../README.md) · [ROCm 10.1 results](FINAL-REPORT-20261018.md) · [Charts](CHARTS.md)
