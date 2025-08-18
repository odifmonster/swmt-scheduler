#!/usr/bin/env python

import datetime as dt

from app.support import HasID, SuperImmut
from app.style import color, Color
from ..dyelot import DyeLot

_CTR = 0

class Job(HasID[str], SuperImmut, attrs=('_prefix','id','color','cycle_time',
                                         'start','end'),
          priv_attrs=('prefix','id','start','lots'),
          frozen=('_Job__prefix','_Job__id','_Job__lots','_Job__color',
                  '_Job__cycle_time')):

    def __init__(self, start: dt.datetime, max_date: dt.datetime,
                 id: str | None = None,
                 lots: tuple[DyeLot, ...] | None = tuple(),
                 cycle_time: dt.timedelta | None = None):
        if lots is None:
            if cycle_time is None:
                cycle_time = dt.timedelta(hours=8)
                globals()['_CTR'] += 1
                id = f'STRIP_{globals()['_CTR']:05}'
            elif id is None:
                raise ValueError('Explicit strip cycle must provide an id.')
            
            clr = Color('STRIP', 0, 'STRIP')
        elif len(lots) == 0:
            if cycle_time is None or id is None:
                raise ValueError('Placeholder jobs must provide a cycle time and id.')
            clr = Color('EMPTY', 1, 'EMPTY')
        else:
            clr = lots[0].color
            globals()['_CTR'] += 1
            id = f'NORMAL_{globals()['_CTR']:05}'
            if clr.shade == color.BLACK:
                cycle_time = dt.timedelta(hours=10)
            elif clr.shade == color.SOLUTION:
                cycle_time = dt.timedelta(hours=6)
            else:
                cycle_time = dt.timedelta(hours=8)

        super().__init__(priv={'prefix': 'Job', 'id': id, 'start': start, 'lots': lots}, color=clr,
                         cycle_time=cycle_time, max_date=max_date)
    
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
        if self.__lots is None:
            return tuple()
        return self.__lots