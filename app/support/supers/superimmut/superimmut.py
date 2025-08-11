#!/usr/bin/env python

from typing import Any

class SuperImmut:

    __slots__ = ()
    _defaults = {}

    def __init_subclass__(cls, attrs: list[str], defaults: dict[str, Any]):
        super().__init_subclass__()

        args_set = set(attrs)
        if len(args_set) < len(attrs):
            raise ValueError('Cannot have duplicate attributes.')
        
        cls.__slots__ = tuple(attrs)
        for k, v in defaults.items():
            if k not in cls.__slots__:
                raise ValueError(f'Cannot assign default value to non-declared attribute {repr(k)}')
            cls._defaults[k] = v
    
    def __init__(self, **kwargs):
        names_set = self._defaults.keys() | kwargs.keys()
        if names_set != set(self.__slots__):
            extra = names_set - set(self.__slots__)
            missing = set(self.__slots__) - names_set
            if len(extra) > 0:
                raise AttributeError('Unexpected attributes: ' + ','.join([repr(x) for x in extra]))
            if len(missing) > 0:
                raise AttributeError('Missing attributes: ' + ', '.join([repr(x) for x in missing]))
            
        for name in type(self)._defaults:
            super(SuperImmut, self).__setattr__(name, self._defaults[name])

        for name, val in kwargs.items():
            super(SuperImmut, self).__setattr__(name, val)
    
    def __setattr__(self, name, value):
        raise AttributeError(f'{type(self)} is immutable.')
    
    def __repr__(self):
        cls_str = repr(type(self))
        cls_str = cls_str[1:-1]
        _, cls_abs_name = cls_str.split()
        cls_abs_name = cls_abs_name[1:-1]
        cls_name = cls_abs_name.split('.')[-1]
        comps = [f'{name}={repr(getattr(self, name))}' for name in self.__slots__]
        return '<' + cls_name + ' ' + ', '.join(comps) + '>'