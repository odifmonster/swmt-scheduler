#!/usr/bin/env python

from typing import Generic, Protocol, TypeVar, TypeVarTuple
from abc import abstractmethod

from ..has_id import HasID
from ..pretty import SupportsPretty, PrettyArgsOpt

T = TypeVar('T', str, int)
T_co = TypeVar('T_co', bound=PrettyArgsOpt, covariant=True)
Ts = TypeVarTuple('Ts')

class ValueLike(Generic[T, T_co, *Ts],
                HasID[T], SupportsPretty[T_co],
                Protocol):
    
    @abstractmethod
    def __getitem__(self, key: tuple):
        raise NotImplementedError()
    
    @abstractmethod
    def __iter__(self):
        raise NotImplementedError()