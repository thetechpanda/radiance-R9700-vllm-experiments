#!/usr/bin/env python3
"""Build the release run index from transformed CSVs and editorial notes."""
import csv
import json
import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
OUT = ROOT / 'docs' / 'RUN-INDEX.md'

# These descriptions are deliberately generalized; raw source labels and
# launch commands are not used in the release.
RUN_NOTES = {
    1: ('Three-agent compaction chain at a 100k target', 'Measure context growth, prefix reuse, latency and stall behaviour under repeated compaction. The prompt-compute counter peaks near 65k tokens/s because it credits work in bursts at request completion; that is not true PP. Read this as a compaction workload, not a clean throughput baseline.'),
    2: ('Three-agent compaction chain extended to 110k', 'Probe the usable depth frontier for three concurrent agents. Compare latency and stall growth with the neighboring 90k and 100k cases.'),
    3: ('Three-agent compaction chain at 90k', 'Lower-depth reference for the three-agent chain. Use as a context for deeper compaction cases, not as an isolated hardware comparison.'),
    4: ('Four-agent compaction at 64k', 'Shallow four-agent point used to see how compaction begins under concurrency. Compare the event/stall profile with deeper four-agent points.'),
    5: ('Four-agent compaction at 80k', 'Intermediate-depth four-agent workload. Look for the onset of queue and compaction stalls as context grows.'),
    6: ('Four-agent compaction at 86k', 'Narrow depth step within the compaction region. Treat small differences cautiously because workload history and cache state affect the storm profile.'),
    7: ('Four-agent compaction at 90k', 'Reference four-agent storm workload used repeatedly for later storage and link comparisons. This is deliberately sustained stress, not a short latency smoke test.'),
    8: ('Clean rerun after a prefill-threshold change', 'Checks whether smaller prefill scheduling steps reduce long stalls. Interpret TTFT, prefill throughput and long-stall counts together; the change reduced some micro-stalls but did not eliminate total stall time.'),
    9: ('Foreign-traffic-contaminated threshold trial', 'Tainted comparison: unrelated traffic shared the service during collection. Keep it for provenance only; do not use its metrics to claim a treatment effect.'),
    10: ('GPU-link upgrade comparison at the four-agent storm point', 'Replays the reference workload after a link change. It improves average transfer/reload behaviour but does not resolve the long-tail stall mechanism.'),
    11: ('Clean-storage four-agent storm trial', 'Tests whether a clean backing tier changes stalls. Compare storage traffic and stall timing; this precedes the loop-backed tier test.'),
    12: ('Loop-backed fast-storage trial', 'Tests the backing-store path with a capped loop device. Use memory telemetry alongside engine metrics to distinguish real tier use from idle capacity.'),
    13: ('Eight-agent overflow / RAM-tier boundary', 'Intentionally exceeds the GPU plus host-memory working set so the backing tier must receive spill traffic. This is a capacity and survival stress test, not a normal operating point.'),
    14: ('Reduced host-tier capacity at four-agent load', 'Compares a smaller RAM tier with the previously tested larger tier. Watch swap, reload rates, memory headroom and deep-context latency.'),
    15: ('Single-card RAM16 tier, four agents at 131k target', 'Qualification run for the 16 GiB shared-memory tier with four agents on one card. It is the key smooth-operation milestone; read error count, turn completion, TTFT by depth and memory pressure together.'),
    16: ('Single-card RAM16 tier, three agents at 150k target', 'Follow-up capacity point with fewer agents and deeper context. Compare sustained completion and tail behaviour with the four-agent milestone.'),
    17: ('Guardrail / correctness trial at four agents', 'Exercises the guard configuration at deep context. Use errors, preemptions and completion behaviour as correctness gates before considering speed.'),
    18: ('Speculative-depth eight versus the four-agent baseline', 'A/B of a wider draft setting under the same deep four-agent load. The wider draft is expected to consume more KV and verification work; evaluate KV capacity, ITL tail and throughput, not only average decode.'),
    19: ('Six-agent capacity-bound run, incomplete', 'Deliberately runs beyond the four-sequence scheduler capacity so agents queue; the archived attempt failed to produce a valid completed benchmark. Treat as a failure-boundary observation, not a performance result.'),
    20: ('Real coding-agent fleet, six agents', 'Runs real tool-using agents to expose scheduler queuing and realistic context growth. Early harness configuration produced zero usable artifacts; use only the later qualified agent runs for performance conclusions.'),
    21: ('Single-agent real coding task', 'Checks end-to-end tool use, response quality signals and completion on the actual coding workflow. It is a functional workload and not comparable to token-padding throughput tests.'),
    22: ('Instrumentation sanity pass', 'Verifies that telemetry collection and counters move coherently. Use it to validate instruments, not to compare serving performance.'),
    23: ('Second instrumentation sanity pass', 'Repeat/extension of the telemetry sanity check. Short duration and small sample count make it unsuitable for latency or throughput ranking.'),
    24: ('ROCm base-image four-agent stress run', 'Sustained four-agent load on the newer runtime stack. Compare with older-stack data only as an indicative comparison because configuration and depth caps differ; this is a stress qualification.'),
    25: ('Compaction jitter and prefix-head preservation', 'Tests staggered compaction and preservation of early context under four-agent load. Read hit/transfer share and long stalls together; the run includes mixed backing-store conditions.'),
    26: ('Runtime/JIT instrumentation sanity', 'Confirms the updated runtime/JIT path starts and emits expected telemetry. Not a throughput benchmark.'),
    27: ('Second runtime/JIT sanity pass', 'Short follow-up sanity sample. Its purpose is startup and metric validity rather than workload capacity.'),
    28: ('Host-memory and storage telemetry during the link/storage campaign', 'Companion host sampler for the corresponding engine run. Use it to correlate available memory, swap, VRAM and I/O with stalls; it is not an independent benchmark.'),
    29: ('Host-memory trace for overflow stress', 'Companion memory trace for the intentional overflow run. Look for tier activation, swap and memory headroom; do not read accumulated file footprint as live cache occupancy.'),
    30: ('Host-memory trace for the reduced-tier comparison', 'Correlates host pressure and storage behaviour with the smaller-tier run. Interpret counter deltas as rates, and gauges as sampled state.'),
    31: ('Host-memory trace for the RAM16 four-agent milestone', 'Companion resource trace for the central four-agent single-card result. Check swap stays controlled while the shared-memory tier is active.'),
    32: ('Host-memory trace for the RAM16 three-agent follow-up', 'Resource companion for the deeper three-agent test. Compare memory headroom and swap with the four-agent tier run.'),
    33: ('Host-memory trace for the guardrail trial', 'Companion resource sampler. Correlate pressure with any guardrail or correctness events in the engine series.'),
    34: ('Host-memory trace for the speculative-depth A/B', 'Companion sampler for the draft-depth comparison. Helps explain KV reservation and memory-pressure changes.'),
    35: ('Host-memory trace for the six-agent real-agent campaign', 'Companion sampler for the agent fleet. Separate host resource behaviour from the agent harness configuration and its task-completion outcomes.'),
}


def main():
    entries = json.loads((DATA/'telemetry-catalog.json').read_text())
    lines = ['# Run index', '', 'Only selected results are published. [Excluded tests](EXCLUDED-TESTS.md) summarises other coverage without redistributing its performance tables; restored exploratory SVGs are retained in the secondary graph archive.', '',
             '## Retained telemetry', '', '| Experiment | Version and provenance | CSV |', '|---|---|---|']
    for e in entries:
        if e['included']:
            lines += [f"| {e['title']} | {e['version']}: {e['provenance']} | [CSV](../data/{e['version']}/{e['slug']}.csv) |"]
    lines += ['', '## Retained benchmark cases', '', '| Experiment | Version | Agents | Completed turns | Mean TTFT |', '|---|---|---:|---:|---:|']
    for version in ('rocm-7.14','rocm-10.1'):
        with (DATA/version/'historical-agent-workloads.csv').open() as stream:
            for row in csv.DictReader(stream):
                lines += [f"| {row['experiment']} | {version} | {row['agent_count']} | {row['successful_turns']} | {row['mean_ttft_s']} s |"]
    lines += ['', 'These are representative operating points, not a matched scaling curve. Workload depth/history and settings differ. The older/newer stress pair is not a controlled ROCm A/B. See the [version evidence](ROCM-VERSIONS.md) and [seven completed ROCm 10.1 repeat cells](REPEAT-CAMPAIGN.md).', '', 'Prompt-credit rates are not measured prefill throughput. Companion resource traces are not independent benchmark runs.']
    lines += ['', '## ROCm 10.1 follow-up campaigns', '', '| Campaign | Completed synthetic cells | Profile / scope |', '|---|---:|---|', '| Earlier dual-card growth | 7 | TP=2, MTP=8, 8 GiB CPU tier; four-agent 150k cell partial |', '| GPU A / dual comparison | 8 | Each profile at 1–4 agents; 10 GiB CPU tier; GPU A MTP=4, dual MTP=8 |', '', 'The [latest campaign report](FINAL-REPORT-20261018.md) includes TTFT tails, preemptions and the first coding fleets. The [eight-cell CSV](../data/rocm-10.1/follow-up-single-vs-dual-text-growth-2026-10-18.csv) already includes all four rows in the separate GPU A export; these are not independent additional cases. The report counts completed empty responses separately from timed turns. The single-card retry completed with all four agents delivering and exiting cleanly in 75:23.']
    OUT.write_text('\n'.join(lines)+'\n')


if __name__ == '__main__':
    main()
