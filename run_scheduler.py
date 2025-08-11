#!/usr/bin/env python

import os, datetime, pandas as pd

from app.support import FloatRange

from app import style

from app.inventory.roll import Roll
from app.inventory import Inventory

from app.schedule.job import Job
from app.schedule.jet import Jet
from app.schedule.demand import Demand, DemandGroup

from getjets import get_multi_jets

DIRPATH = '/Users/lamanwyner/Desktop/Shawmut Projects/Scheduling'
INV_SRC = ('master.xlsx', {'sheet_name': 'inventory',
                           'usecols': ['Roll', 'Item', 'Quality', 'Pounds',
                                       'ASSIGNED_ORDER'],
                           'dtype': {'Roll': 'string', 'Item': 'string',
                                     'Quality': 'string', 'ASSIGNED_ORDER': 'string'}})
JET_SRC = ('master.xlsx', {'sheet_name': 'jet_info',
                           'dtype': {'id': 'string'}})
DMND_SRC = ('Demand Planning 20250806.xlsx', {'sheet_name': 'Demand Planning20230927',
                                              'usecols': 'D,M:P', 'header': 7,
                                              'dtype': {'PA Fin Item': 'string'}})

def load_inv() -> Inventory:
    res = Inventory()

    inv_path = os.path.join(DIRPATH, INV_SRC[0])
    inv_df: pd.DataFrame = pd.read_excel(inv_path, **INV_SRC[1])
    inv_df = inv_df[(inv_df['Pounds'] > 0) & (inv_df['Quality'] == 'A') & inv_df['ASSIGNED_ORDER'].isna()]

    for i in inv_df.index:
        inv_grg = inv_df.loc[i, 'Item']
        grg_id = style.translation.translate_greige_style(inv_grg)
        if not grg_id: continue

        roll_id = inv_df.loc[i, 'Roll']
        grg = style.get_greige_style(grg_id)
        if not grg: continue

        wt = inv_df.loc[i, 'Pounds']
        res.add(Roll(roll_id, grg, wt))
    
    return res

def load_jets(start: datetime.datetime) -> list[Jet]:
    res: list[Jet] = []

    jet_path = os.path.join(DIRPATH, JET_SRC[0])
    jet_df: pd.DataFrame = pd.read_excel(jet_path, **JET_SRC[1])

    for i in jet_df.index:
        rng = FloatRange(jet_df.loc[i, 'port_min'],
                         jet_df.loc[i, 'port_max'])
        
        cur_jet = Jet(jet_df.loc[i, 'id'],
                      jet_df.loc[i, 'turns'],
                      jet_df.loc[i, 'n_ports'],
                      rng, start)
        res.append(cur_jet)

        cur_job_days = jet_df.loc[i, 'days_sch']
        if cur_job_days > 0:
            if cur_job_days > 3:
                cur_job_days += 2
            cur_job = Job(start, datetime.timedelta(days=cur_job_days))
            cur_jet.add_job(cur_job)
    
    return res

def load_dmnd(start: datetime.datetime) -> DemandGroup:
    res = DemandGroup()

    dmnd_path = os.path.join(DIRPATH, DMND_SRC[0])
    dmnd_df: pd.DataFrame = pd.read_excel(dmnd_path, **DMND_SRC[1])
    dmnd_df = dmnd_df[~dmnd_df['PA Fin Item'].isna()]

    prts = {
        'P1 New': start + datetime.timedelta(days=2.5),
        'P2 New': start + datetime.timedelta(days=6.5),
        'P3 New': start + datetime.timedelta(days=9.5),
        'P4 New': start + datetime.timedelta(days=13.5)
    }

    for i in dmnd_df.index:
        fab_id = dmnd_df.loc[i, 'PA Fin Item']
        fab = style.get_fabric_style(fab_id)
        if not fab: continue

        for prt in prts:
            yds = dmnd_df.loc[i, prt]
            if yds == 0: continue
            cur_item = Demand(fab, yds, prts[prt])
            res.add(cur_item)
    
    return res

def main():
    style.init()
    style.translation.init()

    start = datetime.datetime(2025, 8, 6)

    jets = load_jets(start)
    test_fab = style.get_fabric_style('FF ARCTIC-39811-68')
    assert not test_fab is None

    test_dmnd = Demand(test_fab, 9767, start+datetime.timedelta(days=2.5))
    jet_combs = get_multi_jets(start, test_dmnd, jets, ignore_due=True)

    for jcomb in jet_combs:
        print('Combo:')
        for jet in jcomb:
            print(f'  {jet.id} (ports={jet.n_ports})')
        print()

if __name__ == '__main__':
    main()