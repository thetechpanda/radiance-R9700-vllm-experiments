---
layout: default
title: "Podman operation"
---

# Podman operation

[Home](README.md) · [Hardware](docs/HARDWARE.md) · [Build and launch guide](docs/SCRIPTS.md)

## Recorded single-card deployment — 18 October 2026

The inspected deployment used rootful Podman 5.7.0. `podman pod ps` is empty: the workload is a **standalone container**, named `vllm-radiance.1`. Use container commands rather than `podman pod start`.

| Setting | Verified configuration after alignment |
|---|---|
| Image | `localhost/vllm-radiance:rocm10` |
| Image ID | `6fbb1ab181f1ba0f81efddf4c77ee6c3c9f986559d0d4d2c7ded11b000af38bd` |
| Runtime | vLLM 0.30.0; PyTorch 2.12.0+rocm10.1; Triton 3.7.1+gitf0b55c07 |
| Model | `ukisai/Swift-1.5-Qwen3.8-27b-INT4` |
| Checkpoint revision | `81a28ee75eb1cd469f209813a368a79a7e3db3bc` |
| GPU use | GPU A only (`0000:03:00.0`, PCIe 4.0 ×8); TP=1 |
| Scheduling | Maximum context 131,070 tokens; four sequence slots |
| KV | FP8 with model-bound scale sidecar; prefix caching enabled |
| Speculation | MTP, **four configured speculative tokens** |
| Offload | `TieringOffloadingSpec`, **10 GiB** CPU tier (`10737418240` bytes), ARC eviction; no filesystem secondary tier |
| Shared memory | Host IPC; host `/dev/shm` cap 12 GiB |
| Parsers | `qwen3_coder` tool calls and `qwen3` reasoning |
| Network | Bridge network; port 8000 published on all IPv4 interfaces on the inspected server |
| Supervision | Enabled systemd oneshot unit; Podman restart policy `no` |

That single-card startup reported **162,148 logical GPU KV tokens**, or 1.24× the 131,070-token maximum context. This is an aggregate logical capacity figure from the running engine. It does not establish how many full-context requests fit concurrently; the 10 GiB CPU tier also participates in serving.

### Later ROCm 10.1 comparison

The subsequent follow-up used both the single-card profile above and a **10 GiB** dual-card profile (TP=2, MTP=8, eight slots, 168,000 context). The earlier 8 GiB profile below is a separate campaign. See the [accepted matrix and fleet report](docs/FINAL-REPORT-20261018.md) for results. These are dated snapshots; this guide does not claim which profile is running now. The single-card retry completed with all four agents delivering and exiting cleanly in 75:23.

### Previous TP=2 profile

The earlier two-card profile used ROCm 10.1, TP=2, 168,000-token context, eight slots, eight configured MTP tokens, an 8 GiB ARC CPU tier and a 22 GiB `/dev/shm` cap. Its startup reported group-aware GPU KV capacity of 772,030 tokens (4.60× context limit). Those settings and measurements are historical; the inspected service at that point started GPU A alone. The historical startup also showed a smaller GPU KV budget with eight speculative tokens than with four. These are startup allocation observations, not a throughput A/B result.

FP8 KV reduces attention-cache bytes per element compared with BF16. Reproduce its memory benefit and calibrate from your own agent histories using the [FP8 KV guide](docs/FP8-KV-CALIBRATION.md); scales and `--kv-cache-dtype fp8` must both be selected.

## Startup-script review

The selected launcher and service unit were checked together. At the recorded inspection, the enabled systemd service used the installed **`/usr/local/bin/radiance-vllm-start-single`** launcher and defaults to GPU A, TP=1, MTP=4, a 131,070-token limit, four slots and a 10 GiB CPU KV tier. A separate `/usr/local/bin/radiance-vllm-start-dual` launcher is installed for the TP=2 profile. The compatibility command `/usr/local/bin/radiance-vllm-start` delegates to the single-GPU launcher. The recorded service invocation was:

```bash
/usr/local/bin/radiance-vllm-start-single ukisai/Swift-1.5-Qwen3.8-27b-INT4 131070 4 4 0000:03:00.0
```

Arguments are model ID, maximum context, sequence slots, speculative-token count and PCI address. The launchers prepare shared memory, reuse persistent model/compiler caches, select the Swift snapshot and FP8 sidecar, then create the container with `podman run -d --replace`. This **replaces** an existing container of that name and interrupts requests. Backups of the previous launcher and service unit were retained on the server.

| Reviewed launcher family | Profile / status |
|---|---|
| systemd unit → installed single launcher above | Selected by the service at inspection; GPU A, TP=1, 10 GiB ARC profile |
| installed dual launcher | Available for explicit TP=2 use; separate from the systemd default |
| `start-any.sh` | Older TP=2 profile, 20 GiB LRU CPU tier plus filesystem spill; not the current service configuration |
| `start-ram16.sh`, `start-ram16-guard.sh` | Historical single-card 16 GiB ARC profiles |
| `start-nofs.sh` | Historical 20 GiB RAM-only profile |
| `start-nvme0.sh`, `start-nvme0-t4.sh` | Filesystem-spill experiments; the latter reduces CPU tier to 4 GiB |
| `start-mnt20k.sh`, `start-mnt32k.sh`, `start-lpt512.sh` | Earlier single-card scheduling/storage experiments |
| `start.sh`, `start-0.sh`, `start-1.sh`, `start-mxfp4.sh` | Earlier 12 GiB LRU plus filesystem-tier profiles; not current boot entry points |

Script presence or modification time alone is not evidence of a currently qualified configuration. The service definition, container arguments and image identity were checked together. Historical launch profiles remain documented in the [run index](docs/RUN-INDEX.md).

## Everyday operation

Run commands in the same rootful Podman context as the deployment (root or `sudo podman`); an ordinary user's rootless store will show different containers and images.

```bash
sudo podman ps -a
sudo podman pod ps
sudo podman logs --tail 100 -f vllm-radiance.1
sudo podman stats --no-stream vllm-radiance.1
sudo systemctl status radiance-vllm.service
sudo systemctl cat radiance-vllm.service
sudo journalctl -u radiance-vllm.service -n 100 --no-pager
curl --fail http://127.0.0.1:8000/health
curl --fail http://127.0.0.1:8000/v1/models
```

The service is `Type=oneshot` with `RemainAfterExit=yes`: `active (exited)` means the launcher finished, not that inference remains healthy. Its `ExecStop` stops the container cleanly. Podman restart policy is `no`, so a container crash does not automatically recover. Check the API and container state as well as systemd.

To pause service and resume the **existing** container without changing its arguments:

```bash
sudo podman stop --time 120 vllm-radiance.1
sudo podman start vllm-radiance.1
```

`podman start` reuses the stored container configuration; it does not apply edits to the launcher. See [Podman's start documentation](https://docs.podman.io/en/latest/markdown/podman-start.1.html).

To recreate the deployment using the installed launcher, with a service interruption:

```bash
sudo systemctl restart radiance-vllm.service
# Wait for engine initialisation, then verify both:
sudo podman ps -a
curl --fail http://127.0.0.1:8000/health
```

The inspected unit allows 30 minutes for its launcher, but the detached container can continue initialising after the unit exits. Do not infer readiness from container uptime.

## API use

```bash
curl --fail http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"ukisai/Swift-1.5-Qwen3.8-27b-INT4","messages":[{"role":"user","content":"Write a short Python Fibonacci function."}],"max_tokens":256,"temperature":0.2}'

python3 scripts/radiance-top --url http://127.0.0.1:8000/metrics
```

For an OpenAI-compatible coding client, set its API base to `http://127.0.0.1:8000/v1` and model to the ID returned by `/v1/models`. The inspected launch command has no API-key argument. Use a protected network or authenticated proxy for remote access. The portable release launcher binds loopback by default.

## Portable launch on another host

The server's local image is not a registry download. Build a compatible image using the [ROCm 10.1 notes](docs/SCRIPTS.md#build-and-run-the-rocm-101-tp2-profile), supply the matching model and calibration, and ensure `/dev/kfd`, `/dev/dri` and adequate host shared memory are available. The rewritten launcher requires a model directory including any symlink targets and a validated, model-bound FP8 sidecar.

```bash
IMAGE=localhost/vllm-radiance:rocm10 \
MODEL_PATH=/path/to/self-contained/model \
MODEL_ID=ukisai/Swift-1.5-Qwen3.8-27b-INT4 \
KV_SCALE_FILE=/path/to/matching-scales.safetensors \
CACHE_PATH=/path/to/compiler-cache \
bash scripts/launch-tp2-live.sh
```

This portable foreground command uses a distinct container name, `radiance-tp2`, and exits/removes the container when stopped. It preserves the historical TP=2, context, scheduling, FP8, MTP and offload settings; the service snapshot above uses the single-card profile. It does not remount host shared memory, warm page caches or install a service. Do not run it alongside another engine occupying the same GPUs or port. The [single-card RAM16 launcher](scripts/launch-ram16-tested.sh) remains a separate historical profile.

The documented 12 GiB `/dev/shm` cap is a capacity limit, not a RAM reservation; see the [Linux tmpfs documentation](https://www.kernel.org/doc/html/latest/filesystems/tmpfs.html). The earlier TP=2 profile used a 22 GiB limit and reached about 8.18 GiB after readiness. That observation does not establish peak demand for the documented single-card profile. The 10 GiB connector budget and tmpfs capacity are separate limits.

The deployment mounts a persistent Hugging Face cache and compiler/calibration cache. Its additional `/kv-cache` mount does not activate filesystem offload: there is no `secondary_tiers` entry in the recorded connector configuration. Model downloads may need credentials, but the portable launcher uses local files and contains no token. Avoid publishing complete container inspections or environment dumps: they can expose credentials.

## Troubleshooting

- **No container listed:** check rootful versus rootless context and use `ps -a` for exited containers.
- **Health endpoint unavailable:** inspect container logs; JIT compilation/model loading can outlast the systemd launcher. A running process alone is insufficient.
- **Shared-memory allocation failure:** check `df -h /dev/shm`, host memory and swap. `--ipc=host` uses the host namespace; `--shm-size` is not the capacity control for this profile.
- **OOM or stalls:** inspect `free -h`, `vmstat 1` and GPU telemetry. Reduce workload/context before assuming more RAM offload will help.
- **Wrong image/speculation after restart:** inspect only the necessary fields (`.ImageName`, `.Config.Cmd`) and compare `systemctl cat` with the installed launcher. Avoid dumping `.Config.Env` or `.Config.CreateCommand`.
- **GPU/P2P errors:** verify the booted kernel, both host PCIe links and the [P2P setup](docs/DUAL-GPU.md); a container cannot supply the host kernel patch.

<!-- NAVIGATION START -->

[Home](index.md) · [Overview](README.md) · [ROCm 10.1 results](docs/FINAL-REPORT-20261018.md) · [Charts](docs/CHARTS.md)
