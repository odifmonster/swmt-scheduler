#!/usr/bin/env python

from typing import Protocol
from abc import abstractmethod

class SupportsPretty(Protocol):

    @abstractmethod
    def pretty(self, **kwargs): raise NotImplementedError()