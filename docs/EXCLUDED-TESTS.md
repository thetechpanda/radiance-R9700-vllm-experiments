---
layout: default
title: "Excluded exploratory tests"
---

# Excluded exploratory tests

The public release retains the core single-card concurrency/capacity milestones, their resource traces, the relevant ROCm stress reference and the completed ROCm 10.1 repeat cells. Other exploratory results are summarised here; their per-turn CSVs are omitted. Restored exploratory SVGs remain in the [secondary graph archive](../graphs/rocm-7.14/unchosen.md), with per-graph exclusion reasons. Private source evidence is preserved.

Compaction-depth sweeps, storage/loop/tier experiments, scheduling and speculation variants, instrumentation checks, tainted/failed attempts and early agent-harness probes addressed tuning or boundary questions. They do not provide a matched ROCm comparison or the central 131k single-card concurrency result.

The historical one- and two-agent references are short growth tests; the RAM16 three- and four-agent milestones use different histories. The retained older/newer four-agent stress pair is also unmatched. None is presented as a controlled scaling curve.

[Machine-readable exclusion summary](../data/excluded-tests.csv)

| Coverage | Excluded entries | Why omitted |
|---|---:|---|
| Telemetry slots | 30 | Exploratory tuning, instrumentation, storage, compaction, capacity boundaries or separate harness trials; includes one empty slot. |
| Historical benchmark cells | 42 | Redundant or unmatched workload/configuration variants outside the focused comparison. |

<!-- NAVIGATION START -->

[Home](../index.md) · [Overview](../README.md) · [ROCm 10.1 results](FINAL-REPORT-20261018.md) · [Charts](CHARTS.md)
