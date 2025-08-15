#!/usr/bin/env python

import unittest

import random

from testclasses import Roll, RSizeGroup, RStyleGroup, RollGroup, random_str_id

def random_size_group(length: int, style: str, weight: int) -> tuple[RSizeGroup, dict[str, Roll]]:
    szg = RSizeGroup(style=style, weight=weight)
    roll_ids: dict[str, Roll] = {}

    for _ in range(length):
        roll = Roll(random_str_id(10), style, weight)
        roll_ids[roll.id] = roll
        szg.add(roll)
    
    return szg, roll_ids

def random_style_group(nrolls: int, style: str) -> tuple[RStyleGroup, dict[int, dict[str, Roll]]]:
    stg = RStyleGroup(style=style)
    roll_ids: dict[int, dict[str, Roll]] = {}
    weights = list(map(lambda x: x*100, (5,6,7,8)))

    for _ in range(nrolls):
        roll = Roll(random_str_id(10), style, random.choice(weights))
        if roll.weight not in roll_ids:
            roll_ids[roll.weight] = {}
        roll_ids[roll.weight][roll.id] = roll
        stg.add(roll)
    
    return stg, roll_ids

def random_roll_group(nrolls: int) -> tuple[RollGroup, dict[str, dict[int, dict[str, Roll]]]]:
    rg = RollGroup()
    roll_ids: dict[str, dict[int, dict[str, Roll]]] = {}
    styles = list(map(lambda x: f'STYLE{x}', (1,2,3)))
    weights = list(map(lambda x: x*100, (5,6,7)))

    for _ in range(nrolls):
        roll = Roll(random_str_id(10), random.choice(styles), random.choice(weights))
        if roll.style not in roll_ids:
            roll_ids[roll.style] = {}
        if roll.weight not in roll_ids[roll.style]:
            roll_ids[roll.style][roll.weight] = {}
        roll_ids[roll.style][roll.weight][roll.id] = roll
        rg.add(roll)
    
    return rg, roll_ids

class TestGrouped(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()