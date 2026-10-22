#!/usr/bin/env python3
"""Apply the reviewed release selection to data, graphs and generated guides."""
import csv
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = ('rocm-7.14', 'rocm-10.1', 'version-unverified')
LABELS = {'rocm-7.14': 'ROCm 7.14', 'rocm-10.1': 'ROCm 10.1', 'version-unverified': 'Version unverified'}


def catalogue(name='telemetry'):
    return json.loads((ROOT/'data'/f'{name}-catalog.json').read_text())


def write_csv(path, rows):
    if not rows:
        raise ValueError(f'No rows for {path}')
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def editorial_section(path, heading):
    """Retain reviewed interpretation when regenerating data inventories."""
    if not path.exists():
        return ''
    content = path.read_text().split('<!-- NAVIGATION START -->')[0]
    marker = '\n## ' + heading
    return content[content.index(marker):].rstrip() + '\n' if marker in content else ''


def main():
    entries, cases = catalogue(), catalogue('case')
    case_map = {e['legacy_id']: e for e in cases}
    moved = {}
    for family in ('data', 'graphs'):
        for version in VERSIONS:
            (ROOT/family/version).mkdir(parents=True, exist_ok=True)
    exclusion_page = ROOT/'docs/EXCLUDED-TESTS.md'
    for e in entries:
        for family, suffix in (('data', '.csv'), ('graphs', '.svg')):
            final = ROOT/family/e['version']/(e['slug']+suffix)
            candidates = [ROOT/family/(e['legacy_id']+'-telemetry'+suffix)]
            candidates += [ROOT/family/v/(e['slug']+suffix) for v in VERSIONS]
            for old in candidates:
                preserve = e['included'] or family == 'graphs'
                moved[old] = final if preserve else exclusion_page
                if not old.exists():
                    continue
                if preserve:
                    if old != final:
                        old.replace(final)
                else:
                    # Source evidence remains in the separately held research archive.
                    old.unlink()
    old_cases = ROOT/'data/case-summary.csv'
    sources = [old_cases] + [ROOT/'data'/v/'historical-agent-workloads.csv' for v in VERSIONS]
    rows = {}
    for path in sources:
        if path.exists():
            with path.open() as stream:
                for row in csv.DictReader(stream):
                    rows[row['case_id']] = row
    selected = []
    for case_id, row in sorted(rows.items()):
        meta = case_map[case_id]
        if not meta['included']:
            continue
        row.update(version=meta['version'], experiment=meta['title'],
                   version_evidence='Explicit journal attribution' if meta['version']=='rocm-10.1' else 'Recorded profile/date; no per-case image ID')
        selected.append(row)
    for version in VERSIONS:
        dest = ROOT/'data'/version/'historical-agent-workloads.csv'
        group = [row for row in selected if row['version']==version]
        if group:
            write_csv(dest, group)
        elif dest.exists():
            dest.unlink()
    for family, suffix in (('data', '.csv'), ('graphs', '.svg')):
        old = ROOT/family/('case-summary'+suffix)
        moved[old] = ROOT/family/'rocm-7.14'/('historical-agent-workloads'+suffix)
        if old.exists():
            old.unlink()
    # Repair asset links before rebuilding the gallery. Excluded images become links.
    for page in ROOT.rglob('*.md'):
        if page.name.startswith('._') or page.name.lower()=='runbook.md':
            continue
        text = page.read_text()
        def link(match):
            label, dest = match.group(1), match.group(2)
            path, sep, fragment = dest.partition('#')
            if '://' in path or path.startswith('/'):
                return match.group(0)
            target = moved.get((page.parent/path).resolve())
            if target is None:
                return match.group(0)
            relative = Path(os.path.relpath(target, page.parent)).as_posix()
            prefix = '' if target == exclusion_page else match.group(0)[:match.group(0).index('[')]
            return prefix+'['+label+']('+relative+(sep+fragment if sep and target!=exclusion_page else '')+')'
        text = re.sub(r'!?\[([^\]]*)\]\(([^\s)]+)\)', link, text)
        text = text.replace('#benchmark-cases-in-release-order', '#retained-benchmark-cases')
        text = text.replace('#archived-benchmark-families', '#retained-benchmark-cases')
        page.write_text(text)
    excluded = []
    for kind, records in [('telemetry', entries), ('benchmark', cases)]:
        excluded += [dict(kind=kind, reference=e['legacy_id'], experiment=e['title'], version=e['version'], reason=e['selection_reason'])
                     for e in records if not e['included']]
    write_csv(ROOT/'data/excluded-tests.csv', excluded)
    lines = ['# Excluded exploratory tests', '',
             'The public release retains the core single-card concurrency/capacity milestones, their resource traces, the relevant ROCm stress reference and the completed ROCm 10.1 repeat cells. Other exploratory results are summarised here; their per-turn CSVs are omitted. Restored exploratory SVGs remain in the [secondary graph archive](../graphs/rocm-7.14/unchosen.md), with per-graph exclusion reasons. Private source evidence is preserved.', '',
             'Compaction-depth sweeps, storage/loop/tier experiments, scheduling and speculation variants, instrumentation checks, tainted/failed attempts and early agent-harness probes addressed tuning or boundary questions. They do not provide a matched ROCm comparison or the central 131k single-card concurrency result.', '',
             'The historical one- and two-agent references are short growth tests; the RAM16 three- and four-agent milestones use different histories. The retained older/newer four-agent stress pair is also unmatched. None is presented as a controlled scaling curve.', '',
             '[Machine-readable exclusion summary](../data/excluded-tests.csv)', '',
             '| Coverage | Excluded entries | Why omitted |', '|---|---:|---|',
             f'| Telemetry slots | {sum(not e["included"] for e in entries)} | Exploratory tuning, instrumentation, storage, compaction, capacity boundaries or separate harness trials; includes one empty slot. |',
             f'| Historical benchmark cells | {sum(not e["included"] for e in cases)} | Redundant or unmatched workload/configuration variants outside the focused comparison. |']
    exclusion_page.write_text('\n'.join(lines)+'\n')
    for version in VERSIONS:
        for family, suffix in [('data','.csv'),('graphs','.svg')]:
            page = ROOT/family/version/'README.md'
            lines = [f'# {LABELS[version]} {family}', '', 'This folder contains the selected results only. Version assignment follows the reviewed [catalogue](../../data/telemetry-catalog.json); older traces use profile/date evidence, not per-run immutable image IDs.', '']
            for e in entries:
                if e['included'] and e['version']==version:
                    lines += [f'- [{e["title"]}]({e["slug"]}{suffix})']
            for name, label in [('falling-blocks-fleet-outcomes-2026-10-18','Completed coding-fleet per-agent outcomes'), ('falling-blocks-completed-fleet-model-time-2026-10-18','Completed coding fleets: per-agent model time'), ('historical-agent-workloads','Retained historical agent workloads'), ('dual-card-text-growth-2026-10-18','Seven completed dual-card text-growth cells, 18 October 2026'), ('single-card-gpu-a-text-growth-2026-10-18','Four completed single-card GPU A text-growth cells, 18 October 2026'), ('single-card-text-growth-historical','Single-card historical context-growth report'), ('follow-up-single-vs-dual-text-growth-2026-10-18','Eight completed single/dual follow-up cells'), ('follow-up-single-vs-dual-mean-ttft-2026-10-18','Single versus dual: mean TTFT'), ('follow-up-single-vs-dual-maximum-ttft-2026-10-18','Single versus dual: maximum TTFT'), ('follow-up-single-vs-dual-request-decode-rate-2026-10-18','Single versus dual: request decode estimate'), ('single-card-rocm-7.14-ram16-vs-rocm-10.1-ram10','Historical RAM16 versus RAM10: configuration comparison')]:
                if (page.parent/(name+suffix)).exists():
                    lines += [f'- [{label}]({name}{suffix})']
            lines += ['', '[What was excluded and why](../../docs/EXCLUDED-TESTS.md). Different workload/configuration histories are not a controlled ROCm A/B.']
            if family == 'graphs' and version == 'rocm-7.14':
                lines += ['', '[Unchosen graph archive and individual exclusion reasons](unchosen.md).']
            notes = editorial_section(page, 'Campaigns and counting')
            if family == 'graphs' and version == 'rocm-10.1':
                latest = editorial_section(page, 'Latest model and speculation campaign — 19 October')
                if latest:
                    latest = latest.lstrip().split("\n## ", 1)[0]
                    notes = "\n" + latest + "\n" + notes
            lines += ['', '[Latest matrix and fleet report](../../docs/FINAL-REPORT-20261018.md).'] if version == 'rocm-10.1' else []
            if version == 'version-unverified' and len(lines) == 6:
                lines = [f'# {LABELS[version]} {family}', '', f'No selected {family} currently require this reserved category.', '']
            page.write_text('\n'.join(lines)+'\n'+notes)
    (ROOT/'data/README.md').write_text('# Research data\n\nSelected results are in [ROCm 7.14](rocm-7.14/README.md) and [ROCm 10.1](rocm-10.1/README.md). Filenames describe the experiment. The root contains only catalogues and the exclusion summary. Legacy identifiers in catalogues preserve traceability.\n\n[Excluded tests](../docs/EXCLUDED-TESTS.md) explain omitted coverage; private raw evidence remains intact.\n')
    (ROOT/'graphs/README.md').write_text('# Research graphs\n\nSelected charts are in [ROCm 7.14](rocm-7.14/README.md) and [ROCm 10.1](rocm-10.1/README.md). See the [gallery](../docs/CHARTS.md) and [exclusion summary](../docs/EXCLUDED-TESTS.md).\n')
    lines = ['# Derived data dictionary', '', 'The [versioned data folders](../data/README.md) contain selected results. Legacy identifiers are metadata for traceability. Times are relative; memory is GiB. Counter-derived rates need a prior sample. Prompt-compute credit is diagnostic, not measured prefill throughput.', '', '| Experiment | Version | CSV |', '|---|---|---|']
    for e in entries:
        if e['included']:
            lines += [f'| {e["title"]} | {LABELS[e["version"]]} | [CSV](../data/{e["version"]}/{e["slug"]}.csv) |']
    lines += ['', '[Excluded coverage](EXCLUDED-TESTS.md) is summary-only.']
    dictionary = ROOT/'docs/DATA-DICTIONARY.md'
    notes = editorial_section(dictionary, 'ROCm 10.1 campaign summaries')
    dictionary.write_text('\n'.join(lines)+'\n'+notes)
    from render_follow_up import main as render_follow_up
    render_follow_up()
    from render_csv import render
    for version in VERSIONS:
        for path in (ROOT/'data'/version).glob('*.csv'):
            if path.name != 'dual-card-text-growth-2026-10-18.csv':
                render(path, ROOT/'graphs'/version/(path.stem+'.svg'))
    import build_run_index, build_navigation
    build_run_index.main()
    from build_unchosen_graphs import main as build_archive
    build_archive()
    build_navigation.main()


if __name__ == '__main__':
    main()
