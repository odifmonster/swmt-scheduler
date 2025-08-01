#!/usr/bin/env python

from typing import TypeVar, Generic, Hashable

T = TypeVar('T', bound=Hashable)

class HasID(Generic[T]):

    def __init__(self, id: T, prefix: str):
        Generic.__init__(self, lambda _: HasID)

        self.__id = id
        self.__prefix = prefix

    @property
    def id(self):
        return self.__id
    
    def __eq__(self, value):
        return self.__id == value.__id and self.__prefix == value.__prefix
    
    def __hash__(self):
        return self.__id.__hash__()
    
    def view(self):
        return self

HasIDLike = HasID