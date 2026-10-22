---
layout: default
title: "vllm-radiance vs radiance: two engines on the R9700"
description: "A hands-on comparison of coding-agent latency, model generation, KV memory and delivered games on one and two Radeon AI PRO R9700 cards."
permalink: /
---

> **AI-generated article:** This article is fully AI-generated and has not been human-edited; the article itself is an output of this research and part of the evaluation.

<p class="eyebrow">22 October 2026 · Radeon AI PRO R9700 · Qwen3.8 27B</p>

# Two engines. One small box. A lot of context.

<p class="dek">I wanted to know how many coding agents one R9700 could keep useful. That turned into two cards, two inference engines, speculative decoding, memory archaeology—and a collection of playable games.</p>

This is the story of **vllm-radiance vs radiance** on a Minisforum MS-01 with **32 GB of host RAM** and up to **two Radeon AI PRO R9700 32 GB cards**. The interesting question is what happens when several coding agents bring long histories to the same machine: time spent waiting, generation speed, memory pressure and whether the work gets delivered.

There is no single winner across those columns. The recorded radiance MTP-4 runs finish sooner than the older MTP-4 runs; vllm-radiance keeps advantages in other measurements. The model revisions, cache formats and some workload budgets differ. I’ll keep those differences next to the numbers.

> **Transparency:** These are historical deployment observations, with a partly reproducible pipeline. The [tools and AI disclosure](docs/REPRODUCIBILITY.md) identifies recovered source, private/missing evidence and what readers can regenerate or rerun.

<div class="stat-grid" markdown="0">
<div class="stat-card">
<b>−17.6%</b><span>Four-agent wall time: radiance MTP-4 vs historical vllm-radiance MTP-4.</span><small>402.7 vs 488.7 s. Different revisions and KV formats; an observed deployment comparison.</small>
</div>
<div class="stat-card">
<b>+134.4%</b><span>GPU KV pool after increasing slots and context on the same two cards.</span><small>524,304 → 1,228,816 allocated tokens. Capacity measured at boot; six-agent speed untested.</small>
</div>
<div class="stat-card">
<b>4 / 4</b><span>Games delivered by the radiance coding fleet.</span><small>Two later timed out; two exited cleanly. File delivery and process completion are separate results.</small>
</div>
</div>

[Sources: R6-mtp4-n4 vs Z4, pool boot rows, fleet agents 0–3](docs/RADIANCE-VS-VLLM.md#evidence-map).

<div class="reading-path" markdown="1">

[Explore vllm-radiance →](docs/VLLM-RADIANCE.md)
[Explore radiance →](docs/RADIANCE.md)
[The full comparison →](docs/RADIANCE-VS-VLLM.md)

</div>

## What it took to get this box serving

The machine is a **Minisforum MS-01, Core i5-12600H, 32 GB DDR5**, initially with one R9700 and later two. The host RAM stayed the same. The later host links are **PCIe 4.0 ×8 for GPU A and ×4 for GPU B**, so two cards did not make a symmetric workstation.

Before the measurements came the setup work: a topology-specific **P2PDMA kernel patch and verified peer transfers**; a coherent ROCm/PyTorch/vLLM/kernel build; **checkpoint-matched FP8 KV calibration**; and repeated changes to host-cache, shared-memory and swap budgets. Some larger tiers failed. The standalone radiance transition then added model conversion and different service/memory behaviour. These changes enabled the recorded deployments; they do not isolate a speed gain from each individual step.

[Read the setup story](docs/ENVIRONMENT.md) · [Follow the investigation's history](docs/RESEARCH-HISTORY.md) · [Stuff for nerds: scripts, monitoring and worked examples](docs/CODE-CORNER.md).

## First, what exactly is being compared?

**vllm-radiance** is the vLLM fork used in the earlier campaigns. **radiance** is the standalone `stilldeadcode/radiance` engine, recorded here at version **1.9.0**, using converted `.rad` model bundles. TP1 means one card; TP2 splits the model across two. They are configurations, not extra engines.

The main model family is **Swift-1.5 Qwen3.8 27B**, with **4-bit weights**. That is separate from the **FP8 or BF16 KV cache** storing attention history. The 19 October model sweep also tested **Swift-Quark RTN MXFP4** and **AMD Quark AWQ MXFP4**; its fastest cells are not interchangeable with the later INT4 results.

| Campaign | Target / representation | Recorded revision | KV / host tier |
|---|---|---|---|
| vllm-radiance single-card, 18 Oct | `ukisai/Swift-1.5-Qwen3.8-27b-INT4`, hybrid INT4 | `81a28ee7…` | FP8 / 10 GiB |
| vllm-radiance Y/Z engine references, 19 Oct | `ukisai/Swift-1.5-Qwen3.8-27b-W4A16-AWQ` | `9dba8a05` | BF16 / 10 GiB |
| radiance, 21–22 Oct | Converted INT4 `.rad` bundle; served as `ukisai/Swift-1.5-Qwen3.8-27b-W4A16-AWQ` | `81a28ee7…` | FP8 / 10 GiB dual grid, 13 GiB single-card/fleet |

The radiance conversion record names the Swift-1.5 **INT4 source**; the serving name uses **W4A16-AWQ**. An API name is not proof of byte-identical weights. [Full model identities and sources](docs/MODELS.md).

A quick decoder ring: **TTFT** is the wait for the first streamed content, including queueing. **TG** is token generation; this archive contains several request/turn estimates, not a universal fleet throughput score. **PP** is prompt processing. Cached prompt intake is not raw kernel PP, and there is no validated matched PP benchmark here. **Context** is input history plus room for the response; a configured ceiling is not proof that every agent ran there together. [How to read the measurements](docs/DATA-DICTIONARY.md).

## The engine swap: a result with two sides

The closest workload comparison uses ten synthetic turns per agent, one to four agents, and a 126k growth target. The historical reference is from 19 October; radiance ran on 21 October with the recovered harness. The old engine was not rerun alongside it. Different target revisions and BF16 vs FP8 KV prevent an isolated engine-speed claim.

![Two panels compare total wall time for both engines, with speculation off and with MTP-4](graphs/rocm-10.1/engine-wall-comparison.svg)

[Open full-size chart](graphs/rocm-10.1/engine-wall-comparison.svg) · [Source rows and all percentage calculations](docs/RADIANCE-VS-VLLM.md#dual-card-wall-time).

| Agents | Speculation off: radiance vs vllm-radiance | MTP-4: radiance vs vllm-radiance |
|---|---:|---:|
| 1 | 130.6 vs 126.7 s · **3.1% longer** | 102.3 vs 115.1 s · **11.1% shorter** |
| 2 | 232.1 vs 212.1 s · **9.4% longer** | 204.7 vs 231.6 s · **11.6% shorter** |
| 3 | 327.0 vs 306.4 s · **6.7% longer** | 300.5 vs 323.1 s · **7.0% shorter** |
| 4 | 429.3 vs 401.8 s · **6.8% longer** | 402.7 vs 488.7 s · **17.6% shorter** |

That is the useful shape of the result: **vllm-radiance has the shorter non-speculative wall at every agent count; radiance has the shorter MTP-4 wall at every count**. At four agents, radiance MTP-4 and the old non-speculative lane are almost identical: **402.7 vs 401.8 seconds**, a **0.2%** difference.

Earlier repeat cells on a different model (Swift-Quark RTN MXFP4) varied by roughly 15%. That is a warning about repeatability, not an error bar or a significance threshold for these newer runs. These percentages describe the observations; they don’t establish a repeatable ranking.

### Faster to finish does not mean faster in every metric

At one agent with MTP-4, the reported per-turn generation estimate is **137.9 tok/s for radiance vs 185.7 for vllm-radiance**, **25.7% lower** for radiance, while total wall time is **11.1% shorter**. The tests include growing prompts and waits, so a short-response TG estimate cannot stand in for end-to-end completion. Keep the metric definition and the whole workload in view. [Decode fields, latency and limitations](docs/RADIANCE-VS-VLLM.md#latency-and-generation).

## One card: the price of keeping more history

The single-card story is more dramatic—and less directly comparable. The older vllm-radiance family runs longer histories and more turns; radiance uses a larger host tier and reduces its growth cap as concurrency rises. At four agents, that cap is **88,913 vs 126,000 tokens**, **29.4% lower**. The chart therefore shows a latency/depth tradeoff, not an equal-depth speedup.

![Four panels show four-agent mean and maximum TTFT, observed context depth, and request generation estimates](graphs/rocm-10.1/single-card-tradeoffs.svg)

[Open full-size chart](graphs/rocm-10.1/single-card-tradeoffs.svg) · [Single-card source data, turn counts and configurations](docs/RADIANCE-SINGLE-CARD-2026-10-22.md).

At four agents, radiance records **14.34 s mean TTFT vs 101.38 s**, **85.9% lower**, alongside **99,075 vs 126,691 tokens** maximum observed history. The older engine’s request generation estimate is higher: **25.5 vs 17.4 tok/s**. Those are different kinds of value: a shorter wait, a deeper history, a faster output stream.

The practical conclusion is bounded. The recorded vllm-radiance ROCm 10.1 profile was useful at **one to two deep-context agents**, then developed long waits. Radiance completed all four single-card cells with **zero reported errors over 92 turns**, but its four-agent run used a smaller context cap. Neither result establishes four smooth, simultaneous, full-131k coding agents on one card.

## The memory mystery: 524k was not the two-card ceiling

The first radiance TP2 campaign allocated about **524k KV tokens**, while one card allocated **405k**. That looks like poor two-card scaling until the allocation rule becomes visible: the original two-card pool was limited by **four slots × 131k context**. The one-card pool was limited by available VRAM.

Increasing the two-card slot count, then the configured context, produced these measured boot allocations:

![Measured GPU KV pool allocations across one-card and two-card slot and context configurations](graphs/rocm-10.1/memory-allocation.svg)

[Open full-size chart](graphs/rocm-10.1/memory-allocation.svg) · [Boot-allocation CSV](data/rocm-10.1/radiance-pool-ceiling-2026-10-22.csv).

The later **1,228,816-token** pool backs the allocation budget for **six 204,800-token sessions**. That is a capacity result. A reported **165,075-token needle probe** exercises one longer prompt; there is no six-agent 200k performance grid in this release. The larger elastic ceiling remains a projection. [The capacity ladder, measured vs projected](docs/RADIANCE-200K-CONTEXT-2026-10-22.md).

## And did the agents actually build anything?

Yes. I also asked four independent coding agents to build Falling Blocks games. This is where files, process exits and quality checks need their own columns.

| Fleet | Complete deliveries | Clean exits | Recorded check / timing |
|---|---:|---:|---|
| vllm-radiance, single card, first attempt | 3 / 4 | 2 / 4 processes; only 1 / 4 clean deliveries | Three games passed reported behaviour checks; one clean exit produced no files |
| vllm-radiance, dual card | 4 / 4 | 4 / 4 | Reported behaviour checks passed; fleet wall **30:10** |
| vllm-radiance, single-card retry | 4 / 4 | 4 / 4 | Reported behaviour checks passed; fleet wall **75:23**, raised budgets |
| radiance, dual card | 4 / 4 | 2 / 4 | Four reported syntax passes; agents 0–1 timed out after delivery, agents 2–3 exited cleanly |

[Historical fleet outcomes](data/rocm-10.1/falling-blocks-fleet-outcomes-2026-10-18.csv) · [radiance fleet outcomes](data/rocm-10.1/radiance-falling-blocks-fleet-2026-10-21.csv).

Different budgets and checks prevent a fair “better coder” ranking. The successful single-card retry changed several settings; syntax checks alone do not establish browser playability. **Delivering a game and finishing cleanly are different results.**

[Play the games and inspect their provenance](examples/rocm-10.1/falling-blocks/index.html) · [Real-agent method](docs/REAL-AGENT-TEST.md).

## Take the route that answers your question

| What you want to know | Where to go |
|---|---|
| Which measured configuration fits my workload? | [vllm-radiance results](docs/VLLM-RADIANCE.md) · [radiance results](docs/RADIANCE.md) |
| Every wall-time delta, model difference and caveat | [Head-to-head evidence](docs/RADIANCE-VS-VLLM.md) |
| Models, quantization, PP, TG and context definitions | [Model inventory](docs/MODELS.md) · [Data dictionary](docs/DATA-DICTIONARY.md) |
| Memory pools, longer context and what remains untested | [200k capacity report](docs/RADIANCE-200K-CONTEXT-2026-10-22.md) |
| The 41-cell model/speculation sweep | [19 October campaign](docs/DUAL-R9700-SPEC-CAMPAIGN.md) |
| Hardware, setup work and reproduction | [Setup story](docs/ENVIRONMENT.md) · [Hardware](docs/HARDWARE.md) · [Code corner](docs/CODE-CORNER.md) |
| Charts, CSVs and the research trail | [Charts](docs/CHARTS.md) · [Data](data/README.md) · [Journal](docs/RESEARCH-JOURNAL.md) |
| Earlier ROCm 7.14 vs 10.1 investigation | [Historical overview](HISTORICAL-OVERVIEW.md) · [Version evidence](docs/ROCM-VERSIONS.md) |

This is one host with asymmetric PCIe links, limited RAM and a custom kernel. The [exclusion record](docs/EXCLUDED-TESTS.md) stays available, including incomplete and contaminated experiments. The [editorial audit](docs/EDITORIAL-REVIEW.md) records the corrections made when bringing the two engine stories together.

## Humans

The original objective was to find out how many concurrent coding agents could each work at roughly 131k tokens of context on a **single Radeon AI PRO R9700, backed by host RAM for KV cache**. Capacity, response latency and successful task completion all mattered. The later two-card experiments extended that investigation.

This is hands-on systems research, with AI assistance used to help analyse and document the experiments. It started as an attempt to squeeze as much useful Qwen3.8 27B inference as possible out of a Radeon AI PRO R9700, and eventually grew into a two-GPU investigation.

The results, performance, and outcomes are reviewed and interpreted by me. I still need to know what to ask, what matters, and whether the results actually make sense. The execution is a different story. AI let me focus on the objective rather than every individual step required to get there. The implementation may have changed along the way, but the engineering decisions, evaluation, and responsibility for the outcome remained mine.

I did this because it was fun, and I had a blast doing it. That's really the only reason this repository exists.

Don't expect anything more from it. There is a ton I don't know, and nothing here should be treated as "100% correct." This is simply a blob of information documenting what I did, what I observed, and what I think matters. It doesn't pretend to be anything more than useful context you can throw at your agents while configuring and benchmarking your own R9700.

Comments are welcome, but that doesn't mean they'll be listened to. I have no plans to maintain this repository any further. I did what I did, I published what I found, and I'm moving on.

If any of this turns out to be useful to you, I'm happy it was.

## RTFM

Before running any script, code or command in this repository, READ IT TOP TO BOTTOM.
You are still responsible for running commands on your local machine. During the experiments I had folders deleted, models mangled, server hanging in kernel panic, grub bootloader misconfigured, signed kernels panicking because of misconfigured secure boot, etc.

I would not have moved forward if I didn't know what I was doing(-ish) 🤷‍♂️.


## Licence

Except where otherwise noted, the original notes, tables, charts and derived data on this site are licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). The full legal code is in the repository's [LICENSE](LICENSE) file. You are free to share and adapt this material for any purpose, including commercially, provided you give attribution.

Suggested attribution: *“R9700 field notes — vllm-radiance vs radiance, CC BY 4.0”* with a link to this site.

The agent-generated [Falling Blocks game files](examples/rocm-10.1/falling-blocks/README.md) are code artefacts of the recorded runs; CC licences are not designed for software and no separate software licence is asserted over them, but the same attribution request applies as a courtesy and their provenance and hashes are recorded in their manifests.
