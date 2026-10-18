---
layout: default
title: "Chart gallery"
---

# Chart gallery

This gallery includes selected results only; exploratory graphs are available separately in the [unchosen archive](../graphs/rocm-7.14/unchosen.md); their per-turn CSVs remain omitted. See [what was excluded and why](EXCLUDED-TESTS.md). Charts use descriptive experiment names and separate ROCm folders. Version assignment follows recorded build/runtime evidence; unknown versions stay separate. Different workloads and settings are not a controlled ROCm comparison. Prompt-credit traces are diagnostic, not validated prefill throughput.

## ROCm 10.1

[Graph folder](../graphs/rocm-10.1/README.md) · [Data folder](../data/rocm-10.1/README.md)

<details><summary>ROCm base-image four-agent stress run</summary>

The 17 October journal explicitly identifies this stress workload as ROCm 10.1.

Sustained four-agent load on the newer runtime stack. Compare with older-stack data only as an indicative comparison because configuration and depth caps differ; this is a stress qualification.

![ROCm base-image four-agent stress run](../graphs/rocm-10.1/rocm-base-image-four-agent-stress-run.svg)

[Derived CSV](../data/rocm-10.1/rocm-base-image-four-agent-stress-run.csv)

</details>

### Historical agent workloads

Exploratory cases within this recorded software profile; workloads and settings vary. These bars are not a controlled comparison.

![ROCm 10.1 historical agent workloads](../graphs/rocm-10.1/historical-agent-workloads.svg)

### Completed Falling Blocks fleets

![Per-agent model time for completed coding fleets](../graphs/rocm-10.1/falling-blocks-completed-fleet-model-time-2026-10-18.svg)

[Play all eleven games](../examples/rocm-10.1/falling-blocks/index.html) · [Per-agent outcomes CSV](../data/rocm-10.1/falling-blocks-fleet-outcomes-2026-10-18.csv). Both final fleets delivered four games; budgets and client settings differed. The failed first single-card attempt remains in the report.

### Single-card GPU A context-growth report

![ROCm 10.1 single-card GPU A mean and maximum TTFT](../graphs/rocm-10.1/single-card-gpu-a-text-growth-2026-10-18.svg)

### Follow-up: single versus dual cards

![Mean TTFT by agent count](../graphs/rocm-10.1/follow-up-single-vs-dual-mean-ttft-2026-10-18.svg)

![Maximum observed TTFT by agent count](../graphs/rocm-10.1/follow-up-single-vs-dual-maximum-ttft-2026-10-18.svg)

![Mean request decode estimate by agent count](../graphs/rocm-10.1/follow-up-single-vs-dual-request-decode-rate-2026-10-18.svg)

Short-output decode estimates are not fleet throughput or real-agent productivity. [Source data](../data/rocm-10.1/follow-up-single-vs-dual-text-growth-2026-10-18.csv).

### Historical single-card profile comparison

![Historical ROCm 7.14 RAM16 versus ROCm 10.1 RAM10](../graphs/rocm-10.1/single-card-rocm-7.14-ram16-vs-rocm-10.1-ram10.svg)

Different tier budgets, utilisation and image patches prevent an isolated ROCm-version conclusion.

### Dual-card text growth — 18 October 2026

![ROCm 10.1 dual-card text growth TTFT](../graphs/rocm-10.1/dual-card-text-growth-2026-10-18.svg)

[Completed case measurements](../data/rocm-10.1/dual-card-text-growth-2026-10-18.csv)

See the [seven completed dual-card text cases](REPEAT-CAMPAIGN.md). Eight GPU A/dual follow-up cells have completed; see the [latest results](../README.md#latest-rocm-101-results) and [README requirements and results](../README.md#best-recorded-single-card-setup-for-34-deep-context-agents) and [recorded configuration](../data/rocm-10.1/single-card-gpu-a-configuration.json). The [campaign report](FINAL-REPORT-20261018.md) records pressure telemetry and both first fleets; the single-card retry completed with all four agents delivering and exiting cleanly in 75:23.

## ROCm 7.14

[Graph folder](../graphs/rocm-7.14/README.md) · [Data folder](../data/rocm-7.14/README.md)

<details><summary>Single-card RAM16 tier, four agents at 131k target</summary>

ROCm 7.14 by recorded active profile and 6–8 October collection date; no immutable image ID captured per trace.

Qualification run for the 16 GiB shared-memory tier with four agents on one card. It is the key smooth-operation milestone; read error count, turn completion, TTFT by depth and memory pressure together.

![Single-card RAM16 tier, four agents at 131k target](../graphs/rocm-7.14/single-card-ram16-tier-four-agents-at-131k-target.svg)

[Derived CSV](../data/rocm-7.14/single-card-ram16-tier-four-agents-at-131k-target.csv)

</details>

<details><summary>Single-card RAM16 tier, three agents at 150k target</summary>

ROCm 7.14 by recorded active profile and 6–8 October collection date; no immutable image ID captured per trace.

Follow-up capacity point with fewer agents and deeper context. Compare sustained completion and tail behaviour with the four-agent milestone.

![Single-card RAM16 tier, three agents at 150k target](../graphs/rocm-7.14/single-card-ram16-tier-three-agents-at-150k-target.svg)

[Derived CSV](../data/rocm-7.14/single-card-ram16-tier-three-agents-at-150k-target.csv)

</details>

<details><summary>Host-memory trace for the RAM16 four-agent milestone</summary>

ROCm 7.14 by recorded active profile and 6–8 October collection date; no immutable image ID captured per trace.

Companion resource trace for the central four-agent single-card result. Check swap stays controlled while the shared-memory tier is active.

![Host-memory trace for the RAM16 four-agent milestone](../graphs/rocm-7.14/host-memory-trace-for-the-ram16-four-agent-milestone.svg)

[Derived CSV](../data/rocm-7.14/host-memory-trace-for-the-ram16-four-agent-milestone.csv)

</details>

<details><summary>Host-memory trace for the RAM16 three-agent follow-up</summary>

ROCm 7.14 by recorded active profile and 6–8 October collection date; no immutable image ID captured per trace.

Resource companion for the deeper three-agent test. Compare memory headroom and swap with the four-agent tier run.

![Host-memory trace for the RAM16 three-agent follow-up](../graphs/rocm-7.14/host-memory-trace-for-the-ram16-three-agent-follow-up.svg)

[Derived CSV](../data/rocm-7.14/host-memory-trace-for-the-ram16-three-agent-follow-up.csv)

</details>

### Historical agent workloads

Exploratory cases within this recorded software profile; workloads and settings vary. These bars are not a controlled comparison.

![ROCm 7.14 historical agent workloads](../graphs/rocm-7.14/historical-agent-workloads.svg)

### Single-card historical context-growth report

The short one/two-agent references and the three/four-agent RAM16 milestones have different histories/settings.

![ROCm 7.14 single-card historical mean and maximum TTFT](../graphs/rocm-7.14/single-card-text-growth-historical.svg)

## Version unverified or mixed

[Graph folder](../graphs/version-unverified/README.md) · [Data folder](../data/version-unverified/README.md)

<!-- NAVIGATION START -->

[Home](../index.md) · [Overview](../README.md) · [ROCm 10.1 results](FINAL-REPORT-20261018.md)
