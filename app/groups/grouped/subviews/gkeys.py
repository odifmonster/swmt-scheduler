#!/usr/bin/env python

from typing import TypeVar, TypeVarTuple, Generic, Protocol, Generator, Hashable

from app.support import SuperView
from app.groups import DataView

T = TypeVar('T', bound=Hashable)
U = TypeVar('U', bound=Hashable)
Us = TypeVarTuple('Us')

class _GLike(Protocol[T, U]):
    @property
    def depth(self) -> int: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Generator[U]: ...
    def __contains__(self, key: U) -> bool: ...
    def __getitem__(self, key: U | tuple) -> '_GLike[T] | DataView[T]': ...

class GKeys(Generic[T, U, *Us], SuperView[_GLike[T, U]]):

    def __init_subclass__(cls):
        super().__init_subclass__(dunders=['len'], vdunds=['iter','contains'])

    def _iter_tups(self, cur_key: tuple):
        lnk: _GLike[T, U] = self._link

        if len(cur_key) == lnk.depth:
            yield cur_key
            return
        
        sub_grp = lnk[cur_key]
        for x in sub_grp:
            sub_gen = self._iter_tups((*cur_key, x))
            yield from sub_gen
    
    def __iter__(self):
        yield from self._iter_tups(tuple())

    def __contains__(self, key):
        try:
            _ = self._link[key]
            return True
        except:
            return False