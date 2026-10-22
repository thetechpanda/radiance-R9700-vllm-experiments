#!/usr/bin/env python3
"""Build the ROCm 10.1 gallery from imported artefacts; never modify games.

Verifies release sizes/hashes before publishing links. Functional verification
belongs to the recorded target campaign, not this local inventory generator.
"""
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAMES = ROOT / 'examples/rocm-10.1/falling-blocks'
PROFILES = [
    ('radiance-20261021', 'Radiance engine — fleet acceptance',
     'All four agents delivered on the radiance 1.9.0 engine (MTP-4 lane, TP2, 131,072 context, seeds 100–103, 60-minute cap). Agents 2–3 exited clean; agents 0–1 timed out at the cap after delivering complete games. Syntax PASS 4/4; prefix-cache hit 80.1–94.3%.'),
    ('single-card-retry', 'Single card — completed retry',
     'All four agents delivered and exited cleanly. Fleet wall 75:23; 65,536-token request budget, 90-minute per-agent cap; client context corrected to 131,070.'),
    ('dual-card', 'Dual card — completed fleet',
     'All four agents delivered and exited cleanly. Fleet wall 30:10; 32,768-token request budget, 60-minute per-agent cap.'),
    ('single-card', 'Single card — first attempt',
     'Three games produced; one clean delivery, two timeouts after producing files. Agent 0 produced no game. Fleet wall 60:00. Retained as failure evidence.'),
]


def main():
    entries = json.loads((GAMES / 'manifest.json').read_text())
    expected = {(fleet, agent) for fleet, agents in [
        ('single-card', range(1, 4)), ('dual-card', range(4)),
        ('single-card-retry', range(4)), ('radiance-20261021', range(4))] for agent in agents}
    identities = [(e['fleet'], e['agent']) for e in entries]
    if len(identities) != len(set(identities)) or set(identities) != expected:
        raise ValueError('Incomplete or duplicate campaign game inventory')
    for entry in entries:
        path = (GAMES / entry['file']).resolve()
        if GAMES.resolve() not in path.parents:
            raise ValueError('Artefact path outside gallery')
        payload = path.read_bytes()
        if len(payload) != entry['bytes'] or hashlib.sha256(payload).hexdigest() != entry['sha256']:
            raise ValueError(f'Incomplete or changed import: {entry["file"]}')
    css = '''body{max-width:1100px;margin:auto;padding:2rem;background:#0b1220;color:#e2e8f0;font:17px/1.6 system-ui}a{color:#38bdf8}h1{font-size:clamp(2rem,5vw,3.2rem);line-height:1.15}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem}article{background:#152238;padding:1.25rem;border:1px solid #334155;border-radius:10px}h2{margin-top:2.5rem}h3{margin-top:0}.play{display:inline-block;padding:.45rem .9rem;background:#38bdf8;color:#0b1220;font-weight:700;border-radius:6px;text-decoration:none}.muted{color:#94a3b8}footer{margin-top:2.5rem}'''
    output = ['<!doctype html>', '<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
              '<title>ROCm 10.1 — Qwen3.8 Falling Blocks gallery</title>', f'<style>{css}</style></head><body>',
              '<nav><a href="../../../index.html">Research home</a> · <a href="../../../docs/FINAL-REPORT-20261018.html">Results</a> · <a href="README.html">Provenance</a> · <a href="../../rocm-7.14/falling-blocks/index.html">Historical games</a></nav>',
              '<header><p>QWEN3.8 27B · ROCm 10.1 · R9700</p><h1>Fifteen games.<br>Four recorded fleet attempts.</h1>',
              '<p>Start with the radiance-engine acceptance fleet of 21 October — the newest builds — or the completed single-card retry. Each agent built its own seeded Falling Blocks variant. Use a keyboard; controls are shown inside each game.</p>',
              '<p>All fifteen original outputs passed reported target-side checks — syntax and mocked-DOM probes for the October 18–19 fleets, node-syntax on the embedded script for the radiance fleet. That is not full browser qualification. Fleet completion and file production are distinct: the first single-card attempt failed overall.</p></header><main>']
    md = ['---', 'layout: default', 'title: "ROCm 10.1 Falling Blocks games and provenance"', '---', '',
          '# ROCm 10.1 Falling Blocks games and provenance', '',
          '[Play the gallery](index.html) · [Campaign and per-agent outcomes](../../../docs/FINAL-REPORT-20261018.md)', '',
          'Fifteen imported Qwen3.8 27B game artefacts from the completed ROCm 10.1 campaigns. The first single-card attempt, completed dual fleet, successful single-card retry and the radiance-engine acceptance fleet of 21 October remain separate. Agent 0 in the first attempt produced no file; there is no substitute game for it.', '',
          'The target campaigns reported checks passing for all fifteen original outputs: syntax and mocked-DOM probes for the October 18–19 fleets, node --check on the embedded script for the radiance fleet. This is not full browser qualification or a fresh functional test of the imported copies. Where needed, release naming was changed to Falling Blocks and agent files were published as index.html; both original and released hashes are retained in [manifest.json](manifest.json). The generator verifies released bytes and hashes without modifying the games.', '',
          'Only HTML games and provenance are published here. Private agent sessions, tool histories, server paths and credentials are omitted. Some variants store high scores in browser local storage.', '']
    for fleet, title, description in PROFILES:
        output += [f'<section><h2>{html.escape(title)}</h2><p>{html.escape(description)}</p><div class="cards">']
        md += [f'## {title}', '', description, '', '| Agent / seed | Game | Exit / delivery | Released bytes | SHA-256 |', '|---|---|---|---:|---|']
        for entry in sorted((e for e in entries if e['fleet'] == fleet), key=lambda e:e['agent']):
            agent = entry['agent']
            status = 'Exit 0; delivered' if entry['exit_status'] == 0 else 'Exit 124; files delivered before timeout'
            file = html.escape(entry['file'], quote=True)
            output += [f'<article><h3>Agent {agent}</h3><p class="muted">Seed {entry["seed"]} · {entry["bytes"]:,} bytes</p><p>{status}</p><a class="play" href="{file}">Play Agent {agent}</a></article>']
            md += [f'| {agent} / {entry["seed"]} | [Play]({entry["file"]}) | {status} | {entry["bytes"]:,} | `{entry["sha256"]}` |']
        output += ['</div></section>'];md += ['']
    output += ['</main><footer><p>Profile and budget changes prevent a controlled speed or model-quality comparison. See the report for serving configuration, limits and the retained failed attempt.</p></footer></body></html>']
    (GAMES / 'index.html').write_text('\n'.join(output)+'\n')
    (GAMES / 'README.md').write_text('\n'.join(md)+'\n')
    print(f'Published gallery inventory: {len(entries)} games; all import sizes and hashes match.')


if __name__ == '__main__':
    main()
