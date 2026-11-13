#!/usr/bin/env python

import os

_STYLE_MAP = {}

def init() -> None:
    if len(globals()['_STYLE_MAP']) > 0:
        return
    
    srcpath = os.path.join(os.path.dirname(__file__), 'translate.csv')
    masters = set()
    with open(srcpath) as infile:
        for line in infile:
            line = line.strip()
            if not line: continue

            inv, plan = line.split(',')
            globals()['_STYLE_MAP'][inv] = plan
            masters.add(plan)

    for m in masters:
        globals()['_STYLE_MAP'][f'GF {m}'] = m

def get_plan_name(inv_name: str) -> str | None:
    if inv_name not in globals()['_STYLE_MAP']:
        return None
    return globals()['_STYLE_MAP'][inv_name]