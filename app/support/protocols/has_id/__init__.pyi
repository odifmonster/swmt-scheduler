from typing import TypeVar, Protocol, Hashable
from abc import abstractmethod

_T = TypeVar('_T', bound=Hashable)

class HasID(Protocol[_T], Hashable):
    """
    A protocol for objects identified by a user-provided unique id. Allows you to define mutable
    objects whose __eq__ behavior is not equivalent to built-in 'is'.
    """
    @property
    @abstractmethod
    def _prefix(self) -> str:
        """
        Allows __eq__ to differentiate between different classes that implement the HasID protocol.
        """
        ...
    @property
    @abstractmethod
    def id(self) -> _T:
        """The unique, hashable id of this object."""
        ...
    def __eq__(self, value: 'HasID[_T]') -> bool:
        """
        Defines behavior for '==' operator. Objects with the same '_prefix' and 'id' will compare
        equal.
        """
        ...
    def __hash__(self) -> int: ...