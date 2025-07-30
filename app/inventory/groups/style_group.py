#!/usr/bin/env python

from ..roll import Roll, SizeClass, NORMAL, LARGE, SMALL
from .base_classes import Group2D
from .size_group import SizeGroup

class StyleGroup(Group2D[SizeClass, SizeGroup]):

    def _add_group(self, prop: SizeClass) -> None:
        self._add_pair(prop, SizeGroup())

    def _get_prop(self, roll: Roll) -> SizeClass:
        return roll.size_class
    
    def get_k_rolls(self, k: int) -> list[Roll]:
        for size in (NORMAL, LARGE, SMALL):
            if not self._has_group(size):
                continue
            res = self._get_group(size).get_k_rolls(k)
            if res: return res
        return []