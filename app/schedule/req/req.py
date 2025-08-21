#!/usr/bin/env python

from typing import Literal
import datetime as dt

from app.groups import DataView, Data
from app.support import SuperView, setter_like
from app.style import GreigeStyle, Color, FabricStyle
from app.inventory import AllocRoll
from ..dyelot import DyeLot, DyeLotView

class Bucket(SuperView['Req'],
             attrs=['item','greige','color','lots'],
             vattrs=['_Bucket__yds','_Bucket__date','date','yds','lbs',
                     'total_yds','total_lbs','late_yds','late_lbs','yds_table']):
    
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
            if lot.end is None:
                continue

            if lot.end + dt.timedelta(hours=16) <= self.date:
                total_yds += lot.yds

        return self.__yds - total_yds
    
    @property
    def lbs(self) -> float:
        return self.yds / self.item.yld
    
    @property
    def total_yds(self) -> float:
        lots: list[DyeLotView] = self.lots
        return self.__yds - sum(map(lambda l: l.yds, filter(lambda l: not l.start is None, lots)))
    
    @property
    def total_lbs(self) -> float:
        return self.total_yds / self.item.yld
    
    @property
    def late_yds(self) -> list[tuple[float, dt.timedelta]]:
        lots: list[DyeLotView] = self.lots
        lots = sorted(filter(lambda l: not l.start is None, lots), key=lambda l: l.end)
        
        yds_on_time = 0
        total_prod = 0

        raw_table: list[tuple[float, dt.timedelta]] = []
        for lot in lots:
            fin_date = lot.end + dt.timedelta(hours=16)
            total_prod += lot.yds

            if fin_date <= self.date:
                yds_on_time += lot.yds
            else:
                raw_table.append((self.__yds - total_prod, fin_date - self.date))
        
        raw_table.insert(0, (self.__yds - yds_on_time, dt.timedelta(days=0)))
        
        late_table: list[tuple[float, dt.timedelta]] = []
        tdelta = dt.timedelta(days=7)
        for i in range(len(raw_table), 0, -1):
            yds, curdelta = raw_table[i-1]
            late_table.insert(0, (yds, tdelta))
            tdelta = curdelta
        
        return late_table

class ReqView(DataView[str],
              funcs=['bucket','late_yd_buckets','late_lb_buckets','assign_lot','unassign_lot'],
              dunders=['repr'],
              attrs=['item','greige','color','lots']):
    pass

class Req(Data[str], fg_flag=False, dattrs=('item','greige','color','lots'),
          dpriv_attrs=('buckets','lots'), dfrozen=('_Req__buckets','item')):
    
    def __init__(self, item: FabricStyle, p1date: dt.datetime,
                 buckets: tuple[float, float, float, float]):
        priv = {
            'buckets': (Bucket(self, buckets[0], p1date),
                        Bucket(self, sum(buckets[:2]), p1date+dt.timedelta(days=4)),
                        Bucket(self, sum(buckets[:3]), p1date+dt.timedelta(days=7)),
                        Bucket(self, sum(buckets), p1date+dt.timedelta(days=11))),
            'lots': []
        }
        Data.__init__(self, 'REQ ' + item.id, 'Req', ReqView(self), priv=priv,
                      item=item)

    def __repr__(self):
        bucket_rep = ', '.join([f'p{i}={self.bucket(i).yds:.1f}' for i in range(1,5)])
        return f'Req(item={self.item}, ' + bucket_rep + ')'

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
    
    def late_yd_buckets(self) -> list[tuple[float, dt.timedelta]]:
        table = []
        for i in range(1,4):
            table += self.bucket(i).late_yds
        return table
    
    @setter_like
    def assign_lot(self, rolls: list[AllocRoll], pnum: int) -> DyeLot:
        newlot = DyeLot(rolls, self.item, self.view(), pnum)
        self.__lots.append(newlot)
        return newlot
    
    @setter_like
    def unassign_lot(self, lot: DyeLotView) -> None:
        self.__lots.remove(lot)