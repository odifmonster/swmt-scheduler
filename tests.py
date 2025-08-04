#!/usr/bin/env python

import random

from app.support.groups.temp import Data
from app.support.groups import Item

def random_str_id(length: int) -> str:
    digits = [str(x) for x in range(10)]
    return ''.join([random.choice(digits) for _ in range(length)])

item = Item()
d1 = Data(random_str_id(10), 'MASTER1', 'BLUE', 50)
d2 = Data(random_str_id(10), 'MASTER2', 'RED', 100)

item.store(d1, 0)
print(item.data)

rem = item.clear()
rem.color = 'GREEN'
print(rem)

item.store(d2, 1)
print(item.data)
print(item.data == d2)