#!/usr/bin/env python

from app.support import HasID
from ..greige import GreigeStyle, EMPTY_GREIGE
from ..color.color import Color, BLACK

class _FabricBase(HasID[str]):

    def __init__(self, id: str, greige: GreigeStyle, master: str,
                 color: Color, yld: float, allowed_jets: list[str]):
        self.__id = id
        self.__greige = greige
        self.__master = master
        self.__color = color
        self.__yld = yld
        self.__allowed_jets = set(allowed_jets)

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
    
    def can_run_on_jet(self, jet_id: str):
        return jet_id in self.__allowed_jets and (jet_id != 'Jet-09' or self.color.shade == BLACK)
    
class FabricStyle(_FabricBase):
    pass

EMPTY_FABRIC = FabricStyle('NONE', EMPTY_GREIGE, 'NONE MASTER',
                           Color('NONE COLOR', 0, 4), 1, [])