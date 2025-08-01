from typing import TypeVar, Generic, Self, Hashable

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