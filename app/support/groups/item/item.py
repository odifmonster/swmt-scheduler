#!/usr/bin/env python

from typing import TypeVar, Generic

from app.support import Viewable

T = TypeVar('T')

class Item(Generic[T]):

    def __init__(self):
        Generic.__init__(self, lambda _: Item)

        self.__data: Viewable[T] | None = None
        self.__idx: int = -1

    @property
    def was_inserted(self):
        return self.__idx >= 0
    
    @property
    def is_empty(self):
        return self.__data is None
    
    @property
    def data(self) -> T:
        if self.__data is None:
            raise AttributeError('Cannot access data from empty item.',
                                 name='data',
                                 obj=self)
        return self.__data.view()
    
    def __eq__(self, value):
        return self.__idx == value.__idx
    
    def __lt__(self, value):
        return self.__idx < value.__idx
    
    def store(self, val: Viewable[T], idx: int):
        if idx < 0 or idx <= self.__idx:
            raise ValueError('FATAL: Invalid insertion index.')
        if not self.__data is None:
            raise ValueError('FATAL: Cannot store data in non-empty Item.')
        
        self.__data = val
        self.__idx = idx
    
    def empty(self):
        if self.__data is None:
            raise ValueError('FATAL: Cannot empty Item that is already empty.')
        
        temp = self.__data
        self.__data = None
        return temp