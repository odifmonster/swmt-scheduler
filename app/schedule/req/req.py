#!/usr/bin/env python

from typing import Callable
import datetime as dt

from app.support import setter_like
from app.groups import DataView, Data
from app.style import FabricStyle, Color

class ReqView(DataView[str], funcs=['fulfill'],
              attrs=['item','color','shade','yds','lbs','due_date'],
              dunders=['repr']):
    pass

class Req(Data[str], dattrs=('item','color','shade','yds','lbs','due_date'),
                  dpriv_attrs=('yds','observer'),
                  dfrozen=('item','due_date','_Req__observer')):
    
    def __init__(self, item: FabricStyle, yds: float, due_date: dt.datetime,
                 subscriber: 'Req | None' = None):
        str_id = item.id + ' ' + due_date.strftime('%m %d')
        observer: Callable[[float], None] = lambda f: None
        if not subscriber is None:
            observer = lambda f: subscriber.fulfill(f)

        super().__init__(str_id, 'Req', ReqView(self),
                         priv={'yds': yds, 'observer': observer},
                         item=item, due_date=due_date)
        
    @property
    def color(self) -> Color:
        return self.item.color
    
    @property
    def shade(self):
        return self.color.shade
    
    @property
    def yds(self) -> float:
        return self.__yds
    
    @property
    def lbs(self):
        return self.__yds / self.item.yld
    
    def __repr__(self):
        return f'{self._prefix}(id={self.id}, yds={self.yds:.2f})'
    
    @setter_like
    def fulfill(self, lbs: float) -> None:
        used_yds = lbs * self.item.yld
        ret = 0
        if self.yds > 0 and self.yds - used_yds < 0:
            ret = abs(self.yds - used_yds)
        elif self.yds < 0:
            ret = used_yds

        self.__yds -= used_yds
        self.__observer(ret)