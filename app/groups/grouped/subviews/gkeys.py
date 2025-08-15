#!/usr/bin/env python

from typing import TypeVar, TypeVarTuple, Generic, Protocol, Generator, Hashable

from app.support import SuperImmut
from app.groups import DataView

T = TypeVar('T', bound=Hashable)
U = TypeVar('U', bound=Hashable)
Us = TypeVarTuple('Us')

class _GLike(Protocol[T, U]):
    @property
    def depth(self) -> int: ...
    @property
    def n_items(self) -> int: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Generator[U]: ...
    def __contains__(self, key: U) -> bool: ...
    def __getitem__(self, key: U | tuple) -> '_GLike[T] | DataView[T]': ...

class GKeys(Generic[T, U, *Us], SuperImmut,
            priv_attrs=('group',), frozen=('_GKeys__group',)):
    
    def __init__(self, link: _GLike[T, U]):
        super().__init__(priv={'group': link})

    def _iter_tups(self, prev: tuple = tuple()):
        grp: _GLike[T, U] = self.__group
        if len(prev) == grp.depth:
            yield prev
            return
        
        subgrp: _GLike[T] = grp[prev]
        for key in subgrp:
            subgen = self._iter_tups(prev=(*prev, key))
            yield from subgen
    
    def __len__(self):
        grp: _GLike[T, U] = self.__group
        return grp.n_items
    
    def __iter__(self):
        tupgen = self._iter_tups()
        yield from tupgen

    def __contains__(self, key: tuple[U, *Us]):
        grp: _GLike[T, U] = self.__group
        try:
            _ = grp[key]
            return True
        except:
            return False