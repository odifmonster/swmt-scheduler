#!/usr/bin/env python

from typing import ParamSpec, TypeVar, Callable

P = ParamSpec('P')
T = TypeVar('T')

def setter_like(f: Callable[P, T]) -> Callable[P, T]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return f(args, kwargs)
    setattr(wrapper, '_setter_like', 1)
    return wrapper