#!/usr/bin/env python

from typing import Iterator

from collections.abc import Iterable

from ...structures import HasID
from ...inventory.roll import Roll
from ...inventory.style import Fabric
from .allocation import Allocation

LOT_IDX = 0

class _DyeLotBase(HasID[int], Iterable[Allocation]):

    def __init__(self, fabric: Fabric):
        globals()['LOT_IDX'] += 1
        HasID.__init__(self, globals()['LOT_IDX'], 'DYE LOT')
        Iterable.__init__(self)

        self.__fabric = fabric
        self.__allocs: list[Allocation] = []
    
    @property
    def pounds(self) -> float:
        return sum([a.qty for a in self.__allocs])
    
    @property
    def yards(self) -> float:
        return self.pounds * self.__fabric.yds_per_lb
    
    def __iter__(self) -> Iterator[Allocation]:
        return iter(self.__allocs)
    
    def allocate(self, roll: Roll, pounds: float) -> None:
        self.__allocs.append(Allocation(roll, pounds))
        roll.use(pounds)

class DyeLot(_DyeLotBase):
    pass