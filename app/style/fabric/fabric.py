#!/usr/bin/env python

from app.support import HasID, SuperImmut
from .color import Color, LIGHT, MEDIUM

class FabricStyle(HasID[str], SuperImmut,
                  attrs=('_prefix','id','cycle_time','greige','color','yld'),
                  priv_attrs=('id','jets'), frozen=('*id','*jets','greige','color','yld')):
    
    def __init__(self, item, greige, clr_name, clr_num, clr_shade, yld, jets):
        SuperImmut.__init__(self, priv={'id': item, 'jets': tuple(jets)}, greige=greige,
                            color=Color(clr_name, clr_num, clr_shade), yld=yld)
    
    @property
    def _prefix(self):
        return 'FabricStyle'
    
    @property
    def id(self):
        return self.__id
    
    @property
    def cycle_time(self):
        return self.color.cycle_time
    
    def can_run_on_jet(self, jet_id):
        return jet_id in self.__jets
    
    def get_strip(self, soil_level):
        if self.color.shade == LIGHT and soil_level >= 25:
            if soil_level - 27 >= 10:
                return 'HEAVYSTRIP'
            return 'STRIP'
        if self.color.shade == MEDIUM and soil_level >= 45:
            return 'STRIP'
        return None