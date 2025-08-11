#!/usr/bin/env python

from app.support import HasID
from app.inventory.roll import Roll
from ..demand import Demand
from .allocation import Allocation

_LOT_CTR = 0

class _DyeLotBase(HasID[str]):

    def __init__(self, dmnd: Demand, int_id: int = -1):
        if int_id < 0:
            globals()['_LOT_CTR'] += 1
            self.__id = globals()['_LOT_CTR']
        else:
            self.__id = int_id
        
        self.__dmnd = dmnd
        self.__allocs: list[Allocation] = []

    @property
    def _prefix(self):
        return 'DYELOT'
    
    @property
    def id(self):
        return f'{self.__id:010}'
    
    @property
    def dmnd(self):
        return self.__dmnd.view()
    
    @property
    def item(self):
        return self.__dmnd.item
    
    @property
    def lbs(self):
        return sum(map(lambda x: x.lbs, self.__allocs))
    
    @property
    def yds(self):
        return self.lbs * self.item.yds_per_lb
    
    def __repr__(self):
        return f'{self._prefix}(id={self.id}, item={self.item.id}, lbs={self.lbs:.2f})'
    
    def assign_roll(self, roll: Roll, lbs: float):
        self.__allocs.append(Allocation(roll, lbs))
        self.__dmnd.assign(lbs)
    
    def unassign_roll(self, roll: Roll):
        for i in range(len(self.__allocs)):
            a = self.__allocs[i]
            if a.roll.id == roll.id:
                self.__dmnd.unassign(a.lbs)
                roll.deallocate(a.lbs)

class DyeLot(_DyeLotBase):
    pass