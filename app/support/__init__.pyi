from typing import TypeVar, Generic, Protocol, Hashable, Self

_T1 = TypeVar('_T1')

class Viewable(Generic[_T1], Protocol):
    def view(self) -> _T1: ...

_T2 = TypeVar('_T2', bound=Hashable)

class HasIDLike(Generic[_T2], Protocol):
    @property
    def id(self) -> _T2: ...
    def __eq__(self, value: Self) -> bool: ...
    def __hash__(self) -> int: ...

_T3 = TypeVar('_T3', bound=Hashable)

class HasID(Generic[_T3], HasIDLike[_T3], Viewable[HasIDLike[_T3]]):
    def __init__(self, id: _T3, prefix: str) -> None: ...