#!/usr/bin/env python

from typing import TypeVar, Generic, Unpack, Hashable

from app.support import SuperImmut, SuperView, Viewable, setter_like
from ..data import DataView, Data
from .helpers import Atom, _match_props, _repr_props

T = TypeVar('T', bound=Hashable)
U = TypeVar('U', bound=Hashable)

class GroupedView(Generic[T, U], SuperView['Grouped[T, U]']):
    
    def __init_subclass__(cls):
        super().__init_subclass__(funcs=['make_atom','make_group','add','remove'],
                                  dunders=['repr','len','iter','contains','getitem'],
                                  attrs=['depth'])

class Grouped(Generic[T, U], Viewable[GroupedView[T, U]], SuperImmut):

    def __init_subclass__(cls):
        privs = map(lambda n: f'_Grouped__{n}', ['unbound', 'props', 'groups', 'view'])
        privs = tuple(privs)
        super().__init_subclass__(priv_attrs=privs,
                                  frozen=('_Grouped__unbound','_Grouped__props','_Grouped__view'))

    def __init__(self, view: GroupedView[T, U], *args: Unpack[tuple[str, ...]], **kwargs):
        aset = set(args)
        if not kwargs.keys().isdisjoint(aset):
            props = ', '.join([repr(x) for x in aset & kwargs.keys()])
            raise ValueError('Unbound properties ' + props + ' cannot be bound to values.')
        
        SuperImmut.__init__(self, priv={'_Grouped__view': view,
                                        '_Grouped__unbound': args,
                                        '_Grouped__props': kwargs,
                                        '_Grouped__groups': {}})

    @property
    def depth(self):
        return len(self.__unbound)
    
    def __repr__(self):
        contents = []

        if self.depth == 1:
            for val in self.__groups.values():
                vrep = repr(val)
                if not vrep: continue
                contents.append('  ' + vrep)
        else:
            max_k = max(map(lambda k: len(repr(k)), self.__groups.keys()))
            key_prefix = ' '*(max_k+4)

            for key, val in self.__groups.items():
                krep = repr(key)
                vrep = repr(val)
                if not vrep: continue

                vrep_start, *vrep_lines = vrep.split('\n')

                gap = ' '*(max_k-len(krep)+1)
                item_start = '  '+krep+':'+gap+vrep_start
                item_lines = list(map(lambda l: key_prefix+l, vrep_lines))

                contents.append('\n'.join([item_start]+item_lines))
        
        if not contents:
            return ''
        return 'grouped({\n'+'\n'.join(contents)+'\n})'
    
    def __len__(self):
        return sum(map(lambda v: len(v) > 0, self.__groups.values()))
    
    def __iter__(self):
        for key in self.__groups:
            if len(self.__groups[key]) > 0:
                yield key

    def __contains__(self, key):
        return key in self.__groups and len(self.__groups[key]) > 0
    
    def __getitem__(self, key):
        if not type(key) is tuple:
            key = (key,)
        
        if len(key) == 0:
            return self.view()

        kitems = ', '.join([repr(x) for x in key])

        if key[0] not in self:
            raise KeyError(f'Object does not contain key ({kitems}).')
        
        try:
            return self.__groups[key[0]][key[1:]]
        except ValueError:
            raise ValueError(f'{len(key)}-dimension key incompatible with {self.depth}-dimension object.')
        except KeyError:
            raise KeyError(f'Object does not contain key ({kitems}).')
    
    def make_atom(self, data: Data[T], *args: Unpack[tuple[str, ...]]) -> Atom[Data[T]]:
        return Atom[Data[T]](data, *args)
    
    def make_group(self, data: Data[T], prev_props: dict[str]) -> 'Grouped[T] | Atom[T]':
        raise NotImplementedError()
    
    @setter_like
    def add(self, data: Data[T]) -> None:
        if not _match_props(self.__props, data):
            msg = 'Data in this object must share the following properties:\n'
            msg += _repr_props(self.__props)
            raise ValueError(msg)
        
        subprop: U = getattr(data, self.__unbound[0])
        if not subprop in self.__groups:
            self.__groups[subprop] = self.make_group(data, self.__props)
        self.__groups[subprop].add(data)
    
    @setter_like
    def remove(self, dview: DataView[T]) -> Data[T]:
        subprop: U = getattr(dview, self.__unbound[0])
        if not subprop in self.__groups:
            raise ValueError(f'Object does not contain data with property {self.__unbound[0]}={repr(subprop)}.')
        
        return self.__groups[subprop].remove(dview)
    
    def view(self):
        return self.__view