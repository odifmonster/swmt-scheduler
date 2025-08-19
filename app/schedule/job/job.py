#!/usr/bin/env python

import datetime as dt

from app.support import HasID, SuperImmut
from app.style import color, FabricStyle
from ..dyelot import DyeLot

class Job(HasID[str], SuperImmut,
          attrs=('_prefix','id','shade','item','start','end','cycle_time'),
          priv_attrs=('prefix','id','lots'),
          frozen=('_Job__prefix','_Job__id','_Job__lots','_Job__start','shade','item','cycle_time')):

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