#!/usr/bin/env python

from typing import TypeVar, Generic, Protocol
from abc import abstractmethod

from app.support import Viewable, SuperView, PrettyArgsOpt
from app.support.groups import DataLike, ValueLike

T = TypeVar('T', str, int)
T_co = TypeVar('T_co', bound=PrettyArgsOpt, covariant=True)
Empty = tuple[()]

class AtomLike(Generic[T, T_co], ValueLike[T, T_co, T_co], Protocol):

    @property
    @abstractmethod
    def data(self) -> DataLike[T, T_co]:
        raise NotImplementedError()
    
    @property
    @abstractmethod
    def is_empty(self) -> bool:
        raise NotImplementedError()
    
    def __len__(self):
        if self.is_empty:
            return 0
        return 1

    def __iter__(self):
        yield tuple()

    def __getitem__(self, key: Empty):
        if not type(key) is tuple:
            raise TypeError(f'Atoms do not accept type \'{type(key)}\' as keys.')
        if len(key) > 0:
            raise ValueError(f'{len(key)}-dim key incompatible with 0-dim Atom.')
        return self.data
    
    @abstractmethod
    def add(self, data: Viewable[DataLike[T, T_co]]):
        raise NotImplementedError()
    
    @abstractmethod
    def remove(self, id: T):
        raise NotImplementedError()
    
    def pretty(self, **kwargs):
        if self.is_empty:
            return ''
        return self.data.pretty(**kwargs)
    
class AtomView(Generic[T, T_co], SuperView[AtomLike[T, T_co]],
               no_access=['add', 'remove'],
               overrides=[]):
    pass

class Atom(Generic[T, T_co], AtomLike[T, T_co], Viewable[AtomView[T, T_co]]):

    def __init__(self):
        self.__data: Viewable[DataLike[T, T_co]] | None = None
        self.__view = AtomView(self)

    @property
    def data(self):
        if self.__data is None:
            raise AttributeError('Object has no data to access.')
        return self.__data.view()
    
    @property
    def is_empty(self):
        return self.__data is None
    
    def add(self, data: Viewable[DataLike[T, T_co]]):
        if not self.__data is None:
            raise RuntimeError(f'Object already has data.')
        self.__data = data
    
    def remove(self, id: T):
        if self.__data is None:
            raise RuntimeError('Object has no data to remove.')
        if self.__data.view().id != id:
            raise ValueError(f'Object data does not have id {repr(id)}.')
        temp = self.__data
        self.__data = None
        return temp
    
    def view(self):
        return self.__view