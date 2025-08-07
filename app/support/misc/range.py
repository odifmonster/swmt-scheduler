#!/usr/bin/env python

from typing import NamedTuple

class FloatRange(NamedTuple):
    minval: float
    maxval: float

    def contains(self, value):
        return value >= self.minval and value <= self.maxval