#!/usr/bin/env python

from app.support.groups import Item
from .base_iter import BGIter
from .temp import Data, DataView

SKIP_LEN = 7
MAX_SATUR = 0.8

class BaseGroup:

    def __init__(self, initsize: int):
        self.__contents: list[Item[Data, DataView]] = [Item[Data, DataView]() for _ in range(initsize)]
        self.__size = initsize
        self.__length = 0
        self.__insert_idx = 0

    @property
    def length(self): return self.__length

    def _get_nearest_idx(self, item_id: str, skip_inserted: bool):
        idx = hash(item_id) % self.__size
        n_skips = 0

        while n_skips < self.__size:
            cur = self.__contents[idx]

            if not cur.was_inserted() or (not skip_inserted and cur.is_empty()) \
                or (not cur.is_empty() and cur.data.id == item_id):
                return idx
            
            idx = (idx + SKIP_LEN) % self.__size
            n_skips += 1
        
        return -1
    
    def _resize(self, newsize: int):
        pcontents = self.__contents

        self.__contents = [Item[Data, DataView]() for _ in range(newsize)]
        self.__size = newsize

        for item in pcontents:
            if item.is_empty(): continue

            idx = self._get_nearest_idx(item.data.id, False)
            if idx < 0:
                raise RuntimeError(f'FATAL: Resize operation failed (newsize={newsize}).')
            
            self.__contents[idx] = item
    
    def _contains_id(self, item_id: str):
        idx = self._get_nearest_idx(item_id, True)
        return idx >= 0 and self.__contents[idx].was_inserted()
    
    def get_by_id(self, item_id: str):
        idx = self._get_nearest_idx(item_id, True)
        if idx < 0 or self.__contents[idx].is_empty():
            raise ValueError(f'Group does not contain object with id \'{item_id}\'.')
        
        return self.__contents[idx].data
    
    def add(self, data: Data):
        if self._contains_id(data.id):
            return

        if (self.length + 1) / self.__size >= MAX_SATUR:
            self._resize(self.__size * 2)

        idx = self._get_nearest_idx(data.id, False)
        self.__insert_idx += 1
        self.__length += 1
        self.__contents[idx].insert(data, self.__insert_idx-1)

    def remove(self, item_id: str):
        idx = self._get_nearest_idx(item_id, True)
        if idx < 0 or self.__contents[idx].is_empty():
            raise ValueError(f'Group does not contain object with id \'{item_id}\'.')
        
        self.__length -= 1
        return self.__contents[idx].remove()
    
    def iter_items(self):
        return BGIter(self.__contents)