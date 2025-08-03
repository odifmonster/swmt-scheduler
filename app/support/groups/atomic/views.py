#!/usr/bin/env python

from typing import TypeVar, Generic
from collections.abc import Set

from app.support import SuperIter, Viewable, SupportsPrettyID
from app.support.groups import BaseGroup

S_co = TypeVar('S_co', bound=Viewable[SupportsPrettyID], covariant=True)
T_co = TypeVar('T_co', bound=SupportsPrettyID, covariant=True)
U = TypeVar('U', str, int)

class AMapView(Generic[S_co, T_co, U]):

    def __init__(self, link: BaseGroup[S_co, T_co, U], kind: str):
        self._link = link
        self.__kind = kind

    def __repr__(self):
        if self.__kind not in ('keys', 'values', 'items'):
            raise TypeError(f'Unknown MapView kind: \'{self.__kind}\'.')
        
        res = ''
        nxt_line = f'group_{self.__kind}(['

        for i, item in enumerate(self._link.iter_items()):
            nxt_str = ''
            if self.__kind == 'keys':
                nxt_str = item.pretty(kind='key')
            elif self.__kind == 'items':
                nxt_str = f'({item.pretty(kind='key')},{item.pretty(kind='value')})'
            else:
                nxt_str = item.pretty(kind='value')
            
            if len(nxt_line) > 0 and len(nxt_line) + len(nxt_str) > 73:
                if i > 0: nxt_line += ','
                if len(res) > 0: res += '\n'
                res += nxt_line
                nxt_line = nxt_str
            else:
                if i > 0:
                    nxt_line += ', '
                nxt_line += nxt_str
        
        nxt_line += '])'
        if len(res) > 0: res += '\n'
        res += nxt_line
        return res

class AKeysIter(Generic[T_co, U],
                SuperIter[T_co, U],
                get_val=lambda dv: dv.id):
    pass

class AItemsIter(Generic[T_co, U],
                 SuperIter[T_co, tuple[U, T_co]], 
                 get_val=lambda dv: (dv.id, dv)):
    pass

class AKeysView(Generic[S_co, T_co, U],
                Set[U],
                AMapView[S_co, T_co, U]):

    def __init__(self, link: BaseGroup[S_co, T_co, U]):
        AMapView.__init__(self, link, 'keys')

    def __len__(self): return self._link.n_items

    def __iter__(self): return AKeysIter(self._link.iter_items())

    def __contains__(self, key: U): return key in self._link

class AValuesView(Generic[S_co, T_co, U],
                  Set[T_co],
                  AMapView[S_co, T_co, U]):

    def __init__(self, link: BaseGroup[S_co, T_co, U]):
        AMapView.__init__(self, link, 'values')

    def __len__(self): return self._link.n_items

    def __iter__(self): self._link.iter_items()

    def __contains__(self, value: T_co): return value.id in self._link

class AItemsView(Generic[S_co, T_co, U],
                 Set[tuple[U, T_co]], 
                 AMapView[S_co, T_co, U]):

    def __init__(self, link: BaseGroup[S_co, T_co, U]):
        AMapView.__init__(self, link, 'items')

    def __len__(self): return self._link.n_items

    def __iter__(self): return AItemsIter(self._link.iter_items())

    def __contains__(self, item: tuple[U, S_co]):
        return item[0] in self._link