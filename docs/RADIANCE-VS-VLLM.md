---
layout: default
title: "radiance vs radiance-vllm: what actually changes"
---

# radiance vs radiance-vllm: what actually changes

## The engines

**radiance-vllm** is the old stack: a vLLM fork shipped as a `vllm-radiance:*` container, metrics under the `vllm:*` families. It loads weights from a Hugging Face layout — boot takes minutes, weights first — and publishes CPU KV offload as a fill percentage plus store/load byte counters. Prefix caching ran as a 10 GiB ARC tier; MTP K4 drafting came from `--speculative-config`.

**radiance** is the new engine: `stilldeadcode/radiance` 1.9.0, digest-pinned, loading converted `.rad` bundles, metrics under `radiance:*`. It publishes steady-window gauges — `prefill_tokens_per_second` and `decode_tokens_per_second` — and splits prompt intake into counters. Every number on this page traces to [the campaign export](../data/rocm-10.1/radiance-campaign-2026-10-21.csv) and [the fleet export](../data/rocm-10.1/radiance-falling-blocks-fleet-2026-10-21.csv).

## What the metric vocabulary change means for monitoring

The fill gauge is gone. `radiance` reports intake as one number and splits it with counters: `prefill_tokens_total` is GPU recompute; `attn_cached_tokens_total` and `linear_cached_tokens_total` are cache-served. Under n=4 load I measured intake at 8,648 tok/s = 1,690 recompute + 6,958 cache-served. Monitoring now means reading rates, not a dial. The RAM tier has no fill gauge at all: counters only — `prefix_hit_cut_tokens_total`, `prefix_cache_evictions_total`, and `prefix_cache_ckpt_evictions_by_reason_total {reason="retention"|"store_full"}`. The `store_full` reason is the eviction signal that matters.

## KV and tiers

Live KV lives only in the GPU pool: 524,304–524,336 tokens (FP8) at TP2 — 4×131k at 18.6 KiB/token. The RAM tier is deeper but stores *finished* conversations, not live KV. Pinned host pages are capped by the driver's `ttm.pages_limit` (15.29 GiB here), so on this 30 GiB host the prefix tier tops out at about 13 GiB. No disk tier exists; RAM is the deepest published tier.

Pool ÷ agents sets the depth cap: 4 → 131k, 5 → 104.8k, 6 → 87.4k; 6×131k is impossible (14.5 GiB KV vs 9.74 GiB pool).

## Drafter rules

The `.rad` conversion carries the MTP head (verified: `mtp_num_hidden_layers 1`). `RADIANCE_SPECULATIVE_CONFIG` takes MTP *or* DFlash2 — never both. With spec on, `/server_info` reports `drafter:"mtp" kind:"serial" depth:4`. Measured draft acceptance on the campaign workload: 0.657 mid-run, 0.679 final.

## Operational deltas

- **Startup budget checks.** The engine aborts fast, with arithmetic, when host allocations exceed budget: available RAM minus tier, checkpoint slots and arenas must cover pinned towers plus `--host-headroom-mib` (default 4 GiB). A 16 GiB tier boot died in this check with the exact shortfall printed. The vision tower (1.72 GiB pinned) and 144 MiB checkpoint slots (store capped at 1/8 of host RAM, 24 slots ≈ 3.4 GiB) are budget-checked too.
- **Cold-boot device race.** `kfd` registers the second card late, so `--tp 2` aborts in under a second with "1 device usable". The unit needs a delayed start plus `Restart=on-failure`. vLLM never hit this — it spends minutes loading weights before it touches a device.
- **Gating.** `/metrics` and `/v1/models` are bearer-gated (keyless on my LAN); `/health` is open. `/server_info` exposes drafter, depth, KV, version — there is no `--version` flag.
- **Page-cache warming is a boot-time tool.** With the engine resident (24 GiB), a 17.4 GiB model file warms in 11 s, reclaimed to ~0% within minutes. Boot order: warm (11 s) → engine (UP +40 s).

## Measured deltas

Same client, byte-identical harness, same checkpoint (the vllm-radiance fork). Wall seconds, lower is better:

| Cell | radiance non-spec | old non-spec | radiance MTP-4 | old MTP-4 |
|---|---:|---:|---:|---:|
| n=1 | 130.6 | 126.7 | 102.3 | 115.1 |
| n=2 | 232.1 | 212.1 | 204.7 | 231.6 |
| n=3 | 327.0 | 306.4 | 300.5 | 323.1 |
| n=4 | 429.3 | 401.8 | 402.7 | 488.7 |
| n=4 vision | 685.7 | 651.9 | — | — |

[Machine-readable export](../data/rocm-10.1/radiance-campaign-2026-10-21.csv)

Read:

- Non-spec, radiance trails the old engine at every n (3.1–9.4%) — inside seed noise, not separable.
- MTP-4 beats the old engine's MTP arm at every n (−7% to −18%) and radiance non-spec at every n; at n=4, 402.7 lands on the old non-spec wall (401.8).
- Per-agent decode at n=1: 54.4 tok/s non-spec, 137.9 with MTP-4 (2.5×); aggregate 19.61 vs 10.33 (+90%).
- TTFT by depth band (mean, s): 8.32 vs 11.79 (n=1, 60–90k, −30%); 10.19 vs 22.77 (n=2, 90–120k, −55%); 10.37 vs 29.08 (n=3, 90–120k, −64%).
- Shallow-band caveat: first-turn TTFT on warm prompts ran 11.97–14.32 s vs 0.0–1.78 s on the old engine — prefix-cache admission, not compute.
- Fleet: 4/4 delivered games, 4/4 node-syntax PASS; prefix-cache hit share 80.1–94.3%.

## Caveats

- Single host: 2× R9700 32 GiB, 30 GiB RAM, custom kernel. Numbers do not generalize silently.
- Baseline re-validation on the old engine was not run (user decision; recorded); comparability is workload-to-workload, not a fresh baseline.
- The engine reports 1.9.0 at the pinned digest; the onboarding docs I reviewed were 1.8.1-era.
- FB/vision cells are seed-sensitive (inherited campaign finding).
- 13 GiB tier A/B (R9) is within seed noise; tier growth is justified by fleet pressure (570 `store_full` refusals on 10 GiB), not the single-cell grid.

<!-- NAVIGATION START -->

[Home](../index.md) · [Overview](../README.md) · [Latest campaign](RADIANCE-CAMPAIGN-2026-10-21.md) · [Charts](CHARTS.md)
