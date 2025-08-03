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

class ConcreteID(HasID[str]):

    def __init__(self, id: str, suffix: int):
        self.__id = id
        self.__prefix = 'TYPE' + str(suffix)

    @property
    def id(self) -> str:
        return self.__id
    
    @property
    def _prefix(self) -> str:
        return self.__prefix

class TestHasID(unittest.TestCase):

    def test_equals(self):
        var1 = ConcreteID(random_str_id(8), 1)
        var2 = ConcreteID(var1.id, 1)
        var3 = ConcreteID(random_str_id(8), 1)
        var4 = ConcreteID(var1.id, 2)

        self.assertEqual(var1, var2,
                         'Two objects with same id and _prefix should be equal.')
        self.assertNotEqual(var1, var3,
                            'Two objects with different ids and same _prefix should not be equal.')
        self.assertNotEqual(var1, var4,
                            'Two objects with same id and different _prefix should not be equal.')
    
    def test_hash(self):
        var1 = ConcreteID(random_str_id(8), 1)
        var2 = ConcreteID(var1.id, 1)

        self.assertEqual(hash(var1), hash(var2), 'Two equal objects should have the same hash value.')

if __name__ == '__main__':
    unittest.main()