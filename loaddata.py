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
    epoch = dt.datetime.fromtimestamp(0)

    # def _reducer(res: set[str], val: str) -> set[str]:
    #     res.add(val)
    #     return res
    # ignored_lots = agg_sched_info(start, lambda df, i: df.loc[i, 'DyelotID1'],
    #                               _reducer, set())

    inv_df = inv_df[(inv_df['Quality'] == 'A') & inv_df['ASSIGNED_ORDER'].isna()]
    inv_df = inv_df[inv_df['Warehouse'] != 'CC']

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
                 epoch, epoch, epoch, plt)
        inv.add(r)

    fpath, pdargs = excel.get_excel_info('incoming_si_greige')
    si_df = pd.read_excel(fpath, **pdargs)
    si_df['Greige'] = si_df['Greige'].str.upper()

    fpath, pdargs = excel.get_excel_info('incoming_wv_greige')
    wv_df = pd.read_excel(fpath, **pdargs)
    wv_df['Greige'] = wv_df['Greige'].str.upper()

    today = dt.datetime.now()
    today = dt.datetime(today.year, today.month, today.day)
    raw_mon = today + dt.timedelta(days=0-today.weekday())
    avail1 = today + dt.timedelta(hours=10)
    if avail1.weekday() > 4:
        avail1 += dt.timedelta(days=2)
    avail2 = avail1 + dt.timedelta(days=1)
    if avail2.weekday() > 4:
        avail2 += dt.timedelta(days=2)
    monday = dt.datetime(year=raw_mon.year, month=raw_mon.month, day=raw_mon.day)
    max_date = today + dt.timedelta(weeks=1, hours=12)
    counter = 0

    weekly_plan: dict[style.GreigeStyle, float] = {}

    for i in si_df.index:
        grg_id = si_df.loc[i, 'Greige']
        grg = style.greige.get_style(grg_id)
        if grg is None:
            continue

        # if grg not in weekly_plan:
        #     weekly_plan[grg] = 0

        # weekly_plan[grg] += si_df.loc[i, 'weekly_lbs']

        total_lbs = 0
        rolls_added = 0
        if si_df.loc[i, 'Expected SI daily'] <= 0: continue

        for wks in range(5):
            for days in range(5):
                arrive_date = monday + dt.timedelta(weeks=wks, days=days, hours=10)
                if arrive_date < today or arrive_date > max_date: continue
                total_lbs += si_df.loc[i, 'Expected SI daily']
                wt = grg.roll_rng.average()
                if grg.id == 'ANMUT-C':
                    wt = grg.port_rng.average()
                nrolls = int(total_lbs / wt) - rolls_added

                for j in range(nrolls):
                    r = Roll(f'FSPLAN{counter+j+1:06}', grg, wt,
                             arrive_date, max(arrive_date, avail1), max(arrive_date, avail2),
                             roll.FAIRYSTONE)
                    inv.add(r)

                counter += nrolls
                rolls_added += nrolls

    for i in wv_df.index:
        grg_id = wv_df.loc[i, 'Greige']
        grg = style.greige.get_style(grg_id)
        if grg is None:
            continue

        # if grg not in weekly_plan:
        #     weekly_plan[grg] = 0
        
        # weekly_plan[grg] += wv_df.loc[i, 'weekly_lbs']

        total_lbs = 0
        rolls_added = 0
        avg_wkly_lbs = wv_df.loc[i, 'Expected WV 11/17']
        shipment1 = wv_df.loc[i, 'Expected WV 11/17']
        shipment2 = wv_df.loc[i, 'Expected WV 11/3']
        if avg_wkly_lbs <= 0: continue

        for wks in range(5):
            arrive_date = monday + dt.timedelta(weeks=wks, days=1, hours=10)
            arrive1 = dt.datetime(2025, 10, 7, hour=10)
            arrive2 = dt.datetime(2025, 10, 10, hour=10)
            if arrive_date < today or arrive_date > max_date: continue

            total_lbs += avg_wkly_lbs
            wt = grg.roll_rng.average()
            if grg.id == 'ANMUT-C':
                wt = grg.port_rng.average()
            
            nrolls = int(total_lbs / wt) - rolls_added

            for j in range(nrolls):
                r = Roll(f'WFPLAN{counter+j+1:06}', grg, wt,
                         arrive_date, max(arrive_date, avail1), max(arrive_date, avail2),
                         roll.WHITEVILLE)
                inv.add(r)

            counter += nrolls
            rolls_added += nrolls

            # total_lbs += shipment2
            # wt = grg.roll_rng.average()
            # if grg.id == 'ANMUT-C':
            #     wt = grg.port_rng.average()
            # nrolls = int(total_lbs / wt) - rolls_added

            # for j in range(nrolls):
            #     r = Roll(f'WFPLAN{counter+j+1:06}', grg, wt,
            #              arrive2, max(arrive2, avail1), max(arrive2, avail2),
            #              roll.WHITEVILLE)
            #     inv.add(r)

            # counter += nrolls
            # rolls_added += nrolls
    
    return inv, weekly_plan

def _parse_ship_day(day_str: str):
    day_str = day_str.lower()
    if 'every' in day_str or 'all' in day_str or 'any' in day_str:
        return { 'monday', 'tuesday', 'wednesday', 'thursday', 'friday' }

    main_pat = '[^a-z]*{}[^a-z]*'
    day_pats = {
        'monday': 'm(on(days?)?)?', 'tuesday': 't(u(e(s(days?)?)?)?)?',
        'wednesday': 'wed(nesdays?)?', 'thursday': 'th(u(r(s(days?)?)?)?)?',
        'friday': 'f(ri(days?)?)?'
    }

    for day in day_pats:
        if re.fullmatch(main_pat.format(day_pats[day]), day_str) is not None:
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

def sub_bsns_days(start: dt.datetime, ndays: int) -> dt.datetime:
    while ndays > 0:
        wkday = start.weekday()
        if ndays > wkday:
            subdays = wkday
            tdays = wkday + 2
        else:
            subdays = ndays
            tdays = ndays
        ndays -= subdays
        start -= dt.timedelta(days=tdays)
    return start

# The column of the demand tab that holds the safety replenishment: the
# additional yards to order per item to rebuild its safety stock.
SAFETY_COL = 'Safety'

def _read_reqs_sheet(fpath, pdargs: dict) -> pd.DataFrame:
    """
    Read the demand tab. Every column listed in data_info.txt must be in
    the sheet except the safety column, which older workbooks do not have.
    """
    args = dict(pdargs)
    cols = args.get('usecols')
    if not isinstance(cols, list):
        return pd.read_excel(fpath, **args)

    wanted = set(cols)
    args['usecols'] = lambda c: c in wanted
    df = pd.read_excel(fpath, **args)

    missing = wanted - set(df.columns) - {SAFETY_COL}
    if missing:
        raise ValueError(f'Columns not found in sheet {repr(args.get('sheet_name'))} '
                         f'of {fpath}: {sorted(missing)}')
    if SAFETY_COL in wanted and SAFETY_COL not in df.columns:
        print(f'No {repr(SAFETY_COL)} column in sheet {repr(args.get('sheet_name'))}; '
              'scheduling without safety stock')
    return df

def load_demand(start: dt.datetime, new_only: bool = True,
                use_lam_sched: bool = False,
                safety_stock: dict[str, float] | None = None) -> tuple[list[Req], Demand]:
    """
    Load the requirements and demand.

    Safety replenishment comes from the 'Safety' column of the demand tab:
    the additional yards to order per item to rebuild its safety stock.
    These yards are taken as given (they are not netted against on-hand
    fabric the way the hard requirements are) and become a trailing SAFETY
    order on the item's requirement. Rows of the same PA item are summed,
    like the requirements are.

    'safety_stock', when given, replaces the column: it maps a PA item id
    to its safety yards. Pass an empty dict to schedule without safety.
    """
    reqs: list[Req] = []
    dmnd = Demand()

    ship_path, ship_args = excel.get_excel_info('ship_dates')

    if use_lam_sched:
        reqs_path, reqs_args = excel.get_excel_info('pa_min_reqs2')
    else:
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
        sched_days = group['Schedule Day']
        # print(', '.join(list(filter(lambda x: not pd.isna(x), ship_days))), end=' ')
        
        day_set = set()
        for ship_str in ship_days:
            if not pd.isna(ship_str):
                day_set |= _parse_ship_days(ship_str)
        
        # print(name, day_set)

        days = [math.inf] + list(map(lambda x: days_map[x], day_set))
        ship_days_data[name] = min(sched_days)-2

    # def _get_val(df: pd.DataFrame, i: int) -> tuple[str, float]:
    #     return (df.loc[i, 'FinItem'], df.loc[i, 'Qty'])
    # def _reducer(res: dict[str, float], val: tuple[str, float]) -> dict[str, float]:
    #     item, yds = val
    #     if item not in res:
    #         res[item] = 0
    #     res[item] += yds
    #     return res
    
    # not_avail = agg_sched_info(start, _get_val, _reducer, {})

    reqs_df = _read_reqs_sheet(reqs_path, reqs_args)
    to_drop = reqs_df[reqs_df['PA Item'].isna()].index
    reqs_df = reqs_df.drop(to_drop)
    if SAFETY_COL in reqs_df.columns:
        reqs_df[SAFETY_COL] = pd.to_numeric(reqs_df[SAFETY_COL], errors='coerce').fillna(0)
    else:
        reqs_df[SAFETY_COL] = 0.0
    n_safety, total_safety = 0, 0.0
    if not use_lam_sched:
        reqs_df['Ship Day'] = reqs_df['Ply1 Item'].apply(lambda x: _map_ship_day(x, ship_days_data))

    today = dt.datetime.now()
    if today.weekday() == 6:
        today += dt.timedelta(days=1)
    raw_mon = today + dt.timedelta(days=0-today.weekday())
    monday = dt.datetime(year=raw_mon.year, month=raw_mon.month, day=raw_mon.day)

    pairs = [(-1, 'past due')]
    for i in range(13):
        pairs.append((i, f'WK{i}'))

    for fab_id, grp in reqs_df.groupby('PA Item'):
        if safety_stock is None:
            safety_yds = max(0.0, float(sum(grp[SAFETY_COL])))
        else:
            safety_yds = max(0.0, float(safety_stock.get(fab_id, 0)))

        fab = style.fabric.get_style(fab_id)
        if fab is None:
            if safety_yds > 0:
                print(f'Skipping demand on {repr(fab_id)} '
                      f'(including {safety_yds:.0f} yds of safety stock)')
            else:
                print(f'Skipping demand on {repr(fab_id)}')
            continue

        transit = sum(grp['In transit'])
        fin = max(grp['PA Fin'])
        insp = max(grp['Inspection']) * 0.9
        frame = max(grp['Frame']) * 0.85
        on_sched = max(grp['Dye Orders']) * 0.85

        if new_only:
            total_avail = transit + fin + insp + frame + on_sched
        else:
            total_avail = transit + fin
        # if fab.id in not_avail:
        #     total_avail -= not_avail[fab.id]

        cum_req = 0
        dates_yds: list[tuple[int, dt.datetime, float]] = []

        wkday = min(grp['Ship Day']) - 2
        if wkday == math.inf:
            wkday = 2

        for wk_delta, col_end in pairs:
            req_raw = sum(grp[f'FAB req\'d {col_end}'])
            if col_end == 'past due':
                pnum = -1
            else:
                pnum = int(col_end[2:])

            lam_due_date = monday + dt.timedelta(weeks=wk_delta, days=wkday)
            due_date = sub_bsns_days(lam_due_date, 4)

            cum_req += req_raw
            cur_req_yds = max(0, min(req_raw, cum_req - total_avail))
            dates_yds.append((pnum, due_date, cur_req_yds))

        # safety stock goes in a bucket after the last hard requirement, so
        # it is scheduled after every hard order and never counts as late
        safety = None
        if safety_yds > 0:
            last_wk = pairs[-1][0]
            lam_safety_date = monday + dt.timedelta(weeks=last_wk+1, days=wkday)
            safety = (last_wk+1, sub_bsns_days(lam_safety_date, 4), safety_yds)
            n_safety += 1
            total_safety += safety_yds

        x = Req(fab, dates_yds, safety=safety)
        for o in x.orders:
            dmnd.add(o)
        reqs.append(x)

    print(f'Loaded safety stock replenishment for {n_safety} items '
          f'({total_safety:.0f} yds)')
    return reqs, dmnd

def load_jets(start: dt.datetime, end: dt.datetime) -> list[Jet]:
    jet.init(start, end)

    fpath, pdargs = excel.get_excel_info('adaptive_orders')
    df = pd.read_excel(fpath, **pdargs)
    df = df[~(df['start'].isna() | df['end'].isna())]
    moveable_df = df
    
    jets = jet.get_jets()

    for job, grp in moveable_df.groupby('job'):
        first = list(grp.index)[0]

        cur_jet = jet.get_by_alt_id(moveable_df.loc[first, 'machine'])
        if cur_jet is None: continue

        job_start = max(grp['start'])
        job_end = max(grp['end'])
        lots = []

        for i in grp.index:
            item = style.fabric.get_style(moveable_df.loc[i, 'item1'])
            if item is None:
                item = style.fabric.get_style('EMPTY')
        
            lot_lbs = moveable_df.loc[i, 'qty'] / item.yld
            cur_lot = DyeLot.from_adaptive(moveable_df.loc[i, 'dyelot'], item, job_start,
                                           job_end, alt_lbs=lot_lbs)
            lots.append(cur_lot)

        cur_job = Job(lots, job_start, job_id=job)
        cur_jet.add_adaptive_job(cur_job)
    
    for j in jets:
        j.init_new_sched()
    
    return jets

if __name__ == '__main__':
    _, dmnd = load_demand(dt.datetime(2025, 8, 29, hour=8))
    print(dmnd)