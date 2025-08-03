#!/usr/bin/env python

from typing import TypeVar, Generic

from app.support import Viewable, SupportsPrettyID
from app.support.groups import BaseGroup
from .views import AKeysView, AValuesView, AItemsView

S_co = TypeVar('S_co', bound=Viewable[SupportsPrettyID], covariant=True)
T_co = TypeVar('T_co', bound=SupportsPrettyID, covariant=True)
U = TypeVar('U', str, int)

INIT_SIZE = 256

class Atomic(Generic[S_co, T_co, U],
             BaseGroup[S_co, T_co, U]):

    def __init__(self, initsize = INIT_SIZE, **kwargs):
        super().__init__(initsize)

        self.__props = kwargs
        self.__keys = AKeysView[S_co, T_co, U](self)
        self.__values = AValuesView[S_co, T_co, U](self)
        self.__items = AItemsView[S_co, T_co, U](self)

    def _props_matches(self, data: S_co):
        for name in self.__props:
            if getattr(data, name) != self.__props[name]:
                return False
        return True
    
    def _props_repr(self):
        res = '\n  '
        return res + ',\n  '.join([f'{k}={repr(v)}' for k, v in self.__props.items()])
    
    def __len__(self): return self.n_items

    def __iter__(self): return iter(self.__keys)
    
    def __contains__(self, key):
        try:
            self.get_by_id(key)
            return True
        except ValueError:
            return False
    
    def __getitem__(self, key): return self.get_by_id(key)
    
    def add(self, data: S_co):
        if not self._props_matches(data):
            msg = 'Contents of this group must have the following properties:'
            msg += self._props_repr()
            raise ValueError(msg)
        super().add(data)

    def remove(self, item_id):
        return super().remove(item_id)
    
    def keys(self): return self.__keys

    def values(self): return self.__values

    def items(self): return self.__items