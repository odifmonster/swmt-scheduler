#!/usr/bin/env python

import datetime as dt

from app.support import HasID, SuperImmut
from app.style import color
from ..dyelot import DyeLot, DyeLotView

_CTR = 0

class Job(HasID[str], SuperImmut,
          attrs=('_prefix','id','shade','item','start','end','cycle_time','due_date',
                 'lots','lbs','yds'),
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
        return cls(id, item.color.shade, start, cycle_time, lots)

    @classmethod
    def make_placeholder(cls, id: str, start: dt.datetime, end: dt.datetime) -> 'Job':
        return cls(id, color.EMPTY, start, end - start, tuple())
    
    @classmethod
    def make_strip(cls, is_heavy: bool, start: dt.datetime, end: dt.datetime | None = None,
                   id: str | None = None) -> 'Job':
        if end is None or id is None:
            if not (end is None and id is None):
                raise ValueError('Cannot create placeholder strip cycle without id and end.')
            globals()['_CTR'] += 1
            if is_heavy:
                id = f'HEAVYSTRIP_{globals()['_CTR']:05}'
                shade = color.HEAVYSTRIP
                cycle_time = dt.timedelta(hours=14)
            else:
                id = f'STRIP_{globals()['_CTR']:05}'
                shade = color.STRIP
                cycle_time = dt.timedelta(hours=7)
        else:
            shade = color.STRIP
            cycle_time = end - start
        
        return cls(id, shade, start, cycle_time, tuple())

    def __init__(self, id: str, shade: color.ShadeGrade, start: dt.datetime, cycle_time: dt.datetime,
                 lots: tuple[DyeLot, ...]) -> None:
        priv = { 'prefix': 'Job', 'id': id, 'lots': lots, 'start': start }
        SuperImmut.__init__(self, priv=priv, shade=shade, cycle_time=cycle_time)
    
    @property
    def _prefix(self):
        return self.__prefix
    
    @property
    def id(self):
        return self.__id
    
    @property
    def start(self) -> dt.datetime | None:
        return self.__start
    @start.setter
    def start(self, new: dt.datetime | None) -> None:
        self.__start = new
        for lot in self.__lots:
            lot.start = new
            if not new is None:
                lot.end = new + self.cycle_time
    
    @property
    def end(self) -> dt.datetime | None:
        if self.__start is None:
            return None
        return self.__start + self.cycle_time
    
    @property
    def due_date(self) -> dt.datetime:
        return min(self.lots, key=lambda l: l.due_date).due_date

    @property
    def lots(self) -> list[DyeLotView]:
        return [d.view() for d in self.__lots]
    
    @property
    def lbs(self) -> float:
        return sum(map(lambda l: l.lbs, self.lots))
    
    @property
    def yds(self) -> float:
        return sum(map(lambda l: l.yds, self.lots))
    
    def __repr__(self):
        date_fstr = '%m/%d %H:%M'
        shade_name = self.shade.split('_')[1]
        return f'{self._prefix}(shade={shade_name}, start={self.start.strftime(date_fstr)}' + \
            f', end={self.end.strftime(date_fstr)})'