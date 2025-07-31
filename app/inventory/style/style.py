#!/usr/bin/env python

from ...structures import HasID
from .color import Color

class Style(HasID[str]):

    def __init__(self, id: str, prefix: str):
        super().__init__(id, prefix)

    @property
    def name(self) -> str:
        return self._id
    
    def __str__(self) -> str:
        return self._id
    
class Greige(Style):

    def __init__(self, id: str):
        Style.__init__(self, id, 'GREIGE')

class FabricMaster(Style):

    def __init__(self, id: str):
        super().__init__(id, 'FABRIC MASTER')

class _FabricBase(Style):

    def __init__(self,
                 id: str,
                 greige: Greige,
                 master: FabricMaster,
                 color: Color,
                 yld: float):
        Style.__init__(self, id, 'FABRIC')

        self.__greige = greige
        self.__master = master
        self.__color = color
        self.__yld = yld

    @property
    def greige(self) -> Greige:
        return self.__greige
    
    @property
    def master(self) -> FabricMaster:
        return self.__master
    
    @property
    def color(self) -> Color:
        return self.__color
    
    @property
    def yds_per_lb(self) -> float:
        return self.__yld
    
class Fabric(_FabricBase):
    pass