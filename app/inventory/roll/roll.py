#!/usr/bin/env python

from typing import NewType

from app.support import setter_like
from app.groups import DataView, Data
from app.style import GreigeStyle
from .alloc_roll import AllocRoll

SizeClass = NewType('SizeClass', str)
LARGE = SizeClass('LARGE')
NORMAL = SizeClass('NORMAL')
SMALL = SizeClass('SMALL')
HALF = SizeClass('HALF')
PARTIAL = SizeClass('PARTIAL')

class RollView(DataView[str], funcs=['use','reset','apply_changes'], attrs=['greige','lbs','size'],
               dunders=['repr']):
    pass

class Roll(Data[str], dattrs=('greige','lbs','size'), dpriv_attrs=('wt','temp_used'),
           dfrozen=('greige',)):
    
    def __init__(self, id: str, greige: GreigeStyle, wt: float):
        priv = { 'wt': wt, 'temp_used': 0 }
        Data[str].__init__(self, id, 'Roll', RollView(self), priv=priv, greige=greige)

    @property
    def lbs(self) -> float:
        return self.__wt - self.__temp_used
    
    @property
    def size(self):
        grg: GreigeStyle = self.greige
        if grg.roll_range.is_below(self.lbs):
            return LARGE
        if grg.roll_range.contains(self.lbs):
            return NORMAL
        if grg.port_range.is_below(self.lbs):
            return SMALL
        if grg.port_range.contains(self.lbs):
            return HALF
        return PARTIAL
    
    def __repr__(self):
        return f'{self._prefix}(style={self.greige}, lbs={self.lbs}, size={self.size})'
    
    @setter_like
    def use(self, lbs: float, aroll: AllocRoll | None = None, temp: bool = False) -> AllocRoll:
        if lbs > self.lbs:
            raise ValueError(f'{lbs:.2f} exceeds remaining pounds in roll ({self.lbs:.2f}).')
        
        if aroll is None:
            ret = AllocRoll(self.id, self.greige, lbs)
        elif aroll.greige != self.greige:
            raise ValueError(f'Cannot combine rolls with styles {self.greige} and {aroll.greige}.')
        else:
            aroll.add_roll(self.id, lbs)
            ret = aroll
        
        if temp:
            self.__temp_used += lbs
        else:
            self.__wt -= lbs
        
        return ret
    
    @setter_like
    def reset(self) -> None:
        self.__temp_used = 0

    @setter_like
    def apply_changes(self) -> None:
        self.__wt -= self.__temp_used
        self.__temp_used = 0