#!/usr/bin/env python3
"""Keep explicit Jekyll front matter on public Markdown documents."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def public_page(path):
    relative = path.relative_to(ROOT)
    return not any(part.startswith(('.', '_')) for part in relative.parts) and path.name.lower() != 'runbook.md'


def ensure_front_matter():
    count = 0
    for page in ROOT.rglob('*.md'):
        if not public_page(page):
            continue
        text = page.read_text(encoding='utf-8')
        if text.startswith('---\n'):
            continue
        title = next((line[2:].strip() for line in text.splitlines() if line.startswith('# ')), page.stem)
        header = '---\nlayout: default\ntitle: ' + json.dumps(title, ensure_ascii=False) + '\n---\n\n'
        page.write_text(header + text, encoding='utf-8')
        count += 1
    return count


if __name__ == '__main__':
    print(f'Added front matter to {ensure_front_matter()} public Markdown documents')
