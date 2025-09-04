#!/usr/bin/env python

from typing import Callable
import pandas as pd, datetime as dt, re, math

from app import style
from app.support.logging import Logger
from app.materials import roll, Inventory, Roll
from app.schedule import DyeLot, Req, Demand, jet, Jet, Job

import excel

excel.init()
style.translate.init()
style.greige.init()
style.fabric.init()

LOGGER = Logger()
Demand.set_logger(LOGGER)
Jet.set_logger(LOGGER)
Inventory.set_logger(LOGGER)
Roll.set_logger(LOGGER)

def agg_sched_info[T, U](start: dt.datetime, get_val: Callable[[pd.DataFrame, int], U],
                         reducer: Callable[[T, U], T], initial: T) -> T:
    res: T = initial
    fpath, pdargs = excel.get_excel_info('adaptive_orders')
    df = pd.read_excel(fpath, **pdargs)

    for i in df.index:
        if df.loc[i, 'StartTime'] > start:
            res = reducer(res, get_val(df, i))

    return res

def load_inv(start: dt.datetime) -> tuple[Inventory, dict[style.GreigeStyle, float]]:
    inv = Inventory()

    fpath, pdargs = excel.get_excel_info('inventory')
    inv_df = pd.read_excel(fpath, **pdargs)

    # def _reducer(res: set[str], val: str) -> set[str]:
    #     res.add(val)
    #     return res
    # ignored_lots = agg_sched_info(start, lambda df, i: df.loc[i, 'DyelotID1'],
    #                               _reducer, set())

    inv_df = inv_df[(inv_df['Quality'] == 'A') & inv_df['ASSIGNED_ORDER'].isna()]

    for i in inv_df.index:
        inv_id = inv_df.loc[i, 'Item']
        grg_id = style.translate.get_plan_name(inv_id)
        if grg_id is None: continue
        grg = style.greige.get_style(grg_id)
        if grg is None: continue

        roll_id = inv_df.loc[i, 'Roll']
        if roll_id[:2] == 'WF':
            plt = roll.WHITEVILLE
        else:
            plt = roll.FAIRYSTONE
        r = Roll(inv_df.loc[i, 'Roll'], grg, inv_df.loc[i, 'Pounds'],
                 dt.datetime.fromtimestamp(0), plt)
        inv.add(r)

    fpath, pdargs = excel.get_excel_info('incoming_si_greige')
    si_df = pd.read_excel(fpath, **pdargs)
    si_df['greige'] = si_df['greige'].str.upper()

    fpath, pdargs = excel.get_excel_info('incoming_wv_greige')
    wv_df = pd.read_excel(fpath, **pdargs)
    wv_df['greige'] = wv_df['greige'].str.upper()

    today = dt.datetime.now()
    raw_mon = today + dt.timedelta(days=0-today.weekday())
    monday = dt.datetime(year=raw_mon.year, month=raw_mon.month, day=raw_mon.day)
    max_date = monday + dt.timedelta(weeks=1, days=3)
    counter = 0

    weekly_plan: dict[style.GreigeStyle, float] = {}

    for i in si_df.index:
        grg_id = si_df.loc[i, 'greige']
        grg = style.greige.get_style(grg_id)
        if grg is None:
            continue

        if grg not in weekly_plan:
            weekly_plan[grg] = 0

        weekly_plan[grg] += si_df.loc[i, 'weekly_lbs']

        total_lbs = 0
        rolls_added = 0
        for wks in range(5):
            for days in range(5):
                avail_date = monday + dt.timedelta(weeks=wks, days=days)
                if avail_date <= today or avail_date >= max_date: continue
                total_lbs += si_df.loc[i, 'daily_lbs']
                nrolls = int(total_lbs / grg.roll_rng.average()) - rolls_added

                for j in range(nrolls):
                    r = Roll(f'FSPLAN{counter+j+1:06}', grg, grg.roll_rng.average(),
                             monday + dt.timedelta(weeks=wks, days=days),
                             roll.FAIRYSTONE)
                    inv.add(r)

                counter += nrolls
                rolls_added += nrolls

    for i in wv_df.index:
        grg_id = wv_df.loc[i, 'greige']
        grg = style.greige.get_style(grg_id)
        if grg is None:
            continue

        if grg not in weekly_plan:
            weekly_plan[grg] = 0
        
        weekly_plan[grg] += wv_df.loc[i, 'weekly_lbs']

        total_lbs = 0
        rolls_added = 0
        for wks in range(1, 5):
            avail_date = monday + dt.timedelta(weeks=wks, days=1)
            if avail_date <= today or avail_date >= max_date: continue

            total_lbs += wv_df.loc[i, 'weekly_lbs']
            nrolls = int(total_lbs / grg.roll_rng.average()) - rolls_added

            for j in range(nrolls):
                r = Roll(f'WFPLAN{counter+j+1:06}', grg, grg.roll_rng.average(),
                         monday + dt.timedelta(weeks=wks, days=1),
                         roll.WHITEVILLE)
                inv.add(r)

            counter += nrolls
            rolls_added += nrolls
    
    return inv, weekly_plan

def _parse_ship_day(day_str: str):
    day_str = day_str.lower()
    if 'every' in day_str or 'all' in day_str or 'any' in day_str:
        return { 'monday', 'tuesday', 'wednesday', 'thursday', 'friday' }

    main_pat = '[^a-z]*{}[^a-z]*'
    day_pats = {
        'monday': 'm(on(days?)?)?', 'tuesday': 't(u(e(s(days?)?)?)?)?',
        'wednesday': 'wed(nesdays?)?', 'thursday': 'th(ur(s(days?)?)?)?',
        'friday': 'f(ri(days?)?)?'
    }

    for day in day_pats:
        if re.match(main_pat.format(day_pats[day]), day_str) is not None:
            return day

    return None

def _parse_ship_days(days_str: str):
    comps = re.split(',|/|or|and', days_str)
    day_set = set()
    for comp in comps:
        day = _parse_ship_day(comp)
        if type(day) is set:
            return day
        elif day is None:
            print(f'could not parse {repr(comp)}')
        else:
            day_set.add(day)
    return day_set

def _map_ship_day(item, ship_days_data):
    if item in ship_days_data:
        return ship_days_data[item]
    return math.inf

def load_demand(start: dt.datetime) -> tuple[list[Req], Demand]:
    reqs: list[Req] = []
    dmnd = Demand()

    ship_path, ship_args = excel.get_excel_info('ship_dates')
    reqs_path, reqs_args = excel.get_excel_info('pa_min_reqs')

    ship_df = pd.read_excel(ship_path, **ship_args)
    ship_df = ship_df[ship_df['Ply1 Item'] != '0']

    days_map = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4
    }

    grouped = ship_df.groupby('Ply1 Item')
    ship_days_data = {}
    for name, group in grouped:
        ship_days = group['Ship Day'].unique()
        
        day_set = set()
        for ship_str in ship_days:
            if not pd.isna(ship_str):
                day_set |= _parse_ship_days(ship_str)

        days = [math.inf] + list(map(lambda x: days_map[x], day_set))
        ship_days_data[name] = min(days)

    # def _get_val(df: pd.DataFrame, i: int) -> tuple[str, float]:
    #     return (df.loc[i, 'FinItem'], df.loc[i, 'Qty'])
    # def _reducer(res: dict[str, float], val: tuple[str, float]) -> dict[str, float]:
    #     item, yds = val
    #     if item not in res:
    #         res[item] = 0
    #     res[item] += yds
    #     return res
    
    # not_avail = agg_sched_info(start, _get_val, _reducer, {})

    reqs_df = pd.read_excel(reqs_path, **reqs_args)
    reqs_df['Ship Day'] = reqs_df['Ply1 Item'].apply(lambda x: _map_ship_day(x, ship_days_data))

    today = dt.datetime.now()
    raw_mon = today + dt.timedelta(days=0-today.weekday())
    monday = dt.datetime(year=raw_mon.year, month=raw_mon.month, day=raw_mon.day)

    pairs = [(-1, 'past due')]
    for i in range(6):
        pairs.append((i, f'WK{i}'))

    for i in reqs_df.index:
        fab_id = reqs_df.loc[i, 'PA Item']
        fab = style.fabric.get_style(fab_id)
        if fab is None:
            print(f'Skipping demand on {repr(fab_id)}')
            continue

        fin = reqs_df.loc[i, 'PA Fin']
        insp = reqs_df.loc[i, 'Inspection']
        frame = reqs_df.loc[i, 'Frame']
        on_sched = reqs_df.loc[i, 'Dye Orders']

        total_avail = fin + insp + frame + on_sched
        # if fab.id in not_avail:
        #     total_avail -= not_avail[fab.id]

        cum_req = 0
        dates_yds: list[tuple[dt.datetime, float]] = []

        for wk_delta, col_end in pairs:
            req_raw = reqs_df.loc[i, f'FAB req\'d {col_end}']
            wkday = reqs_df.loc[i, 'Ship Day']
            if wkday == math.inf:
                wkday = 2

            lam_due_date = monday + dt.timedelta(weeks=wk_delta, days=wkday)
            due_date = lam_due_date - dt.timedelta(days=5)
            if due_date.weekday() > 4:
                due_date -= dt.timedelta(days=due_date.weekday() - 4)

            cum_req += req_raw
            cur_req_yds = max(0, min(req_raw, cum_req - total_avail))
            dates_yds.append((due_date, cur_req_yds))

        x = Req(fab, dates_yds)
        for o in x.orders:
            dmnd.add(o)
        reqs.append(x)
    
    return reqs, dmnd

def load_jets(start: dt.datetime, end: dt.datetime) -> list[Jet]:
    jet.init(start, end)

    fpath, pdargs = excel.get_excel_info('adaptive_orders')
    df = pd.read_excel(fpath, **pdargs)
    df = df[~(df['StartTime'].isna() | df['EndTime'].isna())]

    for i in df.index:
        cur_jet = jet.get_by_alt_id(df.loc[i, 'Machine'])
        if cur_jet is None:
            continue

        job_id = df.loc[i, 'DyelotID2']
        job_start = df.loc[i, 'StartTime']
        # if job_start > start: continue

        job_end = df.loc[i, 'EndTime']
        job_item = style.fabric.get_style(df.loc[i, 'FinItem'])
        if job_item is None:
            job_item = style.fabric.get_style('EMPTY')

        cur_lot = DyeLot.from_adaptive(job_id, job_item, job_start, job_end)
        cur_job = Job([cur_lot], job_start)
        cur_jet.add_adaptive_job(cur_job)
    
    jets = jet.get_jets()
    for j in jets:
        j.init_new_sched()
    
    return jets

if __name__ == '__main__':
    _, dmnd = load_demand(dt.datetime(2025, 8, 29, hour=8))
    print(dmnd)