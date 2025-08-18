#!/usr/bin/env python

from typing import NamedTuple

from app.support import HasID, SuperImmut
from app.style import GreigeStyle

_CTR = 0

class AllocPair(NamedTuple):
    id: str
    lbs: float

class AllocRoll(HasID[int], SuperImmut, attrs=('_prefix','id','greige','rolls','lbs'),
                priv_attrs=('prefix','id','roll1','roll2'),
                frozen=('_AllocRoll__prefix','_AllocRoll__id','_AllocRoll__roll1',
                        'greige')):
    
    def __init__(self, roll_id: str, greige: GreigeStyle, lbs: float):
        globals()['_CTR'] += 1
        priv = {
            'prefix': 'AllocRoll', 'id': globals()['_CTR'], 'roll1': AllocPair(roll_id, lbs),
            'roll2': None
        }
        SuperImmut.__init__(self, priv=priv, greige=greige)

    @property
    def _prefix(self) -> str:
        return self.__prefix
    
    @property
    def id(self) -> int:
        return self.__id
    
    @property
    def rolls(self) -> tuple[AllocPair] | tuple[AllocPair, AllocPair]:
        if self.__roll2 is None:
            return (self.__roll1,)
        return (self.__roll1, self.__roll2)
    
    @property
    def lbs(self):
        return sum(map(lambda p: p.lbs, self.rolls))
    
    def __repr__(self):
        return f'{self._prefix}(id={self.id:05}, style={self.greige}, lbs={self.lbs:.2f})'
    
    def add_roll(self, roll_id: str, lbs: float):
        if not self.__roll2 is None:
            raise ValueError('Cannot combine more than 2 rolls.')
        self.__roll2 = AllocPair(roll_id, lbs)