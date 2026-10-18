---
layout: default
title: "Research journal"
---

# Research journal

This chronology is a fresh summary of the archived experiment notes, metrics, and handoffs. The research target was **Qwen3.8 27B**, primarily the hybrid `ukisai/Swift-1.5-Qwen3.8-27b-INT4` checkpoint. Dates identify phases, not a claim that every row is directly comparable. Experiment IDs point to the source journal's labels; the release data uses descriptive filenames in separate ROCm version folders; legacy IDs remain catalogue metadata. See the [Hugging Face model inventory](MODELS.md) for other checkpoints evaluated in the broader Radiance work.

## 1. Establish a one-card baseline

The project started with one 32 GB Radeon AI PRO R9700 serving the hybrid Qwen3.8 27B checkpoint `ukisai/Swift-1.5-Qwen3.8-27b-INT4` through Radiance/vLLM. Long-running agents grow their histories by appending tool results. The tests therefore measured repeated streaming turns at increasing context depth, not just prompt throughput on a single request.

Early connectivity through OCuLink limited CPU/GPU transfers. After a direct Gen5 rewire, measured bandwidth improved substantially. Benchmark work then separated several effects that had initially been blended together: prefill queueing from context depth, cache hits from recomputation, and the cost of loading cached KV from host RAM or disk. Tests also explored prompt chunk sizes, speculative token counts, prefix reuse, storage paths, and different concurrency levels.

A key workload correction was to stop sending every agent the same large tool-result chunk. Mixed-size tool results with desynchronised agents better represented interactive coding work. Under that workload, deep turns could remain responsive while shallow high-turn-rate phases still produced queues. The record repeatedly warns that concurrency and request cadence can matter more than nominal context length.

## 2. Reach the RAM16 single-card milestone

The RAM-only 16 GiB shared-memory tier was evaluated in E21 and E22 after larger or filesystem-backed tiers showed memory/stall tradeoffs. E21 exercised four agents with a 131k live cap: 155 turns completed with zero request errors, average TTFT was 16.88 seconds, and the maximum was 53.85 seconds. Three turns crossed the 45-second threshold, so the recorded verdict was usable on average, not a strict tail-latency pass. E22 exercised three agents beyond 150k cumulative context: 124 turns completed with zero request errors; recorded average TTFT was 13.34 seconds.

The result demonstrated that 16 GiB of host shared memory could carry a deep four-agent fleet on the one-card system. It did not mean every request was smooth. The GPU KV pool, traffic pattern, cache churn, and tail latency remained operational constraints. Compare [derived E21 telemetry](../graphs/rocm-7.14/single-card-ram16-tier-four-agents-at-131k-target.svg), [derived E22 telemetry](../graphs/rocm-7.14/single-card-ram16-tier-three-agents-at-150k-target.svg), and the per-run summary chart.

![Four-agent RAM16 single-card telemetry](../graphs/rocm-7.14/single-card-ram16-tier-four-agents-at-131k-target.svg)

![Three-agent RAM16 deeper-context telemetry](../graphs/rocm-7.14/single-card-ram16-tier-three-agents-at-150k-target.svg)

## 3. Measure realistic compaction and tier behaviour

Follow-up compaction runs showed a U-shaped response curve for four agents. A low cap increased turn rate and repeated compaction; high caps increased KV eviction/re-prefill cost. Around 80k per agent was the best observed compromise in that campaign, while 86–90k entered a churn-heavy region. Three-agent runs sustained higher caps with less contention. These are workload-specific results and are summarised by the `CMP` cases in derived telemetry.

Storage/tier tests distinguished RAM-only from filesystem spill. Disk-backed cache could retain more data, but promotion added latency; RAM tier size also had to be balanced against host memory available for model workers and page cache. Several CSVs capture imperfect, sanity, or tainted runs. Their transformed series remain available but should be interpreted with the source journal's classifications.

## 4. Add the second GPU and solve a different problem

By 2026-10-16 the system used two R9700 cards with tensor parallel size 2. GPU KV was reported at 824,254 tokens, up from 167,553 tokens in the single-card state. The second card used a slower x4 path, so the first dual-card state was marked unbenchmarked and asymmetric-link-limited. The source notes explicitly call for a controlled TP=1 versus TP=2 comparison; do not infer a universal speedup from GPU count.

The first two-card service configuration carried too much CPU KV spill for a host with only about 30 GiB RAM. A 20 GiB tier plus filesystem tier caused active swapping. A 16 GiB RAM-only revision reduced swapping but still left little memory margin. Reducing the tier to 4 GiB and removing filesystem spill restored more available memory and stopped active swap. Attempting to reclaim parked swap while the engine was loaded caused an out-of-memory restart; that is a documented failed recovery experiment, not a recommended operation.

TP=2 also required P2P reduction work. The archived build qualified a custom exact two-rank kernel and retained size/geometry patch hooks; a compressed all-reduce path trades numerical exactness for less traffic on selected large messages. The slower card link remained a caveat even with the custom collective.

## 5. ROCm 10.1 results and version limits

On 2026-10-17 a separately built ROCm 10.1 image passed the recorded image/runtime checks and served the two-card setup. A four-agent stress run reached about 126k context and completed 116 turns with zero request errors in 763 seconds. Average TTFT was 11.36 seconds; the archived journal reported about 13.6 generated tokens/s engine-wide and approximately three active requests on average. The nearest ROCm 7.14 case used four agents at a 100k target, completed 36 turns and recorded 26.74 seconds mean TTFT. Since target depth and workload conditions differed, this is an indicative observation rather than a controlled ROCm comparison.

On 2026-10-18, seven cells in a separate ROCm 10.1 text campaign completed: 126k targets at 1–4 agents and 150k targets at 1–3 agents. The final valid attempts had zero client errors. The 150k four-agent case was stopped before completion; other planned cases were not run. See the [full ROCm profile comparison](ROCM-VERSIONS.md), the [repeat-campaign ledger](REPEAT-CAMPAIGN.md), and the [derived earlier stress trace](../graphs/rocm-10.1/rocm-base-image-four-agent-stress-run.svg).

![ROCm 10.1 four-agent stress telemetry](../graphs/rocm-10.1/rocm-base-image-four-agent-stress-run.svg)

## 6. Validate with a real coding task

The workload progressed from generated request traffic to a real, multi-stage coding task: build Falling Blocks variants using tools. A historical four-agent task produced four HTML game outputs; the retained outputs do not independently verify the runtime profile. A separate one-agent run completed 46 turns in 22 minutes, grew context from about 10.7k to 77.7k tokens, and produced a rules document, implementation plan, and game. The agent reported 52 headless logic tests passing; this release did not independently rerun that test suite. The experiment and its limits are detailed in the [real-agent Falling Blocks test record](REAL-AGENT-TEST.md).

## Interpretation rules

- The single-card RAM16 result and the later dual-card 4 GiB service are different configurations.
- An error-free run can still have tail-latency breaches. Report the distribution or stated threshold alongside averages.
- Warm/cold cache, number of agents, context cap, image, speculative settings, and traffic generator version affect comparability.
- Some recorder revisions changed field meaning. Release time series normalise units and counters, but the source journal remains the key for interpreting experiment design and failed/tainted runs.
- This journal uses no raw conversation content, source command strings, host alias, private address, or user filesystem path.

## 7. Complete the focused ROCm 10.1 comparison

The later GPU A/dual 1–4-agent matrix completed. Single-card 10 GiB-tier latency became unsuitable at three/four deep agents; dual avoided that collapse under its different profile. The first coding fleets delivered three games on GPU A (only one clean delivery) and four on dual (all clean exits). The raised-budget single-card retry completed with four clean deliveries in 75:23. Read the [campaign report](FINAL-REPORT-20261018.md) for per-case counts, tails, preemptions, swap and verification limits. This adds current evidence without rewriting earlier tuning decisions as current recommendations.

<!-- NAVIGATION START -->

[Home](../index.md) · [Overview](../README.md) · [ROCm 10.1 results](FINAL-REPORT-20261018.md) · [Charts](CHARTS.md)
