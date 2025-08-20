#!/usr/bin/env python

import datetime as dt

from app.support import HasID, SuperImmut, SuperView, Viewable
from app.style import GreigeStyle, FabricStyle, Color
from app.inventory import AllocRoll

_CTR = 0

class DyeLotView(SuperView['DyeLot'],
                 dunders=['repr','eq','hash'],
                 attrs=['_prefix','id','start','end','rolls','item','greige',
                        'color','yds','lbs','req','due_date']):
    pass

class DyeLot(HasID[int], Viewable[DyeLotView], SuperImmut,
             attrs=('_prefix','id','start','end','rolls','item','greige','color','yds',
                    'lbs','req','due_date'),
             priv_attrs=('prefix','id','view','req','pnum'),
             frozen=('_DyeLot__prefix','_DyeLot__id','_DyeLot__view','_DyeLot__req','_DyeLot__pnum',
                     'rolls','item')):
    
    def __init__(self, rolls: list[AllocRoll], item: FabricStyle, rview, pnum: int) -> None:
        globals()['_CTR'] += 1
        priv={
            'prefix': 'DyeLot', 'id': globals()['_CTR'], 'view': DyeLotView(self),
            'req': rview, 'pnum': pnum,
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
    
    @property
    def req(self):
        return self.__req
    
    @property
    def due_date(self):
        return self.__req.bucket(self.__pnum).date
    
    def view(self):
        return self.__view