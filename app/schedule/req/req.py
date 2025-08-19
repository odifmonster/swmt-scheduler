#!/usr/bin/env python

from typing import Literal
import datetime as dt

from app.support import HasID, SuperImmut, SuperView
from app.style import GreigeStyle, Color, FabricStyle
from app.inventory import AllocRoll
from ..dyelot import DyeLot, DyeLotView

class Bucket(SuperView['Req'],
             attrs=['item','greige','color','lots'],
             vattrs=['_Bucket__yds','_Bucket__date','yds','lbs','date']):
    
    def __init__(self, link: 'Req', yds: float, date: dt.datetime):
        self.__yds = yds
        self.__date = date
        super().__init__(link)

    @property
    def yds(self) -> float:
        lots: list[DyeLotView] = self.lots
        total_yds = 0
        for lot in lots:
            if lot.end + dt.timedelta(hours=16) <= self.date:
                total_yds += lot.yds

        return self.__yds - total_yds
    
    @property
    def lbs(self) -> float:
        return self.yds * self.item.yld
    
    @property
    def date(self) -> dt.datetime:
        return self.__date

class Req(HasID[str], SuperImmut,
          attrs=('_prefix','id','item','greige','color','lots'),
          priv_attrs=('prefix','id','buckets','lots'),
          frozen=('_Req__prefix','_Req__id','_Req__buckets','item')):
    
    def __init__(self, item: FabricStyle, p1date: dt.datetime,
                 buckets: tuple[float, float, float, float]):
        priv = {
            'prefix': 'Req', 'id': 'REQ ' + item.id,
            'buckets': (Bucket(self, buckets[0], p1date),
                        Bucket(self, sum(buckets[:2]), p1date+dt.timedelta(days=4)),
                        Bucket(self, sum(buckets[:3]), p1date+dt.timedelta(days=7)),
                        Bucket(self, sum(buckets), p1date+dt.timedelta(days=11))),
            'lots': []
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
    
    @property
    def lots(self) -> list[DyeLotView]:
        return [dl.view() for dl in self.__lots]
    
    def bucket(self, pnum: Literal[1, 2, 3, 4]) -> Bucket:
        return self.__buckets[pnum-1]
    
    def assign_lot(self, rolls: list[AllocRoll]) -> DyeLot:
        newlot = DyeLot(rolls, self.item)
        self.__lots.append(newlot)
        return newlot
    
    def unassign_lot(self, lot: DyeLotView) -> None:
        self.__lots.remove(lot)