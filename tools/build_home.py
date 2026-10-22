#!/usr/bin/env python3
"""Keep the Pages home and repository README on the same editorial source."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    source=(ROOT/'README.md').read_text()
    if not source.startswith('---\n') or '\n---\n' not in source[4:]:
        raise ValueError('README.md must begin with explicit YAML front matter')
    header,body=source[4:].split('\n---\n',1)
    (ROOT/'index.md').write_text('---\n'+header+'\npermalink: /\n---\n'+body)
    print('index.md generated from README.md')
if __name__=='__main__':main()
