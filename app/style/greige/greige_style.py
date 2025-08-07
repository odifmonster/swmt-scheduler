#!/usr/bin/env python

from app.support import HasID, FloatRange

class _GreigeStyleBase(HasID[str]):

    def __init__(self, id: str, tgt_lbs: float):
        self.__id = id
        self.__port_range = FloatRange(tgt_lbs-20, tgt_lbs+20)
        self.__roll_range = FloatRange(tgt_lbs*2-40, tgt_lbs*2+40)

    @property
    def _prefix(self) -> str:
        return 'GREIGE_STYLE'
    
    @property
    def id(self) -> str:
        return self.__id
    
    @property
    def port_range(self) -> FloatRange:
        return self.__port_range
    
    @property
    def roll_range(self) -> FloatRange:
        return self.__roll_range
    
    def __repr__(self):
        return f'GreigeStyle(\'{self.id}\')'
    
class GreigeStyle(_GreigeStyleBase):
    pass