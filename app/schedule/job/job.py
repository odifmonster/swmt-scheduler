#!/usr/bin/env python

import datetime
from app.support import HasID
from ..dyelot import DyeLot
from ..demand import EMPTY_DEMAND

_JOB_CTR = 0

_EMPTY_LOT = (DyeLot(EMPTY_DEMAND),)

class _JobBase(HasID[int]):

    def __init__(self, start: datetime.datetime, cycle_time: datetime.timedelta,
                 lots: tuple[DyeLot, ...] = _EMPTY_LOT):
        globals()['_JOB_CTR'] += 1
        self.__id = globals()['_JOB_CTR']

        self.__start = start
        self.__cycle_time = cycle_time
        self.__lots = lots

    @property
    def _prefix(self):
        return 'JOB'
    
    @property
    def id(self):
        return self.__id
    
    @property
    def start(self):
        return self.__start
    
    @property
    def cycle_time(self):
        return self.__cycle_time
    
    @property
    def end(self):
        return self.__start + self.__cycle_time
    
    @property
    def lbs(self):
        return sum(map(lambda x: x.lbs, self.__lots))
    
    @property
    def yds(self):
        return sum(map(lambda x: x.yds, self.__lots))
    
    def __repr__(self):
        start_str = self.start.strftime('%m/%d/%y %H:%M:%S')
        end_str = self.end.strftime('%m/%d/%y %H:%M:%S')
        return f'{self._prefix}(id={self.id:05}, start={start_str}, end={end_str})'
    
class Job(_JobBase):
    pass