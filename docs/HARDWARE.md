---
layout: default
title: "Hardware inventory"
---

# Hardware inventory

This inventory combines the collected journal and handoff notes with live verification on 18 October 2026. It distinguishes facts recorded at different times and does not infer missing component models.

| Component | Recorded specification | Confidence / context |
|---|---|---|
| Host platform | Minisforum MS-01; Intel Core i5-12600H; 32 GB DDR5 | Host configuration supplied for the current two-card setup. Live DIMM, board and BIOS details are recorded below. |
| System memory | 32 GB DDR5 installed; approximately 30–30.6 GiB visible to Linux; 8 GiB swap; `vm.swappiness=1` recorded | Host RAM did not increase when GPU 2 was added. |
| GPU A | AMD Radeon AI PRO R9700, 32 GB, gfx1201 / RDNA4 | Present in the single-card phase and retained in the dual-card phase. |
| GPU B | AMD Radeon AI PRO R9700, 32 GB, gfx1201 / RDNA4 | Added by 2026-10-16; TP=2 deployment. |
| GPU A link | Current setup: PCIe 4.0 x8 | Earlier single-card phases used OCuLink x4 and later a direct Gen5 path; archived measurements differ by phase. |
| GPU B link | Current setup: PCIe 4.0 x4 through a redriver-equipped NVMe-to-OCuLink adapter | This adapter/redriver path is required for the second card to operate in the current host. It is the narrower link; archived CPU→GPU bandwidth was about 6.8 GB/s. |
| Storage | NVMe-backed root volume and an optional `/kv-cache` filesystem tier | A later note identifies the root device as `nvme1n1p2`; the current root device and both NVMe models are verified below. |
| Power continuity | A 650 W UPS was discussed during the two-card load phase | This is UPS capacity, not a GPU PSU rating. PSU model and power budget are not recorded. |
| Archived software images | ROCm 7.14 profile: vLLM 0.30.0, AMD PyTorch 2.12, Triton 3.7.1, AITER 0.1.20, libr4d 0.5.0. Later image: ROCm 10.1 with matching component pins. | The older build evidence records a ROCm 7.14.0 base and PyTorch `+rocm7.14`. The separately built ROCm 10.1 profile and result scope are compared in [ROCm version evidence](ROCM-VERSIONS.md). |

## Recorded hardware verification — 18 October 2026

Read-only SSH inspection used `lscpu`, filtered SMBIOS records, `lsblk`, `lspci -tv/-vv`, DRM sysfs and the running container. Serial numbers, network identifiers and credentials are omitted.

| Component | Verified value |
|---|---|
| CPU | Intel Core i5-12600H, family 6/model 154/stepping 3; 12 cores, 16 logical CPUs; reported maximum 4.5 GHz; 18 MiB L3 |
| Board | Shenzhen Meigao Electronic Equipment Co.,Ltd; AHWSA, revision 1.0 |
| BIOS | American Megatrends International, LLC.; version 1.27; SMBIOS date `04/03/2025` (3 April 2025) |
| DIMM A | 16 GB DDR5 SODIMM, Crucial Technology `CT16G56C46S5.M8G1`, single rank |
| DIMM B | 16 GB DDR5 SODIMM, Micron Technology `CT16G56C46S5.C8D`, single rank |
| Memory speed | Both modules rated 5600 MT/s, configured at **4800 MT/s**, 1.1 V; no ECC |
| Linux memory | 32,833,904,640 bytes (30.58 GiB); swap 8,589,930,496 bytes (approximately 8 GiB) |
| GPU A / GPU B | AMD Navi 48, PCI ID `1002:7551`, revision c0, at `03:00.0` / `06:00.0`; Radeon AI PRO R9700; XTX branding supplied by the operator |
| GPU memory | Each DRM device exposes 34,208,743,424 usable VRAM bytes (31.86 GiB), consistent with the nominal 32 GB cards |
| Host-side GPU links | `00:01.0`: 16 GT/s ×8; `00:06.0`: 16 GT/s ×4, both PCIe 4.0 |
| GPU endpoint links | Each endpoint reports 32 GT/s ×16; these downstream readings do **not** remove the upstream ×8/×4 bottlenecks |
| Root NVMe | Kingston `OM3PGP41024P-A0`, 953.9 GiB; root filesystem currently on its second partition |
| Other NVMe | `VS000960KWXFN`, 894.3 GiB; PCI controller identified as SK hynix PE6010 |
| Ethernet controllers | Intel X710 dual 10GbE SFP+, I226-V and I226-LM; controller inventory only, no link-speed test |
| Host software | Ubuntu 26.04.1 LTS; Linux `7.0.0-999-generic`; Podman 5.7.0 |
| Running image software | vLLM `0.30.0`, PyTorch `2.12.0+rocm10.1`, Triton `3.7.1+gitf0b55c07` |

The PCI tree contains intermediate bridges on both GPU paths. The host ports above establish the limiting negotiated widths; endpoint sysfs alone would misleadingly suggest two Gen5 ×16 host connections. Adapter/redriver model numbers and PSU specifications remain unverified. These current observations do not retroactively identify the hardware of every historical run.

## Topology timeline

1. **One GPU, early attachment:** one R9700 connected through OCuLink. The early measured CPU↔GPU path was approximately 6.6 GB/s.
2. **One GPU, direct link:** the card was rewired to a direct path (the later inspection records an upstream PCIe 4.0 ×8 limit); later bandwidth tests recorded approximately 12.9–13.8 GB/s, depending on test and direction.
3. **Two GPUs:** GPU B was added on an x4 path, measuring approximately 6.8 GB/s. Tensor parallelism uses both devices, so the link asymmetry became a system-level constraint.

The live inspection above fills gaps in the historical inventory. PSU and adapter part numbers remain unknown. Device serials are intentionally omitted.

<!-- NAVIGATION START -->

[Home](../index.md) · [Compare](RADIANCE-VS-VLLM.md) · [vllm-radiance](VLLM-RADIANCE.md) · [radiance](RADIANCE.md) · [Charts](CHARTS.md) · [Stuff for nerds](CODE-CORNER.md) · [Disclosure](REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
