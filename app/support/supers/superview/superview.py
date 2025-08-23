#!/usr/bin/env python

def _copy_link_func(name: str):
    def func(slf, *args, **kwargs):
        lnk = object.__getattribute__(slf, '_link')
        lnk_func = getattr(lnk, name)
        if hasattr(lnk_func, '_setter_like') and lnk_func._setter_like == 1:
            cls = type(slf)
            raise RuntimeError(f'\'{cls.__name__}\' objects cannot call methods that mutate the objects they view')
        return lnk_func(*args, **kwargs)
    return func

class SuperView[T]:

    def __init_subclass__(cls, attrs: tuple[str, ...] = tuple(), funcs: tuple[str, ...] = tuple(),
                          dunders: tuple[str, ...] = tuple()):
        super().__init_subclass__()
        cls._attrs = attrs
        cls._funcs = funcs
        cls._dunders = tuple(map(lambda n: f'__{n}__', dunders))

        for name in cls._funcs + cls._dunders:
            setattr(cls, name, _copy_link_func(name))
    
    def __init__(self, link: T):
        super(SuperView, self).__setattr__('_link', link)
    
    def __getattribute__(self, name: str):
        if name in ('_attrs', '_funcs', '_dunders', '_link'):
            return super(SuperView, self).__getattribute__(name)
        
        lnk = super(SuperView, self).__getattribute__('_link')
        attrs = super(SuperView, self).__getattribute__('_attrs')

        if name in attrs:
            return getattr(lnk, name)
        return super(SuperView, self).__getattribute__(name)
    
    def __setattr__(self, name: str, value):
        if name in type(self)._attrs:
            raise AttributeError(f'\'{name}\' is a viewed attribute on another object')
        super(SuperView, self).__setattr__(name, value)