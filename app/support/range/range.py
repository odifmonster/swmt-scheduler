#!/usr/bin/env python

from typing import NamedTuple, Unpack
import datetime as dt

class ContRange[T](NamedTuple):
    minval: T
    maxval: T
    
    def contains(self, val: 'T | ContRange[T]'):
        if hasattr(val, 'minval'):
            return val.minval >= self.minval and val.maxval <= self.maxval
        return val >= self.minval and val <= self.maxval
    
    def is_above(self, val: T):
        return val < self.minval
    
    def is_below(self, val: T):
        return val > self.maxval
    
class FloatRange(ContRange[float]):

    def average(self):
        return (self.minval + self.maxval) / 2

DateRange = ContRange[dt.datetime]

def min_float_rng(*args: Unpack[tuple[FloatRange, ...]]):
    return FloatRange(max(map(lambda r: r.minval, args)), min(map(lambda r: r.maxval, args)))

def max_float_rng(*args: Unpack[tuple[FloatRange, ...]]):
    return FloatRange(min(map(lambda r: r.minval, args)), max(map(lambda r: r.maxval, args)))