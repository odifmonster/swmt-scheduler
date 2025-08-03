#!/usr/bin/env python

import unittest
import random

from app.support import HasID

def random_str_id(length: int):
    res = ''
    digits = list(range(10))

    for _ in range(length):
        res = res + str(random.choice(digits))
    
    return res

def random_int_id(length: int):
    digits = list(range(10))
    res = random.choice(digits[1:])

    for _ in range(length-1):
        res *= 10
        res = res + random.choice(digits)
    
    return res

class TestHasID(unittest.TestCase):

    def test_equals(self):
        var1 = HasID[int](random_int_id(8), 'TYPE1')
        var2 = HasID[int](var1.id, 'TYPE1')
        var3 = HasID[int](random_int_id(8), 'TYPE1')
        var4 = HasID[int](var1.id, 'TYPE2')

        self.assertEqual(var1, var2,
                         'Two objects with same id and _prefix should be equal.')
        self.assertNotEqual(var1, var3,
                            'Two objects with different ids and same _prefix should not be equal.')
        self.assertNotEqual(var1, var4,
                            'Two objects with same id and different _prefix should not be equal.')
    
    def test_hash(self):
        var1 = HasID[str](random_str_id(8), 'VAR_TYPE')
        var2 = HasID[str](var1.id, 'TYPE_VAR')

        self.assertEqual(hash(var1), hash(var2), 'Two equal objects should have the same hash value.')

if __name__ == '__main__':
    unittest.main()