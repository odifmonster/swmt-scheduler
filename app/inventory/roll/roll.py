#!/usr/bin/env python

from typing import NewType

from ...structures import HasID
from ..style import Greige

SizeClass = NewType('SizeClass', str)

PARTIAL = SizeClass('PARTIAL')
SMALL = SizeClass('SMALL')
NORMAL = SizeClass('NORMAL')
LARGE = SizeClass('LARGE')

class _RollBase(HasID[str]):

    def __init__(self, id: str, style: Greige, weight: float):
        super().__init__(id, 'ROLL')

        self.__style: Greige = style
        self.__weight: float = weight

    @property
    def style(self) -> Greige:
        return self.__style
    
    @property
    def weight(self) -> float:
        return self.__weight

    @property
    def size_class(self) -> SizeClass:
        if self.__weight < 550:
            return PARTIAL
        if self.__weight < 650:
            return SMALL
        if self.__weight < 750:
            return NORMAL
        return LARGE
    
    def __str__(self) -> str:
        return f'ROLL[id=\'{self._id}\', style=\'{self.__style}\', size_class={self.size_class}]'
    
    def use(self, amount: float) -> None:
        if self.__weight < amount:
            raise ValueError('Cannot use more than total weight of greige roll.')
        self.__weight -= amount

class Roll(_RollBase):
    pass