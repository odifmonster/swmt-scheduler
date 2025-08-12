#!/usr/bin/env python

from typing import TypeVar, Protocol, Hashable
from abc import abstractmethod

T = TypeVar('T', bound=Hashable)

class HasID(Protocol[T], Hashable):

    @property
    @abstractmethod
    def _prefix(self):
        raise NotImplementedError()
    
    @property
    @abstractmethod
    def id(self) -> T:
        raise NotImplementedError()
    
    def __eq__(self, value: 'HasID[T]'):
        return self._prefix == value._prefix and self.id == value.id
    
    def __hash__(self):
        return hash(self.id)