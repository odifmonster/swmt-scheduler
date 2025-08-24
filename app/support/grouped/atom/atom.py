#!/usr/bin/env python

from typing import Hashable, Unpack

from ...supers import SuperImmut
from ..data import Data, DataView, match_props, repr_props

class Atom[T: Hashable](SuperImmut, attrs=('depth','n_items'), priv_attrs=('props','data'),
                        frozen=('*props',)):

    def __init__(self, data: Data[T], *args: Unpack[tuple[str, ...]]):
        if 'id' not in args:
            raise ValueError('Restricted attributes must include \'id\'')
        
        props: dict[str] = {}
        for attr in args:
            props[attr] = getattr(data, attr)

        data._set_in_group(True)
        SuperImmut.__init__(self, priv={'props': props, 'data': data})
    
    def __len__(self):
        if self.__data is None:
            return 0
        return 1
    
    def __iter__(self):
        if len(self) == 1:
            yield tuple()
        return
    
    def __contains__(self, key):
        if len(self) == 0: return False
        if type(key) is tuple and len(key) == 0:
            return True
        return False
    
    def __getitem__(self, key):
        if not type(key) is tuple:
            raise TypeError('Keys of atoms must be tuples')
        if len(key) > 0:
            raise KeyError(f'{len(key)}-dim key incompatible with 0-dim Grouped object')
        if len(self) == 0:
            raise KeyError(f'Object does not contain key {repr(key)}')
        
        return self.__data.view()
    
    def __repr__(self):
        if len(self) == 0:
            return ''
        return repr(self.__data)
    
    @property
    def depth(self):
        return 0
    
    @property
    def n_items(self):
        return len(self)
    
    def iterkeys(self):
        if len(self) == 1:
            yield tuple()
        return
    
    def itervalues(self):
        if len(self) == 1:
            yield self.__data.view()
        return
    
    def get(self, id: T):
        if len(self) == 0 or self.__data.id != id:
            raise ValueError(f'Object does not contain data with id={repr(id)}')
        return self.__data.view()
    
    def add(self, data: Data[T]):
        if not match_props(data, self.__props):
            msg = 'All data in this atom must have the following properties:\n'
            msg += repr_props(self.__props)
            raise ValueError(msg)
        if len(self) == 1:
            return
        
        data._set_in_group(True)
        self.__data = data

    def remove(self, dview: DataView[T]):
        if len(self) == 0 or self.__data != dview:
            raise ValueError(f'Object does not contain data with id={repr(dview.id)}')
        temp = self.__data
        temp._set_in_group(False)
        self.__data = None
        return temp