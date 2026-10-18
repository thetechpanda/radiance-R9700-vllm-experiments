#!/usr/bin/env python3
"""Generate standalone SVG result charts from the existing local CSV exports.

No server connections, benchmark launches or third-party dependencies.
"""
import csv
import hashlib
import html
import json
from chart_theme import apply_theme
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLUE, ORANGE, PURPLE = '#176ca4', '#d77a22', '#8051a8'


def read(relative):
    with (ROOT/relative).open(newline='') as stream:
        return list(csv.DictReader(stream))


def text(x, y, value, size=14, colour='#172b3a', anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{colour}" text-anchor="{anchor}">{html.escape(str(value))}</text>'


def start(title, subtitle, height):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img">',
            f'<title>{html.escape(title)}</title>', f'<desc>{html.escape(subtitle)}</desc>',
            '<rect width="1200" height="100%" fill="white"/><style>text{font-family:Arial,sans-serif}</style>',
            text(30,35,title,23), text(30,62,subtitle,13)]


def save(relative, parts):
    path = ROOT/relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(parts+['</svg>'])+'\n')
    apply_theme(path)
    print(relative)


def single_report(relative, title, subtitle, rows, footer):
    # Blue bars are mean TTFT; grey markers are observed maxima, not percentiles.
    maximum=max(float(r['maximum']) for r in rows)*1.12
    x0,x1=315,1080
    height=190+len(rows)*66
    parts=start(title,subtitle,height)
    parts += [text(30,91,'Mean TTFT (blue bar) and maximum observed TTFT (grey marker), seconds',13)]
    end=112+len(rows)*66
    for i in range(6):
        value=maximum*i/5;x=x0+(x1-x0)*i/5
        parts += [f'<line x1="{x:.2f}" x2="{x:.2f}" y1="109" y2="{end}" stroke="#e0e6eb"/>',text(round(x,2),end+22,f'{value:.0f}',12,anchor='middle')]
    for i,row in enumerate(rows):
        y=121+i*66;mean=float(row['mean']);peak=float(row['maximum'])
        width=mean/maximum*(x1-x0);mark=x0+peak/maximum*(x1-x0)
        parts += [text(30,y+17,row['label'],14),
                  f'<rect x="{x0}" y="{y}" width="{width:.2f}" height="24" fill="{BLUE}"/>',
                  f'<line x1="{mark:.2f}" x2="{mark:.2f}" y1="{y-3}" y2="{y+28}" stroke="#536879" stroke-width="3"/>',
                  text(30,y+37,row['detail'],11,'#536879'),
                  text(1110,y+17,f'{mean:.2f} / {peak:.2f}',12,anchor='middle')]
    parts += [text(690,end+45,'TTFT (seconds); shared zero-based scale',13,anchor='middle'),text(30,height-16,footer,12)]
    save(relative,parts)


def grouped(relative, title, subtitle, groups, series, unit, footer):
    maximum=max(value for group in groups for value in group['values'])*1.15 or 1
    x0,x1=210,1035;stride=91;height=208+len(groups)*stride
    parts=start(title,subtitle,height)
    for i,(label,colour) in enumerate(series):
        x=30+i*520
        parts += [f'<rect x="{x}" y="84" width="17" height="12" fill="{colour}"/>',text(x+25,95,label,13)]
    end=122+len(groups)*stride
    for i in range(6):
        value=maximum*i/5;x=x0+(x1-x0)*i/5
        parts += [f'<line x1="{x:.2f}" x2="{x:.2f}" y1="116" y2="{end}" stroke="#e0e6eb"/>',text(round(x,2),end+22,f'{value:.1f}',12,anchor='middle')]
    for i,group in enumerate(groups):
        y=130+i*stride;parts += [text(30,y+23,group['label'],15)]
        for j,(value,(_,colour)) in enumerate(zip(group['values'],series)):
            width=value/maximum*(x1-x0);bar_y=y+j*29
            parts += [f'<rect x="{x0}" y="{bar_y}" width="{width:.2f}" height="21" fill="{colour}"/>',text(round(x0+width+8,2),bar_y+16,f'{value:.2f}',12)]
    parts += [text(620,end+47,unit,13,anchor='middle'),text(30,height-32,footer,12),text(30,height-13,'One observation per cell. No confidence intervals or percentile claims.',12)]
    save(relative,parts)


def render_game_fleets():
    relative = 'data/rocm-10.1/falling-blocks-fleet-outcomes-2026-10-18.csv'
    if not (ROOT/relative).exists():
        return
    rows = read(relative)
    by_key = {(row['fleet'], int(row['agent'])): row for row in rows}
    groups = [dict(label=f'Agent {agent}', values=[
        float(by_key[(fleet, agent)]['model_seconds']) / 60
        for fleet in ('dual-card', 'single-card-retry')]) for agent in range(4)]
    grouped('graphs/rocm-10.1/falling-blocks-completed-fleet-model-time-2026-10-18.svg',
            'ROCm 10.1 · Falling Blocks · completed fleets',
            'Four clean deliveries per fleet. Fleet wall: dual 30:10; single-card retry 75:23.',
            groups, [('Dual · 32,768-token budget / 60-min cap', BLUE),
                     ('Single retry · 65,536-token budget / 90-min cap', ORANGE)],
            'Cumulative reported model time per agent (minutes)',
            'Client context and compaction reserve also changed. Not an isolated GPU-count speedup.')


def main():
    render_game_fleets()
    old=read('data/rocm-7.14/historical-agent-workloads.csv')
    by_id={r['case_id']:r for r in old}
    selected=[by_id[k] for k in ('CASE-43','CASE-44','CASE-28','CASE-27')]
    old_rows=[dict(label=f"{r['agent_count']} agent(s) · {'short reference' if i<2 else 'RAM16'}",mean=r['mean_ttft_s'],maximum=r['max_ttft_s'],detail=f"{r['successful_turns']} turns; max observed context {float(r['max_context_k_tokens']):.1f}k; {r['errors']} errors") for i,r in enumerate(selected)]
    single_report('graphs/rocm-7.14/single-card-text-growth-historical.svg',
                  'ROCm 7.14 · single R9700 · historical context-growth references',
                  '131k context-limit research; 1–2-agent short references and 3–4-agent RAM16 milestones differ in history/settings.',
                  old_rows,'Targets were approximately 126k; these runs do not prove simultaneous sustained 131k per agent.')
    current=read('data/rocm-10.1/single-card-gpu-a-text-growth-2026-10-18.csv')
    single_report('graphs/rocm-10.1/single-card-gpu-a-text-growth-2026-10-18.svg',
                  'ROCm 10.1 · single R9700, GPU A · 18 October 2026',
                  'TP1 · MTP4 · CPU KV10 GiB · 131070-token context limit · four completed synthetic growth cases.',
                  [dict(label=f"{r['agents']} agent(s)",mean=r['ttft_avg_s'],maximum=r['ttft_max_s'],detail=f"{r['turns_ok']} turns; max observed context {int(r['max_depth_tok'])/1000:.1f}k; {r['errors']} errors") for r in current],
                  'Mean/max TTFT from completed summaries. Short outputs; no sustained full131k or real-agent qualification.')
    follow=read('data/rocm-10.1/follow-up-single-vs-dual-text-growth-2026-10-18.csv')
    matrix={(r['profile'],int(r['agents'])):r for r in follow}
    for metric,suffix,title,unit,foot in [
        ('mean_ttft_seconds','mean-ttft','Mean TTFT','Mean TTFT (seconds)','Completed synthetic cases; configuration differences remain. Not an isolated ROCm-version comparison.'),
        ('max_ttft_seconds','maximum-ttft','Maximum observed TTFT','Maximum observed TTFT (seconds)','Maximum from each finite run; not p95/p99. Zero client errors does not establish interactive usability.'),
        ('mean_request_decode_tokens_s','request-decode-rate','Mean per-request decode estimate','Per-request decode estimate (tokens/s)','Short synthetic outputs; not fleet throughput, prompt-processing speed or real-agent productivity.')]:
        groups=[dict(label=f'{n} agent(s)',values=[float(matrix[(profile,n)][metric]) for profile in ('gpu-a','dual')]) for n in range(1,5)]
        grouped(f'graphs/rocm-10.1/follow-up-single-vs-dual-{suffix}-2026-10-18.svg',f'ROCm 10.1 · single vs dual R9700 · {title}',
                'Eight completed follow-up cells; ~126k context growth target. TP, MTP, slots and context limits differ.',groups,[('Single R9700 · GPU A',BLUE),('Dual R9700',ORANGE)],unit,foot)
    old_by_agents={int(row['agent_count']):row for row in selected}
    grouped('graphs/rocm-10.1/single-card-rocm-7.14-ram16-vs-rocm-10.1-ram10.svg',
            'Single R9700 · historical ROCm 7.14/RAM16 vs ROCm 10.1/RAM10',
            'Different tier budgets, GPU utilisation and image patches: deployment observations, not a causal ROCm A/B.',
            [dict(label=f'{n} agents',values=[float(old_by_agents[n]['mean_ttft_s']),float(matrix[('gpu-a',n)]['mean_ttft_seconds'])]) for n in (3,4)],
            [('ROCm 7.14 · historical RAM16',PURPLE),('ROCm 10.1 · RAM10',BLUE)],'Mean TTFT (seconds)',
            'RAM16 is historical; later host slowdown prevents recommending a tier increase without memory headroom.')
    sources=['data/rocm-7.14/historical-agent-workloads.csv','data/rocm-10.1/single-card-gpu-a-text-growth-2026-10-18.csv','data/rocm-10.1/follow-up-single-vs-dual-text-growth-2026-10-18.csv']
    fleet_source = 'data/rocm-10.1/falling-blocks-fleet-outcomes-2026-10-18.csv'
    if (ROOT/fleet_source).exists():
        sources.append(fleet_source)
    (ROOT/'graphs/rocm-10.1/follow-up-chart-sources.json').write_text(json.dumps({'sources':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},'generator':'tools/render_follow_up.py','notes':'Generated solely from existing local CSV summaries. No server access or fresh telemetry audit.'},indent=2)+'\n')


if __name__=='__main__':
    main()
