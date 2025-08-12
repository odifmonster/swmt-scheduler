#!/usr/bin/env python

from typing import TypeVar, Generic, Hashable

from app.support import SuperImmut, HasID, SuperView, Viewable

T = TypeVar('T', bound=Hashable)

class DataView(Generic[T], SuperView[HasID[T]]):

    def __init_subclass__(cls, funcs = [], dunders = [], attrs = [],
                          vfuncs = [], vdunds = [], vattrs = []):
        bad_pairs = [
            ('_prefix',attrs), ('id',attrs), ('eq',dunders), ('hash',dunders)
        ]
        if any(map(lambda x: x[0] in x[1], bad_pairs)):
            raise RuntimeError('Classes inheriting from \'DataView\' should not define ' + \
                               'behavior relating to HasID protocol.')
        
        super().__init_subclass__(funcs, dunders+['eq','hash'],
                                  attrs+['_prefix','id'],
                                  vfuncs, vdunds, vattrs)

class Data(Generic[T], HasID[T], Viewable[DataView[T]], SuperImmut):

    def __init_subclass__(cls, dattrs = tuple(), dpriv_attrs = tuple(), dfrozen = tuple()):
        if '_prefix' in dattrs or 'id' in dattrs or 'prefix' in dpriv_attrs or \
            'id' in dpriv_attrs:
            raise RuntimeError('Classes inheriting from \'Data\' should not define ' + \
                               'behavior relating to HasID protocol.')

        subattrs = ('_prefix','id') + dattrs
        sub_priv = ('_Data__id', '_Data__prefix') + dpriv_attrs
        sub_frz = ('_Data__id', '_Data__prefix') + dfrozen
        super().__init_subclass__(attrs=subattrs, priv_attrs=sub_priv, frozen=sub_frz)
    
    def __init__(self, id: T, prefix: str, priv = {}, **kwargs):
        priv['_Data__id'] = id
        priv['_Data__prefix'] = prefix
        SuperImmut.__init__(self, priv=priv, **kwargs)
        object.__setattr__(self, '_in_group', False)
    
    @property
    def _prefix(self) -> str:
        return self.__prefix
    
    @property
    def id(self) -> T:
        return self.__id
    
    def __setattr__(self, name, value):
        if hasattr(self, '_in_group') and getattr(self, '_in_group'):
            raise RuntimeError('Objects cannot be mutated while in a group.')
        SuperImmut.__setattr__(self, name, value)

    def add_to_group(self):
        object.__setattr__(self, '_in_group', True)
    
    def view(self):
        raise NotImplementedError()