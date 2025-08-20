#!/usr/bin/env python

from typing import Literal
import datetime as dt

from app.support import HasID, SuperImmut, SuperView, Viewable, setter_like
from app.style import GreigeStyle, Color, FabricStyle
from app.inventory import AllocRoll
from ..dyelot import DyeLot, DyeLotView

class Bucket(SuperView['Req'],
             attrs=['item','greige','color','lots'],
             vattrs=['_Bucket__yds','_Bucket__date','date','yds','lbs',
                     'total_yds','total_lbs','late_yds','late_lbs']):
    
    def __init__(self, link: 'Req', yds: float, date: dt.datetime):
        self.__yds = yds
        self.__date = date
        super().__init__(link)
    
    @property
    def date(self) -> dt.datetime:
        return self.__date

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
        return self.yds / self.item.yld
    
    @property
    def total_yds(self) -> float:
        lots: list[DyeLotView] = self.lots
        return self.__yds - sum(map(lambda l: l.yds, lots))
    
    @property
    def total_lbs(self) -> float:
        return self.total_yds / self.item.yld
    
    @property
    def late_yds(self) -> tuple[float, dt.timedelta]:
        overdue_yds = self.yds
        lots: list[DyeLotView] = self.lots
        total_yds = 0
        end_time = self.date
        for lot in lots:
            if lot.end + dt.timedelta(hours=16) <= self.date or total_yds < overdue_yds:
                total_yds += lot.yds
                end_time = lot.end + dt.timedelta(hours=16)
            else:
                return (overdue_yds, end_time - self.date)
        return (overdue_yds, dt.timedelta(days=7))
    
    @property
    def late_lbs(self) -> tuple[float, dt.timedelta]:
        yds, time = self.late_yds
        return (yds / self.item.yld, time)

class ReqView(SuperView['Req'],
              funcs=['bucket','assign_lot','unassign_lot'],
              dunders=['repr','eq','hash'],
              attrs=['_prefix','id','item','greige','color','lots']):
    pass

class Req(HasID[str], Viewable[ReqView], SuperImmut,
          attrs=('_prefix','id','item','greige','color','lots'),
          priv_attrs=('prefix','id','view','buckets','lots'),
          frozen=('_Req__prefix','_Req__id','_Req__view','_Req__buckets','item')):
    
    def __init__(self, item: FabricStyle, p1date: dt.datetime,
                 buckets: tuple[float, float, float, float]):
        priv = {
            'prefix': 'Req', 'id': 'REQ ' + item.id, 'view': ReqView(self),
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
    
    def late_yd_buckets(self) -> list[tuple[float, dt.datetime]]:
        table = []
        for i in range(1,4):
            late_pair = self.bucket(i).late_yds
            if late_pair[0] > 0:
                table.append(late_pair)
        return table
    
    def late_lb_buckets(self) -> list[tuple[float, dt.datetime]]:
        table = []
        for i in range(1,4):
            late_pair = self.bucket(i).late_lbs
            if late_pair[0] > 0:
                table.append(late_pair)
        return table
    
    @setter_like
    def assign_lot(self, rolls: list[AllocRoll]) -> DyeLot:
        newlot = DyeLot(rolls, self.item, self.__view)
        self.__lots.append(newlot)
        return newlot
    
    @setter_like
    def unassign_lot(self, lot: DyeLotView) -> None:
        self.__lots.remove(lot)

    def view(self):
        return self.__view