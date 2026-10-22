---
layout: default
title: "Performance standards: radiance pp/tg against collected data"
---

# Performance standards: radiance pp/tg against collected data

The question: radiance publishes speed cards on the same two R9700s; the collected campaign data measures pp (prompt processing) and tg (token generation) on vllm-radiance. Are the standards comparable, and what does an aligned comparison show?

**Short answer:** radiance's published tg numbers are at ~768-token prompt depth; the collected data is chiefly a 126k-deep memory-pressure test. At **comparable depth** the engines land in the same band; at **the campaign's depth** radiance's card numbers do not transfer. radiance publishes **no 27B prefill numbers**, so pp-vs-pp against the collected data cannot be settled from documents — it requires a run.

## 1. Conventions, mapped

Three harnesses, three conventions. Per [the data dictionary](../DATA-DICTIONARY.md), the collected `decode_tokens_s` (per-request steady-state decode) and `turn_tg_avg` (per-turn mean including accepted-draft bursts) must not be compared to each other; the same discipline applies across engines.

| Quantity | Collected campaign CSVs | vllm-radiance BetterBench | radiance |
|---|---|---|---|
| pp (executed prefill) | `pp_effective_ingest_tok_s` = (prompt + cache) over ingest window — **includes prefix-cache credit** | "cold prefill TPS" (prompt tokens / TTFT, cold nonce prompts) | `prompt_per_second` in per-request `timings` = **executed prefill only**; `prefill_tokens_per_second` metric |
| pp (effective, cache-credited) | `pp_effective_ingest_tok_s` with `prefix_cache_hit_frac` alongside | — | `(prompt_n + cache_n) / ttft_ms` from `timings` (documented fields; compute client-side) |
| tg (burst/per-turn) | `turn_tg_avg` | weighted TPS, ITL 1%-low TPS; concurrency TPS (aggregate) | `predicted_per_second` (counts every accepted token, first token excluded) |
| tg (steady decode) | `decode_tokens_s` | ITL low TPS | `decode_tokens_per_second`; step-time ratios via `engine_step_seconds_decode_total / engine_steps_decode_total` |
| Queue/pressure | `ttft_*` bands, preemptions | TTFT p50 | `ttft_ms` (server-side, from body-complete to first token, includes admission wait), `num_requests_preempted` |

The vllm-radiance fork's metrics are vLLM's; radiance deliberately ships a `vllm:`-compatible Prometheus family, so existing dashboards map 1:1 for `time_to_first_token_seconds`, `time_per_output_token_seconds`, `prompt_tokens_total`, `generation_tokens_total`, `num_preemptions_total`, `gpu_prefix_cache_hit_rate`.

## 2. Published numbers, side by side (all 2× R9700, gfx1201)

### radiance official container cards

Greedy, eight prompts (prose, code, explanation, JSON, Rust, German, two with reasoning), 768 tokens each, DFlash2 depth 7, `--max-num-seqs 8 --max-model-len 200000 --kv-cache-dtype fp8`:

| Container | 1 stream | prose / code | 4 streams (total) |
|---|---:|---:|---:|
| `qwen3.8-27b-mxfp4.rad` TP1 | 122 | 77 / 164 | 280 |
| `qwen3.8-27b-mxfp4.rad` TP2 | **204** | 130 / 285 | **438** |
| `qwen3.8-27b-fp8.rad` TP2 | 141 | 93 / 184 | 314 |

Prefill figures radiance does publish are for **Qwen3.8-Flash-Next (MoE), not the 27B**: 2706 tok/s at a 2048-token chunk (TP2); a 20K prompt at 5556 tok/s (exact wire) → 5908 (wht6); a 23K extension at 81K depth 4998 → 5278; a 185,253-token prompt in 91 s (~2036 tok/s).

### vllm-radiance (magiccodingman) publication, same Quark MXFP4 target

BetterBench v0.2.2 / corpus v1, TP2, FP8 KV, 8K/C8, 85% allocation, prefix off:

| Mode | Weighted TPS | c1 | c2 | c4 | c8 | Cold prefill (2K/4K/7K) |
|---|---:|---:|---:|---:|---:|---|
| Non-spec (recommended) | 53.9 | 64 | 101.8 | 181.4 | 304.1 | 4056 / 4480 / 4367 |
| Fast MTP K4 | 135.6 | 67 | 128.7 | 227.3 | 360.2 | 4239 / 4531 / 4348 |
| Fast DFlash2 K7 | 186.7 | 173.5 | 293.7 | 446.6 | 510.2 | 4044 / 4457 / 4281 |

### Collected campaign data (this repository)

Dual TP2 FP8 KV, 126k depth cap, engine `1.1.0-rc1.vllm0.30.0` ([spec campaign](../../data/rocm-10.1/dual-r9700-spec-campaign-2026-10-19.csv), [agent sweep](../../data/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.csv), [8k repro](../../data/rocm-10.1/dual-r9700-8k-repro-2026-10-19.csv)):

| Arm (model / mode) | Agents / depth | `decode_tokens_s` (per req) | `turn_tg_avg` | pp note |
|---|---|---:|---:|---|
| Swift-Quark RTN MXFP4 nospec | 1 / 126k | 16.64 | 77.3 | pp_eff 7454 (hit 0.40) |
| Swift-Quark RTN MXFP4 MTP4 | 1 / 126k | 11.92 | 195.8 | — |
| Swift-Quark RTN MXFP4 DFlash2 K7 | 1 / 126k | 15.85 | 147.1 | — |
| Quark AWQ MXFP4 nospec | 4 / 126k | 17.04 | 40.1 | — |
| Swift W4A16 AWQ MTP4 | 4 / 126k | 16.17 | 59.6 | — |
| Quark AWQ MXFP4 MTP4 | 8 / 15k | 50.05 | 34.7 | — |
| Quark AWQ MXFP4 nospec | 8 / 15k | 39.31 | 31.3 | — |
| Swift INT4 (TP1, MTP4, RAM10) | 1–4 / 131k | — | 40.0 / 32.4 / 26.0 / 25.5 | TTFT 7.46→101.38 s |

## 3. tg vs tg, aligned

| Comparison | Depth | Numbers | Reading |
|---|---|---|---|
| radiance MXFP4 TP2 card (204, DFlash2) vs vllm-radiance K7 (186.7 weighted) | shallow (~1k) vs 8K | 204 vs 186.7 | Same weights, same drafter family, comparable harness depth: same band, radiance ~+9%. Different prompt sets and gates; not an isolated engine A/B. |
| radiance 4-stream (438 total ≈ 110/stream) vs collected 8-agent @15k (fleet ≈ 400 MTP4 / 314 nospec) | ~1k vs 15k | 438 vs 314–400 | Fleet-level decode at **comparable (moderate) depth** is the same band across engines and modes. |
| radiance 4-stream (438) vs collected 4-agent @126k (fleet ≈ 68 nospec, `decode_tokens_s` convention) | ~1k vs 126k | 438 vs 68 | The gap is **context depth**, not engine: the campaign's own nospec tg at 126k (77.3 single, 40.1 per-turn at 4) already sits far below any shallow-depth card number. |
| collected 1-agent @126k MTP4 (195.8 `turn_tg_avg`) vs radiance TP2 card (204) | 126k vs ~1k | 195.8 vs 204 | Numerically equal, conventions and depths differ (`turn_tg` includes draft bursts; radiance counts accepted tokens; 126k vs 768-token prompts). A coincidence, not a comparison — and a hint that radiance at 126k depth is the single most valuable measurement to run. |
| radiance TP1 prose 77 vs collected Swift-Quark nospec 77.3 @126k | ~1k vs 126k | 77 vs 77.3 | Same warning: pure coincidence across incompatible conventions. |

**Conclusion:** at any fixed depth the two engines are in the same band; radiance's headline numbers are shallow-depth marketing-grade cards, and the campaign's low tg numbers are deep-context physics. Nothing in the published material establishes a cross-engine tg delta at 126k.

## 4. pp vs pp, aligned

| Source | pp figure | Conditions |
|---|---|---|
| vllm-radiance publication | 4044–4531 tok/s | cold 2K–7K prompts, TP2 Quark MXFP4, prefix off |
| Collected `pp_effective_ingest` | 7454 (1 agent, hit 0.40) → 2795 (4 agents, hit 0.275) | cache-credited ingest; cold component consistent with the 4–4.5k band |
| radiance | **no 27B dense pp published** | Flash-Next MoE only: 2706 (2K chunk), 5556→5908 (20K, wht6), 185K in 91 s |

The collected pp numbers include prefix-cache credit, so they are **not** comparable to radiance's executed-prefill `prompt_per_second` without the `(prompt_n + cache_n)/ttft` conversion. radiance's MoE prefill figures involve a different model (int8 trunk, 512-expert MoE, QSA attention) and a chunk-size lever (2048 is its optimum) — citing them as 27B pp would be a category error.

**Verdict: pp-vs-pp is undetermined from documents.** It is the first thing a real trial must measure, with the campaign's own cold 2K/4K/7K prompts against radiance's `timings`.

## 5. What a valid A/B needs

1. **One model container served by both engines.** The Quark AWQ-MXFP4 checkpoint is the cleanest: the campaign ran it (arms B/V/W/X), the vllm-radiance fork qualifies it, and radiance serves it byte-for-byte (`qwen3.8-27b-mxfp4.rad`). The Swift INT4 is the continuity case (your campaign model; radiance converts it, the vllm fork serves it via W4A16).
2. **One harness.** The campaign's synthetic text-growth client (see [BENCHMARKS](../BENCHMARKS.md)) against radiance, reading its per-request `timings` (`prompt_n`, `cache_n`, `prompt_per_second`, `predicted_per_second`, `ttft_ms`) — radiance also ships `scripts/agentreplay.py` for the agent-shaped prefix workload, which is the closest thing to your compaction runs.
3. **Same depth grid** (1k / 15k / 126k), same concurrency (1/2/4), same greedy + nonce discipline, prefix cache matched (the campaign ran prefix-off capacity labs and prefix-on production profiles; radiance defaults prefix cache on).
4. **Read radiance's capacity receipt at startup** (`kv: the pool backs N% ... M full-length sessions`) and its `--max-num-seqs` recurrent-state cost (144 MiB f32 per sequence × 2 copies with speculation) before trusting any tg number; the 27B at 32 sequences on radiance's own docs "holds 2.8 full-length sessions" at FP8 TP2.
5. **Record preemptions and prefix-hit cuts** (`num_requests_preempted`, `prefix_hit_cut_tokens_total`) — the campaign's headline pressure metric (7 and 12 preemptions at 3–4 agents single-card) has a direct radiance counterpart.

Until such a run exists, the defensible statement is: **radiance is a credible replacement whose published numbers are consistent with the collected band at comparable depth, whose deep-context behaviour is unmeasured on this host, and whose pp numbers for the 27B family are unpublished.**

<!-- NAVIGATION START -->

[Home](../../index.md) · [Overview](../../README.md) · [ROCm 10.1 results](../FINAL-REPORT-20261018.md) · [Charts](../CHARTS.md)
