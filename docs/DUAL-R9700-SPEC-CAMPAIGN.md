---
layout: default
title: "Dual R9700 model and spec-decode campaign (19 October 2026)"
---

# Dual R9700 model and spec-decode campaign (19 October 2026)

A follow-on campaign on the dual Radeon AI PRO R9700 pair (TP=2) that
onboards one new checkpoint and measures every published speculative-decoding
lane against plain batched decoding on long-context agent load. It runs
alongside — and partly contradicts — the fast-lane numbers published by the
engine project; see [Contradiction with the published fast lanes](#contradiction-with-the-published-fast-lanes).

## Initial eight-cell campaign: scope and configuration

Fixed knobs across all eight cells: TP=2, `max-model-len 131070`,
`max-num-seqs 4`, `max-num-batched-tokens 16384`,
`long-prefill-token-threshold 2048`, prefix caching, bf16 KV (no FP8 KV),
10 GiB ARC CPU KV tier, gpu-utilization 0.98. Reference bench: four
concurrent coding agents, 10 turns each, 126k depth cap, greedy sampling.
Engine `vllm-radiance:rocm10` (radiance 1.1.0-rc1.vllm0.30.0), ROCm 10.1.
One run per cell.

Targets: `ukisai/Swift-1.5-Qwen3.8-27b-W4A16-AWQ` (AWQ INT4 W4A16),
`amd/Qwen3.8-27B-Quark-AWQ-MXFP4` (Quark MXFP4 W4A8), and the onboarded
`ethanwtodd/Swift-1.5-Qwen3.8-27b-Quark-RTN-MXFP4`. Speculative lanes:
MTP K4 (target-native head) and DFlash2 K7
(`tcclaviger/Qwen3.8-27B-DFlash2-FP8`, V2 model runner, PIECEWISE graphs,
TRITON_ATTN draft attention, 8192-token drafter window).

## Results

[Machine-readable export](../data/rocm-10.1/dual-r9700-spec-campaign-2026-10-19.csv)
(all eight cells, 40/40 turns, zero client errors each).

| Cell | wall_s | decode tok/s | mean TTFT s | max TTFT s | KV pool |
|---|---:|---:|---:|---:|---:|
| B2 Quark MXFP4 · non-spec | 420.8 | 17.04 | 16.80 | 56.95 | 4.38× |
| E1 Swift-Quark RTN · non-spec | 439.6 | 16.96 | 14.67 | 52.60 | 3.98× |
| A2 Swift W4A16 · non-spec | 484.3 | 12.67 | 23.19 | 72.76 | 4.32× |
| A1 Swift W4A16 · MTP K4 | 495.4 | 16.17 | 23.19 | 68.49 | 3.52× |
| B1 Quark MXFP4 · MTP K4 | 707.6 | 10.96 | 36.56 | 221.7 | 3.02× |
| E3 Swift-Quark RTN · DFlash2 K7 | 862.1 | 8.73 | 52.97 | 249.66 | 2.69× |
| B4 Quark MXFP4 · DFlash2 K7 | 911.7 | 7.75 | 57.52 | 427.14 | 2.69× |
| E2 Swift-Quark RTN · MTP K4 | 931.3 | 7.45 | 67.25 | 505.56 | 3.02× |

## Findings

- **Non-speculative decoding wins the initial four-agent campaign on every target.** On this workload every
  speculative lane loses turn throughput to plain batched decoding on the
  same weights: E1 439.6 s vs E2 931.3 s (MTP) and E3 862.1 s (DFlash2).
- **The KV pool is the dominant predictor.** Wall time tracks pool
  concurrency almost monotonically; the draft pool's reservation (MTP
  ≈126–179k tokens, DFlash2 ≈222k) pushes the pool below the 524k that four
  full-depth agents need, and preemption cascades dominate the deep bands
  (90–120 k TTFT: 152–172 s mean, up to 505 s).
- **Speculative bursts are real and not usable at depth.** DFlash2 rows show
  single-request decode of 119–171 tok/s with ~0–61 ms TP99 ITL when drafts
  are accepted — while co-resident agents starve. Per-request speed does not
  convert to fleet throughput at batch 4 (A1 vs A2: +27% per-request decode,
  wall unchanged).
- **Acceptance depends on the target.** Live counters during E3 measured
  ~39.4% draft acceptance (K7) for the base-trained drafter on the Swift
  finetune; E3 finished 49.6 s faster than B4 on the base target.
- **New checkpoint onboarded: Swift in the Quark MXFP4 container.**
  `ethanwtodd/Swift-1.5-Qwen3.8-27b-Quark-RTN-MXFP4` (rev `459bc7fe`)
  replicates the winning AMD checkpoint's Quark metadata exactly
  (identical `quantization_config`, 127-entry exclude list, 1695-tensor
  inventory) and serves on the same `RadianceMxfp4W4A8` kernels. Its weights
  are RTN, not AWQ, by author documented decision (the AWQ smoothing recipe
  produced pathological per-layer scales on this finetune; layernorms are
  restored from the BF16 base). Author GSM8K: 95.75% thinking-strict. Our
  smoke checks preserve the finetune's generation style. E1 delivers
  campaign-best mean TTFT (14.67 s) with decode equal to the champion
  (16.96 vs 17.04 tok/s).

## Contradiction with the published fast lanes

The engine project publishes fast-lane numbers on its own benchmark
(non-spec 53.9, MTP K4 135.6, DFlash2 K5 172.3, DFlash2 K7 186.7 weighted
tok/s), qualified at **8K context, concurrency 8, FP8 KV, on FP8/MXFP4
targets**. Our cells run **126k depth, 4 agents, bf16 KV** — outside that
envelope. On our envelope the ordering inverts: the published fastest lane
(DFlash2 K7) is among the slowest here, and non-spec — the published
baseline — is fastest. This does not establish that the published numbers
are wrong in their envelope; it establishes that **they do not transfer to
long-context agent load on this hardware**, and that the engine's own
qualification note ("non-spec recommended; DFlash2 qualified at 8K/C8") is
load-bearing for exactly this reason.

This campaign did not reproduce the published numbers exactly: the
project's benchmark harness is not shipped in the image (verified by
filesystem search). A shallow-zone reproduction with our own agent bench
measured the same Quark lanes at **16K context, 8 agents** — the literal
8K/C8 envelope is infeasible with this harness (its fixed system+task
prompt is ~7.9k real tokens, so turn 1 alone overflows an 8192-token
context; recorded as a gate-fail, not a cell). In the shallow zone MTP had lower observed wall time (81.9 s vs 93.5 s, a 12.4% reduction), but this lies inside the ≈15% repeat-spread floor. The deep campaign pair favoured non-spec (420.8 s vs 707.6 s). Context, concurrency, turn count and pool changed together: this is an observed ordering difference, not an isolated depth effect or a robust reproduction claim. [Shallow cells R1/R2](../data/rocm-10.1/dual-r9700-8k-repro-2026-10-19.csv) and [deep cells B1/B2](../data/rocm-10.1/dual-r9700-spec-campaign-2026-10-19.csv).
[Chart: lane transfer 16K vs 126k](../graphs/rocm-10.1/dual-r9700-lane-transfer-16k-vs-126k.svg)
· [Shallow-zone cells](../data/rocm-10.1/dual-r9700-8k-repro-2026-10-19.csv)
(DFlash2 arms at 16K were cancelled by scope decision; two cells per side
of the inversion are measured).

## Agent-count scaling, prompt processing, and vision input

All eight engine setups — three targets (Swift-Quark RTN MXFP4, Quark AWQ
MXFP4, Swift W4A16 AWQ) × lanes (non-spec, MTP K4, and DFlash2 K7 on the
two MXFP4 targets) — were swept at 126k depth: 1, 2, 3, and 4 concurrent
agents (10 turns each), plus a synthetic vision-input run that injects one
procedural 512×512 PNG per turn per agent (failing-game-UI screenshots as
multimodal input), plus a repeat of the 4-agent point on the serving
checkpoint. **41 cells, 1,160 turns, zero errors, eight engine boots,
zero crashes.** **Prompt ingest rate** is prompt tokens ÷ TTFT over
non-cached turns — an *effective* client-side rate that includes
prefix-cache reuse (the cached prefix is not recomputed, so this exceeds
the GPU's kernel prefill rate by design); `prefix_cache_hit_frac` is the fraction of turns with TTFT recorded as 0.00 s, used as a cache-hit proxy; it does not independently measure token-level cache reuse. The earlier handover estimated kernel prefill near 750–850 tok/s. These client-side fields do not measure that rate directly, so no kernel-throughput claim is derived from this export.

[Machine-readable export](../data/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.csv)
· [Chart: scaling and PP](../graphs/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.svg)

Wall seconds per cell (lower is better; every cell carries decode, TTFT,
depth-band, ingest, and KV-pool columns in the CSV):

| Target · lane | n=1 | n=2 | n=3 | n=4 | Falling Blocks |
|---|---:|---:|---:|---:|---:|
| Swift-Quark MXFP4 · non-spec | 134.2 | 203.7 | 264.7 | 372.8 / 439.0 | 537.1 |
| Swift-Quark MXFP4 · MTP K4 | 94.9 | 179.3 | 244.2 | 406.6 | 664.6 |
| Swift-Quark MXFP4 · DFlash2 K7 | 95.8 | 171.4 | 328.4 | 969.2 | 1674.9 |
| Quark AWQ MXFP4 · non-spec | 130.1 | 213.0 | 270.9 | **330.4** | **463.4** |
| Quark AWQ MXFP4 · MTP K4 | 116.4 | 175.6 | 264.4 | 628.0 | 1385.2 |
| Quark AWQ MXFP4 · DFlash2 K7 | 97.6 | 177.6 | 253.9 | 931.7 | 1609.0 |
| Swift W4A16 · non-spec | 126.7 | 212.1 | 306.4 | 401.8 | 651.9 |
| Swift W4A16 · MTP K4 | 115.1 | 231.6 | 323.1 | 488.7 | 802.9 |

- **Speculation is a low-concurrency option, with target-specific gains.**
  Swift-Quark MTP/DFlash2 at n=1 measured 94.9/95.8 s against 134.2 s non-spec (T1/U1 vs S1). At n=2 the reductions were 12.0%/15.9% (T2/U2 vs S2); the MTP difference is below the repeat-spread floor. On W4A16, MTP at n=2 was slower, 231.6 vs 212.1 s (Z2 vs Y2). Do not claim a universal 25–30% gain across targets and agent counts.
- **Full-load operation favours non-spec as the default.** Quark's n=4 non-spec cell was 330.4 s, against 628.0 s MTP and 931.7 s DFlash2 (V4/W4/X4). On Swift-Quark, MTP at 406.6 s lies within the non-spec repeat spread (372.8/439.0 s); its rank is unresolved. DFlash2 at 969.2 s is clearly slower (U4). These are setup comparisons, not a causal isolation of speculation.
- **MTP's n=4 behaviour is target-dependent.** Swift-Quark rides MTP to
  near-parity at n=4 (406.6 vs 372.8 s); on the Quark base the same K4
  collapses to 628.0 s (1.9× its non-spec), and on W4A16 MTP loses too
  (488.7 vs 401.8). Same MTP depth, different targets and boot pools (3.32× / 2.94× / 3.44×); this export does not isolate acceptance from capacity.
- **The DFlash2 K7 cliff is target-independent.** At n=4 both targets
  land ~930–970 s with ingest collapsing to ~930–970 tok/s (deep bands
  ~630); at n=3 the base target handles it (253.9 s, even beating its
  non-spec 270.9, a gap below the repeat-spread floor) while Swift-Quark is slower (328.4 vs 264.7). The recommendation is to reserve DFlash2 for low-concurrency use on this profile.
- **Vision penalises speculation hardest.** On Quark, FB wall goes
  463.4 → 1385.2 → 1609.0 s (non-spec → MTP → DFlash, 3.0–3.5×); on
  Swift-Quark 537.1 → 664.6 → 1674.9. Image prefill + draft tax + pool
  pressure compound.
- **W4A16 pays a decode tax**: 10.3–19.8 tok/s vs 16–23 for the MXFP4
  lanes — these are different quantisation/kernel paths, not a generic claim that one INT4 bit width is smaller than another. It stays
  competitive at n=1 (115.1 s with MTP is the fastest single-agent cell
  of its target) and trails at n≥3.
- **Per-agent decode is nearly flat with concurrency** (16.6 → 24.9
  tok/s on the non-spec lanes): the box is weight-bandwidth-bound at
  these batch sizes, so wall time grows sublinearly (1.97× for 3×
  agents) and fleet throughput rises with concurrency.
- **Effective prompt ingest collapses with queueing**: 6,019–8,381 tok/s
  single-stream → 1,885–3,848 at four agents on healthy lanes (client-side
  rate; the kernel rate is the ~750–850 tok/s above — the gap is prefix
  caching doing its job). Ingest rises within each run's depth bands
  (bigger prefills amortise scheduling).
- **Repeat spread on the 4-agent point**: 372.8 / 439.0 / 439.6 s
  (E1) — a 15% spread; single-run gaps below ~15% on this box are not
  separable.
- **The vision lane is seed-sensitive.** The W4A16 FB run (651.9 s) drew
  a short-turn, shallow-depth agent profile (mean TTFT 2.77 s, 95%
  cache hits, deep bands empty, tg 9.1) where the Quark FB runs drew
  deep ones. Compare each vision cell with its n=4 text twin in the same lane; even that difference includes changed histories and cache reuse, not only image computation.

## Vision increments and depth-band coverage

![Vision cell minus its n=4 text twin](../graphs/rocm-10.1/dual-r9700-vision-increment-2026-10-19.svg)

Quark's observed increments were +133.0 s (+40.3%) non-spec, +757.2 s (+120.6%) MTP and +677.3 s (+72.7%) DFlash2 (V5−V4, W5−W4, X5−X4). Swift non-spec is +44.1% using S4, or +22.3% using repeat S6. These are history-sensitive workload increments, not isolated vision-kernel costs. [Sweep source](../data/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.csv).

![TTFT means by context band for all sweep cells](../graphs/rocm-10.1/dual-r9700-depth-band-ttft-2026-10-19.svg)

A blank or zero no-sample band is shown as a dash. No deep observations does not mean zero deep-context latency. These synthetic PNG-input cells are not new game-building fleets.

## Serving outcome

The measured recommendation for four-agent service is
`swift-quark-mxfp4` at `131070 / 4 / non-spec` — the onboarded checkpoint on
the winning kernel path, with the style probe confirming the Swift
writing style survives the quantisation. The full sweep adds one fact:
the Quark base target on the same non-spec lane is the fastest cell at
n=4 (330.4 s) and on vision (463.4 s) — this is an observed setup difference, with boot-pool variation and limited replication. The
onboarded checkpoint stays Swift-Quark for output-style reasons; the
systemd unit and the INT4 service definition were not modified; swapping
the live service is an operator decision, and rollback remained one
command throughout.

## Limits

Source files and SHA-256 hashes for all six generated charts are in the [chart provenance manifest](../graphs/rocm-10.1/dual-r9700-spec-chart-sources.json).

One run per cell (the n=4 serving point has two repeats; the campaign
E1 arm has one): the 15% repeat spread is the resolution floor, so
same-lane gaps below ~15% are not separable. Depth is capped at 126k by
the harness. `turn_tg_avg` in the CSV is a per-turn mean that includes
accepted-draft bursts and is not comparable to `decode_tokens_s`. BF16
KV throughout (FP8 KV is a separate calibration axis, not tested here).
Falling Blocks cells are seed-sensitive (see the W4A16 anomaly above)
and are used for lane ranking, not absolute numbers. KV pool size varies
by boot (2.61–4.30×) and is the master variable for same-lane wall
swing. Arm C (FP8-dynamic) and arm D (NVFP4→MXFP4 conversion) were
excluded as gate-fails; reasons in [Excluded exploratory tests](EXCLUDED-TESTS.md).

<!-- NAVIGATION START -->

[Home](../index.md) · [Overview](../README.md) · [Latest campaign](RADIANCE-CAMPAIGN-2026-10-21.md) · [Charts](CHARTS.md)
