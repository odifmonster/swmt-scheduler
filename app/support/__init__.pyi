from app.support import groups as groups

from typing import TypeVar, Generic, Protocol, Self, Any, \
    Hashable, Iterator, Callable
from abc import abstractmethod

_T_HasID = TypeVar('_T_HasID', str, int)
_T_View_co = TypeVar('T_View_co', contravariant=True)

class HasID(Protocol[_T_HasID], Hashable):
    """
    A protocol for objects uniquely identifiable by user-provided ids (as opposed
    to python default id(object)).
    """
    @property
    @abstractmethod
    def _prefix(self) -> str:
        """For internal use only. Necessary to implement, but do not access."""
        ...
    @property
    @abstractmethod
    def id(self) -> _T_HasID: ...
    def __eq__(self, value: Self) -> bool: ...
    def __hash__(self) -> int: ...

class Viewable(Protocol[_T_View_co]):
    """
    A protocol for objects that provide live, read-only "views" of their data.
    """
    @abstractmethod
    def view(self) -> _T_View_co: ...

_T_SV_co = TypeVar('_T_SV_co', covariant=True)

class SuperView(Generic[_T_SV_co]):
    """
    Super class for easy creation of view types. Type parameter is usually a Protocol,
    and 'gettables' is a list of attributes to make read-only for this view.
    """
    def __init_subclass__(cls, gettables: list[str]) -> None: ...
    def __init__(self, link: _T_SV_co) -> None: ...

_T_SI_co = TypeVar('_T_SI_co', covariant=True)
_U_SI_co = TypeVar('_U_SI_co', covariant=True)

class SuperIter(Generic[_T_SI_co, _U_SI_co], Iterator[_U_SI_co]):
    """
    Super class for easy creation of "wrapper" iterators. The wrapper applies a
    function to every output of the inner iterator to get its next value.
    """
    def __init_subclass__(cls, get_val: Callable[[_T_SI_co], _U_SI_co]) -> None: ...
    def __init__(self, link: Iterator[_T_SI_co]) -> None: ...
    def __iter__(self) -> Iterator[_U_SI_co]: ...
    def __next__(self) -> _U_SI_co: ...

class SupportsPretty(Protocol):
    """
    A protocol for objects whose string representations change depending on context.
    """
    @abstractmethod
    def pretty(self, **kwargs: dict[str, Any]) -> str: ...

_T_SPID = TypeVar('_T_SPID', str, int)

class SupportsPrettyID(Generic[_T_SPID], SupportsPretty, HasID[_T_SPID], Protocol):
    """
    A protocol for objects that can be pretty and have ids (for contents of groups).
    """
    ...