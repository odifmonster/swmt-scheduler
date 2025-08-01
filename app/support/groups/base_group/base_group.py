#!/usr/bin/env python

from typing import TypeVar, Generic, Hashable
from abc import ABC, abstractmethod

from app.support import HasID, HasIDLike
from app.support.groups import Item
from .base_iter import BGIter

S = TypeVar('S', bound=HasIDLike)
T = TypeVar('T', bound=HasID)
U = TypeVar('U', bound=Hashable)

SKIP_LEN = 7
MAX_SATUR = 0.8

class BaseGroup(Generic[S, T, U], ABC):

    def __init__(self, init_size: int):
        Generic.__init__(self, lambda _: BaseGroup)
        ABC.__init__(self)

        self.__contents: list[Item[T, S]] = [Item[T, S]() for _ in range(init_size)]
        self.__size: int = init_size
        self.__length: int = 0
        self.__insert_idx: int = 0
    
    @property
    def n_items(self):
        return self.__length
    
    def _get_nearest_idx(self, item_id: U, skip_inserted: bool):
        idx = hash(item_id) % self.__size
        n_skips = 0

        while n_skips < self.__size:
            cur_item = self.__contents[idx]

            if not cur_item.was_inserted or (not skip_inserted and cur_item.is_empty) \
                or (not cur_item.is_empty and cur_item.data.id == item_id):
                return idx
            
            idx = (idx + SKIP_LEN) % self.__size
            n_skips += 1
        
        return -1
    
    def _resize(self, newsize: int):
        pcontents = self.__contents
        self.__contents = [Item[T, T]() for _ in range(newsize)]
        self.__size = newsize

        for x in pcontents:
            if x.is_empty: continue

            idx = self._get_nearest_idx(x.data.id, False)
            if idx < 0:
                raise RuntimeError('FATAL: Resizing failed.')
            self.__contents[idx] = x
    
    def contains_id(self, item_id: U):
        idx = self._get_nearest_idx(item_id, True)
        return idx >= 0 and not self.__contents[idx].is_empty

    @abstractmethod
    def add(self, value: T):
        if self.contains_id(value.id): return

        if (self.__length + 1) / self.__size >= MAX_SATUR:
            self._resize(self.__size*2)
        
        idx = self._get_nearest_idx(value.id, False)
        self.__insert_idx += 1
        self.__length += 1
        self.__contents[idx].store(value, self.__insert_idx)
    
    @abstractmethod
    def remove(self, item_id: U) -> T:
        if not self.contains_id(item_id):
            raise ValueError(f'Group does not contain value (id={str(item_id)}).')
        idx = self._get_nearest_idx(item_id, True)
        self.__length -= 1
        return self.__contents[idx].empty()
    
    def get_by_id(self, item_id: U) -> S:
        if not self.contains_id(item_id):
            raise ValueError(f'Group does not contain value (id={str(item_id)}).')
        idx = self._get_nearest_idx(item_id, True)
        return self.__contents[idx].data

    def iter_items(self):
        return BGIter[T, S](self.__contents)