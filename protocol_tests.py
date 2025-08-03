#!/usr/bin/env python

import unittest

from typing import Protocol
from abc import abstractmethod
import random

from app.support import HasID, Viewable

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
    
class DataLike(HasID[str], Protocol):

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError()
    
    @property
    @abstractmethod
    def value(self) -> int:
        raise NotImplementedError()
    
class DataView(DataLike):

    def __init__(self, link: DataLike):
        self.__link = link

    @property
    def _prefix(self) -> str: return self.__link._prefix
    
    @property
    def id(self) -> str: return self.__link.id
    
    @property
    def name(self) -> str: return self.__link.name
    
    @property
    def value(self) -> int: return self.__link.value

class Data(DataLike, Viewable[DataView]):

    def __init__(self, id: str, name: str, value: int):
        self.__id = id
        self.__name = name
        self.__value = value

    @property
    def _prefix(self) -> str: return 'DATA'

    @property
    def id(self) -> str: return self.__id

    @property
    def name(self) -> str: return self.__name
    @name.setter
    def name(self, value: str) -> None: self.__name = value

    @property
    def value(self) -> int: return self.__value
    @value.setter
    def value(self, new: int) -> None: self.__value = new

    def view(self) -> DataView: return DataView(self)

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

class TestViewable(unittest.TestCase):

    def test_equals(self):
        var = Data(random_str_id(8), 'Jane', 100)
        self.assertEqual(var, var.view(), 'An object should be equal to its view.')
    
    def test_is_live(self):
        var = Data(random_str_id(8), 'Kevin', 5)
        var_view = var.view()
        self.assertTrue(all([var.name == var_view.name,
                             var.value == var_view.value]),
                        'Object attributes and view attributes should be equal after initialization.')
        
        var.name = 'James'
        var.value = 50
        self.assertTrue(all([var.name == var_view.name,
                             var.value == var_view.value]),
                        'Object and view attributes should be equal after change.')
    
    def test_read_only_view(self):
        var = Data(random_str_id(8), 'Rachel', 25)
        view = var.view()
        
        def attempt_set(v: DataView, val: int):
            v.value = val

        self.assertRaises(AttributeError, lambda: attempt_set(view, 500))

def main():
    suite = unittest.TestSuite()
    suite.addTests([TestHasID(methodName='run'), TestViewable(methodName='run')])
    runner = unittest.TextTestRunner()

    runner.run(suite)

if __name__ == '__main__':
    main()