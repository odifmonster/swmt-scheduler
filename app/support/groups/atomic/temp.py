#!/usr/bin/env python

from typing import Protocol

from app.support import Viewable, SuperView, HasID

class DataLike(HasID[str], Protocol):

    @property
    def _prefix(self): return 'DATA'

    @property
    def id(self) -> str: raise NotImplementedError()

    @property
    def name(self) -> str: raise NotImplementedError()

    @property
    def value(self) -> int: raise NotImplementedError()

class DataView(SuperView[DataLike],
               DataLike,
               gettables=['_prefix', 'id', 'name', 'value',
                          '__eq__', '__hash__']):
    pass

class Data(DataLike, Viewable[DataView]):

    def __init__(self, id: str, name: str, value: int):
        self.__id = id
        self.__name = name
        self.__value = value
        self.__view = DataView(self)

    @property
    def id(self): return self.__id

    @property
    def name(self): return self.__name
    @name.setter
    def name(self, new: str): self.__name = new

    @property
    def value(self): return self.__value
    @value.setter
    def value(self, new: int): self.__value = new

    def view(self): return self.__view