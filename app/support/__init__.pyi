from typing import TypeVar, Protocol, Self, Hashable
from abc import abstractmethod

_T_HasID = TypeVar('_T_HasID', str, int)

class HasID(Protocol[_T_HasID], Hashable):
    """
    A protocol for objects uniquely identifiable by user-provided ids (as opposed
    to python default id(object)).
    """
    @property
    @abstractmethod
    def _prefix(self) -> str:
        """For internal use only. Necessary to implement, but do not access."""
        ...
    @property
    @abstractmethod
    def id(self) -> _T_HasID: ...
    def __eq__(self, value: Self) -> bool: ...
    def __hash__(self) -> int: ...