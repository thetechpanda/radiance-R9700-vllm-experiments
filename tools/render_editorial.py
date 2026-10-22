#!/usr/bin/env python3
"""Reproducible comparison figures from public CSVs; no inference or raw archive access."""
import csv
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'graphs/rocm-10.1'
BLUE, AMBER, GREEN, MUTED = '#62c6ff', '#ffbd69', '#6ae1bc', '#9cacc0'
SOURCES = [
 'data/rocm-10.1/radiance-campaign-2026-10-21.csv',
 'data/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.csv',
 'data/rocm-10.1/radiance-single-card-2026-10-22.csv',
 'data/rocm-10.1/follow-up-single-vs-dual-text-growth-2026-10-18.csv',
 'data/rocm-10.1/radiance-pool-ceiling-2026-10-22.csv',
]

def read(path):
 with (ROOT/path).open(newline='') as f: return list(csv.DictReader(f))

def text(x,y,value,size=16,fill='#e9edf3',anchor='start',weight='normal'):
 return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{html.escape(str(value))}</text>'

def begin(title,subtitle,height):
 return [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title desc">',f'<title id="title">{html.escape(title)}</title>',f'<desc id="desc">{html.escape(subtitle)}</desc>','<rect width="1200" height="100%" rx="16" fill="#0e1828"/>','<g font-family="system-ui,sans-serif">',text(36,42,'R9700 / MEASURED FIELD NOTES',12,GREEN,weight='bold'),text(36,83,title,29,weight='bold'),text(36,115,subtitle,15,MUTED)]

def finish(name,parts):
 (OUT/name).write_text('\n'.join(parts+['</g></svg>'])+'\n')
 print(name)

def grid(p,x,y,w,h,maximum,ticks=4):
 for i in range(ticks+1):
  pos=x+w*i/ticks
  p.append(f'<line x1="{pos}" x2="{pos}" y1="{y}" y2="{y+h}" stroke="#29364a"/>')
  value=maximum*i/ticks
  label=f'{value:,.0f}' if maximum>=1000 else f'{value:g}'
  p.append(text(pos,y+h+25,label,13,MUTED,'middle'))

def wall_chart(new,old):
 p=begin('Same workload family. Two different engine deployments.','Total wall time, seconds (lower is better) · 10 turns per agent · 126k growth cap',740)
 for col,(mode,label) in enumerate([('none','Speculation off'),('mtp','MTP-4')]):
  left=36+col*588; x=left+92; y=215; w=400
  p += [text(left,167,label,22,weight='bold')]
  grid(p,x,y,w,350,600)
  for i,n in enumerate(range(1,5)):
   a=next(r for r in old if r['arm'].startswith(('Y' if mode=='none' else 'Z')+str(n)+'-'))
   b=next(r for r in new if int(r['agents'])==n and r['spec_mode']==mode and int(r['images'])==0 and not r['arm'].startswith('R9'))
   yy=y+12+i*85
   p.append(text(left,yy+30,f'{n} agent'+('s' if n>1 else ''),15))
   for j,(r,c) in enumerate([(a,AMBER),(b,BLUE)]):
    v=float(r['wall_s']);by=yy+j*27
    p += [f'<rect x="{x}" y="{by}" width="{v/600*w:.2f}" height="20" rx="3" fill="{c}"/>',text(x+v/600*w+8,by+15,f'{v:.1f}',13,c)]
  p.append(text(x+w/2,613,'Total wall time (s) · zero-based scale',14,MUTED,'middle'))
 p += [text(36,659,'● vllm-radiance / 19 Oct / BF16 KV / rev 9dba8a05',15,AMBER),text(625,659,'● radiance / 21 Oct / FP8 KV / rev 81a28ee7',15,BLUE),text(36,693,'Historical comparison; checkpoint revision and cache format differ. One observation per cell, no confidence intervals.',14,MUTED),text(36,718,'Sources: dual-r9700-agent-count-sweep-2026-10-19.csv (Y/Z) + radiance-campaign-2026-10-21.csv (R1–R6).',12,MUTED)]
 finish('engine-wall-comparison.svg',p)

def delta_chart(new,old):
 p=begin('Where the wall-time differences land','radiance relative to historical vllm-radiance · (radiance / baseline − 1) × 100',630)
 x=600; scale=17; top=205
 for v in [-20,-10,0,10,20]:
  xx=x+v*scale
  p += [f'<line x1="{xx}" x2="{xx}" y1="175" y2="510" stroke="#42546d"/>',text(xx,544,f'{v:+d}%' if v else '0%',14,MUTED,'middle')]
 for i,n in enumerate(range(1,5)):
  yy=top+i*77;p.append(text(36,yy+21,f'{n} agent'+('s' if n>1 else ''),18))
  for j,(mode,c,prefix) in enumerate([('none',AMBER,'Y'),('mtp',BLUE,'Z')]):
   a=next(r for r in old if r['arm'].startswith(prefix+str(n)+'-'))
   b=next(r for r in new if int(r['agents'])==n and r['spec_mode']==mode and int(r['images'])==0 and not r['arm'].startswith('R9'))
   v=(float(b['wall_s'])/float(a['wall_s'])-1)*100;by=yy+j*26
   p += [f'<rect x="{min(x,x+v*scale):.2f}" y="{by}" width="{abs(v)*scale:.2f}" height="19" rx="3" fill="{c}"/>',text(x+v*scale+(-8 if v<0 else 8),by+15,f'{v:+.1f}%',14,c,'end' if v<0 else 'start')]
 p += [text(230,159,'SHORTER WALL',12,MUTED),text(835,159,'LONGER WALL',12,MUTED),text(36,579,'● Speculation off',15,AMBER),text(260,579,'● MTP-4',15,BLUE),text(36,611,'Observed deltas, not isolated engine effects. The earlier ≈15% repeat spread is context, not a significance test.',14,MUTED)]
 finish('engine-wall-deltas.svg',p)

def single_chart(single,old):
 p=begin('One card: less waiting, less tested context','Four-agent results · different run lengths, host tiers and model representations',760)
 a=next(r for r in old if r['profile']=='gpu-a' and r['agents']=='4');b=single[-1]
 panels=[('Mean TTFT',float(a['mean_ttft_seconds']),float(b['ttft_avg_s']),120,'s · lower is better'),('Maximum observed TTFT',float(a['max_ttft_seconds']),float(b['ttft_max_s']),700,'s · lower is better'),('Maximum observed prompt depth',float(a['max_observed_context_tokens'])/1000,float(b['max_depth_tokens'])/1000,140,'k tokens · higher is deeper'),('Reported request generation estimate',float(a['mean_request_decode_tokens_s']),float(b['tg_avg_tokens_s']),30,'tok/s · see metric caveat')]
 for i,(title,av,bv,mx,unit) in enumerate(panels):
  left=36+(i%2)*588;top=170+(i//2)*240;x=left+35;w=445
  p += [text(left,top,title,20,weight='bold'),text(left,top+24,unit,13,MUTED)]
  grid(p,x,top+52,w,94,mx)
  for j,(v,c) in enumerate([(av,AMBER),(bv,BLUE)]):
   yy=top+58+j*42
   p += [f'<rect x="{x}" y="{yy}" width="{v/mx*w:.2f}" height="26" rx="4" fill="{c}"/>',text(x+v/mx*w+7,yy+19,f'{v:.2f}' if i!=2 else f'{v:.1f}',14,c)]
 p += [text(36,675,'● vllm-radiance / MTP-4 / 10 GiB tier / 126k cap / 114 timed turns',14,AMBER),text(36,702,'● radiance / MTP-4 / 13 GiB tier / 88.9k cap / 32 turns',14,BLUE),text(36,732,'Request generation estimates use different export definitions; not aggregate throughput or a controlled speedup.',14,MUTED)]
 finish('single-card-tradeoffs.svg',p)

def pool_chart(rows):
 p=begin('The pool grew when the allocation changed','Boot-measured GPU KV capacity · this is allocated storage, not six-agent throughput',650)
 chosen=rows[:4];x=400;w=640;mx=1400000
 grid(p,x,180,w,315,mx)
 for i,r in enumerate(chosen):
  y=194+i*74;v=int(r['pool_tokens']);c=AMBER if i==1 else BLUE
  label=r['config'].replace(' context','').replace('131072','131k').replace('204800','200k')
  p += [text(36,y+23,label,17),f'<rect x="{x}" y="{y}" width="{v/mx*w:.2f}" height="32" rx="4" fill="{c}"/>',text(x+v/mx*w+10,y+23,f'{v:,}',16,c)]
 p += [text(720,548,'GPU pool tokens · zero-based scale',14,MUTED,'middle'),text(36,587,'524,304 → 1,228,816 tokens = +134.4% allocated capacity; cards unchanged, slots/context changed.',17,GREEN),text(36,620,'Source: radiance-pool-ceiling-2026-10-22.csv. 200k validation: boot allocation + reported single-prompt probe only.',13,MUTED)]
 finish('memory-allocation.svg',p)

def legacy_single_chart():
 rows=read('data/rocm-10.1/radiance-single-card-comparison-2026-10-22.csv')
 p=begin('Single-card history: time per turn and time to first content','All profiles use MTP-4; unequal run lengths, context depths, representations and 10/13 GiB host tiers',760)
 series=[('vllm-radiance single-card',AMBER),('radiance TP1',BLUE),('radiance TP2',GREEN)]
 for col,(key,title,mx) in enumerate([('seconds_per_turn','Whole-cell wall / timed turns (s)',40),('ttft_avg_s','Mean TTFT (s)',120)]):
  left=36+col*588;x=left+75;w=405;y=215
  p.append(text(left,165,title,20,weight='bold'));grid(p,x,y,w,350,mx)
  for i,n in enumerate(range(1,5)):
   yy=y+5+i*87;p.append(text(left,yy+28,f'n={n}',15))
   for j,(prefix,c) in enumerate(series):
    r=next(r for r in rows if r['engine_setup'].startswith(prefix) and int(r['agents'])==n)
    v=float(r[key]);by=yy+j*22
    p += [f'<rect x="{x}" y="{by}" width="{v/mx*w:.2f}" height="16" rx="2" fill="{c}"/>',text(x+v/mx*w+6,by+13,f'{v:.2f}',12,c)]
 p += [text(36,631,'● vllm-radiance GPU A',15,AMBER),text(430,631,'● radiance TP1',15,BLUE),text(825,631,'● radiance TP2',15,GREEN),text(36,670,'n4 TP1 radiance: 88,913-token growth cap / 99,075 observed maximum / 32 total turns.',15,MUTED),text(36,698,'n4 historical GPU A: 126,000-token growth cap / 126,691 observed maximum / 114 timed turns.',15,MUTED),text(36,732,'Source: radiance-single-card-comparison-2026-10-22.csv. Unequal-depth observations, not an engine speedup.',13,MUTED)]
 finish('radiance-single-card-comparison-2026-10-22.svg',p)

def legacy_pool_chart(rows):
 p=begin('GPU allocation and host history are different storage','Solid = recorded allocation / tier print; dashed = projection, not boot measurement',840)
 x=470;w=550;mx=1400000
 grid(p,x,180,w,490,mx)
 for i,r in enumerate(rows):
  yy=192+i*66;v=int(r['pool_tokens']);projected='projection' in r['kind'];host=r['config'].startswith('host')
  c=GREEN if host else BLUE
  label=r['config'].replace(' context','').replace('131072','131k').replace('204800','200k')
  p += [text(36,yy+20,label,15),f'<rect x="{x}" y="{yy}" width="{v/mx*w:.2f}" height="26" rx="3" fill="{c if not projected else "none"}" stroke="{c}" stroke-dasharray="{ "7 5" if projected else "none"}"/>',text(x+v/mx*w+9,yy+20,f'{v:,}',14,c)]
 p += [text(36,735,'GPU tokens store live KV; host-tier tokens store completed conversation state. Do not sum for live concurrency.',14,MUTED),text(36,767,'Driver-max tier is a theoretical cap before vision/host reservations; it is not a usable 15.29 GiB prefix budget.',14,MUTED),text(36,805,'Source: radiance-pool-ceiling-2026-10-22.csv. Latest allocation is not a sustained six-agent 200k benchmark.',13,MUTED)]
 finish('radiance-pool-ceiling-2026-10-22.svg',p)

def main():
 new,old,single,follow,pools=[read(p) for p in SOURCES]
 wall_chart(new,old);delta_chart(new,old);single_chart(single,follow);pool_chart(pools)
 (OUT/'radiance-campaign-2026-10-21.svg').write_bytes((OUT/'engine-wall-comparison.svg').read_bytes())
 legacy_single_chart();legacy_pool_chart(pools)
 manifest={'sources':{s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in SOURCES+['data/rocm-10.1/radiance-single-card-comparison-2026-10-22.csv']},'formula':'percent change = (radiance / specified baseline - 1) * 100','limitations':['Historical deployments; no isolated engine A/B.','Different target revisions and KV formats in the dual-engine comparison.','Unequal depth, run length, target representation and host tier in single-card comparison.','No confidence intervals. Approximately 15% earlier repeat spread is not a significance threshold.','Boot allocation is not sustained concurrency qualification.']}
 (OUT/'editorial-chart-sources.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':main()
