#!/usr/bin/env python

import os

from .. import greige
from .fabric import FabricStyle

_FABRIC_STYLES = {}

def init():
    if len(globals()['_FABRIC_STYLES']) > 0:
        return
    
    srcpath = os.path.join(os.path.dirname(__file__), 'styles.csv')
    with open(srcpath) as infile:
        for line in infile:
            line = line.strip()
            if not line: continue

            fab, grg, _, clr_name, clr_num, yld, shade, jets_str = line.split(',')
            fab = fab.strip()
            grg = greige.get_style(grg.strip())
            if not grg: continue

            clr_name = clr_name.strip()
            clr_num = int(clr_num)
            yld = float(yld)
            shade = int(float(shade))
            jets = jets_str.split()

            cur_item = FabricStyle(fab, grg, clr_name, clr_num, shade, yld, jets)
            globals()['_FABRIC_STYLES'][fab] = cur_item
    
    none_grg = greige.GreigeStyle('NONE', 0, 1)
    all_jets = list(map(lambda i: f'Jet-{i:02}', range(1, 11)))
    globals()['_FABRIC_STYLES']['HEAVYSTRIP'] = \
        FabricStyle('HEAVYSTRIP', none_grg, 'HEAVYSTRIP', 1, 'HEAVYSTRIP', 1,
                    all_jets)
    globals()['_FABRIC_STYLES']['STRIP'] = \
        FabricStyle('STRIP', none_grg, 'STRIP', 2, 'STRIP', 1, all_jets)
    globals()['_FABRIC_STYLES']['EMPTY'] = \
        FabricStyle('EMPTY', none_grg, 'EMPTY', 3, 'EMPTY', 1, all_jets)

def get_style(id):
    if id not in globals()['_FABRIC_STYLES']:
        return None
    return globals()['_FABRIC_STYLES'][id]