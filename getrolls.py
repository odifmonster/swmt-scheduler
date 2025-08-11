#!/usr/bin/env python

from typing import NamedTuple, Iterator, Generator

from app.support import FloatRange

from app.style import GreigeStyle

from app.inventory.roll import RollView, PARTIAL, SMALL, NORMAL, LARGE
from app.inventory import Inventory

from app.schedule.jet import Jet

class RollSplitItem(NamedTuple):
    roll: RollView
    lbs: float

class RollSplit:

    def __init__(self, roll: RollView):
        self.__roll = roll
        self.__splits: list[RollSplitItem] = []
        self.__excess: RollSplitItem | None = None

    @property
    def roll(self) -> RollView:
        return self.__roll

    @property
    def excess_cost(self) -> int:
        if self.__excess is None:
            return 0
        if self.__excess.lbs < 20:
            return 0
        if self.__excess.lbs < 150:
            return 3
        if self.__excess.lbs < self.__roll.item.port_range.minval:
            return 2
        return 1
    
    def __iter__(self) -> Iterator[RollSplitItem]:
        return iter(self.__splits)

    def reset(self) -> None:
        self.__splits = []
        self.__excess = None

    def split(self, tgt_lbs: float, wt_rng: FloatRange) -> None:
        if tgt_lbs - self.__roll.weight > 20:
            self.__excess = RollSplitItem(self.roll, self.roll.weight)
            return
        if tgt_lbs - self.__roll.weight >= 0:
            self.__splits = [RollSplitItem(self.roll, self.roll.weight)]
            return
        
        x = round(self.__roll.weight / tgt_lbs)
        avg_split = self.__roll.weight / x
        if wt_rng.contains(avg_split) and abs(avg_split - tgt_lbs) <= 20:
            self.__splits = [RollSplitItem(self.__roll, avg_split) for _ in range(x)]
        else:
            n_splits = int(self.__roll.weight / tgt_lbs)
            extra_wt = self.__roll.weight - tgt_lbs*n_splits
            self.__splits = [RollSplitItem(self.__roll, tgt_lbs) for _ in range(n_splits)]
            self.__excess = RollSplitItem(self.__roll, extra_wt)

def is_valid_roll(roll: RollView, greige: GreigeStyle, dmnd_lbs: float, jet: Jet) -> bool:
    if roll.size_class == SMALL:
        return False
    
    wt = roll.weight / 2
    roll_ports = 2
    if roll.size_class == PARTIAL:
        wt = roll.weight
        roll_ports = 1

    roll_ports = min(jet.n_ports, roll_ports)
    
    if not (jet.port_range.contains(wt) and jet.port_range.contains(wt)):
        return False
    if not (greige.port_range.contains(wt)):
        return False
    
    return wt*jet.n_ports >= dmnd_lbs

def start_rolls(inv: Inventory, greige: GreigeStyle, dmnd_lbs: float, jet: Jet) -> Generator[RollView]:
    sizes = (NORMAL, LARGE, PARTIAL)
    if jet.n_ports == 1:
        sizes = (PARTIAL, NORMAL, LARGE)
    for size in sizes:
        if size not in inv[greige]: continue
        for roll_id in inv[greige, size]:
            roll = inv[greige, size, roll_id]
            if is_valid_roll(roll, greige, dmnd_lbs, jet):
                yield roll

def get_roll_splits(options: list[RollSplit],
                    start_roll: RollView,
                    jet: Jet) -> list[RollSplit]:
    res: list[RollSplitItem] = []
    
    tgt_lbs = start_roll.weight / 2
    if start_roll.size_class == PARTIAL:
        tgt_lbs = start_roll.weight

    min_lbs = max(tgt_lbs-20, jet.port_range.minval, start_roll.item.port_range.minval)
    max_lbs = jet.port_range.maxval
    wt_rng = FloatRange(min_lbs, max_lbs)
    
    for rsplit in options:
        rsplit.split(tgt_lbs, wt_rng)

        if rsplit.roll == start_roll:
            for item in rsplit:
                if len(res) == jet.n_ports:
                    return res
                res.append(item)
    
    options.sort(key=lambda rs: rs.excess_cost)

    for rsplit in options:
        if rsplit.roll == start_roll: continue
        for item in rsplit:
            if len(res) == jet.n_ports:
                return res
            res.append(item)
    
    return res

def get_greige_rolls(inv: Inventory,
                     greige: GreigeStyle,
                     dmnd_lbs: float,
                     jet: Jet) -> list[RollSplitItem]:
    options: list[RollSplit] = []
    for size in inv[greige]:
        for roll_id in inv[greige, size]:
            options.append(RollSplit(inv[greige, size, roll_id]))
    
    start_opts = start_rolls(inv, greige, dmnd_lbs, jet)
    for start in start_opts:
        rsplits = get_roll_splits(options, start, jet)
        if len(rsplits) == jet.n_ports:
            return rsplits
        for x in options:
            x.reset()
    return []