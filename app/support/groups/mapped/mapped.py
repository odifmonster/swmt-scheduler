#!/usr/bin/env python

from app.support import Viewable
from app.support.groups import Item
from .mapped_like import MappedLike, MappedView
from ..temp import Data, DPrettyArgsOpt

SKIP_LEN = 7
MAX_SATUR = 0.8

class Mapped(MappedLike, Viewable[MappedView]):

    def __init__(self, initize: int):
        self.__contents = [Item[str, DPrettyArgsOpt]() for _ in range(initize)]
        self.__size = initize
        self.__length = 0
        self.__insert_idx = 0

        self.__view = MappedView(self)

    @property
    def n_items(self): return self.__length

    def _get_nearest_idx(self, id: str, skip_inserted: bool):
        idx = hash(id) % self.__size
        n_skips = 0

        while n_skips < self.__size:
            cur = self.__contents[idx]

            if not cur.inserted() or (not skip_inserted and cur.is_empty()) \
                or (not cur.is_empty() and cur.data.id == id):
                return idx
            
            idx = (idx + SKIP_LEN) % self.__size
            n_skips += 1
        
        return -1
    
    def _resize(self, newsize: int):
        pcontents = self.__contents

        self.__contents = [Item[str, DPrettyArgsOpt]() for _ in range(newsize)]
        self.__size = newsize

        for x in pcontents:
            if x.is_empty(): continue

            idx = self._get_nearest_idx(x.data.id, False)
            if idx < 0:
                raise ValueError(f'Cannot resize to size {newsize}.')
            
            self.__contents[idx] = x
    
    def _get_by_id(self, id: str):
        idx = self._get_nearest_idx(id, True)
        if idx >= 0:
            return self.__contents[idx]
        return None
    
    def add(self, data: Data):
        item = self._get_by_id(data.id)
        if not item is None and not item.is_empty():
            return
        
        if (self.__length + 1) / self.__size >= MAX_SATUR:
            self._resize(self.__size * 2)

        idx = self._get_nearest_idx(data.id, False)
        self.__insert_idx += 1
        self.__length += 1
        self.__contents[idx].store(data, self.__insert_idx-1)
    
    def remove(self, id: str):
        item = self._get_by_id(id)
        if item is None or item.is_empty():
            raise ValueError(f'Object does not contain data with id {repr(id)}.')
        
        self.__length -= 1
        return item.clear()
    
    def view(self): return self.__view