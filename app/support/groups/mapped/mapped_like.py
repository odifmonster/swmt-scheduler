#!/usr/bin/env python

from typing import Protocol, Iterator, TypeVar, Generic, Any

from app.support import SuperView, SupportsPretty, PrettyArgsOpt, Viewable, \
    SupportsPrettyID

class MPrettyArgsOpt(PrettyArgsOpt, total=False):
    lpad: str

class MPrettyArgs(MPrettyArgsOpt, total=True):

    @classmethod
    def create(cls, maxlen = 60, maxlines = 8, lpad = ''):
        return cls(maxlen=maxlen, maxlines=maxlines, lpad=lpad)

T1 = TypeVar('T1', str, int)
U1_co = TypeVar('U1_co', bound=PrettyArgsOpt, covariant=True)
Data = Viewable[SupportsPrettyID[T1, U1_co]]

T2 = TypeVar('T2')

class MappedLike(Generic[T1, U1_co, T2], SupportsPretty[MPrettyArgsOpt], Protocol):

    @property
    def n_items(self) -> int: raise NotImplementedError()

    def __len__(self) -> int: raise NotImplementedError()

    def __iter__(self) -> Iterator[T2]: raise NotImplementedError()

    def __contains__(self, key: T2) -> bool: raise NotImplementedError()

    def __getitem__(self, key: T2) -> 'MappedView[T1, U1_co, Any]': raise NotImplementedError()

    def add(self, data: Data[T1, U1_co]) -> None: raise NotImplementedError()

    def remove(self, id: T1) -> Data[T1, U1_co]: raise NotImplementedError()

    def pretty(self, **kwargs): raise NotImplementedError()

class MappedView(Generic[T1, U1_co, T2],
                 MappedLike[T1, U1_co, T2],
                 SuperView[MappedLike[T1, U1_co, T2]],
                 no_access=['add', 'remove']):
    pass