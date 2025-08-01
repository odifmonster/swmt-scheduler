#!/usr/bin/env python

from typing import TypeVar, Generic, Self

from app.support import Viewable

T = TypeVar('T', bound=Viewable)
U = TypeVar('U')

class Item(Generic[T, U]):

    def __init__(self):
        Generic.__init__(self, lambda _: Item)
        
        self.__data: T | None = None
        self.__idx = 0

    @property
    def was_inserted(self):
        return self.__idx >= 0
    
    @property
    def is_empty(self):
        return self.__data is None
    
    @property
    def data(self) -> U:
        if self.__data is None:
            raise AttributeError('This Item has no data', name='data', obj=self)
        return self.__data.view()
    
    def __eq__(self, value: Self):
        return self.__idx == value.__idx
    
    def __lt__(self, value: Self):
        return self.__idx < value.__idx
    
    def store(self, value: T, idx):
        if idx < 0 or idx <= self.__idx:
            raise ValueError(f'FATAL: Bad insertion index ({idx})')
        if not self.__data is None:
            raise ValueError('FATAL: This Item is not empty.')
        
        self.__data = value
        self.__idx = idx

    def empty(self) -> T:
        if self.__data is None:
            raise ValueError(f'FATAL: This Item is already empty.')
        
        temp = self.__data
        self.__data = None
        return temp