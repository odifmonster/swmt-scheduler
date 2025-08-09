#!/usr/bin/env python

import os

from .greige_style import GreigeStyle

INFILE = 'styles.csv'
GREIGE_STYLES = {}

def init_greige():
    with open(os.path.join(os.path.dirname(__file__), INFILE)) as infile:
        for line in infile:
            line = line.strip()
            if not line: continue

            id, tgt_lbs = line.split(',')
            tgt_lbs = float(tgt_lbs)
            greige = GreigeStyle(id, tgt_lbs)

            globals()['GREIGE_STYLES'][id] = greige

def get_greige_style(id: str):
    if id not in globals()['GREIGE_STYLES']:
        return None
    return globals()['GREIGE_STYLES'][id]