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

class TestAtomic(unittest.TestCase):

    def test_getitem(self):
        atom = Atomic(name='DVar1', value=5)
        vals: list[Data] = []

        for _ in range(25):
            d = Data(random_str_id(), 'DVar1', 5)
            atom.add(d)
            vals.append(d)

        self.assertTrue(
            all(map(lambda v: atom[v.id] == v, vals)),
            'Getting an item by id should return a view of the same item.'
        )

        view = atom[vals[0].id]
        def attempt_set(view: DataView):
            view.name = 'DVar2'

        self.assertRaises(AttributeError, lambda: attempt_set(view))

    def test_add(self):
        atom = Atomic(name='DVar1', value=5)
        atom.add(Data(random_str_id(), 'DVar1', 5))

        self.assertEqual(len(atom), 1)
        self.assertRaises(ValueError, lambda: atom.add(Data(random_str_id(), 'DVar2', 5)))
        self.assertRaises(ValueError, lambda: atom.add(Data(random_str_id(), 'DVar1', 10)))
        self.assertRaises(ValueError, lambda: atom.add(Data(random_str_id(), 'DVar2', 10)))

if __name__ == '__main__':
    unittest.main()