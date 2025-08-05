#!/usr/bin/env python

import random
from app.support.groups.temp import Data
from app.support.groups import Grouped2D

def random_str_id(length: int = 8):
    digits = [str(x) for x in range(10)]
    return ''.join([random.choice(digits) for _ in range(length)])

gvar = Grouped2D(master='MASTER1', color='BLACK')

vals: list[Data] = []
value_opts = [100, 200, 300]
for _ in range(20):
    value = random.choice(value_opts)
    vals.append(Data(random_str_id(), 'MASTER1', 'BLACK', value))
    gvar.add(vals[-1])

print(gvar.pretty())

sub_gvar = gvar[200]
print(sub_gvar.pretty())

sub_gvar.add(vals[0])