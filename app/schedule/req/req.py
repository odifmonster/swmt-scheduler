#!/usr/bin/env python

from typing import Literal
import datetime as dt

from app.support import HasID, SuperImmut, SuperView
from app.style import GreigeStyle, Color, FabricStyle

class Bucket(SuperView['Req'],
             attrs=['item','greige','color'],
             vattrs=['_Bucket__yds','_Bucket__date','yds','lbs','date']):
    
    def __init__(self, link: 'Req', yds: float, date: dt.datetime):
        self.__yds = yds
        self.__date = date
        super().__init__(link)

    @property
    def yds(self) -> float:
        return self.__yds
    
    @property
    def lbs(self) -> float:
        return self.yds * self.item.yld
    
    @property
    def date(self) -> dt.datetime:
        return self.__date

class Req(HasID[str], SuperImmut,
          attrs=('_prefix','id','item','greige','color'),
          priv_attrs=('prefix','id','buckets'),
          frozen=('_Req__prefix','_Req__id','_Req__buckets','item')):
    
    def __init__(self, item: FabricStyle, p1date: dt.datetime,
                 buckets: tuple[float, float, float, float]):
        priv = {
            'prefix': 'Req', 'id': 'REQ ' + item.id,
            'buckets': (Bucket(self, buckets[0], p1date),
                        Bucket(self, buckets[1], p1date+dt.timedelta(days=4)),
                        Bucket(self, buckets[2], p1date+dt.timedelta(days=7)),
                        Bucket(self, buckets[3], p1date+dt.timedelta(days=11)))
        }
        SuperImmut.__init__(self, priv=priv, item=item)

    @property
    def _prefix(self) -> str:
        return self.__prefix
    
    @property
    def id(self) -> str:
        return self.__id

    @property
    def greige(self) -> GreigeStyle:
        return self.item.greige
    
    @property
    def color(self) -> Color:
        return self.item.color
    
    def bucket(self, pnum: Literal[1, 2, 3, 4]) -> Bucket:
        return self.__buckets[pnum-1]