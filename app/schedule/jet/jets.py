#!/usr/bin/env python

import os, datetime as dt

from .jet import Jet

_JET_MAP = {}
_ALT_JET_MAP = {}

def init(start: dt.datetime, end: dt.datetime):
    if len(globals()['_JET_MAP']) > 0 and len(globals()['_ALT_JET_MAP']) > 0:
        return

    with open(os.path.join(os.path.dirname(__file__), 'jets.csv')) as infile:
        for line in infile:
            line = line.strip()
            if not line: continue

            jet_id, alt_id, n_ports, min_load, max_load = line.split(',')
            n_ports = int(n_ports)
            min_load = float(min_load)
            max_load = float(max_load)

            newjet = Jet(jet_id, n_ports, min_load, max_load, start, end)
            _JET_MAP[jet_id] = newjet
            _ALT_JET_MAP[alt_id] = newjet

def get_jets():
    return list(globals()['_JET_MAP'].values())

def get_by_alt_id(id):
    if id not in globals()['_ALT_JET_MAP']:
        return None
    return globals()['_ALT_JET_MAP'][id]