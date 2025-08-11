#!/usr/bin/env python

import os, datetime as dt, pandas as pd

from app.support import FloatRange

from app import style

from app.inventory.roll import Roll, RollLike
from app.inventory import Inventory

from app.schedule.job import Job
from app.schedule.jet import Jet
from app.schedule.demand import Demand, DemandGroup, DemandView
from app.schedule.dyelot import DyeLot
from app.schedule.job import Job

from getjets import get_single_jets, get_multi_jets
from getrolls import get_greige_rolls, RollSplitItem

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

def load_jets(start: dt.datetime) -> list[Jet]:
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
            cur_job = Job(start, dt.timedelta(days=cur_job_days))
            cur_jet.add_job(cur_job)
    
    return res

def load_dmnd(start: dt.datetime) -> DemandGroup:
    res = DemandGroup()

    dmnd_path = os.path.join(DIRPATH, DMND_SRC[0])
    dmnd_df: pd.DataFrame = pd.read_excel(dmnd_path, **DMND_SRC[1])
    dmnd_df = dmnd_df[~dmnd_df['PA Fin Item'].isna()]

    prts = {
        'P1 New': start + dt.timedelta(days=2.5),
        'P2 New': start + dt.timedelta(days=6.5),
        'P3 New': start + dt.timedelta(days=9.5),
        'P4 New': start + dt.timedelta(days=13.5)
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

def tjc_update(inv: Inventory, allocated: dict[str, set[DyeLot]], empty: list[Roll],
               jet_lots: dict[Jet, list[DyeLot]], lot: DyeLot, jet: Jet,
               roll_splits: list[RollSplitItem]) -> None:
    for item in roll_splits:
        if item.roll.id not in allocated:
            allocated[item.roll.id] = set()
        if lot not in allocated[item.roll.id]:
            allocated[item.roll.id].add(lot)

        roll = inv.remove(item.roll.id)
        lot.assign_roll(roll, item.lbs)
        if roll.weight <= 20:
            empty.append(roll)
        else:
            inv.add(roll)
        
    jet_lots[jet].append(lot)

def tjc_reset(inv: Inventory, allocated: dict[str, set[DyeLot]], empty: list[Roll]) -> None:
    for roll in empty:
        inv.add(roll)

    for rid, rlots in allocated.items():
        roll = inv.remove(rid)
        for lot in rlots:
            lot.unassign_roll(roll)
        inv.add(roll)

def assign_combo(jet_lots: dict[Jet, list[DyeLot]]) -> None:
    for jet in jet_lots:
        for lot in jet_lots[jet]:
            job = Job(jet.last_job_end, jet.avg_cycle, lots=(lot,))
            jet.add_job(job)

def try_jet_combo(dmnd: Demand, combo: tuple[Jet, ...], inv: Inventory,
                  checked: dict[int, bool]) -> bool:
    allocated: dict[str, set[DyeLot]] = {}
    empty: list[Roll] = []
    jet_lots: dict[Jet, list[DyeLot]] = {}

    prt_rng = dmnd.item.greige.port_range
    prt_avg = (prt_rng.minval+prt_rng.maxval)/2
    total_over = 0
    
    for jet in combo:
        if checked[jet.n_ports]:
            break

        roll_splits = get_greige_rolls(inv, dmnd.item.greige, jet.n_ports*prt_avg, jet,
                                       allowance=max(0, total_over))
        if not roll_splits:
            checked[jet.n_ports] = True
            break

        cur_lbs = sum(map(lambda x: x.lbs, roll_splits))
        cur_over = cur_lbs - prt_avg*jet.n_ports
        total_over += cur_over

        if jet not in jet_lots:
            jet_lots[jet] = []
        lot = DyeLot(dmnd)
        tjc_update(inv, allocated, empty, jet_lots, lot, jet, roll_splits)

    if dmnd.yards >= 100:
        tjc_reset(inv, allocated, empty)
        return False
    
    assign_combo(jet_lots)
    return True

def assign_multi_jets(start_date: dt.datetime, dmnd: Demand, jets: list[Jet],
                      inv: Inventory, ignore_due: bool = False) -> bool:
    checked: dict[int, bool] = {}
    for jet in jets:
        checked[jet.n_ports] = False

    jet_combos = get_multi_jets(start_date, dmnd, jets, ignore_due=ignore_due)

    for combo in jet_combos:
        if all(map(lambda j: checked[j.n_ports], jets)):
            return False
        if try_jet_combo(dmnd, combo, inv, checked):
            return True
    
    return False

def main():
    style.init()
    style.translation.init()

    start = dt.datetime(2025, 8, 6)

    inv = load_inv()
    jets = load_jets(start)

    fab = style.get_fabric_style('FF ARCTIC-39811-68')
    assert not fab is None
    p2 = start + dt.timedelta(days=2.5)

    dmnd = Demand(fab, 9767, p2)
    success = assign_multi_jets(start, dmnd, jets, inv, ignore_due=True)

    if success:
        for jet in jets:
            print(f'{jet.id} schedule:')
            for job in jet:
                print('  ' + repr(job))
                lot = job.lots[0]
                for roll_alloc in lot:
                    print(f'    roll={roll_alloc.roll.id}\tlbs={roll_alloc.lbs:.2f}')
            print()

if __name__ == '__main__':
    main()