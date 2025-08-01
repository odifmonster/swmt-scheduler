#!/usr/bin/env python

from typing import TypeVar, Generic, Hashable, Callable
from collections.abc import Collection

from app.support import HasIDLike, HasID
from app.support.groups import BaseGroup

S = TypeVar('S', bound=HasIDLike)
T = TypeVar('T', bound=HasID)
U = TypeVar('U', bound=Hashable)

INIT_SIZE = 256

class Atomic(Generic[S, T, U], Collection[S], BaseGroup[S, T, U]):

    def __init__(self, match_props: Callable[[T], bool], init_size: int = INIT_SIZE):
        Generic.__init__(self, lambda _: Atomic)
        Collection.__init__(self)
        BaseGroup.__init__(self, init_size)

        self.__match_props: Callable[[T], bool] = match_props

    def __contains__(self, x: S):
        return self.contains_id(x.id)
    
    def __iter__(self):
        return self.iter_items()
    
    def __len__(self):
        return self.n_items
    
    def add(self, value: T):
        if not self.__match_props(value):
            raise ValueError(f'Object (id={str(value.id)}) does not match properties set for this group.')
        
        BaseGroup.add(self, value)

    def remove(self, item_id: U):
        return BaseGroup.remove(self, item_id)