#!/usr/bin/env python

import os

from .greige import GreigeStyle

_GREIGE_STYLES = {}

def init():
    srcpath = os.path.join(os.path.dirname(__file__), 'styles.csv')
    with open(srcpath) as infile:
        for line in infile:
            line = line.strip()
            if not line: continue

            item, tgt_lbs = line.split(',')
            tgt_lbs = float(tgt_lbs)
            globals()['_GREIGE_STYLES'][item] = GreigeStyle(item, tgt_lbs-20, tgt_lbs+20)

def get_greige_style(id: str) -> GreigeStyle | None:
    if id not in globals()['_GREIGE_STYLES']:
        return None
    return globals()['_GREIGE_STYLES'][id]