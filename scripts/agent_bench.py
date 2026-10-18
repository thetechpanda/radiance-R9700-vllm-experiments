#!/usr/bin/env python3
"""Concurrent OpenAI-compatible agent-load probe using generated synthetic context."""
import argparse, concurrent.futures, json, os, random, threading, time, urllib.error, urllib.request

def synthetic_result(agent, turn, chars):
    rng=random.Random(agent*100000+turn)
    alphabet='abcdef0123456789'
    lines=[]; size=0; i=0
    while size<chars:
        line=f"record_{i:05d} = {{key: '{''.join(rng.choice(alphabet) for _ in range(18))}', value: {rng.randrange(100000)}}}\n"
        lines.append(line);size+=len(line);i+=1
    return ''.join(lines)[:chars]

def stream_request(url, model, messages, api_key, timeout):
    body={'model':model,'messages':messages,'stream':True,'stream_options':{'include_usage':True}}
    headers={'Content-Type':'application/json','Accept':'text/event-stream'}
    if api_key:headers['Authorization']='Bearer '+api_key
    req=urllib.request.Request(url,data=json.dumps(body).encode(),headers=headers,method='POST')
    start=time.perf_counter();first=None;usage={};text=[]
    with urllib.request.urlopen(req,timeout=timeout) as response:
        for raw in response:
            line=raw.decode('utf-8','replace').strip()
            if not line.startswith('data:'):continue
            payload=line[5:].strip()
            if payload=='[DONE]':break
            try:event=json.loads(payload)
            except json.JSONDecodeError:continue
            if event.get('usage'):usage=event['usage']
            choices=event.get('choices') or []
            if choices:
                delta=(choices[0].get('delta') or {}).get('content')
                if delta:
                    if first is None:first=time.perf_counter()
                    text.append(delta)
    end=time.perf_counter()
    return {'ttft_s':(first or end)-start,'elapsed_s':end-start,'text':''.join(text),
            'usage':usage,'status':'ok'}

def run_agent(agent,args,api_key):
    msgs=[{'role':'system','content':'You are a concise coding assistant. Analyze the synthetic records and report a short summary.'}]
    turns=[]
    for turn in range(args.turns):
        msgs.append({'role':'user','content':f"Agent {agent}, step {turn+1}. Review this generated test output and summarize anomalies:\n"+synthetic_result(agent,turn,args.max_tool_chars)})
        try:
            result=stream_request(args.base_url.rstrip('/')+'/chat/completions',args.model,msgs,api_key,args.timeout)
            msgs.append({'role':'assistant','content':result['text']})
            usage=result['usage']; out_tok=usage.get('completion_tokens')
            if out_tok is None:out_tok=max(1,len(result['text'])//4)
            turns.append({'ttft_s':result['ttft_s'],'elapsed_s':result['elapsed_s'],'output_tokens':out_tok,'usage_reported':bool(usage),'status':'ok'})
        except Exception as exc:
            turns.append({'status':'error','error_type':type(exc).__name__,'message':str(exc)[:240]})
            break
    return {'agent':agent,'turns':turns}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-url',default='http://127.0.0.1:8000/v1');p.add_argument('--model',required=True)
    p.add_argument('--agents',type=int,default=4);p.add_argument('--turns',type=int,default=12)
    p.add_argument('--max-tool-chars',type=int,default=3000);p.add_argument('--timeout',type=float,default=300)
    p.add_argument('--output',help='write a JSON summary to this path; no prompts, responses, or credentials are saved')
    p.add_argument('--api-key-env',default='RADIANCE_API_KEY',help='environment variable holding the API key')
    a=p.parse_args()
    if min(a.agents,a.turns,a.max_tool_chars)<=0:p.error('agents, turns, and max-tool-chars must be positive')
    endpoint=a.base_url.rstrip('/')
    if not endpoint.endswith('/v1'):p.error('--base-url should end in /v1')
    key=os.environ.get(a.api_key_env,''); start=time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.agents) as pool:
        agents=list(pool.map(lambda n:run_agent(n,a,key),range(a.agents)))
    samples=[t for agent in agents for t in agent['turns'] if t['status']=='ok']
    errors=sum(t['status']=='error' for agent in agents for t in agent['turns'])
    ttft=[t['ttft_s'] for t in samples]; elapsed=time.perf_counter()-start
    result={'model':a.model,'agents':a.agents,'requested_turns_per_agent':a.turns,'completed_turns':len(samples),'errors':errors,'wall_seconds':round(elapsed,3),'mean_ttft_seconds':round(sum(ttft)/len(ttft),3) if ttft else None,'max_ttft_seconds':round(max(ttft),3) if ttft else None,'agents_detail':agents}
    # Per-turn output is timing-only; conversation text and secret values never enter this report.
    print(json.dumps({k:v for k,v in result.items() if k!='agents_detail'},indent=2))
    if a.output:
        clean={k:v for k,v in result.items() if k!='agents_detail'}
        with open(a.output,'w',encoding='utf-8') as f:json.dump(clean,f,indent=2)
    return 1 if errors else 0
if __name__=='__main__':raise SystemExit(main())
