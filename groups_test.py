#!/usr/bin/env python

import unittest

import random

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

          g = Grouped[int, int]('style', 'weight', 'id', style='STYLE1')

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
    """