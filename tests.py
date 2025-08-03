#!/usr/bin/env python

import unittest

import random

from app.support.groups import Data, DataView, Atomic

def random_str_id() -> str:
    res = ''
    digits = list(range(10))

    for _ in range(10):
        res += str(random.choice(digits))

    return res

def random_data(length: int, name: str, value: int) -> list[Data]:
    return [Data(random_str_id(), name, value) for _ in range(length)]

class TestAtomic(unittest.TestCase):

    def test_getitem(self):
        atom = Atomic(name='DVar1', value=5)
        vals: list[Data] = random_data(25, 'DVar1', 5)

        for v in vals: atom.add(v)

        self.assertTrue(
            all(map(lambda v: atom[v.id] == v, vals)),
            'Getting an item by id should return a view of the same item.'
        )

        view = atom[vals[0].id]
        def attempt_set(view: DataView):
            view.name = 'DVar2'

        self.assertRaises(AttributeError, lambda: attempt_set(view))

    def test_iter(self):
        atom = Atomic(name='DVar1', value=5)
        vals = random_data(20, 'DVar1', 50)

        val_ids = [v.id for v in vals]
        self.assertTrue(
            all(map(lambda x: x[0] == x[1], zip(val_ids, iter(atom))))
        )
    
    def test_contains(self):
        atom = Atomic(name='Data', value=0)
        atom.add(Data('a_unique_id', 'Data', 0))

        self.assertTrue('a_unique_id' in atom)
        self.assertFalse('another_id' in atom)

    def test_add(self):
        atom = Atomic(name='DVar1', value=5)
        atom.add(Data(random_str_id(), 'DVar1', 5))

        self.assertEqual(len(atom), 1)
        self.assertRaises(ValueError, lambda: atom.add(Data(random_str_id(), 'DVar2', 5)))
        self.assertRaises(ValueError, lambda: atom.add(Data(random_str_id(), 'DVar1', 10)))
        self.assertRaises(ValueError, lambda: atom.add(Data(random_str_id(), 'DVar2', 10)))

if __name__ == '__main__':
    unittest.main()