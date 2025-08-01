from . import groups as groups
from . import decors as decors

from typing import TypeVar, Generic, Hashable, Self

_T1 = TypeVar('T1', bound=Hashable)

class HasID(Generic[_T1], Hashable):
    def __init__(self, id: _T1, prefix: str) -> None: ...
    @property
    def id(self) -> _T1:
        """The unique, hashable id of this object."""
        ...
    def __eq__(self, value: Self) -> bool: ...
    def __hash__(self) -> int: ...