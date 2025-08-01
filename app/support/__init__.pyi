from typing import TypeVar, Generic, Self, Hashable, Protocol
from abc import abstractmethod

_T_HasID = TypeVar('_T_HasID', str, int)

class HasID(Generic[_T_HasID], Hashable):
    """
    A base class for providing objects with identifiers. Provides custom definition
    of uniqueness within the application.
    """
    def __init__(self, id: _T_HasID, prefix: str) -> None: ...
    @property
    def id(self) -> _T_HasID: ...
    def __eq__(self, value: Self) -> bool: ...
    def __hash__(self) -> int: ...

_T_v_co = TypeVar('_T_v_co', covariant=True)

class Viewable(Protocol[_T_v_co]):
    """
    A protocol for creating "viewable" objects. The 'view' object provides a live,
    read-only observer of data in some other linked object.
    """
    @abstractmethod
    def view(self) -> _T_v_co: ...