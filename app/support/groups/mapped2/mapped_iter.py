#!/usr/bin/env python

from typing import TypeVar, Generic
from collections.abc import Iterator # pyright: ignore[reportShadowedImports]

from app.support import SuperIter, SupportsPrettyID, PrettyArgsOpt
from app.support.groups import Item

T = TypeVar('T', str, int)
U_co = TypeVar('U_co', bound=PrettyArgsOpt, covariant=True)

DataView = SupportsPrettyID[T, U_co]

class MappedIter(Generic[T, U_co],
                 Iterator[DataView[T, U_co]]):

    def __init__(self, data: list[Item[T, U_co]]):
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

class MIDIter(Generic[T, U_co],
              SuperIter[DataView[T, U_co], T],
              get_val=lambda dv: dv.id):
    pass