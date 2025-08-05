#!/usr/bin/env python

import random
from app.support.groups.temp import Data
from app.support.groups import Grouped1D

def random_str_id(length: int = 8):
    digits = [str(x) for x in range(10)]
    return ''.join([random.choice(digits) for _ in range(length)])

gvar = Grouped1D()

vals: list[Data] = [Data(random_str_id(), 'MASTER1', 'BLACK', 500) for _ in range(15)]

for d in vals:
    gvar.add(d)

print(gvar.pretty())

dvar = vals[7]
print(dvar.id)
print(gvar[dvar.id].pretty(kind='object'))

dvar.inc()
print(gvar[dvar.id].pretty())

for d_id in gvar:
    print(gvar[d_id].pretty())