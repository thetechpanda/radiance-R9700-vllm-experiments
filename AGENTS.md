# Maintaining the R9700 field notes

This is a curated, first-person systems-research publication about deep-context coding agents on Radeon AI PRO R9700 hardware, using vllm-radiance and standalone radiance. The reader should understand the story on the home page and find the receipts in the detail pages. Preserve the author's voice and responsibility. Follow the user's current instructions when they change scope or preferences.

## Read before editing

- `README.md`: canonical main article; `index.md` is generated from it.
- `docs/ENVIRONMENT.md`: the machine, constraints and setup work.
- `docs/RESEARCH-HISTORY.md`: dated chronology and surviving evidence.
- `docs/REPRODUCIBILITY.md`: tools, AI assistance, provenance and remaining gaps.
- `docs/CODE-CORNER.md`: script inventory and worked examples.
- `docs/RADIANCE-VS-VLLM.md`, `docs/VLLM-RADIANCE.md`, `docs/RADIANCE.md`: comparison and engine summaries.
- `docs/DATA-DICTIONARY.md`, `data/case-catalog.json`, `data/telemetry-catalog.json`: definitions and evidence selection.
- `docs/EDITORIAL-REVIEW.md`: errors already found and corrected.

## Editorial house style

Lead with a concrete question, finding or constraint. Write readable, technically specific prose; use first person for the author's documented actions. Keep the playful, nerdy character without inventing quotations, emotions, motives or achievements. Historical reconstruction must say what was recorded, when, and what remains unknown.

Use a blog-like main narrative with clear comparisons and a few legible charts. Put detailed procedures, inventories and caveats in the relevant nested page; keep essential confounds beside the headline result. Avoid a front page that becomes a file catalogue. Explain PP, TG, TTFT, TP, KV precision and context before relying on them. Engine names are `vllm-radiance` and `radiance`; TP1/TP2 are configurations, not separate engines.

Preserve the `## Humans` and `## RTFM` sections of README verbatim unless the user explicitly asks to edit them. Keep the licence and game attribution scopes intact. Do not let generated navigation or an archive rewrite change this text.

Present advantages and disadvantages of both engines. Prefer “records a shorter wall” to “wins”; avoid loaded comparisons such as “honest cap”, “explodes” or a universal best configuration. Say “selected for output-style preference” when selection was not the fastest measured cell. A catchier headline must never outrun its evidence.

## Evidence rules

Every quantitative performance claim must point to the relevant public CSV and cell/run identifier, or be explicitly labelled a reported observation whose underlying receipt is not public. Keep measured values, derived arithmetic, boot allocations, estimates, projections and interpretation distinguishable.

Name the target/source checkpoint, revision, quantization, engine/version, GPU count, TP, KV dtype, host tier, context target and workload family where relevant. Shared API names do not establish identical weights. The 19 Oct Y/Z references have revision `9dba8a05` and BF16 KV; the later radiance campaign records `81a28ee7…` and FP8 KV. The historical 18 Oct single-card profile is MTP-4, not non-spec.

- Percentage change is `(new / named baseline - 1) * 100`; state which direction is better and keep the baseline visible.
- Whole-cell wall per timed turn is not mean request latency under concurrency.
- In the later campaign exports, `decode_tokens_s` is total successful output / whole-cell wall. `turn_tg_avg` / `tg_avg_tokens_s` is a mean of valid request-generation estimates. The earlier follow-up's `mean_request_decode_tokens_s` is a separate reported request estimate. Do not silently swap denominators.
- Cache-inclusive ingest and bursty prompt-credit counters are not validated raw-kernel PP. Do not fill a missing PP benchmark with a proxy.
- A pre-turn growth stopping target, observed maximum prompt, server context ceiling and simultaneous full-depth qualification are different quantities.
- GPU KV boot allocation is not throughput. A host prefix tier stores completed-conversation state and does not establish extra live GPU concurrency.
- Per-card KV KiB/token uses per-card GiB divided by the shared token count; do not divide that count by GPU count again.
- Missing values are not zero results. Read each field's dictionary before calculating from a blank or `0.0`.
- Delivery, clean process exit, syntax validation, behaviour probes and browser playability are separate outcomes. Radiance's recorded game fleet delivered 4/4, with 2/4 clean exits (agents 2–3; agents 0–1 timed out after delivery).
- Earlier roughly 15% repeat spread is descriptive variability from another setup, not a significance threshold. No matched repeat distribution or isolated engine A/B is implied.

Retain failed and excluded experiments with their reasons. Do not silently discard data or mix different campaigns into one best-case leaderboard. Preserve original values and record corrections in the editorial audit.

## Private material and recovered code

`src/**`, private handovers, raw conversations, server snapshots, session traces and credentials are outside the public release. Never publish private LAN addresses, GPU UUIDs, operator paths, environment dumps or complete raw container inspections. Use sanitized examples and narrow configuration fields.

Scripts may be recovered from an authorized source after inspection. Record source/released SHA-256, whether the copy is exact or adapted, and what changed in `data/recovery-manifest.json`. Immutable recovered originals are evidence: retain their quirks and document them; put fixes or portable wrappers in separate files. Never claim a sanitized adaptation is byte-identical to its source. Do not add raw logs or AI transcripts merely to claim completeness.

Document AI/tool involvement, evaluator model identity where known, missing inputs, unsuccessful checks and limitations candidly. Source hashes prove identity, not correctness. Multiple agents sharing one model/source are not independent experimental replication.

## Source and generation map

- `README.md` -> `tools/build_home.py` -> `index.md`.
- Original public exports -> `tools/build_comparison_data.py` -> the single-card comparison CSV and corrected fleet paths.
- Public CSVs -> `tools/render_editorial.py` -> editorial SVGs and source-hash manifest.
- Catalogues + pages -> `tools/build_navigation.py` -> chart gallery, footer navigation, game gallery and missing front matter. It also calls the editorial renderer.
- `tools/build_code_corner.py` maintains only the marked script-inventory block in the code corner. Edit narrative outside that block.
- `tools/build_release.py` needs the separate private archive; `tools/build_run_index.py` instead uses transformed public CSVs and editorial notes; do not run them as a routine editorial step or imply they rebuild every campaign from a clone.
- `_layouts/default.html`, `assets/css/editorial.css`, `_config.yml` provide standard Jekyll presentation. `tools/`, private material and this AGENTS file remain excluded from the site.

Edit generators rather than generated blocks. Update existing YAML titles when headings change; the metadata helper only adds missing front matter. Keep legacy URLs working or update referring links. Preserve CSV bytes where source hashes apply. Document tools with external dependencies or live effects explicitly.

## Verification appropriate to the change

For editorial/figure updates, regenerate the affected public outputs, check source arithmetic and hashes, and run `git diff --check`. Verify repeat generation leaves affected outputs unchanged. Compare the Humans/RTFM text with the prior revision when touching the home page.

For site/navigation/layout changes, build with native Jekyll and run `python3 tools/check_pages.py _site`. Check repository-base-path hosting too when URLs/layout change. Inspect desktop and narrow mobile layouts, table scrolling and chart labels. The link checker does not prove factual accuracy, external-link health, accessibility completeness or game correctness. Record only checks actually performed and scope dated counts to their build.

For script changes, use syntax/help/offline checks where useful. Do not execute a recovered needle, benchmark, game fleet, model conversion or service launcher merely to validate documentation: these send real requests or alter the environment. An editorial request is not a request to restart inference, replace models or rerun experiments. When the user explicitly authorizes live work, use the requested environment and record the actual effects and results.

When the author requests inference-fleet assistance, use their radiance fleet for substantive draft/evidence work within the authorized scope. Verify the returned work; log the role of the assistance in the disclosure. Do not substitute assistant-side agents without making that distinction clear.

## Closing an edit

Keep home, engine summaries, environment/history, code corner, disclosure and evidence links consistent. State what changed, why, which checks passed and what remains unverified. Save source and curated outputs together. Publication is handled by the existing workflow; distinguish working-tree edits from committed/published results. Do not describe a deployment that did not happen.
