#!/usr/bin/env python

import pandas as pd, datetime as dt

from app import style
from app.inventory import Inventory, Roll
from app.schedule import Req, Demand, Job, Jet, jet

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

def load_adaptive_jobs(start: dt.datetime, end: dt.datetime) -> list[Jet]:
    jet.init(start, end)

    fpath, pdargs = excel.get_excel_info('adaptive_orders')
    df = pd.read_excel(fpath, **pdargs)
    df = df[~(df['StartTime'].isna() | df['EndTime'].isna())]

    for i in df.index:
        cur_jet = jet.get_jet_by_alt(df.loc[i, 'Machine'])
        if cur_jet is None: continue

        job_id = df.loc[i, 'Dyelot']
        if 'STRIP' in job_id:
            cur_job = Job.make_strip(False, df.loc[i, 'StartTime'], end=df.loc[i, 'StartTime'],
                                     id=job_id)
        else:
            cur_job = Job.make_placeholder(df.loc[i, 'Dyelot'], df.loc[i, 'StartTime'],
                                           df.loc[i, 'EndTime'])
        cur_jet.add_placeholder(cur_job)
    
    ret = jet.get_jets()
    for j in ret:
        j.init_new_sched()
        print(j.id, j.sched.jobs_since_strip)
    
    return ret

if __name__ == '__main__':
    inv = load_inv()
    print(inv)