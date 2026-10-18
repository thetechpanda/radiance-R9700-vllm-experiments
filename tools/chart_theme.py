#!/usr/bin/env python3
"""Shared dark SVG chart theme, including retained historical graphs."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BACKGROUND = '#0b1220'
FOREGROUND = '#e2e8f0'
FONT = 'system-ui, sans-serif'
COLOURS = {
    '#172b3a': FOREGROUND, '#142637': FOREGROUND,
    '#1f2937': FOREGROUND, '#111827': FOREGROUND,
    '#536879': '#94a3b8', '#e0e6eb': '#263449',
    '#176ca4': '#38bdf8', '#d77a22': '#fbbf24',
    '#8051a8': '#a78bfa', '#1b8a70': '#34d399',
}
ET.register_namespace('', 'http://www.w3.org/2000/svg')


def apply_theme(path):
    root = ET.fromstring(path.read_text())
    root.set('fill', FOREGROUND)
    root.set('font-family', FONT)
    # The first full-canvas rectangle is the chart background.
    first_rect = next((e for e in root if e.tag.rsplit('}',1)[-1]=='rect'), None)
    if first_rect is not None:
        first_rect.set('fill', BACKGROUND)
    for element in root.iter():
        for attribute in ('fill','stroke'):
            value = element.get(attribute)
            if value and value.lower() in COLOURS:
                element.set(attribute, COLOURS[value.lower()])
        if 'font-family' in element.attrib:
            element.set('font-family', FONT)
        if element.tag.rsplit('}',1)[-1] == 'style' and element.text:
            style = element.text
            for old,new in COLOURS.items():
                style = re.sub(re.escape(old)+r'(?![0-9a-fA-F])',new,style,flags=re.I)
            style = re.sub(r'font-family\s*:[^;}]+', 'font-family:'+FONT, style)
            element.text = style
    path.write_text(ET.tostring(root, encoding='unicode')+'\n')


def main():
    paths = sorted((ROOT/'graphs').rglob('*.svg'))
    for path in paths:
        apply_theme(path)
    print(f'Applied shared dark theme to {len(paths)} SVG charts')


if __name__ == '__main__':
    main()
