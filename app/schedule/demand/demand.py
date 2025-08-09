#!/usr/bin/env python

from typing import Unpack, Protocol
from abc import abstractmethod
import datetime

from app.support import PrettyArgsOpt, SuperView, Viewable
from app.support.groups import DataLike
from app.style import FabricStyle

_DMND_CTR = 0

class DemandLike(DataLike[int, PrettyArgsOpt], Protocol):

    @property
    def _prefix(self):
        return 'DEMAND'
    
    @property
    @abstractmethod
    def id(self):
        raise NotImplementedError()
    
    @property
    @abstractmethod
    def item(self) -> FabricStyle:
        raise NotImplementedError()
    
    @property
    @abstractmethod
    def yards(self):
        raise NotImplementedError()
    
    @property
    @abstractmethod
    def due_date(self) -> datetime.datetime:
        raise NotImplementedError()
    
    @abstractmethod
    def assign(self, pounds: float):
        raise NotImplementedError()
    
    def pretty(self, **kwargs: Unpack[PrettyArgsOpt]):
        date_str = self.due_date.strftime('%a %d %b %Y')
        return f'{self._prefix}(id={self.id:05}, item={repr(self.item.id)}, due_date={date_str})'
    
class DemandView(SuperView[DemandLike],
                 no_access=['assign'],
                 overrides=[],
                 dunders=['eq','hash']):
    pass

class Demand(DemandLike, Viewable[DemandView]):

    def __init__(self, item: FabricStyle, yards: float, due_date: datetime.datetime):
        globals()['_DMND_CTR'] += 1
        self.__id = globals()['_DMND_CTR']

        self.__item = item
        self.__yards = yards
        self.__due_date = due_date
        self.__view = DemandView(self)
    
    @property
    def id(self):
        return self.__id
    
    @property
    def item(self) -> FabricStyle:
        return self.__item
    
    @property
    def yards(self):
        return self.__yards
    
    @property
    def due_date(self) -> datetime.datetime:
        return self.__due_date

    def assign(self, pounds: float):
        yds = pounds * self.item.yds_per_lb * pounds
        self.__yards -= yds
    
    def view(self):
        return self.__view