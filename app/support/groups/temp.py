#!/usr/bin/env python

from typing import Protocol, Literal, Unpack, Self

from app.support import SupportsPrettyID, Viewable, SuperView, PrettyArgsOpt

class DPrettyArgsOpt(PrettyArgsOpt, total=False):
    kind: Literal['object', 'key', 'value']

class DPrettyArgs(DPrettyArgsOpt, total=True):

    @classmethod
    def create(cls, kind = 'object', maxlen = 60, maxlines = 1) -> Self:
        return cls(kind=kind, maxlen=maxlen, maxlines=maxlines)
    
class DataLike(SupportsPrettyID[str, DPrettyArgsOpt], Protocol):

    @property
    def _prefix(self) -> str: return 'DATA'

    @property
    def id(self) -> str: raise NotImplementedError()

    @property
    def master(self) -> str: raise NotImplementedError()

    @property
    def color(self) -> str: raise NotImplementedError()

    @property
    def value(self) -> int: raise NotImplementedError()

    def __repr__(self):
        return self.pretty(kind='object')
    
    def __str__(self):
        return self.pretty(kind='value')

    def use(self, amount: int) -> None: raise NotImplementedError()

    def pretty(self, **kwargs: Unpack[DPrettyArgsOpt]):
        opts = self.validate_args(kwargs)
        opts = DPrettyArgs.create(**opts)

        if opts['kind'] == 'object':
            return self.shorten_line(f'<{self._prefix}: id=\'{self.id}\'>', **opts)
        if opts['kind'] == 'key':
            return self.shorten_line(f'\'{self.id}\'', **opts)
        
        items = map(lambda x: (x, repr(getattr(self, x))), ['master', 'color', 'value'])
        contents = ', '.join([f'{x}={y}' for x,y in items])
        return self.shorten_line(f'{self._prefix}({contents})', **opts)

class DataView(DataLike, SuperView[DataLike], no_access=['use']):
    pass

class Data(DataLike, Viewable[DataView]):

    def __init__(self, id: str, master: str, color: str, value: int):
        self.__id = id
        self.__master = master
        self.__color = color
        self.__value = value
        self.__view = DataView(self)

    @property
    def id(self): return self.__id

    @property
    def master(self): return self.__master

    @property
    def color(self): return self.__color
    @color.setter
    def color(self, new: str): self.__color = new

    @property
    def value(self): return self.__value

    def use(self, amount): self.__value -= amount

    def view(self): return self.__view