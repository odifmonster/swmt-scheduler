#!/usr/bin/env python

import pandas as pd, datetime as dt

from app import style
from app.materials import Inventory, Roll
from app.schedule import Req, Demand

import excel

excel.init()
style.translate.init()
style.greige.init()
style.fabric.init()

def load_inv() -> Inventory:
    inv = Inventory()

    fpath, pdargs = excel.get_excel_info('inventory')
    df = pd.read_excel(fpath, **pdargs)
    df = df[(df['Quality'] == 'A') & df['ASSIGNED_ORDER'].isna()]

    for i in df.index:
        inv_id = df.loc[i, 'Item']
        grg_id = style.translate.get_plan_name(inv_id)
        if grg_id is None: continue
        grg = style.greige.get_style(grg_id)
        if grg is None: continue

        r = Roll(df.loc[i, 'Roll'], grg, df.loc[i, 'Pounds'])
        inv.add(r)
    
    return inv

def load_demand(p1date: dt.datetime) -> tuple[list[Req], Demand]:
    reqs: list[Req] = []
    dmnd = Demand()

    fpath, pdargs = excel.get_excel_info('pa_demand_plan')
    df = pd.read_excel(fpath, **pdargs)
    df = df.fillna(value={'P1 New': 0, 'P2 New': 0, 'P3 New': 0, 'P4 New': 0})
    df = df[~df['PA Fin Item'].isna()]

    for i in df.index:
        fab_id = df.loc[i, 'PA Fin Item']
        fab = style.fabric.get_style(fab_id)
        if not fab: continue

        buckets: list[tuple[int, float]] = []
        for i in range(1, 5):
            buckets.append(i, df.loc[i, f'P{i} New'])
        
        newreq = Req(fab, buckets, p1date)
        reqs.append(newreq)
        for order in newreq.orders:
            dmnd.add(order)
    
    return reqs, dmnd

def load_jets() -> list[int]:
    return [0]

if __name__ == '__main__':
    inv = load_inv()
    print(inv)