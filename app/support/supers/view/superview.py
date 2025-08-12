#!/usr/bin/env python

from typing import TypeVar, Generic

T = TypeVar('T')

def copy_link_func(name):
    def func(slf, *args, **kwargs):
        lnk = object.__getattribute__(slf, '_SuperView__link')
        lnk_func = getattr(lnk, name)
        if hasattr(lnk_func, '_setter_like'):
            cls = type(slf)
            raise TypeError(f'Objects of type \'{cls.__name__}\' cannot call methods that mutate the objects they view.')
        return getattr(lnk, name)(*args, **kwargs)
    return func

class SuperView(Generic[T]):

    def __init_subclass__(cls, funcs = [], dunders = [], attrs = [],
                          vfuncs = [], vdunds = [], vattrs = []):
        super().__init_subclass__()

        to_dund = lambda name: f'__{name}__'
        dunders = list(map(to_dund, dunders))
        vdunds = list(map(to_dund, vdunds))

        for name in funcs + dunders:
            setattr(cls, name, copy_link_func(name))

        cls._viewed_funcs = funcs + dunders
        cls._viewed_attrs = attrs
        cls._self_funcs = vfuncs + vdunds
        cls._self_attrs = vattrs

    def __init__(self, link: T):
        object.__setattr__(self, '_SuperView__link', link)

    def __getattribute__(self, name):
        if name in ('_SuperView__link', '_viewed_funcs', '_viewed_attrs', '_self_attrs'):
            return object.__getattribute__(self, name)
            
        link = object.__getattribute__(self, '_SuperView__link')
        funcs = object.__getattribute__(self, '_viewed_funcs')
        attrs = object.__getattribute__(self, '_viewed_attrs')
        vfuncs = object.__getattribute__(self, '_self_funcs')
        vattrs = object.__getattribute__(self, '_self_attrs')

        if name in funcs or name in vfuncs or name in vattrs:
            return object.__getattribute__(self, name)
        if name in attrs:
            return getattr(link, name)

    def __setattr__(self, name, value):
        attrs = self._viewed_attrs
        funcs = self._viewed_funcs
        vfuncs = self._self_funcs
        vattrs = self._self_attrs

        cls = type(self)

        if name in attrs:
            raise AttributeError(f'\'{name}\' is a viewed attribute on another object.')
        if name in funcs or name in vfuncs:
            raise AttributeError(f'\'{name}\' is bound to a method and cannot be reassigned.')
        if name not in vattrs:
            raise AttributeError(f'Type \'{cls.__name__}\' has no attribute \'{name}\'.')

        object.__setattr__(self, name, value)