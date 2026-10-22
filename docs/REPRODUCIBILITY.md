---
layout: default
title: "Reproducibility, tools and AI disclosure"
description: "What readers can rebuild, which scripts were recovered, how AI was used, and what remains missing."
---

# Reproducibility, tools and AI disclosure

> **AI-generated article:** This article is fully AI-generated and has not been human-edited; the article itself is an output of this research and part of the evaluation.

**This is a curated research record, not a fully reproducible benchmark package.** You can inspect the released measurements, recalculate comparisons, regenerate selected figures and build the site. We have also recovered the original synthetic benchmark and editorial scripts. Model files, complete historical environments and all raw evidence are still not included.

Disclosure date: **22 October 2026**. This is an account of work actually recorded, not a promise about future maintenance. The author's [Humans and RTFM sections](../README.md#humans) remain unchanged.

## Different kinds of reproduction

| Layer | Public material / automation | What that does not prove |
|---|---|---|
| Arithmetic | CSVs, cell IDs, definitions and rounding rules | Correct arithmetic does not authenticate the measurement or isolate an engine effect |
| New comparison and figures | `tools/build_comparison_data.py`, `tools/render_editorial.py`, six public CSVs and [source hashes](../graphs/rocm-10.1/editorial-chart-sources.json) | Hashes prove file identity, not scientific correctness |
| Home and navigation | `README.md`, catalogues, manifests, `tools/build_home.py`, `tools/build_navigation.py` | Prose, selection and interpretation remain editorial work |
| Earlier figures and raw-data release | Other renderers plus `tools/build_release.py` / archive-index tools | Some inputs require the private archive; not every historical output is derivable from a public clone |
| Site build | Jekyll, layout/CSS and GitHub Actions | CI builds and checks links; it does not run every generator, audit every number or rerun inference |
| Original synthetic client | [Recovered v4 harness](../scripts/recovered/bench_agents4.py), exact source hash and documented quirks | A matching client does not recreate model files, caches, runtime versions or historical scheduling |
| Fleet and editorial process | Recovered Pi recipe/settings, task tools, editorial orchestration and prompts in the checkout | Seeded requests do not guarantee identical model answers; exact evolving per-pass snapshots and complete traces are not supplied |

There is **no single command for every generation, build, data check and visual review**. Recalculating results, rebuilding the presentation and independently repeating the experiments are different capabilities.

## How the evidence reached the page

The work used **vllm-radiance**, then standalone **stilldeadcode/radiance**, with OpenAI-compatible streaming clients, synthetic context growth, image-input cells, real coding tasks and boot-capacity checks. Those families answer different questions and are kept separate.

The released data is curated. Some tables derive from telemetry; others are campaign summaries, boot readings or transcriptions from reports. There is no universal raw-log-to-every-number pipeline. Read the [dictionary](DATA-DICTIONARY.md), [run index](RUN-INDEX.md), [catalogues](../data/README.md) and [exclusion record](EXCLUDED-TESTS.md) for provenance. Blank/unavailable values are not automatically zero.

The editorial revision recalculated existing measurements, rebuilt a comparison CSV and generated SVGs. It corrected interpretation, the historical MTP label, one rounded value and game paths. It did not add a fresh matched engine baseline or performance grid. The [audit](EDITORIAL-REVIEW.md) records corrections, including a later receipt correction: radiance agents 0–1 timed out after delivery, while agents 2–3 exited cleanly. **The final recorded outcome is 4/4 delivered, 2/4 clean**, superseding an earlier erroneous CSV and review conclusion of 0/4 clean.

## Models and environment are part of the result

The family is **Swift-1.5 Qwen3.8 27B**. The INT4 source, W4A16-AWQ API alias, converted `.rad` bundle, MXFP4 targets and DFlash2 drafter are separate identities in the [model inventory](MODELS.md). Weight quantization and KV precision are separate settings. The Y/Z references record `9dba8a05` with BF16 KV; radiance records `81a28ee7…` with FP8 KV. A shared API name is not proof of identical weights.

The [setup story](ENVIRONMENT.md), [hardware inventory](HARDWARE.md), engine pages and [script guide](SCRIPTS.md) identify the available component versions, topology, contexts, speculation and memory budgets. Models, tokenizers, calibration data/sidecars, converted bundles and engine images are not redistributed. Some revisions/digests survive; no complete immutable environment exists for every historical cell. The site licence does not relicense third-party engines, models or packages; see [licence scope](../README.md#licence).

## AI assistance: division of work

AI helped execute, analyse and document the broader investigation. We do not have a complete attribution ledger for every historical line of prose or code. The author retained the decisions, interpretation and responsibility stated in the human disclaimer.

For the initial editorial rewrite, an **OpenAI Codex assistant** coordinated source inspection, arithmetic, editing, code/SVG generation and validation. Its exact model build was not recorded in the public repository. Two initial assistant-side subagents performed read-only evidence/publication audits. These were separate from the author's inference fleet.

The author's radiance fleet then performed **18 tasks in three passes**, with up to six concurrent reviewers. Tasks covered dual-engine evidence, single-card evidence, memory, engine drafts, the home-page story, correction and final proofing. The follow-up assigned three environment/history/code-corner source tasks and six final documentation reviews, for **27 radiance tasks across the initial rewrite and this follow-up**; both follow-up drivers/prompts are retained. Multiple contexts using the same model and material are not independent scientific replication or diverse-model consensus.

The fleet used API model `ukisai/Swift-1.5-Qwen3.8-27b-W4A16-AWQ`, the recorded `81a28ee7…` conversion family, on radiance 1.9.0. A Python orchestrator called `/v1/chat/completions`, exposing scoped `read_file` and `list_files` tools over a temporary public-repository copy. Agents returned drafts/reports; they did not directly edit the release or control the service. The coordinator checked and applied selected output.

Requested settings: **temperature 0.5**, **low reasoning effort**, **10,000 max output tokens per request**, task seeds **101–606 in steps of 101** for each six-task pass, and up to **23 request rounds per task**. The three follow-up tasks use the first three seeds. These describe requests, not a guarantee that each server option was applied identically or that replay will be deterministic. Complete AI token, energy and cost accounting was not collected.

The recovered `tools/editorial_fleet/fleet.py`, `round2.py` and `round3.py` now publish the actual orchestration and prompts; `documentation_followup.py` and `documentation_proof.py` record the later tasks. They are available in the git checkout, excluded from rendered Pages. Original prompts preserve then-current mistakes, including the superseded fleet-exit claim. They are evidence of the process, not authoritative current facts. The exact historical repository snapshot for every request and all draft/tool traces are not included. The integer-only [fleet exit receipts](EDITORIAL-REVIEW.md#the-later-fleet-receipt-correction) are now public so that particular correction can be inspected directly.

Agents repeated source errors and introduced new ones, including a wrong PP expansion and an incorrect per-card memory calculation. Source checking corrected those. Review agreement also failed to expose the original erroneous fleet CSV until actual exit receipts were revisited. That is a limit of the review, not a reason to present it as independent validation.

## Recovered scripts and provenance

The authorized server inspection located the original synthetic harness, long-context needle script, campaign wrappers, Pi client recipe/settings and editorial scripts. Exact originals and portable adaptations are labelled in the [recovered-code guide](../scripts/recovered/README.md) and [SHA-256 manifest](../data/recovery-manifest.json).

The v4 benchmark generates synthetic text/images; those fixtures can now be inspected without private conversations. Its runtime `command` CSV column can capture operational environment details, so raw outputs remain private and published exports omit it. The portable `scripts/agent_bench.py` remains a different replacement client. Recovering source does not make the two clients interchangeable.

The recovered needle supplies the method for the reported long-context probe; its historical response/timing receipt is still not in the public capacity CSV. The adapters replace operator paths and separate benchmark requests from service configuration. None was run as a new performance experiment during this recovery.

## Publication tools and observed versions

Python standard-library code performs CSV/JSON arithmetic, hashes, SVG/XML generation and link checks. The new charts are **code-generated SVGs**, not generated images. HTML/CSS and standard Jekyll/Kramdown provide the site; `_config.yml` lists its plugins. [Stuff for nerds](CODE-CORNER.md) inventories the tools and gives worked examples.

Native builds used Podman with `docker.io/jekyll/jekyll:pages`, resolved for the preview to:

```text
sha256:7236b9b68020eb442e9732e9c25aafe4439804d63395b7a20591288dfd4e3c06
```

Observed build versions: **Ruby 3.3.4, Jekyll 3.10.0, github-pages 232**. Local generation used **Python 3.14.7**; the verification host reported **Python 3.14.4**. The tag and CI major-version references are mutable; CI does not pin that preview digest or guarantee byte-identical HTML. A native-gem installation attempt lacked development headers; the successful builds used the container. The local Docker daemon was unavailable.

SSH copied selected source files and invoked isolated tools on the author's host. A temporary Python HTTP server served public HTML. **webctl-puppet with Chrome** inspected desktop/mobile pages and chart labels. Visual inspection is not a committed automated screenshot suite. Private source conversations, credentials, network identifiers and operator snapshots were kept out of the release.

## What readers can run locally

From the checkout, without inference:

```bash
python3 tools/build_comparison_data.py
python3 tools/build_home.py
python3 tools/build_navigation.py
python3 tools/check_recovery.py
```

Navigation also regenerates the editorial figures, game/chart galleries, code inventory and missing front matter. It does not rewrite prose or rebuild every historical dataset. See [Pages instructions](PAGES.md) for native rendering, then `python3 tools/check_pages.py _site` for local links/anchors. A repository-base-path build needs the matching `--base-path` argument. Link checks do not certify external URLs, scientific accuracy, accessibility completeness or game behaviour.

## Remaining gaps

Private calibration histories, raw conversations/logs, some original session traces, operator handovers and full historical build inputs remain withheld or unavailable. Public hashes of unavailable sources do not reconstruct them. Some early build identities and package locks were not captured. The recovered Pi recipe pins its npm package but not every image/apt/transitive dependency.

No sustained six-agent 200k grid, matched raw-kernel PP benchmark, blinded model-quality study or complete repeated-run distribution is added. Boot allocation remains different from measured concurrency performance. Changes in revision, KV precision, target depth, host tier and workload length remain confounds. The [historical account](RESEARCH-HISTORY.md) preserves these unfinished questions alongside the results.

<!-- NAVIGATION START -->

[Home](../index.md) · [Compare](RADIANCE-VS-VLLM.md) · [vllm-radiance](VLLM-RADIANCE.md) · [radiance](RADIANCE.md) · [Charts](CHARTS.md) · [Stuff for nerds](CODE-CORNER.md)
<!-- NAVIGATION END -->
