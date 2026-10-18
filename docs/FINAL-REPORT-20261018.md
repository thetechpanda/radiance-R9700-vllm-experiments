---
layout: default
title: "ROCm 10.1 matrix and Falling Blocks fleets — final report, 18 October 2026"
---

# ROCm 10.1 matrix and Falling Blocks fleets — final report, 18 October 2026

Campaign `20261018T025319Z`, as recorded in the local research handover. All fleets are complete, including the GPU A retry (successful). Scope: the eight-cell synthetic agent matrix on the service-managed single-GPU-A and dual-card deployments under ROCm 10.1, comparison against the 7.14-era evidence, and the real coding-agent Falling Blocks fleets on both deployments. GPU B alone is out of scope: every historical single-card baseline ran on card A at PCIe 4.0 ×8; the ×4 second card has no baseline.

## Deployment profiles

| Profile | Service | TP | Max context | Slots | Speculative | CPU KV tier |
|---|---|---:|---:|---:|---:|---:|
| Single GPU A | `radiance-vllm.service` | 1 | 131070 | 4 | MTP 4 | 10 GiB ARC |
| Dual card | launcher `radiance-vllm-start-dual` | 2 | 168000 | 8 | MTP 8 | 10 GiB ARC |

Both used the local `vllm-radiance:rocm10` image (ROCm 10.1, PyTorch 2.12.0+rocm10.1, vLLM 0.30.0), model `ukisai/Swift-1.5-Qwen3.8-27b-INT4`, fp8 KV, gpu-mem-util 0.98. Every fleet launch captured a sanitised runtime manifest (profile, command, GPU UUID); the dual fleet manifest records `--tensor-parallel-size 2`.

## Synthetic matrix — 8/8 accepted

The accepted case records report zero client errors and zero allocation failures. Counts below include completed empty responses; TTFT statistics exclude responses with no first token. One workload case at a time under the campaign lock, transient `systemd-run` jobs, acceptance gate on exit status, usage/finish accounting, artefact presence and context growth.

| Profile | Agents | Wall | Turns | Mean TTFT | Max TTFT | Preemptions |
|---|---:|---:|---:|---:|---:|---:|
| GPU A | 1 | 341.1 s | 27 | 7.456 s | 18.782 s | 0 |
| GPU A | 2 | 615.1 s | 63 | 11.922 s | 40.644 s | 0 |
| GPU A | 3 | 2829.2 s | 94 | 71.464 s | 456.188 s | 7 |
| GPU A | 4 | 3951.3 s | 115 | 101.384 s | 654.907 s | 12 |
| Dual | 1 | 292.1 s | 28 | 5.191 s | 12.660 s | 0 |
| Dual | 2 | 428.1 s | 64 | 6.362 s | 22.339 s | 0 |
| Dual | 3 | 644.1 s | 94 | 7.739 s | 25.563 s | 0 |
| Dual | 4 | 804.1 s | 118 | 10.853 s | 27.235 s | 0 |

The single-card profile collapses at depth: 19 KV preemptions (cache pressure at 100%), tail latency in the 5–11 minute band. The dual profile served the same agent counts with zero preemptions and a 27 s worst TTFT at four agents. Host swap grew 0.37→1.07 GiB across the dual phase while MemAvailable stayed near 7.3 GiB — reported as a trend, not a stop condition. Two cells (GPU A n4, dual n2) each recorded one null-TTFT empty response, counted separately in the ledger.

## Comparison with the 7.14-era evidence

The legacy ledger spans both runtime eras: CASE-37 belongs to ROCm 10.1; it must not be counted as ROCm 7.14. Version assignment follows the reviewed catalogues, not the directory where raw records were originally collected. The retained historical single-card references are shown below.

| Agents | ROCm 7.14 reference | Timed turns | Mean / maximum TTFT | ROCm 10.1 GPU A mean / maximum TTFT |
|---:|---|---:|---:|---:|
| 1 | Short 126k-target reference | 10 | 12.36 / 21.67 s | 7.456 / 18.782 s |
| 2 | Short 126k-target reference | 20 | 17.54 / 44.11 s | 11.922 / 40.644 s |
| 3 | RAM16 milestone | 124 | 13.34 / 58.28 s | 71.464 / 456.188 s |
| 4 | RAM16 milestone | 155 | 16.88 / 53.85 s | 101.384 / 654.907 s |

**These are unmatched deployment comparisons.** The historical 1–2-agent references stopped around 118–121k observed context; the RAM16 milestones reached roughly 126k. Tier budget, utilisation, patch level and workload history differ from ROCm 10.1. The newer profile uses 10 GiB ARC and utilisation 0.98; the RAM16 profile used 16 GiB and 0.995. TTFT accounting also differs. Each cell is a single observation.

The smaller CPU tier is a plausible contributor to pressure, not an isolated causal finding. A 16 GiB tier previously caused severe host slowdown: **keep the current tier at 10 GiB; no 16 GiB rerun is planned.** Four agents is the final single-card boundary case. The dual deployment is the strongest measured current option for 3–4 deep agents, with the profile differences above retained explicitly.

## Falling Blocks fleets — real coding agents

Four concurrent coding agents (seeds 100–103) per fleet, each building a Falling Blocks game (`falling-blocks.html`, `rules.md`, `plan.md`) against the served model inside isolated `pi-bench:4` containers, 3600 s per agent (5400 s in the retry).

**Fleet GPU A — failed case** (unit exit 1, wall 60:00):

| Agent | Seed | Turns | Exit | Artefacts | Verified quality |
|---|---|---:|---|---|---|
| 0 | 100 | 1 | 0 | none | — |
| 1 | 101 | 28 | 0 | all three | PASS (all checks) |
| 2 | 102 | 36 | 124 (timeout) | all three | PASS (all checks) |
| 3 | 103 | 32 | 124 (timeout) | all three | PASS (all checks) |

Agent 0 did not deliver: a single assistant message, thinking-only, stopped at exactly 32,768 output tokens (the client per-request cap) with zero tool calls; the harness settled the `length`-terminated turn as a completed session — a silent zero-artefact "success". Agents 2–3 finished all artefacts by ~42 minutes and were killed at the cap while play-testing beyond the required deliverables.

**Fleet dual — success** (unit exit 0, wall 30:10): all four agents exit 0, all artefacts, no container leaks; seed-100 completed cleanly.

| Agent | Seed | Turns | Exit | Model seconds | Input tokens | Output tokens |
|---|---|---:|---|---:|---:|---:|
| 0 | 100 | 27 | 0 | 1807.9 | 1,617,264 | 69,172 |
| 1 | 101 | 25 | 0 | 1339.5 | 1,051,419 | 43,086 |
| 2 | 102 | 18 | 0 | 1331.8 | 820,044 | 47,410 |
| 3 | 103 | 11 | 0 | 1058.5 | 354,639 | 37,315 |

**Fleet A retry — success** (fresh attempt dir, unit exit 0, wall 75:23, no timeouts). Documented config changes only: per-request output budget `maxTokens` 32,768 → **65,536**, `contextWindow` 168,000 → **131,070** (the harness carried the dual-era value; 131,070 is the single-card engine maximum), compaction reserve 34,816 → 67,584, per-agent timeout 3600 → **5400 s**. Seeds unchanged.

| Agent | Seed | Turns | Exit | Artefacts | Model seconds | Output tokens |
|---|---|---:|---|---|---:|---:|
| 0 | 100 | 26 | 0 | all three | 4311.7 | 93,564 |
| 1 | 101 | 28 | 0 | all three | 4027.1 | 42,520 |
| 2 | 102 | 31 | 0 | all three | 4123.6 | 57,904 |
| 3 | 103 | 58 | 0 | all three | 4538.9 | 78,672 |

Seed-100 — the attempt-1 runaway — completed cleanly, spending 93,564 cumulative output tokens across 26 requests: the same seed succeeded under the revised client and budget profile. All four games passed the reported syntax and mocked-DOM behaviour probes with confirmed line clears. The retry kept seeds fixed but changed output budget, client context, compaction reserve and timeout together. The outcome improved from one clean delivery to four; it does not isolate which change was decisive. This was the final planned attempt.

### Artefact verification

All eleven produced games (3 from fleet A attempt 1, 4 from fleet dual, 4 from the retry), checked on target inside `localhost/pi-bench:4`:

- **Syntax**: inline-script `vm.Script` compile — 11/11 PASS.
- **Behaviour**: headless mocked-DOM probe (movement, rotation, pause/resume, hard-drop scoring, reset, line clear) — **11/11 PASS with a confirmed line clear on every game, zero ambiguous items**. The checker is a scope-injecting, API-discovering adaptation of the release's `tools/check_falling_blocks.cjs`, which hard-codes the four retained 7.14-era games' API shapes; the new games keep state in objects, bind `KeyP`-style key codes, use set-style pause APIs, column-major boards, and deterministic first spawns, so the probe is injected into each game's own script scope and discovers its surface (final version v13; iteration history v1–v13 preserved in the runbook). Mocked DOM is not full browser qualification.
- **Usage**: parsed per fleet with the release `scripts/parse_falling_blocks_events.py`. `usage.cacheRead/cacheWrite` are 0 fleet-wide because vLLM does not report cached tokens in OpenAI-compatible usage; this is a reporting property, not a cache defect.

Every produced game passed the reported probes. Those checks establish the exercised behaviours, not complete game quality or browser compatibility. The observed fleet failures involved missing deliverables and time limits; this comparison does not isolate model behaviour from serving conditions.

## Conclusions

1. **Dual card is the deployment for concurrent agents under ROCm 10.1**: 4/4 clean fleet exits, zero matrix preemptions and 27 s worst matrix TTFT. The fleet took 30:10, compared with 75:23 for the successful single-card retry; budgets and client settings differed.
2. **Single GPU A is viable to 2 agents and degrades sharply at 3–4** on the current 10 GiB KV tier; the historical comparison does not isolate tier size from runtime and other deployment changes.
3. **Budget and delivery checks matter**: every produced game passed the reported mocked-DOM probes, including a confirmed line clear; the failure modes observed are a reasoning runaway consuming the entire output budget and QA loops exceeding the wall clock.
4. **Fleet A retry (raised budgets) succeeded 4/4 on identical seeds**: per-request output 32,768 → 65,536, context corrected to the single-card maximum 131,070, per-agent wall 3600 → 5400 s. The seed-100 reasoning runaway that produced zero artefacts at the 32k cap completed a full verified game at the raised budget — the same seed succeeded under the revised profile. The measured successful single-card settings were 65,536 output tokens per request, a 67,584-token compaction reserve and a 5,400-second per-agent cap. One attempt does not establish minimum required budgets; dual completed its fleet within the original 3,600-second / 32,768-token settings.

## Evidence and accounting

[Per-agent fleet outcome CSV](../data/rocm-10.1/falling-blocks-fleet-outcomes-2026-10-18.csv) · [Game gallery and provenance](../examples/rocm-10.1/falling-blocks/README.md)

- [Eight-cell timed-turn export](../data/rocm-10.1/follow-up-single-vs-dual-text-growth-2026-10-18.csv) and [single-card configuration](../data/rocm-10.1/single-card-gpu-a-configuration.json).
- [Retained historical references](../data/rocm-7.14/historical-agent-workloads.csv) and [version provenance](ROCM-VERSIONS.md).
- The table above includes one empty completion in GPU A n4 and one in dual n2. Their counts are 115/64 completed responses versus 114/63 timed turns in the exported CSVs. Do not combine these counting conventions.
- Wall times above cover accepted case execution; CSV harness elapsed times use a narrower interval and can differ slightly.
- Fleet outcomes and headless checks are reported from the local handover. The underlying sessions, target paths and private transcripts are not published. The eleven games are published under [`examples/rocm-10.1/falling-blocks/`](../examples/rocm-10.1/falling-blocks/README.md) with a [gallery](../examples/rocm-10.1/falling-blocks/index.html) and a [manifest](../examples/rocm-10.1/falling-blocks/manifest.json) recording original and released hashes; seven games had the four-line-clear banner and matching sound identifiers renamed for public naming (rules unchanged), and every released file was re-verified on its released bytes.
- The earlier seven-cell campaign is separate and remains unchanged. The raised-budget single-card fleet retry completed successfully (4/4 clean, all artefacts, all checks passed) and is recorded above.

All tables are single-observation records. Fleet outcomes and headless checks were executed on the target during the campaign and captured in the handover; no new tests were run for the document itself.

This document is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/); see the repository [LICENSE](../LICENSE) and the [Licence section](../README.md#licence).

<!-- NAVIGATION START -->

[Home](../index.md) · [Overview](../README.md) · [Charts](CHARTS.md)
