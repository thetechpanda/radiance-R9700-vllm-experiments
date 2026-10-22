---
layout: default
title: "Server runbook: radiance trial with the new models"
---

# Server runbook: radiance trial with the new models

Operator checklist for running the trial that the [startup guide](startup-guide.md)
plans: check out the `radiance` repository on the server for reference,
download the models, wait for the currently running campaign tests to finish,
then re-run those campaign arms against radiance. Written for the recorded
dual-R9700 host (Podman, rootful). Every command is from upstream docs or the
recorded deployment — none of this has been executed on that host yet, so
read each step before running it and record what you see.

Conventions used below:

- `RAD_REF` — the radiance repo checkout directory on the server (reference
  material: docs, compose files, recipes, `agentreplay.py`).
- `MODELS` — the models data directory on the server NVMe (the recorded
  deployment keeps HF snapshots and caches there; radiance needs direct-I/O
  capable local filesystem — `chattr +C` the directory on btrfs).
- `RADIANCE_API_KEY` — generate once, keep in the trial directory, never in
  a git-tracked file.

## 1. Check out the radiance repo for reference

The checkout is reference material while you run the trial — the compose
files, recipes and `agentreplay.py` live there, and the docs answer most
startup questions faster than issues do.

```sh
mkdir -p ~/radiance-trial
RAD_REF=~/radiance-ref
git clone https://codeberg.org/StillDeadcode/radiance.git "$RAD_REF"
git -C "$RAD_REF" checkout 816e24bd46   # 1.8.1, the state reviewed 2026-10-19
git -C "$RAD_REF" log -1 --format='%H %s' | tee ~/radiance-trial/checkout.txt
```

Pin the commit. radiance releases fast (1.7.0 → 1.8.1 in three days at the
review date) and containers are version-pinned to the engine that converted
them — a model converted with one version refuses to load in another without
re-conversion (`--reuse`).

### 1b. Pin the engine image — the checkout pins the source, not the engine

The published image is what converts and serves; the git checkout is
reference material. Pin the image by **digest** and use that digest for every
conversion, inspection and serving command below — an untagged
`stilldeadcode/radiance` can move under you.

Run this block in the same Bash session as the later steps. A failed pull,
inspection or digest check exits that session before conversion or serving.

{% raw %}
```sh
podman pull docker.io/stilldeadcode/radiance:latest || exit 1
# RepoDigests is the registry manifest digest — the identifier @sha256: accepts.
# `podman images --no-trunc` shows the local image ID, which is NOT this.
RADIANCE_IMG=$(podman image inspect docker.io/stilldeadcode/radiance:latest \
  --format '{{index .RepoDigests 0}}') || exit 1
[[ $RADIANCE_IMG =~ @sha256:[0-9a-f]{64}$ ]] || {
  echo "no valid registry digest — abort" >&2
  exit 1
}
echo "$RADIANCE_IMG" | tee ~/radiance-trial/image.txt
```
{% endraw %}

`$RADIANCE_IMG` is used in every container command in this runbook. Record
the engine version the startup report prints and confirm it matches the
checkout's pinned release — if they diverge, you are converting with one
engine and reading another's docs.

## 2. Download the models

Three containers, in priority order. Budget the disk first: ~18 GiB + ~27
GiB + ~15 GiB + ~14 GiB converted ≈ 75 GiB on `MODELS`.

| # | Model | What it is for | Size |
|---|---|---|---|
| M1 | `StillDeadcode/qwen3.8-27b-mxfp4` (`.rad`) | The engine's native showpiece; the published speed cards; includes vision + DFlash2 drafter | 18.05 GiB |
| M2 | `ukisai/Swift-1.5-Qwen3.8-27b-INT4` → convert | The campaign checkpoint — continuity with every recorded number | ~15 GiB HF + ~14 GiB `.rad` |
| M3 | `StillDeadcode/qwen3.8-27b-fp8` (`.rad`) | Same-quantization comparator for the campaign's FP8 experiments | check the card before download |

```sh
MODELS=/srv/models   # adjust to the server's data mount
mkdir -p "$MODELS/rad" "$MODELS/hf/ukisai" ~/radiance-trial

# M1 — published MXFP4 container (single file)
curl -fL -C - -o "$MODELS/rad/qwen3.8-27b-mxfp4.rad" \
  https://huggingface.co/StillDeadcode/qwen3.8-27b-mxfp4/resolve/main/qwen3.8-27b-mxfp4.rad

# M2 — the campaign checkpoint at the recorded revision
hf download ukisai/Swift-1.5-Qwen3.8-27b-INT4 \
  --local-dir "$MODELS/hf/ukisai/Swift-1.5-Qwen3.8-27b-INT4" \
  --revision 81a28ee75eb1cd469f209813a368a79a7e3db3bc

# M3 — published FP8 container; list the repo files first, take the .rad
curl -s https://huggingface.co/api/models/StillDeadcode/qwen3.8-27b-fp8 \
  | jq -r '.siblings[].rfilename' | grep '\.rad$'   # confirm the exact .rad name
curl -fL -C - -o "$MODELS/rad/qwen3.8-27b-fp8.rad" \
  https://huggingface.co/StillDeadcode/qwen3.8-27b-fp8/resolve/main/<name-from-listing>
```

Then convert M2 with the recipe that matches its `config.json` field-for-field
([swift-models.md](swift-models.md)). Plan first, convert second:

```sh
podman run --rm -v "$MODELS":/models --security-opt seccomp=unconfined \
    --entrypoint rad-convert "$RADIANCE_IMG" \
    /models/hf/ukisai/Swift-1.5-Qwen3.8-27b-INT4 \
    -o /models/rad/swift15-27b-int4.rad \
    --recipe /opt/radiance/share/radiance/recipes/q38-27b-w4a16.recipe \
    --plan-only -v | tee ~/radiance-trial/convert-plan.txt
# satisfied with the plan: drop --plan-only and re-run
```

Verify every container before serving — `rad-info` prints geometry, quant,
vision tower, MTP/DFlash drafter presence:

```sh
for f in qwen3.8-27b-mxfp4 qwen3.8-27b-fp8 swift15-27b-int4; do
  podman run --rm -v "$MODELS/rad":/models:ro --entrypoint rad-info \
    "$RADIANCE_IMG" "/models/$f.rad" | tee ~/radiance-trial/info-$f.txt
done
```

Record for each model: exact engine tag/digest, download URL, revision/commit,
`rad-info` output. These become the provenance columns of the results CSV.

## 3. Gate: wait for the running tests to finish

Do not start radiance while campaign tests are running — radiance measures
the VRAM budget before allocation and refuses to start when a card lost
memory mid-startup (`pool allocation refused`), and the 32 GiB host cannot
run both engines.

{% raw %}
```sh
# 1. the campaign fleet must have exited (fleet + per-agent scripts, and any
#    synthetic probes)
pgrep -af 'run_falling_blocks|agent_bench.py'       # expect: no output
podman ps --format '{{.Names}}' | grep falling_blocks  # expect: none

# 2. the endpoint must show nothing in flight
curl -s localhost:8000/metrics | grep -E 'num_requests_(running|waiting)'
# expect: zeros; prefix-cache counters keep rising for a while after the
# last turn — the in-flight gauges are the gate, not the counters

# 3. stop the vllm-radiance service (unit + container), then confirm the cards
systemctl stop <vllm-radiance-unit>
podman ps                                    # expect: no inference container
rocm-smi --showuse --showmemuse              # expect: utilisation ~0, VRAM freed
```
{% endraw %}

Checkpoint before proceeding: no client processes, no in-flight requests, no
inference container, cards idle. The baseline is *stopped*, not removed —
launchers, systemd unit and model caches stay intact (startup guide §8).

## 4. Start radiance and validate

Before launching the server, run the startup guide's §5 `rad-kbench` check
with `$RADIANCE_IMG` while the cards are free. Then start M1 (MXFP4), with
the agent-profile flags from the startup guide (§3–4), on **port 8001**:

```sh
podman run -d --name radiance \
    --network host --init \
    --ulimit memlock=-1 \
    --device /dev/kfd --device /dev/dri \
    --group-add "$(getent group render | cut -d: -f3)" \
    --group-add "$(getent group video | cut -d: -f3)" \
    --security-opt label=disable --security-opt seccomp=unconfined \
    -v "$MODELS/rad":/models:ro \
    --stop-timeout 60 \
    "$RADIANCE_IMG" \
      --model /models/qwen3.8-27b-mxfp4.rad \
      --host :: --port 8001 --api-key "$RADIANCE_API_KEY" \
      --tp 2 --max-num-seqs 4 --max-model-len 131072 --kv-cache-dtype fp8 \
      --gpu-headroom-mib 96 --prefix-cache-mib 10240 --prefix-cache-ttl 3600 \
      --checkpoint-slots 24 --vision-tower-placement ram \
      --num-speculative-tokens 0
```

`--num-speculative-tokens 0` is the non-spec baseline (§5 arms R1–R4, R7);
the spec arms change it as noted there. The startup guide (its §3) starts
with the container's default drafting depth — here we set it explicitly so
every cell declares its lane.

Then complete the startup guide's §5 validation, with `$RADIANCE_IMG` for
the image name and port **8001** in every API URL: startup receipt into
`~/radiance-trial/startup-mxfp4.txt`, `server_info` + `/props`, text smoke,
vision smoke. The kernel check was done before launch; do not run it against
the occupied cards. Keep every receipt. `--live` output redirected to a file is the monitor log for
the whole trial — the closest analogue of [radiance-top](../SCRIPTS.md).

## 5. Re-run the campaign arms

**Harness status — read before scheduling arms.** The campaign's deep-context
baselines (S1–S6, E1, B1, the 8k-repro pair) were produced by the campaign's
own bench harness — fixed per-turn prompt growth, a client-side depth cap,
greedy sampling, N agents × M turns. **That harness is not in this
repository's `scripts/`.** What is public:

- [`scripts/run_falling_blocks_fleet.sh`](../../scripts/run_falling_blocks_fleet.sh)
  launches the Pi coding-agent **task-completion** harness (the Falling
  Blocks games). It enforces no turn count, no depth cap and no sampling;
  its provider endpoint and credentials come from the Pi config baked into
  `PI_IMAGE` — the fleet script's URL argument is only a health check. It is
  an acceptance harness ("agents complete real tasks on radiance"), not a
  baseline-comparable bench.
- [`scripts/agent_bench.py`](../../scripts/agent_bench.py) is the synthetic
  probe: per-turn growth of `--max-tool-chars` characters, growing history,
  **no depth cap, no sampling control** (the server default applies), and it
  keeps only client-side stream timings. Its defaults (3,000 chars/turn) are
  not the campaign workload.

So R1–R6 are **blocked pending harness reconstruction** (§5a); R7 runs today.
The campaign CSVs describe outcomes and some configuration, not the complete
workload. They cannot by themselves reconstruct its prompts or stopping rules.

The campaign used TP=2, a 131k server ceiling, prefix caching, bf16 KV and
greedy sampling. Recover the request-level sampling fields as well as the
server settings; radiance changes the KV dtype (`--kv-cache-dtype
fp8` is the engine default here) and the drafting lane, so **declare the lane
per arm** and record the sampling the harness actually used.

### 5a. Recover and validate the harness (unblocks R1–R6)

Recover the original harness and configuration, or reconstruct and validate
an equivalent workload before running a baseline comparison. Adding depth
and sampling controls to `agent_bench.py` alone does not establish equivalence.
Keep R1–R6 blocked until the following evidence is recorded:

1. Recover the initial system/task prompt separately from per-turn tool-input
   growth, including seeds, tokenization/chat template, response token limit,
   sampling fields, history handling, turn count and concurrency. Recover the
   depth-cap rule: whether it checks before or after a turn, and whether it
   counts prompt tokens, completion tokens, or both.
2. Recover the image-injection behavior for R4: the source, size and placement
   of each image in history, in addition to the text workload. The published
   description is one procedural 512×512 PNG per turn per agent.
3. Validate the recovered or reconstructed client on the baseline engine with
   the original checkpoint/revision, quantization, KV dtype, cache settings
   and drafting lane. Preserve per-turn token/depth traces, completion/error
   counts, sampling configuration, cache behavior and timings. Confirm workload
   semantics first; matching wall time alone is not evidence of equivalence.
4. Export a sanitized configuration and validation receipt, then use that
   same client and workload for the radiance comparison. If the original
   workload cannot be recovered or validated, label it a new workload and
   collect fresh baseline-engine and radiance measurements for it. Do not use
   the historical wall times as its matched baseline.

Use the [sweep CSV](../../data/rocm-10.1/dual-r9700-agent-count-sweep-2026-10-19.csv),
[8k-repro CSV](../../data/rocm-10.1/dual-r9700-8k-repro-2026-10-19.csv) and
[campaign CSV](../../data/rocm-10.1/dual-r9700-spec-campaign-2026-10-19.csv)
as validation references, not a prompt-generation recipe. Deep S1–S6 cells
used 10 turns per agent and a recorded 126000 depth cap. Shallow
`R1-quark-nospec`/`R2-quark-mtp4` used eight agents, a recorded 15000 depth
cap and a 16384 server ceiling; each completed 21 turns across the fleet.
Their observed maximum depths (15446/15412) exceed the recorded cap, so a
hard prompt-plus-response ceiling of 15000 is not an established stopping rule.

Do not infer growth from `max_depth_tokens / turns`: that depth includes the
initial prompt, generated history and chat formatting. The campaign's
[~7.9k-token shallow prompt](../DUAL-R9700-SPEC-CAMPAIGN.md) is its initial
system/task prompt, not an increment added on every turn. A characters-per-token
estimate cannot recover either workload.

Drafter note for R5/R6: radiance's `RADIANCE_SPECULATIVE_CONFIG` carries
**either MTP or the DFlash2 drafter, never both**, and the published MXFP4
container ships the **DFlash2** drafter — so `--num-speculative-tokens N` on
M1 drafts with DFlash2, not the campaign's MTP K4 head. The campaign B1 cell
(MTP K4) has no drop-in radiance equivalent on M1: `rad-info` on the
container tells you which drafter is present, and the MTP-lane comparison
needs a container converted with the MTP head (the Swift MTP head survives
conversion — [swift-models.md](swift-models.md)). Record the drafter name in
every spec row; do not label a DFlash2 row "MTP K4".

### 5b. Per-arm server configuration

All arms share the §4 container (swap `--model` for M2/M3 as noted) with
these per-arm deltas. For every model or flag change, stop and remove the
old container, then repeat the full §4 `podman run` command with the new
arguments. `podman restart` retains the original arguments.

```sh
podman stop radiance && podman rm radiance
# Now repeat §4's full podman run command with the required model/flag changes.
```

| Arms | Engine flags (delta from §4) |
|---|---|
| R1–R4, R7 | non-spec: `--num-speculative-tokens 0`, `--max-num-seqs 4` (R7: 1) |
| R5 | `--max-num-seqs 8 --max-model-len 16384` — eight agents need eight slots; run the pair twice: `--num-speculative-tokens 0` (non-spec) and `--num-speculative-tokens 4` (spec) |
| R6 | §4 flags with the spec lane: `--num-speculative-tokens 4`; see drafter note |

### 5c. Run what is runnable

R7 runs after §4 validation. Calibrate each input to ~2K, ~4K or ~7K tokens
with `rad-tokcheck` and record the measured input count. The repeat count below
is an example, not a measured 7K prompt. Before **each** measured request,
stop/remove the server and repeat the §4 launch with R7's §5b flags; wait for
readiness and issue no chat/vision smoke requests between this fresh launch
and the measurement. The host prefix tier is not mounted persistently here.
Reject any receipt with a nonzero or missing `cache_n`; never book it as cold.

```sh
set -o pipefail
# One R7 request after the fresh-server procedure above; repeat for each size.
PROMPT_7K=$(python3 -c "print('record_key=abcdef0123456789 '*1500, end='')")
jq -n --arg prompt "$PROMPT_7K" \
  '{model:"m",messages:[{role:"user",content:$prompt}],max_tokens:16,reasoning_effort:"none"}' \
  | curl --fail --silent --show-error localhost:8001/v1/chat/completions \
      -H "Authorization: Bearer $RADIANCE_API_KEY" \
      -H 'Content-Type: application/json' --data-binary @- \
  | jq -ce '.timings | select(.cache_n == 0 and .prompt_n > 0)' \
  | tee -a ~/radiance-trial/r7-timings.jsonl || exit 1
# Require a receipt with positive prompt_n and cache_n == 0 before proceeding.
```

R1–R6 have no runnable baseline-comparison command until §5a is satisfied.

```sh
# Optional, not baseline-comparable: the Pi fleet as a task-completion
# acceptance run. The fleet script's URL argument is only its health check —
# the agent containers get their endpoint and key from the Pi provider config
# baked into PI_IMAGE, so rebuild PI_IMAGE's provider to point at
# http://localhost:8001/v1 with $RADIANCE_API_KEY before running.
# PI_NETWORK=host gives each agent container access to the host loopback API.
PI_NETWORK=host PI_IMAGE=<pi image configured for :8001> PI_MODEL=m PI_PROVIDER=<provider> \
WORK_ROOT=~/radiance-trial/accept-$(date -u +%Y%m%dT%H%M%SZ) \
  scripts/run_falling_blocks_fleet.sh 4 100 3600 http://localhost:8001/health \
  2>&1 | tee ~/radiance-trial/accept-fleet.txt
python3 scripts/parse_falling_blocks_events.py ~/radiance-trial/accept-*/agent-* \
  > ~/radiance-trial/accept-turns.csv
```

The validated harness must retain client-side `ttft_s`/`elapsed_s` per turn,
radiance's per-request `timings` and the `radiance:` metrics. Document their
mapping onto the campaign schema before comparing results; the startup guide
(§6) proposes:
`pp_effective_ingest_tok_s = (prompt_n+cache_n)/ttft`, `turn_tg_avg` from
per-turn output tokens over elapsed, `decode_tokens_s` from the steady window
— `radiance:decode_tokens_per_second` is the steady-window source. One run
per cell; treat gaps under ~15% as noise (recorded repeat spread).

| Arm | Mirrors | Config | Baseline to beat / match | Status |
|---|---|---|---|---|
| R1 | S1 | 1 agent, 10 turns, cap 126k, non-spec | 134.2 s wall, 16.64 tok/s decode, 7,454 tok/s ingest, 40% cache hits | blocked: §5a recovery and validation |
| R2 | S4/S6/E1 | 4 agents, cap 126k, non-spec | 372.8 / 439.0 / 439.6 s wall (15% spread band) | blocked: §5a recovery and validation |
| R3 | S2/S3 | 2 and 3 agents, cap 126k | 203.7 / 264.7 s | blocked: §5a recovery and validation |
| R4 | S5 | 4 agents, cap 126k, + one 512×512 PNG per turn per agent | 537.1 s, +44% vs S4 → the radiance vision cost | blocked: §5a image-harness recovery and validation |
| R5 | 8k-repro | 8 agents, cap 15k, server 16K: non-spec vs DFlash2 drafting | 93.5 s vs 81.9 s (published ordering reproduces shallow) | blocked: §5a recovery and validation |
| R6 | B1 | 4 agents, cap 126k, spec lane (DFlash2 on M1) | 707.6 s — the depth inversion, on radiance's graph-captured drafting | blocked: §5a recovery and validation |
| R7 | new | cold pp at 2K/4K/7K, 1 agent | radiance publishes **no** 27B prefill numbers — this fills the pp gap from [performance-standards.md](performance-standards.md) | **ready today** |

R4 caveat: the campaign's S5 injected one procedural 512×512 PNG per turn
per agent; the sanitized fleet script in `scripts/` runs the text-only task
shape. Reproduce S5 only with the image-injecting harness variant; with the
text-only script, R4 measures the text fleet and the vision smoke (§4)
measures the tower — record that split, do not book it as S5.

Run order: §4 validation + R7 on M1 first (ready today — the startup receipt,
smokes and the pp grid answer the boot and prefill questions while the
harness is recovered and validated), then R1 → R2 → R6 once §5a passes,
then the rest. Swap models by stopping and removing the container (§5b),
then repeating §4 with `--model /models/swift15-27b-int4.rad` (same
`$RADIANCE_IMG`, same per-arm flags from §5b) — M2 gets R1/R2/R4
(continuity cells), M3 gets R1/R2. Re-run the §4 validation receipts on every
model swap.

Record per cell: model, engine digest, drafter name (`rad-info`), arm,
wall_s, decode tok/s, mean/max TTFT, ingest, cache-hit fraction, preemptions
(`num_requests_preempted`), draft acceptance where a spec lane ran, and the
`--live` log window. Write it into a CSV with the campaign's column names so
the comparison is column-for-column.

## 6. Judge the trial

The four decisions, in order (decisions 2–4 land only after the §5a harness
recovery and validation; decision 1 and the R7 grid do not depend on it):

1. **Does it boot and serve on this host at all** — startup receipt clean,
   smokes green, R7 grid completes; the optional Pi fleet (5c) completing its
   tasks is the real-agent acceptance signal.
2. **R1 vs S1** — 1-agent 126k decode and ingest: the engine's 204 tok/s
   shallow claim meets your 16.64 tok/s deep baseline on your box.
3. **R2 vs the E1/S4/S6 band** — 4-agent wall time inside/outside the
   372.8–439.6 s band, with preemption counts compared against the
   campaign's 7/12-preemption cells.
4. **R6** — radiance's graph-captured drafting at 126k (DFlash2 on M1): does
   the campaign's depth inversion (spec loses at depth) survive on an engine
   that removes the vLLM eager-drafting penalty? The drafter differs from
   B1's MTP head — compare the *shape* (spec vs non-spec at depth), and
   label rows by the drafter `rad-info` reports.

If the trial ends, roll back (§7) and write the numbers up as a campaign
page in this repository — one run per cell, provenance per row, same rules
as every other page here.

## 7. Rollback

```sh
podman stop radiance          # SIGTERM finishes the in-flight step
podman rm radiance
systemctl start <vllm-radiance-unit>
curl -s localhost:8000/v1/models | jq   # baseline serving again
```

Nothing in the recorded deployment was modified: the baseline container,
launchers, systemd unit, model caches and port are untouched; radiance ran
as its own container, port and model directory.

## Failure quick reference

The startup guide's [friction table](startup-guide.md#7-known-friction) is
the first stop (`pool allocation refused`, pin-cap refusals, ABI refusals
after an engine update, 413 media bodies, reasoning-eaten `max_tokens`).
Two runbook-specific traps: starting radiance **before** the §3 gate passes
(VRAM budget race), and converting with one engine tag then serving with
another (version-pinned containers — re-convert with `--reuse`).

<!-- NAVIGATION START -->

[Home](../../index.md) · [Overview](../../README.md) · [ROCm 10.1 results](../FINAL-REPORT-20261018.md) · [Charts](../CHARTS.md)
