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

    def _has_group(self, key: T) -> bool:
        return key in self.__groups

    def _get_group(self, key: T) -> U:
        return self.__groups[key]
    
    @abstractmethod
    def _add_group(self, prop: T) -> None:
        raise NotImplementedError()
    
    @abstractmethod
    def _get_prop(self, roll: Roll) -> T:
        raise NotImplementedError()
    
    def __iter__(self) -> Iterator[Roll]:
        return Iter2D(list(self.__groups.values()))
    
    def add_roll(self, roll: Roll) -> None:
        Group.add_roll(self, roll)

        prop = self._get_prop(roll)
        if not prop in self.__groups:
            self._add_group(prop)
        group = self.__groups[prop]
        group.add_roll(roll)

    def remove_roll(self, roll: Roll) -> Roll:
        prop = self._get_prop(roll)
        group = self.__groups[prop]
        group.remove_roll(roll)

        return Group.remove_roll(self, roll)