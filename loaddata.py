#!/usr/bin/env python

import pandas as pd, datetime as dt

from app import style
from app.inventory import Inventory, Roll
from app.schedule import Req, Demand

import excel
excel.init()

style.translation.init()
style.greige.init()
style.fabric.init()

def load_inv() -> Inventory:
    inv = Inventory()

    fpath, pdargs = excel.get_excel_info('inventory')
    df = pd.read_excel(fpath, **pdargs)
    df = df[(df['Quality'] == 'A') & df['ASSIGNED_ORDER'].isna()]

    for i in df.index:
        grg_id = style.translation.translate_greige(df.loc[i, 'Item'])
        if grg_id is None:
            continue

        grg = style.greige.get_greige_style(grg_id)
        if grg is None:
            continue

        roll = Roll(df.loc[i, 'Roll'], grg, df.loc[i, 'Pounds'])
        inv.add(roll)
    
    return inv

def load_demand(p1date: dt.datetime) -> Demand:
    dmnd = Demand()

    fpath, pdargs = excel.get_excel_info('pa_demand_plan')
    df = pd.read_excel(fpath, **pdargs)
    df = df.fillna(value={'P1 New': 0, 'P2 New': 0, 'P3 New': 0, 'P4 New': 0})
    df = df[~df['PA Fin Item'].isna()]

    for i in df.index:
        fab = style.fabric.get_fabric_style(df.loc[i, 'PA Fin Item'])
        if fab is None:
            continue

        buckets = (df.loc[i, 'P1 New'], df.loc[i, 'P2 New'],
                   df.loc[i, 'P3 New'], df.loc[i, 'P4 New'])
        req = Req(fab, p1date, buckets)
        dmnd.add(req)
    
    return dmnd

if __name__ == '__main__':
    dmnd = load_demand(dt.datetime(2025, 8, 13))
    print(dmnd)