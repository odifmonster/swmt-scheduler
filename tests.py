#!/usr/bin/env python

import random
from app.support.groups.temp import Data
from app.support.groups import Grouped1D

def random_str_id(length: int = 8):
    digits = [str(x) for x in range(10)]
    return ''.join([random.choice(digits) for _ in range(length)])

gvar1 = Grouped1D(master='MASTER1', color='BLACK', value=500)

vals: list[Data] = [Data(random_str_id(), 'MASTER1', 'BLACK', 500) for _ in range(15)]

for d in vals:
    gvar1.add(d)

print(gvar1.pretty())

dvar = vals[7]
print(dvar.id)
print(gvar1[dvar.id].pretty(kind='object'))

bad_data = Data(random_str_id(), 'MASTER1', 'BLUE', 500)
gvar1.add(bad_data)