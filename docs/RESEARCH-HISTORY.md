---
layout: default
title: "A history of the R9700 investigation: what we tried, what survives"
description: "A source-led account of the machine, failed approaches, measured campaigns, corrected claims and unfinished questions."
---

# What we tried, what survives

A result table makes an experiment look tidier than it was. This record includes rewiring, kernel work, model conversion, cache calibration, builds that needed repairs, agents that produced nothing, and measurements whose labels later proved wrong. Those are part of the work, not debris to sweep away before publication.

The author gives the reason plainly in the [human disclaimer](../HUMANS.md#humans): this was done because it was fun. The original question was practical: **how many coding agents could carry roughly 131k histories on one R9700 plus host RAM, with useful waits and completed work?** The investigation changed the machine and eventually the engine. It never became a clean experiment with only one variable changing.

This account distinguishes the dates and claims in the surviving records from later interpretation. The [journal](RESEARCH-JOURNAL.md), campaign CSVs, configuration records, artefact manifests and [correction ledger](EDITORIAL-REVIEW.md) are its sources. Missing evidence remains missing.

## The early single-card record: depth was only half the question

The retained ROCm 7.14 branch records experiments with prompt cadence, compaction, memory tiers and storage. The journal describes an early OCuLink path and a later direct rewire; those changes improved recorded transfer behaviour but did not remove every long wait. The later hardware inventory establishes ×8 and ×4 host bottlenecks rather than retrospectively assigning one topology to every early run.

The E21 RAM16 milestone is the clearest single-card reference: four agents completed 155 turns with 16.88 s mean TTFT and a 53.85 s maximum. Three turns exceeded the stated 45-second threshold. The E22 three-agent follow-up completed 124 turns with 13.34 s mean TTFT at deeper cumulative history. “Usable on average” survives in the journal alongside the tail misses; neither should be erased by the other. [Milestone narrative](RESEARCH-JOURNAL.md#2-reach-the-ram16-single-card-milestone) · [retained workload summary](../data/rocm-7.14/historical-agent-workloads.csv).

The same record notes a workload correction: equal large tool chunks had synchronized agents unrealistically. Mixed-size, desynchronized traffic changed what the benchmark was testing. That is why nominal context size alone cannot turn all these runs into one scaling curve.

## By 16 October: a second card, the same small host

The second R9700 created a different system. GPU A's later host path was PCIe 4.0 ×8; GPU B used ×4 through an NVMe-to-OCuLink adapter/redriver. Peer transfers required topology-specific qualification, including the preserved P2PDMA whitelist patch and a custom kernel. The record establishes that this setup worked; it does not establish that all two-card R9700 systems require the same patch.

The host still exposed about 30 GiB of RAM. Early 20 GiB host-cache/filesystem combinations drove active swapping. A 16 GiB RAM-only revision left limited margin. A subsequent 4 GiB ARC/no-filesystem profile recovered headroom. Attempting swap reclaim while the model was resident caused an out-of-memory restart. The failure explains the later caution about “just give it more host cache.” [Two-card transition](RESEARCH-JOURNAL.md#4-add-the-second-gpu-and-solve-a-different-problem) · [setup work](ENVIRONMENT.md).

## 17–18 October: a new software profile and a narrower question

The journal dates a separately built ROCm 10.1 image to 17 October. Its four-agent stress observation completed 116 turns with zero reported request errors, but its nearest older reference used a different depth/workload. That was evidence the deployment worked, not an isolated ROCm speed test. [Version evidence](ROCM-VERSIONS.md) · [stress export](../data/rocm-10.1/rocm-base-image-four-agent-stress-run.csv).

The 18 October follow-up made the question more focused: one and two cards at one to four concurrent agents, Swift-1.5 INT4 with FP8 KV and a 10 GiB host tier. The single-card profile used MTP-4; dual used MTP-8, more slots and a larger configured context. At four agents, mean/maximum TTFT was **101.38/654.91 s single** versus **10.85/27.23 s dual**. The unequal settings remain part of the comparison. [Original eight-cell export](../data/rocm-10.1/follow-up-single-vs-dual-text-growth-2026-10-18.csv) · [acceptance report](FINAL-REPORT-20261018.md).

The real-agent test left a different kind of evidence: games. In the first single-card attempt, one process exited cleanly after exhausting its reasoning budget without producing files; two others delivered and then timed out. Three games survived, but only one clean delivery. The dual fleet delivered four with clean exits in 30:10. A single-card retry changed several client budgets and delivered four cleanly in 75:23. The same seed's later success did not isolate a hardware effect; it showed why an exit code alone had been an inadequate acceptance criterion. [Fleet outcome ledger](../data/rocm-10.1/falling-blocks-fleet-outcomes-2026-10-18.csv).

## 19 October: model choice and speculation became separate axes

The 41-cell, 1,160-turn sweep compared three target checkpoints across several drafting lanes. The fastest observed four-agent cell was AMD Quark AWQ non-spec V4 at 330.4 s. Swift-Quark RTN non-spec was selected in the campaign with an output-style preference; its S4/S6 repeats were 372.8/439.0 s. Selection and fastest measurement were different facts.

DFlash2's four-agent walls were much longer on both tested MXFP4 targets. Boot pool sizes also changed between lanes. Earlier repeat spread showed variability, but supplied no statistical error bar for later engine comparisons. Those details prevent a neat story in which speculative decoding simply makes agents faster. [Sweep CSV](../data/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.csv) · [campaign interpretation](DUAL-R9700-SPEC-CAMPAIGN.md).

## 21 October: the engine changed, and so did the comparison limits

The standalone radiance 1.9.0 campaign completed ten cells, 280 turns and zero reported errors. Its recovered client matched the recorded harness hash. Its model/cache identity did not match every older reference: radiance records revision `81a28ee7…` and FP8 KV; Y/Z records `9dba8a05` and BF16 KV. The older engine was not rerun alongside it.

Historical vllm-radiance non-speculative walls were shorter at every tested agent count. Radiance MTP-4 walls were shorter than the historical MTP lane by 7.0–17.6%. Different latency and generation columns favoured different deployments. This is a mixed result worth preserving, not an inconvenience to the narrative. [Radiance grid](../data/rocm-10.1/radiance-campaign-2026-10-21.csv) · [comparison contract](RADIANCE-VS-VLLM.md).

Four more games arrived. The corrected receipts show agents 0–1 timing out after delivery and agents 2–3 exiting cleanly: **4/4 delivered, 2/4 clean**. The current ROCm 10.1 gallery contains **fifteen games across four fleet attempts**, with the older eleven behaviour probes distinguished from the radiance syntax checks. [Corrected fleet CSV](../data/rocm-10.1/radiance-falling-blocks-fleet-2026-10-21.csv) · [artefact manifests](../examples/rocm-10.1/falling-blocks/manifest.json).

## 22 October: capacity was larger than the first allocation

The single-card radiance grid completed 92 turns with zero reported errors. Its four-agent growth target fell to 88,913 tokens; the older reference targeted 126,000. Lower waits came with a different history budget, so an equal-depth engine speedup was not established. [Single-card record](RADIANCE-SINGLE-CARD-2026-10-22.md).

The two-card memory story also needed a correction. The original 524,304-token pool was a four-slot allocation target. Six slots and a 204,800-token server limit later allocated 1,228,816 tokens on the same cards. That is **134.4% more allocated capacity**, not proof of six simultaneously useful 200k agents. The reported 165k needle probe answered one acceptance question; it did not supply the missing concurrency grid. [Measured/projection ladder](RADIANCE-200K-CONTEXT-2026-10-22.md).

## The publication is part of the history

The first editorial review corrected the shared-checkpoint assumption, metric denominators, turn counts, biased language and a configuration limit presented as a hardware ceiling. It also accepted an erroneous fleet CSV that said all four radiance processes timed out. Re-reading the actual exit-status files corrected that conclusion to two clean exits. Multiple AI reviewers had checked the same wrong source; agreement had not made it true.

The transparency follow-up recovered the original synthetic benchmark, needle script, client recipe and editorial prompts, with hashes and explicit adapter labels. That makes more of the method inspectable. The recovered prompts retain their mistakes as evidence of what was asked then, while the current pages use the corrected receipts. [Editorial audit](EDITORIAL-REVIEW.md) · [recovery manifest](../data/recovery-manifest.json) · [AI/tools disclosure](REPRODUCIBILITY.md).

## For the next reader

The archive preserves results, selected traces, configurations, code, patches and games. It does not preserve every raw session, calibration input, model file, historical image or complete experimental environment. There is no matched engine rerun, sustained six-agent 200k grid, common raw-kernel PP benchmark or blinded quality study.

Reuse the questions as well as the numbers. Ask how much history each agent actually held, how long it waited, whether it delivered, which settings changed, and what evidence would make the claim false. Keep the failures in view. They explain why this particular small machine ended up configured the way it did.

<!-- NAVIGATION START -->

[Home](../index.md) · [Compare](RADIANCE-VS-VLLM.md) · [vllm-radiance](VLLM-RADIANCE.md) · [radiance](RADIANCE.md) · [Charts](CHARTS.md) · [Stuff for nerds](CODE-CORNER.md) · [Disclosure](REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
