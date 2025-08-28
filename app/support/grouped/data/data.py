#!/usr/bin/env python

from typing import Hashable

from ...protocols import HasID
from ...supers import SuperImmut, SuperView

class Data[T: Hashable](HasID[T], SuperImmut):

    def __init_subclass__(cls, mod_in_group: bool, attrs: tuple[str, ...] = tuple(),
                          priv_attrs: tuple[str, ...] = tuple(), frozen: tuple[str, ...] = tuple()):
        cls._mod_in_group = mod_in_group
        super().__init_subclass__(attrs=attrs + ('_Data__id','_Data__prefix','_Data__view','_in_group'),
                                  priv_attrs=priv_attrs,
                                  frozen=frozen + ('_Data__id','_Data__prefix','_Data__view','_in_group'))
        
    def __init__(self, id: T, prefix: str, view: 'DataView[T]', priv: dict[str] = {}, **kwargs):
        SuperImmut.__init__(self, priv=priv, _Data__id=id, _Data__prefix=prefix,
                            _Data__view=view, _in_group=False, **kwargs)
    
    def __setattr__(self, name: str, value):
        if not type(self)._mod_in_group and self._in_group:
            raise RuntimeError(f'\'{type(self).__name__}\' objects cannot be mutated while in a group')
        SuperImmut.__setattr__(self, name, value)

    def _set_in_group(self, in_group: bool):
        super(SuperImmut, self).__setattr__('_in_group', in_group)
        
    @property
    def _prefix(self):
        return self.__prefix
    
    @property
    def id(self):
        return self.__id
    
    def view(self):
        return self.__view
    
class DataView[T: Hashable](SuperView[HasID[T]]):

    def __init_subclass__(cls, attrs: tuple[str, ...] = tuple(), funcs: tuple[str, ...] = tuple(),
                          dunders: tuple[str, ...] = tuple()):
        super().__init_subclass__(attrs=attrs + ('_prefix','id'), funcs=funcs + ('view',),
                                  dunders=dunders + ('eq','hash'))