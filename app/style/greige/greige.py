#!/usr/bin/env python

from app.support import HasID, SuperImmut, FloatRange

class GreigeStyle(HasID[str], SuperImmut,
                  attrs=('_prefix','id','port_range','roll_range'),
                  priv_attrs=('prefix','id')):
    
    def __init__(self, item: str, port_min: float, port_max: float):
        priv = { 'prefix': 'GreigeStyle', 'id': item }
        prt_rng = FloatRange(port_min, port_max)
        rll_rng = FloatRange(port_min*2, port_max*2)
        SuperImmut.__init__(self, priv=priv, port_range=prt_rng, roll_range=rll_rng)

    @property
    def _prefix(self):
        return self.__prefix
    
    @property
    def id(self) -> str:
        return self.__id

EMPTY = GreigeStyle('NONE', 0, 400)