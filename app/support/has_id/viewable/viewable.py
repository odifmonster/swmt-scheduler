#!/usr/bin/env python

from typing import TypeVar, Generic, Protocol
from abc import abstractmethod

T = TypeVar('T')

class Viewable(Generic[T], Protocol):

    @abstractmethod
    def view(self) -> T:
        raise NotImplementedError()