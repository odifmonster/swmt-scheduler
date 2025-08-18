#!/usr/bin/env python

import os

from ..greige import get_greige_style
from ..color import Color
from .fabric import FabricStyle

_FABRIC_STYLES = {}

def init() -> None:
    srcpath = os.path.join(os.path.dirname(__file__), 'styles.csv')
    with open(srcpath) as infile:
        for line in infile:
            line = line.strip()
            if not line: continue

            fab, grg, master, clr_name, clr_num, yld, shade, jets_str = line.split(',')
            fab = fab.strip()
            grg = get_greige_style(grg.strip())
            if not grg: continue

            master = master.strip()
            clr_name = clr_name.strip()
            clr_num = int(clr_num)
            yld = float(yld)
            shade = int(shade)
            jets = jets_str.split()

            cur_color = Color(clr_name, clr_num, shade)
            cur_item = FabricStyle(fab, grg, master, cur_color, yld, jets)
            globals()['_FABRIC_STYLES'][fab] = cur_item

def get_fabric_style(id: str) -> FabricStyle | None:
    if id not in globals()['_FABRIC_STYLES']:
        return None
    return globals()['_FABRIC_STYLES'][id]