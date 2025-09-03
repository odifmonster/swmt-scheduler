#!/usr/bin/env python

from typing import Protocol
import datetime as dt

from app.support import setter_like
from app.support.grouped import Data, DataView
from app.style import FabricStyle
from app.materials import PortLoad
from ...dyelot import DyeLot, DyeLotView

class _Req(Protocol):
    item: FabricStyle
    @property
    def lots(self) -> list[DyeLotView]: ...
    @property
    def total_yds_prod(self) -> float: ...
    def total_yds_by(date: dt.datetime) -> float: ...
    def assign(rolls: list[PortLoad]) -> DyeLot: ...
    def unassign(lview: DyeLotView) -> DyeLot: ...

class Order(Data[str], mod_in_group=True,
            attrs=('item','greige','color','yds','init_yds','cum_yds','total_yds',
                   'lbs','init_lbs','cum_lbs','total_lbs','pnum','due_date'),
            priv_attrs=('req','init_cur_yds','init_cum_yds'),
            frozen=('*req','*init_cur_yds','*init_cum_yds','item','pnum','due_date')):
    
    def __init__(self, req: _Req, item, pnum, due_date, cur_yds, cum_yds):
        Data.__init__(self, f'P{pnum}@{item.id}', 'Order', OrderView(self),
                      priv={'req': req, 'init_cur_yds': cur_yds,
                            'init_cum_yds': cum_yds}, item=item,
                      pnum=pnum, due_date=due_date)
    
    @property
    def greige(self):
        return self.item.greige
    
    @property
    def color(self):
        return self.item.color

    @property
    def yds(self):
        return max(0, min(self.__init_cur_yds, self.cum_yds))
    
    @property
    def init_yds(self):
        return self.__init_cur_yds

    @property
    def cum_yds(self):
        r: _Req = self.__req
        return self.__init_cum_yds - r.total_yds_by(self.due_date)
    
    @property
    def total_yds(self):
        r: _Req = self.__req
        return self.__init_cum_yds - r.total_yds_prod
    
    @property
    def lbs(self):
        return self.yds / self.item.yld
    
    @property
    def init_lbs(self):
        return self.init_yds / self.item.yld
    
    @property
    def cum_lbs(self):
        return self.cum_yds / self.item.yld
    
    @property
    def total_lbs(self):
        return self.total_yds / self.item.yld
    
    def late_table(self, next_avail: dt.datetime):
        if self.yds <= 0:
            return []
        
        r: _Req = self.__req
        max_late_time = next_avail - self.due_date
        lots: list[DyeLotView] = sorted(filter(lambda l: not l.end is None, r.lots),
                                        key=lambda l: l.end)
        if not lots:
            return [(self.yds, max_late_time)]
        
        last_late = self.__init_cum_yds
        idx = 0
        for i in range(len(lots), 0, -1):
            total_prod = r.total_yds_by(lots[i-1].end)
            if self.__init_cum_yds - total_prod > 0:
                last_late = min(self.__init_cum_yds - total_prod, self.init_yds)
                idx = i
                break
        
        table = []
        if idx == len(lots):
            table.append((last_late, max_late_time))
        else:
            table.append((last_late, lots[idx].end - self.due_date))

        for i in range(idx, 0, -1):
            if lots[i-1].end <= self.due_date:
                break
            table.append((lots[i-1].yds, lots[i-1].end - self.due_date))
        
        return table
    
    @setter_like
    def assign(self, ports):
        return self.__req.assign(ports)
    
    @setter_like
    def unassign(self, lview):
        return self.__req.unassign(lview)

class OrderView(DataView[str],
                attrs=('item','greige','color','yds','init_yds','cum_yds','total_yds',
                       'lbs','init_lbs','cum_lbs','total_lbs','pnum','due_date'),
                funcs=('late_table','assign','unassign'),
                dunders=('repr',)):
    pass