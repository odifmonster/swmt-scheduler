#!/usr/bin/env python

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

            item, min_lbs, max_lbs = line.split(',')
            min_lbs = float(min_lbs)
            max_lbs = float(max_lbs)
            globals()['_GREIGE_STYLES'][item] = GreigeStyle(item, min_lbs, max_lbs)

def get_style(id):
    if id not in globals()['_GREIGE_STYLES']:
        return None
    return globals()['_GREIGE_STYLES'][id]