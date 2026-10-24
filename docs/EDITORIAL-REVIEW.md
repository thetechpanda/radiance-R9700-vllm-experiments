---
layout: default
title: "Editorial review: what was checked and corrected"
---

# Editorial review: what was checked and corrected

This pass brings the vllm-radiance and standalone radiance results into one readable comparison. It preserves the original measurements and the author’s human disclaimer, separates the engine summaries from the detailed campaigns, and corrects claims that went beyond the evidence.

Review used the public CSVs, recorded configuration, artefact manifests and the recovered benchmark harness. Independent draft and evidence reviews ran on the author’s radiance inference fleet. Their output was checked against source records before inclusion; review-agent agreement is not evidence that a benchmark claim is true.

## Corrections to the previous release

| Previous statement / issue | Correction and evidence |
|---|---|
| Home described only ROCm 7.14 vs 10.1 | Main story now compares vllm-radiance and radiance; the [historical overview](../HISTORICAL-OVERVIEW.md) preserves the earlier branch. |
| Dual-engine “same checkpoint” | [Y/Z sweep](../data/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.csv) records `9dba8a05`; [radiance](../data/rocm-10.1/radiance-campaign-2026-10-21.csv) records `81a28ee7…`. The API alias is not proof of identical weights. BF16 vs FP8 KV also differs. |
| Single-card historical baseline labelled “non-spec” | The [configuration JSON](../data/rocm-10.1/single-card-gpu-a-configuration.json) records **MTP-4**. The derived comparison is rebuilt from original sources. |
| `decode_tokens_s` described as per-request steady-state | Recovered harness computes total successful output / whole-cell wall. `tg_avg` is a mean of valid per-turn decode estimates. The [dictionary](DATA-DICTIONARY.md) now states both formulas and the verified harness hash. |
| “+90% decode” presented as the radiance MTP improvement | 19.61 vs 10.33 compares **new vs historical non-spec** aggregate end-to-end output. Within radiance n1, MTP changes that field **19.61 → 24.79 (+26.4%)**; turn TG **54.4 → 137.9 (+153.5%)**. |
| Shallow-band old TTFT `0.0` treated as measured zero | Blank/zero no-sample bands are not zero latency. No percentage is calculated from them. |
| One-card “nearly four times” turn cost | 34.65 / 12.59 = **2.75×**, not nearly 4×. Whole-cell wall per timed turn is not mean request latency under concurrency. |
| Single-card four-agent cap presented as an equal-depth result | radiance growth cap **88,913**, observed max **99,075**; old target **126,000**, observed max **126,691**. Unequal depths, tier sizes and turn counts are placed before the comparison. |
| All radiance TP1 cells described as ten turns per agent | n4 has **32 turns total / eight per agent**. n1–3 have 10/20/30 total, for **92** overall. |
| “Honest”, “explodes”, unqualified engine wins | Replaced with descriptive results. The old stack’s lower non-spec walls and higher TG values remain visible. Small gaps do not establish an all-reduce explanation. |
| ≈15% repeat spread used as statistical threshold | The earlier repeat cells are a different model/setup. This describes variability; it supplies no confidence interval for the new comparisons. |
| Four 131k sessions described as a hardware ceiling | This was the **four-slot allocation target**. Later measured boots allocate 786,448 and 1,228,816 tokens. |
| Six 200k sessions implied as tested performance | This is a measured **allocation**, not a sustained six-agent workload. The reported 165k probe is distinct from the capacity CSV and is not a full grid. |
| One KV-density number used for all boots | Density calculated from each rounded per-card allocation differs; the capacity report gives all measured rows and labels projections. |
| Radiance 4/4 fleet delivery implied completion | **4/4 files delivered, 2/4 clean exits** after the later receipt correction described below. Reported syntax checks are distinct from historical behaviour checks. |
| Fleet CSV linked nonexistent `falling-blocks.html` files | Links now point to the released `agent-N/index.html` files. Outcome values are unchanged. |
| TP2 n2 seconds per turn truncated to 10.23 | **204.7 / 20 = 10.235 → 10.24**, with explicit half-up rounding in the comparison generator. |
| Charts repeated stale checkpoint/lane/cap claims | Retained chart URLs now regenerate with corrected labels and caveats; four additional editorial figures have source hashes. |

## What this review did not measure

No new benchmark grid, matched baseline rerun, model-quality assessment or six-agent 200k throughput test is added. The author’s fleet was used for editorial work. Its use here does not fill those gaps in the research dataset.

Raw conversations, operator handovers and server logs remain outside the public release. Reported longer-context probes are identified as reported observations when their underlying receipt is not in the public CSV. [Excluded experiments](EXCLUDED-TESTS.md) retain their recorded dispositions.

## Reproduction and verification

`tools/build_comparison_data.py` rebuilds the derived comparison from the original source exports. `tools/render_editorial.py` produces the comparison SVGs and a [source-hash manifest](../graphs/rocm-10.1/editorial-chart-sources.json). `tools/build_home.py` generates `index.md` from the canonical `README.md` so the site and repository tell the same story. Navigation and gallery changes are made in their generator.

The author’s radiance fleet completed **18 editorial/evidence tasks across three passes**. The final pass rechecked the home-page percentages, both engine summaries, memory arithmetic, single-card accounting, chart data and publication structure. Remaining proofreading fixes corrected the sweep-only pool range, made memory-axis numbers consistent and removed a stale middle-of-page navigation fragment.

The initial editorial pass completed native Jekyll builds for both root and repository-base-path hosting: **61 HTML pages, 1,324 internal links/assets, zero errors** in each build. Desktop and 390-pixel mobile inspection verified the main page, nested engine page, table scrolling and chart layout; malformed stat-card HTML found during inspection was corrected. CSV-derived chart values and source hashes, generator idempotence, released game paths and the original responsibility and safety notes were checked. New public text was scanned for private network addresses, operator paths and credential patterns.

No experiment was silently discarded to improve a headline. No live benchmark or production configuration was changed as part of this editorial work.

## The later fleet receipt correction

The initial public fleet CSV incorrectly marked every radiance process as timed out. The first editorial pass checked against that CSV and repeated **0/4 clean exits**. A subsequent amended release corrected the records; authorized server inspection then read the original per-agent exit files directly. The current result is **4/4 deliveries, 2/4 clean exits**. Agreement among reviewers using the same wrong source had not authenticated it.

| Agent / seed | Original exit receipt | Meaning |
|---|---|---|
| 0 / 100 | [124](../data/receipts/radiance-fleet-20261021/agent-0.exit-status.txt) | Delivered, then timed out |
| 1 / 101 | [124](../data/receipts/radiance-fleet-20261021/agent-1.exit-status.txt) | Delivered, then timed out |
| 2 / 102 | [0](../data/receipts/radiance-fleet-20261021/agent-2.exit-status.txt) | Clean exit with delivery |
| 3 / 103 | [0](../data/receipts/radiance-fleet-20261021/agent-3.exit-status.txt) | Clean exit with delivery |

The receipt files contain only integer status values; source/released hashes are in the [recovery manifest](../data/recovery-manifest.json). The amended fifteen-game gallery and its provenance were preserved while the editorial work was reconciled. The [disclosure](REPRODUCIBILITY.md) records the additional source recovery and reviews, and the [history](RESEARCH-HISTORY.md) retains this correction as part of the record.

## Transparency and historical follow-up

Three additional radiance tasks drafted/audited setup, history and the code corner; six more reviewed the completed documentation. The total is **27 radiance tasks** across the initial rewrite and follow-up. The original and new drivers are identified separately in the recovery manifest.

Final findings led to an explicit inventory filter for hidden/macOS metadata, refreshed navigation, a canonical Home link in the Pages guide, and disclosure/manifest coverage for the final review driver. One reviewer confused the older vllm-radiance fleet's four clean exits in 30:10 with the later radiance fleet; that suggested numerical change was rejected against the distinct campaign evidence, and the older passage was labelled more explicitly. Other speculative parser/legacy-footer objections did not describe a failing current input; current generation and link checks remain the acceptance evidence.

The source recovery now exposes the original synthetic harness, long-prompt probe, Pi base recipe, actual editorial prompts and integer-only process exits. Portable adapters and configuration examples remain labelled as adaptations. Full historical images, calibration inputs and all raw traces are still outside the release.

Follow-up validation: native root and repository-base-path builds each checked **66 HTML pages and 1,816 internal links/assets with zero errors**. The code-corner mobile preview showed 44 inventory rows with no page overflow or broken images. The recovery checker matched all 22 manifest entries; the original human disclaimer and corrected fleet statuses were preserved, and generation remained idempotent. No new inference benchmark or model conversion was run for this follow-up.

## Graph archive rendering correction — 22 October 2026

A reader found the graph archive collapsing into deeply nested narrow panels with literal closing HTML tags. The earlier link checks had passed because the targets existed; they did not validate disclosure markup. Both graph generators emitted same-line `details`/`summary` markup that Kramdown misparsed with block HTML parsing enabled. The generators now use separate lines and explicit Markdown modes for panel bodies and plain-text summaries. The built-site checker now rejects nested, mismatched, unclosed and escaped disclosure tags. This was a presentation failure missed by the earlier acceptance checks.

## Human preface integration — 24 October 2026

At the author’s request, `HUMANS.md` is linked near the home-page disclosure and from the shared footer. The former home-page responsibility and safety sections have been removed from the home page. The author has revised the closing summary and removed the separate safety subsection; current safety guidance is in Security Stance; their old home-page anchors now lead to the preface link. The page has a human-written disclosure that records AI English copy-editing and integration. The rest of the preface remains the author’s account; this change does not add evidence or resolve its previously identified technical qualifications. Licence and game attribution scopes are unchanged.

Validation for this integration: native Jekyll 3.10.0 builds for root and repository-base-path hosting each produced **67 HTML pages, 1,837 internal links/assets and zero link-check errors**. The home page and preface were inspected at desktop and 390-pixel mobile widths using webctl-puppet. At the time of that build, note migration, the unchanged home-page licence section, repeat home generation and whitespace checks passed. The author has since revised the preface and removed the separate safety subsection; later link checks use the Security Stance target. These checks cover site integration, not factual validation of the preface’s technical claims.

The subsequent terminology pass applies inline-code styling to metrics, acronyms and technical names in the main article and human preface, standardises their spelling and capitalisation, and replaces obsolete safety-section references with Security Stance links. Link targets and terminal-output blocks were checked against the pre-pass copies; no benchmark data was edited. Historical reviewer prompts remain unchanged.

## Human preface screenshot crop — 24 October 2026

A proposed prose qualification pass was applied, then reverted at the author’s request because it changed the preface’s voice. The author’s wording is restored; the requested terminology formatting, layout changes and screenshot crop remain. No new experiment was run and no public CSV was changed.

The `nvtop` screenshot was deterministically cropped to `(left=0, top=0, width=1500, height=760)` and saved as lossless `assets/nvtop.png`; its process-command rows are excluded. Every retained decoded pixel was compared with the source and matched. The uncropped image is withheld from the public source and build. This was an exact crop using standard image tools, explicitly requested by the author; no generative image editing was used.

- Withheld original SHA-256: `9164b30b7941b4d5304658136326889071f5b148e8a25bae4ea7b76b4958f37f`
- Released PNG SHA-256: `85df467670848756054277b64060127d70adfaee76dab4c565933476518d86c1`

<!-- NAVIGATION START -->

[Home](../index.md) · [Compare](RADIANCE-VS-VLLM.md) · [vllm-radiance](VLLM-RADIANCE.md) · [radiance](RADIANCE.md) · [Charts](CHARTS.md) · [Stuff for nerds](CODE-CORNER.md) · [Disclosure](REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
