#!/usr/bin/env python

from collections.abc import Iterator # pyright: ignore[reportShadowedImports]

from app.support import SuperIter
from app.support.groups import Item
from ..temp import DataView, DPrettyArgsOpt

class MappedIter(Iterator[DataView]):

    def __init__(self, data: list[Item[str, DPrettyArgsOpt]]):
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

class MIDIter(SuperIter[DataView, str],
              get_val=lambda dv: dv.id):
    pass