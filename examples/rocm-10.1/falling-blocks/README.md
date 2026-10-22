---
layout: default
title: "ROCm 10.1 Falling Blocks games and provenance"
---

# ROCm 10.1 Falling Blocks games and provenance

[Play the gallery](index.html) · [Campaign and per-agent outcomes](../../../docs/FINAL-REPORT-20261018.md)

Fifteen imported Qwen3.8 27B game artefacts from the completed ROCm 10.1 campaigns. The first single-card attempt, completed dual fleet, successful single-card retry and the radiance-engine acceptance fleet of 21 October remain separate. Agent 0 in the first attempt produced no file; there is no substitute game for it.

The target campaigns reported checks passing for all fifteen original outputs: syntax and mocked-DOM probes for the October 18–19 fleets, node --check on the embedded script for the radiance fleet. This is not full browser qualification or a fresh functional test of the imported copies. Where needed, release naming was changed to Falling Blocks and agent files were published as index.html; both original and released hashes are retained in [manifest.json](manifest.json). The generator verifies released bytes and hashes without modifying the games.

Only HTML games and provenance are published here. Private agent sessions, tool histories, server paths and credentials are omitted. Some variants store high scores in browser local storage.

## Radiance engine — fleet acceptance

All four agents delivered on the radiance 1.9.0 engine (MTP-4 lane, TP2, 131,072 context, seeds 100–103, 60-minute cap). Agents 2–3 exited clean; agents 0–1 timed out at the cap after delivering complete games. Syntax PASS 4/4; prefix-cache hit 80.1–94.3%.

| Agent / seed | Game | Exit / delivery | Released bytes | SHA-256 |
|---|---|---|---:|---|
| 0 / 100 | [Play](radiance-20261021/agent-0/index.html) | Exit 124; files delivered before timeout | 19,567 | `500080e5931b85a0da2ffaab8fce6d72b374275318a92d25b07c0a505772697d` |
| 1 / 101 | [Play](radiance-20261021/agent-1/index.html) | Exit 124; files delivered before timeout | 18,407 | `40f3fcff9a731da51f8a5e2bfd359251c378d9461e66c8adfc9b72621094490f` |
| 2 / 102 | [Play](radiance-20261021/agent-2/index.html) | Exit 0; delivered | 19,624 | `128f7ebc4982c8369539d3b4e3f057c457fe7c155eef4d5d13a58ce0b67fdb2b` |
| 3 / 103 | [Play](radiance-20261021/agent-3/index.html) | Exit 0; delivered | 18,632 | `b57bc39313ee6933ce989f1d2de055ee149a0609d14925afc72f64077be51719` |

## Single card — completed retry

All four agents delivered and exited cleanly. Fleet wall 75:23; 65,536-token request budget, 90-minute per-agent cap; client context corrected to 131,070.

| Agent / seed | Game | Exit / delivery | Released bytes | SHA-256 |
|---|---|---|---:|---|
| 0 / 100 | [Play](single-card-retry/agent-0/index.html) | Exit 0; delivered | 26,083 | `25028047bfad8bb46e534133ee92bcbe9f4c17fe96f4900ae85fe32116f98277` |
| 1 / 101 | [Play](single-card-retry/agent-1/index.html) | Exit 0; delivered | 27,055 | `4a151cf7034e2dc691f3d753cc33a7e2ee3f7594584541ed98912486a5ba447d` |
| 2 / 102 | [Play](single-card-retry/agent-2/index.html) | Exit 0; delivered | 23,562 | `cd3d1fd677bae39c28041000573dba79918cfb4ceb8be44a3fd81fda88b8d39c` |
| 3 / 103 | [Play](single-card-retry/agent-3/index.html) | Exit 0; delivered | 25,991 | `3d476f77081811cec037a6cafb576414738b54fce3c6f1878d4c7bcc7662f94f` |

## Dual card — completed fleet

All four agents delivered and exited cleanly. Fleet wall 30:10; 32,768-token request budget, 60-minute per-agent cap.

| Agent / seed | Game | Exit / delivery | Released bytes | SHA-256 |
|---|---|---|---:|---|
| 0 / 100 | [Play](dual-card/agent-0/index.html) | Exit 0; delivered | 24,939 | `13ac48a98ae1c334c6f91cb2c3522ed28ee8e622e8824aca1a6272cda9580240` |
| 1 / 101 | [Play](dual-card/agent-1/index.html) | Exit 0; delivered | 24,074 | `91464b05c99d38d59ebf06b62507bdea0889c3bd811f6370ff9be944feba6024` |
| 2 / 102 | [Play](dual-card/agent-2/index.html) | Exit 0; delivered | 25,022 | `7e12b58e134ce36c4dfaa975c419d31e3715e2bb418cea54375529ec46a0e548` |
| 3 / 103 | [Play](dual-card/agent-3/index.html) | Exit 0; delivered | 22,429 | `17d5e33c2c099a406fe99eb1ff0786de2a2265150e04961cdb1069555393a267` |

## Single card — first attempt

Three games produced; one clean delivery, two timeouts after producing files. Agent 0 produced no game. Fleet wall 60:00. Retained as failure evidence.

| Agent / seed | Game | Exit / delivery | Released bytes | SHA-256 |
|---|---|---|---:|---|
| 1 / 101 | [Play](single-card/agent-1/index.html) | Exit 0; delivered | 22,877 | `ae3568ce6d75499c9bc406f5d823b4810ff84212a27ee6ff79de5ab004d511ec` |
| 2 / 102 | [Play](single-card/agent-2/index.html) | Exit 124; files delivered before timeout | 20,394 | `97bd7dea46d988104d77ea6cef8b87e568aab76b92a276a637582bd237588879` |
| 3 / 103 | [Play](single-card/agent-3/index.html) | Exit 124; files delivered before timeout | 22,387 | `14743704b583e9ebf66ee23a70d92d793aa70090c3dfca105c3527e813c17a4a` |

<!-- NAVIGATION START -->

[Home](../../../index.md) · [Compare](../../../docs/RADIANCE-VS-VLLM.md) · [vllm-radiance](../../../docs/VLLM-RADIANCE.md) · [radiance](../../../docs/RADIANCE.md) · [Charts](../../../docs/CHARTS.md) · [Stuff for nerds](../../../docs/CODE-CORNER.md) · [Disclosure](../../../docs/REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
