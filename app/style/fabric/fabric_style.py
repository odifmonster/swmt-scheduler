#!/usr/bin/env python

from app.support import HasID
from ..greige import GreigeStyle
from ..color.color import Color

class _FabricBase(HasID[str]):

    def __init__(self, id: str, greige: GreigeStyle, master: str,
                 color: Color, yld: float):
        self.__id = id
        self.__greige = greige
        self.__master = master
        self.__color = color
        self.__yld = yld

    @property
    def _prefix(self):
        return 'FABRIC_STYLE'
    
    @property
    def id(self):
        return self.__id
    
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
    
    def __repr__(self):
        return f'FabricStyle({repr(self.id)})'
    
class FabricStyle(_FabricBase):
    pass