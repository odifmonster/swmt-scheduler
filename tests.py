#!/usr/bin/env python

import random

from app.support.groups.mapped import Mapped
from app.support.groups.temp import Data

def random_str_id(length: int = 8):
    digits = [str(x) for x in range(10)]
    return ''.join([random.choice(digits) for _ in range(length)])

mvar = Mapped(256)

d1 = Data(random_str_id(), 'MASTER1', 'BLACK', 500)
d1copy = Data(d1.id, d1.master, d1.color, d1.value)

d2 = Data(random_str_id(), 'MASTER2', 'BLUE', 450)

print(mvar.n_items)
mvar.add(d1)
print(mvar.n_items)
mvar.add(d1copy)
print(mvar.n_items)

mvar.add(d2)

mview = mvar.view()

try:
    mview.remove(d2.id)
except AttributeError as e:
    print(e)

print(mvar.n_items)
mvar.remove(d2.id)
print(mvar.n_items)