#!/usr/bin/env python

from typing import TypeVar, Generic, Unpack, Hashable

from app.support import SuperImmut
from ..data import Data, DataView

T = TypeVar('T', bound=Hashable)

def _match_props(props: dict[str], data):
    return all(map(lambda x: x[1] == getattr(data, x[0]), props.items()))

def _repr_props(props: dict[str]):
    return '\n'.join(map(lambda x: f'  {x[0]}={repr(x[1])}', props.items()))

class Atom(Generic[T], SuperImmut, priv_attrs=('props','data'), frozen=('_Atom__props',)):

    def __init__(self, data: Data[T], *args: Unpack[tuple[str, ...]]):
        if 'id' not in args:
            raise ValueError('Restricted properties missing \'id\'.')
        
        props = {}
        for attr in args:
            props[attr] = getattr(data, attr)

        data._set_in_group(True)
        super().__init__(priv={'props':props, 'data':data})

    def __repr__(self):
        if self.__data is None:
            return ''
        return repr(self.__data)
    
    def __len__(self):
        return 0 if self.__data is None else 1
    
    def __iter__(self):
        if not self.__data is None:
            yield tuple()

    def __contains__(self, key):
        if self.__data is None:
            return False
        return key == tuple()
    
    def __getitem__(self, key):
        if not type(key) is tuple:
            raise TypeError(f'Unrecognized key type \'{type(key)}\'.')
        if len(key) > 0:
            raise ValueError(f'{len(key)}-dimension key incompatible with 0-dimension object.')
        if self.__data is None:
            raise KeyError(f'Object does not contain key ().')
        return self.__data.view()
    
    def is_empty(self):
        return self.__data is None

    def add(self, data: Data[T]):
        if not self.__data is None:
            return
        
        if not _match_props(self.__props, data):
            msg = 'This Atom will only accept Data with the following properties:\n'
            msg += _repr_props(self.__props)
            raise ValueError(msg)

        data._set_in_group(True)
        self.__data = data
    
    def remove(self, dview: DataView[T]) -> Data[T]:
        if self.__data is None:
            raise ValueError('Cannot remove data from empty Atom.')
        if self.__data != dview:
            raise ValueError(f'Object does not contain data with id={repr(dview.id)}.')
        
        temp = self.__data
        temp._set_in_group(False)
        self.__data = None

        return temp