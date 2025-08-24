#!/usr/bin/env python

from typing import NewType

from app.support.grouped import Data, DataView
from app.support import SuperImmut, setter_like
from app.style import GreigeStyle

SizeClass = NewType('SizeClass', str)
LARGE = SizeClass('LARGE')
NORMAL = SizeClass('NORMAL')
SMALL = SizeClass('SMALL')
HALF = SizeClass('HALF')
PARTIAL = SizeClass('PARTIAL')

class RollAlloc(SuperImmut, attrs=('roll_id','lbs'), frozen=('roll_id','lbs')):
    def __init__(self, roll_id, lbs):
        SuperImmut.__init__(self, roll_id=roll_id, lbs=lbs)

class Roll(Data[str], mod_in_group=False, attrs=('item','size','lbs'),
           priv_attrs=('init_wt','cur_wt','allocs'), frozen=('*init_wt','item')):
    
    def __init__(self, id, item, lbs):
        Data.__init__(self, id, 'Roll', RollView(self),
                      priv={'init_wt': lbs, 'cur_wt': lbs, 'allocs': set()}, item=item)

    def __repr__(self):
        return f'Roll(id={repr(self.id)}, item={repr(self.item)}, wt={round(self.lbs, ndigits=2)})'

    @property
    def lbs(self):
        return self.__cur_wt
    
    @property
    def size(self):
        grg: GreigeStyle = self.item
        if grg.port_rng.is_above(self.lbs):
            return PARTIAL
        if grg.port_rng.contains(self.lbs):
            return HALF
        if grg.roll_rng.is_above(self.lbs):
            return SMALL
        if grg.roll_rng.contains(self.lbs):
            return NORMAL
        return LARGE
    
    @setter_like
    def allocate(self, lbs: float):
        globals()['_CTR'] += 1
        ret = RollAlloc(self.id, lbs)
        self.__allocs.add(ret)
        self.__cur_wt -= lbs
        return ret
    
    @setter_like
    def deallocate(self, piece: RollAlloc):
        self.__allocs.remove(piece)
        self.__cur_wt += piece.lbs

class RollView(DataView[str], attrs=('item','size','lbs'), funcs=('allocate','deallocate'),
               dunders=('repr',)):
    pass