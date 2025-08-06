#!/usr/bin/env python

from typing import TypeVar, TypeVarTuple, Generic, Protocol
from abc import abstractmethod

from app.support import SupportsPretty, PrettyArgsOpt
from .data import DataLike

T = TypeVar('T', str, int)
T_co = TypeVar('T_co', bound=PrettyArgsOpt, covariant=True)
U_co = TypeVar('U_co', bound=PrettyArgsOpt, covariant=True)
Ts = TypeVarTuple('Ts')

class ValueLike(Generic[T, T_co, U_co, *Ts], SupportsPretty[T_co], Protocol):

    @abstractmethod
    def __len__(self):
        raise NotImplementedError()

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError()
    
    @abstractmethod
    def __getitem__(self, key: tuple):
        raise NotImplementedError()
    
    @abstractmethod
    def add(self, data: DataLike[T, U_co]):
        raise NotImplementedError()
    
    @abstractmethod
    def remove(self, id: T):
        raise NotImplementedError()