#!/usr/bin/env python

from ..temp import Data, DataView

class Item:

    def __init__(self):
        self.__data: Data | None = None
        self.__idx = -1

    @property
    def data(self) -> DataView:
        if self.__data is None:
            raise AttributeError('Cannot access data from empty Item.')
        return self.__data.view()
    
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