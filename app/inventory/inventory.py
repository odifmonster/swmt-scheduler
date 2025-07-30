#!/usr/bin/env python

from .style import Greige
from .roll import Roll
from .groups import Group2D, StyleGroup

class Inventory(Group2D[Greige, StyleGroup]):

    def _add_group(self, prop: Greige) -> None:
        self._add_pair(prop, StyleGroup())

    def _get_prop(self, roll: Roll) -> Greige:
        return roll.style
    
    def get_k_rolls(self, k: int, **kwargs) -> list[Roll]:
        if 'style' not in kwargs:
            raise ValueError('Method \'get_k_rolls\' requires \'style\' argument.')
        if not isinstance(kwargs['style'], Greige):
            raise TypeError('\'style\' argument must be of type \'Greige\'.')
        
        return self._get_group(kwargs['style']).get_k_rolls(k)