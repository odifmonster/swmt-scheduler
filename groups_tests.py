#!/usr/bin/env python

import unittest

import random

from app.support.groups import *

def random_str_id(length: int):
    res = ''
    digits = list(range(10))

    for _ in range(length):
        res = res + str(random.choice(digits))
    
    return res

class TestItem(unittest.TestCase):

    def test_insert_errors(self):
        ivar = Item[Data, DataView]()
        dvar1 = Data(random_str_id(8), 'DVar1', 10)
        dvar2 = Data(random_str_id(8), 'DVar2', 25)

        self.assertRaises(ValueError, lambda: ivar.insert(dvar1, -1))
        ivar.insert(dvar1, 0)
        self.assertRaises(RuntimeError, lambda: ivar.insert(dvar2, 1))
        ivar.remove()
        self.assertRaises(ValueError, lambda: ivar.insert(dvar2, 0))
    
    def test_remove_errors(self):
        ivar = Item[Data, DataView]()
        dvar1 = Data(random_str_id(8), 'DVar1', 10)

        self.assertRaises(RuntimeError, lambda: ivar.remove())
        ivar.insert(dvar1, 0)
        ivar.remove()
        self.assertRaises(RuntimeError, lambda: ivar.remove())

    def test_bool_funcs(self):
        ivar = Item[Data, DataView]()
        dvar1 = Data(random_str_id(8), 'DVar1', 10)

        self.assertFalse(ivar.was_inserted(),
                         'was_inserted() should be False after initialization.')
        self.assertTrue(ivar.is_empty(),
                        'is_empty() should be True after initialization.')
        ivar.insert(dvar1, 0)
        self.assertTrue(ivar.was_inserted() and not ivar.is_empty(),
                        'Items should be inserted and not empty after insertion.')
        ivar.remove()
        self.assertTrue(ivar.was_inserted() and ivar.is_empty(),
                        'Items should be inserted and empty after removal.')
    
    def test_data_view(self):
        ivar = Item[Data, DataView]()
        dvar1 = Data(random_str_id(8), 'DVar1', 10)
        dvar2 = Data(random_str_id(8), 'DVar2', 25)

        self.assertRaises(AttributeError, lambda: ivar.data)
        ivar.insert(dvar1, 0)
        ivar.remove()
        self.assertRaises(AttributeError, lambda: ivar.data)
        ivar.insert(dvar2, 1)
        self.assertEqual(ivar.data, dvar2,
                         'The data inserted should be equal to the Item\'s data.')
        
def random_group(length: int, initsize: int = 256) -> tuple[BaseGroup, list[Data]]:
    bgvar = BaseGroup(initsize)
    vals = []
    for i in range(length):
        d = Data(random_str_id(8), f'DVar{i+1}', i**2)
        bgvar.add(d)
        vals.append(d)

    return bgvar, vals
        
class TestBaseGroup(unittest.TestCase):

    def test_length(self):
        bgvar = BaseGroup(256)
        for i in range(10):
            self.assertEqual(bgvar.length, i)
            bgvar.add(Data(random_str_id(8), f'DVar{i+1}', i**2))
        self.assertEqual(bgvar.length, 10)
    
    def test_iter(self):
        bgvar, vals = random_group(10)
        
        for i, d in enumerate(bgvar.iter_items()):
            self.assertEqual(vals[i], d)
    
    def test_writable(self):
        bgvar, vals = random_group(10)

        dvar = vals[3]
        dvar.name = 'NewDVar'
        dvar.value = -4

        dview = bgvar.get_by_id(dvar.id)
        self.assertTrue(dview.name == 'NewDVar' and dview.value == -4)
        
        def attempt_set_name(bgvar: BaseGroup, item_id: str, newname: str):
            bgvar.get_by_id(item_id).name = newname
        
        self.assertRaises(AttributeError, lambda: attempt_set_name(bgvar, dvar.id, 'NewDVar2'))

        remdvar = bgvar.remove(dvar.id)
        remdvar.name = 'OldDVar'
        remdvar.value = 50

        self.assertTrue(dvar.name == 'OldDVar' and dvar.value == 50)
        self.assertTrue(dview.name == 'OldDVar' and dview.value == 50)

    def test_resize(self):
        bgvar, vals = random_group(10, initsize=8)

        for i, d in enumerate(bgvar.iter_items()):
            self.assertEqual(vals[i], d)

    def test_add_duplicate(self):
        bgvar, vals = random_group(10)

        bgvar.add(vals[2])
        views = list(bgvar.iter_items())
        self.assertEqual(vals[2], views[2])

    def test_remove(self):
        bgvar, vals = random_group(10)

        bgvar.remove(vals[2].id)
        self.assertEqual(bgvar.length, 9)

def main():
    suite = unittest.TestSuite()
    suite.addTest(TestItem(methodName='run'))
    suite.addTest(TestBaseGroup(methodName='run'))

    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == '__main__':
    main()