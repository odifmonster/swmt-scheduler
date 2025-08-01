from typing import TypeVar, Generic, Self, Iterator
from abc import ABC, abstractmethod
from app.support import Viewable, HasID

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
    def __eq__(self, value: Self) -> bool: ...
    def __lt__(self, value: Self) -> bool: ...
    def store(self, value: _T_item, idx: int) -> None: ...
    def empty(self) -> _T_item:
        """Empties this item and returns the actual object stored."""
        ...

_S_BG = TypeVar('_S_BG', bound=Viewable[HasID])
_T_BG = TypeVar('_T_BG', bound=HasID)
_U_BG = TypeVar('_U_BG', str, int)

class BaseGroup(Generic[_S_BG, _T_BG, _U_BG], ABC):
    """
    An abstract base class for set-like groups that preserve insertion order and
    whose contents implement HasID for identifying uniqueness.
    """
    def __init__(self, initsize: int) -> None: ...
    @property
    def n_items(self) -> int: ...
    @abstractmethod
    def add(self, value: _S_BG) -> None: ...
    @abstractmethod
    def remove(self, item_id: _U_BG) -> _S_BG:
        """Removes and returns the object with this id."""
        ...
    def get_by_id(self, item_id: _U_BG) -> _T_BG:
        """Returns a view of the object with this id."""
        ...
    def iter_items(self) -> Iterator[_T_BG]:
        """Returns a flat iterator over views of the objects in this group."""
        ...