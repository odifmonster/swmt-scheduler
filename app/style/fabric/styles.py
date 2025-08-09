#!/usr/bin/env python

import os

from ..greige import get_greige_style
from ..color import Color
from .fabric_style import FabricStyle

INFILE = 'styles.csv'
FABRIC_STYLES = {}

def init_fabric():
    with open(os.path.join(os.path.dirname(__file__), INFILE)) as infile:
        for line in infile:
            line = line.strip()
            if not line: continue

            item, greige_id, yld, master, clr_name, clr_num, shade_num, jet_str = line.split(',')
            greige = get_greige_style(greige_id)
            if greige is None:
                continue

            yld = float(yld)
            clr_num = int(clr_num)
            shade_num = int(shade_num)
            clr = Color(clr_name, clr_num, shade_num)
            jets = jet_str.split()

            fab = FabricStyle(item, greige, master, clr, yld, jets)
            globals()['FABRIC_STYLES'][item] = fab

def get_fabric_style(id: str):
    if id not in globals()['FABRIC_STYLES']:
        return None
    return globals()['FABRIC_STYLES'][id]