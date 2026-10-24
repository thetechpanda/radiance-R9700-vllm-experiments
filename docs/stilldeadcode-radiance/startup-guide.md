---
layout: default
title: "Startup guide: radiance on the dual R9700"
---

# Startup guide: radiance on the dual R9700

A pre-trial plan derived from radiance's own docs (README, GUIDE, DOCKER, compose files) as of 2026-10-19 (`1.8.1`), mapped onto the recorded host ([Hardware](../HARDWARE.md): Minisforum MS-01, i5, 32 GiB DDR5, 2× R9700 32 GiB, GPU A PCIe 4.0 ×8, GPU B ×4 via OCuLink, Podman per [PODMAN.md](../../PODMAN.md)). Read every command before running it; see the author’s [Security Stance](../../HUMANS.md#security-stance). Nothing below has been executed on this host.

## 0. Go / no-go checks

| Check | Requirement | Recorded-host status |
|---|---|---|
| Kernel driver | `amdgpu` supporting **ROCm 10.1** userspace | The ROCm 10.1 deployment qualifies; the ROCm 7.14 deployment does not run the 10.1 image |
| Resizable BAR | Above 4G Decoding + Resizable BAR on; startup **refuses** a card whose VRAM the CPU cannot reach | Already required by the vllm-radiance deployment |
| P2P / kernel patch | **Not required.** radiance probes peer access at launch and falls back to pinned-host-staged all-reduce where a pair cannot P2P; it reports the choice in the startup report | The [P2PDMA whitelist patch](../../patches/) is a vLLM/RCCL requirement; radiance needs none for boot. GPU B's ×4 host link is the caveat: "cards whose host link is narrower than their peer link pay more" |
| RAM pinning | `memlock` unlimited; driver caps all-process pinning at **RAM − 1/64 − 1.5 GiB** | 32 GiB host ⇒ ~30 GiB total pin ceiling — budget it (§4) |
| Models filesystem | Local filesystem with direct I/O (ext4/XFS/btrfs; btrfs-compressed extents lose O_DIRECT) | Match; use a `chattr +C` directory on btrfs |
| seccomp | io_uring + NUMA syscalls allowed (`seccomp=unconfined`) | Podman default is unconfined; keep it |

## 1. Pin the version, get the image

```sh
# published image (kernels built for gfx1201 = R9700)
podman pull docker.io/stilldeadcode/radiance:latest
# better: after `podman images`, retag to a digest you recorded; 1.8.1 was HEAD at review
```

The image is `FROM scratch` + resolved libs + busybox/curl/jq; it needs no ROCm, compiler or Python on the host. Tools on `PATH`: `radiance`, `rad-convert`, `rad-info`, `rad-kbench`, `rad-tune`, `rad-schemas`, `rad-tokcheck`; recipes in `/opt/radiance/share/radiance/recipes/`. Building your own (`docker/build.sh`, needs buildx) is documented for other GPU targets; unnecessary for gfx1201.

## 2. Get the model

**Fastest valid start — the published MXFP4 container** (same checkpoint as campaign arms B/V/W/X, includes vision + DFlash2 drafter, 18.05 GiB, fits TP1 *and* TP2):

```sh
mkdir -p /srv/models/rad
curl -LC - -O https://huggingface.co/StillDeadcode/qwen3.8-27b-mxfp4/resolve/main/qwen3.8-27b-mxfp4.rad
# requires engine >= 1.2.3 (current 1.8.1 is fine)
```

**Continuity start — convert the campaign model** (Swift 1.5 INT4, see [swift-models.md](swift-models.md)):

```sh
podman run --rm -v /srv/models:/models --security-opt unconfined \
    --entrypoint rad-convert stilldeadcode/radiance \
    /models/hf/ukisai/Swift-1.5-Qwen3.8-27b-INT4 \
    -o /models/rad/swift15-27b-int4.rad \
    --recipe /opt/radiance/share/radiance/recipes/q38-27b-w4a16.recipe --plan-only -v
# drop --plan-only for the real conversion; record the exact engine tag + command
```

Inspect any container before serving: `podman run --rm -v /srv/models/rad:/models:ro --entrypoint rad-info stilldeadcode/radiance /models/<name>.rad`.

## 3. First run (Podman, TP2, both cards)

The compose files' requirements (`deploy/compose/common.yaml`) map 1:1 to Podman flags:

```sh
podman run -d --name radiance \
    --network host --init \
    --ulimit memlock=-1 \
    --device /dev/kfd --device /dev/dri \
    --group-add "$(getent group render | cut -d: -f3)" \
    --group-add "$(getent group video | cut -d: -f3)" \
    --security-opt label=disable --security-opt seccomp=unconfined \
    -v /srv/models/rad:/models:ro \
    --stop-timeout 60 \
    stilldeadcode/radiance \
      --model /models/qwen3.8-27b-mxfp4.rad \
      --host :: --port 8000 --api-key "$RADIANCE_API_KEY" \
      --tp 2 --max-num-seqs 8 --max-model-len 131072 \
      --kv-cache-dtype fp8 --gpu-headroom-mib 96
```

Notes against the upstream compose (which uses `--max-num-seqs 32 --max-model-len 200000`):

- The guide starts at `--max-num-seqs 8 --max-model-len 131072` to match the campaign's 131k/4-agent contract; upstream's 32×200k row is a different (capacity) contract — on the hybrid 27B, 32 sequences pay ~144 MiB × 2 of GDN state each and the docs say FP8 TP2 then "holds 2.8 full-length sessions".
- `--security-opt label=disable` is the Podman/SELinux analogue of the compose mount; on AppArmor hosts it is not needed.
- The image sets `GPU_MAX_ALLOC_PERCENT=100` / `GPU_MAX_HEAP_SIZE=100` itself.
- One model per server, one server at a time: radiance serves a single model and takes both cards by default (`--tp 2`). Stop vllm-radiance before starting radiance — the VRAM budget is measured before allocation, and a card that lost memory to another process mid-startup fails with `pool allocation refused`.
- Stop cleanly: SIGTERM finishes the in-flight step and releases the cards (60 s grace; `scripts/fnstop.sh` is the upstream helper). VRAM is not freed until the process exits.

## 4. Memory budget on the 32 GiB host

radiance pins more host memory by default than the vllm-radiance profile did. The pin ceiling is ~30 GiB (RAM − 1/64 − 1.5 GiB); pinned memory is unswappable (the campaign's dual-phase swap rose to 1.07 GiB — pinned bytes sit outside that).

| Item | Default | Size on 27B | Budget |
|---|---|---|---|
| Token embedding | `--embedding-placement ram` (pinned shard per rank) | 248320×5120 bf16 = 2.37 GiB; 1.18 GiB a card at TP2 (GUIDE §4.3) | ~2.4 GiB pinned |
| Prefix-cache host tier | off | — | `--prefix-cache-mib 10240` mirrors the campaign's 10 GiB ARC tier (finished conversations only — see feature-comparison) |
| Linear-state snapshot store | `--checkpoint-slots auto`, capped at 1/8 RAM (≈4 GiB) and at what the host can pin | 144 MiB per snapshot (f32 state) | auto wants ~10 slots/sequence at 200k; expect "held to an eighth of host memory" on 32 GiB — set `--checkpoint-slots` explicitly (e.g. 24) and watch `prefix_cache_ckpt_evictions_by_reason_total{reason="store_full"}` |
| `--vision-tower-placement` | `vram` (0.86 GiB/card ≈ 24k fp8 KV tokens) | — | `ram` adds ~1.7 GiB pinned (one tower per rank) + per-image link read (~55 ms at ×16; ~110/220 ms at ×8/×4) |
| `--host-pool-mib` (weights tier) | 0 for dense 27B | — | leave 0: the 27B fits VRAM at TP2; the pool is for MoE/expert tiering |

Suggested agent-profile starting point (TP2, MXFP4):

```sh
--tp 2 --max-num-seqs 4 --max-model-len 131072 --kv-cache-dtype fp8 \
--gpu-headroom-mib 96 --prefix-cache-mib 10240 --prefix-cache-ttl 3600 \
--checkpoint-slots 24 --vision-tower-placement ram --api-key "$RADIANCE_API_KEY"
```

## 5. Validate before trusting it

```sh
# 1. startup receipt — read it; paste it into any issue
podman logs radiance | sed -n '/STARTUP REPORT/,$p'
#   DERIVED: VRAM split, KV pool ("kv: the pool backs N% ... M full-length sessions"),
#   weights by tier, kernel rows. FINDINGS: warnings with cost + fix (e.g. link-below-max
#   on the GPU B ×4 path; pin-cap refusals).

# 2. what is loaded
curl -s localhost:8000/server_info | jq '.model, .cards, .kv, .capabilities'
curl -s localhost:8000/props | jq '.modalities'          # vision present?

# 3. kernel correctness on your cards (cards must be free)
podman run --rm --device /dev/kfd --device /dev/dri --security-opt seccomp=unconfined \
    --group-add render --group-add video \
    --entrypoint rad-kbench stilldeadcode/radiance --home /opt/radiance/share/radiance --max-cases 1

# 4. text smoke
curl -s localhost:8000/v1/chat/completions -H "Authorization: Bearer $RADIANCE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"m","messages":[{"role":"user","content":"Reply with OK only."}],"max_tokens":8,"reasoning_effort":"none"}' | jq -r '.choices[0].message.content, .timings'

# 5. vision smoke (base64 data-URL only; the server never fetches URLs)
#    one small PNG in a content part; confirm 200, image tokens counted, tower read in log
```

`--live` (or `radiance --model ... --live`) gives the in-place cards/throughput/acceptance view; redirected it appends greppable `key=value` lines — the closest analogue of the campaign's [radiance-top](../SCRIPTS.md) monitor. The web dashboard (`/`), `/stats`, `/sessions`, `/graph`, `/diagnostics` (loopback-only without a key) complete the observability set.

## 6. Wire the benchmark harness

radiance emits a `vllm:`-compatible Prometheus family — the campaign's TTFT/TPOT/preemption/prefix-hit metrics map 1:1 — plus `radiance:` counters (`decode_tokens_per_second`, `prefill_tokens_per_second`, draft acceptance by position, `prefix_hit_cut_tokens_total`, `num_requests_preempted`).

For the pp/tg A/B defined in [performance-standards.md](performance-standards.md):

1. Serve the **same container** both engines cannot do simultaneously; run radiance, then restore vllm-radiance, and record engine tag + startup receipt per run (one run per cell, as in the campaign).
2. Run the text-growth client unchanged; parse radiance's per-request `timings` (`prompt_n`, `cache_n`, `prompt_per_second`, `predicted_per_second`, `ttft_ms`, `draft_n`, `draft_n_accepted`) into the same CSV schema (`pp_effective_ingest_tok_s = (prompt_n+cache_n)/ttft`, `turn_tg_avg ≈ predicted_per_second`, `decode_tokens_s` from the steady window).
3. Add the grid rows the docs leave open: 126k-deep 1-agent tg (the 195.8-vs-204 question), cold 2K/4K/7K pp, 4-agent 126k fleet decode + preemptions.
4. Use `scripts/agentreplay.py` (upstream) for the compaction/parent-subagent prefix workload — it targets exactly the snapshot-store metric the campaign's 7/12-preemption cells care about.

## 7. Known friction

| Symptom | Cause / fix (documented) |
|---|---|
| `pool allocation refused` on the second card | Another process took VRAM between budget and allocation — stop vllm-radiance first; refused `host_pool` = pin ceiling exceeded; `amdgpu.no_system_mem_limit=1` lifts the driver cap, not RAM |
| `WARN link-below-max` on GPU B | Expected on the ×4 OCuLink path; read at 90% busy it costs prefill; the host-staged all-reduce fallback adds 2–10% on a 23.6K prefill (upstream's two-R9700 measurement), decode within noise |
| Container refuses to start after an engine update | Containers are version-pinned (pre-1.5.0 ParoQuant refused; ABI 22 in 1.8.1) — re-convert with `--reuse <old.rad>` to copy unchanged tensors |
| `--vision-tower-placement ram` refused | No tower (text-only container), `--mm-max-patches 0`, or host cannot pin |
| Media request 413 | Base64 body over `--max-body-mib` (512 default) |
| Empty `content`, `finish_reason: "length"` | Reasoning ate `max_tokens` (Qwen3.8 defaults to `xhigh`): `reasoning_effort`, `thinking_token_budget`, or `--reasoning-effort medium` |
| Snapshot store warnings | `--checkpoint-slots` set explicitly; watch `store_full` evictions — displaced snapshots re-prefill whole histories, the campaign's 131k pain in radiance form |

## 8. Rollback

Keep the vllm-radiance profile ([launchers](../SCRIPTS.md)) intact. radiance runs as a separate container name, port and model directory; nothing in the recorded deployment changes. If the trial ends, `podman rm -f radiance` and the baseline is untouched.

<!-- NAVIGATION START -->

[Home](../../index.md) · [Overview](../../README.md) · [ROCm 10.1 results](../FINAL-REPORT-20261018.md) · [Charts](../CHARTS.md)
