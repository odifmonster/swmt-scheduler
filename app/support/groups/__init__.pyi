from typing import TypeVar, Generic, Self
from app.support import Viewable

_T_Item = TypeVar('_T_Item', bound=Viewable)
_U_Item = TypeVar('_U_Item')

class Item(Generic[_T_Item, _U_Item]):
    """
    A class for storing data about the contents of Groups. Tracks insertion order for
    iteration and sorting purposes.
    """
    def __init__(self) -> None: ...
    @property
    def data(self) -> _U_Item:
        """Returns a view of this Item's contents (if non-empty)."""
        ...
    def __eq__(self, value: Self) -> bool: ...
    def __lt__(self, value: Self) -> bool: ...
    def was_inserted(self) -> bool: ...
    def is_empty(self) -> bool: ...
    def insert(self, data: _T_Item, idx: int) -> None:
        """
        Call when inserting data into this Item. 'idx' argument should reflect the
        order of insertion in the container class.
        """
        ...
    def remove(self) -> _T_Item:
        """Empties this Item and returns the actual object it was holding."""
        ...