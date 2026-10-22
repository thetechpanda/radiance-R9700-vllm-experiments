---
layout: default
title: "Recovered scripts: originals, adapters and their limits"
---

# Recovered scripts: originals, adapters and their limits

These files were recovered from the author's inference host during the transparency follow-up. The [recovery manifest](../../data/recovery-manifest.json) records source/released hashes and whether a file is exact, adapted or an example. Read the [code corner](../../docs/CODE-CORNER.md) for worked examples and the [disclosure](../../docs/REPRODUCIBILITY.md) for what is still missing.

| File / family | Status | What it supplies |
|---|---|---|
| [bench_agents4.py](bench_agents4.py) | Byte-identical original; SHA-256 starts `ab17f129…` | Synthetic text/image growth, streaming TTFT/TG, token usage, per-cell summary |
| [needle160k.py](needle160k.py) | Byte-identical original | The generated long-prompt needle probe; running this sends a real large request immediately |
| [run_grid.sh](run_grid.sh) | Portable adapter of three recovered wrappers | Sequential n1–4, single-card caps, and non-spec image cell; requires an already configured server |
| [convert_model.sh](convert_model.sh) | Portable adapter | Recorded M2 conversion recipe; operator supplies image and model paths |
| [Pi recipe](pi-fleet/Containerfile) and [provider](pi-fleet/models.example.json) / [settings](pi-fleet/settings.example.json) examples | Recovered base recipe plus sanitized settings | Pi 1.1.0 client, 131,070 context, 32,768 max output, reserve 34,816; not the raised-budget retry |
| Existing `scripts/run_falling_blocks_*`, prompt generator and event parser | Matched against server copies | The agent runner now includes the recovered optional `PI_NETWORK` mode; other matching files were already present |
| `tools/editorial_fleet/fleet.py`, `round2.py`, `round3.py` | Byte-identical recovered orchestration/prompts | The initial 18 editorial tasks; code is available in the git checkout, excluded from the rendered site |
| `tools/editorial_fleet/documentation_followup.py` | New follow-up, separately labelled | Environment/history/code-corner source review |

## Original does not mean ideal

The original v4 harness sends synthetic tool-result messages and places a system-labelled instruction inside a **user** message. It is agent-shaped traffic, not a real tool-executing agent. It appends text reconstructed from streamed replies and uses `usage` token counts where provided. Its temperature is 0.7; it supplies no sampling seed. The growth cap is checked on the previous prompt, so a final step can overshoot it.

TTFT includes the first recognized content, reasoning content or tool-call chunk. Streaming gaps are chunk timings, not necessarily one-token intervals. The original stores request errors in the summary but can still return process exit 0; inspect `errors` before accepting a run. The adapter adds a final recorded-error check and refuses to append into an existing result CSV.

With `--csv-append`, v4 also inspects the named Podman container and records selected environment variables and the full command in a `command` column. That can expose operational details or credentials. **Its raw CSV/logs are private working outputs**, not files to commit; published campaign exports omit that column. Supplying a non-existent container makes inspection fall back to client arguments; that changes provenance capture and must be disclosed.

`run_grid.sh` does not enable/disable speculation, select GPUs, restart inference or verify model identity. The profile name labels requests only. Match the server configuration to the campaign before scheduling it; do not run grids alongside other inference work. Its default `CONTEXT_LIMIT=131070` preserves the recovered client wrapper's guard, which is distinct from radiance's recorded 131,072 server limit. Logs/cell IDs differ from the original wrappers; the adapter excludes their automatic game-fleet stage.

The conversion adapter requires Podman and the matching image recipe. It writes a new model bundle, mounts input read-only, and refuses to overwrite an existing output. It was syntax-checked here; no conversion was rerun. Model files and the engine build context are not included.

## Pi build inputs

The base recipe pins the Pi npm package at 1.1.0 but not the Node image digest, apt packages or transitive npm dependency lock. It is therefore a recoverable recipe, not a fully frozen image. Copy the examples into a private build directory as `models.json` and `settings.json`, then set your endpoint/credentials before building. Those operator files are gitignored in this directory. On a Linux host, a loopback API requires the recovered `PI_NETWORK=host` option or an equivalent reachable endpoint; bridge-container localhost is not the host.

The examples preserve the older client context and budgets even if the current server supports 204,800. Changing them defines a new client configuration. The later successful single-card retry used different budgets; do not label its settings the same as these examples.

## Replaying the editorial tool

Copy the three recovered editorial scripts beside each other in a private scratch directory and provide a **public-only repository snapshot** in its `repo/` subdirectory. Each script makes live API requests to localhost port 8000 and writes drafts/tool traces under its workspace. They expect the recorded served model ID and an already running compatible endpoint; no service is created.

`fleet.py` runs six initial tasks; `round2.py` and `round3.py` import it and replace the tasks for their six-task passes. The follow-up file runs three additional documentation tasks. Requested settings are recorded in the source. Do not launch all passes simultaneously. Treat outputs/traces as private until reviewed.

The original prompts retain then-current mistakes, including the subsequently corrected fleet-exit statement. They are historical evidence, not current author instructions or validated facts. Read [the historical account](../../docs/RESEARCH-HISTORY.md) and the editorial corrections before reusing them. Prompts and tools can now be inspected, but the exact changing per-pass repository snapshots and all original outputs are not supplied; a new run is not deterministic replay.

<!-- NAVIGATION START -->

[Home](../../index.md) · [Compare](../../docs/RADIANCE-VS-VLLM.md) · [vllm-radiance](../../docs/VLLM-RADIANCE.md) · [radiance](../../docs/RADIANCE.md) · [Charts](../../docs/CHARTS.md) · [Stuff for nerds](../../docs/CODE-CORNER.md) · [Disclosure](../../docs/REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
