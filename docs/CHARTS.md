---
layout: default
title: "Chart gallery"
---

# Chart gallery

This gallery includes selected results only; exploratory graphs are available separately in the [unchosen archive](../graphs/rocm-7.14/unchosen.md); their per-turn CSVs remain omitted. See [what was excluded and why](EXCLUDED-TESTS.md). Charts use descriptive experiment names and separate ROCm folders. Version assignment follows recorded build/runtime evidence; unknown versions stay separate. Different workloads and settings are not a controlled ROCm comparison. Prompt-credit traces are diagnostic, not validated prefill throughput.

## ROCm 10.1

[Graph folder](../graphs/rocm-10.1/README.md) · [Data folder](../data/rocm-10.1/README.md)

### Dual R9700 model & spec-decode campaign — 19 October 2026

![Spec-decode campaign cells](../graphs/rocm-10.1/dual-r9700-spec-campaign-2026-10-19.svg)

![Agent-count sweep: wall time and prompt ingest by setup](../graphs/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.svg)

![Within-lane vision increments](../graphs/rocm-10.1/dual-r9700-vision-increment-2026-10-19.svg)

![Mean TTFT by depth band](../graphs/rocm-10.1/dual-r9700-depth-band-ttft-2026-10-19.svg)

![16K fast-lane repro cells](../graphs/rocm-10.1/dual-r9700-8k-repro-2026-10-19.svg)

![Lane transfer: 16K vs 126k](../graphs/rocm-10.1/dual-r9700-lane-transfer-16k-vs-126k.svg)

Eight setups, 41 sweep cells, 1,160 turns, zero client errors. The PNG-input cells are synthetic, separate from the game-building fleets. Recommendation: Swift-Quark non-spec at four agents; keep the ≈15% spread floor, boot-pool variation and vision seed sensitivity. Effective ingest is not kernel prefill. The shallow ordering is observational, with multiple settings changed. [Campaign write-up](DUAL-R9700-SPEC-CAMPAIGN.md) · [Campaign CSV](../data/rocm-10.1/dual-r9700-spec-campaign-2026-10-19.csv) · [Sweep CSV](../data/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.csv) · [16K repro CSV](../data/rocm-10.1/dual-r9700-8k-repro-2026-10-19.csv).

<details><summary>ROCm base-image four-agent stress run</summary>

The 17 October journal explicitly identifies this stress workload as ROCm 10.1.

Sustained four-agent load on the newer runtime stack. Compare with older-stack data only as an indicative comparison because configuration and depth caps differ; this is a stress qualification.

![ROCm base-image four-agent stress run](../graphs/rocm-10.1/rocm-base-image-four-agent-stress-run.svg)

[Derived CSV](../data/rocm-10.1/rocm-base-image-four-agent-stress-run.csv)

</details>

<details><summary>Radiance 1.9.0 campaign: wall seconds vs vllm-radiance twins, 21 October 2026</summary>

radiance 1.9.0 at a pinned image digest, TP2, fp8 KV, M2 converted checkpoint (awq-int4-rad); collected 21 October 2026 on the dual R9700 host. Old-engine arms are the published 19 October campaign numbers for the same checkpoint, not a re-run.

Grouped wall seconds for the recovered byte-identical agent harness under the radiance engine (non-spec and MTP-4) against the vllm-radiance Y/Z arms on the same checkpoint, n=1..4. MTP-4 is the winning lane: it beats the old MTP arm at every agent count and the old non-spec arm at n=1-3; the non-spec lane trails the old engine inside seed noise. Read with the campaign write-up; baseline re-validation on the old engine was not run.

![Radiance 1.9.0 campaign: wall seconds vs vllm-radiance twins, 21 October 2026](../graphs/rocm-10.1/radiance-campaign-2026-10-21.svg)

[Derived CSV](../data/rocm-10.1/radiance-campaign-2026-10-21.csv)

</details>

<details><summary>Single-card serving: per-turn price and TTFT, old engine vs radiance (22 October 2026)</summary>

radiance 1.9.0 pinned digest, M2 checkpoint (awq-int4-rad); TP1 grid 22 October, TP2 grid 21 October 2026, same recovered client; old-engine rows are the published 18 October follow-up campaign, not a re-run.

Two-panel comparison of single-card agent serving: seconds per turn and mean TTFT at n=1..4 for vllm-radiance single-card (27-turn family, non-spec), radiance TP1 MTP-4 and radiance TP2 MTP-4. The old engine's per-turn price explodes 2.7x with load (12.59 to 34.65) and its TTFT collapses at n=3-4 (71.46/101.38 mean, 654.91 max, depth held via preemption); radiance stays flat (9.68 to 9.06 s/turn, TTFT max 22.02) at an honest 88,913-token cap on n=4. Turn families differ; s/turn normalizes turns, not lane.

![Single-card serving: per-turn price and TTFT, old engine vs radiance (22 October 2026)](../graphs/rocm-10.1/radiance-single-card-comparison-2026-10-22.svg)

[Derived CSV](../data/rocm-10.1/radiance-single-card-comparison-2026-10-22.csv)

</details>

<details><summary>KV pool ceiling ladder: measured boots and marked projections (22 October 2026)</summary>

Boot prints of radiance 1.9.0 at the pinned digest on the dual R9700 host, 21-22 October 2026; projection rows are elastic GiB over measured KV density (18.2 KiB/token/card), marked dashed.

Horizontal bars of KV pool tokens per engine configuration: four measured boot prints (TP1 4-slot 404,608; TP2 4-slot 524,304; TP2 6-slot 131k 786,448; TP2 6-slot 200k 1,228,816, the current default) plus two dashed projections (elastic ceiling ~1,284,500 at ~9.8 sessions; TTM tier max ~471,400) and the host tier measured at 400,912. The engine rule pool = min(what fits, slots x context) explains why 1-card and 2-card pools looked similar at 4 slots: both targeted 4x131k; the cards were never the 524k limit.

![KV pool ceiling ladder: measured boots and marked projections (22 October 2026)](../graphs/rocm-10.1/radiance-pool-ceiling-2026-10-22.svg)

[Derived CSV](../data/rocm-10.1/radiance-pool-ceiling-2026-10-22.csv)

</details>

### Historical agent workloads

Exploratory cases within this recorded software profile; workloads and settings vary. These bars are not a controlled comparison.

![ROCm 10.1 historical agent workloads](../graphs/rocm-10.1/historical-agent-workloads.svg)

### Completed Falling Blocks fleets

![Per-agent model time for completed coding fleets](../graphs/rocm-10.1/falling-blocks-completed-fleet-model-time-2026-10-18.svg)

[Play all fifteen games](../examples/rocm-10.1/falling-blocks/index.html) · [Per-agent outcomes CSV](../data/rocm-10.1/falling-blocks-fleet-outcomes-2026-10-18.csv). Both final fleets delivered four games; budgets and client settings differed. The failed first single-card attempt remains in the report.

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

[Home](../index.md) · [Overview](../README.md) · [Latest campaign](RADIANCE-CAMPAIGN-2026-10-21.md)
