#!/usr/bin/env python3
"""Transform the local R9700 archive into a sanitized, derived research release.

No source files are copied. Recorder epochs become relative elapsed time;
monotonic counters become rates or interval averages; host command strings,
conversation corpora, logs, local paths, and server snapshots are not emitted.
"""
import csv, math, os, json, hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
SOURCE=Path(os.environ['RESEARCH_SOURCE']).expanduser().resolve()  # separately held source archive
OUT=HERE/'data'

def num(value):
 try:
  x=float(value)
  return x if math.isfinite(x) else None
 except (TypeError,ValueError): return None

def roundv(x): return '' if x is None else round(x,3)
def fmt_id(i): return f'RUN-{i:02d}'

def family_from_name(name):
 s=name.lower()
 if 'tainted' in s:return 'scheduler trial · tainted'
 if 'dead' in s:return 'capacity trial · incomplete'
 if '_cmp_' in s:return 'context compaction'
 if 'ram16' in s:return 'single-card RAM16 tier'
 if s.startswith('metrics_mem_'):return 'host memory and I/O'
 if 'rocm10' in s:return 'dual-card ROCm stress'
 if 'v8_' in s:return 'runtime / JIT comparison'
 if 'sanity' in s:return 'instrumentation sanity'
 if 'e13' in s:return 'scheduler tuning'
 if any(x in s for x in ('e14','e15','e16','e18','e19')):return 'KV tier / storage / link'
 if any(x in s for x in ('e23','e24','e25')):return 'fleet follow-up'
 return 'engine telemetry'

# Counters are converted to interval rates. Histograms are converted to interval means.
COUNTERS={
 'p_all':('prompt_tokens_s',1),'p_comp':('prompt_compute_credit_rate_tokens_s',1),
 'p_hit':('prefix_cache_tokens_s',1),'p_xfer':('tier_transfer_tokens_s',1),
 'gen':('generated_tokens_s',1),'ext_hits':('tier_hits_s',1),'ext_q':('tier_queries_s',1),
 'off_load_b':('tier_load_mib_s',1/1048576),'off_load_t':('tier_loads_s',1),
 'off_store_b':('tier_store_mib_s',1/1048576),'spec_d':('draft_tokens_s',1),
 'spec_acc':('accepted_draft_tokens_s',1),'spec_dt':('speculative_time_s_per_s',1),
 'preempt':('preemptions_s',1),'succ':('successful_requests_s',1)
}
HISTS={'q':('queue_mean_ms','q_sum','q_cnt'),'pf':('prefill_mean_ms','pf_sum','pf_cnt'),
       'ttft':('ttft_mean_ms','ttft_sum','ttft_cnt'),'itl':('itl_mean_ms','itl_sum','itl_cnt'),
       'iter':('iteration_mean_ms','iter_sum','iter_cnt')}
GAUGES={'running':'requests_running','waiting':'requests_waiting'}

def convert_engine(source, dest, run_id):
 with source.open(newline='',encoding='utf-8-sig') as f:
  reader=csv.DictReader(f); raw=list(reader); fields=reader.fieldnames or []
 if not raw: return 0
 times=[num(r.get('t')) for r in raw]; times=[x for x in times if x is not None]
 if not times:return 0
 t0=times[0]; names=['run_id','elapsed_seconds']+list(GAUGES.values())+['gpu_kv_pool_pct','cpu_tier_signal_pct']+[x[0] for x in COUNTERS.values()]+[x[0] for x in HISTS.values()]
 prev={}; prev_counts={}; out=[]
 for r in raw:
  t=num(r.get('t'))
  if t is None:continue
  dt=max(t-prev.get('_time',t),0)
  row={'run_id':run_id,'elapsed_seconds':roundv(t-t0)}
  for key,name in GAUGES.items(): row[name]=roundv(num(r.get(key)))
  for key,name in [('kv_gpu','gpu_kv_pool_pct'),('kv_cpu','cpu_tier_signal_pct')]:
   v=num(r.get(key)); row[name]=roundv(v*100 if v is not None else None)
  for key,(name,mult) in COUNTERS.items():
   v=num(r.get(key)); old=prev.get(key)
   row[name]=roundv(max(0,(v-old)/dt)*mult if v is not None and old is not None and dt>0 else None)
   if v is not None:prev[key]=v
  for prefix,(name,sk,ck) in HISTS.items():
   sv,cv=num(r.get(sk)),num(r.get(ck)); os,oc=prev.get(sk),prev_counts.get(ck)
   if sv is not None and cv is not None and os is not None and oc is not None and cv>oc:
    row[name]=roundv((sv-os)/(cv-oc)*1000)
   else:row[name]=''
   if sv is not None:prev[sk]=sv
   if cv is not None:prev_counts[ck]=cv
  prev['_time']=t; out.append(row)
 with dest.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=names);w.writeheader();w.writerows(out)
 return len(out)

def convert_memory(source,dest,run_id):
 with source.open(newline='',encoding='utf-8-sig') as f:
  reader=csv.DictReader(f);raw=list(reader);fields=reader.fieldnames or []
 if not raw:return 0
 times=[num(r.get('t')) for r in raw];times=[x for x in times if x is not None]
 if not times:return 0
 t0=times[0]; prev={}; names=['run_id','elapsed_seconds','available_memory_gib','page_cache_gib','swap_used_gib','vram_used_gib','vram_total_gib','gpu_kv_usage_pct','cpu_tier_usage_pct','requests_running','requests_waiting','preemptions_delta','prefix_hits_s','prefix_queries_s','allocation_failures_delta','loop_read_mib_s','loop_write_mib_s','nvme_read_mib_s','nvme_write_mib_s','image_store_gib'];out=[]
 scales={'mem_avail_mb':('available_memory_gib',1/1024),'mem_cached_mb':('page_cache_gib',1/1024),'swap_used_mb':('swap_used_gib',1/1024),'vram_used_mb':('vram_used_gib',1/1024),'vram_total_mb':('vram_total_gib',1/1024),'kv_usage':('gpu_kv_usage_pct',100),'off_cpu_usage':('cpu_tier_usage_pct',100),'running':('requests_running',1),'waiting':('requests_waiting',1),'img_alloc_gb':('image_store_gib',1)}
 counter={'preemptions':'preemptions_delta','p_hits':'prefix_hits_s','p_queries':'prefix_queries_s','off_alloc_fail':'allocation_failures_delta','loop_r_mb':'loop_read_mib_s','loop_w_mb':'loop_write_mib_s','nvme0_r_mb':'nvme_read_mib_s','nvme0_w_mb':'nvme_write_mib_s'}
 for r in raw:
  t=num(r.get('t'))
  if t is None:continue
  dt=max(t-prev.get('_time',t),0);row={'run_id':run_id,'elapsed_seconds':roundv(t-t0)}
  for key,(name,mult) in scales.items():row[name]=roundv((num(r.get(key))*mult) if num(r.get(key)) is not None else None)
  for key,name in counter.items():
   v=num(r.get(key));old=prev.get(key)
   row[name]=roundv(max(0,(v-old)/dt) if v is not None and old is not None and dt>0 else None)
   if v is not None:prev[key]=v
  prev['_time']=t;out.append(row)
 with dest.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=names);w.writeheader();w.writerows(out)
 return len(out)

def build_cases(sources,dest):
 combined={}
 for source in sources:
  if not source.exists():continue
  with source.open(newline='',encoding='utf-8-sig') as f: current=list(csv.DictReader(f))
  for r in current:combined[r.get('label','')]=r  # newer root summary wins over dated snapshots
 rows=[combined[k] for k in sorted(combined) if k]
 names=['case_id','agent_count','image_mode','depth_cap_k_tokens','successful_turns','errors','duration_minutes','max_context_k_tokens','mean_ttft_s','max_ttft_s','fleet_decode_tokens_s','per_agent_decode_tokens_s','itl_p99_ms','ttft_0_30k_s','ttft_30_60k_s','ttft_60_90k_s','ttft_90_120k_s','ttft_120k_plus_s']
 out=[]
 for i,r in enumerate(rows,1):
  label=r.get('label','').lower();case_id=f'CASE-{i:02d}'
  meta=next((e for e in json.loads((OUT/'case-catalog.json').read_text()) if e['legacy_id']==case_id),None)
  if meta is None or meta['source_label_sha256']!=hashlib.sha256(r.get('label','').encode()).hexdigest():raise ValueError('Source case identity changed; review catalogue before rebuilding')
  # The coarse label keeps only experimental family/count/depth, dropping names and command payloads.
  family='compaction' if 'cmp' in label else 'ram-tier' if 'ram' in label else 'stress' if 'stress' in label else 'capacity' if '100k' in label or '131k' in label or '150k' in label else 'comparison'
  row={'case_id':case_id,'agent_count':r.get('agents',''),'image_mode':'with-images' if r.get('images')=='1' else 'text-only','depth_cap_k_tokens':roundv((num(r.get('depth_cap')) or 0)/1000),'successful_turns':r.get('turns_ok',''),'errors':r.get('errors',''),'duration_minutes':roundv((num(r.get('wall_s')) or 0)/60),'max_context_k_tokens':roundv((num(r.get('max_depth_tok')) or 0)/1000),'mean_ttft_s':roundv(num(r.get('ttft_avg_s'))),'max_ttft_s':roundv(num(r.get('ttft_max_s'))),'fleet_decode_tokens_s':roundv(num(r.get('decode_tps'))),'per_agent_decode_tokens_s':roundv(num(r.get('tg_avg'))),'itl_p99_ms':roundv(num(r.get('tp99_itl_ms')))}
  row['case_family']=family
  for col in names[13:]:row[col]=roundv(num(r.get(col.replace('_s',''))))
  if case_id in {e['legacy_id'] for e in json.loads((OUT/'case-catalog.json').read_text()) if e['included']}:out.append(row)
 # Include a coarse family code, not original experiment names or command metadata.
 names.insert(1,'case_family')
 with dest.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=names);w.writeheader();w.writerows(out)
 return len(out)

def main():
 if not SOURCE.is_dir():raise SystemExit(f'Source archive not found: {SOURCE}')
 obsolete=HERE/'docs'/'ARCHIVE-SIGNALS.md'
 if obsolete.exists():obsolete.unlink()
 OUT.mkdir(exist_ok=True)
 for old in list(OUT.glob('RUN-*-telemetry.csv'))+[OUT/'case-summary.csv']:
  if old.exists():old.unlink()
 selection={e['legacy_id']:e for e in json.loads((OUT/'telemetry-catalog.json').read_text())}
 sources=sorted(SOURCE.joinpath('data').glob('*.csv'));catalog=[];i=0
 for src in sources:
  if src.name=='bench_results.csv':continue
  i+=1;rid=fmt_id(i)
  if rid not in selection:raise ValueError('Unreviewed telemetry source; update catalogue before rebuilding')
  if selection[rid]['source_name_sha256']!=hashlib.sha256(src.name.encode()).hexdigest():raise ValueError('Source telemetry identity changed; review catalogue before rebuilding')
  if not selection[rid]['included']:continue
  dest_dir=OUT/selection[rid]['version'];dest_dir.mkdir(exist_ok=True)
  dst=dest_dir/(selection[rid]['slug']+'.csv')
  with src.open(newline='',encoding='utf-8-sig') as f:header=next(csv.reader(f),[])
  if 'mem_avail_mb' in header:n=convert_memory(src,dst,rid);kind='host-memory'
  elif 't' in header:n=convert_engine(src,dst,rid);kind='engine-metrics'
  else:n=0;kind='empty-or-unrecognized'
  if n==0 and dst.exists():dst.unlink()
  status='tainted' if 'tainted' in src.name.lower() else 'failed / incomplete' if 'dead' in src.name.lower() else 'empty' if n==0 else 'read with journal context'
  catalog.append((rid,kind,family_from_name(src.name),n,status))
 cases=build_cases([SOURCE/'bench_results.csv',SOURCE/'bench_results.csv.bak-20261016',SOURCE/'data'/'bench_results.csv'],OUT/'case-summary.csv')
 (HERE/'docs'/'DATA-DICTIONARY.md').write_text('# Derived data dictionary\n\nAll tables here are generated by `tools/build_release.py` from the private working archive. Original files are not distributed. Every telemetry series uses a relative elapsed-time axis; engine monotonic counters are converted to rates or interval means, fractions become percentages, memory is converted to GiB, and command strings, absolute epochs, and host paths are omitted. Blank interval-rate cells indicate the first sample or insufficient count delta. Values are rounded to three decimals.\n\n## Prompt-compute caveat\n\n`prompt_compute_credit_rate_tokens_s` is the change in a cumulative prompt-compute counter divided by the recorder interval. The source counter credits prompt work in bursts at request completion, so a burst can appear as an implausibly high one-interval rate (for example, about 65,000 tokens/s in `RUN-01`). This is a counter-credit artifact, not sustained prefill throughput (PP). Do not use this field or its graph as a PP benchmark. The released telemetry does not include a validated per-run PP series; report PP as unavailable for these traces.\n\n| Series ID | Data family | Samples | Interpretation flag |\n|---|---|---:|---|\n'+''.join(f'| {a} | {c} | {d} | {e} |\n' for a,b,c,d,e in catalog)+f'\n`case-summary.csv` contains {cases} derived per-run records from the current, dated, and backup benchmark summaries. Labels are generalized into experiment families; launch command strings are omitted. The header-only telemetry source is represented as an empty flag and emits no series.\n',encoding='utf-8')
 print(f'Built {sum(e["included"] for e in selection.values())} selected telemetry series and {cases} historical summaries; exploratory results omitted.')
 from organise_results import main as organise
 organise()

if __name__=='__main__':
 main()
