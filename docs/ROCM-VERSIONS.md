---
layout: default
title: "ROCm 7.14 and ROCm 10.1 evidence"
---

# ROCm 7.14 and ROCm 10.1 evidence

The primary research objective is ROCm 7.14 versus ROCm 10.1 using the `vllm-radiance` repository. This page separates results from the two software profiles. The eight-cell ROCm 10.1 follow-up matrix and first single/dual coding fleets have recorded outcomes; the raised-budget single-card retry completed with four clean deliveries in 75:23. The archived build record identifies the older profile as ROCm **7.14**: the base image is tagged 7.14.0 and the PyTorch package carries `+rocm7.14`. There is no basis here for interpreting that version as ROCm 7.1.4.

## Newer dual-card campaign — 19 October

The [model/speculation campaign](DUAL-R9700-SPEC-CAMPAIGN.md) adds an eight-cell initial comparison and a 41-cell sweep under ROCm 10.1. The later sweep varies target, lane and concurrency with BF16 KV. Its recommendation is Swift-Quark RTN MXFP4 with speculation off for four-agent load (S4/S6; initial reference E1). It is not evidence of a ROCm 7.14→10.1 speedup, and it does not replace the earlier single-card capacity finding. [Sweep CSV](../data/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.csv).

## Recorded software profiles

| Profile | Recorded components | Evidence scope |
|---|---|---|
| ROCm 7.14 | vLLM 0.30.0; AMD PyTorch 2.12 with `+rocm7.14`; Triton 3.7.1; AITER 0.1.20; libr4d 0.5.0 | Main archived two-card image and historical tuning work. |
| ROCm 10.1 | vLLM 0.30.0; PyTorch 2.12.0+rocm10.1; Triton 3.7.1; AITER 0.1.20; libr4d 0.5.0 | Separately built image, runtime checks, later TP=2 stress and repeat-campaign work. |

The versions share several component numbers, but changing the ROCm userspace and rebuilding the stack means the profiles are distinct. A successful import, startup or JIT check establishes that the image can start those paths; it does not alone establish model quality or comparative serving performance.

## Closest archived stress comparison

The archived notes compare a four-agent ROCm 10.1 stress run with a four-agent ROCm 7.14 text-growth case. This is an earlier stress reference, not the latest matrix or a controlled A/B:

| Profile and case | Target / observed maximum context | Completed turns | Mean TTFT | Maximum TTFT | Client errors |
|---|---:|---:|---:|---:|---:|
| ROCm 7.14, four-agent text-growth case | 100k / 109.5k | 36 | 26.74 s | 84.64 s | 0 |
| ROCm 10.1, four-agent stress case | 126k / 126.1k | 116 | 11.36 s | 47.9 s | 0 |

The ROCm 10.1 case ran longer, completed more turns, and reached a deeper observed context. The depth target, workload history, and configuration were not matched, so the difference cannot be attributed to ROCm alone. Treat the result as a promising operational observation, not a causal speedup claim. The older test family also includes many capacity, compaction, storage, instrumentation and failed or tainted trials. Those answer different questions and are not version comparisons; their source records remain in the research archive.

## Later ROCm 10.1 text campaign

On 18 October 2026, seven text-only cells completed on ROCm 10.1 with TP=2, eight configured MTP tokens and an 8 GiB CPU KV tier. The 126k and 150k targets each completed for 1, 2 and 3 agents; the 126k four-agent case also completed. The 150k four-agent case was stopped before completion, and the remaining planned cases were not run. Completed final attempts had zero client errors. The full per-cell TTFT record and incomplete-case status are in the [repeat-campaign ledger](REPEAT-CAMPAIGN.md).

This later campaign is internally more comparable because the profile and workload family were held fixed across its completed cells. It still has one observation per cell and does not compare ROCm 10.1 against ROCm 7.14 under matched conditions. No full-suite claim follows from the seven completed cases.

## Latest ROCm 10.1 follow-up

The [matrix and fleet report](FINAL-REPORT-20261018.md) records GPU A and dual-card deployments at 1–4 agents. GPU A mean TTFT rose from 7.46/11.92 seconds at 1/2 agents to 71.46/101.38 seconds at 3/4. Dual mean TTFT ranged from 5.19 to 10.85 seconds, with no recorded KV preemptions. Both used a 10 GiB ARC CPU tier; TP, context limit, slots and MTP depth differed. These are deployment comparisons within ROCm 10.1.

The historical RAM16 three/four-agent means were 13.34/16.88 seconds. They are useful operating references, but do not isolate a runtime effect. A 16 GiB tier later caused host slowdown and is not the current recommendation. See [both single-card configurations](../README.md#best-recorded-single-card-setup-for-34-deep-context-agents).

## What is not a version comparison

- Historical compaction, storage, scheduling and speculative-depth variants answer tuning questions; the [exclusion summary](EXCLUDED-TESTS.md) explains their treatment.
- Game files stored under `rocm-7.14` preserve historical collection provenance; the HTML itself does not verify a runtime identity.
- First ROCm 10.1 fleets produced three games on GPU A and four on dual; only the dual fleet had four clean exits. These are single-fleet task observations, not controlled measures of model competence.
- GPU B alone was not measured in the focused follow-up. GPU A versus dual has completed, but their serving settings differ.

<!-- NAVIGATION START -->

[Home](../index.md) · [Overview](../README.md) · [Latest campaign](RADIANCE-CAMPAIGN-2026-10-21.md) · [Charts](CHARTS.md)
