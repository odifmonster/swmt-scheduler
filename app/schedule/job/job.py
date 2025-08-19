#!/usr/bin/env python

import datetime as dt

from app.support import HasID, SuperImmut
from app.style import color, Color
from ..dyelot import DyeLot

_CTR = 0

class Job(HasID[str], SuperImmut, attrs=('_prefix','id','color','cycle_time',
                                         'start','end','max_date'),
          priv_attrs=('prefix','id','start','lots'),
          frozen=('_Job__prefix','_Job__id','_Job__lots','color','cycle_time')):
    
    @classmethod
    def make_strip(cls, start: dt.datetime, id: str | None = None,
                   end_time: dt.datetime | None = None) -> 'Job':
        if id is None or end_time is None:
            if not (id is None and end_time is None):
                raise ValueError('Explicit strip cycle must provide an id and an end time.')
            globals()['_CTR'] += 1
            id = f'STRIP_{globals()['_CTR']:05}'
            cycle_time = dt.timedelta(hours=7)
            end_time = start + cycle_time
        else:
            cycle_time = end_time - start

        return cls(start, end_time, id, tuple(), Color('STRIP', 0, 'STRIP'), cycle_time)
    
    @classmethod
    def make_empty_job(cls, start: dt.datetime, id: str, end_time: dt.datetime) -> 'Job':
        return cls(start, end_time, id, tuple(), Color('EMPTY', 1, 'EMPTY'), end_time - start)
    
    @classmethod
    def make_job(cls, start: dt.datetime, max_date: dt.datetime, lots: tuple[DyeLot, ...]) -> 'Job':
        clr = lots[0].color
        if clr.shade == color.BLACK:
            cycle_time = dt.timedelta(hours=10)
        elif clr.shade == color.SOLUTION:
            cycle_time = dt.timedelta(hours=6)
        else:
            cycle_time = dt.timedelta(hours=8)
        globals()['_CTR'] += 1
        id = f'NORMAL_{globals()['_CTR']:05}'
        return cls(start, max_date, id, lots, clr, cycle_time)

    def __init__(self, start: dt.datetime, max_date: dt.datetime, id: str,
                 lots: tuple[DyeLot, ...], clr: Color, cycle_time: dt.timedelta):
        SuperImmut.__init__(self, priv={'prefix': 'Job', 'id': id, 'start': start, 'lots': lots},
                            color=clr, cycle_time=cycle_time, max_date=max_date)
    
    @property
    def _prefix(self):
        return self.__prefix
    
    @property
    def id(self):
        return self.__id
    
    @property
    def start(self):
        return self.__start
    @start.setter
    def start(self, new: dt.datetime):
        self.__start = new
    
    @property
    def end(self):
        return self.__start + self.cycle_time
    
    @property
    def lots(self):
        return self.__lots