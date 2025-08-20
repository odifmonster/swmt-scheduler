#!/usr/bin/env python

import os, datetime as dt

from .jet import Jet

_JETS = []
_ALT_JETS = {}

def init(start: dt.datetime, end: dt.datetime):
    srcpath = os.path.join(os.path.dirname(__file__), 'jets.csv')
    with open(srcpath) as infile:
        for line in infile:
            line = line.strip()
            if not line: continue

            jet_id, alt_id, n_ports, min_load, max_load = line.split(',')
            jet = Jet(jet_id, int(n_ports), float(min_load), float(max_load), start, end)

            globals()['_JETS'].append(jet)
            globals()['_ALT_JETS'][alt_id] = jet

def get_jet_by_alt(alt_id: str) -> Jet | None:
    if alt_id not in globals()['_ALT_JETS']:
        return None
    return globals()['_ALT_JETS'][alt_id]

def get_jets() -> list[Jet]:
    return globals()['_JETS'].copy()