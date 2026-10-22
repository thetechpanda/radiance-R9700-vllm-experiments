---
layout: default
title: "Real-agent Falling Blocks test"
---

# Real-agent Falling Blocks test

This was an end-to-end coding task on the research server using real tool-using coding agents. It complements the synthetic request cases in the [benchmark index](RUN-INDEX.md); it is not one of the 48 rows in the derived case-summary CSV.

## What the agents did

Each agent received a Falling Blocks rules reference and a seeded set of variant requirements. The task was staged: write a rules document for the assigned variant, produce an implementation plan, then build a playable single-file HTML game. This drove an initial prompt prefill followed by multiple tool-using generation phases with growing context. The test exercised agent orchestration, tool calls, long-running request behaviour, context growth, and completion of a concrete coding task.

## Historical outcomes

| Run | Workload | Recorded outcome | Evidence limits |
|---|---|---|---|
| Single-agent task | One agent built its rules, plan, and Falling Blocks game over 46 turns and 22 minutes. Context grew from about 10.7k to 77.7k tokens. | The agent completed the task and reported 52 headless game-logic tests passing. | The test report came from the agent; the test suite was not independently rerun for this release. Private task files are not redistributed; this is separate from the recovered four-agent games linked below. |
| Four-agent task | Four real coding agents worked on seeded Falling Blocks variants in a historical server run. | All four agents finished and produced HTML game files between 21,236 and 24,737 bytes each. | The retained files do not verify the runtime profile, and the collected record does not provide a matching cleaned per-agent metrics table or chart. This is evidence of task completion, not versioned or controlled throughput evidence. |

The single-agent run's output sizes were about 12 kB for the rules, 9.5 kB for the plan, and 21 kB for the game. The four-agent run is distinct from earlier harness attempts, which produced no usable game outputs before the reasoning and token settings were corrected.

## ROCm 10.1 fleets — 18 October 2026

| Profile | Agent | Deliverables | Exit / outcome |
|---|---:|---|---|
| GPU A, first attempt | 0 | None | Exit 0 after a thinking-only, budget-limited response; failed delivery |
| GPU A, first attempt | 1 | Rules, plan, game | Exit 0; delivered |
| GPU A, first attempt | 2 | Rules, plan, game | Exit 124; timed out at 60 minutes |
| GPU A, first attempt | 3 | Rules, plan, game | Exit 124; timed out at 60 minutes |
| Dual | 0–3, each | Rules, plan, game | All four exit 0; fleet wall 30:10 |
| GPU A, revised-budget retry | 0–3, each | Rules, plan, game | All four exit 0; fleet wall 75:23 |

All eleven produced games passed reported syntax and mocked-DOM probes, including line clearing. This is narrower than full browser qualification. The first GPU A fleet failed overall despite three produced games; exit status alone missed agent 0's absent deliverables. The raised-budget GPU A retry completed: all four agents delivered and exited cleanly in 75:23.

The [campaign report](FINAL-REPORT-20261018.md#falling-blocks-fleets--real-coding-agents) includes per-agent turns, usage and verification scope. All eleven produced games are available in the [ROCm 10.1 gallery](../examples/rocm-10.1/falling-blocks/index.html). Do not combine these fleets with the historical games below or attribute model competence to GPU count.

## Tools developed for the real-agent workload

| Tool | Role in the experiment | Release status |
|---|---|---|
| [`falling_blocks_prompt.py`](../scripts/falling_blocks_prompt.py) | Produces a seeded Falling Blocks task prompt. | Rewritten script included. |
| [`run_falling_blocks_agent.sh`](../scripts/run_falling_blocks_agent.sh) | Runs one task in a configured Pi coding-agent container and saves session events. | Rewritten script included. |
| [`run_falling_blocks_fleet.sh`](../scripts/run_falling_blocks_fleet.sh) | Checks server health and launches multiple agents in parallel. | Rewritten script included. |
| [`parse_falling_blocks_events.py`](../scripts/parse_falling_blocks_events.py) | Converts session usage/timing metadata into CSV without printing message content. | Rewritten script included. |
| [`radiance-top`](../scripts/radiance-top) | Live terminal view of server counters and GPU telemetry, with aggregate/per-card display and plain output. | Monitor included. |
| Synthetic benchmark client | Sends repeatable synthetic tool-result conversations to an OpenAI-compatible endpoint. | Rewritten [`agent_bench.py`](../scripts/agent_bench.py) is included; it is not the real-agent Falling Blocks harness. |

The [game gallery](../examples/rocm-7.14/falling-blocks/index.html) now includes the four recovered HTML outputs from the completed four-agent task, with [provenance and hashes](../examples/rocm-7.14/falling-blocks/README.md). These game files passed a privacy/network-reference review and were subsequently renamed to Falling Blocks; no task transcripts are included. The agent scripts are rewritten for release. The [research journal](RESEARCH-JOURNAL.md) and [chart gallery](CHARTS.md) provide context for related synthetic and telemetry runs.

<!-- NAVIGATION START -->

[Home](../index.md) · [Compare](RADIANCE-VS-VLLM.md) · [vllm-radiance](VLLM-RADIANCE.md) · [radiance](RADIANCE.md) · [Charts](CHARTS.md) · [Stuff for nerds](CODE-CORNER.md) · [Disclosure](REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
