import json, time, urllib.request, urllib.error
body = "".join("line%06d filler word here. " % i for i in range(14000))
body += "NEEDLE: the magic word is ORCHID. "
body += "".join("line%06d filler word here. " % i for i in range(14000, 15000))
payload = {"model": "ukisai/Swift-1.5-Qwen3.8-27b-W4A16-AWQ",
  "messages": [{"role": "user", "content": "Find the needle and answer with just the magic word.\n\n" + body}],
  "max_tokens": 700, "stream_options": {"include_usage": True}, "stream": True}
t0 = time.time()
req = urllib.request.Request("http://127.0.0.1:8000/v1/chat/completions",
  data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
try:
    resp = urllib.request.urlopen(req, timeout=600)
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read()[:400].decode()); raise SystemExit(1)
ttft = None; txt = ""; usage = None
for line in resp:
    s = line.decode().strip()
    if not s.startswith("data:"): continue
    d = s[5:].strip()
    if d == "[DONE]": break
    j = json.loads(d)
    ch = j.get("choices") or []
    delta = ch[0]["delta"] if ch else {}
    if delta.get("content") or delta.get("reasoning_content"):
        if ttft is None: ttft = time.time() - t0
        txt += (delta.get("content") or delta.get("reasoning_content") or "")
    if j.get("usage"): usage = j["usage"]
pt = usage["prompt_tokens"] if usage else "?"
print("prompt_tokens=%s ttft=%.1fs total=%.1fs" % (pt, ttft, time.time() - t0))
print("answer_tail:", repr(txt[-200:]))
