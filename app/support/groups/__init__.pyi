from app.support.groups.atomic import *

from typing import TypeVar, Generic, Self, Any, \
    Iterator
from abc import ABC, abstractmethod
from collections.abc import KeysView
from app.support import Viewable, SupportsPrettyID

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

_S_BG_co = TypeVar('_S_BG_co', bound=Viewable[SupportsPrettyID], covariant=True)
_T_BG_co = TypeVar('_T_BG_co', bound=SupportsPrettyID, covariant=True)
_U_BG = TypeVar('_U_BG', str, int)

class BaseGroup(Generic[_S_BG_co, _T_BG_co, _U_BG], ABC):
    """
    An abstract container-like class whose contents are read-only until they are
    removed. Contents are accessed by id, and insertion order is preserved.
    """
    def __init__(self, initsize: int) -> None: ...
    @property
    def n_items(self) -> int:
        """
        The number of items in this Group. For sub-classes, differs from len(Group)
        in that "nested" groups will return the flat number of items, not the number
        of sub-groups.
        """
        ...
    @abstractmethod
    def __len__(self) -> int: ...
    @abstractmethod
    def __iter__(self) -> Iterator[Any]: ...
    @abstractmethod
    def __contains__(self, key: Any) -> Iterator[Any]: ...
    @abstractmethod
    def __getitem__(self, key: Any) -> Any: ...
    @abstractmethod
    def add(self, data: _S_BG_co) -> None: ...
    @abstractmethod
    def remove(self, item_id: _U_BG) -> _S_BG_co: ...
    @abstractmethod
    def keys(self) -> KeysView[Any]: ...
    def get_by_id(self, item_id: _U_BG) -> _T_BG_co: ...
    def iter_items(self) -> Iterator[_T_BG_co]: ...