#!/usr/bin/env python

import os

INFILE = 'translate.csv'
STYLE_DICT = {}

def init():
    with open(os.path.join(os.path.dirname(__file__), INFILE)) as infile:
        for line in infile:
            line = line.strip()
            if not line: continue

            inv, plan = line.split(',')
            globals()['STYLE_DICT'][inv] = plan

def translate_greige_style(inv_name):
    return STYLE_DICT.get(inv_name, '')