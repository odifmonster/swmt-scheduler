from . import groups as groups
from . import decors as decors

from typing import TypeVar, Generic, Hashable, Self
from abc import ABC, abstractmethod

_T1 = TypeVar('T1', bound=Hashable)

class HasID(Generic[_T1], Hashable):
    def __init__(self, id: _T1, prefix: str) -> None: ...
    @property
    def id(self) -> _T1:
        """The unique, hashable id of this object."""
        ...
    def __eq__(self, value: Self) -> bool: ...
    def __hash__(self) -> int: ...

_T2 = TypeVar('T2')

class Viewable(Generic[_T2], ABC):
    """
    Generic, abstract class for view types. Subclasses should not have setters
    or setter-like behavior, and should provide live views into data from
    other objects.
    """
    @abstractmethod
    def view(self) -> _T2: ...