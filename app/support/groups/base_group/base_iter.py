#!/usr/bin/env python

from typing import TypeVar, Generic
from collections.abc import Iterator

from app.support.groups import Item

S = TypeVar('S')
T = TypeVar('T')

class BGIter(Generic[T, S], Iterator[T]):

    def __init__(self, contents: list[Item[T, S]]):
        self.__data: list[Item[T, S]] = sorted(contents)
        self.__idx: int = 0

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