#!/usr/bin/env python

from .style import Style, Greige
from .color import Color

class FabricMaster(Style):

    def __init__(self, name: str):
        Style.__init__(self, name, 'MASTER STYLE')

class Fabric(Style):

    def __init__(self,
                 name: str,
                 master: FabricMaster,
                 greige: Greige,
                 color: Color,
                 yld: float):
        Style.__init__(name, 'FABRIC STYLE')

        self.__master = master
        self.__greige = greige
        self.__color = color
        self.__yld = yld

    @property
    def master(self) -> FabricMaster:
        return self.__master
    
    @property
    def greige(self) -> Greige:
        return self.__greige
    
    @property
    def color(self) -> Color:
        return self.__color
    
    @property
    def yds_per_lb(self) -> float:
        return self.__yld