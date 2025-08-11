#!/usr/bin/env python

from typing import TypeVar, TypeVarTuple, Generic, Unpack, Hashable, \
    Any

from app.support import PrettyArgsOpt, Viewable
from app.support.groups import ValueLike, DataLike, Atom
from .grouped_like import GroupedLike, GroupedView

T = TypeVar('T', str, int)
T_co = TypeVar('T_co', bound=PrettyArgsOpt, covariant=True)
U = TypeVar('U', bound=Hashable)
Us = TypeVarTuple('Us')
Data = Viewable[DataLike[T, T_co]]

class Grouped(Generic[T, T_co, U, *Us],
              GroupedLike[T, T_co, U, *Us],
              Viewable[GroupedView[T, T_co, U, *Us]]):
    
    def __init__(self,
                 *unbound: Unpack[tuple[str, ...]],
                 **props: Unpack[dict[str, Any]]):
        self.__unbound = unbound
        self.__props = props
        self.__flat_items: dict[str, Data[T, T_co]] = {}
        self.__groups: dict[U, ValueLike[T, PrettyArgsOpt, T_co, *Us]] = {}
        self.__view = GroupedView[T, T_co, U, *Us](self)
    
    @property
    def _depth(self):
        return len(self.__unbound)
    
    def _match_props(self, data: Data[T, T_co]):
        for name, val in self.__props.items():
            if getattr(data, name) != val:
                return False
        return True
    
    def _repr_props(self):
        return '\n'.join([f'    {k}={repr(v)}' for k, v in self.__props.items()])
    
    def __len__(self):
        return sum(map(lambda x: len(x.view()), self.__groups.values()))
    
    def __iter__(self):
        return iter(self.__groups)
    
    def __contains__(self, key: U):
        return key in self.__groups
    
    def __getitem__(self, key: U | tuple):
        if not type(key) is tuple:
            key = (key,)
        if len(key) > self._depth:
            raise KeyError(f'{len(key)}-dim key incompatible with {self._depth}-dim InvGroup.')
        if len(key) == 0:
            return self.__view
        return self.__groups[key[0]][key[1:]]
    
    def add(self, data: Data[T, T_co]):
        if data.view().id in self.__flat_items:
            return
        
        if not self._match_props(data):
            msg = 'Objects in this group must have properties:\n'
            msg += self._repr_props()
            raise ValueError(msg)
        
        self.__flat_items[data.view().id] = data

        subkey: T = getattr(data, self.__unbound[0])
        if not subkey in self.__groups:
            if self._depth == 1:
                self.__groups[subkey] = Atom[T, PrettyArgsOpt]()
            else:
                newprops = {k: v for k, v in self.__props.items()}
                newprops[self.__unbound[0]] = subkey
                new_ub = self.__unbound[1:]
                self.__groups[subkey] = Grouped[T, T_co, *Us](*new_ub, **newprops) # pyright: ignore[reportInvalidTypeForm]
        self.__groups[subkey].add(data)
    
    def remove(self, id: T):
        if not id in self.__flat_items:
            raise ValueError(f'Object does not contain data with id={repr(id)}.')
        
        data = self.__flat_items[id]
        del self.__flat_items[id]

        subkey: T = getattr(data, self.__unbound[0])
        subgroup = self.__groups[subkey]
        subgroup.remove(id)
        
        return data
    
    def view(self):
        return self.__view