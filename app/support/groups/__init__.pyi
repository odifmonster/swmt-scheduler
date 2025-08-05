from app.support.groups.grouped import Grouped1D as Grouped1D
from app.support.groups.grouped import Grouped2D as Grouped2D

from typing import TypeVar, Protocol, Iterator
from abc import abstractmethod
from app.support import HasID, ValueLike, PrettyArgsOpt

_T_A = TypeVar('_T_A', str, int)
_T_A_co = TypeVar('_T_A_co', bound=PrettyArgsOpt, covariant=True)
_Empty = tuple[()]

class AtomLike(Protocol[_T_A, _T_A_co], HasID[_T_A], ValueLike[_T_A, _T_A_co]):
    """
    A protocol for 'atoms' of a group (these are individual data points and not
    themselves groups). As such, they will also have ids.
    """
    @abstractmethod
    def __getitem__(self, key: _Empty) -> 'AtomLike[_T_A, _T_A_co]': ...
    @abstractmethod
    def __iter__(self) -> 'Iterator[AtomLike[_T_A, _T_A_co]]': ...