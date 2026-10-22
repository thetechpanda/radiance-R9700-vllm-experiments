---
layout: default
title: "vllm-radiance: the capacity hunt and the model sweep"
---

# vllm-radiance: the capacity hunt and the model sweep

The investigation started here: one R9700, a long coding-agent history, and a host-RAM tier intended to keep more conversations useful. The vLLM fork produced the historical single-card milestones, the one-vs-two-card matrix and the 41-cell model/speculation sweep. These are distinct campaigns, with different models and cache precision—not one configuration progressing up a leaderboard.

The recorded ROCm 10.1 engine is `1.1.0-rc1.vllm0.30.0` (vLLM 0.30.0; PyTorch 2.12.0+rocm10.1 in the recorded matrix). The later standalone [radiance engine](RADIANCE.md) is a separate stack. [Compare their evidence](RADIANCE-VS-VLLM.md).

## Checkpoints, revisions and quant types

The campaigns moved across four target checkpoints and one drafter. Revisions are
recorded verbatim from the exports.

| Checkpoint | Revision | Quant | Used in |
|---|---|---|---|
| `ukisai/Swift-1.5-Qwen3.8-27b-INT4` | `81a28ee75eb1cd469f209813a368a79a7e3db3bc` | AWQ+GPTQ INT4 hybrid (GDN) | 18 Oct single/dual matrix; single-card config |
| `ukisai/Swift-1.5-Qwen3.8-27b-W4A16-AWQ` | `9dba8a05877150d587215a519ce6befec3c9978a` | AWQ INT4 W4A16 | 19 Oct spec campaign + sweep (Y/Z arms) |
| `amd/Qwen3.8-27B-Quark-AWQ-MXFP4` | `5233554c5fa56afda40150556b95573c2d7d29c0` | Quark MXFP4 W4A8 | 19 Oct spec campaign + sweep (B/V/W/X arms) |
| `ethanwtodd/Swift-1.5-Qwen3.8-27b-Quark-RTN-MXFP4` | `459bc7fe8340e75dbd22701692db909e21917dc7` | Quark MXFP4 RTN W4A8 | 19 Oct spec campaign + sweep (S/T/U arms, E1) |
| `tcclaviger/Qwen3.8-27B-DFlash2-FP8` | — | FP8 drafter | DFlash2 K7 speculative lane only |

The INT4 checkpoint is the primary research target behind the single-card RAM16
milestone. The Swift-Quark RTN MXFP4 target belongs to the later sweep; its RTN weights must not be described as AWQ. Sources: [model inventory](MODELS.md), [initial model campaign](../data/rocm-10.1/dual-r9700-spec-campaign-2026-10-19.csv), [agent-count sweep](../data/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.csv).

## Configuration by campaign

These are deployment profiles, not an isolated A/B. The 131,070-token ceiling is a
configured limit; it does not establish that every agent sustained the full context
simultaneously.

| Campaign | TP | Context | Slots | Spec | KV | CPU tier | gpu-util |
|---|---:|---:|---:|---|---|---|---:|
| 18 Oct single (GPU A) | 1 | 131070 | 4 | MTP 4 | FP8 | 10 GiB ARC | 0.98 |
| 18 Oct dual | 2 | 168000 | 8 | MTP 8 | FP8 | 10 GiB ARC | 0.98 |
| 19 Oct spec + sweep | 2 | 131070 | 4 | non-spec / MTP K4 / DFlash2 K7 | **BF16** | 10 GiB ARC | 0.98 |

All 19 Oct cells also fixed `max-num-batched-tokens 16384`,
`long-prefill-token-threshold 2048` and prefix caching. Note the 19 Oct sweep used
**BF16 KV** — it did not test FP8 calibration, so it is a different evidence scope
from the 18 Oct FP8-KV matrix. The single-card INT4 profile is fully recorded in
[`data/rocm-10.1/single-card-gpu-a-configuration.json`](../data/rocm-10.1/single-card-gpu-a-configuration.json).

## One card vs two: the recorded INT4 matrix

These rows all come from the **18 October FP8-KV** deployment family. Single GPU A uses MTP-4 / four slots / 131,070 context; dual uses MTP-8 / eight slots / 168,000. Both use a 10 GiB ARC tier. It is a deployment comparison, not an isolated GPU-count scaling test.

| Agents | Single mean / maximum TTFT | Single mean request decode | Dual mean / maximum TTFT | Dual mean request decode |
|---|---:|---:|---:|---:|
| 1 | 7.46 / 18.78 s | 40.0 tok/s | 5.19 / 12.66 s | 45.4 tok/s |
| 2 | 11.92 / 40.64 s | 32.4 tok/s | 6.36 / 22.34 s | 26.9 tok/s |
| 3 | 71.46 / 456.19 s | 26.0 tok/s | 7.74 / 25.56 s | 18.3 tok/s |
| 4 | 101.38 / 654.91 s | 25.5 tok/s | 10.85 / 27.23 s | 16.4 tok/s |

Source: [single/dual follow-up CSV](../data/rocm-10.1/follow-up-single-vs-dual-text-growth-2026-10-18.csv), gpu-a and dual n1–4. At four agents the dual deployment has **89.3% lower mean TTFT**, alongside a **35.7% lower request decode estimate**. Different dimensions favour different profiles. Single-card preemptions are 0/0/7/12; dual records zero in all four cases in the [acceptance report](FINAL-REPORT-20261018.md). Dual-phase swap usage rose from 0.37 to 1.07 GiB.

![Single vs dual mean time to first content](../graphs/rocm-10.1/follow-up-single-vs-dual-mean-ttft-2026-10-18.svg)

**Useful range observed:** one to two deep-context agents on the recorded single-card ROCm 10.1 profile; three to four develop long waits. The historical ROCm 7.14 **RAM16** runs record 13.34/16.88 s mean TTFT at three/four agents, but use different settings and histories. A later 16 GiB tier caused severe host slowdown. Those results are retained context, not a recommendation to enlarge the current tier. [Historical comparison](ROCM-VERSIONS.md).

## What PP and TG can tell you

TTFT includes queueing and recovery. The matrix's `mean_request_decode_tokens_s` is a reported short-response request estimate, not fleet productivity. In the later sweep, `decode_tokens_s` means total output ÷ whole-cell wall, while `turn_tg_avg` means the mean of valid request generation estimates. Those denominators must not be substituted for one another.

**Raw kernel PP is unavailable as a validated matched comparison.** `pp_effective_ingest_tok_s` includes cache reuse through prompt tokens ÷ TTFT. The sweep cache-hit proxy counts zero-TTFT turns and is not token-level cache efficiency. Missing/zero depth-band samples do not mean zero latency. [Full dictionary and formulas](DATA-DICTIONARY.md).

## The model sweep and the recommendation

The 19 Oct sweep is 41 cells, 1,160 turns, zero client errors, eight engine boots
([`dual-r9700-agent-count-sweep-2026-10-19.csv`](../data/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.csv)).
Whole-cell wall seconds at one to four agents (ten turns per agent):

| Target · lane | n=1 | n=2 | n=3 | n=4 | + images |
|---|---:|---:|---:|---:|---:|
| Swift-Quark RTN · non-spec (S) | 134.2 | 203.7 | 264.7 | 372.8 / 439.0 | 537.1 |
| Swift-Quark RTN · MTP K4 (T) | 94.9 | 179.3 | 244.2 | 406.6 | 664.6 |
| Swift-Quark RTN · DFlash2 K7 (U) | 95.8 | 171.4 | 328.4 | 969.2 | 1674.9 |
| Quark AWQ · non-spec (V) | 130.1 | 213.0 | 270.9 | **330.4** | **463.4** |

**The recorded campaign selected Swift-Quark RTN MXFP4, non-spec, for four-agent service (S4/S6; E1 reference).** This selection included the author's output-style preference; the fastest observed four-agent cell was **AMD Quark AWQ non-spec V4, 330.4 s**, compared with Swift-Quark's 372.8/439.0 s repeats. There is no blinded quality test proving the preferred checkpoint better. The measured speculation pattern varies with concurrency: DFlash2 records ≈930–970 s at n4 on both tested MXFP4 targets, and MTP at n=4 is target-dependent (near-parity on Swift-Quark,
a 1.9× longer wall on the Quark base, W4 628.0 s). The Quark base is the fastest n=4
cell (V4 330.4 s) — an observed setup difference with boot-pool variation, a separate result from the recorded checkpoint preference.

**Limits that keep this contextual:** mostly single observations, with Swift-Quark n4 repeat references at 372.8 / 439.0 / 439.6 s. The roughly 15% spread is descriptive variability, not a statistical threshold for other configurations; depth is capped at 126k; **KV pool size also varies** (2.61–4.30× in this sweep, recorded as full-context capacity equivalents) and is not isolated from speculation; BF16 KV
throughout; vision/Falling-Blocks cells are seed-sensitive. This is a setup
comparison, not a causal isolation of any single knob.

## Real coding agents: Falling Blocks

Four concurrent agents (seeds 100–103) each built a Falling Blocks game.
[`falling-blocks-fleet-outcomes-2026-10-18.csv`](../data/rocm-10.1/falling-blocks-fleet-outcomes-2026-10-18.csv):

- **Dual card** — 4/4 clean exits, all artefacts, wall 30:10, original 32,768-token / 3,600 s budgets.
- **Single-card first attempt** — 3/4 delivered; agent 0 (seed 100) hit the 32,768-token cap in reasoning with zero tool calls and produced no files (a silent "success").
- **Single-card retry** — 4/4 clean, wall 75:23, after raising per-request output to 65,536, correcting context to 131,070, compaction reserve to 67,584, and the per-agent cap to 5,400 s. Seed 100 then completed a full verified game.

All eleven produced games passed the reported `vm.Script` syntax check and the
mocked-DOM behaviour probe (movement, rotation, pause, hard-drop, reset, line clear)
— 11/11 with a confirmed line clear. These are not full browser qualification, and a
single fleet per profile does not establish that hardware changes model competence.

![Model and speculative-lane sweep](../graphs/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.svg)

[Detailed sweep report](DUAL-R9700-SPEC-CAMPAIGN.md) · [Full matrix and fleet results](FINAL-REPORT-20261018.md) · [Historical overview](../HISTORICAL-OVERVIEW.md).

## Standing caveats

Single host (2× R9700 32 GiB, custom kernel, P2PDMA patch); GPU B has no single-card
baseline. The 10 GiB tier is kept deliberately — a 16 GiB tier previously made the
host crawl. No tested current single-card configuration establishes smooth 3–4-agent
service at full 131k; the recorded dual deployment avoids the single-card long-wait pattern in this matrix.
The selected results here are contextual to this hardware, these budgets and these
workloads — do not generalise them silently.

<!-- NAVIGATION START -->

[Home](../index.md) · [Compare](RADIANCE-VS-VLLM.md) · [radiance](RADIANCE.md) · [Charts](CHARTS.md) · [Stuff for nerds](CODE-CORNER.md) · [Disclosure](REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
