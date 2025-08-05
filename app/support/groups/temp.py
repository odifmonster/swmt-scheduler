#!/usr/bin/env python

from typing import Literal, Protocol, Unpack, Iterator

from app.support import PrettyArgsOpt, SuperView, Viewable
from app.support.groups import AtomLike

Empty = tuple[()]

class DataArgsOpt(PrettyArgsOpt, total=False):
    kind: Literal['object', 'key', 'value']

class DataArgs(DataArgsOpt, total=True):

    @classmethod
    def create(cls, kind = 'value', maxlen = 60, maxlines = 1) -> 'DataArgs':
        return cls(kind=kind, maxlen=maxlen, maxlines=maxlines)

class DataLike(AtomLike[str, DataArgsOpt], Protocol):

    @property
    def _prefix(self) -> str:
        return 'DATA'

    @property
    def id(self) -> str:
        raise NotImplementedError()
    
    @property
    def master(self) -> str:
        raise NotImplementedError()
    
    @property
    def color(self) -> str:
        raise NotImplementedError()
    
    @property
    def value(self) -> int:
        raise NotImplementedError()
    
    def _validate_key(self, key) -> Empty:
        if not type(key) is tuple:
            raise KeyError(f'Expected \'key\' type \'tuple\', got \'{type(key)}\'.')
        if len(key) > 0:
            raise KeyError('DataLike only accepts empty tuples as keys.')
        return key
    
    def __getitem__(self, key) -> 'DataLike':
        raise NotImplementedError()
    
    def __iter__(self) -> 'Iterator[DataLike]':
        raise NotImplementedError()
    
    def inc(self) -> None:
        raise NotImplementedError()
    
    def pretty(self, **kwargs: Unpack[DataArgsOpt]):
        opts = self.validate_args(kwargs)
        opts = DataArgs.create(**opts)

        if opts['kind'] == 'object':
            return f'<{self._prefix}: id={repr(self.id)}>'
        if opts['kind'] == 'key':
            return repr(self.id)
        return f'{self._prefix}({self.master}-{self.color})={self.value}'

class DataView(DataLike,
               SuperView[DataLike],
               no_access=['inc'],
               overrides=['__getitem__', '__iter__']):
    
    def __getitem__(self, key):
        self._validate_key(key)
        return self
    
    def __iter__(self):
        yield self

class Data(DataLike, Viewable[DataView]):

    def __init__(self, id: str, master: str, color: str, value: int):
        self.__id = id
        self.__master = master
        self.__color = color
        self.__value = value
        self.__view = DataView(self)

    @property
    def id(self):
        return self.__id
    
    @property
    def master(self):
        return self.__master
    
    @property
    def color(self):
        return self.__color
    @color.setter
    def color(self, new: str):
        self.__color = new

    @property
    def value(self):
        return self.__value
    
    def __getitem__(self, key):
        self._validate_key(key)
        return self.__view
    
    def __iter__(self):
        yield self.__view
    
    def inc(self):
        self.__value += 1

    def view(self):
        return self.__view