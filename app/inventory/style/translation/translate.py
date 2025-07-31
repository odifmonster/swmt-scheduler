#!/usr/bin/env python

import os

STYLE_DICT: dict[str, str] = {}
INITIALIZED: bool = False

def init() -> None:
    with open(os.path.join(os.path.dirname(__file__), 'trans.csv')) as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue

            inv, plan = line.split(',')
            globals()['STYLE_DICT'][inv] = plan
    globals()['INITIALIZED'] = True

def translate_style(inv_style: str) -> str:
    if not globals()['INITIALIZED']:
        raise RuntimeError('\'app.inventory.style.translate\' module not properly initialized.')
    if inv_style not in globals()['STYLE_DICT']:
        raise ValueError(f'Unknown greige style: \'{inv_style}\'')
    
    return globals()['STYLE_DICT'][inv_style]