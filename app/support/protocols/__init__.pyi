from typing import Protocol, Hashable
from abc import abstractmethod

class HasID[T: Hashable](Protocol):
    """
    A protocol for objects that use their own unique, hashable
    ids for hashing and equality.
    """
    def __eq__(self, other: 'HasID[T]') -> bool: ...
    def __hash__(self) -> int: ...
    def __repr__(self) -> str: ...
    @property
    @abstractmethod
    def _prefix(self) -> str:
        """
        For internal use only. Prevents two objects of different types from
        being treated as equal.
        """
        ...
    @property
    @abstractmethod
    def id(self) -> T:
        """The unique, hashable id of this object."""
        ...