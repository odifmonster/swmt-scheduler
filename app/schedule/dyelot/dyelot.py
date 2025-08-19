#!/usr/bin/env python

from typing import Protocol
import datetime as dt

from app.support import HasID, SuperImmut, SuperView, Viewable
from app.style import GreigeStyle, FabricStyle, Color
from app.inventory import AllocRoll

_CTR = 0

class _ReqView(Protocol):
    item: FabricStyle
    @property
    def _prefix(self) -> str: ...
    @property
    def id(self) -> str: ...
    @property
    def greige(self) -> GreigeStyle: ...
    @property
    def color(self) -> Color: ...
    @property
    def lots(self) -> list['DyeLotView']: ...

class DyeLotView(SuperView['DyeLot'],
                 dunders=['repr','eq','hash'],
                 attrs=['_prefix','id','start','end','rolls','item','greige',
                        'color','yds','lbs']):
    pass

class DyeLot(HasID[int], Viewable[DyeLotView], SuperImmut,
             attrs=('_prefix','id','start','end','rolls','item','greige','color','yds',
                    'lbs'),
             priv_attrs=('prefix','id','view','req'),
             frozen=('_DyeLot__prefix','_DyeLot__id','_DyeLot__view','_DyeLot__req','rolls','item')):
    
    def __init__(self, rolls: list[AllocRoll], item: FabricStyle, rview: _ReqView) -> None:
        globals()['_CTR'] += 1
        priv={
            'prefix': 'DyeLot', 'id': globals()['_CTR'], 'view': DyeLotView(self),
            'req': rview
        }
        SuperImmut.__init__(self, priv=priv, start=dt.datetime.fromtimestamp(0),
                            end=dt.datetime.fromtimestamp(10), rolls=tuple(rolls),
                            item=item)
    
    @property
    def _prefix(self):
        return self.__prefix
    
    @property
    def id(self):
        return self.__id
    
    @property
    def greige(self) -> GreigeStyle:
        return self.item.greige
    
    @property
    def color(self) -> Color:
        return self.item.color
    
    @property
    def lbs(self) -> float:
        return sum([r.lbs for r in self.rolls])
    
    @property
    def yds(self) -> float:
        return self.lbs * self.item.yld
    
    def view(self):
        return self.__view