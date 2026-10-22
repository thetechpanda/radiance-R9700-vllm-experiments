---
layout: default
title: "Hugging Face model inventory"
---

# Hugging Face model inventory

The central R9700 agent serving campaign studied **Qwen3.8 27B**. Its primary checkpoint was [`ukisai/Swift-1.5-Qwen3.8-27b-INT4`](https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-27b-INT4), an AWQ+GPTQ INT4 hybrid GDN variant. This is the model behind the single-card RAM16 milestone and the follow-on TP=2 investigation summarised in the [research journal](RESEARCH-JOURNAL.md).

## Recorded ROCm 10.1 checkpoint

The follow-up single/dual comparison used the Swift-1.5 checkpoint at revision `81a28ee75eb1cd469f209813a368a79a7e3db3bc`, FP8 attention KV and model-matched calibration. MTP depth was four on GPU A and eight on dual. DFlash2 and MXFP4 experiments below are separate research branches, not the configuration behind these matrix results. See the [configuration record](../data/rocm-10.1/single-card-gpu-a-configuration.json).

The broader collected Radiance work also contains tests and build/benchmark notes for the following Hugging Face checkpoints. Their presence here records model use in the research archive; it does not mean their results are included in the retained case charts or directly comparable to the primary Swift-1.5 campaign. Check the cited notes and each benchmark's configuration before interpreting a result.

| Hugging Face repository | Role in the collected work | How to interpret it |
|---|---|---|
| [`ukisai/Swift-1.5-Qwen3.8-27b-INT4`](https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-27b-INT4) | **Primary research target:** hybrid Qwen3.8 27B, AWQ+GPTQ INT4; used for the one-card agent campaign and TP=2 follow-up. | Central model for the historical agent-serving findings in this package. |
| [`amd/Qwen3.8-27B-Quark-AWQ-MXFP4`](https://huggingface.co/amd/Qwen3.8-27B-Quark-AWQ-MXFP4) | Qwen3.8 27B Quark AWQ/MXFP4 target used in separate Radiance W4A8 and DFlash2 work. | Related model-format/kernel experiments, not a substitute for the Swift-1.5 INT4 run results. |
| [`tcclaviger/Qwen3.8-27B-DFlash2-FP8`](https://huggingface.co/tcclaviger/Qwen3.8-27B-DFlash2-FP8) | Target-matched Qwen3.8 DFlash2 draft checkpoint used in separate speculative decoding experiments. | Drafter, not the primary target model. Speculative results depend on the paired target and runtime path. |
| `Qwen3.8-27B-heretic-ara-fp8-magiccodingman` | Native-FP8 Qwen3.8 target recorded in Radiance build and benchmark notes. | Separate target variant. The source archive refers to it by local model name/path; no HF namespace is asserted here. |
| `Qwen3.8-27B-heretic-ara-DFlash2-fp8-magiccodingman` | Selective-FP8 DFlash2 draft recorded alongside the heretic-ara target. | Drafter, not a standalone target result. Source notes use local paths rather than a verified HF repository ID. |
| `Qwen3.8-27B-heretic-ara-heretic-org` | Additional Qwen3.8 target variant appearing in DFlash2 loading/serving notes. | Related exploratory checkpoint; not the primary Swift-1.5 campaign. Source notes do not establish a canonical HF namespace. |
| `Qwen3.8-27B-DFlash2-z-lab` | DFlash2 draft variant appearing in model load and serve notes. | Drafter; source notes do not establish a canonical HF namespace. |

The model snapshot, tokenizer files, draft weights, and FP8 KV calibration sidecars are not redistributed with this package. The primary launch instructions use operator-supplied model paths and IDs. See [launch instructions](SCRIPTS.md), [benchmark interpretation](BENCHMARKS.md), and the [run index](RUN-INDEX.md).

<!-- NAVIGATION START -->

[Home](../index.md) · [Overview](../README.md) · [Latest campaign](RADIANCE-CAMPAIGN-2026-10-21.md) · [Charts](CHARTS.md)
