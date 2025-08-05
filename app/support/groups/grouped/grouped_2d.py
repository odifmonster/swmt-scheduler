#!/usr/bin/env python

from typing import Iterator, Unpack, Protocol

from app.support import ValueLike, PrettyArgsOpt, Viewable, SuperView
from ..temp import Data, DataView
from .grouped_1d import GroupedArgs, Grouped1D, Grouped1DView

class Grouped2DLike(ValueLike[PrettyArgsOpt, int, str], Protocol):

    @property
    def n_items(self) -> int:
        raise NotImplementedError()
    
    def _match_props(self, data: Data) -> bool:
        raise NotImplementedError()
    
    def _repr_props(self) -> str:
        raise NotImplementedError()
    
    def __len__(self) -> int:
        raise NotImplementedError()
    
    def __iter__(self) -> Iterator[int]:
        raise NotImplementedError()
    
    def __contains__(self, key: int) -> bool:
        raise NotImplementedError()
    
    def __getitem__(self, key: tuple) -> 'DataView | Grouped1DView | Grouped2DLike':
        raise NotImplementedError()
    
    def add(self, data: Data) -> None:
        raise NotImplementedError()

    def remove(self, id: str) -> Data:
        raise NotImplementedError()
    
    def pretty(self, **kwargs: Unpack[PrettyArgsOpt]):
        opts = self.validate_args(kwargs)
        opts = GroupedArgs.create(**opts)

        lines = []
        cur_line = 'grouped({'
        prefix = ' '*len(cur_line)

        for key in self:
            krep = repr(key)
            vrep = self[key].pretty()

            vrep_lines = vrep.split('\n')
            if len(vrep_lines) > 1:
                lpad = ' '*(len(krep)+2)
                new_vlines = [vrep_lines[0]] + [lpad+x for x in vrep_lines[1:]]
                cur_line += (krep + ': ' + '\n'.join(new_vlines))

                if lines: lines[-1] += ','
                lines.append(cur_line)
                cur_line = ''
                continue

            cur_item = krep + ': ' + vrep
            if not lines and len(cur_line) == len(prefix) or not cur_line:
                cur_line += cur_item
            else:
                plen = 0 if not lines else len(prefix)
                if plen + len(cur_line) + len(cur_item) + 2 > opts['maxlen']:
                    if lines: lines[-1] += ','
                    lines.append(cur_line)
                    cur_line = cur_item
                else:
                    cur_item += (', ' + cur_item)

        if cur_line:
            lines.append(cur_line)
        
        lines = [lines[0]] + [prefix+x for x in lines[1:]]
        return '\n'.join(lines) + '})'
    
class Grouped2DView(Grouped2DLike,
                    SuperView[Grouped2DLike],
                    no_access=['_match_props', '_repr_props', 'add', 'remove'],
                    overrides=[]):
    pass

class Grouped2D(Grouped2DLike, Viewable[Grouped2DView]):

    def __init__(self, **kwargs):
        self.__flat_items: dict[str, Data] = {}
        self.__groups: dict[int, Grouped1D] = {}
        self.__props = kwargs
        self.__unbound = ('value', 'id')
        self.__view = Grouped2DView(self)

    @property
    def n_items(self) -> int:
        return sum(map(lambda k: self.__groups[k].n_items, self.__groups))
    
    def _match_props(self, data: Data) -> bool:
        for name, val in self.__props.items():
            if getattr(data, name) != val:
                return False
        return True
    
    def _repr_props(self) -> str:
        items = [f'    {k}={repr(v)}' for k, v in self.__props.items()]
        return '\n'.join(items)
    
    def __len__(self) -> int:
        return len(self.__groups)
    
    def __iter__(self) -> Iterator[int]:
        return iter(self.__groups)
    
    def __contains__(self, key: int) -> bool:
        return key in self.__groups
    
    def __getitem__(self, key):
        if not type(key) is tuple:
            key = (key,)
        if len(key) > len(self.__unbound):
            raise KeyError(f'Index length of {len(key)} exceeds number of axes ({len(self.__unbound)}).')
        if len(key) == 0:
            return self.__view
        return self.__groups[key[0]][key[1:]]
    
    def add(self, data: Data):
        if data.view().id in self.__flat_items:
            return
        if not self._match_props(data):
            msg = 'Objects in this group must have these properties:\n'
            msg += self._repr_props()
            raise ValueError(msg)
        
        group_key = getattr(data, self.__unbound[0])
        if not group_key in self.__groups:
            sub_props = { k: v for k,v in self.__props.items() }
            sub_props[self.__unbound[0]] = group_key
            self.__groups[group_key] = Grouped1D(**sub_props)
        
        self.__groups[group_key].add(data)
        self.__flat_items[data.view().id] = data

    def remove(self, id: str) -> Data:
        if id not in self.__flat_items:
            raise ValueError(f'Group does not contain data with id {repr(id)}.')
        
        temp = self.__flat_items[id]
        group_key = getattr(temp, self.__unbound[0])
        self.__groups[group_key].remove(id)
        del self.__flat_items[id]
        return temp
    
    def view(self):
        return self.__view