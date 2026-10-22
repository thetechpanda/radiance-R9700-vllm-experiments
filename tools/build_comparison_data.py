#!/usr/bin/env python3
"""Rebuild the single-card comparison; profile identity comes from the recorded config."""
import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/rocm-10.1'

def read(name):
 with (DATA/name).open(newline='') as f:return list(csv.DictReader(f))

def main():
 rows=[]
 for r in read('follow-up-single-vs-dual-text-growth-2026-10-18.csv'):
  if r['profile']!='gpu-a':continue
  rows.append(dict(engine_setup='vllm-radiance single-card (historical growth family, MTP-4)',agents=r['agents'],depth_cap_tokens=126000,turns=r['completed_turns'],wall=r['client_wall_seconds'],ttft_avg_s=r['mean_ttft_seconds'],ttft_max_s=r['max_ttft_seconds'],decode_per_request_tps=r['mean_request_decode_tokens_s'],source='follow-up-single-vs-dual-text-growth-2026-10-18.csv',max_observed_context_tokens=r['max_observed_context_tokens'],prefix_tier_mib=10240))
 for name,label,tier in [('radiance-single-card-2026-10-22.csv','radiance TP1 MTP-4',13312),('radiance-campaign-2026-10-21.csv','radiance TP2 MTP-4',10240)]:
  for r in read(name):
   if r['spec_mode']!='mtp' or r['arm'].startswith('R9'):continue
   rows.append(dict(engine_setup=label,agents=r['agents'],depth_cap_tokens=r['depth_cap_tokens'],turns=r['turns_ok'],wall=r['wall_s'],ttft_avg_s=r['ttft_avg_s'],ttft_max_s=r['ttft_max_s'],decode_per_request_tps=r['tg_avg_tokens_s'],source=name,max_observed_context_tokens=r['max_depth_tokens'],prefix_tier_mib=tier))
 for r in rows:
  r['seconds_per_turn']=str((Decimal(r.pop('wall'))/Decimal(r['turns'])).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
 columns=['engine_setup','agents','depth_cap_tokens','turns','seconds_per_turn','ttft_avg_s','ttft_max_s','decode_per_request_tps','source','max_observed_context_tokens','prefix_tier_mib']
 with (DATA/'radiance-single-card-comparison-2026-10-22.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader();writer.writerows(rows)
 # Correct released artifact paths; no change to outcomes or recorded checks.
 path=DATA/'radiance-falling-blocks-fleet-2026-10-21.csv'
 with path.open(newline='') as f:reader=csv.DictReader(f);names=reader.fieldnames;fleet=list(reader)
 for r in fleet:r['game_file']=r['game_file'].replace('/falling-blocks.html','/index.html')
 with path.open('w',newline='') as f:writer=csv.DictWriter(f,fieldnames=names);writer.writeheader();writer.writerows(fleet)
 print(f'{len(rows)} comparison rows rebuilt; {len(fleet)} artifact paths checked')
if __name__=='__main__':main()
