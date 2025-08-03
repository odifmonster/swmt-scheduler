#!/usr/bin/env python

from typing import TypeVar, Generic, Self
from collections.abc import Hashable

T = TypeVar('T', str, int)

class HasID(Generic[T], Hashable):

    def __init__(self, id: T, prefix: str):
        self.id = id
        self._prefix = prefix

    def __eq__(self, value: Self):
        return self.id == value.id and self._prefix == value._prefix
    
    def __hash__(self):
        return self.id.__hash__()