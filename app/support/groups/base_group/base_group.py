#!/usr/bin/env python

from typing import TypeVar, Generic
from abc import ABC, abstractmethod

from app.support import Viewable, HasID
from app.support.groups import Item
from .base_iter import BGIter

S_co = TypeVar('S_co', bound=Viewable[HasID], covariant=True)
T_co = TypeVar('T_co', bound=HasID, covariant=True)
U = TypeVar('U', str, int)

SKIP_LEN = 7
MAX_SATUR = 0.8

class BaseGroup(Generic[S_co, T_co, U], ABC):

    def __init__(self, initsize: int):
        self.__contents: list[Item[S_co, T_co]] = [Item[S_co, T_co]() for _ in range(initsize)]
        self.__size = initsize
        self.__length = 0
        self.__insert_idx = 0

    @property
    def n_items(self): return self.__length

    def _get_nearest_idx(self, item_id: U, skip_inserted: bool):
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

        self.__contents = [Item[S_co, T_co]() for _ in range(newsize)]
        self.__size = newsize

        for item in pcontents:
            if item.is_empty(): continue

            idx = self._get_nearest_idx(item.data.id, False)
            if idx < 0:
                raise RuntimeError(f'FATAL: Resize operation failed (newsize={newsize}).')
            
            self.__contents[idx] = item
    
    def _contains_id(self, item_id: U):
        idx = self._get_nearest_idx(item_id, True)
        return idx >= 0 and self.__contents[idx].was_inserted()
    
    @abstractmethod
    def __len__(self): raise NotImplementedError()

    @abstractmethod
    def __iter__(self): raise NotImplementedError()

    @abstractmethod
    def __contains__(self, key): raise NotImplementedError()
    
    @abstractmethod
    def __getitem__(self, key): raise NotImplementedError()
    
    @abstractmethod
    def add(self, data: S_co):
        if self._contains_id(data.view().id):
            return

        if (self.__length + 1) / self.__size >= MAX_SATUR:
            self._resize(self.__size * 2)

        idx = self._get_nearest_idx(data.view().id, False)
        self.__insert_idx += 1
        self.__length += 1
        self.__contents[idx].insert(data, self.__insert_idx-1)

    @abstractmethod
    def remove(self, item_id: U):
        idx = self._get_nearest_idx(item_id, True)
        if idx < 0 or self.__contents[idx].is_empty():
            raise ValueError(f'Group does not contain object with id \'{item_id}\'.')
        
        self.__length -= 1
        return self.__contents[idx].remove()
    
    def get_by_id(self, item_id: U):
        idx = self._get_nearest_idx(item_id, True)
        if idx < 0 or self.__contents[idx].is_empty():
            raise ValueError(f'Group does not contain object with id \'{item_id}\'.')
        
        return self.__contents[idx].data
    
    def iter_items(self):
        return BGIter[S_co, T_co](self.__contents)