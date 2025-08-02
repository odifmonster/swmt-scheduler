#!/usr/bin/env python

from typing import NamedTuple

from .style import Style

class WeightRange(NamedTuple):
    min: float
    max: float
    avg: float

class Greige(Style):

    def __init__(self, id, std_wt):
        super().__init__(id, 'GREIGE_STYLE')
        self.__std_wt = std_wt

    @property
    def roll_range(self):
        return WeightRange(self.__std_wt-40, self.__std_wt+40, self.__std_wt)
    
    @property
    def port_range(self):
        return WeightRange(self.__std_wt/2-20,
                           self.__std_wt/2+20,
                           self.__std_wt/2)
    
    def __str__(self):
        ret = f'GREIG_STYLE'
        ret += f'\n  [style=\'{self.name}\','
        ret += f'\n   std weight={self.__std_wt:.2f}]'
        return ret