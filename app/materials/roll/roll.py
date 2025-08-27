#!/usr/bin/env python

from typing import NewType

from app.support.grouped import Data, DataView
from app.support import HasID, SuperImmut, setter_like
from app.style import GreigeStyle

SizeClass = NewType('SizeClass', str)
LARGE = SizeClass('LARGE')
NORMAL = SizeClass('NORMAL')
SMALL = SizeClass('SMALL')
HALF = SizeClass('HALF')
PARTIAL = SizeClass('PARTIAL')

_CTR = 0

class RollAlloc(HasID[int], SuperImmut,
                attrs=('_prefix','id','roll_id','lbs'),
                priv_attrs=('id',), frozen=('*id','roll_id','lbs')):

    def __init__(self, roll_id, lbs):
        globals()['_CTR'] += 1
        SuperImmut.__init__(self, priv={'id': globals()['_CTR']},
                            roll_id=roll_id, lbs=lbs)

    def __repr__(self):
        return f'RollAlloc(roll={repr(self.roll_id)}, lbs={self.lbs:.2f})'
    
    @property
    def _prefix(self):
        return 'RollAlloc'
    
    @property
    def id(self):
        return self.__id

class Roll(Data[str], mod_in_group=False, attrs=('item','size','lbs','snapshot'),
           priv_attrs=('init_wt','cur_wt','allocs','temp_allocs'),
           frozen=('*init_wt','item')):
    
    def __init__(self, id, item, lbs):
        Data.__init__(self, id, 'Roll', RollView(self),
                      priv={'init_wt': lbs, 'cur_wt': lbs, 'allocs': set(), 'temp_allocs': {}},
                      item=item, snapshot=None)

    def __repr__(self):
        return f'Roll(id={repr(self.id)}, item={repr(self.item)}, wt={round(self.lbs, ndigits=2)})'

    @property
    def lbs(self):
        if self.snapshot is None or self.snapshot not in self.__temp_allocs:
            return self.__cur_wt
        return self.__cur_wt - sum(map(lambda p: p.lbs, self.__temp_allocs[self.snapshot]))
    
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
    def allocate(self, lbs, snapshot = None):
        ret = RollAlloc(self.id, lbs)
        if snapshot is None:
            if self.__cur_wt + 1 < lbs:
                raise ValueError(f'{lbs:.2f} lbs exceeds remaining weight in roll ({self.lbs:.2f})')
            self.__allocs.add(ret)
            self.__cur_wt -= lbs
        else:
            if snapshot not in self.__temp_allocs:
                self.__temp_allocs[snapshot] = set()
            temp_lbs = self.__cur_wt - sum(map(lambda p: p.lbs, self.__temp_allocs[snapshot]))
            if temp_lbs + 1 < lbs:
                raise ValueError(f'{lbs:.2f} lbs exceeds remaining weight in roll ({temp_lbs:.2f})')
            self.__temp_allocs[snapshot].add(ret)
        return ret
    
    @setter_like
    def deallocate(self, piece, snapshot = None):
        if snapshot is None:
            if self.id == 'WF921130':
                print(piece, piece.id)

            self.__allocs.remove(piece)
            self.__cur_wt += piece.lbs
        else:
            self.__temp_allocs[snapshot].remove(piece)

    @setter_like
    def apply_snap(self, snapshot = None):
        if snapshot and snapshot in self.__temp_allocs:
            for item in self.__temp_allocs[snapshot]:
                self.__allocs.add(item)
                self.__cur_wt -= item.lbs
        
        self.__temp_allocs.clear()

class RollView(DataView[str], attrs=('item','size','lbs','snapshot'),
               funcs=('allocate','deallocate','release_snaps'),
               dunders=('repr',)):
    pass