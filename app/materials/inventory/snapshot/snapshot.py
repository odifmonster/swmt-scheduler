#!/usr/bin/env python

from app.support import HasID, SuperImmut

_CTR = 0

class Snapshot(HasID[int], SuperImmut, attrs=('_prefix','id'), priv_attrs=('id',),
               frozen=('*id',)):
    
    def __init__(self):
        globals()['_CTR'] += 1
        SuperImmut.__init__(self, priv={'id': globals()['_CTR']})

    @property
    def _prefix(self):
        return 'Snapshot'
    
    @property
    def id(self):
        return self.__id