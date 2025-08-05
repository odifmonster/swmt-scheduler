#!/usr/bin/env python

from typing import Iterator, Unpack

from app.support import ValueLike, PrettyArgsOpt
from ..temp import Data, DataView

class GroupedArgs(PrettyArgsOpt, total=True):

    @classmethod
    def create(cls, maxlen = 60, maxlines = 10) -> 'GroupedArgs':
        return cls(maxlen=maxlen, maxlines=maxlines)

class Grouped1D(ValueLike[PrettyArgsOpt, str]):

    def __init__(self, **kwargs):
        self.__groups: dict[str, Data] = {}
        self.__props = kwargs
    
    @property
    def n_items(self) -> int:
        return len(self.__groups)
    
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
    
    def __iter__(self) -> Iterator[str]:
        return iter(self.__groups)
    
    def __contains__(self, key: str) -> bool:
        return key in self.__groups
    
    def __getitem__(self, key: tuple[str]) -> DataView:
        if not type(key) is tuple:
            key = (key,)
        return self.__groups[key[0]][key[1:]]
    
    def add(self, data: Data) -> None:
        if data.view().id in self:
            return
        if not self._match_props(data):
            msg = 'Objects in this group must have these properties:\n'
            msg += self._repr_props()
            raise ValueError(msg)
        
        self.__groups[data.view().id] = data

    def remove(self, id: str) -> Data:
        if id not in self:
            raise ValueError(f'Group does not contain data with id {repr(id)}.')
        temp = self.__groups[id]
        del self.__groups[id]
        return temp
    
    def pretty(self, **kwargs: Unpack[PrettyArgsOpt]):
        opts = self.validate_args(kwargs)
        opts = GroupedArgs.create(**opts)

        lines = []
        cur_line = 'grouped({'
        prefix = ' '*len(cur_line)

        for key in self:
            krep = repr(key)
            vrep = self.__groups[key].pretty()

            vrep_lines = vrep.split('\n')
            if len(vrep_lines) > 1:
                lpad = ' '*len(krep+': ')
                new_vlines = [vrep_lines[0]] + [lpad+x for x in vrep_lines[1:]]
                cur_line += (krep + '\n'.join(new_vlines))

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
        
        lines = [lines[0]] + [prefix+x for x in lines[1:]]
        return '\n'.join(lines) + '})'