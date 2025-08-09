#!/usr/bin/env python

import random

from app.style import GreigeStyle
from app.inventory import Inventory
from app.inventory.roll import Roll, NORMAL

def random_str_id(length: int = 8) -> str:
    digits = [str(x) for x in range(10)]
    return ''.join([random.choice(digits) for _ in range(length)])

STYLES = [
    GreigeStyle('AU4782', 375), GreigeStyle('AU5429D', 387),
    GreigeStyle('AU4782K', 375), GreigeStyle('AU7529', 350)
]

def random_roll() -> Roll:
    return Roll(random_str_id(), random.choice(STYLES), random.normalvariate(mu=700, sigma=75))

def main():
    inv = Inventory()
    
    for _ in range(100):
        inv.add(random_roll())
    
    print(inv.pretty())

if __name__ == '__main__':
    main()