#!/usr/bin/env python

from typing import TypeVar, Generic, Protocol, NamedTuple
from datetime import datetime

class _SupportsComp(Protocol):
    def __eq__(self, value: '_SupportsComp') -> bool: ...
    def __le__(self, value: '_SupportsComp') -> bool: ...
    def __lt__(self, value: '_SupportsComp') -> bool: ...
    def __ge__(self, value: '_SupportsComp') -> bool: ...
    def __gt__(self, value: '_SupportsComp') -> bool: ...

T = TypeVar('T', bound=_SupportsComp)

class ContRange(Generic[T], NamedTuple):
    minval: T
    maxval: T

    def contains(self, value: T):
        return self.minval <= value and self.maxval >= value
    
    def is_above(self, value: T):
        return self.minval > value
    
    def is_below(self, value: T):
        return self.maxval < value
    
class FloatRange(ContRange[float]):

    def average(self) -> float:
        return (self.minval+self.maxval)/2

DateRange = ContRange[datetime]