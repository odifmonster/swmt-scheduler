#!/usr/bin/env python

from typing import TypeVar, Generic, Self

from app.support import Viewable, SupportsPrettyID, PrettyArgsOpt

T = TypeVar('T', str, int)
U_co = TypeVar('U_co', bound=PrettyArgsOpt, covariant=True)
Data = Viewable[SupportsPrettyID[T, U_co]]

class Item(Generic[T, U_co]):

    def __init__(self):
        self.__data: Data[T, U_co] | None = None
        self.__idx = -1

    @property
    def data(self):
        if self.__data is None:
            raise AttributeError('Cannot access data from empty Item.')
        return self.__data.view()
    
    def __eq__(self, other: Self):
        return self.__idx == other.__idx
    
    def __lt__(self, other: Self):
        return self.__idx < other.__idx
    
    def inserted(self):
        return self.__idx >= 0
    
    def is_empty(self):
        return self.__data is None
    
    def store(self, data: Data, idx: int):
        if idx <= self.__idx:
            raise ValueError(f'Bad insertion index: {idx}.')
        if not self.__data is None:
            raise RuntimeError('Attempted to overwrite existing Item data.')
        
        self.__data = data
        self.__idx = idx
    
    def clear(self) -> Data:
        if self.__data is None:
            raise RuntimeError('Attempted to clear empty Item.')
        temp = self.__data
        self.__data = None
        return temp