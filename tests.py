#!/usr/bin/env python

from typing import TypeVar, TypeVarTuple
import random

from app.support.groups import Grouped
from item import Item, ItemArgsOpt

T = TypeVar('T')
Ts = TypeVarTuple('Ts')
InvGroup = Grouped[str, ItemArgsOpt, T, *Ts]
    
def random_str_id(length: int = 8):
    digits = [str(i) for i in range(10)]
    return ''.join([random.choice(digits) for _ in range(length)])

def main():
    inv = InvGroup[str, str, int, str]('master', 'color', 'value', 'id')

    masters = [f'MASTER{i+1}' for i in range(3)]
    colors = ['BLACK', 'BLUE']
    values = [400, 500]

    for _ in range(50):
        inv.add(Item(random_str_id(), random.choice(masters),
                     random.choice(colors), random.choice(values)))
    
    print(inv.pretty())

if __name__ == '__main__':
    main()