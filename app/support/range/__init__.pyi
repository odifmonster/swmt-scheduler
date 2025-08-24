from typing import Protocol, NamedTuple, Unpack
import datetime as dt

class _SupportsComp(Protocol):
    def __eq__(self, other: '_SupportsComp') -> bool: ...
    def __le__(self, other: '_SupportsComp') -> bool: ...
    def __lt__(self, other: '_SupportsComp') -> bool: ...
    def __ge__(self, other: '_SupportsComp') -> bool: ...
    def __gt__(self, other: '_SupportsComp') -> bool: ...

class ContRange[T: _SupportsComp](NamedTuple):
    minval: T
    maxval: T
    def contains(self, val: 'T | ContRange[T]') -> bool:
        """
        Returns True iff 'val' is fully contained within the defined range.
        """
        ...
    def is_above(self, val: T) -> bool:
        """Returns True iff this range is fully above 'val'."""
        ...
    def is_below(self, val: T) -> bool:
        """Returns True iff this range is fully below 'val'."""
        ...

class FloatRange(ContRange[float]):
    def average(self) -> float:
        """Returns the middle value of the range."""
        ...

DateRange = ContRange[dt.datetime]

def min_float_rng(*args: Unpack[tuple[FloatRange, ...]]) -> FloatRange:
    """
    Gets a "minimum" of all the provided ranges. The result is the largest
    range such that passing it to the 'contains' method of every argument
    returns True.
    """
    ...

def max_float_rng(*args: Unpack[tuple[FloatRange, ...]]) -> FloatRange:
    """
    Gets a "maximum" of all the provided ranges. The result is the smallest
    range such that passing every argument to its 'contains' method returns
    True.
    """
    ...