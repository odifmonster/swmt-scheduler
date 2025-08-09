#!/usr/bin/env python

import datetime

from app import style
from app import schedule

def main():
    style.init()

    start = datetime.datetime(2025, 8, 6)
    p2 = start + datetime.timedelta(days=6)

    aura = style.get_fabric_style('FF AURA30000-39064-63')
    aura_demand = schedule.Demand(aura, 2130, p2)

    print(aura_demand.pretty())

if __name__ == '__main__':
    main()