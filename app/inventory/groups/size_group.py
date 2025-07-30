#!/usr/bin/env python

from ..roll import Roll
from .base_classes import Group

class SizeGroup(Group):

    @property
    def total_weight(self) -> float:
        return super().total_weight
    
    def add_roll(self, roll: Roll) -> None:
        super().add_roll(roll)

    def remove_roll(self, roll: Roll) -> None:
        return super().remove_roll(roll)
    
    def get_k_rolls(self, k: int, **kwargs) -> list[Roll]:
        if self.length < k:
            return []
        
        ret: list[Roll] = []
        for i, roll in enumerate(self):
            if i < k:
                ret.append(roll)

        return ret