from app.support.protocols import PrettyArgsOpt as PrettyArgsOpt

from typing import TypeVar, Generic, Protocol, Self, Any, \
    Hashable, Iterable, Callable, Generator, \
    Unpack
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
    and 'no_access' is a list of methods that the view should not have access to
    (presumably because they change the underlying object in some way). 'overrides'
    is a list of overridden methods/properties (if any).
    """
    def __init_subclass__(cls, no_access: list[str], overrides: list[str]) -> None: ...
    def __init__(self, link: _T_SV_co) -> None: ...

_T_SI_co = TypeVar('_T_SI_co', covariant=True)
_U_SI_co = TypeVar('_U_SI_co', covariant=True)

class SuperIter(Generic[_T_SI_co, _U_SI_co], Iterable[_U_SI_co]):
    """
    Super class for easy creation of "wrapper" iterators. The wrapper applies a
    function to every output of the inner iterator to get its next value.
    """
    def __init_subclass__(cls, get_val: Callable[[_T_SI_co], _U_SI_co]) -> None: ...
    def __init__(self, link: Iterable[_T_SI_co]) -> None: ...
    def __iter__(self) -> Generator[_U_SI_co, Any, None]: ...

_T_P_co = TypeVar('_T_P_co', bound=PrettyArgsOpt, covariant=True)

class SupportsPretty(Protocol[_T_P_co]):
    """
    A protocol for objects whose string representations should be formatted differently
    depending on context. Provides two helper functions for maintaining a certain
    maximum representation size.
    """
    def shorten_line(self, line: str, **kwargs: Unpack[_T_P_co]) -> str: ...
    def shorten_lines(self, lines: list[str], **kwargs: Unpack[_T_P_co]) -> list[str]: ...
    def validate_args(self, val: _T_P_co) -> _T_P_co: ...
    @abstractmethod
    def pretty(self, **kwargs: Unpack[_T_P_co]) -> str: ...