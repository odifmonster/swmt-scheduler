from typing import TypeVar, Generic
from app.helper import Viewable

_T1 = TypeVar('_T1', bound=Viewable)
_U1 = TypeVar('_U1')

class Item(Generic[_T1, _U1]):
    """
    A class for storing data in specialized collections of objects with hashable ids.
    Most important function is differentiating between removed (and thus mutable) objects
    and merely accessed (and immutable) objects.
    """
    def __init__(self) -> None: ...
    @property
    def was_inserted(self) -> bool:
        """Returns True iff this object has had data stored in it at some point."""
        ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def data(self) -> _U1:
        """Returns a view on this Item's data."""
        ...
    def store(self, val: _T1, idx: int) -> None:
        """Stores the provided value in this Item and tracks order of insertion."""
        ...
    def clear(self) -> _T1:
        """Empties the contents of this Item and returns the original object stored."""
        ...