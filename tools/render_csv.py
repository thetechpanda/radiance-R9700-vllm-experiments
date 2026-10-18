#!/usr/bin/env python3
"""Render derived Radiance benchmark CSVs as standalone SVG charts."""
import argparse
import csv
import html
import json
import math
from pathlib import Path
import re
import textwrap

from chart_theme import apply_theme
from build_run_index import RUN_NOTES

W = 1200
PALETTE = ['#38bdf8', '#34d399', '#fbbf24', '#fb7185', '#a78bfa']
FONT = 'system-ui, sans-serif'


def load(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def tick_label(value):
    magnitude = abs(value)
    # Human-readable axis labels: avoid scientific notation for normal
    # telemetry ranges and group thousands with commas.
    if magnitude >= 1000:
        return f'{value:,.0f}'
    if magnitude >= 100:
        return f'{value:,.1f}'.rstrip('0').rstrip('.')
    if magnitude >= 1:
        return f'{value:,.2f}'.rstrip('0').rstrip('.')
    return f'{value:.4f}'.rstrip('0').rstrip('.') if value else '0'


def svg_start(height):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}">',
            f'<rect width="{W}" height="{height}" fill="#0b1220"/>']


def render_cases(data, path, out):
    vals = []
    for row in data:
        try:
            vals.append((row['case_id'], float(row['per_agent_decode_tokens_s']),
                         int(float(row['agent_count']))))
        except (KeyError, ValueError, TypeError):
            continue
    if not vals:
        return False
    x0, x1 = 220, 1080
    ymax = max((v for _, v, _ in vals), default=1) or 1
    # Leave space for an explicit zero-based x-axis and agent-count legend.
    plot_end = 80 + len(vals) * 24
    height = plot_end + 100
    svg = svg_start(height)
    svg += [f'<text x="30" y="36" fill="#f8fafc" font-size="22" font-family="{FONT}">Per-agent decode throughput across benchmark runs</text>',
            f'<text x="30" y="60" fill="#94a3b8" font-size="13" font-family="{FONT}">Derived run summary · case identifiers are anonymized</text>']
    for tick in range(5):
        x = x0 + tick / 4 * (x1 - x0)
        value = ymax * tick / 4
        svg += [f'<line x1="{x:.1f}" y1="72" x2="{x:.1f}" y2="{plot_end-5}" stroke="#263449"/>',
                f'<text x="{x:.1f}" y="{plot_end+14}" text-anchor="middle" fill="#94a3b8" font-size="11" font-family="monospace">{tick_label(value)}</text>']
    for i, (label, value, agents) in enumerate(vals):
        y = 78 + i * 24
        width = value / ymax * (x1 - x0)
        color = PALETTE[min(max(agents - 1, 0), len(PALETTE) - 1)]
        svg += [f'<text x="{x0-10}" y="{y+13}" text-anchor="end" fill="#cbd5e1" font-size="11" font-family="monospace">{html.escape(label)}</text>',
                f'<rect x="{x0}" y="{y}" width="{width:.1f}" height="14" rx="3" fill="{color}"/>',
                f'<text x="{x0+width+6:.1f}" y="{y+11}" fill="#e2e8f0" font-size="10" font-family="monospace">{value:.1f}</text>']
    axis_y = plot_end + 25
    svg.append(f'<text x="{(x0+x1)/2}" y="{axis_y+14}" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="{FONT}">Per-agent decode throughput (tokens/s)</text>')
    legend_y = height - 18
    legend_x = x0
    for agents in sorted({n for _, _, n in vals}):
        color = PALETTE[min(max(agents - 1, 0), len(PALETTE) - 1)]
        svg += [f'<rect x="{legend_x}" y="{legend_y-11}" width="12" height="12" rx="2" fill="{color}"/>',
                f'<text x="{legend_x+18}" y="{legend_y}" fill="#cbd5e1" font-size="11" font-family="{FONT}">{agents} agent{"s" if agents != 1 else ""}</text>']
        legend_x += 100
    svg.append('</svg>')
    out.write_text('\n'.join(svg), encoding='utf-8')
    return True


def render_cases_grouped(data, out):
    """Render case records in agent-count sections on one shared scale."""
    groups = {}
    for row in data:
        try:
            agents = int(float(row['agent_count']))
            try:
                value = float(row['per_agent_decode_tokens_s'])
            except (ValueError, TypeError):
                value = None
            case = (row.get('experiment', row['case_id']), value, float(row.get('depth_cap_k_tokens') or 0))
            groups.setdefault(agents, []).append(case)
        except (KeyError, ValueError, TypeError):
            continue
    if not groups:
        return False

    x0, x1 = 510, 1080
    maximum = max((value for cases in groups.values() for _, value, _ in cases
                   if value is not None), default=1) or 1
    layout = []
    y = 105
    for agents in sorted(groups):
        cases = sorted(groups[agents], key=lambda item: item[0])
        layout.append(('heading', agents, y, len(cases)))
        y += 24
        for case_id, value, depth in cases:
            layout.append(('case', (case_id, value, depth), y, agents))
            y += 21
        y += 9
    plot_end = y
    height = plot_end + 92
    svg = svg_start(height)
    svg += [f'<text x="30" y="36" fill="#f8fafc" font-size="22" font-family="{FONT}">{html.escape(out.parent.name.replace("rocm-", "ROCm "))} historical agent workloads</text>',
            f'<text x="30" y="59" fill="#cbd5e1" font-size="12" font-family="{FONT}">What: per-agent decode rate across historical agent workloads. Why: compare behavior as concurrent fleet size changes.</text>',
            f'<text x="30" y="78" fill="#94a3b8" font-size="11" font-family="{FONT}">Grouped by agent count · one shared tokens/s scale · cases vary in depth and workload; see the run index before comparing.</text>']
    for tick in range(5):
        x = x0 + tick / 4 * (x1 - x0)
        value = maximum * tick / 4
        svg += [f'<line x1="{x:.1f}" y1="96" x2="{x:.1f}" y2="{plot_end-5}" stroke="#263449"/>',
                f'<text x="{x:.1f}" y="{plot_end+14}" text-anchor="middle" fill="#94a3b8" font-size="11" font-family="monospace">{tick_label(value)}</text>']
    for kind, record, row_y, detail in layout:
        if kind == 'heading':
            agents, count = record, detail
            color = PALETTE[min(max(agents - 1, 0), len(PALETTE) - 1)]
            label = f'{agents} agent{"s" if agents != 1 else ""} · {count} benchmark case{"s" if count != 1 else ""}'
            svg.append(f'<text x="30" y="{row_y+14}" fill="{color}" font-size="13" font-weight="700" font-family="{FONT}">{label}</text>')
            continue
        case_id, value, depth = record
        agents = detail
        color = PALETTE[min(max(agents - 1, 0), len(PALETTE) - 1)]
        label = case_id
        svg.append(f'<text x="{x0-10}" y="{row_y+12}" text-anchor="end" fill="#cbd5e1" font-size="10" font-family="monospace">{html.escape(label)}</text>')
        if value is None:
            svg.append(f'<text x="{x0+6}" y="{row_y+10}" fill="#fbbf24" font-size="10" font-family="monospace">no throughput result</text>')
        else:
            width = value / maximum * (x1 - x0)
            svg += [f'<rect x="{x0}" y="{row_y}" width="{width:.1f}" height="13" rx="3" fill="{color}"/>',
                    f'<text x="{x0+width+6:.1f}" y="{row_y+10}" fill="#e2e8f0" font-size="10" font-family="monospace">{value:.1f}</text>']
    axis_y = plot_end + 25
    svg.append(f'<text x="{(x0+x1)/2}" y="{axis_y+14}" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="{FONT}">Per-agent decode throughput (tokens/s)</text>')
    svg.append('</svg>')
    out.write_text('\n'.join(svg), encoding='utf-8')
    return True


def render_telemetry(data, path, out):
    if 'elapsed_seconds' not in data[0]:
        return False
    picks = [
        ('requests_running', 'Running requests'),
        ('requests_waiting', 'Waiting requests'),
        ('gpu_kv_pool_pct', 'GPU KV pool (%)'),
        ('cpu_tier_signal_pct', 'CPU tier signal (%)'),
        ('prompt_compute_credit_rate_tokens_s', 'Prompt-credit rate · not PP'),
        ('generated_tokens_s', 'Generation (tokens/s)'),
        ('available_memory_gib', 'Available memory (GiB)'),
        ('swap_used_gib', 'Swap used (GiB)'),
        ('vram_used_gib', 'VRAM used (GiB)'),
    ]
    series = []
    for key, title in picks:
        if key not in data[0]:
            continue
        points = []
        for row in data:
            try:
                points.append((float(row['elapsed_seconds']), float(row[key])))
            except (ValueError, TypeError, KeyError):
                continue
        if points:
            series.append((title, points))
    if not series:
        return False

    panels = series[:6]
    x0, x1 = 305, 1155
    plot_h, panel_h = 78, 122
    all_times = [t for _, points in panels for t, _ in points]
    t0, t1 = min(all_times), max(all_times)
    span = max(t1 - t0, 1)
    catalogue_path = Path(__file__).resolve().parents[1]/'data/telemetry-catalog.json'
    entries = json.loads(catalogue_path.read_text())
    entry = next((e for e in entries if e['slug'] == path.stem or e['legacy_id']+'-telemetry' == path.stem), None)
    note = (entry['title'], entry['interpretation']) if entry else ('Telemetry', 'Version and experiment provenance unavailable.')
    version = entry['version'].replace('rocm-', 'ROCm ') if entry else 'Version unverified'
    explanation_lines = textwrap.wrap(note[1], width=155) or ['No run-specific interpretation available.']
    has_prompt_credit = any(title.startswith('Prompt-credit rate') for title, _ in panels)
    warning_y = 78 + len(explanation_lines) * 14
    top = warning_y + (25 if has_prompt_credit else 17)
    height = top + len(panels) * panel_h + 22
    svg = svg_start(height)
    svg += [f'<text x="28" y="34" fill="#f8fafc" font-size="19" font-family="{FONT}">{html.escape(version)} · {html.escape(note[0])}</text>',
            f'<text x="28" y="56" fill="#94a3b8" font-size="11" font-family="{FONT}">What / how to read: {html.escape(explanation_lines[0])}</text>']
    for i, line in enumerate(explanation_lines[1:], start=1):
        svg.append(f'<text x="28" y="{56 + 14*i}" fill="#94a3b8" font-size="11" font-family="{FONT}">{html.escape(line)}</text>')
    if any(title.startswith('Prompt-credit rate') for title, _ in panels):
        svg.append(f'<text x="28" y="{warning_y}" fill="#fbbf24" font-size="11" font-family="{FONT}">PP unavailable: completion-credited counter bursts are diagnostic only, not sustained prefill throughput.</text>')

    for index, (title, points) in enumerate(panels):
        y0 = top + index * panel_h
        low = min(v for _, v in points)
        high = max(v for _, v in points)
        if math.isclose(high, low):
            pad = max(abs(low) * .05, 1)
            low, high = low - pad, high + pad
        color = PALETTE[index % len(PALETTE)]
        # A stable 0..100 percentage axis retains the meaning of utilization metrics.
        if title.endswith('(%)'):
            low, high = 0, 100
        coords = []
        for elapsed, value in points:
            x = x0 + (elapsed - t0) / span * (x1 - x0)
            y = y0 + plot_h - (value - low) / (high - low) * plot_h
            coords.append(f'{x:.1f},{y:.1f}')
        svg.append(f'<text x="28" y="{y0+18}" fill="#e2e8f0" font-size="13" font-family="{FONT}">{html.escape(title)}</text>')
        for tick in range(5):
            fraction = tick / 4
            y = y0 + plot_h * (1 - fraction)
            value = low + (high - low) * fraction
            svg += [f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="#263449"/>',
                    f'<text x="{x0-10}" y="{y+4:.1f}" text-anchor="end" fill="#94a3b8" font-size="10" font-family="monospace">{tick_label(value)}</text>']
        for tick in range(5):
            fraction = tick / 4
            x = x0 + fraction * (x1 - x0)
            elapsed = t0 + fraction * span
            label = f'{elapsed/60:.1f}m' if span >= 120 else f'{elapsed:.0f}s'
            svg += [f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y0+plot_h}" stroke="#1d2a3d"/>',
                    f'<text x="{x:.1f}" y="{y0+plot_h+15}" text-anchor="middle" fill="#94a3b8" font-size="10" font-family="monospace">{label}</text>']
        svg.append(f'<polyline points="{" ".join(coords)}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round"/>')
    svg.append('</svg>')
    out.write_text('\n'.join(svg), encoding='utf-8')
    return True


def render(path, out):
    data = load(path)
    if not data:
        return False
    if 'per_agent_decode_tokens_s' in data[0]:
        result = render_cases_grouped(data, out)
    else:
        result = render_telemetry(data, path, out)
    if result: apply_theme(out)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', nargs='+', type=Path)
    parser.add_argument('--out', type=Path, default=Path('graphs'))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for path in args.csv:
        directory = args.out/path.parent.name if path.parent.name in ('rocm-7.14','rocm-10.1','version-unverified') else args.out
        directory.mkdir(parents=True, exist_ok=True)
        print(('rendered ' if render(path, directory / (path.stem + '.svg')) else 'skipped ') + str(path))


if __name__ == '__main__':
    main()
