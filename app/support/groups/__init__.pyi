from typing import TypeVar, Protocol, Generic, Iterator
from abc import abstractmethod
from app.support import ValueLike, PrettyArgsOpt, Viewable

_T_A = TypeVar('_T_A', str, int)
_T_A_co = TypeVar('_T_A_co', bound=PrettyArgsOpt, covariant=True)
_Empty = tuple[()]

class AtomLike(Protocol[_T_A, _T_A_co], ValueLike[_T_A, _T_A_co]):
    """
    A protocol for 'atoms' of a group (these are individual data points and not
    themselves groups).
    """
    @abstractmethod
    def __getitem__(self, key: _Empty) -> 'AtomLike[_T_A, _T_A_co]': ...
    @abstractmethod
    def __iter__(self) -> 'Iterator[AtomLike[_T_A, _T_A_co]]': ...

_DataView = AtomLike[_T_A, _T_A_co]
_Data = Viewable[_DataView[_T_A, _T_A_co]]

class Item(Generic[_T_A, _T_A_co]):
    """
    A generic container for atoms of groups. It tracks order of insertion for iterating
    purposes. Its contents cannot be mutated unless they are removed.
    """
    def __init__(self) -> None: ...
    @property
    def inserted(self) -> bool:
        """Returns True iff this Item held data at some point."""
        ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def data(self) -> _DataView[_T_A, _T_A_co]:
        """Returns a live, read-only view of the contents of this Item."""
        ...
    def store(self, data: _Data[_T_A, _T_A_co], at_idx: int) -> None:
        """Stores the provided data, tracks insertion order using 'at_idx'."""
        ...
    def clear(self) -> _Data[_T_A, _T_A_co]:
        """Clears this Item and returns the mutable object it was storing."""
        ...