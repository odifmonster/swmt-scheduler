#!/usr/bin/env python

from typing import TypeVar, Generic, Unpack, Hashable

from ..data import Data

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
        self.groups: dict[U, Grouped[T] | Data[T] | None] = {}

    @property
    def depth(self):
        return len(self.unbound)
    
    def _match_props(self, data: Data[T]) -> bool:
        return all(map(lambda x: x[1] == getattr(data, x[0]), self.props.items()))
    
    def _repr_props(self):
        return '\n'.join(map(lambda x: f'  {x[0]}={repr(x[1])}', self.props.items()))
    
    def _repr_atom(self):
        assert self.depth == 0, 'Do not call \'_repr_atom\' for Grouped objects with \'depth\' > 0.'
        if len(self.groups) == 0 or self.groups[self.props['id']] is None:
            return ''
        return repr(self.groups[self.props['id']])
    
    def _repr_list(self):
        assert self.depth == 1, 'Do not call \'_repr_list\' for Grouped objects with \'depth\' != 1.'
        
        contents = []
        for val in self.groups.values():
            vrep = repr(val)
            if not vrep: continue
            contents.append('  ' + vrep)
        
        if not contents: return ''
        return 'grouped({\n' + ',\n'.join(contents) + '\n})'

    def __repr__(self):
        if self.depth == 0:
            return self._repr_atom()
        if self.depth == 1:
            return self._repr_list()
        
        contents = []
        max_k = max(map(lambda k: len(repr(k)), self.groups.keys()))

        for key in self.groups.keys():
            vrep = repr(self.groups[key])
            if not vrep: continue

            key_prefix = ' '*(max_k+4)
            vrep_start, *vrep_lines = vrep.split('\n')

            gap = ' '*(max_k-len(repr(key))+1)
            item_start = '  '+repr(key)+':'+gap+vrep_start
            item_lines = list(map(lambda s: key_prefix+s, vrep_lines))

            item = '\n'.join([item_start] + item_lines)
            contents.append(item)
        
        if not contents: return ''
        return 'grouped({\n' + ',\n'.join(contents) + '\n})'
    
    def add(self, data: Data[T]):
        if not self._match_props(data):
            msg = 'All data in this object must have the following properties:\n'
            msg += self._repr_props()
            raise ValueError(msg)
        
        subprop: U = getattr(data, self.unbound[0])

        if self.depth == 0:
            self.groups[subprop] = data
        else:
            self.groups[subprop].add(data)
        
        data._add_to_group()