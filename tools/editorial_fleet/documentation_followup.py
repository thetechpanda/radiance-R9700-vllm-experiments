"""Source-based follow-up drafts; run beside fleet.py with an isolated repo/ copy."""
import concurrent.futures
import fleet
original=fleet.ROOT
fleet.ROOT=original/'documentation-followup';fleet.ROOT.mkdir(exist_ok=True)
fleet.REPO=original/'repo'
common='''Chief editor: original18-task review used an erroneous fleet CSV. Direct server receipts now confirm radiance agents0/1exit124 and2/3exit0:4/4delivery2/4clean. Preserve this correction. Main modelrevisions differ9dba8a05BF16vs81a28ee7FP8, no universalwinner. Original benchmarkv4 now recovered byte-identically. Do not execute workloads. Return source-linked draft/report under1200words. '''
fleet.TASKS={
'environment-story':common+'''Read docs/HARDWARE.md,DUAL-GPU.md,SCRIPTS.md,ENGINEERING-RESEARCH.md,FP8-KV-CALIBRATION.md,RESEARCH-JOURNAL.md and PODMAN.md. Draft a compelling environment/setup article: MS-01/i5/32GBRAM/one then twoR9700s; asymmetricx8/x4 hostlinks, P2PDMAkernel qualification, coherentROCmcomponent build, checkpoint/calibration, ARC/sharedmemory budgets,monitoring, convertedradmodel transition. Distinguish hostOS fromcontainerOS, enablingwork fromcontrolledspeedgains, failedmemoryprofiles, unknownPSU/adapter. Use recorded dates not invented scenes. No unsupported claims.''',
'research-history':common+'''Read README.md,HISTORICAL-OVERVIEW.md,docs/RESEARCH-JOURNAL.md,REPEAT-CAMPAIGN.md,FINAL-REPORT-20261018.md,ENGINEERING-RESEARCH.md,EDITORIAL-REVIEW.md and radiance reports. Write historian-style chronological account for future readers: originalquestion,hardwareprogression,FP8/cache,failures,18Octmatrix,19Octsweep,21Octnewengine,22Octcapacity,subsequenteditorialcorrections. Distinguish dated records fromproven truths. No inventedquotes,motives,dates. Originalauthor says fun. Include gaps and what survives; source perperiod.''',
'code-corner-audit':common+'''Read AGENTS.md,docs/SCRIPTS.md,BENCHMARKS.md and list scripts/**/* tools/**/*. Propose Stuff for nerds codecorner with allscriptsinventory includingradiance-top,syntheticworkload,games,chart/data/navigationgeneration,recoveredoriginals. Give source-based workedexamples and mark local-only vs live inference vs servicechanging. Note originalv4 runtime-command/env capture, noseed, mayexit0withrecordederrors, portableagent_benchis different. Flag stale script guidance. No execution.'''}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:list(p.map(fleet.run,fleet.TASKS.items()))
