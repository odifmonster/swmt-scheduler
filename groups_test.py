#!/usr/bin/env python

import unittest

from typing import Generator, Any
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

def flatten_dict(d: dict | Roll) -> Generator[Roll]:
    if not type(d) is dict:
        yield d
        return
    
    for key in d:
        sub_gen = flatten_dict(d[key])
        yield from sub_gen

class TestGrouped(unittest.TestCase):

    def test_len_keys(self):
        for _ in range(10):
            nrolls = random.randint(100, 200)
            grp, raw_dict = random_roll_group(nrolls)
            grp_keys = grp.fullkeys()
            rolls_list = list(flatten_dict(raw_dict))
            self.assertEqual(len(grp_keys), nrolls)

            n_remove = random.randint(1, nrolls-1)
            to_remove = random.sample(rolls_list, n_remove)
            for r in to_remove:
                grp.remove(r)
            
            self.assertEqual(len(grp_keys), nrolls-n_remove)

    def test_iter_keys(self):
        for _ in range(10):
            nrolls = random.randint(100, 200)
            grp, raw_dict = random_roll_group(nrolls)
            grp_keys = grp.fullkeys()
            passes: dict[Roll, int] = { r: 0 for r in flatten_dict(raw_dict) }

            for key in grp_keys:
                rview = grp[key]
                passes[rview] += 1
            
            self.assertTrue(all(map(lambda npass: npass == 1, passes.values())))
            not_removed = list(passes.keys())

            n_remove = random.randint(1, nrolls-1)
            to_remove = random.sample(list(passes.keys()), n_remove)
            for r in to_remove:
                grp.remove(r)
                not_removed.remove(r)
            
            for key in grp_keys:
                passes[grp[key]] += 1
            
            self.assertTrue(all(map(lambda r: passes[r] == 1, to_remove)))
            self.assertTrue(all(map(lambda r: passes[r] == 2, not_removed)))
    
    def test_contains_keys(self):
        for _ in range(10):
            nrolls = random.randint(100, 200)
            grp, raw_dict = random_roll_group(nrolls)
            grp_keys = grp.fullkeys()
            rolls_list = list(flatten_dict(raw_dict))

            for r in rolls_list:
                self.assertTrue((r.style, r.weight, r.id) in grp_keys)

            n_remove = random.randint(1, nrolls-1)
            to_remove = random.sample(rolls_list, n_remove)
            for r in to_remove:
                grp.remove(r)
            
            self.assertTrue(all(map(lambda r: (r.style,r.weight,r.id) not in grp_keys, to_remove)))

if __name__ == '__main__':
    unittest.main()