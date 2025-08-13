#!/usr/bin/env python

from typing import TypeVar, Generic, Unpack, Hashable

from ..data import DataView, Data
from .helpers import Atom, _match_props, _repr_props

T = TypeVar('T', bound=Hashable)
U = TypeVar('U', bound=Hashable)

class Grouped(Generic[T, U]):

    def __init__(self, *args: Unpack[tuple[str, ...]], **kwargs):
        aset = set(args)
        if not kwargs.keys().isdisjoint(aset):
            props = ', '.join([repr(x) for x in aset & kwargs.keys()])
            raise ValueError('Unbound properties ' + props + ' cannot be bound to values.')
        
        self.unbound = args
        self.props = kwargs
        self.groups: dict[U, Grouped[T] | Atom[T]] = {}

    @property
    def depth(self):
        return len(self.unbound)
    
    def __repr__(self):
        contents = []

        if self.depth == 1:
            for val in self.groups.values():
                vrep = repr(val)
                if not vrep: continue
                contents.append('  ' + vrep)
        else:
            max_k = max(map(lambda k: len(repr(k)), self.groups.keys()))
            key_prefix = ' '*(max_k+4)

            for key, val in self.groups.items():
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
        return sum(map(lambda v: len(v) > 0, self.groups.values()))
    
    def __iter__(self):
        for key in self.groups:
            if len(self.groups[key]) > 0:
                yield key

    def __contains__(self, key):
        return key in self.groups and len(self.groups[key]) > 0
    
    def make_atom(self, data: Data[T], *args: Unpack[tuple[str, ...]]) -> Atom[Data[T]]:
        return Atom[Data[T]](data, *args)
    
    def make_group(self, data: Data[T], prev_props: dict[str]) -> 'Grouped[T] | Atom[T]':
        raise NotImplementedError()
    
    def add(self, data: Data[T]) -> None:
        if not _match_props(self.props, data):
            msg = 'Data in this object must share the following properties:\n'
            msg += _repr_props(self.props)
            raise ValueError(msg)
        
        subprop: U = getattr(data, self.unbound[0])
        if not subprop in self.groups:
            self.groups[subprop] = self.make_group(data, self.props)
        self.groups[subprop].add(data)
    
    def remove(self, dview: DataView[T]) -> Data[T]:
        subprop: U = getattr(dview, self.unbound[0])
        if not subprop in self.groups:
            raise ValueError(f'Object does not contain data with property {self.unbound[0]}={repr(subprop)}.')
        
        return self.groups[subprop].remove(dview)