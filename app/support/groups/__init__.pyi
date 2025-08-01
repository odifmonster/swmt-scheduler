from typing import TypeVar, Generic
from app.support import Viewable

_T_item = TypeVar('_T_item', bound=Viewable)
_U = TypeVar('_U')

class Item(Generic[_T_item, _U]):
    """
    A wrapper class for storing hashable items in a collection. Contains link
    to data and tracks order of insertion for iterating.
    """
    def __init__(self) -> None: ...
    @property
    def was_inserted(self) -> bool: ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def data(self) -> _U:
        """Returns a view of the stored data."""
        ...
    def store(self, value: _T_item, idx: int) -> None: ...
    def empty(self) -> _T_item:
        """Empties this item and returns the actual object stored."""
        ...