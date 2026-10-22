---
layout: default
title: "Engine, kernel, and model research"
---

# Engine, kernel, and model research

The R9700 archive contains more than the RAM16 agent-capacity campaign. This document rolls up the other major investigation threads into one new summary. It keeps conclusions separate where their model, image, context length, or correctness gate differed.

## Relation to the ROCm comparison

These are historical engineering branches with separate qualification gates. The later [ROCm 10.1 matrix and fleets](FINAL-REPORT-20261018.md) used Swift-1.5 INT4, calibrated FP8 KV, ARC CPU offload and MTP. Historical DFlash, MXFP4 and larger native offload experiments below do not define the current serving profile or override its 10 GiB CPU-tier limit.

## FP8 KV cache and calibration

A model-bound FP8-KV sidecar was calibrated for the Qwen hybrid model. At about 126k context, the recorded four-agent comparison improved repeat per-agent decode from 32.9 to 41.8 tokens/s (+27%), repeat end-to-end output from 28.5 to 36.3 tokens/s (+27%), and mean TTFT from 58.7 to 45.9 seconds (-22%), with no reported preemptions. At 32k context FP8 KV was about 10% slower, consistent with a bandwidth benefit that grows at depth. In that earlier comparison, cache capacity remained approximately flat because its allocation path retained padding; this is not a claim about every later backend. The later deployment was reported to double capacity with FP8. The measured speed result was specific to deep context; FP8 also targets memory capacity, while calibration supplies suitable scales. See [FP8 KV calibration and reproduction](FP8-KV-CALIBRATION.md) for the full workflow and the distinction between the earlier padded layout and later capacity observations.

Calibration requires the exact model/checkpoint identity and FP8 cache dtype. Q/K/V scales and zero-points are model-specific; offline TunableOp state also needs signature checks. The later RX5 work kept calibration sidecars and persisted TunableOp opt-in rather than broadening the production default.

## R4D kernels and speculative decoding

Matched BetterBench results showed close non-speculative decode parity with the prior reference path. MTP and DFlash increased throughput substantially in those specific two-GPU, short-context tests. DFlash K7 measured about 3.15× the non-spec weighted throughput and 2.64× at concurrency eight; however, strict token-for-token equivalence did not pass. Later model-specific K7 runs were coherent on selected fixtures but still did not establish lossless equivalence. DFlash therefore remained experimental.

Kernel correctness was treated as a separate result from speed. R4D attention, R4D GDN, and compressed all-reduce could each change deterministic greedy streams versus prior paths. Exact two-rank all-reduce and compressed all-reduce are different modes: compression is a numerical change, not a transparent bandwidth switch. Build and benchmark claims must name the selected path.

A v0.30 publication gate also recorded a tool-use qualification failure for the fast MTP path. The recommendation at that publication checkpoint was ordinary non-speculative serving; later MTP work on a different model/configuration does not erase that gate.

## MXFP4 / W4A8

The archive records native gfx1201 Quark MXFP4 W4A8 integration and successive guarded decode-kernel work. Correctness depends on the checkpoint's quantization contract, activation quantization, GDN state, MTP head dtype, and serving shape. A required GDN overflow guard matters because non-finite activations can poison dynamic FP8 scaling while still producing plausible-looking text.

Follow-on experiments improved decode speed, but no single profile should be treated as generic across models and sequence counts. Some A-tiled, norm-quant, and FP8-stream paths remained disabled or opt-in because they were not broadly qualified. NVFP4 work passed conversion fixtures but lacked a real checkpoint quality/continuous-recompute qualification; it is not a broad native NVFP4 support claim.

## Native CPU KV offload

Native CPU KV offload behaved as an external prefix-cache tier, not simply more live GPU KV capacity. A 24 GiB dual-rank mapping restored one long prefix with about 8.67 GB moved in 308 ms of aggregate transfer-counter time. At 256k with three concurrent requests, the 24 GiB tier improved measured end-to-end output from 1.854 to 2.735 tokens/s (+47.5%) by restoring one prefix; at four requests, cache churn meant the forced-restore phase retained no prefix and returned to recomputation behaviour.

Registration reliability became a correctness constraint. The archived matrix was healthy at 24 GiB but exposed partial-rank registration failures at 32 and 36 GiB. The hardening work consumed pending HIP errors and made fallback behaviour explicit. A later rank-major layout was still experimental and had not passed live dual-GPU qualification at the documented larger capacities. Those capacities are targets, not achieved results.

## Serving correctness and API behaviour

Separate qualification fixed tool-call parsing for valid nested object schemas where JSON Schema permits omitted `additionalProperties`. The issue affected both streaming and non-streaming Chat Completions and was rooted in the schema-to-grammar representation. Structured-output speculative decoding also needed two state-machine fixes: stop draft batches when the grammar reaches termination, reset termination state correctly, and validate pre-boundary drafts against the active grammar.

These fixes are API/correctness work, not throughput improvements. Their regression gates should remain in place when changing the vLLM pin or parser/grammar stack.

## Build and publication discipline

The source archive kept stable vLLM version changes behind patch audits, component pins, parser/tool gates, exact manifests, and image qualification. The ROCm 7.14 stack and a separate ROCm 10.1 image were both recorded. A newer base image passing import/startup checks does not, by itself, qualify model quality or an apples-to-apples performance gain.

For each result, report model/quantization, image stack, GPU count/topology, context/concurrency, cache/tier state, speculative mode, correctness gate, and whether the run was controlled against a matched baseline. This is the minimum context needed to interpret the derived CSVs responsibly.

<!-- NAVIGATION START -->

[Home](../index.md) · [Overview](../README.md) · [Latest campaign](RADIANCE-CAMPAIGN-2026-10-21.md) · [Charts](CHARTS.md)
