#!/usr/bin/env python

from typing import TypeVar, Generic

from app.helper import Viewable

T = TypeVar('T', bound=Viewable)
U = TypeVar('U')

class Item(Generic[T, U]):

    def __init__(self):
        Generic.__init__(self, lambda _: Item)

        self.__data: T | None = None
        self.__idx: int = -1

    @property
    def was_inserted(self) -> bool:
        return self.__idx >= 0
    
    @property
    def is_empty(self) -> bool:
        return self.__data is None
    
    @property
    def data(self) -> U:
        if self.__data is None:
            raise AttributeError('Attempted to access data from empty item.',
                                 name='data',
                                 obj=self)
        return self.__data.view()
    
    def store(self, val: T, idx: int) -> None:
        if idx < 0 or idx < self.__idx:
            raise ValueError(f'FATAL: Invalid insertion index ({idx}).')
        if not self.__data is None:
            raise ValueError(f'FATAL: Cannnot store new values in non-empty items.')
        self.__data = val
        self.__idx = idx

    def clear(self) -> T:
        if self.__data is None:
            raise ValueError(f'FATAL: Cannot clear empty items.')
        temp = self.__data
        self.__data = None
        return temp