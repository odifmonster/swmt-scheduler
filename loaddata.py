#!/usr/bin/env python

import pandas as pd, datetime as dt

from app import style
from app.materials import Inventory, Roll
from app.schedule import DyeLot, Req, Demand, jet, Jet, Job

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

    for row in df.index:
        fab_id = df.loc[row, 'PA Fin Item']
        fab = style.fabric.get_style(fab_id)
        if not fab: continue

        buckets: list[tuple[int, float]] = []
        for i in range(1, 5):
            buckets.append((i, df.loc[row, f'P{i} New']))
        
        newreq = Req(fab, buckets, p1date)
        reqs.append(newreq)
        for order in newreq.orders:
            dmnd.add(order)
    
    return reqs, dmnd

def load_jets(start: dt.datetime) -> list[Jet]:
    jet.init(start)

    fpath, pdargs = excel.get_excel_info('adaptive_orders')
    df = pd.read_excel(fpath, **pdargs)
    df = df[~(df['StartTime'].isna() | df['EndTime'].isna())]

    for i in df.index:
        cur_jet = jet.get_by_alt_id(df.loc[i, 'Machine'])
        if cur_jet is None:
            continue

        job_id = df.loc[i, 'Dyelot']
        job_start = df.loc[i, 'StartTime']
        job_end = df.loc[i, 'EndTime']

        cur_lot = DyeLot.from_adaptive(job_id, job_start, job_end)
        cur_job = Job([cur_lot], job_start)
        cur_jet.add_adaptive_job(cur_job)
    
    jets = jet.get_jets()
    for j in jets:
        j.init_new_sched()
    
    return jets

if __name__ == '__main__':
    inv = load_inv()
    print(inv)