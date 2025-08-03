#!/usr/bin/env python

from typing import Unpack, TypedDict

from app.support.groups import BaseGroup
from .temp import Data, DataView

INIT_SIZE = 256

class AProps(TypedDict):
    name: str
    value: int

class Atomic(BaseGroup[Data, DataView, str]):

    def __init__(self, initsize = INIT_SIZE, **kwargs: Unpack[AProps]):
        super().__init__(initsize)

        self.__props = kwargs

    def _props_matches(self, data: Data):
        for name in self.__props:
            if getattr(data, name) != self.__props[name]:
                return False
        return True
    
    def _props_repr(self):
        res = '\n  '
        return res + ',\n  '.join([f'{k}={repr(v)}' for k, v in self.__props.items()])
    
    def __len__(self): return self.n_items
    
    def __getitem__(self, key: str): return self.get_by_id(key)
    
    def add(self, data: Data):
        if not self._props_matches(data):
            msg = 'Contents of this group must have the following properties:'
            msg += self._props_repr()
            raise ValueError(msg)
        super().add(data)

    def remove(self, item_id: str):
        return super().remove(item_id)