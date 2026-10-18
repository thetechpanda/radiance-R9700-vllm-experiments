---
layout: default
title: "Dual-GPU findings"
---

# Dual-GPU findings

## Topology and serving state

The two-card phase used two AMD Radeon AI PRO R9700 32 GB GPUs (`gfx1201`) with TP=2. The first card's measured CPU-to-GPU path was about 12.9 GB/s; the second card's x4 path was about 6.8 GB/s. GPU KV was reported at 824,254 tokens. These are archived observations, not rated link values. Tensor parallel execution depends on both ranks, so the slower path can limit the engine.

## P2P all-reduce and patch hooks

The enabling step was the custom Linux PCI P2PDMA whitelist patch: it added Intel host-bridge device `8086:4621` in `drivers/pci/p2pdma.c` with `REQ_SAME_HOST_BRIDGE`. This allowed Linux to consider P2P for the MS-01 GPU topology while retaining the same-host-bridge requirement and the remaining topology/ACS checks. The patch changed eligibility; it did not prove that transfers would route correctly. The custom `7.0.0-999` kernel was booted and P2P verification confirmed working transfers on this setup. The preserved minimal patch is [`0001-pci-p2pdma-whitelist-intel-4621.patch`](../patches/0001-pci-p2pdma-whitelist-intel-4621.patch). See the [kernel and boot instructions](SCRIPTS.md#custom-kernel-installation-and-grub-settings).

The Radiance/libr4d build qualified `r4d_ar_oneshot_2rank_exact_kernel` on both ranks. The image documentation describes an exact PCIe P2P all-reduce with RCCL fallback. A separate compressed path reduces bytes for selected large payloads and changes numerical results relative to exact BF16 reduction.

The build inputs name two applied hooks:

- `patch_ar_maxbytes` preserves the qualified message-size limits for the exact collective path.
- `patch_ar_geometry` exposes measured geometry controls for compressed TP=2 all-reduce.

The kernel code is provided by the Radiance/libr4d build dependency and is not reprinted in this research package. The technical record is in the V030 upgrade notes and libr4d qualification work referenced by the source archive.

## Host memory became the limit

The GPU upgrade did not increase the host's roughly 30 GiB of RAM. A 20 GiB CPU KV reservation plus a filesystem spill tier left too little headroom and drove active swapping. A later 16 GiB RAM-only attempt improved the immediate state but continued to pressure memory under the two-worker process. At that historical stage, the service tier was reduced to 4 GiB with ARC eviction and no filesystem tier. The journal reports available memory rising from about 1.7 to 13.7 GiB and active swapping stopping after that change.

An attempted swap reclaim while the engine was resident ended in an out-of-memory restart. The archive treats that as a failure; it is excluded from the release scripts.

## Evidence and limits

The first TP=2 state was explicitly unbenchmarked. The later ROCm 10.1 stress run completed 116 four-agent turns with zero request errors at up to 126k context, but its nearest prior comparison was not configuration-matched. A controlled TP=1 versus TP=2 benchmark on the same image, workload, and cache state is not present in the collected material.

See [the research journal](RESEARCH-JOURNAL.md), [hardware table](HARDWARE.md), and [derived stress data](../data/rocm-10.1/rocm-base-image-four-agent-stress-run.csv).

## ROCm 10.1 follow-up: 10 GiB tier

The later eight-cell matrix used a different TP=2 profile: 10 GiB ARC CPU tier, FP8 KV, MTP=8, eight slots and 168,000-token context limit. Four agents completed with mean/maximum TTFT 10.85/27.23 seconds and zero KV preemptions; the four-agent coding fleet delivered all games with clean exits in 30:10. Swap usage increased from 0.37 to 1.07 GiB across the dual phase.

These newer results supersede any suggestion that dual-card operation remains entirely unmeasured. They do not create a controlled TP=1/TP=2 scaling comparison: speculation, slots and context limits differ. See the [matrix and fleet report](FINAL-REPORT-20261018.md) and [campaign ledger](REPEAT-CAMPAIGN.md). Historical capacities above refer to their own startup profiles, not a universal KV limit.

<!-- NAVIGATION START -->

[Home](../index.md) · [Overview](../README.md) · [ROCm 10.1 results](FINAL-REPORT-20261018.md) · [Charts](CHARTS.md)
