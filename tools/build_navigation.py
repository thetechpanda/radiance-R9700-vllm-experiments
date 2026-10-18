#!/usr/bin/env python3
"""Generate the rendered chart gallery and cross-document navigation."""
from pathlib import Path
import re
import json
from page_metadata import public_page, ensure_front_matter

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'


def title(path):
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('# '):
            return line[2:].strip()
    return path.stem.replace('-', ' ').title()


def build_chart_gallery():
    output = ['# Chart gallery', '',
        'This gallery includes selected results only; exploratory graphs are available separately in the [unchosen archive](../graphs/rocm-7.14/unchosen.md); their per-turn CSVs remain omitted. See [what was excluded and why](EXCLUDED-TESTS.md). Charts use descriptive experiment names and separate ROCm folders. Version assignment follows recorded build/runtime evidence; unknown versions stay separate. Different workloads and settings are not a controlled ROCm comparison. Prompt-credit traces are diagnostic, not validated prefill throughput.', '']
    entries = json.loads((ROOT/'data/telemetry-catalog.json').read_text())
    for version, label in [('rocm-10.1','ROCm 10.1'), ('rocm-7.14','ROCm 7.14'), ('version-unverified','Version unverified or mixed')]:
        output += [f'## {label}', '', f'[Graph folder](../graphs/{version}/README.md) · [Data folder](../data/{version}/README.md)', '']
        for entry in entries:
            if not entry.get('included', False) or entry['version'] != version:
                continue
            name = entry['slug']
            chart = ROOT/'graphs'/version/(name+'.svg')
            output += [f'<details><summary>{entry["title"]}</summary>', '', entry['provenance'], '', entry['interpretation'], '']
            if chart.exists():
                output += [f'![{entry["title"]}](../graphs/{version}/{name}.svg)', '', f'[Derived CSV](../data/{version}/{name}.csv)', '']
            else:
                output += ['No chart: the source series contains no usable samples.', '']
            output += ['</details>', '']
        if version != 'version-unverified':
            output += ['### Historical agent workloads', '', 'Exploratory cases within this recorded software profile; workloads and settings vary. These bars are not a controlled comparison.', '', f'![{label} historical agent workloads](../graphs/{version}/historical-agent-workloads.svg)', '']
        if version == 'rocm-7.14':
            output += ['### Single-card historical context-growth report', '', 'The short one/two-agent references and the three/four-agent RAM16 milestones have different histories/settings.', '', '![ROCm 7.14 single-card historical mean and maximum TTFT](../graphs/rocm-7.14/single-card-text-growth-historical.svg)', '']
        if version == 'rocm-10.1':
            output += ['### Completed Falling Blocks fleets', '',
                       '![Per-agent model time for completed coding fleets](../graphs/rocm-10.1/falling-blocks-completed-fleet-model-time-2026-10-18.svg)', '',
                       '[Play all eleven games](../examples/rocm-10.1/falling-blocks/index.html) · [Per-agent outcomes CSV](../data/rocm-10.1/falling-blocks-fleet-outcomes-2026-10-18.csv). Both final fleets delivered four games; budgets and client settings differed. The failed first single-card attempt remains in the report.', '']
            output += ['### Single-card GPU A context-growth report', '', '![ROCm 10.1 single-card GPU A mean and maximum TTFT](../graphs/rocm-10.1/single-card-gpu-a-text-growth-2026-10-18.svg)', '',
                       '### Follow-up: single versus dual cards', '',
                       '![Mean TTFT by agent count](../graphs/rocm-10.1/follow-up-single-vs-dual-mean-ttft-2026-10-18.svg)', '',
                       '![Maximum observed TTFT by agent count](../graphs/rocm-10.1/follow-up-single-vs-dual-maximum-ttft-2026-10-18.svg)', '',
                       '![Mean request decode estimate by agent count](../graphs/rocm-10.1/follow-up-single-vs-dual-request-decode-rate-2026-10-18.svg)', '',
                       'Short-output decode estimates are not fleet throughput or real-agent productivity. [Source data](../data/rocm-10.1/follow-up-single-vs-dual-text-growth-2026-10-18.csv).', '',
                       '### Historical single-card profile comparison', '',
                       '![Historical ROCm 7.14 RAM16 versus ROCm 10.1 RAM10](../graphs/rocm-10.1/single-card-rocm-7.14-ram16-vs-rocm-10.1-ram10.svg)', '',
                       'Different tier budgets, utilisation and image patches prevent an isolated ROCm-version conclusion.', '']
            output += ['### Dual-card text growth — 18 October 2026', '', '![ROCm 10.1 dual-card text growth TTFT](../graphs/rocm-10.1/dual-card-text-growth-2026-10-18.svg)', '', '[Completed case measurements](../data/rocm-10.1/dual-card-text-growth-2026-10-18.csv)', '']
            output += ['See the [seven completed dual-card text cases](REPEAT-CAMPAIGN.md). Eight GPU A/dual follow-up cells have completed; see the [latest results](../README.md#latest-rocm-101-results) and [README requirements and results](../README.md#best-recorded-single-card-setup-for-34-deep-context-agents) and [recorded configuration](../data/rocm-10.1/single-card-gpu-a-configuration.json). The [campaign report](FINAL-REPORT-20261018.md) records pressure telemetry and both first fleets; the single-card retry completed with all four agents delivering and exiting cleanly in 75:23.', '']
    (DOCS / 'CHARTS.md').write_text('\n'.join(output), encoding='utf-8')


def add_navigation():
    pages = sorted(p for p in ROOT.rglob('*.md') if public_page(p))
    for page in pages:
        content = page.read_text(encoding='utf-8')
        content = content.split('<!-- NAVIGATION START -->')[0].rstrip()
        if page in (ROOT / 'README.md', ROOT / 'index.md'):
            page.write_text(content + '\n', encoding='utf-8')
            continue
        destinations = [ROOT / 'index.md', ROOT / 'README.md',
                        DOCS / 'FINAL-REPORT-20261018.md', DOCS / 'CHARTS.md']
        links = []
        for destination in destinations:
            if destination == page or not destination.exists():
                continue
            rel = Path(__import__('os').path.relpath(destination, page.parent)).as_posix()
            label = {ROOT / 'index.md': 'Home', ROOT / 'README.md': 'Overview',
                     DOCS / 'FINAL-REPORT-20261018.md': 'ROCm 10.1 results',
                     DOCS / 'CHARTS.md': 'Charts'}[destination]
            links.append(f'[{label}]({rel})')
        footer = '\n\n<!-- NAVIGATION START -->\n\n' + ' · '.join(links) + '\n'
        page.write_text(content + footer, encoding='utf-8')


def main():
    from build_unchosen_graphs import main as build_archive
    build_archive()
    from chart_theme import main as apply_chart_theme
    apply_chart_theme()
    from build_game_gallery import main as build_game_gallery
    if (ROOT / 'examples/rocm-10.1/falling-blocks/manifest.json').exists():
        build_game_gallery()
    build_chart_gallery()
    add_navigation()
    ensure_front_matter()


if __name__ == '__main__':
    main()
