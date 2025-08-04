from typing import TypeVar, Generic, Self
from app.support import Viewable, SupportsPrettyID, PrettyArgsOpt

_T_I = TypeVar('_T_I', str, int)
_U_I_co = TypeVar('_U_I_co', bound=PrettyArgsOpt, covariant=True)

_DataView = SupportsPrettyID[_T_I, _U_I_co]
_Data = Viewable[_DataView[_T_I, _U_I_co]]

class Item(Generic[_T_I, _U_I_co]):
    """
    A class for storing data about the contents of Groups. Tracks insertion order (this
    must be provided by the container class). Can be sorted by insertion order.
    """
    def __init__(self) -> None: ...
    @property
    def data(self) -> _DataView[_T_I, _U_I_co]:
        """Returns a live, read-only view of the data stored in this item."""
        ...
    def __eq__(self, other: Self) -> bool: ...
    def __lt__(self, other: Self) -> bool: ...
    def inserted(self) -> bool:
        """Returns True iff this Item had data stored in it at one point."""
        ...
    def is_empty(self) -> bool: ...
    def store(self, data: _Data[_T_I, _U_I_co], idx: int) -> None:
        """Stores the provided data, tracks order of insertion with 'idx'."""
        ...
    def clear(self) -> _Data[_T_I, _U_I_co]:
        """Removes the stored data and returns it."""
        ...

