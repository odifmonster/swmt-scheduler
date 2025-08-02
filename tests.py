#!/usr/bin/env python

from app.styles import Greige
from app.inventory import Roll

def main():
    grg = Greige('AU7529', 350)
    r = Roll('FSQ07-5953', grg, 695)
    print(r)

if __name__ == '__main__':
    main()