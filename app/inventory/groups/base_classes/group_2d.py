#!/usr/bin/env python

from typing import Iterator, TypeVar, Generic

from abc import abstractmethod

from ....structures import Iter2D
from ...roll import Roll, SizeClass
from ...style import Greige
from .group import Group, INIT_SIZE

T = TypeVar('T', SizeClass, Greige)
U = TypeVar('U', bound=Group)

class Group2D(Group, Generic[T, U]):

    def __init__(self, init_size: int = INIT_SIZE):
        Group.__init__(self, init_size)

        self.__groups: dict[T, U] = {}

    @property
    def total_weight(self) -> float:
        return sum([g.total_weight for g in self.__groups.values()])
    
    def _add_pair(self, key: T, value: U) -> None:
        self.__groups[key] = value
    
    def __iter__(self) -> Iterator[Roll]:
        return Iter2D(list(self.__groups.values()))
    
    @abstractmethod
    def _add_group(self, prop: T) -> None:
        raise NotImplementedError()
    
    @abstractmethod
    def _get_prop(self, roll: Roll) -> T:
        raise NotImplementedError()
    
    def add_roll(self, roll: Roll) -> None:
        Group.add_roll(self, roll)

        prop = self._get_prop(roll)
        group = self.__groups[prop]
        group.add_roll(roll)

    def remove_roll(self, roll: Roll) -> Roll:
        Group.remove_roll(self, roll)

        prop = self._get_prop(roll)
        group = self.__groups[prop]
        return group.remove_roll(roll)