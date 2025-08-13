#!/usr/bin/env python

import unittest

import random

from app.groups import Grouped
from testclasses import Roll, RollView, RSizeGroup, RStyleGroup, RollGroup, \
    random_str_id


class TestGrouped(unittest.TestCase):

    """
    Tests to run:

        1. Grouped object throws an error on bad initialization
          A Grouped object can be directly initialized like so:

          g = Grouped[int, int]('string1', 'string2', ..., name1=<value1>, name2=<value2>)

          Ensure that a ValueError is raised if any of the strings at the beginning appear as
          names. So

          g = Grouped[int, int]('style', 'weight', 'id', style='hello')

          should raise a ValueError.
        
        2. Grouped object throws an error when data has wrong properties
          This test will make use of the provided RSizeGroup class. A new RSizeGroup can be
          initialized like so:

          sg = RSizeGroup(style=some_style, weight=some_weight)

          Where some_style is a str and some_weight is an int. Ensure that a ValueError is
          thrown when adding a new roll whose properties do not match what was passed in.
          So if some_style='STYLE1' and some_weight=100, then

          sg.add(Roll('a roll id', 'STYLE2', 100))

          should raise an error.
        
        3. Roll object throws an error after being added to group
          This test will make use of the provided RollGroup class. A new RollGroup can be
          initialized like so:

          rg = RollGroup()

          If you call rg.add(roll) for any Roll object, and then try to re-assign roll's
          weight, you should get a RuntimeError.

        4. Grouped object throws an error if you attempt to remove data it does not have
          This test will make use of the provided RollGroup and Roll classes, as well as
          the .view() function of the Roll type. This is because the 'remove' function of
          a RollGroup accepts RollViews as arguments, not Rolls.
          
          There is no need to test for the error message, simply check that passing the
          view of a roll not in a RollGroup results in a ValueError. This should apply to
          rolls never added to the group as well as rolls previously added and then removed.

        5. Roll object can be modified after being removed from a group
          Can be added as part of test 3. Exactly what it sounds like. Can use assertEqual
          on some attribute to ensure that it actually changed.
"""

    def test_bad_initialization(self):
        with self.assertRaises(ValueError) as cm:
            g = Grouped[int, int]('style', 'weight', 'id', style='hello')
        
        error_msg = "Unbound properties \'style\' cannot be bound to values."
        self.assertEqual(str(cm.exception), error_msg)

    def test_RSizeGroup_properties(self) :
        sg = RSizeGroup(style='STYLE1', weight = 100)
        with self.assertRaises(ValueError):
            sg.add(Roll('1', 'STYLE2', 100))
      
    def test_mod_after_add(self):
        roll = Roll('1', 'STYLE2', 100)
        rg = RollGroup()
        rg.add(roll)
        with self.assertRaises(RuntimeError):
            roll.weight = 90
        
    def test_group_remove(self):
        rg = RollGroup()
        roll = Roll('1', 'STYLE2', 100)
        with self.assertRaises(ValueError):
            rg.remove(roll.view())
        
        roll2 = Roll('2', 'STYLE2', 100)
        rg.add(roll2)
        rg.remove(roll2.view())
        with self.assertRaises(ValueError):
            rg.remove(roll2.view())
      
        roll2.weight = 150
        self.assertEqual(roll2.weight, 150)
    
    
    
if __name__ == '__main__':
  unittest.main()
