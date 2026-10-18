---
layout: default
title: "Derived data dictionary"
---

# Derived data dictionary

The [versioned data folders](../data/README.md) contain selected results. Legacy identifiers are metadata for traceability. Times are relative; memory is GiB. Counter-derived rates need a prior sample. Prompt-compute credit is diagnostic, not measured prefill throughput.

| Experiment | Version | CSV |
|---|---|---|
| Single-card RAM16 tier, four agents at 131k target | ROCm 7.14 | [CSV](../data/rocm-7.14/single-card-ram16-tier-four-agents-at-131k-target.csv) |
| Single-card RAM16 tier, three agents at 150k target | ROCm 7.14 | [CSV](../data/rocm-7.14/single-card-ram16-tier-three-agents-at-150k-target.csv) |
| ROCm base-image four-agent stress run | ROCm 10.1 | [CSV](../data/rocm-10.1/rocm-base-image-four-agent-stress-run.csv) |
| Host-memory trace for the RAM16 four-agent milestone | ROCm 7.14 | [CSV](../data/rocm-7.14/host-memory-trace-for-the-ram16-four-agent-milestone.csv) |
| Host-memory trace for the RAM16 three-agent follow-up | ROCm 7.14 | [CSV](../data/rocm-7.14/host-memory-trace-for-the-ram16-three-agent-follow-up.csv) |

[Excluded coverage](EXCLUDED-TESTS.md) is summary-only.

## ROCm 10.1 campaign summaries

| Dataset | Scope |
|---|---|
| [Earlier dual growth](../data/rocm-10.1/dual-card-text-growth-2026-10-18.csv) | Seven completed cells; TP=2, 8 GiB CPU tier |
| [GPU A growth](../data/rocm-10.1/single-card-gpu-a-text-growth-2026-10-18.csv) | Four completed single-card cells; TP=1, MTP=4, 10 GiB CPU tier |
| [Single/dual follow-up](../data/rocm-10.1/follow-up-single-vs-dual-text-growth-2026-10-18.csv) | Eight cells, including those same four GPU A rows; do not add both exports as independent samples |
| [Single-card configuration](../data/rocm-10.1/single-card-gpu-a-configuration.json) | Checkpoint and reviewed launch settings |

TTFT is in seconds; decode estimates are tokens/s for short responses, not aggregate fleet throughput. Counts in these CSVs are timed turns. The later acceptance report additionally counts one empty completion in GPU A n4 and one in dual n2. Reported case wall time and harness elapsed time use different boundaries. See [accounting and review limits](FINAL-REPORT-20261018.md#evidence-and-accounting).

## Coding-fleet outcome export

[Per-agent outcomes](../data/rocm-10.1/falling-blocks-fleet-outcomes-2026-10-18.csv) contains twelve rows across three fleet attempts, with eleven game files. `deliverables_complete` means all requested files existed; `clean_delivery` additionally requires exit 0. `fleet_wall_seconds` repeats the fleet wall time on each agent row and must not be summed. Output tokens are cumulative across requests; `max_output_tokens_per_request` is a per-request limit. Blank values are unavailable, not zero. Verification columns report target campaign checks; they do not claim fresh browser testing of these copies.

<!-- NAVIGATION START -->

[Home](../index.md) · [Overview](../README.md) · [ROCm 10.1 results](FINAL-REPORT-20261018.md) · [Charts](CHARTS.md)
