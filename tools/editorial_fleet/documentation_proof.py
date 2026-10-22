"""Six bounded final documentation reviews against a public-only snapshot."""
import concurrent.futures
import fleet
original=fleet.ROOT
fleet.ROOT=original/'documentation-proof';fleet.ROOT.mkdir(exist_ok=True);fleet.REPO=original/'repo'
common='''Final source review. Read the named files, return only concrete defects and source evidence, maximum600words; do not draft replacements or execute code. Direct verified fleet receipts:agent0/1exit124,agent2/3exit0;4/4delivery2/4clean. Recovery originalharness is present; portableclient isdifferent. PPpromptprocessing; allocatedpoolnotperformance; percarddensity uses sharedpooltokens, do notdivide byGPUcount. Missing0TTFTbandsnotlatencyzero. Do not infer templateorprofilelabel actuallyconfiguresserver. The historical originalprompts intentionallyretain olderrors. '''
fleet.TASKS={
'proof-setup':common+'Read docs/ENVIRONMENT.md against HARDWARE.md,DUAL-GPU.md,SCRIPTS.md,PODMAN.md. Check hostvscontainer, kernelqualification,datedmemorybudgets,model/calibration,unknowncomponents,claimedcausality. Flag onlyactualmismatch.',
'proof-history':common+'Read docs/RESEARCH-HISTORY.md against RESEARCH-JOURNAL.md,FINAL-REPORT-20261018.md,sweepCSV,radianceCSV/fleetCSV. Check chronology,numbers,inventedquotes/motives,retainedfailures,new2/4correction. Keep historianvoice but no ungroundedstory.',
'proof-code':common+'Read docs/CODE-CORNER.md and scripts/recovered/README.md against referenced scripts and tools/build_code_corner.py. Check commandflags,baseURLsuffixes,sideeffects,alltoolcoverage,rawCSV/privacy and originalvsadapterdistinction. No execution.',
'proof-disclosure':common+'Read docs/REPRODUCIBILITY.md,EDITORIAL-REVIEW.md,data/recovery-manifest.json and recoverededitorialdrivers. Check automationclaimscope,private/missinginputs,AIassistancecounts:18initial+3followupdraft+6finalproof, originalpromptsnowpublished but notallperpasssnapshots. Flag misleadingclaims.',
'proof-maintenance':common+'Read AGENTS.md,_config.yml,tools/page_metadata.py,build_navigation.py,build_home.py,build_code_corner.py and docs/PAGES.md. Checkmaintenanceinstructionsmatchactualgeneratedsources,siteexclusions,originalhumanpreservation,evidencepolicy. AGENTS shouldversionedbutnotrendered. No inventedblockingapprovalrules.',
'proof-home':common+'Read README.md, docs/RADIANCE.md,RADIANCE-VS-VLLM.md,RADIANCE-CAMPAIGN-2026-10-21.md,DATA-DICTIONARY.md and fleetCSV. Checknewhardwarestory/links/transparency,2/4cleanthroughout,15gamecounts,allclaimsclear/nocontradictions. Mention exactremainingbadquotesonly.'}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as p:list(p.map(fleet.run,fleet.TASKS.items()))
