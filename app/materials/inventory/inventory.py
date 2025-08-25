#!/usr/bin/env python

from typing import NamedTuple

from app.support import FloatRange, min_float_rng
from app.support.grouped import Atom, Grouped, GroupedView
from app.style import GreigeStyle
from ..roll import Roll, RollView, RollAlloc, SizeClass, LARGE, NORMAL, SMALL, HALF, PARTIAL
from .snapshot import Snapshot

class PortLoad(NamedTuple):
    roll1: RollAlloc
    roll2: RollAlloc | None
    lbs: float

class SizeGroup(Grouped[str, str]):

    def __init__(self, **kwargs):
        super().__init__(SizeView(self), 'id', **kwargs)
    
    def make_group(self, data, **kwargs):
        return Atom[str](data, 'item', 'size', 'id')
    
class SizeView(GroupedView[str, str]):
    pass

class StyleGroup(Grouped[str, SizeClass]):
    
    def __init__(self, **kwargs):
        super().__init__(StyleView(self), 'size', 'id', **kwargs)

    def make_group(self, data, **kwargs):
        return SizeGroup(size=data.size, **kwargs)

class StyleView(GroupedView[str, SizeClass]):
    pass

class Inventory(Grouped[str, GreigeStyle]):
    
    def __init__(self):
        super().__init__(InvView(self), 'item', 'size', 'id')

    def make_group(self, data, **kwargs):
        return StyleGroup(item=data.item)
    
    def get_starts(self, greige: GreigeStyle):
        if greige not in self:
            return
        
        for size in (NORMAL, HALF):
            if size not in self[greige]:
                continue
            for rview in self[greige, size].itervalues():
                yield rview
    
    def get_roll_loads(self, rview: RollView, snapshot: Snapshot, prev_wts: list[float],
                       jet_rng: FloatRange):
        if not prev_wts:
            wt_rng = rview.item.port_rng
        else:
            wt_rng = FloatRange(max(prev_wts)-20, min(prev_wts)+20)
        wt_rng = min_float_rng(wt_rng, jet_rng)

        if rview.size == NORMAL and not wt_rng.contains(rview.lbs / 2) or \
            rview.size == HALF and not wt_rng.contains(rview.lbs):
            return
        
        x = round(rview.lbs / wt_rng.average())
        if wt_rng.contains(rview.lbs / x):
            port_wt = rview.lbs / x
        elif prev_wts:
            port_wt = wt_rng.average()
        else:
            port_wt = rview.item.port_rng.average()
        
        while rview.lbs + 1 >= port_wt:
            cur_wt = min(rview.lbs, port_wt)
            prev_wts.append(cur_wt)
            roll: Roll = self.remove(rview)
            piece = roll.allocate(cur_wt, snapshot=snapshot)
            self.add(roll)
            yield PortLoad(piece, None, cur_wt)
    
    def get_comb_loads(self, greige: GreigeStyle, snapshot: Snapshot, prev_wts: list[float],
                       jet_rng: FloatRange):
        if greige not in self or PARTIAL not in self[greige]:
            return
        
        for view1 in self[greige, PARTIAL]:
            for view2 in self[greige, PARTIAL]:
                rview1: RollView = view1
                rview2: RollView = view2
                if rview1 == rview2: continue
                if rview1.lbs < 50 or rview2.lbs < 50: continue

                if not prev_wts:
                    wt_rng = greige.port_rng
                else:
                    wt_rng = FloatRange(max(prev_wts)-20, min(prev_wts)+20)
                wt_rng = min_float_rng(wt_rng, jet_rng)
                if wt_rng.is_below(rview1.lbs) or wt_rng.is_below(rview2.lbs): continue

                roll1: Roll = self.remove(view1)
                roll2: Roll = self.remove(view2)
                piece1, piece2 = None, None
                if wt_rng.contains(roll1.lbs + roll2.lbs):
                    piece1 = roll1.allocate(roll1.lbs, snapshot=snapshot)
                    piece2 = roll2.allocate(roll2.lbs, snapshot=snapshot)
                elif wt_rng.is_below(roll1.lbs + roll2.lbs):
                    wt1, wt2 = roll1.lbs, roll2.lbs
                    if roll1.lbs > roll2.lbs:
                        wt2 = wt_rng.maxval - roll1.lbs - 1
                    else:
                        wt1 = wt_rng.maxval - roll2.lbs - 1
                    
                    piece1 = roll1.allocate(wt1, snapshot=snapshot)
                    piece2 = roll2.allocate(wt2, snapshot=snapshot)

                self.add(roll1)
                self.add(roll2)
                if piece1 and piece2:
                    pload = PortLoad(piece1, piece2, piece1.lbs + piece2.lbs)
                    prev_wts.append(pload.lbs)
                    yield pload
    
    def get_port_loads(self, greige: GreigeStyle, snapshot: Snapshot, jet_rng: FloatRange,
                       start: RollView | None = None):
        if greige not in self:
            return
        
        prev_wts: list[float] = []
        if start:
            yield from self.get_roll_loads(start, snapshot, prev_wts, jet_rng)
        
        for size in (NORMAL, HALF, LARGE, SMALL):
            if size not in self[greige]: continue

            views: list[RollView] = list(self[greige, size].itervalues())
            for rview in views:
                yield from self.get_roll_loads(rview, snapshot, prev_wts, jet_rng)
        
        yield from self.get_comb_loads(greige, snapshot, prev_wts, jet_rng)

class InvView(GroupedView[str, GreigeStyle],
              funcs=('get_starts','get_roll_loads','get_comb_loads','get_port_loads')):
    pass