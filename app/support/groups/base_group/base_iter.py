#!/usr/bin/env python

from collections.abc import Iterator

from app.support.groups import Item
from .temp import Data, DataView

class BGIter(Iterator[DataView]):

    def __init__(self, data: list[Item[Data, DataView]]):
        self.__data = sorted(data)
        self.__idx = 0

    def __iter__(self): return self

    def __next__(self):
        self.__idx += 1
        try:
            return self.__data[self.__idx-1].data
        except AttributeError:
            return self.__next__()
        except IndexError:
            raise StopIteration()