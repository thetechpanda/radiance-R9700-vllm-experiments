---
layout: default
title: "ROCm 7.14: unchosen graph archive"
---

# ROCm 7.14: unchosen graph archive

[Selected graphs](README.md) · [Main gallery](../../docs/CHARTS.md)

These **29 archived graphs** are available for inspection but are not selected for the main ROCm 7.14 versus ROCm 10.1 comparison. Each entry explains its exclusion. They cover tuning, boundary and instrumentation work; they must not be read as matched runtime comparisons.

Version attribution for older traces follows the recorded profile and collection date, rather than an immutable image ID captured with every run. Companion memory plots are not independent workload results.

<details markdown="1">
<summary markdown="0">Three-agent compaction chain at a 100k target</summary>

**Why unchosen:** A 100k three-agent compaction-chain sweep; it investigates compaction rather than the selected 131k concurrency/runtime comparison.

![Three-agent compaction chain at a 100k target](three-agent-compaction-chain-at-a-100k-target.svg)

[Open full-size SVG](three-agent-compaction-chain-at-a-100k-target.svg)

</details>

<details markdown="1">
<summary markdown="0">Three-agent compaction chain extended to 110k</summary>

**Why unchosen:** A 110k extension of the compaction sweep; different depth and history prevent a matched runtime comparison.

![Three-agent compaction chain extended to 110k](three-agent-compaction-chain-extended-to-110k.svg)

[Open full-size SVG](three-agent-compaction-chain-extended-to-110k.svg)

</details>

<details markdown="1">
<summary markdown="0">Three-agent compaction chain at 90k</summary>

**Why unchosen:** A 90k compaction reference; useful tuning context but redundant in the focused comparison.

![Three-agent compaction chain at 90k](three-agent-compaction-chain-at-90k.svg)

[Open full-size SVG](three-agent-compaction-chain-at-90k.svg)

</details>

<details markdown="1">
<summary markdown="0">Four-agent compaction at 64k</summary>

**Why unchosen:** A shallow 64k four-agent compaction case; outside the long-context target.

![Four-agent compaction at 64k](four-agent-compaction-at-64k.svg)

[Open full-size SVG](four-agent-compaction-at-64k.svg)

</details>

<details markdown="1">
<summary markdown="0">Four-agent compaction at 80k</summary>

**Why unchosen:** An 80k compaction-depth step; part of an exploratory sweep rather than a selected operating point.

![Four-agent compaction at 80k](four-agent-compaction-at-80k.svg)

[Open full-size SVG](four-agent-compaction-at-80k.svg)

</details>

<details markdown="1">
<summary markdown="0">Four-agent compaction at 86k</summary>

**Why unchosen:** An 86k compaction-depth step near a workload cliff; not a matched ROCm comparison.

![Four-agent compaction at 86k](four-agent-compaction-at-86k.svg)

[Open full-size SVG](four-agent-compaction-at-86k.svg)

</details>

<details markdown="1">
<summary markdown="0">Four-agent compaction at 90k</summary>

**Why unchosen:** A 90k four-agent compaction-storm reference; intentionally stresses prefix loss rather than the selected context-growth workload.

![Four-agent compaction at 90k](four-agent-compaction-at-90k.svg)

[Open full-size SVG](four-agent-compaction-at-90k.svg)

</details>

<details markdown="1">
<summary markdown="0">Clean rerun after a prefill-threshold change</summary>

**Why unchosen:** A prefill-threshold tuning rerun; changes scheduler configuration and is not a runtime-only comparison.

![Clean rerun after a prefill-threshold change](clean-rerun-after-a-prefill-threshold-change.svg)

[Open full-size SVG](clean-rerun-after-a-prefill-threshold-change.svg)

</details>

<details markdown="1">
<summary markdown="0">Foreign-traffic-contaminated threshold trial</summary>

**Why unchosen:** Unrelated traffic contaminated the measurement; its metrics cannot establish a treatment effect.

![Foreign-traffic-contaminated threshold trial](foreign-traffic-contaminated-threshold-trial.svg)

[Open full-size SVG](foreign-traffic-contaminated-threshold-trial.svg)

</details>

<details markdown="1">
<summary markdown="0">GPU-link upgrade comparison at the four-agent storm point</summary>

**Why unchosen:** The GPU-link path changed; link bandwidth and runtime effects cannot be isolated.

![GPU-link upgrade comparison at the four-agent storm point](gpu-link-upgrade-comparison-at-the-four-agent-storm-point.svg)

[Open full-size SVG](gpu-link-upgrade-comparison-at-the-four-agent-storm-point.svg)

</details>

<details markdown="1">
<summary markdown="0">Clean-storage four-agent storm trial</summary>

**Why unchosen:** A backing-storage experiment; storage-path effects are outside the selected runtime comparison.

![Clean-storage four-agent storm trial](clean-storage-four-agent-storm-trial.svg)

[Open full-size SVG](clean-storage-four-agent-storm-trial.svg)

</details>

<details markdown="1">
<summary markdown="0">Loop-backed fast-storage trial</summary>

**Why unchosen:** A loop-backed storage experiment; it tests a tier implementation rather than the retained deployment profiles.

![Loop-backed fast-storage trial](loop-backed-fast-storage-trial.svg)

[Open full-size SVG](loop-backed-fast-storage-trial.svg)

</details>

<details markdown="1">
<summary markdown="0">Eight-agent overflow / RAM-tier boundary</summary>

**Why unchosen:** An intentional eight-agent overflow boundary test; it exceeds the intended operating point.

![Eight-agent overflow / RAM-tier boundary](eight-agent-overflow-ram-tier-boundary.svg)

[Open full-size SVG](eight-agent-overflow-ram-tier-boundary.svg)

</details>

<details markdown="1">
<summary markdown="0">Reduced host-tier capacity at four-agent load</summary>

**Why unchosen:** A smaller host-tier experiment; its memory budget differs from the retained profiles.

![Reduced host-tier capacity at four-agent load](reduced-host-tier-capacity-at-four-agent-load.svg)

[Open full-size SVG](reduced-host-tier-capacity-at-four-agent-load.svg)

</details>

<details markdown="1">
<summary markdown="0">Guardrail / correctness trial at four agents</summary>

**Why unchosen:** A guardrail/correctness configuration probe; useful qualification history but not a matched performance case.

![Guardrail / correctness trial at four agents](guardrail-correctness-trial-at-four-agents.svg)

[Open full-size SVG](guardrail-correctness-trial-at-four-agents.svg)

</details>

<details markdown="1">
<summary markdown="0">Speculative-depth eight versus the four-agent baseline</summary>

**Why unchosen:** An eight-token speculation variant; draft-depth changes KV reservations and prevents an isolated runtime comparison.

![Speculative-depth eight versus the four-agent baseline](speculative-depth-eight-versus-the-four-agent-baseline.svg)

[Open full-size SVG](speculative-depth-eight-versus-the-four-agent-baseline.svg)

</details>

<details markdown="1">
<summary markdown="0">Six-agent capacity-bound run, incomplete</summary>

**Why unchosen:** The six-agent capacity-bound attempt was incomplete; it is not a valid completed performance result.

![Six-agent capacity-bound run, incomplete](six-agent-capacity-bound-run-incomplete.svg)

[Open full-size SVG](six-agent-capacity-bound-run-incomplete.svg)

</details>

<details markdown="1">
<summary markdown="0">Real coding-agent fleet, six agents</summary>

**Why unchosen:** An early six-agent real-agent harness trial produced no usable artefacts; it is not a successful task-completion result.

![Real coding-agent fleet, six agents](real-coding-agent-fleet-six-agents.svg)

[Open full-size SVG](real-coding-agent-fleet-six-agents.svg)

</details>

<details markdown="1">
<summary markdown="0">Single-agent real coding task</summary>

**Why unchosen:** A single-agent functional coding task; different workload and fleet size from the selected synthetic runtime comparison.

![Single-agent real coding task](single-agent-real-coding-task.svg)

[Open full-size SVG](single-agent-real-coding-task.svg)

</details>

<details markdown="1">
<summary markdown="0">Instrumentation sanity pass</summary>

**Why unchosen:** A short instrumentation sanity check; insufficient workload coverage for performance ranking.

![Instrumentation sanity pass](instrumentation-sanity-pass.svg)

[Open full-size SVG](instrumentation-sanity-pass.svg)

</details>

<details markdown="1">
<summary markdown="0">Second instrumentation sanity pass</summary>

**Why unchosen:** A second short instrumentation check; it validates metrics rather than serving capacity.

![Second instrumentation sanity pass](second-instrumentation-sanity-pass.svg)

[Open full-size SVG](second-instrumentation-sanity-pass.svg)

</details>

<details markdown="1">
<summary markdown="0">Compaction jitter and prefix-head preservation</summary>

**Why unchosen:** Compaction jitter and prefix-preservation settings changed; several workload/cache effects are mixed.

![Compaction jitter and prefix-head preservation](compaction-jitter-and-prefix-head-preservation.svg)

[Open full-size SVG](compaction-jitter-and-prefix-head-preservation.svg)

</details>

<details markdown="1">
<summary markdown="0">Runtime/JIT instrumentation sanity</summary>

**Why unchosen:** A runtime/JIT startup sanity check; it is not a sustained performance workload.

![Runtime/JIT instrumentation sanity](runtime-jit-instrumentation-sanity.svg)

[Open full-size SVG](runtime-jit-instrumentation-sanity.svg)

</details>

<details markdown="1">
<summary markdown="0">Second runtime/JIT sanity pass</summary>

**Why unchosen:** A short follow-up runtime/JIT sanity check; it is not a capacity or latency qualification.

![Second runtime/JIT sanity pass](second-runtime-jit-sanity-pass.svg)

[Open full-size SVG](second-runtime-jit-sanity-pass.svg)

</details>

<details markdown="1">
<summary markdown="0">Host-memory and storage telemetry during the link/storage campaign</summary>

**Why unchosen:** A resource companion to the omitted link/storage campaign; it is not an independent benchmark.

![Host-memory and storage telemetry during the link/storage campaign](host-memory-and-storage-telemetry-during-the-link-storage-campaign.svg)

[Open full-size SVG](host-memory-and-storage-telemetry-during-the-link-storage-campaign.svg)

</details>

<details markdown="1">
<summary markdown="0">Host-memory trace for overflow stress</summary>

**Why unchosen:** A resource companion to the intentional overflow test; it describes a boundary case.

![Host-memory trace for overflow stress](host-memory-trace-for-overflow-stress.svg)

[Open full-size SVG](host-memory-trace-for-overflow-stress.svg)

</details>

<details markdown="1">
<summary markdown="0">Host-memory trace for the reduced-tier comparison</summary>

**Why unchosen:** A resource companion to the reduced-tier tuning trial; its configuration is outside the selected comparison.

![Host-memory trace for the reduced-tier comparison](host-memory-trace-for-the-reduced-tier-comparison.svg)

[Open full-size SVG](host-memory-trace-for-the-reduced-tier-comparison.svg)

</details>

<details markdown="1">
<summary markdown="0">Host-memory trace for the guardrail trial</summary>

**Why unchosen:** A resource companion to the guardrail probe; it is not an independent runtime comparison.

![Host-memory trace for the guardrail trial](host-memory-trace-for-the-guardrail-trial.svg)

[Open full-size SVG](host-memory-trace-for-the-guardrail-trial.svg)

</details>

<details markdown="1">
<summary markdown="0">Host-memory trace for the six-agent real-agent campaign</summary>

**Why unchosen:** A resource companion to the early six-agent harness trial; its telemetry does not establish successful task completion.

![Host-memory trace for the six-agent real-agent campaign](host-memory-trace-for-the-six-agent-real-agent-campaign.svg)

[Open full-size SVG](host-memory-trace-for-the-six-agent-real-agent-campaign.svg)

</details>

No graph is shown for the empty speculative-depth companion recorder: it contained no usable samples. Its absence is not a successful test result.

<!-- NAVIGATION START -->

[Home](../../index.md) · [Compare](../../docs/RADIANCE-VS-VLLM.md) · [vllm-radiance](../../docs/VLLM-RADIANCE.md) · [radiance](../../docs/RADIANCE.md) · [Charts](../../docs/CHARTS.md) · [Stuff for nerds](../../docs/CODE-CORNER.md) · [Disclosure](../../docs/REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
