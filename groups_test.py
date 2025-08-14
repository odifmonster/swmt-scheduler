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

    def setUp(self):
        szg, szg_rids = random_size_group(50, 'STYLE1', 700)
        self.szg = szg
        self.szg_rids = szg_rids

        stg, stg_rids = random_style_group(75, 'STYLE1')
        self.stg = stg
        self.stg_rids = stg_rids

        rg, rg_rids = random_roll_group(100)
        self.rg = rg
        self.rg_rids = rg_rids

        self.removed: list[Roll] = []

    def test_len_1d(self):
        n_remove = random.randint(1,10)
        ids_to_remove = random.sample(list(self.szg_rids.keys()), n_remove)
        view = self.szg.view()

        self.assertEqual(len(self.szg), 50)
        self.assertEqual(len(view), 50)

        for rid in ids_to_remove:
            self.removed.append(self.szg.remove(self.szg_rids[rid].view()))
        
        self.assertEqual(len(self.szg), 50-n_remove)
        self.assertEqual(len(view), 50-n_remove)

        for roll in self.removed:
            self.szg.add(roll)

        self.assertEqual(len(self.szg), 50)
        self.assertEqual(len(view), 50)

    def test_len_2d(self):
        weights = list(self.stg_rids.keys())
        to_remove = weights[:2]
        view = self.stg.view()

        self.assertEqual(len(self.stg), len(weights))
        self.assertEqual(len(view), len(weights))

        for wt in to_remove:
            for rid in self.stg_rids[wt]:
                r = self.stg.remove(self.stg_rids[wt][rid].view())
                self.removed.append(r)
        
        self.assertEqual(len(self.stg), len(weights)-2)
        self.assertEqual(len(view), len(weights)-2)
        added = self.removed[0]
        self.stg.add(self.removed[0])
        self.assertEqual(len(self.stg), len(weights)-1)
        self.assertEqual(len(view), len(weights)-1)

        for roll in self.removed:
            if roll.weight != added.weight:
                self.stg.add(roll)
                break
        
        self.assertEqual(len(self.stg), len(weights))
        self.assertEqual(len(view), len(weights))

    def test_iter_1d(self):
        checked: set[str] = set()
        view = self.szg.view()

        for rid in self.szg:
            self.assertFalse(rid in checked)
            checked.add(rid)
        
        self.assertEqual(set(self.szg_rids.keys()), checked)
        self.assertEqual(set(view), checked)

        to_remove = random.sample(list(checked), 5)
        for rid in to_remove:
            r = self.szg.remove(self.szg_rids[rid].view())
            self.removed.append(r)
        
        self.assertEqual(set(self.szg), set(self.szg_rids.keys()) - set(to_remove))
        self.assertEqual(set(self.szg), set(self.szg_rids.keys()) - set(to_remove))

        for roll in self.removed:
            self.szg.add(roll)
        
        self.assertEqual(set(self.szg), set(self.szg_rids.keys()))
        self.assertEqual(set(view), set(self.szg_rids.keys()))

    def test_iter_2d(self):
        checked: set[int] = set()
        view = self.stg.view()

        for wt in self.stg:
            self.assertFalse(wt in checked)
            checked.add(wt)
        
        self.assertEqual(set(self.stg_rids.keys()), checked)
        self.assertEqual(set(view), checked)

        to_remove = random.sample(list(checked), 2)
        for wt in to_remove:
            for rid in self.stg_rids[wt]:
                r = self.stg.remove(self.stg_rids[wt][rid].view())
                self.removed.append(r)
        
        self.assertEqual(set(self.stg), set(self.stg_rids.keys()) - set(to_remove))
        self.assertEqual(set(view), set(self.stg_rids.keys()) - set(to_remove))

        for roll in self.removed:
            self.stg.add(roll)

        self.assertEqual(set(self.stg), set(self.stg_rids.keys()))
        self.assertEqual(set(view), set(self.stg_rids.keys()))

    def test_contains_1d(self):
        view = self.szg.view()

        for rid in self.szg_rids:
            self.assertTrue(rid in self.szg)
            self.assertTrue(rid in view)

        to_remove = random.sample(list(self.szg_rids.keys()), 5)
        for rid in to_remove:
            r = self.szg.remove(self.szg_rids[rid].view())
            self.removed.append(r)
            self.assertFalse(rid in self.szg)
            self.assertFalse(rid in view)
        
        for roll in self.removed:
            self.szg.add(roll)
            self.assertTrue(roll.id in self.szg)
            self.assertTrue(roll.id in view)
    
    def test_contains_2d(self):
        view = self.stg.view()

        for wt in self.stg_rids:
            self.assertTrue(wt in self.stg)
            self.assertTrue(wt in view)

        to_remove = random.choice(list(self.stg_rids.keys()))
        for rid in self.stg_rids[to_remove]:
            r = self.stg.remove(self.stg_rids[to_remove][rid].view())
            self.removed.append(r)
        
        self.assertFalse(to_remove in self.stg)
        self.assertFalse(to_remove in view)
        self.stg.add(self.removed[0])
        self.assertTrue(to_remove in self.stg)
        self.assertTrue(to_remove in view)

    def test_getitem_errors(self):
        bad_style = 'A_BAD_STYLE'
        bad_id = 'A_BAD_ID'

        with self.assertRaises(KeyError) as cm:
            v1 = self.rg[bad_style, 500, bad_id]

        self.assertEqual(str(cm.exception), f'"Object does not contain key (\'{bad_style}\', 500, \'{bad_id}\')."')

        with self.assertRaises(ValueError) as cm:
            style1 = 'STYLE1'
            wt1 = 700
            id1 = list(self.rg_rids[style1][wt1].keys())[0]
            v1 = self.rg[style1, wt1, id1, 'hello']
        
        self.assertEqual(str(cm.exception), f'4-dimension key incompatible with 3-dimension object.')
    
    def test_getitem_views(self):
        style1 = 'STYLE1'
        wt1 = 700

        style1view = self.rg[style1]
        size1view = self.rg[style1, wt1]

        with self.assertRaises(TypeError) as cm:
            style1view.add(Roll(random_str_id(10), style1, random.choice([500,600,700,800])))

        err = 'Objects of type \'{}\' cannot call methods that mutate the objects they view.'
        self.assertEqual(str(cm.exception), err.format(type(style1view).__name__))

        with self.assertRaises(TypeError) as cm:
            size1view.add(Roll(random_str_id(10), style1, wt1))

        self.assertEqual(str(cm.exception), err.format(type(size1view).__name__))
    
    def test_getitem_live(self):
        size1view = self.rg['STYLE1', 700]
        size1ids = list(self.rg_rids['STYLE1'][700].keys())

        for rid in self.rg_rids['STYLE1'][700]:
            self.rg.remove(self.rg['STYLE1', 700, rid])
            size1ids.remove(rid)
            self.assertEqual(len(size1view), len(size1ids))
            self.assertTrue(rid not in size1view)

if __name__ == '__main__':
    unittest.main()