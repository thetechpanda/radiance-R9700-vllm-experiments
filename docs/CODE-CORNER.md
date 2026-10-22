---
layout: default
title: "Stuff for nerds: the code corner"
description: "The monitor, benchmark harnesses, fleet tools, collection pipeline, recovered source and publication machinery—with worked examples."
---

# Stuff for nerds

The charts are the last step. This is the plumbing: watch the GPUs, grow a conversation until memory matters, send four agents off to build something, collect what happened, and turn selected measurements into figures a reader can inspect.

The examples below explain the actual tools. **Local generation, metrics reads, live inference, model conversion and service launch are different actions.** Running the site generators does not touch inference. Running a benchmark or agent fleet does. The [setup story](ENVIRONMENT.md) explains the machine; [reproducibility disclosure](REPRODUCIBILITY.md) separates recoverable method from missing evidence.

## The collection pipeline

| Stage | What did the work | What survives |
|---|---|---|
| Configure a deployment | Kernel/build work, model/calibration files, Podman and selected launchers | Patch, dated settings, selected image/revision identifiers; not a complete universal installer |
| Observe the host/engine | `radiance-top` and historical samplers | Selected normalized resource traces; not every original recorder is bundled |
| Generate agent-shaped traffic | Recovered `bench_agents4.py` | Exact synthetic generator, streaming metrics and summary format; model/runtime still required |
| Execute real coding tasks | Pi 1.1.0 client image, seeded prompt generator, agent/fleet shell runners | Recovered recipe/settings examples, scripts, selected game outputs and manifests |
| Summarize sessions | `parse_falling_blocks_events.py` | Usage/timing CSV fields without conversation text; parser input remains private |
| Curate a release | Archive transformer, catalogues, reports and editorial review | Selected derived CSVs, reasons for exclusions and correction ledger |
| Make the publication | Python SVG generators, Markdown, Jekyll, layout/CSS, link checks | Source, generated charts, source hashes and site workflow |

There is no single raw-log pipeline behind every table. Some exports are transformed telemetry; others are curated campaign summaries or recorded boot values. The [dictionary](DATA-DICTIONARY.md) says which is which. A script being present does not prove it generated every historical result.

## Watch a running engine

**Metrics reads; no inference request or service change.** Run on the GPU host for its local DRM sensor lanes. A remote metrics URL does not magically provide that host's local sysfs sensors.

```bash
python3 scripts/radiance-top --url http://127.0.0.1:8000/metrics
python3 scripts/radiance-top --plain \
  --url http://127.0.0.1:8000/metrics --interval 2
```

If the endpoint requires authentication, the monitor accepts `--api-key`; see [monitor options](SCRIPTS.md#radiance-top-monitor). Keep keys and captured operational output private.

Controls: **w** cycles 30/60/120/300/600-second and since-start windows; **1** switches aggregate/per-GPU presentation; **p** pauses the display; **q** or Escape quits. It recognizes both engines' metric families. A missing counter stays unavailable rather than becoming a guessed number.

![Recorded radiance-top screen](../scripts/radiance-top.png)

This is the retained monitor illustration, not a fresh measurement. Its PP/TG lanes follow engine-specific counters/gauges. Prompt intake with cached tokens, recompute credit, end-to-end output and per-turn generation are different rates. The monitor is a diagnostic instrument, not a substitute for a matched PP benchmark. [Metric meanings](DATA-DICTIONARY.md).

## Grow a synthetic conversation

**Live inference.** The portable replacement is useful for a new experiment:

```bash
python3 scripts/agent_bench.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model YOUR_SERVED_MODEL_ID --agents 2 --turns 10 \
  --max-tool-chars 12000 --output src/reproductions/new-run.json
```

Create the private output directory first. This client generates records and writes a summary; it does not reproduce the original v4 workload, token distribution or turn totals. Confirm its model/context/output options against the server. A new run is new evidence, not a recreation of a published row by naming it after that row.

The original client is now inspectable too:

```bash
python3 scripts/recovered/bench_agents4.py --help
```

`--help` does not send requests. An actual example against an already configured server is:

```bash
mkdir -p src/reproductions/v4-example
python3 scripts/recovered/bench_agents4.py \
  --base-url http://127.0.0.1:8000 \
  --model YOUR_SERVED_MODEL_ID -n 1 \
  --chunk-tokens 10000 --max-tokens 126000 \
  --max-model-len 131070 -o 256 --turns-max 24 \
  --container YOUR_CONTAINER_NAME --label new-v4-example \
  --csv-append src/reproductions/v4-example/raw-summary.csv
```

Notice **no `/v1`** on v4's base URL: that client appends `/v1/chat/completions` itself. It generates synthetic tool-result text, optionally real procedural PNGs, and streams the reply. The growth target is checked on the previous prompt; it is not a hard request-depth ceiling. The named Podman container is inspected for runtime provenance. Its command/environment CSV column is private output and must be sanitized before any publication.

It supplies no sampling seed and can exit 0 with request errors recorded in its summary. Validating only `$?` is inadequate. The recovered grid adapter adds an error-count check, uses fresh output directories and keeps server configuration separate:

```bash
BASE_URL=http://127.0.0.1:8000 MODEL=YOUR_SERVED_MODEL_ID \
CONTAINER=YOUR_CONTAINER_NAME CONTEXT_LIMIT=131070 \
RESULTS_DIR=src/reproductions/new-single-grid \
bash scripts/recovered/run_grid.sh single-mtp4
```

That is a real four-cell workload. The name `single-mtp4` does not select one GPU or enable drafting. The operator must already have matched those server settings. [Original/adapter differences and quirks](../scripts/recovered/README.md).

## Four agents, four games, several definitions of success

**Live inference and new client containers.** The public task generator can be inspected without launching agents:

```bash
python3 scripts/falling_blocks_prompt.py --seed 100 \
  --output /tmp/falling-blocks-prompt.txt
```

For a real fleet, provide a Pi client image with the intended provider/model configured. The recovered [Containerfile](../scripts/recovered/pi-fleet/Containerfile) pins Pi **1.1.0**; its [provider](../scripts/recovered/pi-fleet/models.example.json) and [settings](../scripts/recovered/pi-fleet/settings.example.json) examples preserve the older budgets. Copy those examples as `models.json` and `settings.json` into a private build context, replace endpoint/credential placeholders, and build with Podman. The Node image tag and package dependencies are not a complete immutable lock.

On a Linux host with a loopback API, the recovered networking option is:

```bash
PI_IMAGE=YOUR_CONFIGURED_PI_IMAGE PI_PROVIDER=radiance \
PI_MODEL=YOUR_SERVED_MODEL_ID PI_NETWORK=host \
WORK_ROOT=src/reproductions/new-game-fleet \
bash scripts/run_falling_blocks_fleet.sh 4 100 3600 \
  http://127.0.0.1:8000/health
```

The final URL is a **health check only**. The client image's provider configuration selects the inference endpoint. Seeds 100–103 select task variants; each agent gets a 3,600-second process limit. The runner writes prompts, sessions, logs and files. Those sessions are private until reviewed.

Summarize the latest session per agent without printing its message text:

```bash
python3 scripts/parse_falling_blocks_events.py \
  src/reproductions/new-game-fleet/agent-* \
  > src/reproductions/new-game-fleet/usage.csv
```

A usage CSV does not establish task success. Check files, exit status and the actual game separately. The recorded radiance fleet delivered all four games, with **two clean exits and two delivered-then-timeout**. The gallery preserves fifteen ROCm 10.1 game artefacts across four fleet attempts; the earlier eleven behaviour checks and later four syntax checks are different validation scopes. [Fleet results](RADIANCE-VS-VLLM.md#real-tasks-delivery-and-clean-exit).

## Turn a public CSV into a chart

**Local files only; no model required.** The comparison generator uses the original public exports and the recorded profile metadata. It rounds wall/turn values explicitly; the renderer computes bars from those exports and writes source hashes.

```bash
python3 tools/build_comparison_data.py
python3 tools/build_home.py
python3 tools/build_navigation.py
python3 tools/check_recovery.py
```

Navigation also regenerates editorial figures and this page's inventory. To render only the new figures: `python3 tools/render_editorial.py`. Older campaign chart families have their own renderers; archive transformation needs the separate private inputs. These commands do not rewrite narrative prose or remeasure inference.

The [source-hash manifest](../graphs/rocm-10.1/editorial-chart-sources.json) makes the six editorial input CSVs identifiable. It does not prove the measurements true. [Native site builds and link checks](PAGES.md) are the next layer, followed by visual inspection. A passing link check cannot certify a percentage, a game or a model.

## Conversion, calibration and launchers

The recovered [conversion adapter](../scripts/recovered/convert_model.sh) invokes `rad-convert` with the recorded M2 recipe and then `rad-info`. It requires the matching digest-pinned image, local model snapshot and a new output path; it writes a potentially large bundle. The source model, recipe implementation and exact engine environment remain required external inputs.

`make_qkv_sidecar.py` derives validated Q/K/V-only scales from an existing calibration artefact. It needs the matching Radiance Python packages and `safetensors`; it is not a standalone standard-library calibrator and does not reconstruct a missing calibration corpus. [Calibration procedure](FP8-KV-CALIBRATION.md).

The `launch-*.sh` scripts start inference containers and may alter host/shared-memory state. Their settings describe particular historical profiles or templates, not a current best default. Read them together with [Podman operation](../PODMAN.md), the setup story and the intended campaign. The kernel patch changes the host; a container cannot apply it by being launched.

## The editorial agents' own machinery

`tools/editorial_fleet/` contains the recovered Python API driver and the actual initial/correction/proofreading prompts, plus the later documentation follow-up. They make live requests and write drafts/tool traces. They do not form part of the site build and do not directly edit the release. Run a pass from an isolated private workspace with a public-only `repo/` copy; read the [replay instructions](../scripts/recovered/README.md#replaying-the-editorial-tool).

The prompts preserve their historical errors, including a fleet outcome later corrected against exit receipts. They are useful evidence of the editing process, not a source to trust over the corrected data. No promise of identical AI output follows from publishing a seed. [AI assistance and limits](REPRODUCIBILITY.md#ai-assistance-division-of-work).

## Every shipped script and tool

This inventory is generated from the checkout by `tools/build_code_corner.py`. Paths under `tools/` refer to repository source and are deliberately excluded from the rendered site. Script links under `scripts/` are static source files; visiting a link does not execute them. The `radiance-top.png` image and HTML game artefacts are assets rather than extra collection tools.

<!-- CODE INVENTORY START -->

| Source | Effect / prerequisite | Purpose |
|---|---|---|
| [scripts/agent_bench.py](../scripts/agent_bench.py) | Live inference | Portable replacement synthetic-load client; JSON summary |
| [scripts/falling_blocks_prompt.py](../scripts/falling_blocks_prompt.py) | Local files | Seeded game-task text generator |
| [scripts/launch-example.sh](../scripts/launch-example.sh) | Inference launch / possible host changes | Historical profile or template; read selected settings before use |
| [scripts/launch-ram16-tested.sh](../scripts/launch-ram16-tested.sh) | Inference launch / possible host changes | Historical profile or template; read selected settings before use |
| [scripts/launch-rocm10-tp2.sh](../scripts/launch-rocm10-tp2.sh) | Inference launch / possible host changes | Historical profile or template; read selected settings before use |
| [scripts/launch-tp1-rocm10.sh](../scripts/launch-tp1-rocm10.sh) | Inference launch / possible host changes | Historical profile or template; read selected settings before use |
| [scripts/launch-tp2-live.sh](../scripts/launch-tp2-live.sh) | Inference launch / possible host changes | Historical profile or template; read selected settings before use |
| [scripts/make_qkv_sidecar.py](../scripts/make_qkv_sidecar.py) | Local artefact creation | Validated Q/K/V scale derivation; Radiance/safetensors dependencies |
| [scripts/parse_falling_blocks_events.py](../scripts/parse_falling_blocks_events.py) | Local private inputs | Latest Pi session per agent -> usage/timing fields |
| [scripts/radiance-top](../scripts/radiance-top) | Metrics reads + local sensors | Dual-engine monitor; reads endpoints and host DRM, no inference |
| [scripts/recovered/bench_agents4.py](../scripts/recovered/bench_agents4.py) | Live inference + runtime inspection | Exact recovered original; synthetic text/images and raw CSV provenance |
| [scripts/recovered/convert_model.sh](../scripts/recovered/convert_model.sh) | Model conversion container | Adapted M2 recipe; operator-provided image/input, new output |
| [scripts/recovered/needle160k.py](../scripts/recovered/needle160k.py) | Live inference immediately | Exact recovered large-prompt probe; no CLI/help mode |
| [scripts/recovered/pi-fleet/Containerfile](../scripts/recovered/pi-fleet/Containerfile) | Image build / network during build | Recovered Pi 1.1.0 recipe; requires operator provider/settings files |
| [scripts/recovered/pi-fleet/models.example.json](../scripts/recovered/pi-fleet/models.example.json) | Configuration example | Sanitized provider/endpoint/model budgets, not a credential file |
| [scripts/recovered/pi-fleet/settings.example.json](../scripts/recovered/pi-fleet/settings.example.json) | Configuration example | Recorded Pi compaction and thinking settings |
| [scripts/recovered/run_grid.sh](../scripts/recovered/run_grid.sh) | Live inference | Adapted sequential grid; server configuration is external |
| [scripts/run_falling_blocks_agent.sh](../scripts/run_falling_blocks_agent.sh) | Client containers + live inference | One seeded Pi task; writes private sessions/logs |
| [scripts/run_falling_blocks_fleet.sh](../scripts/run_falling_blocks_fleet.sh) | Client containers + live inference | Concurrent game agents; separate health/provider endpoints |
| `tools/build_code_corner.py` | Local publication | Refresh this marked inventory; preserve narrative |
| `tools/build_comparison_data.py` | Local released inputs | Comparison arithmetic/rounding and corrected game paths |
| `tools/build_game_gallery.py` | Local publication | Verify released bytes/hashes and regenerate game gallery |
| `tools/build_home.py` | Local publication | Canonical README -> Pages index |
| `tools/build_navigation.py` | Local publication | Gallery/footer/front matter; calls editorial/code/game generators |
| `tools/build_release.py` | Local, private archive required | Curated telemetry/case transformation; RESEARCH_SOURCE required |
| `tools/build_run_index.py` | Local released inputs | Run index from transformed CSVs, catalogues and editorial notes |
| `tools/build_unchosen_graphs.py` | Local publication | Retained exploratory graph archive and exclusion descriptions |
| `tools/chart_theme.py` | Local SVG writes | Apply shared palette to existing SVGs |
| `tools/check_falling_blocks.cjs` | Local game-code execution | Node mocked-DOM checks for supported historical game API shapes |
| `tools/check_pages.py` | Local built HTML | Check local file/anchor links; does not render or validate facts |
| `tools/check_recovery.py` | Local source verification | Check recovery manifest hashes; no recovered code execution |
| `tools/editorial_fleet/documentation_followup.py` | Live inference + local tool reads | AI draft/evidence task orchestration; private outputs, not a publication build |
| `tools/editorial_fleet/documentation_proof.py` | Live inference + local tool reads | AI draft/evidence task orchestration; private outputs, not a publication build |
| `tools/editorial_fleet/fleet.py` | Live inference + local tool reads | AI draft/evidence task orchestration; private outputs, not a publication build |
| `tools/editorial_fleet/round2.py` | Live inference + local tool reads | AI draft/evidence task orchestration; private outputs, not a publication build |
| `tools/editorial_fleet/round3.py` | Live inference + local tool reads | AI draft/evidence task orchestration; private outputs, not a publication build |
| `tools/organise_results.py` | Local released inputs | Versioned result/catalogue organization and inventories |
| `tools/page_metadata.py` | Local publication | Add missing front matter; excludes private paths/AGENTS |
| `tools/render_csv.py` | Local released inputs | General CSV-to-SVG renderer |
| `tools/render_editorial.py` | Local released inputs | Editorial comparison charts and source-hash manifest |
| `tools/render_follow_up.py` | Local released inputs | Earlier single/dual/fleet report figures and hashes |
| `tools/render_spec_campaign.py` | Local released inputs | Model/speculation sweep, vision and depth-band figures |
| [patches/0001-pci-p2pdma-whitelist-intel-4621.patch](../patches/0001-pci-p2pdma-whitelist-intel-4621.patch) | Host kernel source change | Recorded Intel bridge P2PDMA eligibility patch; requires topology qualification |
| `.github/workflows/pages.yml` | CI build; deployment on configured main-branch events | Native Pages build, local-link checks and publication; does not run every generator |

<!-- CODE INVENTORY END -->

<!-- NAVIGATION START -->

[Home](../index.md) · [Compare](RADIANCE-VS-VLLM.md) · [vllm-radiance](VLLM-RADIANCE.md) · [radiance](RADIANCE.md) · [Charts](CHARTS.md) · [Disclosure](REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
