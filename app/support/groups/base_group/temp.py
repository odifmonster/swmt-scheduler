#!/usr/bin/env python

from typing import Protocol
from abc import abstractmethod
from app.support import HasID, Viewable

class DataLike(HasID[str], Protocol):

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError()
    
    @property
    @abstractmethod
    def value(self) -> int:
        raise NotImplementedError()
    
class DataView(DataLike):

    def __init__(self, link: DataLike):
        self.__link = link

    @property
    def _prefix(self) -> str: return self.__link._prefix
    
    @property
    def id(self) -> str: return self.__link.id
    
    @property
    def name(self) -> str: return self.__link.name
    
    @property
    def value(self) -> int: return self.__link.value

class Data(DataLike, Viewable[DataView]):

    def __init__(self, id: str, name: str, value: int):
        self.__id = id
        self.__name = name
        self.__value = value

    @property
    def _prefix(self) -> str: return 'DATA'

    @property
    def id(self) -> str: return self.__id

    @property
    def name(self) -> str: return self.__name
    @name.setter
    def name(self, value: str) -> None: self.__name = value

    @property
    def value(self) -> int: return self.__value
    @value.setter
    def value(self, new: int) -> None: self.__value = new

    def view(self) -> DataView: return DataView(self)