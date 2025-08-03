#!/usr/bin/env python

from typing import TypeVar, Protocol
from abc import abstractmethod

T_co = TypeVar('T_co', covariant=True)

class Viewable(Protocol[T_co]):

    @abstractmethod
    def view(self) -> T_co:
        raise NotImplementedError()