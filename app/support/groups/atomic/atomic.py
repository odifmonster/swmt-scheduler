#!/usr/bin/env python

from typing import TypeVar, Generic, Any
from abc import abstractmethod

from app.support import Viewable, HasID
from ..base_group import BaseGroup

S = TypeVar('S', bound=Viewable[HasID])
T = TypeVar('T', bound=HasID)
U = TypeVar('U', str, int)

INIT_SIZE = 256

class Atomic(Generic[S, T, U], BaseGroup[S, T, U]):

    def __init__(self, initsize = INIT_SIZE, **kwargs):
        BaseGroup[S, T, U].__init__(self, initsize)

        self.__props = kwargs
    
    def __contains__(self, value: U):
        return self._contains_id(value)
    
    def __iter__(self):
        return self.iter_items()
    
    def __len__(self):
        return self.n_items

    @abstractmethod
    def get_props(self, value: S) -> dict[str, Any]:
        raise NotImplementedError()
    
    def add(self, value: S):
        val_props = self.get_props(value)
        for prop in self.__props:
            if self.__props[prop] != val_props[prop]:
                raise ValueError(f'Object (id=\'{str(value)}\') does not match properties of this group.')
        
        BaseGroup[S, T, U].add(self, value)
    
    def remove(self, item_id: U):
        return BaseGroup[S, T, U].remove(self, item_id)