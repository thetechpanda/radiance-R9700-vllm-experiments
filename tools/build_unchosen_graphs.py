#!/usr/bin/env python3
"""Index archived graphs that are outside the selected comparison."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    entries = json.loads((ROOT/'data/telemetry-catalog.json').read_text())
    for version in sorted({e['version'] for e in entries}):
        directory = ROOT/'graphs'/version
        archived = [e for e in entries if e['version']==version and not e['included']
                    and (directory/(e['slug']+'.svg')).is_file()]
        if not archived:
            continue
        label = version.replace('rocm-', 'ROCm ')
        lines = ['---', 'layout: default', f'title: "{label}: unchosen graph archive"', '---', '',
                 f'# {label}: unchosen graph archive', '',
                 '[Selected graphs](README.md) · [Main gallery](../../docs/CHARTS.md)', '',
                 f'These **{len(archived)} archived graphs** are available for inspection but are not selected for the main ROCm 7.14 versus ROCm 10.1 comparison. Each entry explains its exclusion. They cover tuning, boundary and instrumentation work; they must not be read as matched runtime comparisons.', '',
                 'Version attribution for older traces follows the recorded profile and collection date, rather than an immutable image ID captured with every run. Companion memory plots are not independent workload results.', '']
        for e in archived:
            filename = e['slug']+'.svg'
            lines += ['<details markdown="1">', f'<summary markdown="0">{e["title"]}</summary>', '',
                      '**Why unchosen:** '+e['selection_reason']+'.', '',
                      f'![{e["title"]}]({filename})', '', f'[Open full-size SVG]({filename})', '', '</details>', '']
        lines += ['No graph is shown for the empty speculative-depth companion recorder: it contained no usable samples. Its absence is not a successful test result.', ''] if version=='rocm-7.14' else []
        (directory/'unchosen.md').write_text('\n'.join(lines))
        overview = directory/'README.md'
        text = overview.read_text()
        text = text.replace('This folder contains the selected results only.', 'The list below contains the selected results. This folder also retains archived exploratory graphs.')
        marker = '## Unchosen graph archive'
        if marker not in text:
            insertion = f'\n\n{marker}\n\n[View all {len(archived)} unchosen graphs and the reason for each exclusion](unchosen.md).\n\n'
            if '<!-- NAVIGATION START -->' in text:
                text = text.replace('<!-- NAVIGATION START -->',insertion+'<!-- NAVIGATION START -->')
            else:
                text += insertion
        overview.write_text(text)


if __name__ == '__main__':
    main()
