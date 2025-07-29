#!/usr/bin/env python

from typing import TypeVar, Generic, Iterable

from collections.abc import Iterator

T = TypeVar('T')

class _Iter2DBase(Generic[T], Iterator):

    def __init__(self, data: Iterable[Iterable[T]]):
        self.__data: Iterable[Iterable[T]] = data
        self.__iters: list[Iterator[T]] = [x.__iter__() for x in data]
        self.__cur_iter: Iterator[T] = self.__iters[0]
        self.__idx: int = 0

    def __iter__(self) -> Iterator[T]:
        return self
    
    def __next__(self) -> T:
        try:
            return self.__cur_iter.__next__()
        except StopIteration:
            self.__idx += 1
        
        try:
            self.__cur_iter = self.__iters[self.__idx]
            return self.__cur_iter.__next__()
        except IndexError:
            self.__idx = 0
            self.__iters = [x.__iter__() for x in self.__data]
            self.__cur_iter = self.__iters[0]
            raise StopIteration()
        
class Iter2D(_Iter2DBase):
    pass