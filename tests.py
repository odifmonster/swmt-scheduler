#!/usr/bin/env python

from typing import Iterable
import datetime, random

from app import style
from app.schedule import demand

def random_demand(ps: list[datetime.datetime], styles: list[style.FabricStyle]) -> demand.Demand:
    return demand.Demand(random.choice(styles), max(0,random.normalvariate(mu=2500, sigma=500)),
                         random.choice(ps))

def main():
    style.init()

    start = datetime.datetime(2025, 8, 6)
    priorities = [start + datetime.timedelta(days=2),
                  start + datetime.timedelta(days=6),
                  start + datetime.timedelta(days=9),
                  start + datetime.timedelta(days=13)]
    
    style_names = ['FF AURA30000-39064-63', 'FF TAFFETAHP-38712-60',
                   'FF AU3426M-38840-62']
    styles: list[style.FabricStyle] = list(map(lambda name: style.get_fabric_style(name), style_names))

    dmnd_grp = demand.DemandGroup()
    for _ in range(100):
        dmnd_grp.add(random_demand(priorities, styles))
    
    print(dmnd_grp.pretty())

if __name__ == '__main__':
    main()