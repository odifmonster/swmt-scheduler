#!/usr/bin/env python

from typing import NewType

from ..style import Style, Greige
from ..color import Color

FabricMaster = NewType('FabricMaster', str)

class Fabric(Style):

    def __init__(self, id: str, greige: Greige, master: str, color: Color, yld: float):
        super().__init__(id, 'FABRIC_STYLE')

        self.__greige = greige
        self.__master = FabricMaster(master)
        self.__color = color
        self.__yld = yld

    @property
    def greige(self):
        return self.__greige
    
    @property
    def master(self):
        return self.__master
    
    @property
    def color(self):
        return self.__color
    
    @property
    def yds_per_lb(self):
        return self.__yld
    
    def __str__(self):
        ret = f'FABRIC_STYLE'
        ret += f'\n  [name=\'{self.name}\','
        ret += f'\n   master=\'{self.master}\','
        ret += f'\n   color=\'{self.color.name}\']'
        return ret