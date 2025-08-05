#!/usr/bin/env python

from typing import TypeVar, Generic, Any
from collections.abc import Set, Collection # pyright: ignore[reportShadowedImports]

from app.support import PrettyArgsOpt, Viewable, SupportsPrettyID
from app.support.groups import MappedLike

T1 = TypeVar('T1', str, int)
U1_co = TypeVar('U1_co', bound=PrettyArgsOpt)
T2 = TypeVar('T2')

DataView = SupportsPrettyID[T1, U1_co]
Data = Viewable[DataView[T1, U1_co]]
type AnyView = DataView[T1, U1_co] | MappedLike[T1, U1_co, Any]
type AnyData = Data[T1, U1_co] | MappedLike[T1, U1_co, Any]

class MViewBase(Generic[T1, U1_co, T2]):

    def __init__(self, link: MappedLike[T1, U1_co, T2]):
        self._link = link

    def __repr__(self): return 'This is a view'
    
    def __len__(self): return len(self._link)

class MKeysView(Generic[T1, U1_co, T2],
                MViewBase[T1, U1_co, T2],
                Set[T2]):
    
    def __init__(self, link: MappedLike[T1, U1_co, T2]):
        super().__init__(link)
    
    def __iter__(self):
        for key in self._link:
            yield key
    
    def __contains__(self, x: T2):
        return x in self._link
    
    def __le__(self, other: Set[T2]):
        for x in self:
            if x not in other: return False
        return True
    
class MItemsView(Generic[T1, U1_co, T2],
                 MViewBase[T1, U1_co, T2],
                 Set[T2]):
    
    def __init__(self, link: MappedLike[T1, U1_co, T2]):
        super().__init__(link)

    def __iter__(self):
        for key in self._link:
            yield (key, self._link[key])
    
    def __contains__(self, x: tuple[T2, AnyData[T1, U1_co]]):
        return x[0] in self._link
    
    def __le__(self, other: Set[tuple[T2, AnyData[T1, U1_co]]]):
        for x in self:
            if x not in other: return False
        return True

class MValuesView(Generic[T1, U1_co, T2],
                  MViewBase[T1, U1_co, T2],
                  Collection[AnyView[T1, U1_co]]):
    
    def __init__(self, link: MappedLike[T1, U1_co, T2]):
        super().__init__(link)

    def __iter__(self):
        for key in self._link:
            yield self._link[key]
    
    def __contains__(self, x: AnyData[T1, U1_co]):
        for val in self:
            if x == val:
                return True
        return False