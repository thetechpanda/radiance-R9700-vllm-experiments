#!/usr/bin/env python3
"""bench_agents4.py v4: incremental coding-agent traffic bench (OpenCode-shaped).

Mimics real coding agents: shared system prompt, short user task, context
grows by tool RESULTS (~10k tok/turn, role=tool), model's own output appended,
streaming (real TTFT/ITL), exact engine token counts (usage), stops cleanly
before max-model-len.

v4 adds: --max-tokens depth cap, --images (attach a real PNG per turn per
agent, exercises the vision encoder + vision tokens in KV), --label +
--csv-append (one CSV summary row per run).

Usage: bench_agents4.py [--base-url URL] [--model TAG] [-n 4]
       [--chunk-tokens 10000] [--max-tokens 126000] [--max-model-len 131070]
       [-o 256] [--turns-max 24] [--images] [--label NAME] [--csv-append PATH]
"""
import argparse, base64, json, os, shlex, statistics, struct, subprocess, threading, time, urllib.request, urllib.error, zlib

def full_command(container="vllm-radiance.1"):
    """Full server invocation for this run: container env (RADIANCE_*/VLLM_*)
    + entrypoint + engine args, read live from podman inspect. Falls back to
    the bench argv if podman is unavailable. Newlines/quotes collapsed so the
    value is a single safe CSV cell."""
    try:
        env = json.loads(subprocess.check_output(
            ["podman", "inspect", container, "--format", "{{json .Config.Env}}"],
            text=True, timeout=15))
        entry = json.loads(subprocess.check_output(
            ["podman", "inspect", container, "--format", "{{json .Config.Entrypoint}}"],
            text=True, timeout=15))
        args = json.loads(subprocess.check_output(
            ["podman", "inspect", container, "--format", "{{json .Config.Cmd}}"],
            text=True, timeout=15))
        keep = [e for e in env if e.split("=", 1)[0].startswith(
            ("RADIANCE_", "VLLM_", "HIP_", "PYTORCH_ROCM", "AITER", "GPU_ARCHS",
             "MAMBA", "WEIGHT_QUANT", "NCCL"))]
        cmd = " ".join((entry or []) + (args or []))
        full = "env " + " ".join(shlex.quote(e) for e in keep) + " " + cmd
        return " ".join(full.split())
    except Exception:
        return " ".join(shlex.quote(x) for x in __import__("sys").argv)

SYSTEM_PROMPT = (
    "You are OpenCode, an expert software engineer agent operating autonomously "
    "on the user's codebase. You act through tools: read files before editing, "
    "make minimal correct changes, verify with shell commands, and never invent "
    "APIs. Prefer specialized tools over raw shell. Cite file paths and line "
    "numbers. Keep reasoning concise and grounded in observed code, not guesses. "
    "When a task is complete, summarize the change and the verification performed. "
) * 8

def code_line(i):
    return (f"  const handler_{i % 64:02d} = async (ctx: Ctx, payload: Buf) => {{ "
            f"const key = hash(ctx.ns, payload.off, {i}); "
            f"if (!registry.has(key)) registry.set(key, derive(payload, {i % 7})); "
            f"return registry.get(key).transform(ctx.flags); }}; // module {i}")

def file_result(j, n_lines):
    head = f"[tool read_file] src/module_{j:02d}/handler.ts ({n_lines} lines)\n"
    return head + "\n".join(code_line(j * 1000 + k) for k in range(n_lines)) + "\n"

def task_text(a):
    return (f"Refactor the request handlers in module_{a:02d} so the registry is "
            f"built lazily per namespace, add a unit test for the hot path, and "
            f"make sure `npm run check` passes. Start by reading the module files, "
            f"then the shared registry, then edit and verify.")

def make_png(seed, size=512):
    """Stdlib PNG: RGB gradient + seed-dependent bands (real encoder work)."""
    rows = []
    for y in range(size):
        row = bytearray([0])  # filter type 0
        for x in range(size):
            r = (x * 255 // size + seed * 37 + y) % 256
            g = (y * 255 // size + seed * 53) % 256
            b = ((x ^ y) * seed % 256)
            row += bytes((r, g, b))
        rows.append(bytes(row))
    raw = zlib.compress(b"".join(rows), 6)
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", raw)
           + chunk(b"IEND", b""))
    return "data:image/png;base64," + base64.b64encode(png).decode()

def user_msg(text, img_seed=None):
    if img_seed is None:
        return {"role": "user", "content": text}
    return {"role": "user", "content": [
        {"type": "text", "text": text},
        {"type": "image_url", "image_url": {"url": make_png(img_seed)}}]}

def post_stream(base_url, model, messages, max_tokens, stop):
    body = json.dumps({
        "model": model, "messages": messages, "max_tokens": max_tokens,
        "temperature": 0.7, "stream": True,
        "stream_options": {"include_usage": True},
    }).encode()
    req = urllib.request.Request(
        f"{base_url}/v1/chat/completions", data=body,
        headers={"Content-Type": "application/json"})
    t0 = time.time(); ttft = None; itls = []; parts = []; last = None
    prompt_tokens = None; completion_tokens = 0
    with urllib.request.urlopen(req, timeout=1800) as r:
        for raw in r:
            if stop.is_set():
                break
            s = raw.decode("utf-8", "replace").strip()
            if not s.startswith("data:"):
                continue
            p = s[5:].strip()
            if p == "[DONE]":
                break
            d = json.loads(p)
            u = d.get("usage")
            if u:
                prompt_tokens = u.get("prompt_tokens", prompt_tokens)
                completion_tokens = u.get("completion_tokens", completion_tokens)
            ch = d["choices"][0] if d.get("choices") else {}
            delta = ch.get("delta", {}) if ch else {}
            piece = delta.get("content") or delta.get("reasoning_content")
            if not piece and delta.get("tool_calls"):
                piece = json.dumps(delta["tool_calls"])
            if piece:
                now = time.time()
                if ttft is None:
                    ttft = now - t0
                elif last is not None:
                    itls.append(now - last)
                last = now
                parts.append(piece)
    return ttft or 0.0, itls, completion_tokens, "".join(parts), time.time() - t0, prompt_tokens

def agent_loop(a, args, results, lock, stop):
    messages = [user_msg(SYSTEM_PROMPT and f"[system]\n{SYSTEM_PROMPT}"),
                user_msg(task_text(a))]
    chunk_lines = max(1, round(args.chunk_tokens / 60.0))
    prev_prompt = None; prev_completion = 0; chunk_actual = None
    turn = 0
    while turn < args.turns_max and not stop.is_set():
        if prev_prompt is not None and prev_prompt >= args.max_tokens:
            print(f"[agent {a:02d}] stop at depth {prev_prompt} tok (cap {args.max_tokens})",
                  flush=True)
            return
        if prev_prompt is not None:
            est = prev_prompt + prev_completion + (chunk_actual or int(chunk_lines * 62))
            if est + args.output_tokens + 512 > args.max_model_len:
                print(f"[agent {a:02d}] stop at depth {prev_prompt} tok (overflow guard)",
                      flush=True)
                return
        turn += 1
        messages.append({"role": "tool", "tool_call_id": f"call_{a:02d}_{turn:02d}",
                         "content": file_result(a * 20 + turn, chunk_lines)})
        if args.images:
            messages.append(user_msg(f"Screenshot of the failing UI for module_{a:02d} "
                                     f"(step {turn}); correlate with the tool output.",
                                     img_seed=a * 100 + turn))
        try:
            ttft, itls, ctok, text, wall, ptok = post_stream(
                args.base_url, args.model, messages, args.output_tokens, stop)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            with lock:
                results.append({"agent": a, "turn": turn, "depth_tok": prev_prompt or 0,
                                "error": f"HTTP {e.code}: {detail}"})
            return
        except Exception as e:
            with lock:
                results.append({"agent": a, "turn": turn, "depth_tok": prev_prompt or 0,
                                "error": repr(e)})
            return
        messages.append({"role": "assistant", "content": text or "(tool call)"})
        if ptok is not None and prev_prompt is not None:
            chunk_actual = ptok - prev_prompt - prev_completion
        depth = ptok if ptok is not None else (prev_prompt or 0)
        prev_prompt, prev_completion = ptok or (prev_prompt or 0), ctok
        decode_t = wall - ttft
        tg = (ctok / decode_t) if decode_t > 0.5 and ctok else 0.0
        itl99 = round(statistics.quantiles(itls, n=100)[98], 3) if len(itls) > 10 else None
        rec = {"agent": a, "turn": turn, "depth_tok": depth, "ttft": round(ttft, 3),
               "tg": round(tg, 2), "out_tok": ctok, "wall": round(wall, 2), "itl_p99": itl99}
        with lock:
            results.append(rec)
        print(f"[agent {a:02d}] turn {turn:2d} depth {depth:6d} tok  "
              f"TTFT {ttft:6.2f}s  TG {tg:5.1f} tok/s  out {ctok:4d}  "
              f"ITLp99 {round(itl99*1000) if itl99 is not None else '-'}ms", flush=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8000")
    ap.add_argument("--model", default="ukisai/Swift-1.5-Qwen3.8-27b-INT4")
    ap.add_argument("-n", "--agents", type=int, default=4)
    ap.add_argument("--chunk-tokens", type=int, default=10000)
    ap.add_argument("--max-tokens", type=int, default=126000, help="depth cap")
    ap.add_argument("--max-model-len", type=int, default=131070)
    ap.add_argument("-o", "--output-tokens", type=int, default=256)
    ap.add_argument("--turns-max", type=int, default=24)
    ap.add_argument("--images", action="store_true", help="one PNG per turn per agent")
    ap.add_argument("--label", default="")
    ap.add_argument("--csv-append", default="")
    ap.add_argument("--container", default="vllm-radiance.1",
                    help="container name inspected for the command/env column")
    args = ap.parse_args()

    results, lock, stop = [], threading.Lock(), threading.Event()
    threads = [threading.Thread(target=agent_loop, args=(a, args, results, lock, stop))
               for a in range(args.agents)]
    t0 = time.time()
    for t in threads: t.start()
    for t in threads: t.join()
    wall = time.time() - t0

    ok = [r for r in results if "error" not in r]
    errs = [r for r in results if "error" in r]
    print("\n=== SUMMARY BY DEPTH BUCKET (real engine token counts) ===")
    print(f"{'depth':>10} {'turns':>6} {'TTFT avg':>9} {'TTFT max':>9} {'TG avg':>8} {'ITLp99 avg':>11}")
    buckets = []
    for lo in range(0, max(args.max_tokens, 150000), 30000):
        b = [r for r in ok if lo <= r["depth_tok"] < lo + 30000]
        if not b:
            continue
        itl = [r["itl_p99"] for r in b if r["itl_p99"]]
        tg = [r["tg"] for r in b if r["tg"]]
        tavg = statistics.mean(r["ttft"] for r in b)
        tmax = max(r["ttft"] for r in b)
        buckets.append((lo, len(b), round(tavg, 2), round(tmax, 2),
                        round(statistics.mean(tg), 1) if tg else 0,
                        round(statistics.mean(itl) * 1000) if itl else 0))
        print(f"{lo//1000:>4}-{(lo+30000)//1000:>4}k {len(b):>6} {tavg:>8.2f}s {tmax:>8.2f}s "
              f"{statistics.mean(tg) if tg else 0:>7.1f} "
              f"{statistics.mean(itl)*1000 if itl else 0:>10.0f}ms")
    itl_all = [r["itl_p99"] for r in ok if r["itl_p99"]]
    tg_all = [r["tg"] for r in ok if r["tg"]]
    ttft_avg = statistics.mean(r["ttft"] for r in ok) if ok else 0
    max_depth = max((r["depth_tok"] for r in ok), default=0)
    decode_tps = sum(r["out_tok"] for r in ok) / wall if wall else 0
    print(f"\nturns ok={len(ok)} errors={len(errs)} wall={wall:.0f}s "
          f"decode={decode_tps:.1f} tok/s avg_turn_TTFT={ttft_avg:.2f}s max_depth={max_depth}")
    for r in errs[:8]:
        print("ERR", r["agent"], r["turn"], r["error"][:200])

    if args.csv_append:
        hdr_needed = True
        try:
            with open(args.csv_append) as f:
                hdr_needed = f.read(1) == ""
        except FileNotFoundError:
            pass
        with open(args.csv_append, "a") as f:
            if hdr_needed:
                f.write("label,agents,images,depth_cap,turns_ok,errors,wall_s,"
                        "max_depth_tok,ttft_avg_s,ttft_max_s,decode_tps,"
                        "tg_avg,tp99_itl_ms,"
                        "ttft_0-30k,ttft_30-60k,ttft_60-90k,ttft_90-120k,ttft_120k+,"
                        "command\n")
            bt = {lo: t[2] for lo, t in zip(range(0, 150000, 30000), buckets)} if False else {}
            bmap = {t[0]: t for t in buckets}
            row = [args.label or f"n{args.agents}", args.agents, int(args.images),
                   args.max_tokens, len(ok), len(errs), round(wall, 1), max_depth,
                   round(ttft_avg, 2), round(max((r["ttft"] for r in ok), default=0), 2),
                   round(decode_tps, 2), round(statistics.mean(tg_all), 1) if tg_all else 0,
                   round(statistics.mean(itl_all) * 1000) if itl_all else 0]
            for lo in range(0, 150000, 30000):
                row.append(bmap[lo][2] if lo in bmap else "")
            row.append('"' + full_command(args.container).replace('"', '""') + '"')
            f.write(",".join(str(x) for x in row) + "\n")
        print(f"CSV row appended -> {args.csv_append}")

if __name__ == "__main__":
    main()
