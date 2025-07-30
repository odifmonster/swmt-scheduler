#!/usr/bin/env python

from abc import ABC, abstractmethod
from collections.abc import Collection, Iterator

from ...roll import Roll
from .item import Item

INIT_SIZE = 512
SKIP_LEN = 7
MAX_SATUR = 0.8

class GroupIter(Iterator[Roll]):

    def __init__(self, data: list[Item]):
        self.__data: list[Item] = sorted(data)
        self.__idx: int = 0

    def __iter__(self) -> Iterator[Roll]:
        return self
    
    def __next__(self) -> Roll:
        self.__idx += 1
        try:
            cur = self.__data[self.__idx-1]
            if cur.is_empty:
                return self.__next__()
            return cur.data
        except IndexError:
            raise StopIteration()

class Group(ABC, Collection[Roll]):

    def __init__(self, init_size: int = INIT_SIZE):
        super().__init__()

        self.__contents: list[Item] = [Item() for _ in range(init_size)]
        self.__size: int = init_size
        self.__length: int = 0
        self.__counter: int = 0
    
    @property
    def _contents(self) -> list[Item]:
        return self.__contents
    
    @property
    def _size(self) -> int:
        return self.__size
    
    @property
    def length(self) -> int:
        return self.__length
    
    @property
    @abstractmethod
    def total_weight(self) -> float:
        non_empty = [i for i in self.__contents if not i.is_empty]
        return sum([i.data.weight for i in non_empty])
    
    def _get_nearest_idx(self, roll: Roll, skip_inserted: bool) -> int:
        idx = hash(roll) % self.__size
        n_skips = 0

        while n_skips < self.__size:
            cur_item = self.__contents[idx]
            if not cur_item.was_inserted or (not skip_inserted and cur_item.is_empty) or \
                (not cur_item.is_empty and cur_item.data == roll):
                return idx
            
            idx = (idx + SKIP_LEN) % self.__size
            n_skips += 1
        
        return -1
    
    def _resize(self, newsize: int) -> None:
        pcontents = self.__contents
        self.__contents = [Item() for _ in range(newsize)]
        self.__size = newsize

        for item in pcontents:
            if item.is_empty: continue

            idx = self._get_nearest_idx(item.data, False)
            if idx < 0:
                raise RuntimeError('FATAL: Attempted to resize group to invalid size.')
            self.__contents[idx] = item
    
    def __len__(self) -> int:
        return self.__length
    
    def __iter__(self) -> Iterator[Roll]:
        return GroupIter(self.__contents)
    
    def __contains__(self, roll: Roll) -> bool:
        idx = self._get_nearest_idx(roll, True)
        return idx >= 0 and not self.__contents[idx].is_empty
    
    @abstractmethod
    def add_roll(self, roll: Roll) -> None:
        if roll in self:
            raise ValueError(f'Attempted to add duplicate {roll}.')
        
        if (self.__length+1) / self.__size >= MAX_SATUR:
            self._resize(self.__size*2)
        
        idx = self._get_nearest_idx(roll, False)
        self.__counter += 1
        self.__contents[idx].store(roll, self.__counter)
        self.__length += 1
    
    @abstractmethod
    def remove_roll(self, roll: Roll) -> Roll:
        if roll not in self:
            raise ValueError(f'Group object does not contain {roll}.')
        
        idx = self._get_nearest_idx(roll, True)
        self.__length -= 1
        return self.__contents[idx].clear()
    
    @abstractmethod
    def get_k_rolls(self, k: int, **kwargs) -> list[Roll]:
        raise NotImplementedError()
    
    def remove_rolls(self, rolls: list[Roll]) -> list[Roll]:
        for r in rolls:
            if r not in self:
                raise ValueError(f'Group object does not contain {r}.')
        
        removed: list[Roll] = []
        for r in rolls:
            removed.append(self.remove_roll(r))