---
layout: default
title: "Qwen3.8 Falling Blocks examples"
---

# Qwen3.8 Falling Blocks examples

[Play the gallery](index.html) · [Research home](../../../README.md) · [Recorded workload](../../../docs/REAL-AGENT-TEST.md)

The four `agent-N/index.html` files are recovered Qwen3.8 27B coding-agent outputs from a historical four-agent task. Their retained provenance does not independently verify the runtime profile. The archive containing this set is dated 17 October 2026; this date is an archive label, not a verified generation timestamp. No surrounding task files, session records or transcripts are published.

The recovered HTML has been renamed to Falling Blocks: display text, identifiers and browser-storage keys were updated; game rules were not changed. The [machine-readable manifest](manifest.json) records both original and released byte sizes and SHA-256 hashes. The original outputs ranged from 21,236 to 24,737 bytes; the renamed releases differ slightly in size.

| Game | Selection / distinguishing features | Bytes |
|---|---|---:|
| [Agent 0](agent-0/index.html) | Featured for its hold/ghost/preview implementation and full-canvas interface | 24,163 |
| [Agent 1](agent-1/index.html) | Alternative board and panel layout, hold and sound | 24,028 |
| [Agent 2](agent-2/index.html) | Alternative hold, ghost and preview implementation | 24,745 |
| [Agent 3 — Pastel](agent-3/index.html) | Featured for its light palette and compact score cards | 21,260 |

“Featured” is a curation choice based on the recovered implementation, not an independently measured quality score. All four are included so readers can compare them.

## Running and controls

Open a game from the Pages gallery or serve this package locally using the [Pages preview instructions](../../../docs/PAGES.md). A desktop keyboard is required; these outputs do not provide a full touch-control interface. Read the controls within the chosen game: hard drop and hold bindings vary. Sound starts after a user gesture. High-score persistence uses browser-local storage where supported.

## Release checks

Each file was checked for private paths, addresses, tokens and network references before inclusion. The files are standalone HTML/CSS/JavaScript and contain no remote asset URLs, `fetch` calls or WebSocket connections. Before the rename, all four passed script parsing, initialisation, 120 simulated render frames, movement, pause, hard-drop scoring and reset checks. The renamed files are queued for the same target-side checks using `node tools/check_falling_blocks.cjs` from the repository root. DOM and canvas are mocked; those checks do not establish full Falling Blocks rules compliance or replace browser playtesting. The historical single-agent report of 52 passing tests belongs to another run and is not claimed for these four files.

<!-- NAVIGATION START -->

[Home](../../../index.md) · [Overview](../../../README.md) · [ROCm 10.1 results](../../../docs/FINAL-REPORT-20261018.md) · [Charts](../../../docs/CHARTS.md)
