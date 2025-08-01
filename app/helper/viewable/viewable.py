#!/usr/bin/env python

from typing import TypeVar, Generic

from abc import ABC, abstractmethod

T = TypeVar('T')

class Viewable(Generic[T], ABC):

    @abstractmethod
    def view(self) -> T:
        raise NotImplementedError()