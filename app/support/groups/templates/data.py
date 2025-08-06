#!/usr/bin/env python

from typing import TypeVar, Generic, Protocol

from app.support import HasID, SupportsPretty, PrettyArgsOpt

T = TypeVar('T', str, int)
T_co = TypeVar('T_co', bound=PrettyArgsOpt, covariant=True)

class DataLike(Generic[T, T_co], HasID[T], SupportsPretty[T_co],
               Protocol):
    pass