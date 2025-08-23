#!/usr/bin/env python

class SuperImmut:

    def __init_subclass__(cls, attrs: tuple[str, ...] = tuple(),
                          priv_attrs: tuple[str, ...] = tuple(),
                          frozen: tuple[str, ...] = tuple()):
        super().__init_subclass__()

        mangled_priv: set[str] = set()
        for a in priv_attrs:
            mangled_priv.add(f'_{cls.__name__}__{a}')
        all_attrs = set(attrs) | set(mangled_priv)

        mangled_frz: set[str] = set()
        for a in frozen:
            if a[0] == '*':
                mangled_frz.add(f'_{cls.__name__}__{a[1:]}')
            else:
                mangled_frz.add(a)
        
        if not mangled_frz.issubset(all_attrs):
            diff = mangled_frz.difference(all_attrs)
            msg = 'Frozen attributes '
            msg += ', '.join([repr(x) for x in diff])
            msg += ' not declared as part of private or public attributes'
            raise ValueError(msg)
        
        cls._attrs = tuple(all_attrs)
        cls._frozen = tuple(mangled_frz)
    
    def __init__(self, priv: dict[str] = {}, **kwargs):
        for a, val in priv.items():
            priv_name = f'_{type(self).__name__}__{a}'
            if priv_name not in type(self)._attrs:
                raise AttributeError(f'\'{type(self).__name__}\' object has no attribute \'{priv_name}\'')
            super(SuperImmut, self).__setattr__(priv_name, val)
        
        for a, val in kwargs.items():
            if a not in type(self)._attrs:
                raise AttributeError(f'\'{type(self).__name__}\' object has no attribute \'{a}\'')
            super(SuperImmut, self).__setattr__(a, val)
    
    def __setattr__(self, name: str, value):
        if name in type(self)._frozen:
            raise AttributeError(f'Attribute \'{name}\' of \'{type(self).__name__}\' object is immutable')
        super(SuperImmut, self).__setattr__(name, value)