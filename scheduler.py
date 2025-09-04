#!/usr/bin/env python

from typing import Generator
import sys, os, math, datetime as dt, pandas as pd

from app import style
from app.support import logging
from app.style import GreigeStyle, color
from app.materials import Inventory, PortLoad, Snapshot
from app.schedule import DyeLot, Order, OrderView, Req, Demand, Jet, JetSched

from helpers import add_back_piece, apply_snapshot, get_init_tables, get_sched_tables, \
    get_late_tables, get_new_inv, get_logs_table, df_cols_to_string
from formatters import *
from loaddata import load_inv, load_demand, load_jets, LOGGER

style.greige.init()
style.fabric.init()

TODAY = dt.datetime.now()
_raw_monday = TODAY + dt.timedelta(days=0 - TODAY.weekday())
MONDAY = dt.datetime(year=_raw_monday.year, month=_raw_monday.month,
                     day=_raw_monday.day)

def try_load_jet(inv: Inventory, loads: Generator[PortLoad], jet: Jet, snapshot: Snapshot) \
    -> list[PortLoad]:
    ret: list[PortLoad] = []
    for i, load in enumerate(loads):
        ret.append(load)
        if i+1 == jet.n_ports: break
    
    if len(ret) < jet.n_ports:
        for load in ret:
            add_back_piece(inv, load.roll1, snapshot)
            if load.roll2:
                add_back_piece(inv, load.roll2, snapshot)
    
    return ret

@logging.logged_func(LOGGER, jload_args, jload_ret)
def get_jet_loads(inv: Inventory, greige: GreigeStyle, jet: Jet,
                  max_date: dt.datetime | None = None, create: bool = False) \
    -> tuple[Snapshot | None, list[PortLoad]]:
    snap = Snapshot()
    max_ret: list[PortLoad] = []
    
    for rview in inv.itervalues():
        roll = inv.remove(rview)
        roll.snapshot = snap
        inv.add(roll)

    for start in inv.get_starts(greige, jet.load_rng):
        pl_gen = inv.get_port_loads(greige, snap, jet.load_rng,
                                    start=start, max_date=max_date, create=create)
        ret = try_load_jet(inv, pl_gen, jet, snap)
        if len(ret) == jet.n_ports:
            return snap, ret

        if len(ret) > len(max_ret):
            max_ret = ret
    
    pl_gen = inv.get_port_loads(greige, snap, jet.load_rng, max_date=max_date,
                                create=create)
    ret = try_load_jet(inv, pl_gen, jet, snap)
    if len(ret) == jet.n_ports:
        return snap, ret
    elif len(ret) > len(max_ret):
        max_ret = ret

    return None, max_ret

@logging.logged_func(LOGGER, gpl_loop_args, gpl_loop_ret)
def gpl_loop(o1: Order, o2: Order, inv: Inventory, jet: Jet) \
    -> tuple[DyeLot, DyeLot, Snapshot] | str:
    if not (o1.item.can_run_on_jet(jet.id) and o2.item.can_run_on_jet(jet.id)):
        return 'Jet cannot run items'
    
    avg_load = o1.greige.port_rng.average()
    min_o1_ports = math.ceil(o1.total_lbs / avg_load)
    min_total_ports = math.ceil((o1.total_lbs+o2.lbs) / avg_load)

    if min_total_ports > jet.n_ports:
        return 'Minimum required ports exceeds jet size'
    if round((min_o1_ports / min_total_ports) * jet.n_ports) == jet.n_ports:
        return 'Split too uneven'

    max_due = min(o1.due_date, o2.due_date) - dt.timedelta(days=1)
    min_arrival = MONDAY + dt.timedelta(weeks=1, days=3)
    snap, loads = get_jet_loads(inv, o1.greige, jet, max_date=max_due)
    if snap is None:
        if o1.greige == style.greige.get_style('AU3426 WIDE'):
            snap, loads = get_jet_loads(inv, style.greige.get_style('AU3426'), jet,
                                        max_date=max_due)
        
        if snap is None:
            snap, loads = get_jet_loads(inv, o1.greige, jet,
                                        max_date=min_arrival,
                                        create=True)
    
    ports1 = round((min_o1_ports / min_total_ports) * jet.n_ports)
    lot1 = o1.assign(loads[:ports1])
    lot2 = o2.assign(loads[ports1:])
    
    return lot1, lot2, snap

def get_paired_lots(o1: Order, o2: Order, inv: Inventory, jets: list[Jet]) \
    -> dict[Jet, tuple[DyeLot, DyeLot, Snapshot]]:
    lots_map: dict[Jet, tuple[DyeLot, DyeLot, Snapshot]] = {}

    for jet in jets:
        res = gpl_loop(o1, o2, inv, jet)
        if type(res) is str: continue
        lots_map[jet] = res
    
    return lots_map

@logging.logged_func(LOGGER, gsl_loop_args, gsl_loop_ret)
def gsl_loop(order: Order, inv: Inventory, jet: Jet) -> tuple[DyeLot, Snapshot] | str:
    if not order.item.can_run_on_jet(jet.id):
        return 'Jet cannot run item'
    grg_due = order.due_date - dt.timedelta(days=1)
    min_arrival = MONDAY + dt.timedelta(weeks=1, days=3)
    snap, loads = get_jet_loads(inv, order.greige, jet, max_date=grg_due)
    flag = False
    if snap is None:
        flag = True
        if order.greige == style.greige.get_style('AU3426 WIDE'):
            snap, loads = get_jet_loads(inv, style.greige.get_style('AU3426'), jet,
                                        max_date=grg_due)
        
        if snap is None:
            snap, loads = get_jet_loads(inv, order.greige, jet,
                                        max_date=min_arrival,
                                        create=True)
        # return 'Could not fill jet'
    return order.assign(loads), snap

@logging.logged_func(LOGGER, single_lots_args, single_lots_ret)
def get_single_lots(order: Order, inv: Inventory, jets: list[Jet]) \
    -> dict[Jet, tuple[DyeLot, Snapshot]]:
    lots_map: dict[Jet, tuple[DyeLot, Snapshot]] = {}
    
    for jet in jets:
        ret = gsl_loop(order, inv, jet)
        if type(ret) is str: continue
        lots_map[jet] = ret
    
    return lots_map

def get_order_pairs(order: Order, dmnd: Demand) -> list[tuple[Order, Order]]:
    to_remove: list[OrderView] = list(dmnd.get_matches(order))
    ret: list[tuple[Order, Order]] = []
    for oview in to_remove:
        o2 = dmnd.remove(oview)
        ret.append((order, o2))
        dmnd.add(o2)
    return ret

@logging.logged_func(LOGGER, desc_args=all_lots_args, desc_ret=all_lots_ret)
def get_all_lots(order: Order, dmnd: Demand, inv: Inventory,
                 jets: list[Jet]) -> dict[Jet, list[tuple[DyeLot, *tuple[DyeLot, ...], Snapshot]]]:
    lots_map: dict[Jet, list[tuple[DyeLot, *tuple[DyeLot, ...], Snapshot]]] = {}

    single_lots = get_single_lots(order, inv, jets)
    for single_lot in single_lots:
        if single_lot in lots_map:
            lots_map[single_lot].append(single_lots[single_lot])
        else:
            lots_map[single_lot] = [single_lots[single_lot]]

    pairs = get_order_pairs(order, dmnd)
    for pair in pairs:
        paired_lots = get_paired_lots(pair[0], pair[1], inv, jets)
        for paired_lot in paired_lots:
            if paired_lot in lots_map:
                lots_map[paired_lot].append(paired_lots[paired_lot])
            else:
                lots_map[paired_lot] = [paired_lots[paired_lot]]
                
    return lots_map

@logging.logged_func(LOGGER, sc_cost_args, sc_cost_ret)
def sched_cost(jet: Jet) -> tuple[float, float, float]:
    shade_vals = {
        color.SOLUTION: 0, color.LIGHT: 5, color.MEDIUM: 10, color.BLACK: 20
    }
    not_seq_cost = 0
    non_black_9 = 0
    cur_jobs = jet.cur_sched.full_sched
    for job1, job2 in zip(cur_jobs[:-1], cur_jobs[1:]):
        if job1.shade in (color.STRIP, color.HEAVYSTRIP, color.EMPTY) or \
            job2.shade in (color.STRIP, color.HEAVYSTRIP, color.EMPTY):
            continue

        val1 = shade_vals[job1.shade]
        val2 = shade_vals[job2.shade]
        diff = val2 - val1
        if diff > 0:
            diff /= 2
        
        total_yds = sum(map(lambda l: l.yds, job2.lots))
        not_seq_cost += abs(diff*total_yds*0.01)

    strip_cost = 0
    cost_12_port_hrs = 150
    
    for job in cur_jobs:
        if job.shade in (color.STRIP, color.HEAVYSTRIP):
            hrs = (job.end - job.start).total_seconds() / 3600
            strip_cost += cost_12_port_hrs * (hrs / 12) * jet.n_ports
            
    return strip_cost, not_seq_cost, non_black_9

@logging.logged_func(LOGGER, order_cost_args, order_cost_ret)
def order_cost(order: Order | OrderView, next_avail: dt.datetime) -> float:
    if order.yds < 200:
        return 0

    table = order.late_table(next_avail)
    first_row = table[0]
    first_yds, first_delta = first_row
    cost = 0.0
    days_late_idxs = [4,5,6,10]
    start_cost_map = {4: 1000, 5:1500, 6:2500, 10:5000}
    scaling_map = {4:.01, 5: .015, 6: .025, 10: .5, 11: 1}
    found_idx = False
    index = 0
    
    for idx in days_late_idxs:
        if first_delta < dt.timedelta(days=idx) and not found_idx:
            cost += start_cost_map[idx]
            found_idx = True
            index = idx
    if not found_idx:
        cost += first_delta.days*1000
        index = 11
    
    for row in table:
        found_idx = False
        for idx in days_late_idxs:
            if row[1] < dt.timedelta(days=idx) and not found_idx:
                found_idx = True
                scalar = scaling_map[idx]
        if not found_idx:
            scalar = 0.1*row[1].days
        
        cost += row[0] * scalar

    if order.total_lbs > 0 and order.due_date >= next_avail:
        cost += 5000 + max(min(order.total_lbs, order.init_lbs), 500)
    return cost

@logging.logged_func(LOGGER, late_cost_args, late_cost_ret)
def late_cost(order: Order, dmnd: Demand, next_avail: dt.datetime) -> tuple[float, float]:
    cur_late = order_cost(order, next_avail)
    rem_late = 0.0
    end_cur_wk = order.due_date + dt.timedelta(days=5-order.due_date.weekday())

    for date in dmnd:
        if date > end_cur_wk: continue
        for other_order in dmnd[date].itervalues():
            rem_late += order_cost(other_order, next_avail)
            
    return cur_late, rem_late

def req_cost(req: Req) -> float:
    if not req.orders:
        return 0
    
    sorted_ords = sorted(req.orders, key=lambda o: o.due_date)
    if sorted_ords[-1].total_yds > 0:
        return 0
    return abs(sorted_ords[-1].total_yds) * .04

@logging.logged_func(LOGGER, inv_cost_args, inv_cost_ret)
def excess_inv_cost(order: Order, reqs: list[Req]) -> tuple[float, float]:
    cur_inv, rem_inv = 0, 0
    for req in reqs:
        if order.item == req.item:
            cur_inv += req_cost(req)
        else:
            rem_inv += req_cost(req)

    return cur_inv, rem_inv

@logging.logged_func(LOGGER, used_cost_args, used_cost_ret)
def used_inv_cost(inv: Inventory, extras: dict[GreigeStyle, list[PortLoad]], dmnd: Demand) -> float:
    needed_grg: dict[GreigeStyle, dict[dt.datetime, float]] = {}
    p4date = dt.datetime.fromtimestamp(0)
    for order in dmnd.itervalues():
        if order.pnum == 4:
            p4date = order.due_date
        rem_lbs = min(order.init_lbs, order.total_lbs)
        if rem_lbs <= 0: continue
        if order.greige not in needed_grg:
            needed_grg[order.greige] = {}
        if order.due_date not in needed_grg[order.greige]:
            needed_grg[order.greige][order.due_date] = 0
        needed_grg[order.greige][order.due_date] += rem_lbs
    
    avail_grg: dict[GreigeStyle, float] = {}
    for grg in inv:
        if grg not in avail_grg:
            avail_grg[grg] = 0
        for rview in inv[grg].itervalues():
            avail_grg[grg] += rview.lbs
    for grg in extras:
        if grg not in avail_grg:
            avail_grg[grg] = 0
        avail_grg[grg] += sum(map(lambda p: p.lbs, extras[grg]))

    used_cost = 0
    for grg in needed_grg:
        if grg not in avail_grg:
            avail_grg[grg] = 0

        dates = sorted(needed_grg[grg].keys())
        for date in dates:
            rem_needed = max(0, needed_grg[grg][date] - avail_grg[grg])
            avail_grg[grg] -= needed_grg[grg][date]
            days_late = (p4date - date).total_seconds() / (3600*24) + 1
            if days_late < 4:
                used_cost += rem_needed * 2.5 * 0.005
            elif days_late < 5:
                used_cost += rem_needed * 2.5 * 0.007
            elif days_late < 6:
                used_cost += rem_needed * 2.5 * 0.012
            elif days_late < 10:
                used_cost += rem_needed * 2.5 * 0.025
            else:
                used_cost += rem_needed * 2.5 * 0.5
    
    return used_cost

@logging.logged_func(LOGGER, cost_args, cost_ret)
def cost(jet: Jet, sched: JetSched, order: Order, dmnd: Demand, reqs: list[Req],
         snap: Snapshot, inv: Inventory, next_avail: dt.datetime) -> float:
    apply_snapshot(inv, snap)
    prevsched = jet.set_sched(sched)

    cur_late, rem_late = late_cost(order, dmnd, next_avail)
    cur_inv, rem_inv = excess_inv_cost(order, reqs)
    used_inv = used_inv_cost(inv, prevsched.free_greige(), dmnd)
    strips, not_seq, nb9 = sched_cost(jet)

    apply_snapshot(inv, None)
    jet.set_sched(prevsched)

    ret = sum((cur_late, rem_late, cur_inv, rem_inv, used_inv))
    all_jobs = list(filter(lambda j: j.shade not in (color.STRIP, color.HEAVYSTRIP),
                           jet.jobs))
    if jet.cur_sched.full_sched:
        ret += (strips+not_seq+nb9) / (len(all_jobs)*jet.n_ports)
    return ret

def key_sched(s_and_c: tuple[Jet, Snapshot | None, JetSched, float]):
    return s_and_c[-1]

@logging.logged_func(LOGGER, best_job_args, best_job_ret)
def get_best_job(lots_map: dict[Jet, list[tuple[DyeLot, tuple[DyeLot, ...], Snapshot]]],
                 order: Order, dmnd: Demand, reqs: list[Req], inv: Inventory,
                 next_avail: dt.datetime) \
                    -> tuple[Jet, Snapshot | None, JetSched, float] | None:
    sched_and_costs: list[tuple[Jet, Snapshot | None, JetSched, float]] = []
    cur_fri = order.due_date + dt.timedelta(days=4 - order.due_date.weekday())
    next_fri = max(next_avail, cur_fri + dt.timedelta(weeks=2))
    for jet in lots_map:
        for tup in lots_map[jet]:
            lots = tup[:-1]
            snapshot = tup[-1]
            index = jet.get_start_idx(lots, order.due_date)
            cur_jet_jobs = jet.cur_sched.jobs
            for i in range(index, len(cur_jet_jobs)+1):
                newsched, _ = jet.insert(lots, i)
                if newsched is not None:
                    newcost = cost(jet, newsched, order, dmnd, reqs, snapshot, inv,
                                   next_fri)
                    sched_and_costs.append((jet, snapshot, newsched, newcost))
        cur_cost = cost(jet, jet.cur_sched, order, dmnd, reqs, snapshot, inv,
                        next_fri)
        sched_and_costs.append((jet, None, jet.cur_sched, cur_cost))
    sorted_s_and_c = sorted(sched_and_costs, key=key_sched)
    if len(sorted_s_and_c) > 0:
        return sorted_s_and_c[0]
    return None

def add_back_free_loads(prevsched: JetSched, inv: Inventory) -> None:
    free_grg = prevsched.free_greige()
    for loads in free_grg.values():
        for load in loads:
            rview1 = inv.get(load.roll1.roll_id)
            roll1 = inv.remove(rview1, remkey=True)
            roll1.deallocate(load.roll1)
            inv.add(roll1)

            if load.roll2:
                rview2 = inv.get(load.roll2.roll_id)
                roll2 = inv.remove(rview2, remkey=True)
                roll2.deallocate(load.roll2)
                inv.add(roll2)

@logging.logged_func(LOGGER, desc_args=sched_ord_args, desc_ret=sched_ord_ret)
def schedule_order(order: Order, dmnd: Demand, reqs: list[Req], inv: Inventory,
                   jets: list[Jet], next_avail: dt.datetime) -> tuple[Order, bool]:
    lots_map = get_all_lots(order, dmnd, inv, jets)
    ret = get_best_job(lots_map, order, dmnd, reqs, inv, next_avail)
    if ret is None:
        return order, False
    
    best_jet, best_snap, best_sched, _ = ret

    apply_snapshot(inv, best_snap, temp=False)
    if best_snap is None:
        return order, False
    
    prevsched = best_jet.set_sched(best_sched)
    add_back_free_loads(prevsched, inv)
    return order, True

@logging.logged_func(LOGGER, desc_args=make_sched_args, desc_ret=make_sched_ret)
def make_schedule(dmnd: Demand, reqs: list[Req], inv: Inventory, jets: list[Jet],
                  next_avail: dt.datetime) -> None:
    dates = sorted(dmnd)
    for date in dates:
        print(f'Making schedule for orders for {date.strftime('%m/%d')}')
        views = sorted(dmnd[date].itervalues(), key=lambda o: o.init_yds)
        for oview in views:
            print(f'  Making schedule for {oview}')
            order = dmnd.remove(oview)

            while order.total_yds > 150:
                order, cont = schedule_order(order, dmnd, reqs, inv, jets,
                                             next_avail)
                if not cont:
                    break
            
            dmnd.add(order)

def get_input_tables(inv: Inventory, dmnd: Demand) \
    -> tuple[pd.DataFrame, pd.DataFrame]:
    inv_data, order_data = get_init_tables(inv, dmnd)

    roll_ids, inv_table = inv_data
    inv_df = pd.DataFrame(data=inv_table, index=roll_ids)
    inv_df = df_cols_to_string(inv_df, 'greige')

    order_ids, order_table = order_data
    order_df = pd.DataFrame(data=order_table, index=order_ids)
    order_df = df_cols_to_string(order_df, 'item')

    return inv_df, order_df

def write_output(writer: pd.ExcelWriter, logpath: str, inv_df: pd.DataFrame,
                 order_df: pd.DataFrame, inv: Inventory, dmnd: Demand, jets: list[Jet],
                 lgr: logging.Logger) -> None:
    jobs, lots, rolls = get_sched_tables(jets)

    job_ids, job_data = jobs
    jobs_df = pd.DataFrame(data=job_data, index=job_ids)
    jobs_df = df_cols_to_string(jobs_df, 'jet', 'greige', 'color')

    lot_ids, lot_data = lots
    lots_df = pd.DataFrame(data=lot_data, index=lot_ids)
    lots_df = df_cols_to_string(lots_df, 'jet', 'job', 'item', 'greige', 'color')

    rolls_df = pd.DataFrame(data=rolls)
    rolls_df = df_cols_to_string(rolls_df, 'jet', 'job', 'lot', 'greige', 'roll1', 'roll2',
                                 'item', 'color')
    
    new_ids, new_inv = get_new_inv(inv)
    new_inv_df = pd.DataFrame(data=new_inv, index=new_ids)
    
    inv_df = pd.concat([inv_df, new_inv_df])
    inv_df['date_needed'] = inv_df['avail_date']
    inv_df['used'] = 0
    inv_df['used'] = inv_df['used'].astype('float64')

    for i in inv_df.index:
        used1 = rolls_df[rolls_df['roll1'] == i]
        used2 = rolls_df[rolls_df['roll2'] == i]
        lbs_used, min_date = None, None

        if len(used1) > 0:
            lbs_used = sum(used1['lbs1'])
            min_date = min(used1['start'])
        if len(used2) > 0:
            if lbs_used is None:
                lbs_used = sum(used2['lbs2'])
                min_date = min(used2['start'])
            lbs_used += sum(used2['lbs2'])
            min_date = min(min_date, min(used2['start']))

        if lbs_used is not None:
            inv_df.loc[i, 'used'] = lbs_used
            inv_df.loc[i, 'date_needed'] = min_date
    
    late, late_detail, missing = get_late_tables(dmnd)

    order_ids, late_data = late
    late_df = pd.DataFrame(data=late_data, index=order_ids)
    late_df = df_cols_to_string(late_df, 'item')

    late_ids, late_detail_data = late_detail
    late_df2 = pd.DataFrame(data=late_detail_data, index=late_ids)
    late_df2 = df_cols_to_string(late_df2, 'order', 'item')

    miss_ids, miss_data = missing
    missing_df = pd.DataFrame(data=miss_data, index=miss_ids)
    missing_df = df_cols_to_string(missing_df, 'item')

    inv_df.to_excel(writer, sheet_name='inventory', float_format='%.2f',
                    index_label='roll_id')
    order_df.to_excel(writer, sheet_name='demand', float_format='%.2f',
                      index_label='order_id')
    jobs_df.to_excel(writer, sheet_name='jobs', float_format='%.2f', index_label='job_id')
    lots_df.to_excel(writer, sheet_name='dyelots', float_format='%.2f', index_label='lot_id')
    rolls_df.to_excel(writer, sheet_name='roll_allocation', float_format='%.2f',
                      index=False)
    late_df.to_excel(writer, sheet_name='late_orders', float_format='%.2f', index_label='order_id')
    late_df2.to_excel(writer, sheet_name='late_details', float_format='%.2f',
                      index_label='bucket_id')
    missing_df.to_excel(writer, sheet_name='not_scheduled', float_format='%.2f', index_label='order_id')
    
    all_logs = get_logs_table(lgr)
    for tup in all_logs:
        fname, proc_ids, logs_data = tup
        logs_df = pd.DataFrame(data=logs_data, index=proc_ids)
        logs_df = df_cols_to_string(logs_df, 'name', 'desc1', 'desc2', 'desc3')
        logs_df.to_csv(os.path.join(logpath, fname), sep='\t',
                       index_label='process_id')

def main(start_str: str, end_str: str):
    outpath = os.path.join(os.path.dirname(__file__), 'datasrc', 'output.xlsx')
    writer = pd.ExcelWriter(outpath, datetime_format='MM/DD HH:MM:SS')

    start = dt.datetime.fromisoformat(start_str)
    end = dt.datetime.fromisoformat(end_str)

    print('Loading program data...')
    inv, _ = load_inv(start)
    reqs, dmnd = load_demand(start)
    jets = load_jets(start, end)
    print('\rFinished loading data!')

    inv_df, dmnd_df = get_input_tables(inv, dmnd)
    friday = start + dt.timedelta(days=4 - start.weekday())
    make_schedule(dmnd, reqs, inv, jets, friday + dt.timedelta(weeks=2))
    write_output(writer, os.path.join(os.path.dirname(__file__), 'datasrc'),
                 inv_df, dmnd_df, inv, dmnd, jets, LOGGER)

    writer.close()

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])