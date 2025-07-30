#!/usr/bin/env python

from typing import Self

from ...roll import Roll

class _ItemBase:

    def __init__(self):
        self.__data: Roll | None = None
        self.__insert_idx: int = -1

    @property
    def data(self) -> Roll:
        if self.__data is None:
            raise RuntimeError('Cannot access data from empty Item.')
        return self.__data
    
    @property
    def is_empty(self) -> bool:
        return self.__data is None
    
    @property
    def was_inserted(self) -> bool:
        return self.__insert_idx >= 0
    
    def __eq__(self, other: Self) -> bool:
        return self.__insert_idx == other.__insert_idx
    
    def __lt__(self, other: Self) -> bool:
        return self.__insert_idx < other.__insert_idx
    
    def store(self, roll: Roll, insert_idx: int) -> None:
        self.__data = roll
        self.__insert_idx = insert_idx

    def clear(self) -> Roll:
        if self.__data is None:
            raise ValueError('Cannot clear empty Item.')
        temp = self.__data
        self.__data = None
        return temp
    
class Item(_ItemBase):
    pass