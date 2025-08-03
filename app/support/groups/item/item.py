#!/usr/bin/env python

from typing import TypeVar, Generic, Self

from app.support import Viewable

T = TypeVar('T', bound=Viewable)
U = TypeVar('U')

class Item(Generic[T, U]):

    def __init__(self):
        self.__data: T | None = None
        self.__idx = -1

    @property
    def data(self) -> U:
        if self.__data is None:
            raise AttributeError('Cannot access data from empty Item.',
                                 name='data', obj=self)
        return self.__data.view()
    
    def __eq__(self, value: Self):
        return self.__idx == value.__idx
    
    def __lt__(self, value: Self):
        return self.__idx < value.__idx
    
    def was_inserted(self):
        return self.__idx >= 0
    
    def is_empty(self):
        return self.__data is None
    
    def insert(self, data: T, idx):
        if idx <= self.__idx:
            raise ValueError(f'Invalid insertion index: {idx}.')
        if not self.is_empty():
            raise RuntimeError('Cannot insert data into non-empty Item.')
        
        self.__data = data
        self.__idx = idx

    def remove(self) -> T:
        if self.__data is None:
            raise RuntimeError('Cannot remove data from an empty Item.')
        
        temp = self.__data
        self.__data = None
        return temp