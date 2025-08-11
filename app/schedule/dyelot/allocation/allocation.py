#!/usr/bin/env python

from app.support import HasID
from app.inventory.roll import Roll

_ALLOC_CTR = 0

class _AllocationBase(HasID[int]):

    def __init__(self, roll: Roll, lbs: float):
        globals()['_ALLOC_CTR'] += 1
        self.__id = globals()['_ALLOC_CTR']

        roll.allocate(lbs)
        self.__roll = roll.view()

        self.__lbs = lbs
    
    @property
    def _prefix(self):
        return 'ALLOCATION'
    
    @property
    def id(self):
        return self.__id
    
    @property
    def roll(self):
        return self.__roll
    
    @property
    def lbs(self):
        return self.__lbs
    
    def __repr__(self):
        return f'{self._prefix}(roll={self.roll.id}, lbs={self.lbs:.2f})'
    
class Allocation(_AllocationBase):
    pass