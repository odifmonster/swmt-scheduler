#!/usr/bin/env python

import datetime as dt

from app.support import HasID, SuperImmut, SuperView
from app.style import fabric

_CTR = 0

class DyeLot(HasID[str], SuperImmut,
             attrs=('_prefix','id','ports','item','greige','shade','cycle_time',
                    'start','end','yds','lbs','min_date'),
             priv_attrs=('id','start','fin_time','view'),
             frozen=('*id','*fin_time','*view','ports','item','cycle_time','min_date')):
    
    @classmethod
    def from_adaptive(cls, id, item, start, end):
        return cls(id, tuple(), item, start, end - start, dt.timedelta(hours=0),
                   start)
    
    @classmethod
    def new_strip(cls, item: fabric.FabricStyle, start):
        if item.id not in ('STRIP', 'HEAVYSTRIP'):
            raise ValueError(f'Cannot create new strip cycle with item {repr(item)}')
        
        globals()['_CTR'] += 1
        new_id = f'{item.id}{globals()['_CTR']:05}'
        return cls(new_id, tuple(), item, start, item.cycle_time, dt.timedelta(hours=0),
                   start)
    
    @classmethod
    def new_lot(cls, item: fabric.FabricStyle, ports):
        globals()['_CTR'] += 1
        new_id = f'LOT{globals()['_CTR']:05}'
        min_date = max(map(lambda pl: pl.avail_date, ports))
        return cls(new_id, tuple(ports), item, None, item.cycle_time, dt.timedelta(hours=16),
                   min_date)

    def __init__(self, id, ports, item, start, cycle_time, fin_time, min_date):
        SuperImmut.__init__(self, priv={'id': id, 'start': start, 'fin_time': fin_time,
                                        'view': DyeLotView(self)},
                            ports=ports, item=item, cycle_time=cycle_time,
                            min_date=min_date)
        
    def __repr__(self):
        start = 'N/A' if self.start is None else self.start.strftime('%m/%d %H:%M')
        end = 'N/A' if self.end is None else self.end.strftime('%m/%d %H:%M')
        return f'{self._prefix}(id={repr(self.id)}, item={repr(self.item)}, start={start}, end={end})'
    
    @property
    def _prefix(self):
        return 'DyeLot'
    
    @property
    def id(self):
        return self.__id
    
    @property
    def greige(self):
        return self.item.greige
    
    @property
    def color(self):
        return self.item.color
    
    @property
    def shade(self):
        return self.item.color.shade
    
    @property
    def start(self):
        return self.__start
    @start.setter
    def start(self, new):
        if not (new is None or self.__start is None):
            raise RuntimeError('A DyeLot cannot be linked to more than one active Job at a time')
        self.__start = new
    
    @property
    def end(self):
        if self.__start is None:
            return self.__start
        return self.__start + self.cycle_time + self.__fin_time
    
    @property
    def yds(self):
        return self.lbs * self.item.yld
    
    @property
    def lbs(self):
        return sum(map(lambda p: p.lbs, self.ports))
    
    def view(self):
        return self.__view
    
class DyeLotView(SuperView[DyeLot],
                 attrs=('_prefix','id','ports','item','greige','shade','cycle_time',
                        'start','end','yds','lbs','min_date'),
                 dunders=('eq','hash','repr')):
    pass