#!/usr/bin/env python

from typing import TypeVar, Generic

T_co = TypeVar('T_co', covariant=True)

def make_dunder(name):
    def func(slf, *args, **kwargs):
        lnk = getattr(slf, '_SuperView__link')
        return getattr(lnk, name)(*args, **kwargs)
    return func

class SuperView(Generic[T_co]):

    _no_access = []
    _overrides = []
    _dunders = []

    def __init_subclass__(cls, no_access, overrides, dunders):
        super().__init_subclass__()
        cls._no_access = [x for x in no_access]
        cls._overrides = [x for x in overrides]
        for dund in dunders:
            name = f'__{dund}__'
            setattr(cls, name, make_dunder(name))

    def __init__(self, link: T_co):
        self.__link = link

    def __getattribute__(self, name):
        if name == '_SuperView__link':
            return object.__getattribute__(self, name)
        elif name in type(self)._no_access:
            raise AttributeError(f'\'{str(type(self))}\' object has no attribute \'{name}\'.')
        elif name in type(self)._overrides:
            return getattr(self, name)
        return getattr(self.__link, name)
    
    def __setattr__(self, name, value):
        if name == '_SuperView__link':
            object.__setattr__(self, name, value)
        else:
            raise AttributeError('View-type objects cannot set values.')