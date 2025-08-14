from typing import TypeVar, Protocol
from abc import abstractmethod

_T = TypeVar('_T')

class Viewable(Protocol[_T]):
    """
    A protocol for objects that provide views of themselves.
    """
    @abstractmethod
    def view(self) -> _T:
        """Return a live, read-only view of this object."""
        ...