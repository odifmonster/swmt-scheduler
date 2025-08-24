#!/usr/bin/env python

from app.support import HasID, SuperImmut, FloatRange

class GreigeStyle(HasID[str], SuperImmut, attrs=('_prefix','id','roll_rng','port_rng'),
                  priv_attrs=('prefix','id'), frozen=('*prefix','*id','roll_rng','port_rng')):
    
    def __init__(self, id: str, port_min: float, port_max: float):
        SuperImmut.__init__(self, priv={'id': id, 'prefix': 'GreigeStyle'},
                            roll_rng=FloatRange(port_min, port_max),
                            port_rng=FloatRange(port_min*2, port_max*2))
    
    @property
    def _prefix(self):
        return self.__prefix
    
    @property
    def id(self):
        return self.__id