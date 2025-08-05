#!/usr/bin/env python

from typing import TypeVar, Generic

from app.support import PrettyArgsOpt, Viewable
from app.support.groups import AtomLike

T = TypeVar('T', str, int)
T_co = TypeVar('T_co', bound=PrettyArgsOpt, covariant=True)
DataView = AtomLike[T, T_co]
Data = Viewable[DataView[T, T_co]]

class Item(Generic[T, T_co]):

    def __init__(self):
        self.__data: Data[T, T_co] | None = None
        self.__idx = -1

    @property
    def inserted(self) -> bool:
        return self.__idx >= 0
    
    @property
    def is_empty(self) -> bool:
        return self.__data is None

    @property
    def data(self) -> DataView[T, T_co]:
        if self.__data is None:
            raise AttributeError('Cannot access data from empty Item.')
        return self.__data.view()
    
    def store(self, data: Data[T, T_co], at_idx: int) -> None:
        if not self.is_empty:
            raise RuntimeError('Cannot store data in non-empty Item.')
        if at_idx <= self.__idx:
            raise ValueError(f'Bad insertion index: {at_idx}.')
        
        self.__data = data
        self.__idx = at_idx

    def clear(self) -> Data[T, T_co]:
        if self.__data is None:
            raise ValueError('Cannot clear an empty Item.')
        
        temp = self.__data
        self.__data = None
        return temp