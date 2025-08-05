#!/usr/bin/env python

from typing import TypeVar, Generic, Protocol
from abc import abstractmethod

from app.support import HasID, ValueLike, PrettyArgsOpt

T = TypeVar('T', str, int)
T_co = TypeVar('T_co', bound=PrettyArgsOpt, covariant=True)

class AtomLike(Generic[T, T_co], HasID[T], ValueLike[T_co], Protocol):

    @abstractmethod
    def __getitem__(self, key):
        raise NotImplementedError()
    
    @abstractmethod
    def __iter__(self):
        raise NotImplementedError()