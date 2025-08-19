#!/usr/bin/env python

from app.support import HasID, SuperImmut
from app.style import FabricStyle
from app.inventory import AllocRoll
from ..req import Req

_CTR = 0

class DyeLot(HasID[str], SuperImmut, attrs=('_prefix', 'id', 'item', 'color', 'greige',
                                            'lbs', 'yds'),
             priv_attrs=('prefix', 'id', 'req', 'rolls'),
             frozen=('_DyeLot__prefix', '_DyeLot__id', '_DyeLot__req')):
    
    def __init__(self, req: Req):
        globals()['_CTR'] += 1
        priv = {
            'prefix': 'DyeLot', 'id': globals()['_CTR'], 'req': req, 'rolls': []
        }
        SuperImmut.__init__(self, priv=priv)
    
    @property
    def _prefix(self):
        return self.__prefix
    
    @property
    def id(self):
        return f'{self.__id:05}'
    
    @property
    def item(self) -> FabricStyle:
        return self.__req.item
    
    @property
    def color(self):
        return self.__req.color
    
    @property
    def greige(self):
        return self.__req.greige
    
    @property
    def lbs(self):
        rolls: list[AllocRoll] = self.__rolls
        return sum(map(lambda r: r.lbs, rolls))
    
    @property
    def yds(self):
        return self.lbs * self.item.yld
    
    def __iter__(self):
        return iter(self.__rolls)
    
    def add_roll(self, roll: AllocRoll) -> None:
        req: Req = self.__req
        self.__rolls.append(roll)
        req.fulfill(roll.lbs)