#!/usr/bin/env python

from typing import TypeVar, Protocol
from abc import abstractmethod

T = TypeVar('T')

class Viewable(Protocol[T]):

    @abstractmethod
    def view(self) -> T:
        raise NotImplementedError()