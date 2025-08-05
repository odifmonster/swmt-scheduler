#!/usr/bin/env python

from typing import TypeVar, Generic, Callable, Iterator

T_co = TypeVar('T_co', covariant=True)
U_co = TypeVar('U_co', covariant=True)

class SuperIter(Generic[T_co, U_co]):

    _get_val: Callable[[T_co], U_co] = lambda _: None

    def __init_subclass__(cls, get_val: Callable[[T_co], U_co]):
        super().__init_subclass__()
        cls._get_val = get_val

    def __init__(self, link: Iterator[T_co]):
        self.__link = link

    def __iter__(self):
        for x in self.__link:
            yield type(self)._get_val(x)