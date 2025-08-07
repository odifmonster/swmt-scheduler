#!/usr/bin/env python

from typing import TypeVar, TypeVarTuple, Generic, Protocol, Hashable, \
    Unpack
from abc import abstractmethod

from app.support import PrettyArgsOpt, SuperView
from app.support.groups import ValueLike

T = TypeVar('T', str, int)
T_co = TypeVar('T_co', bound=PrettyArgsOpt, covariant=True)
U = TypeVar('U', bound=Hashable)
Us = TypeVarTuple('Us')

class GroupedArgs(PrettyArgsOpt, total=True):

    @classmethod
    def create(cls, maxlen = 75, maxlines = 10):
        return cls(maxlen=maxlen, maxlines=maxlines)

class GroupedLike(Generic[T, T_co, U, *Us],
                  ValueLike[T, PrettyArgsOpt, T_co, U, *Us],
                  Protocol):
    
    @property
    @abstractmethod
    def _depth(self):
        raise NotImplementedError()
    
    @abstractmethod
    def __len__(self):
        raise NotImplementedError()
    
    @abstractmethod
    def __iter__(self):
        raise NotImplementedError()
    
    @abstractmethod
    def __contains__(self, key):
        raise NotImplementedError()
    
    @abstractmethod
    def __getitem__(self, key):
        raise NotImplementedError()
    
    @abstractmethod
    def add(self, data):
        raise NotImplementedError()
    
    @abstractmethod
    def remove(self, id):
        raise NotImplementedError()
    
    def pretty(self, **kwargs: Unpack[PrettyArgsOpt]):
        if len(self) == 0:
            return ''
        
        opts = self.validate_args(kwargs)
        opts = GroupedArgs.create(**opts)

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

class GroupedView(Generic[T, T_co, U, *Us],
                  SuperView[GroupedLike[T, T_co, U, *Us]],
                  no_access=['add','remove'],
                  overrides=[],
                  dunders=['len','iter','contains','getitem']):
    pass