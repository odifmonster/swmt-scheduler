#!/usr/bin/env python

import pandas as pd

from app import style
from app.materials import Inventory, Roll

import excel

excel.init()
style.translate.init()
style.greige.init()

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

def load_demand() -> list[int]:
    return [0]

def load_jets() -> list[int]:
    return [0]

if __name__ == '__main__':
    inv = load_inv()
    print(inv)