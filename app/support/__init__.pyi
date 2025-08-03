from app.support import groups as groups

from typing import TypeVar, Generic, Protocol, Self, \
    Hashable
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