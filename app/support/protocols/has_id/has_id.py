#!/usr/bin/env python

from typing import TypeVar, Protocol, Self
from abc import abstractmethod
from collections.abc import Hashable

T = TypeVar('T', str, int)

class HasID(Protocol[T], Hashable):

    @property
    @abstractmethod
    def _prefix(self):
        raise NotImplementedError()
    
    @property
    @abstractmethod
    def id(self):
        raise NotImplementedError()

    def __eq__(self, value: Self):
        return self.id == value.id and self._prefix == value._prefix
    
    def __hash__(self):
        return self.id.__hash__()