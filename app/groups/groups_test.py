#!/usr/bin/env python

import unittest

import random
from app.support import setter_like
from data import DataView, Data

class RollView(DataView[str],
               funcs=['use','temp_use','reset'],
               attrs=['color','weight']):
    pass

class Roll(Data[str],
           attrs=('color','weight'),
           priv_attrs=('color','weight','allocated','view'),
           frozen=('_Roll__color','_Roll__view')):
    
    def __init__(self, id: str, color: str, weight: float):
        priv = { 'color': color, 'weight': weight, 'allocated': 0,
                 'view': RollView(self) }
        super().__init__(id, 'ROLL', priv)
    
    @property
    def color(self) -> str:
        return self.__color
    
    @property
    def weight(self) -> float:
        return self.__weight - self.__allocated
    
    @setter_like
    def use(self, amount: float) -> None:
        if amount > self.weight:
            raise ValueError(f'Used amount {amount:.2f} exceeds total roll weight ({self.weight:.2f}).')
        self.__weight -= amount
    
    @setter_like
    def temp_use(self, amount: float) -> None:
        if amount > self.weight:
            raise ValueError(f'Used amount {amount:.2f} exceeds total roll weight ({self.weight:.2f}).')
        self.__allocated += amount

    @setter_like
    def reset(self) -> None:
        self.__allocated = 0

    def view(self) -> RollView:
        return self.__view
    
def random_str_id(length: int = 10):
    digits = [str(x) for x in range(10)]
    return ''.join([random.choice(digits) for _ in range(length)])

class TestDataImpl(unittest.TestCase):

    """
    Behaviors to test:

        1. Instantiate a roll object. The id, color, and weight are the same as what was passed
           in, and _prefix is equal to 'ROLL'.
        2. You get an AttributeError when trying to set _prefix, id, or color. You also get one
           when trying to set _Roll__prefix, _Roll__id, _Roll__color, or _Roll__view.
        4. You are able to retrieve a view of a Roll object. When you change the Roll object's
           weight through 'use' or 'temp_use', the view object's weight changes as well.
        5. If you call 'add_to_group' and then try to change a Roll's weight, it throws a
           RuntimeError. If you then call 'remove_from_group', you can change it again.
    """

    def test_instantiate_roll(self):
        roll = Roll('6005781230', 'BLACK', 500)
        self.assertEqual(roll.id, '6005781230')
        # continue implementation here

    def test_set_immutables(self):
        roll = Roll(random_str_id(), 'BLACK', 500)
        # see app/support/supers/supers_test.py for how to check error messages