---
layout: default
title: "The box behind the charts: hardware and setup"
description: "The small host, asymmetric GPU links, kernel work, coherent ROCm build, calibration and memory budgets behind the measurements."
---

# The box behind the charts

The host stayed small while the experiment grew. One R9700 became two, but the machine still had **32 GB of system RAM**. Getting useful coding-agent service meant fitting model weights, live KV, cached conversations, compiler work and the operating system into a constrained box. Much of the work happened before there was a chart worth publishing.

This page explains the setup work and why it mattered. The [hardware inventory](HARDWARE.md) preserves component details; the [historical account](RESEARCH-HISTORY.md) follows the decisions and failures; [Stuff for nerds](CODE-CORNER.md) supplies the code and examples. This is the recorded environment, not a universal shopping list or a turnkey installation.

## The machine, without the mythology

| Part | Recorded configuration | Why it matters |
|---|---|---|
| Host | Minisforum MS-01, Intel Core i5-12600H | Small host running the serving workers, tool containers and operating system |
| Host RAM | 32 GB DDR5, 4800 MT/s; about 30.58 GiB visible to Linux | Adding GPU memory did not add host memory; cache budgets competed with workers and page cache |
| Swap | 8 GiB, recorded `vm.swappiness=1` | Swap use and active swapping were monitored separately; swap was not extra fast KV storage |
| GPU A | Radeon AI PRO R9700, nominal 32 GB, gfx1201/RDNA4 | The retained single-card baseline; host-side PCIe 4.0 ×8 in the later topology |
| GPU B | Same model/capacity | Added by 16 October, through PCIe 4.0 ×4 via an NVMe-to-OCuLink adapter/redriver |
| Storage | Kingston root NVMe plus a second NVMe identified as SK hynix PE6010 | Model files, build/cache state and filesystem-tier experiments; a mount alone does not enable offload |
| Host software | Ubuntu 26.04.1 LTS, custom Linux `7.0.0-999-generic`, Podman 5.7.0 | Host kernel/device access and container runtime are separate from the inference image |

Source: [18 October hardware verification](HARDWARE.md#recorded-hardware-verification--18-october-2026). The exact adapter/redriver and PSU model/power budget were not established. A discussed **650 W UPS** is not evidence of the GPU PSU rating. Device serials and private network details are omitted.

GPU endpoints reported faster downstream capabilities, but the upstream host ports still limited these paths to ×8 and ×4. The archived CPU→GPU measurements were about **12.9 GB/s** and **6.8 GB/s**, respectively. Those are recorded transfer observations from the [topology notes](HARDWARE.md#topology-timeline), not a benchmark of every later workload or proof of symmetric two-card scaling.

## 1. Make the two-card path work

The documented enabling change added Intel host bridge `8086:4621` to Linux's PCI P2PDMA whitelist with `REQ_SAME_HOST_BRIDGE`. The minimal [kernel patch](../patches/0001-pci-p2pdma-whitelist-intel-4621.patch) changes eligibility; it does not itself prove that peer transfers work.

The record then describes building/installing the custom kernel, generating its initramfs, updating GRUB, satisfying the machine's Secure Boot signing requirements and verifying peer transfers after boot. Host-specific signing/enrollment material is not published. The recorded IOMMU/ACS/PCIe settings belong to this topology; they are not generic instructions for every AMD workstation. A container cannot supply a missing host kernel patch. [Kernel/boot procedure](SCRIPTS.md#custom-kernel-installation-and-grub-settings).

The inference stack qualified an exact two-rank all-reduce path with RCCL fallback. A separate compressed mode reduces traffic for selected payloads and changes numerical results relative to exact BF16 reduction. That is a correctness/configuration choice, not a free bandwidth switch. The narrower second link remained part of the machine. [Dual-GPU qualification and limits](DUAL-GPU.md).

## 2. Build a coherent serving stack

The ROCm 10.1 vllm-radiance image used a **ROCm 10.1 / Ubuntu 24.04 development base**. That container base is distinct from the host's Ubuntu version. The recorded component set was vLLM 0.30.0, PyTorch 2.12.0 stamped `+rocm10.1`, Triton 3.7.1, torchvision 0.27.1, AITER 0.1.20 and libr4d 0.5.0.

The multistage build compiled wheels against that base, pruned unused GPU architectures, assembled patches and kernels, and produced a smaller runtime image. The record describes eight-way build orchestration and `BUILD_JOBS=16`; inference was stopped during the build because compiling and serving together exceeded the host's resource budget.

Practical fixes included disabling the failing AOTriton path and unavailable MAGMA dependency, forcing torchvision's ROCm extension build, stamping source-wheel metadata correctly, and placing the ROCm-provided `amdsmi` module where platform detection could import it. These are documented build repairs, not measured engine-speed gains. The full compatible engine checkout and all build inputs are not bundled here. [Build procedure and component caveats](SCRIPTS.md#build-and-run-the-rocm-101-tp2-profile).

## 3. Match model weights, cache precision and calibration

The early central checkpoint was `ukisai/Swift-1.5-Qwen3.8-27b-INT4`, recorded at `81a28ee75eb1cd469f209813a368a79a7e3db3bc`. Four-bit weights and FP8 attention KV solve different memory problems. The vllm-radiance FP8 path required a checkpoint-matched Q/K/V scale sidecar and its provenance manifest; loading any file with the right extension was not sufficient.

Calibration observed the exact model using representative histories, validated the resulting scales and checked held-out behaviour. The public package includes the workflow and a Q/K/V-only sidecar derivation tool, but not private calibration histories, model weights or calibration artefacts. Earlier padded KV allocation and later compact storage behaved differently; neither a calibration pass nor the FP8 dtype alone establishes a universal capacity or quality result. [Calibration method](FP8-KV-CALIBRATION.md) · [model identities](MODELS.md).

## 4. Give host RAM a budget, not a wish

Early two-card profiles attempted a 20 GiB host KV tier plus filesystem spill. The journal records active swapping, then a 16 GiB RAM-only revision with little margin. A later 4 GiB ARC/no-filesystem profile recovered headroom. Attempting to reclaim swap with the engine resident caused an out-of-memory restart. Those failures belong to the record; they are not procedures to repeat casually. [Memory history](RESEARCH-JOURNAL.md#4-add-the-second-gpu-and-solve-a-different-problem).

The 18 October matrix subsequently used a **10 GiB ARC tier** on both single and dual configurations. Its single-card shared-memory cap was **12 GiB**; older profiles used a 22 GiB cap. A tmpfs capacity is not a reservation, and neither is the same as the connector's cache budget. The later standalone radiance deployment used a **13 GiB prefix tier**, with different allocation checks. Do not carry a historical vLLM budget into the new engine by analogy. [Podman memory notes](../PODMAN.md) · [capacity ladder](RADIANCE-200K-CONTEXT-2026-10-22.md).

## 5. Watch the system while it works

`radiance-top` reads engine metrics and, when run on the GPU host, local DRM sensors. It was extended to recognize both `vllm:*` and `radiance:*` metric families. Hardware lanes, request waits, cache signals and token rates made it possible to distinguish a busy GPU from useful service.

Monitoring did not make every rate comparable. Cached prompt intake, recompute credits, end-to-end output and per-turn generation estimates have different denominators. The [dictionary](DATA-DICTIONARY.md) states those differences; the [code corner](CODE-CORNER.md#watch-a-running-engine) shows monitor commands and controls. Reading metrics is network activity, but does not itself send an inference request or reconfigure the service.

## 6. Move to the standalone engine

The 21–22 October campaign moved to digest-pinned **radiance 1.9.0**, using a converted `.rad` bundle. The recovered conversion recipe names the INT4 source while the API alias says W4A16-AWQ. The [model table](MODELS.md) keeps those identities separate from the older Y/Z revision.

The operator record describes service supervision for a cold-boot device-registration race and page-cache warming of the model bundle. These are reported operational measures, not independently repeated tests in this editorial pass. Warming before startup is not a claim that the entire file stays resident while inference runs. The later read-only inspection still reported six slots and a 204,800 server context limit; that confirms settings, not simultaneous six-agent performance.

The earlier engine's launchers and service names remain dated operational references. Read the actual image, service definition and selected arguments together before running anything. [radiance results](RADIANCE.md) · [recovered scripts](../scripts/recovered/README.md) · [complete disclosure](REPRODUCIBILITY.md).

## What the setup effort bought—and what it did not establish

The custom topology worked, the stack served requests, and the recorded workloads exposed useful operating ranges. The setup also changed across campaigns. It did not produce one controlled test isolating a kernel patch, ROCm version, second GPU, cache dtype or engine change. The comparison pages keep those constraints beside the results so another reader can reuse the work without inheriting a claim the experiment never established.

<!-- NAVIGATION START -->

[Home](../index.md) · [Compare](RADIANCE-VS-VLLM.md) · [vllm-radiance](VLLM-RADIANCE.md) · [radiance](RADIANCE.md) · [Charts](CHARTS.md) · [Stuff for nerds](CODE-CORNER.md) · [Disclosure](REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
