#!/usr/bin/env python

from typing import NamedTuple, Protocol, Generic, TypeVar
import datetime

class _SupportsComparison(Protocol):
    def __eq__(self, value) -> bool: ...
    def __le__(self, value) -> bool: ...
    def __lt__(self, value) -> bool: ...
    def __ge__(self, value) -> bool: ...
    def __gt__(self, value) -> bool: ...

T = TypeVar('T', bound=_SupportsComparison)

class CompRange(Generic[T], NamedTuple):
    minval: T
    maxval: T

    def contains(self, value: T):
        return value >= self.minval and value <= self.maxval
    
    def is_above(self, value: T):
        return value < self.minval
    
    def is_below(self, value: T):
        return value > self.maxval

FloatRange = CompRange[float]
DateRange = CompRange[datetime.datetime]