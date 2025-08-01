#!/usr/bin/env python

from typing import TypeVar, ParamSpec, Callable

P = ParamSpec('P')
T = TypeVar('T')

def setterlike(f: Callable[P, T]) -> Callable[P, T]:
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        return f(*args, **kwargs)
    setattr(inner, '_setterlike', 1)
    return inner