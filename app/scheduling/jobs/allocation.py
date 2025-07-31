#!/usr/bin/env python

from ...structures import HasID
from ...inventory.roll import Roll

ALLOC_IDX = 0

class _AllocationBase(HasID[int]):

    def __init__(self, roll: Roll, qty: float):
        globals()['ALLOC_IDX'] += 1
        super().__init__(globals()['ALLOC_IDX'], 'ALLOCATION')

        self.__roll = roll
        self.__qty = qty
    
    @property
    def roll_id(self) -> str:
        return self.__roll._id
    
    @property
    def qty(self) -> float:
        return self.__qty
    
class Allocation(_AllocationBase):
    pass