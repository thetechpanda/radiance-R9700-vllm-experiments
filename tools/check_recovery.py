#!/usr/bin/env python3
"""Check the released recovered-source manifest without executing any recovered code."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    entries=json.loads((ROOT/'data/recovery-manifest.json').read_text())['entries']
    for e in entries:
        actual=hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest()
        if actual!=e['released_sha256']:raise SystemExit(f'Released hash mismatch: {e["path"]}')
        if e['status'] in ('recovered_exact','verified_existing_exact') and actual!=e['source_sha256']:
            raise SystemExit(f'Original source mismatch: {e["path"]}')
    print(f'{len(entries)} recovered/adapted entries match their released hashes; originals match source hashes')
if __name__=='__main__':main()
