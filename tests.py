#!/usr/bin/env python

import random

from app import inventory

def random_id(length: int) -> str:
    res = ''
    digits = [str(i) for i in range(10)]
    for _ in range(length):
        res = res + random.choice(digits)
    return res

def random_roll(style: inventory.style.Greige) -> inventory.roll.Roll:
    return inventory.roll.Roll(random_id(8), style, random.normalvariate(mu=700, sigma=50))