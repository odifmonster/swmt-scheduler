#!/usr/bin/env python

import datetime as dt

from app.support import HasID, SuperImmut
from app.style import color, FabricStyle
from ..dyelot import DyeLot, DyeLotView

_CTR = 0

class Job(HasID[str], SuperImmut,
          attrs=('_prefix','id','shade','item','start','end','cycle_time','lots',
                 'lbs','yds'),
          priv_attrs=('prefix','id','start','lots'),
          frozen=('_Job__prefix','_Job__id','_Job__lots','shade','item','cycle_time')):
    
    @classmethod
    def make_job(cls, start: dt.datetime, lots: tuple[DyeLot, ...]) -> 'Job':
        globals()['_CTR'] += 1
        id = f'NORMAL_{globals()['_CTR']:05}'
        item = lots[0].item
        if item.color.shade == color.BLACK:
            cycle_time = dt.timedelta(hours=10)
        elif item.color.shade == color.SOLUTION:
            cycle_time = dt.timedelta(hours=6)
        else:
            cycle_time = dt.timedelta(hours=8)

        for lot in lots:
            lot.start = start
            lot.end = start + cycle_time
        return cls(id, item.color.shade, item, start, cycle_time, lots)

    def __init__(self, id: str, shade: color.ShadeGrade, item: FabricStyle,
                 start: dt.datetime, cycle_time: dt.datetime,
                 lots: tuple[DyeLot, ...]) -> None:
        priv = { 'prefix': 'Job', 'id': id, 'lots': lots, 'start': start }
        SuperImmut.__init__(self, priv=priv, shade=shade, item=item, cycle_time=cycle_time)
    
    @property
    def _prefix(self):
        return self.__prefix
    
    @property
    def id(self):
        return self.__id
    
    @property
    def start(self) -> dt.datetime:
        return self.__start
    @start.setter
    def start(self, new: dt.datetime) -> None:
        self.__start = new
        for lot in self.__lots:
            lot.start = new
            lot.end = new + self.cycle_time
    
    @property
    def end(self) -> dt.datetime:
        return self.__start + self.cycle_time

    @property
    def lots(self) -> list[DyeLotView]:
        return [d.view() for d in self.__lots]
    
    @property
    def lbs(self) -> float:
        return sum(map(lambda l: l.lbs, self.lots))
    
    @property
    def yds(self) -> float:
        return sum(map(lambda l: l.yds, self.lots))