#!/usr/bin/env python

import random

from app.support.groups.mapped import Mapped
from app.support.groups.temp import Data

def random_str_id(length: int = 8):
    digits = [str(x) for x in range(10)]
    return ''.join([random.choice(digits) for _ in range(length)])

mvar = Mapped(256)
vals: list[Data] = []

for _ in range(25):
    vals.append(Data(random_str_id(), 'MASTER1', 'BLACK', 500))
    mvar.add(vals[-1])

print(mvar.pretty())

for key in mvar:
    print(repr(key))

print(vals[3].id in mvar)
print(mvar.n_items, len(mvar))
print(vals)