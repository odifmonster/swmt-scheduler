from typing import TypeVar, TypeVarTuple, Protocol, Generic, Any, \
    Iterator, \
    Unpack
from abc import abstractmethod
from app.support import HasID, SupportsPretty, PrettyArgsOpt, Viewable, \
    SuperView

_T_D = TypeVar('_T_D', str, int)
_T_D_co = TypeVar('_T_D_co', bound=PrettyArgsOpt, covariant=True)

class DataLike(Protocol[_T_D, _T_D_co], HasID[_T_D], SupportsPretty[_T_D_co]):
    """
    A protocol for objects that can be added to groups. Combines HasID and
    SupportsPretty protocols.
    """
    ...

_T_V_co = TypeVar('_T_V_co', bound=PrettyArgsOpt, covariant=True)
_T_Vs = TypeVarTuple('_T_Vs')

class ValueLike(Protocol[_T_D, _T_V_co, _T_D_co, *_T_Vs], SupportsPretty[_T_V_co]):
    """
    A protocol for objects that are values of groups.
    """
    @abstractmethod
    def __len__(self) -> int: ...
    @abstractmethod
    def __iter__(self) -> Iterator: ...
    @abstractmethod
    def __getitem__(self, key: tuple) -> 'ValueLike[_T_D, Any, _T_D_co] | DataLike[_T_D, _T_D_co]':
        ...
    @abstractmethod
    def add(self, data: DataLike[_T_D, _T_D_co]) -> None: ...
    @abstractmethod
    def remove(self, id: _T_D) -> DataLike[_T_D, _T_D_co]: ...

_Empty = tuple[()]

class AtomLike(Protocol[_T_D, _T_D_co], ValueLike[_T_D, _T_D_co, _T_D_co]):
    """
    A protocol for "atoms" of a group. These represent individual elements of a group,
    but support group-like functions for the purpose of properly abstracting group
    operations.
    """
    @property
    @abstractmethod
    def data(self) -> DataLike[_T_D, _T_D_co]: ...
    @property
    @abstractmethod
    def is_empty(self) -> bool: ...
    def __iter__(self) -> Iterator[_Empty]: ...
    def __getitem__(self) -> DataLike[_T_D, _T_D_co]: ...
    @abstractmethod
    def add(self, data: Viewable[DataLike[_T_D, _T_D_co]]) -> None: ...
    @abstractmethod
    def remove(self, id: _T_D) -> Viewable[DataLike[_T_D, _T_D_co]]: ...
    def pretty(self, **kwargs: Unpack[_T_D_co]) -> str: ...

class AtomView(Generic[_T_D, _T_D_co], AtomLike[_T_D, _T_D_co],
               SuperView[AtomLike[_T_D, _T_D_co]],
               no_access=['add', 'remove'], overrides=[]):
    """
    A live, read-only view of an Atom object. Cannot use 'add' or 'remove' methods.
    """
    ...

class Atom(Generic[_T_D, _T_D_co], AtomLike[_T_D, _T_D_co],
           Viewable[AtomView[_T_D, _T_D_co]]):
    """
    The concrete and mutable implementation of the AtomLike protocol.
    """
    ...
    def __init__(self) -> None: ...