#!/usr/bin/env python

from typing import NewType

from app.support import HasID, SuperImmut
from ..greige import GreigeStyle, EMPTY as EMPTY_GRG
from ..color import Color, BLACK, EMPTY as EMPTY_SHD

FabricMaster = NewType('FabricMaster', str)

class FabricStyle(HasID[str], SuperImmut,
                  attrs=('_prefix','id','greige','master','color','yld'),
                  priv_attrs=('prefix','id','jets')):
    
    def __init__(self, item: str, greige: GreigeStyle, master: str,
                 color: Color, yld: float, allowed_jets: list[str]):
        priv = {
            'prefix': 'FabricStyle', 'id': item, 'jets': tuple(allowed_jets)
        }
        SuperImmut.__init__(self, priv=priv, greige=greige,
                            master=FabricMaster(master), color=color, yld=yld)
    
    @property
    def _prefix(self):
        return self.__prefix
    
    @property
    def id(self):
        return self.__id
    
    def can_run_on_jet(self, jet_id: str):
        if self.color.shade == EMPTY_SHD:
            return True
        return jet_id in self.__jets and (jet_id != 'Jet-09' or self.color.shade == BLACK)

EMPTY = FabricStyle('NONE', EMPTY_GRG, 'NONE', Color('NONE', 0, 5), 1, [])