#!/usr/bin/env python

from typing import Any

type ArgTup = tuple[str, ...]

class SuperImmut:

    def __init_subclass__(cls, attrs: ArgTup = tuple(), priv_attrs: ArgTup = tuple(),
                          frozen: ArgTup | None = None):
        super().__init_subclass__()

        temp_pa = []
        for a in priv_attrs:
            if a[0] == '_':
                temp_pa.append(a)
            else:
                temp_pa.append(f'_{cls.__name__}__{a}')
        priv_attrs = tuple(temp_pa)
        all_attrs = set(attrs + priv_attrs)

        if frozen is None:
            frozen = attrs + priv_attrs
        frz_set = set(frozen)
        
        if not frz_set <= all_attrs:
            raise ValueError('All frozen attributes must be declared as part of \'attrs\' or \'priv_attrs\'.')

        cls._attrs = attrs
        cls._priv_attrs = priv_attrs
        cls._frozen = frozen

    def __init__(self, priv: dict[str, Any] = {}, **kwargs):
        cls = type(self)

        for name, val in priv.items():
            if name[0] != '_':
                pname = f'_{cls.__name__}__{name}'
            else:
                pname = name
            if pname not in cls._priv_attrs:
                raise AttributeError(f'Type \'{cls.__name__}\' has no private attribute \'{name}\'.')
            super(SuperImmut, self).__setattr__(pname, val)

        for name, val in kwargs.items():
            if name not in cls._attrs:
                raise AttributeError(f'Type \'{cls.__name__}\' has no public attribute \'{name}\'.')
            super(SuperImmut, self).__setattr__(name, val)

    def __setattr__(self, name, val):
        cls = type(self)

        if not (name in cls._attrs or name in cls._priv_attrs):
            raise AttributeError(f'Type \'{cls.__name__}\' has no attribute \'{name}\'.')
        if name in cls._frozen:
            raise AttributeError(f'Attribute \'{name}\' of type \'{cls.__name__}\' is immutable.')
        super(SuperImmut, self).__setattr__(name, val)