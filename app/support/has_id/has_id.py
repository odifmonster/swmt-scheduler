#!/usr/bin/env python

from typing import TypeVar, Self, Generic
from collections.abc import Hashable

T = TypeVar('T', str, int)

class HasID(Generic[T], Hashable):

    def __init__(self, id: T, prefix: str):
        Hashable.__init__(self)

        self.__id = id
        self.__prefix = prefix
    
    @property
    def id(self):
        return self.__id
    
    def __eq__(self, value: Self):
        return self.__id == value.__id and self.__prefix == value.__prefix
    
    def __hash__(self):
        return self.__id.__hash__()