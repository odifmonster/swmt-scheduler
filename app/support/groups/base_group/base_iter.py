#!/usr/bin/env python

from typing import TypeVar, Generic
from collections.abc import Iterator

from ..item import Item

T = TypeVar('T')
U = TypeVar('U')

class BGIter(Generic[T, U], Iterator[U]):

    def __init__(self, data: list[Item[T, U]]):
        Generic.__init__(self, lambda _: BGIter)
        Iterator[U].__init__(self)

        self.__data = sorted(data)
        self.__idx = 0

    def __iter__(self):
        return self
    
    def __next__(self):
        self.__idx += 1
        try:
            return self.__data[self.__idx-1].data
        except AttributeError:
            return self.__next__()
        except IndexError:
            raise StopIteration()