#!/usr/bin/env python

from typing import Hashable, Unpack

from ..supers import SuperImmut, SuperView, setter_like
from .atom import Atom
from .data import Data, DataView, match_props, repr_props

class Grouped[T: Hashable, U: Hashable](SuperImmut):
    
    def __init_subclass__(cls):
        privs = tuple(map(lambda a: f'_Grouped__{a}', ['ids_map','props','unbound','groups','view']))
        frozen = tuple(map(lambda a: f'_Grouped__{a}', ['unbound','props','view']))
        super().__init_subclass__(attrs=('n_items','depth')+privs, frozen=frozen)
    
    def __init__(self, view: 'GroupedView[T, U]', *args: Unpack[tuple[str, ...]], **kwargs):
        if not set(args).isdisjoint(kwargs.keys()):
            inter = set(args).intersection(kwargs.keys())
            inter = list(inter)
            msg = 'Unbound attributes '
            msg += ', '.join([repr(x) for x in inter])
            msg += ' bound to values '
            msg += ', '.join([repr(kwargs[x]) for x in inter])
            raise ValueError(msg)
        
        SuperImmut.__init__(self, _Grouped__ids_map={}, _Grouped__props=kwargs,
                            _Grouped__unbound=args, _Grouped__groups={}, _Grouped__view=view)
    
    def __len__(self):
        groups: dict[U, 'Grouped[T] | Atom[T]'] = self.__groups
        return sum(map(lambda grp: 0 if len(grp) == 0 else 1, groups.values()))
    
    def __iter__(self):
        groups: dict[U, 'Grouped[T] | Atom[T]'] = self.__groups
        for key in groups:
            if len(groups[key]) > 0:
                yield key

    def __contains__(self, key):
        groups: dict[U, 'Grouped[T] | Atom[T]'] = self.__groups
        return key in groups and len(groups[key]) > 0
    
    def __getitem__(self, key):
        if not type(key) is tuple:
            key = (key,)
        if len(key) == 0:
            return self.view()
        if key[0] not in self.__groups or len(self.__groups[key[0]]) == 0:
            raise KeyError(f'Object does not contain items with {self.__unbound[0]}={repr(key[0])}')
        try:
            return self.__groups[key[0]][key[1:]]
        except KeyError as err:
            if '-dim key incompatible' in str(err):
                raise KeyError(f'{len(key)}-dim key incompatible with {self.depth}-dim Grouped object')
            msg = 'Object does not contain items with '
            msg += ', '.join([f'{self.__unbound[i]}={repr(key[i])}' for i in range(len(key))])
            raise KeyError(msg)

    @property
    def depth(self):
        return len(self.__unbound)
    
    @property
    def n_items(self):
        groups: dict[U, 'Grouped[T] | Atom[T]'] = self.__groups
        return sum(map(lambda grp: grp.n_items, groups.values()))
    
    def make_group(self, data: Data[T], **kwargs) -> 'Grouped[T] | Atom[T]':
        raise NotImplementedError()
    
    def get(self, id: T) -> DataView[T]:
        groups: dict[U, 'Grouped[T] | Atom[T]'] = self.__groups
        id_map: dict[T, U] = self.__ids_map

        if id not in id_map:
            raise ValueError(f'Object does not contain data with id={repr(id)}')
        return groups[id_map[id]].get(id)
    
    @setter_like
    def add(self, data: Data[T]):
        if not match_props(data, self.__props):
            msg = 'All data in this group must have the following properties:\n'
            msg += repr_props(self.__props)
            raise ValueError(msg)
        
        groups: dict[U, 'Grouped[T] | Atom[T]'] = self.__groups
        subkey: U = getattr(data, self.__unbound[0])
        if subkey not in groups:
            groups[subkey] = self.make_group(data, **self.__props)
        
        groups[subkey].add(data)
        self.__ids_map[data.id] = subkey

    @setter_like
    def remove(self, dview: DataView[T]):
        groups: dict[U, 'Grouped[T] | Atom[T]'] = self.__groups
        subkey: U = getattr(dview, self.__unbound[0])
        if subkey not in groups or len(groups[subkey]) == 0:
            raise ValueError(f'Object does not contain data with {self.__unbound[0]}={repr(subkey)}')
        
        ret = groups[subkey].remove(dview)
        del self.__ids_map[dview.id]
        return ret
    
    def view(self) -> 'GroupedView[T, U]':
        return self.__view

class GroupedView[T: Hashable, U: Hashable](SuperView[Grouped[T, U]]):
    
    def __init_subclass__(cls):
        super().__init_subclass__(attrs=('depth','n_items'),
                                  funcs=('make_group','get','add','remove'),
                                  dunders=('len','iter','contains','getitem'))