#!/usr/bin/env python

import app

from loaddata import load_inv
from getrolls import get_port_loads

def main():
    app.style.greige.init()

    print('loading inv...')
    inv = load_inv()
    print('done loading inv!')
    grg = app.style.greige.get_greige_style('AU7389G')

    ploads = get_port_loads(grg, inv, app.support.FloatRange(300, 400))
    i = 0
    for load in ploads:
        if i >= 8:
            break
        print(f'load {i+1}')
        print(f'  roll=\'{load.roll1.id}\'  lbs={load.roll1.lbs:.2f}')
        if not load.roll2 is None:
            print(f'  roll=\'{load.roll2.id}\'  lbs={load.roll2.lbs:.2f}')
        i += 1

if __name__ == '__main__':
    main()