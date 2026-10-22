#!/usr/bin/env python3
"""Refresh only the marked source inventory in the hand-edited code-corner article."""
import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
START='<!-- CODE INVENTORY START -->'
END='<!-- CODE INVENTORY END -->'
ROLES={
'agent_bench.py':('Live inference','Portable replacement synthetic-load client; JSON summary'),
'radiance-top':('Metrics reads + local sensors','Dual-engine monitor; reads endpoints and host DRM, no inference'),
'falling_blocks_prompt.py':('Local files','Seeded game-task text generator'),
'parse_falling_blocks_events.py':('Local private inputs','Latest Pi session per agent -> usage/timing fields'),
'make_qkv_sidecar.py':('Local artefact creation','Validated Q/K/V scale derivation; Radiance/safetensors dependencies'),
'run_falling_blocks_agent.sh':('Client containers + live inference','One seeded Pi task; writes private sessions/logs'),
'run_falling_blocks_fleet.sh':('Client containers + live inference','Concurrent game agents; separate health/provider endpoints'),
'bench_agents4.py':('Live inference + runtime inspection','Exact recovered original; synthetic text/images and raw CSV provenance'),
'needle160k.py':('Live inference immediately','Exact recovered large-prompt probe; no CLI/help mode'),
'run_grid.sh':('Live inference','Adapted sequential grid; server configuration is external'),
'convert_model.sh':('Model conversion container','Adapted M2 recipe; operator-provided image/input, new output'),
'Containerfile':('Image build / network during build','Recovered Pi 1.1.0 recipe; requires operator provider/settings files'),
'models.example.json':('Configuration example','Sanitized provider/endpoint/model budgets, not a credential file'),
'settings.example.json':('Configuration example','Recorded Pi compaction and thinking settings'),
'build_release.py':('Local, private archive required','Curated telemetry/case transformation; RESEARCH_SOURCE required'),
'build_run_index.py':('Local released inputs','Run index from transformed CSVs, catalogues and editorial notes'),
'build_comparison_data.py':('Local released inputs','Comparison arithmetic/rounding and corrected game paths'),
'build_home.py':('Local publication','Canonical README -> Pages index'),
'build_navigation.py':('Local publication','Gallery/footer/front matter; calls editorial/code/game generators'),
'build_code_corner.py':('Local publication','Refresh this marked inventory; preserve narrative'),
'build_game_gallery.py':('Local publication','Verify released bytes/hashes and regenerate game gallery'),
'build_unchosen_graphs.py':('Local publication','Retained exploratory graph archive and exclusion descriptions'),
'chart_theme.py':('Local SVG writes','Apply shared palette to existing SVGs'),
'check_pages.py':('Local built HTML','Check local file/anchor links; does not render or validate facts'),
'check_recovery.py':('Local source verification','Check recovery manifest hashes; no recovered code execution'),
'check_falling_blocks.cjs':('Local game-code execution','Node mocked-DOM checks for supported historical game API shapes'),
'organise_results.py':('Local released inputs','Versioned result/catalogue organization and inventories'),
'page_metadata.py':('Local publication','Add missing front matter; excludes private paths/AGENTS'),
'render_csv.py':('Local released inputs','General CSV-to-SVG renderer'),
'render_editorial.py':('Local released inputs','Editorial comparison charts and source-hash manifest'),
'render_follow_up.py':('Local released inputs','Earlier single/dual/fleet report figures and hashes'),
'render_spec_campaign.py':('Local released inputs','Model/speculation sweep, vision and depth-band figures'),
}
def main():
    rows=[]
    for directory in ('scripts','tools','patches'):
        for p in sorted((ROOT/directory).rglob('*')):
            if not p.is_file() or any(part.startswith('.') for part in p.relative_to(ROOT).parts) or '__pycache__' in p.parts or p.suffix in ('.md','.png','.pyc'):continue
            if p.suffix not in ('.py','.sh','.cjs','.json','.patch') and p.name not in ('radiance-top','Containerfile'):continue
            rel=p.relative_to(ROOT).as_posix()
            if 'editorial_fleet' in p.parts:effect,purpose='Live inference + local tool reads','AI draft/evidence task orchestration; private outputs, not a publication build'
            elif p.name.startswith('launch-'):effect,purpose='Inference launch / possible host changes','Historical profile or template; read selected settings before use'
            elif p.suffix=='.patch':effect,purpose='Host kernel source change','Recorded Intel bridge P2PDMA eligibility patch; requires topology qualification'
            else:effect,purpose=ROLES.get(p.name,('Unclassified: inspect before use','New source file; add an explicit effect/role to the inventory generator'))
            label=f'[{rel}](../{rel})' if directory!='tools' else f'`{rel}`'
            rows.append(f'| {label} | {effect} | {purpose} |')
    rows.append('| `.github/workflows/pages.yml` | CI build; deployment on configured main-branch events | Native Pages build, local-link checks and publication; does not run every generator |')
    page=ROOT/'docs/CODE-CORNER.md';s=page.read_text();a=s.index(START)+len(START);b=s.index(END,a)
    table='\n\n| Source | Effect / prerequisite | Purpose |\n|---|---|---|\n'+'\n'.join(rows)+'\n\n'
    page.write_text(s[:a]+table+s[b:]);print(f'Code-corner inventory: {len(rows)} scripts/configs/workflow entries')
if __name__=='__main__':main()
