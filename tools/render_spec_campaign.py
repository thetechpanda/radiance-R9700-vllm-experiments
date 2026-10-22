#!/usr/bin/env python3
"""Render the completed model/spec campaign from three curated CSV exports.

Keeps the initial four-agent campaign, later 41-cell sweep and two shallow
reproduction cells distinct. No raw archive or server access; stdlib only.
"""
import csv
import hashlib
import html
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = 'data/rocm-10.1/'
OUT = 'graphs/rocm-10.1/'
SOURCES = [DATA + name for name in (
    'dual-r9700-spec-campaign-2026-10-19.csv',
    'dual-r9700-agent-count-sweep-2026-10-19.csv',
    'dual-r9700-8k-repro-2026-10-19.csv')]
BG, FG, MUTED, GRID = '#0b1220', '#e2e8f0', '#94a3b8', '#263449'
COLOURS = {'none': '#38bdf8', 'mtp': '#a78bfa', 'dflash2': '#fbbf24'}
LANES = {'none': 'Non-spec', 'mtp': 'MTP K4', 'dflash2': 'DFlash2 K7'}
TARGETS = [('Swift-Quark RTN MXFP4', 'ethanwtodd/'),
           ('Quark AWQ MXFP4', 'amd/'), ('Swift W4A16 AWQ', 'ukisai/')]
OUTPUTS = []


def read(path):
    with (ROOT/path).open(newline='') as stream:
        return [r for r in csv.DictReader(stream) if r['status'] == 'complete']


def text(x, y, value, size=15, colour=FG, anchor='start'):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{colour}" '
            f'text-anchor="{anchor}">{html.escape(str(value))}</text>')


def start(title, subtitle, height):
    lines = textwrap.wrap(subtitle, width=160)
    return ['<svg xmlns="http://www.w3.org/2000/svg" width="1440" '
            f'height="{height}" viewBox="0 0 1440 {height}" role="img" '
            'font-family="system-ui, sans-serif">',
            f'<title>{html.escape(title)}</title><desc>{html.escape(subtitle)}</desc>',
            f'<rect width="1440" height="{height}" fill="{BG}"/>',
            text(30, 38, title, 26),
            *[text(30, 68+i*21, line, 14, MUTED) for i, line in enumerate(lines)]]


def save(name, parts):
    relative = OUT+name
    (ROOT/relative).write_text('\n'.join(parts+['</svg>'])+'\n')
    OUTPUTS.append(relative)
    print(relative)


def target(row):
    return next(label for label, prefix in TARGETS if row['target_model'].startswith(prefix))


def vision(row):
    return 'fallingblocks' in row['arm'] or '-fb' in row['arm']


def bars(rows, name, title, subtitle, footer):
    rows = sorted(rows, key=lambda r: float(r['wall_s']))
    height = 220+len(rows)*48
    parts = start(title, subtitle, height)
    left, width = 365, 570
    maximum = max(float(r['wall_s']) for r in rows)*1.08
    for tick in range(6):
        x = left+width*tick/5
        parts += [f'<path d="M{x:.1f} 118 V{118+len(rows)*48}" stroke="{GRID}"/>',
                  text(x, 143+len(rows)*48, f'{maximum*tick/5:.0f}', 12, MUTED, 'middle')]
    for i, row in enumerate(rows):
        y = 141+i*48
        parts += [text(left-15, y+5, row['arm'], 14, FG, 'end'),
                  f'<rect x="{left}" y="{y-14}" width="{width*float(row["wall_s"])/maximum:.1f}" height="24" fill="{COLOURS[row["spec_mode"]]}"/>',
                  text(960, y+5, f'{float(row["wall_s"]):.1f} s | decode {float(row["decode_tokens_s"]):.1f} tok/s | TTFT {float(row["ttft_avg_s"]):.1f} s', 13)]
    parts += [text(30, height-48, 'Blue: non-spec | purple: MTP K4 | amber: DFlash2 K7. Wall seconds; lower is better.', 14),
              text(30, height-23, footer, 13, MUTED)]
    save(name, parts)


def sweep(rows):
    parts = start('Eight decoding setups: where the low-concurrency advantage ends',
                  '33 text cells: 1–4 agents, 10 turns per agent, ~126k growth cap. TP=2, context 131070, 4 slots, BF16 KV, 10 GiB ARC. Eight image-input cells are separate.', 1210)
    for t, (label, prefix) in enumerate(TARGETS):
        selected = [r for r in rows if r['target_model'].startswith(prefix) and not vision(r)]
        base_y = 140+t*320
        parts += [text(40, base_y-13, label, 20)]
        for col, (metric, title, maximum) in enumerate([
                ('wall_s', 'Total wall time (s; lower is better)', 1050),
                ('pp_effective_ingest_tok_s', 'Effective ingest (tok/s; cache-influenced)', 9000)]):
            left = 95+col*700
            top, height, width = base_y+18, 190, 550
            parts += [text(left, top-5, title, 14, MUTED)]
            for i in range(5):
                yy = top+height-height*i/4
                parts += [f'<path d="M{left} {yy:.1f} h{width}" stroke="{GRID}"/>',
                          text(left-9, yy+4, f'{maximum*i/4:.0f}', 11, MUTED, 'end')]
            for n in range(1, 5):
                parts += [text(left+(n-1)*width/3, top+height+23, str(n), 13, MUTED, 'middle')]
            parts += [text(left+width/2, top+height+44, 'Concurrent agents', 12, MUTED, 'middle')]
            for lane, colour in COLOURS.items():
                group = [r for r in selected if r['spec_mode'] == lane]
                primary = {n: next((r for r in group if int(r['agents']) == n), None) for n in range(1, 5)}
                coords = []
                for n, row in primary.items():
                    if row:
                        coords.append((left+(n-1)*width/3, top+height-height*float(row[metric])/maximum))
                if coords:
                    points = ' '.join(f'{x:.1f},{y:.1f}' for x, y in coords)
                    parts += [f'<polyline points="{points}" fill="none" stroke="{colour}" stroke-width="3"/>']
                for row in group:
                    x = left+(int(row['agents'])-1)*width/3
                    y = top+height-height*float(row[metric])/maximum
                    tip = html.escape(f'{row["arm"]}: {row[metric]}; {row["turns_ok"]} turns')
                    parts += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{colour}" stroke="{BG}"><title>{tip}</title></circle>']
        legend_y = base_y+286
        for j, lane in enumerate(COLOURS):
            first = next((r for r in selected if r['spec_mode'] == lane and r['kv_concurrency']), None)
            if first:
                parts += [text(65+j*460, legend_y, f'{LANES[lane]} | recorded boot pool {first["kv_concurrency"]}×', 13, COLOURS[lane])]
    parts += [text(30, 1135, 'Swift non-spec has two n=4 sweep observations; both points are shown. Lines connect the first observation at each agent count.', 13),
              text(30, 1161, 'Repeat-spread floor ≈15%; smaller gaps are unresolved. Pool varies by boot (2.61–4.30×); it is not a controlled speculation-only A/B.', 13, MUTED),
              text(30, 1187, 'Effective ingest includes cache reuse and queueing; it is not kernel prefill speed. Tooltips retain cell IDs and exact values.', 13, MUTED)]
    save('dual-r9700-agent-count-sweep-2026-10-19.svg', parts)


def vision_cost(rows):
    groups = []
    for label, prefix in TARGETS:
        for lane in COLOURS:
            selected = [r for r in rows if r['target_model'].startswith(prefix) and r['spec_mode'] == lane]
            base = next((r for r in selected if not vision(r) and int(r['agents']) == 4), None)
            image = next((r for r in selected if vision(r)), None)
            if base and image:
                groups.append((label, lane, base, image))
    height = 230+len(groups)*53
    parts = start('Vision-input increment: image cell minus its four-agent text twin',
                  'One procedural 512×512 PNG per agent per turn; synthetic input stress, not a real game-building fleet. Each comparison stays within its target and lane.', height)
    maximum = max(float(v['wall_s'])-float(b['wall_s']) for _, _, b, v in groups)*1.07
    for i, (label, lane, base, image) in enumerate(groups):
        y = 139+i*53
        delta = float(image['wall_s'])-float(base['wall_s'])
        percent = delta/float(base['wall_s'])*100
        parts += [text(355, y+5, f'{label} · {LANES[lane]}', 13, FG, 'end'),
                  f'<rect x="375" y="{y-14}" width="{570*delta/maximum:.1f}" height="24" fill="{COLOURS[lane]}"/>',
                  text(970, y+5, f'+{delta:.1f} s (+{percent:.1f}%) | {base["arm"].split("-",1)[0]} → {image["arm"].split("-",1)[0]}', 14)]
    parts += [text(30, height-71, 'Text/vision histories and cache-hit rates differ: observed increments do not isolate image-compute cost. Seed sensitivity matters.', 13),
              text(30, height-46, 'Swift non-spec uses S4 as its text twin; using repeat S6 changes +44.1% to +22.3%. W4A16 vision cells have unusually high cache hits.', 13, MUTED),
              text(30, height-21, 'Deep-band absence means no observation at that depth, not zero latency. See the band heatmap and source CSV.', 13, MUTED)]
    save('dual-r9700-vision-increment-2026-10-19.svg', parts)


def depth_bands(rows):
    bands = ['ttft_0_30k_s', 'ttft_30_60k_s', 'ttft_60_90k_s', 'ttft_90_120k_s', 'ttft_120k_plus_s']
    labels = ['0–30k', '30–60k', '60–90k', '90–120k', '120k+']
    maximum = max(float(r[k]) for r in rows for k in bands if r[k])
    height = 240+len(rows)*32
    parts = start('Mean TTFT by observed context band — all 41 sweep cells',
                  'Seconds; darker cells have lower mean TTFT. A dash means no observed turns or unavailable data, not zero latency. Blank and zero no-sample states are both displayed as dashes.', height)
    for j, label in enumerate(labels):
        parts += [text(495+j*150, 125, label, 14, MUTED, 'middle')]
    for i, row in enumerate(rows):
        y = 143+i*32
        parts += [text(400, y+19, row['arm'], 13, FG, 'end')]
        for j, key in enumerate(bands):
            value = float(row[key]) if row[key] else 0
            opacity = .12+.78*value/maximum if value else 0
            parts += [f'<rect x="{425+j*150}" y="{y}" width="140" height="27" fill="#38bdf8" fill-opacity="{opacity:.3f}"/>',
                      text(495+j*150, y+19, f'{value:.1f}' if value else '—', 13, BG if opacity>.5 else FG, 'middle')]
    parts += [text(30, height-48, 'TTFT includes queueing, cache recovery and prefill. These are context-band means, not percentiles or isolated kernel rates.', 13),
              text(30, height-23, 'Rows preserve CSV cell IDs and order. No interpolation into unobserved depth bands.', 13, MUTED)]
    save('dual-r9700-depth-band-ttft-2026-10-19.svg', parts)


def transfer(shallow, campaign):
    r1, r2 = (next(r for r in shallow if r['arm'].startswith(k)) for k in ('R1-', 'R2-'))
    b2, b1 = (next(r for r in campaign if r['arm'].startswith(k)) for k in ('B2-', 'B1-'))
    parts = start('Observed lane ordering across shallow and deep workload profiles',
                  'Same Quark target and TP=2/BF16 KV, but context, concurrency, turn counts and pool differ. Each profile is normalised to its own non-spec wall time.', 435)
    for i, (label, plain, mtp) in enumerate([('16K / 8 agents / 21 turns', r1, r2), ('131070 limit / 4 agents / 40 turns', b2, b1)]):
        y = 150+i*105
        parts += [text(30, y, label, 15)]
        for j, row in enumerate((plain, mtp)):
            yy = y-15+j*32
            ratio = float(row['wall_s'])/float(plain['wall_s'])
            parts += [f'<rect x="400" y="{yy}" width="{450*ratio:.1f}" height="24" fill="{COLOURS[row["spec_mode"]]}"/>',
                      text(1180, yy+18, f'{LANES[row["spec_mode"]]}: {row["wall_s"]} s ({ratio:.2f}×)', 13)]
    parts += [text(30, 360, 'At 16K, MTP wall is 12.4% lower — inside the ≈15% repeat-spread floor. At deep load it is 68.2% higher.', 14),
              text(30, 388, 'These observations do not isolate depth or reproduce the project benchmark. Literal 8K overflowed; DFlash2 repro arms were cancelled.', 13, MUTED),
              text(30, 414, 'Compare within-profile ordering cautiously; do not compare raw wall times as equivalent work.', 13, MUTED)]
    save('dual-r9700-lane-transfer-16k-vs-126k.svg', parts)


def main():
    OUTPUTS.clear()
    campaign, rows, shallow = [read(p) for p in SOURCES]
    bars(campaign, 'dual-r9700-spec-campaign-2026-10-19.svg',
         'Initial four-agent campaign: three targets and their decoding lanes',
         'Eight cells; 40 turns each, ~126k growth cap, TP=2, context 131070, BF16 KV, 10 GiB ARC. Separate from the later 41-cell sweep.',
         'One observation per cell. Pools differ across setups; blue = non-spec, purple = MTP, amber = DFlash2.')
    sweep(rows)
    vision_cost(rows)
    depth_bands(rows)
    bars(shallow, 'dual-r9700-8k-repro-2026-10-19.svg',
         'Shallow reproduction: two completed 16K cells',
         'Quark MXFP4; 8 agents, 21 turns per cell, engine context 16384. Literal 8K failed the prompt-size gate; two DFlash2 arms were cancelled.',
         'Observed MTP gain is 12.4%, below the ≈15% repeat-spread floor. This is not the project benchmark.')
    transfer(shallow, campaign)
    (ROOT/(OUT+'dual-r9700-spec-chart-sources.json')).write_text(json.dumps({
        'generator': 'tools/render_spec_campaign.py',
        'sources': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES},
        'outputs': OUTPUTS,
        'counts': {'initial_campaign_cells': len(campaign), 'sweep_cells': len(rows),
                   'sweep_turns': sum(int(r['turns_ok']) for r in rows), 'shallow_completed_cells': len(shallow)},
        'limits': ['One observation per cell except stated repeats; ≈15% repeat-spread floor.',
                   'Effective ingest is cache-influenced; it is not kernel prefill throughput.',
                   'Vision inputs are synthetic; no new game-building fleet is implied.']}, indent=2)+'\n')


if __name__ == '__main__':
    main()
