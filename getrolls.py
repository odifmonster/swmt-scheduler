#!/usr/bin/env python

from typing import NamedTuple, Generator

from app.support import FloatRange
from app.style import GreigeStyle
from app.inventory import roll, Inventory, RollView

class RollPiece(NamedTuple):
    id: str
    rview: RollView
    lbs: float

class PortLoad(NamedTuple):
    roll1: RollPiece
    roll2: RollPiece | None

class SplitRoll(NamedTuple):
    full: list[RollPiece]
    extra: RollPiece

def get_splits(rview: RollView, tgt_rng: FloatRange) -> SplitRoll:
    x = round(rview.lbs / tgt_rng.average())
    if x > 0 and tgt_rng.contains(rview.lbs / x):
        split_wt = rview.lbs / x
        full = [RollPiece(rview.id, rview, split_wt) for _ in range(x)]
        return SplitRoll(full, RollPiece(rview.id, rview, 0))
    
    split_wt = tgt_rng.average()
    nsplits = int(rview.lbs / split_wt)
    full = [RollPiece(rview.id, rview, split_wt) for _ in range(nsplits)]
    return SplitRoll(full, RollPiece(rview.id, rview, rview.lbs - nsplits*split_wt))

def get_comb_rolls(greige: GreigeStyle, inv: Inventory, extras: list[RollPiece],
                   tgt_rng: FloatRange) -> Generator[PortLoad]:
    extra_ids: set[str] = { piece.id for piece in extras }
    if roll.PARTIAL not in inv[greige]:
        return
    
    subgroup = inv[greige, roll.PARTIAL]
    pieces = extras.copy()
    
    for rid in subgroup:
        if rid not in extra_ids:
            pieces.append(RollPiece(rid, subgroup[rid], subgroup[rid].lbs))
    
    used_ids: set[str] = set()

    for i in range(len(pieces)):
        roll1 = pieces[i]
        for j in range(i+1, len(pieces)):
            roll2 = pieces[j]
            if tgt_rng.contains(roll1.lbs + roll2.lbs) and roll1.id not in used_ids and \
                roll2.id not in used_ids:
                used_ids.add(roll1.id)
                used_ids.add(roll2.id)
                yield PortLoad(roll1, roll2)

def get_normal_loads(greige: GreigeStyle, inv: Inventory, prev_wts: list[float],
                     jet_rng: FloatRange) -> Generator[PortLoad]:
    if roll.NORMAL not in inv[greige]:
        return
    
    for rid in inv[greige, roll.NORMAL]:
        rview = inv[greige, roll.NORMAL, rid]
        
        if not prev_wts:
            rng = FloatRange(max(jet_rng.minval, greige.port_range.minval),
                             min(jet_rng.maxval, greige.port_range.maxval))
        else:
            rng = FloatRange(max(max(prev_wts)-20, jet_rng.minval),
                             min(min(prev_wts)+20, jet_rng.maxval))
            
        if not rng.contains(rview.lbs / 2): continue

        prev_wts.append(rview.lbs / 2)
        yield PortLoad(RollPiece(rview.id, rview, rview.lbs / 2), None)
        yield PortLoad(RollPiece(rview.id, rview, rview.lbs / 2), None)

def get_half_loads(greige: GreigeStyle, inv: Inventory, prev_wts: list[float],
                   jet_rng: FloatRange) -> Generator[PortLoad]:
    if roll.HALF not in inv[greige]:
        return
    
    for rid in inv[greige, roll.HALF]:
        rview = inv[greige, roll.HALF, rid]

        if not prev_wts:
            rng = FloatRange(max(jet_rng.minval, greige.port_range.minval),
                             min(jet_rng.maxval, greige.port_range.maxval))
        else:
            rng = FloatRange(max(max(prev_wts)-20, jet_rng.minval),
                             min(min(prev_wts)+20, jet_rng.maxval))
            
        if not rng.contains(rview.lbs): continue

        prev_wts.append(rview.lbs)
        yield PortLoad(RollPiece(rview.id, rview, rview.lbs), None)

def get_odd_loads(greige: GreigeStyle, inv: Inventory, prev_wts: list[float],
                  jet_rng: FloatRange, extras: list[RollPiece]) -> Generator[PortLoad]:
    if not prev_wts:
        rng = FloatRange(max(jet_rng.minval, greige.port_range.minval),
                         min(jet_rng.maxval, greige.port_range.maxval))
    else:
        rng = FloatRange(max(max(prev_wts)-20, jet_rng.minval),
                         min(min(prev_wts)+20, jet_rng.maxval))
    for size in (roll.LARGE, roll.SMALL):
        if size not in inv[greige]: continue

        for rid in inv[greige, size]:
            
            splits = get_splits(inv[greige, size, rid], rng)

            for item in splits.full:
                prev_wts.append(item.lbs)
                yield PortLoad(item, None)

            if splits.extra.lbs > 20:
                extras.append(splits.extra)

def get_port_loads(greige: GreigeStyle, inv: Inventory, jet_rng: FloatRange) -> Generator[PortLoad]:
    if greige not in inv:
        return
    
    prev_wts: list[float] = []
    normal = get_normal_loads(greige, inv, prev_wts, jet_rng)
    for load in normal:
        yield load
    half = get_half_loads(greige, inv, prev_wts, jet_rng)
    for load in half:
        yield load
    extras: list[RollPiece] = []
    odd = get_odd_loads(greige, inv, prev_wts, jet_rng, extras)
    for load in odd:
        yield load
    if not prev_wts:
        tgt_rng = FloatRange(max(jet_rng.minval, greige.port_range.minval),
                             min(jet_rng.maxval, greige.port_range.maxval))
    else:
        tgt_rng = FloatRange(max(max(prev_wts)-20, jet_rng.minval),
                             min(min(prev_wts)+20, jet_rng.maxval))
    comb = get_comb_rolls(greige, inv, extras, tgt_rng)
    for load in comb:
        yield load