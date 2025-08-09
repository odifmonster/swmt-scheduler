#!/usr/bin/env python

from typing import NewType, Protocol, Unpack
from abc import abstractmethod

from app.support import PrettyArgsOpt, SuperView, Viewable
from app.support.groups import DataLike
from app.style import GreigeStyle

SizeClass = NewType('SizeClass', str)
PARTIAL = SizeClass('PARTIAL')
SMALL = SizeClass('SMALL')
NORMAL = SizeClass('NORMAL')
LARGE = SizeClass('LARGE')

class RollArgs(PrettyArgsOpt, total=True):

    @classmethod
    def create(cls, maxlen = 40, maxlines = 1):
        return cls(maxlen=maxlen, maxlines=maxlines)
    
class RollLike(DataLike[str, PrettyArgsOpt], Protocol):

    @property
    def _prefix(self):
        return 'ROLL'
    
    @property
    @abstractmethod
    def id(self):
        raise NotImplementedError()
    
    @property
    @abstractmethod
    def item(self):
        raise NotImplementedError()
    
    @property
    @abstractmethod
    def weight(self):
        raise NotImplementedError()
    
    @property
    @abstractmethod
    def size_class(self):
        raise NotImplementedError()
    
    @abstractmethod
    def allocate(self, amount):
        raise NotImplementedError()
    
    def pretty(self, **kwargs):
        return f'{self._prefix}(id={repr(self.id)}, item={repr(self.item)}, weight={self.weight:.2f})'

class RollView(SuperView[RollLike],
               no_access=['allocate'],
               overrides=[],
               dunders=['eq', 'hash']):
    pass

class Roll(RollLike, Viewable[RollView]):

    def __init__(self, id: str, greige: GreigeStyle, weight: float):
        self.__id = id
        self.__greige = greige
        self.__weight = weight
        self.__view = RollView(self)

    @property
    def id(self):
        return self.__id
    
    @property
    def item(self):
        return self.__greige
    
    @property
    def weight(self):
        return self.__weight
    
    @property
    def size_class(self):
        if self.__greige.roll_range.is_above(self.__weight+100):
            return PARTIAL
        if self.__greige.roll_range.is_above(self.__weight):
            return SMALL
        if self.__greige.roll_range.contains(self.__weight):
            return NORMAL
        return LARGE
    
    def allocate(self, amount: float):
        if self.__weight <= 0:
            raise ValueError(f'Cannot allocate {amount:.2f} pounds of a roll.')
        if self.__weight < amount:
            raise ValueError('Cannot allocate more than total pounds in a roll.')
        self.__weight -= amount

    def view(self):
        return self.__view