#!/usr/bin/env python

from typing import TypeVar, TypeVarTuple, Generic, Protocol, Unpack, \
    Iterator, Any

from app.support import Viewable, SuperView, PrettyArgsOpt
from app.support.groups import ValueLike, Atom
from item import Item, ItemView, ItemArgsOpt

T = TypeVar('T')
Ts = TypeVarTuple('Ts')
InvValue = ValueLike[str, PrettyArgsOpt, ItemArgsOpt, *Ts]

class InvArgs(PrettyArgsOpt, total=True):

    @classmethod
    def create(cls, maxlen = 75, maxlines = 10):
        return cls(maxlen=maxlen, maxlines=maxlines)
    
class InvGroupLike(Generic[T, *Ts],
                   ValueLike[str, PrettyArgsOpt, ItemArgsOpt, T, *Ts],
                   Protocol):
    
    @property
    def _depth(self) -> int:
        raise NotImplementedError()
    
    def _match_props(self, data: Item) -> bool:
        raise NotImplementedError()
    
    def _repr_props(self) -> str:
        raise NotImplementedError()
    
    def __len__(self) -> int:
        raise NotImplementedError()
    
    def __iter__(self) -> Iterator[T]:
        raise NotImplementedError()
    
    def __contains__(self, key: T) -> bool:
        raise NotImplementedError()
    
    def __getitem__(self, key: T | tuple) -> 'ItemView | InvGroupView':
        raise NotImplementedError()
    
    def add(self, data: Item) -> None:
        raise NotImplementedError()
    
    def remove(self, id: str) -> Item:
        raise NotImplementedError()
    
    def pretty(self, **kwargs: Unpack[PrettyArgsOpt]):
        if len(self) == 0:
            return ''
        
        opts = self.validate_args(kwargs)
        opts = InvArgs.create(**opts)

        lines = ['grouped({']
        
        if self._depth == 1:
            cur_line = '  '

            for key in self:
                vrep = self[key].pretty()

                if len(cur_line) == 2:
                    cur_line += vrep
                elif len(cur_line) + len(vrep) + 2 > opts['maxlen']:
                    if len(lines) > 1:
                        lines[-1] += ','
                    lines.append(cur_line)
                    cur_line = '  ' + vrep
                else:
                    cur_line += (', ' + vrep)
            
            lines.append(cur_line)
            lines.append('})')
        else:
            for key in self:
                krep = repr(key)
                vrep_lines = self[key].pretty().split('\n')

                vrep_lines[0] = krep + ': ' + vrep_lines[0]
                vrep_lines = ['  '+x for x in vrep_lines]
                lines.append('\n'.join(vrep_lines))
            lines.append('})')
        
        return '\n'.join(lines)

class InvGroupView(Generic[T, *Ts], InvGroupLike[T, *Ts],
                   SuperView[InvGroupLike[T, *Ts]],
                   no_access=['add', 'remove', '_match_props', '_repr_props'],
                   overrides=['']):
    pass

class InvGroup(Generic[T, *Ts], InvGroupLike[T, *Ts],
               Viewable[InvGroupView[T, *Ts]]):
    
    def __init__(self,
                 *unbound: Unpack[tuple[str, ...]],
                 **props: dict[str, Any]):
        self.__unbound = unbound
        self.__props = props
        self.__flat_items: dict[str, Item] = {}
        self.__groups: dict[T, InvValue[*Ts]] = {}
        self.__view = InvGroupView[T, *Ts](self)

    @property
    def _depth(self):
        return len(self.__unbound)
    
    def _match_props(self, data):
        for name, val in self.__props.items():
            if getattr(data, name) != val:
                return False
        return True
    
    def _repr_props(self):
        return '\n'.join([f'    {k}={repr(v)}' for k, v in self.__props.items()])
    
    def __len__(self):
        return sum(map(lambda x: len(x), self.__groups.values()))
    
    def __iter__(self):
        return iter(self.__groups)
    
    def __contains__(self, key: T):
        return key in self.__groups
    
    def __getitem__(self, key: T | tuple):
        if not type(key) is tuple:
            key = (key,)
        if len(key) > self._depth:
            raise KeyError(f'{len(key)}-dim key incompatible with {self._depth}-dim InvGroup.')
        if len(key) == 0:
            return self.__view
        return self.__groups[key[0]][key[1:]]
    
    def add(self, data):
        if data.id in self.__flat_items:
            return
        
        if not self._match_props(data):
            msg = 'Objects in this group must have properties:\n'
            msg += self._repr_props()
            raise ValueError(msg)
        
        self.__flat_items[data.id] = data

        subkey: T = getattr(data, self.__unbound[0])
        if not subkey in self.__groups:
            if self._depth == 1:
                self.__groups[subkey] = Atom[str, ItemArgsOpt]()
            else:
                newprops = {k: v for k, v in self.__props.items()}
                newprops[self.__unbound[0]] = subkey
                new_ub = self.__unbound[1:]
                self.__groups[subkey] = InvGroup[*Ts](*new_ub, **newprops) # pyright: ignore[reportInvalidTypeForm]
        self.__groups[subkey].add(data)
    
    def remove(self, id: str):
        if not id in self.__flat_items:
            raise ValueError(f'Object does not contain data with id={repr(id)}.')
        
        data = self.__flat_items[id]
        del self.__flat_items[id]

        subkey: T = getattr(data, self.__unbound[0])
        subgroup = self.__groups[subkey]
        subgroup.remove(id)
        if len(subgroup) == 0:
            del self.__groups[subkey]
        
        return data
    
    def view(self):
        return self.__view