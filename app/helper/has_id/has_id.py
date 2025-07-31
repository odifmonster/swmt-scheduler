#!/usr/bin/env python

from typing import TypeVar, Generic, Self

from collections.abc import Hashable

T = TypeVar('T', bound=Hashable)

class HasID(Generic[T], Hashable):

    def __init__(self, id: T, prefix: str):
        Generic.__init__(self, lambda _: HasID)
        Hashable.__init__(self)

        self.__id = id
        self.__prefix = prefix
    
    @property
    def id(self) -> T:
        return self.__id
    
    def __eq__(self, value: Self) -> bool:
        return self.__id == value.__id and self.__prefix == value.__prefix
    
    def __hash__(self) -> int:
        return self.__id.__hash__()