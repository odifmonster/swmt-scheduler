#!/usr/bin/env python

import random

from app.support.groups.mapped import Mapped
from app.support.groups.temp import Data, DPrettyArgsOpt

def random_str_id(length: int = 8):
    digits = [str(x) for x in range(10)]
    return ''.join([random.choice(digits) for _ in range(length)])

vals: list[Data] = []
mvar = Mapped[str, DPrettyArgsOpt, str](subattrs=('master', 'color', 'value'))

masters = ['MASTER1', 'MASTER2', 'MASTER3']
colors = ['BLACK', 'BLUE']
values = list(range(3))

for _ in range(50):
    vals.append(Data(random_str_id(),
                     random.choice(masters),
                     random.choice(colors),
                     random.choice(values)))
    mvar.add(vals[-1])

some_val = vals[8]
submap = mvar[some_val.master, some_val.color, some_val.value]
print(submap.pretty())