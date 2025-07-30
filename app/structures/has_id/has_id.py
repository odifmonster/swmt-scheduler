#!/usr/bin/env python

from typing import TypeVar, Generic, Self

from collections.abc import Hashable

T = TypeVar('T', bound=Hashable)

class _HasIDBase(Generic[T], Hashable):

    def __init__(self, id: T, prefix: str):
        Hashable.__init__(self)

        self.__id = id
        self.__prefix = prefix

    @property
    def _id(self) -> T:
        return self.__id
    
    def __eq__(self, other: Self) -> bool:
        return self.__id == other.__id and self.__prefix == other.__prefix
    
    def __hash__(self) -> int:
        return self.__id.__hash__()

class HasID(_HasIDBase, Generic[T]):
    pass