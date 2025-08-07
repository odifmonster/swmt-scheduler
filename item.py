#!/usr/bin/env python

from typing import Literal, Protocol, Unpack

from app.support import Viewable, SuperView, PrettyArgsOpt
from app.support.groups import DataLike

class ItemArgsOpt(PrettyArgsOpt, total=False):
    kind: Literal['object', 'value']

class ItemArgs(ItemArgsOpt, total=True):

    @classmethod
    def create(cls, kind = 'value', maxlen = 60, maxlines = 1):
        return cls(kind=kind, maxlen=maxlen, maxlines=maxlines)
    
class ItemLike(DataLike[str, ItemArgsOpt], Protocol):

    @property
    def _prefix(self) -> str:
        return 'ITEM'

    @property
    def id(self) -> str:
        raise NotImplementedError()
    
    @property
    def master(self) -> str:
        raise NotImplementedError()
    
    @property
    def color(self) -> str:
        raise NotImplementedError()
    
    @property
    def value(self) -> int:
        raise NotImplementedError()
    
    def increment(self) -> None:
        raise NotImplementedError()
    
    def pretty(self, **kwargs: Unpack[ItemArgsOpt]):
        opts = self.validate_args(kwargs)
        opts = ItemArgs.create(**opts)

        if opts['kind'] == 'object':
            return f'<{self._prefix}: id={repr(self.id)}>'
        
        return f'{self._prefix}({self.master}-{self.color}-{self.value:02})'

class ItemView(ItemLike, SuperView[ItemLike],
               no_access=['increment'],
               overrides=['']):
    pass

class Item(ItemLike, Viewable[ItemView]):

    def __init__(self, id: str, master: str, color: str, value: int):
        self.__id = id
        self.__master = master
        self.__color = color
        self.__value = value
        self.__view = ItemView(self)

    @property
    def id(self):
        return self.__id
    
    @property
    def master(self):
        return self.__master
    
    @property
    def color(self):
        return self.__color
    @color.setter
    def color(self, new: str):
        self.__color = new

    @property
    def value(self):
        return self.__value
    
    def increment(self):
        self.__value += 1

    def view(self):
        return self.__view