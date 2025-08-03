#!/usr/bin/env python

import unittest

from typing import Protocol
from abc import abstractmethod
import random

from app.support import HasID, Viewable
from app.support.groups import Item

def random_str_id(length: int):
    res = ''
    digits = list(range(10))

    for _ in range(length):
        res = res + str(random.choice(digits))
    
    return res
    
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
        self.__view = DataView(self)

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

    def view(self) -> DataView: return self.__view

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

if __name__ == '__main__':
    unittest.main()