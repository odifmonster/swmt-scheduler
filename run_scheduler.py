#!/usr/bin/env python

from typing import TypedDict
import os, datetime as dt, pandas as pd

from app.support import FloatRange

from app import style

from app.inventory.roll import Roll
from app.inventory import Inventory

from app.schedule.job import Job
from app.schedule.jet import Jet
from app.schedule.demand import Demand, DemandGroup
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
OUT_WRITER = ('output.xlsx', {'datetime_format': 'YYYY-MM-DD HH:MM'})

class NotScheduled(TypedDict):
    due_date: list[dt.datetime]
    fin_item: list[str]
    greige_item: list[str]
    yds_needed: list[float]
    lbs_needed: list[float]

class JetAlloc(TypedDict):
    job_id: list[str]
    starttime: list[dt.datetime]
    endtime: list[dt.datetime]
    jet: list[str]
    fin_item: list[str]
    greige_item: list[str]
    pounds: list[float]
    yards: list[float]

class RollAlloc(TypedDict):
    alloc_id: list[str]
    job_id: list[str]
    greige_item: list[str]
    roll: list[str]
    pounds: list[float]

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
            cur_job = Job(start, dt.timedelta(days=cur_job_days), start)
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

def assign_combo(jet_lots: dict[Jet, list[DyeLot]], max_date: dt.datetime) -> None:
    for jet in jet_lots:
        for lot in jet_lots[jet]:
            job = Job(jet.last_job_end, jet.avg_cycle, max_date, lots=(lot,))
            jet.add_job(job)

def try_jet_combo(dmnd: Demand, combo: tuple[Jet, ...], inv: Inventory,
                  checked: dict[int, bool], max_date: dt.datetime) -> bool:
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
    
    assign_combo(jet_lots, max_date)
    return True

def assign_multi_jets(start_date: dt.datetime, dmnd: Demand, jets: list[Jet],
                      inv: Inventory, ignore_due: bool = False) -> bool:
    checked: dict[int, bool] = {}
    for jet in jets:
        checked[jet.n_ports] = False

    max_date = dmnd.due_date
    if ignore_due:
        max_date = start_date+dt.timedelta(days=10)
    jet_combos = get_multi_jets(start_date, dmnd, jets, ignore_due=ignore_due)

    for combo in jet_combos:
        if combo is None:
            continue

        print('Trying combo ' + ', '.join([j.id for j in combo]))
        if all(map(lambda j: checked[j.n_ports], jets)):
            return False
        if try_jet_combo(dmnd, combo, inv, checked, max_date):
            print('Assigned to combo!')
            return True
    
    return False

def assign_single_jet(start_date: dt.datetime, dmnd: Demand, jets: list[Jet],
                      inv: Inventory, ignore_due: bool = False) -> bool:
    single_jets = get_single_jets(dmnd, jets, ignore_due=ignore_due)
    max_date = dmnd.due_date
    if ignore_due:
        max_date = start_date+dt.timedelta(days=10)

    for jet in single_jets:
        print(f'Checking {jet.id}')
        roll_splits = get_greige_rolls(inv, dmnd.item.greige, dmnd.pounds, jet)
        if not roll_splits: continue

        print(f'Assigning job to {jet.id}')
        lot = DyeLot(dmnd)

        for item in roll_splits:
            roll = inv.remove(item.roll.id)
            lot.assign_roll(roll, item.lbs)
            if roll.weight > 20:
                inv.add(roll)
        
        job = Job(jet.last_job_end, jet.avg_cycle, max_date, lots=(lot,))
        jet.add_job(job)
        return True
    
    return False

def assign_demand(dmnd: Demand, start_date: dt.datetime, jets: list[Jet], inv: Inventory,
                  ignore_due: bool = False) -> bool:
    prt_rng = dmnd.item.greige.port_range
    prt_avg = (prt_rng.minval+prt_rng.maxval)/2

    if prt_avg*8 > dmnd.pounds:
        print('Attempting to assign to single jet')
        success = assign_single_jet(start_date, dmnd, jets, inv, ignore_due=ignore_due)
        if success:
            return True
    
    print('Attempting to assign to multiple jets')
    success = assign_multi_jets(start_date, dmnd, jets, inv, ignore_due=ignore_due)
    return success

def convert_cols_to_string(df: pd.DataFrame, cols: list[str]) -> None:
    for col in cols:
        df[col] = df[col].astype('string')

def generate_schedule(start: dt.datetime) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    not_scheduled = NotScheduled(due_date=[], fin_item=[], greige_item=[], yds_needed=[],
                                 lbs_needed=[])

    inv = load_inv()
    dmnd = load_dmnd(start)
    jets = load_jets(start)

    pdates = sorted(iter(dmnd))
    for pdate in pdates:
        date_str = pdate.strftime('%a %b %d %Y')
        print(f'Scheduling for {date_str} ...')
        for grg in dmnd[pdate]:
            for clr in dmnd[pdate, grg]:
                for req_id in dmnd[pdate, grg, clr]:
                    if dmnd[pdate, grg, clr, req_id].yards < 100:
                        continue

                    req = dmnd.remove(req_id)
                    print(f'  Scheduling demand on item {req.item.id}...')
                    due_str = req.due_date.strftime('%a %b %d %Y')
                    print(f'    Attempting to schedule before {due_str}...')
                    success = assign_demand(req, start, jets, inv)
                    if success:
                        dmnd.add(req)
                        continue

                    print('    Attempting to schedule with no date restriction...')
                    success = assign_demand(req, start, jets, inv, ignore_due=True)
                    if not success:
                        not_scheduled['due_date'].append(req.due_date)
                        not_scheduled['fin_item'].append(req.item.id)
                        not_scheduled['greige_item'].append(req.item.greige.id)
                        not_scheduled['lbs_needed'].append(req.pounds)
                        not_scheduled['yds_needed'].append(req.yards)

                    print(f'  Finished processing demand on item {req.item.id}!')
                    dmnd.add(req)
        print(f'Finished scheduling all demand for {date_str}!')
    
    jet_alloc = JetAlloc(job_id=[], starttime=[], endtime=[], jet=[],
                         fin_item=[], greige_item=[], pounds=[], yards=[])
    roll_alloc = RollAlloc(alloc_id=[], job_id=[], greige_item=[], roll=[], pounds=[])

    for jet in jets:
        for job in jet:
            jet_alloc['job_id'].append(f'{job.id:05}')
            jet_alloc['starttime'].append(job.start)
            jet_alloc['endtime'].append(job.end)
            jet_alloc['jet'].append(jet.id)
            fab_item = job.lots[0].item
            jet_alloc['fin_item'].append(fab_item.id)
            jet_alloc['greige_item'].append(fab_item.greige.id)
            jet_alloc['pounds'].append(job.lbs)
            jet_alloc['yards'].append(job.yds)

            lot = job.lots[0]
            for aroll in lot:
                roll_alloc['alloc_id'].append(f'{aroll.id:05}')
                roll_alloc['job_id'].append(f'{job.id:05}')
                roll_alloc['greige_item'].append(aroll.roll.item.id)
                roll_alloc['roll'].append(aroll.roll.id)
                roll_alloc['pounds'].append(aroll.lbs)
    
    ns_df = pd.DataFrame(data=not_scheduled)
    convert_cols_to_string(ns_df, ['fin_item', 'greige_item'])

    jet_df = pd.DataFrame(data=jet_alloc, )
    convert_cols_to_string(jet_df, ['job_id', 'jet', 'fin_item', 'greige_item'])
    jet_df.set_index('job_id')

    roll_df = pd.DataFrame(data=roll_alloc)
    convert_cols_to_string(roll_df, ['alloc_id', 'job_id', 'greige_item'])
    roll_df.set_index('alloc_id')

    return jet_df, roll_df, ns_df

def main():
    style.init()
    style.translation.init()

    start = dt.datetime(2025, 8, 6)
    jobs, rolls, not_sched = generate_schedule(start)

    writer: pd.ExcelWriter = pd.ExcelWriter(os.path.join(DIRPATH, OUT_WRITER[0]), **OUT_WRITER[1])

    jobs.to_excel(writer, sheet_name='jet_allocation', index=False)
    rolls.to_excel(writer, sheet_name='roll_allocation', index=False)
    not_sched.to_excel(writer, sheet_name='not_scheduled')

    writer.close()

if __name__ == '__main__':
    main()