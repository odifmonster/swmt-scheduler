#!/usr/bin/env python

from typing import Protocol, Hashable
from abc import abstractmethod

class HasID[T: Hashable](Protocol):

    def __eq__(self, other: 'HasID[T]'):
        return self._prefix == other._prefix and self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
    
    def __repr__(self):
        return f'{self._prefix}(id={repr(self.id)})'

    @property
    @abstractmethod
    def _prefix(self) -> str:
        raise NotImplementedError()
    
    @property
    @abstractmethod
    def id(self) -> T:
        raise NotImplementedError()