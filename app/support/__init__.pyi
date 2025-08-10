from app.support.protocols import PrettyArgsOpt as PrettyArgsOpt
from app.support import groups as groups

from typing import TypeVar, Generic, Protocol, Self, Any, \
    Hashable, Iterable, Callable, Generator, NamedTuple, \
    Unpack
from abc import abstractmethod
import datetime

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
    Super class for easy creation of view types. Type parameter is usually a Protocol.
    """
    def __init_subclass__(cls, no_access: list[str], overrides: list[str],
                          dunders: list[str]) -> None:
        """
        Define a new view type.
        no_access: a list of methods that the view should not have access to
        overrides: a list of overridden methods/properties (if any)
        dunders: a list of 'dunder' methods that can be used by the view (without underscores)
        """
        ...
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

class SuperImmut:
    """
    Super class for easy creation of custom immutable objects. All attribute values
    are defined in the initializer and unchangeable after that point.
    """
    def __init_subclass__(cls, attrs: list[str], defaults: dict[str, Any]) -> None:
        """
        Define a custom immutable type. The positional arguments are the names of
        this type's attributes. The keyword arguments are (optional) default values
        for any of the provided attributes.
        """
        ...
    def __init__(self, **kwargs: Unpack[dict[str, Any]]) -> None: ...
    def __setattr__(self, name: str, value: Any) -> None:
        """Always raises an AttributeError."""
        ...
    def __repr__(self) -> str: ...

class _SupportsComparison(Protocol):
    def __eq__(self, value) -> bool: ...
    def __le__(self, value) -> bool: ...
    def __lt__(self, value) -> bool: ...
    def __ge__(self, value) -> bool: ...
    def __gt__(self, value) -> bool: ...

_T_CR = TypeVar('_T_CR', bound=_SupportsComparison)

class CompRange(Generic[_T_CR], NamedTuple):
    minval: _T_CR
    maxval: _T_CR
    def contains(self, value: _T_CR) -> bool:
        """Return True iff 'value' is within this range."""
        ...
    def is_above(self, value: _T_CR) -> bool:
        """Return True iff 'value' is below this range."""
        ...
    def is_below(self, value: _T_CR) -> bool:
        """Return True iff 'value' is above this range."""
        ...

FloatRange = CompRange[float]
DateRange = CompRange[datetime.datetime]

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