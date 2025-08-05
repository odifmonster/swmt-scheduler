#!/usr/bin/env python

from typing import Protocol, Iterator, TypeVar, Generic
from abc import abstractmethod

from app.support import SuperView, SupportsPretty, PrettyArgsOpt, Viewable, \
    SupportsPrettyID


class MPrettyArgs(PrettyArgsOpt, total=True):

    @classmethod
    def create(cls, maxlen = 60, maxlines = 8):
        return cls(maxlen=maxlen, maxlines=maxlines)

T1 = TypeVar('T1', str, int)
U1_co = TypeVar('U1_co', bound=PrettyArgsOpt, covariant=True)
DataView = SupportsPrettyID[T1, U1_co]
Data = Viewable[DataView[T1, U1_co]]

T2 = TypeVar('T2')

class MappedLike(Generic[T1, U1_co, T2], 
                 SupportsPretty[PrettyArgsOpt],
                 Protocol):

    @property
    @abstractmethod
    def n_items(self) -> int: raise NotImplementedError()

    @abstractmethod
    def __len__(self) -> int: raise NotImplementedError()

    @abstractmethod
    def __iter__(self) -> Iterator[T2]: raise NotImplementedError()

    @abstractmethod
    def __contains__(self, key: T2) -> bool: raise NotImplementedError()

    @abstractmethod
    def __getitem__(self, key: T2): raise NotImplementedError()

    @abstractmethod
    def __eq__(self, other: 'MappedLike[T1, U1_co, T2]'): raise NotImplementedError()

    @abstractmethod
    def add(self, data: Data[T1, U1_co]) -> None: raise NotImplementedError()

    @abstractmethod
    def remove(self, id: T1) -> Data[T1, U1_co]: raise NotImplementedError()

    @abstractmethod
    def pretty(self, **kwargs): raise NotImplementedError()

class MappedView(Generic[T1, U1_co, T2],
                 SuperView[MappedLike[T1, U1_co, T2]],
                 no_access=['add', 'remove']):
    pass