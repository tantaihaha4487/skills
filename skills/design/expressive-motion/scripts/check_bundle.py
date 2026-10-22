#!/usr/bin/env python3
"""Offline structure and token checks, not a visual quality score."""
import json
import re
from tokens import ROOT, TOKENS, export

def check():
    data=json.loads(TOKENS.read_text())
    assert data['kind']=='expressive-motion-tokens'
    skill=(ROOT/'SKILL.md').read_text()
    assert skill.startswith('---\nname: expressive-motion\n')
    checked=0
    for path in [ROOT/'SKILL.md',*sorted((ROOT/'references').glob('*.md'))]:
        text=path.read_text()
        assert not re.search(r'\b(TODO|TBD|FIXME)\b',text),path
        assert text.count('```')%2==0,path
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if '://' in target or target.startswith('#'): continue
            link=(path.parent/target.split('#')[0]).resolve()
            assert link.is_relative_to(ROOT),f'Out of bundle: {target}'
            assert link.exists(),f'Missing link: {target}'
            checked+=1
    for platform in ('css','qml'):
        assert len(export(data,platform))==11
    print(f'Bundle OK: {checked} links, 11 wrappers')
if __name__=='__main__': check()
