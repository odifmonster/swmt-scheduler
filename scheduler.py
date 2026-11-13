#!/usr/bin/env python

from typing import Generator, Callable, NamedTuple
import sys, os, math, datetime as dt, pandas as pd

from app import style
from app.support import logging
from app.style import GreigeStyle, color
from app.materials import Inventory, PortLoad, Snapshot, RollView
from app.schedule import DyeLot, Order, OrderView, Req, Demand, Jet, JetSched, \
    Job

from helpers import add_back_piece, apply_snapshot, get_init_tables, get_sched_tables, \
    get_late_tables, get_new_inv, get_lot_pnums, df_cols_to_string, get_logs_table, \
    get_safety_table
from formatters import *
from loaddata import load_inv, load_demand, load_jets, LOGGER

style.greige.init()
style.fabric.init()

# Cost per yard of safety stock left unbuilt. This is deliberately small next
# to the late costs on hard orders (which start at 1000 per order), so safety
# only wins a jet slot when nothing with a real due date wants it. It still
# has to outweigh the jet sequencing costs of an extra job, which are single
# digits once averaged over a jet's schedule.
SAFETY_YD_COST = 0.05

# Whether a safety order may create planned (not yet knit) greige when the
# inventory cannot fill a jet. Safety stock is built opportunistically from
# greige that is on hand or already expected, so by default it may not.
SAFETY_CREATE_GREIGE = False

_raw_today = dt.datetime.now()
TODAY = dt.datetime(year=_raw_today.year, month=_raw_today.month, day=_raw_today.day)
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
def get_jet_loads(inv: Inventory, greige: GreigeStyle, jet: Jet, min_pnum: int,
                  max_date: dt.datetime | None = None, create: bool = False,
                  snap: Snapshot | None = None) \
    -> tuple[Snapshot | None, list[PortLoad]]:
    if snap is None:
        snap = Snapshot()
    max_ret: list[PortLoad] = []

    alt_grg = None

    def concat_gens[T: PortLoad | RollView](gen1: Generator[T],
                                            gen2: Generator[T]):
        yield from gen1
        yield from gen2
    
    for rview in inv.itervalues():
        roll = inv.remove(rview)
        roll.snapshot = snap
        inv.add(roll)

    starts = inv.get_starts(greige, jet.load_rng, jet.n_ports, min_pnum)
    if alt_grg is not None:
        starts1 = starts
        starts2 = inv.get_starts(alt_grg, jet.load_rng, jet.n_ports, min_pnum)
        starts = concat_gens(starts1, starts2)

    for start in starts:
        pl_gen = inv.get_port_loads(start.item, snap, jet.load_rng, jet.n_ports,
                                    min_pnum, start=start, max_date=max_date,
                                    create=create)

        ret = try_load_jet(inv, pl_gen, jet, snap)
        if len(ret) == jet.n_ports:
            return snap, ret

        if len(ret) > len(max_ret):
            max_ret = ret
    
    pl_gen = inv.get_port_loads(greige, snap, jet.load_rng, jet.n_ports, min_pnum,
                                max_date=max_date, create=create)
    ret = try_load_jet(inv, pl_gen, jet, snap)
    if len(ret) == jet.n_ports:
        return snap, ret
    
    if alt_grg is not None:
        pl_gen = inv.get_port_loads(alt_grg, snap, jet.load_rng, jet.n_ports, min_pnum,
                                    max_date=max_date, create=create)
        ret = try_load_jet(inv, pl_gen, jet, snap)
    if len(ret) == jet.n_ports:
        return snap, ret
    
    if len(ret) > len(max_ret):
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
    o1pct = min_o1_ports / min_total_ports
    ports1 = math.ceil(o1pct * (jet.n_ports / 2)) * 2

    if min_total_ports > jet.n_ports or jet.n_ports < 4:
        return 'Minimum required ports exceeds jet size'
    if ports1 == jet.n_ports:
        return 'Split too uneven'

    max_due = min(o1.due_date, o2.due_date) - dt.timedelta(days=1)
    min_arrival = TODAY + dt.timedelta(weeks=1, hours=10)
    snap, loads = get_jet_loads(inv, o1.greige, jet, min(o1.pnum, o2.pnum), max_date=max_due)
    if snap is None:
        # the partial loads were already handed back to inventory
        if (o1.safety or o2.safety) and not SAFETY_CREATE_GREIGE:
            return 'Could not fill jet without new greige for safety stock'
        snap, loads = get_jet_loads(inv, o1.greige, jet, min(o1.pnum, o2.pnum),
                                    max_date=min_arrival,
                                    create=True)

    lot1 = o1.assign(loads[:ports1])
    lot2 = o2.assign(loads[ports1:])
    
    return lot1, lot2, snap

def get_paired_lots(o1: Order, o2: Order, inv: Inventory, jets: list[Jet]) \
    -> dict[Jet, tuple[DyeLot, DyeLot, Snapshot]]:
    lots_map: dict[Jet, tuple[DyeLot, DyeLot, Snapshot]] = {}

    for jet in jets:
        # print(f'      rolls for paired lot on {jet.id}')
        res = gpl_loop(o1, o2, inv, jet)
        if type(res) is str: continue
        lots_map[jet] = res
    
    return lots_map

@logging.logged_func(LOGGER, gsl_loop_args, gsl_loop_ret)
def gsl_loop(order: Order, inv: Inventory, jet: Jet) -> tuple[DyeLot, Snapshot] | str:
    if not order.item.can_run_on_jet(jet.id):
        return 'Jet cannot run item'
    grg_due = order.due_date - dt.timedelta(days=1)
    min_arrival = TODAY + dt.timedelta(weeks=1, hours=10)
    snap, loads = get_jet_loads(inv, order.greige, jet, order.pnum, max_date=grg_due)
    flag = False
    if snap is None:
        # the partial loads were already handed back to inventory
        if order.safety and not SAFETY_CREATE_GREIGE:
            return 'Could not fill jet without new greige for safety stock'
        flag = True
        snap, loads = get_jet_loads(inv, order.greige, jet, order.pnum,
                                    max_date=min_arrival,
                                    create=True)
        # return 'Could not fill jet'
    return order.assign(loads), snap

@logging.logged_func(LOGGER, single_lots_args, single_lots_ret)
def get_single_lots(order: Order, inv: Inventory, jets: list[Jet]) \
    -> dict[Jet, tuple[DyeLot, Snapshot]]:
    lots_map: dict[Jet, tuple[DyeLot, Snapshot]] = {}
    est_ports1 = math.ceil(max(order.init_lbs, order.total_lbs) \
                           / order.greige.port_rng.average())
    est_ports2 = math.ceil(max(0, order.total_lbs) \
                           / order.greige.port_rng.average())

    max_ports = max(map(lambda j: j.n_ports, filter(lambda j: order.item.can_run_on_jet(j.id), jets)))
    
    for jet in jets:
        if est_ports2 >= 8 and jet.n_ports <= min(4, max_ports): continue
        if est_ports1 < 4 and est_ports2 < 4 and jet.n_ports > 4: continue
        if jet.n_ports < min(4, max_ports) and est_ports2 / jet.n_ports > 1: continue
        if jet.n_ports == 1: continue
        # print(f'      rolls for single lot on {jet.id}')
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

def get_multi_jets(order: Order, jets: list[Jet], prev: tuple[Jet, ...]) \
    -> Generator[tuple[Jet, ...]]:
    total = order.total_lbs
    ports = math.ceil(total / order.greige.port_rng.average())

    if sum(map(lambda j: j.n_ports, prev)) >= ports:
        yield prev
        return
    if len(prev) == 4:
        return
    
    for jet in jets:
        if not order.item.can_run_on_jet(jet.id): continue
        yield from get_multi_jets(order, jets, (*prev, jet))

def get_multi_lots(order: Order, inv: Inventory, jets: list[Jet]) \
    -> dict[Snapshot, dict[Jet, list[DyeLot]]]:
    multi_gen = get_multi_jets(order, jets, tuple())
    grg_due = order.due_date - dt.timedelta(days=1)
    min_arrival = MONDAY + dt.timedelta(weeks=1, days=2, hours=10)
    multi_lots: dict[Snapshot, dict[Jet, list[DyeLot]]] = {}

    for jet_tup in multi_gen:
        if len(jet_tup) == 1: continue

        snap = Snapshot()
        multi_lots[snap] = {}

        for jet in jet_tup:
            if jet not in multi_lots[snap]:
                multi_lots[snap][jet] = []

            retsnap, loads = get_jet_loads(inv, order.greige, jet,
                                           max_date=grg_due, snap=snap)
            if retsnap is not None and retsnap == snap:
                multi_lots[snap][jet].append(order.assign(loads))
                continue
            
            snap, loads = get_jet_loads(inv, order.greige, jet,
                                        max_date=min_arrival, create=True,
                                        snap=snap)
            multi_lots[snap][jet].append(order.assign(loads))
    
    for snap in multi_lots:
        for jet in multi_lots[snap]:
            lots = sorted(multi_lots[snap][jet], key=lambda l: l.min_date)
            multi_lots[snap][jet] = lots
    
    return multi_lots

def sched_over_max(jet: Jet, nweeks: int) -> float:
    jet_jobs = jet.jobs
    job_lbs: Callable[[Job], float] = lambda j: sum(map(lambda l: l.lbs, j.lots))
    total_lbs = sum(map(job_lbs, jet_jobs))

    start = jet.date_rng.minval
    if jet_jobs:
        start = jet_jobs[0].start
    ndays = nweeks*5
    max_lbs = 36000 * jet.n_ports / 39

    return max(0, total_lbs / ndays - max_lbs) * 0.01

@logging.logged_func(LOGGER, sc_cost_args, sc_cost_ret)
def sched_cost(jet: Jet) -> tuple[float, float, float]:
    shade_vals = {
        color.SOLUTION: 15, color.LIGHT: 0, color.MEDIUM: 5, color.BLACK: 20,
        color.LIGHT0: 2
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

def safety_cost(order: Order | OrderView) -> float:
    """
    The cost of a safety stock order. Safety has no due date, so there is
    no lateness: the only cost is the safety yards that have not been built
    yet. The remaining total on the order also counts any hard yards still
    ahead of it, so the unfilled safety is capped at the bucket's own size.
    """
    return max(0, min(order.init_yds, order.total_yds)) * SAFETY_YD_COST

@logging.logged_func(LOGGER, order_cost_args, order_cost_ret)
def order_cost(order: Order | OrderView, next_avail: dt.datetime,
               ignore_amt: float, cur_ports: int = -1) -> float:
    if order.safety:
        return safety_cost(order)

    table = order.late_table(next_avail, ignore_amt)
    if not table:
        return 0
    
    first_row = table[0]
    first_yds, first_delta = first_row
    cost = 0.0
    days_late_idxs = [2,3,4,8]
    start_cost_map = {2: 1000, 3:1500, 4:2500, 8:10000}
    scaling_map = {2:.01, 3: .015, 4: .025, 8: .5, 9: 1}
    found_idx = False
    index = 0
    for idx in days_late_idxs:
        if first_delta < dt.timedelta(days=idx) and not found_idx:
            cost += start_cost_map[idx]
            found_idx = True
            index = idx
    if not found_idx:
        exp = first_delta.days - 8
        cost += 10000 * (2 ** exp)
        index = 11
    
    for row in table:
        found_idx = False
        for idx in days_late_idxs:
            if row[1] < dt.timedelta(days=idx) and not found_idx:
                found_idx = True
                scalar = scaling_map[idx]
        if not found_idx:
            scalar = 1*row[1].days
        
        cost += row[0] * scalar

    if order.total_lbs > 0 and order.due_date >= next_avail:
        cost += 5000 + max(min(order.total_lbs, order.init_lbs), 500)

    rem_cycles = 0
    if cur_ports > 0:
        rem_cycles = math.ceil(round(order.total_lbs / 350) / cur_ports)
    return cost + 100 * (max(rem_cycles, 0)+1)

@logging.logged_func(LOGGER, late_cost_args, late_cost_ret)
def late_cost(order: Order, dmnd: Demand, next_avail: dt.datetime,
              cur_ports: int, ignore_rem: bool = False) \
                -> tuple[float, float, dict[str, float]]:
    """
    Returns the late cost of the order being scheduled, the late cost of
    every other order, and the late cost of each other hard (non-safety)
    order by order id. The last value is what a safety order is not
    allowed to make worse, order by order.
    """
    if ignore_rem:
        ignore_amt = min(order.init_yds, order.total_yds)
    else:
        ignore_amt = 0
    cur_late = order_cost(order, next_avail, ignore_amt, cur_ports=cur_ports)
    rem_late = 0.0
    hard_late: dict[str, float] = {}
    end_cur_wk = order.due_date + dt.timedelta(days=5-order.due_date.weekday())

    for date in dmnd:
        for other_order in dmnd[date].itervalues():
            if other_order.item == order.item and other_order.due_date > order.due_date: continue
            other_cost = order_cost(other_order, next_avail, 0)
            rem_late += other_cost
            if not other_order.safety:
                hard_late[other_order.id] = other_cost

    return cur_late, rem_late, hard_late

def hard_late_cost(dmnd: Demand, next_avail: dt.datetime) -> dict[str, float]:
    """The late cost of every hard order in the demand, by order id, under the current schedules."""
    costs: dict[str, float] = {}
    for date in dmnd:
        for other_order in dmnd[date].itervalues():
            if other_order.safety: continue
            costs[other_order.id] = order_cost(other_order, next_avail, 0)
    return costs

def worsened_hard_orders(base: dict[str, float], new: dict[str, float]) -> list[str]:
    """The ids of the hard orders whose late cost is higher in 'new' than in 'base'."""
    return [oid for oid, c in new.items() if c > base.get(oid, 0) + 1e-3]

def req_cost(req: Req, due_date: dt.datetime) -> float:
    if not req.orders:
        return 0

    sorted_ords = sorted(filter(lambda o: o.due_date <= due_date, req.orders),
                         key=lambda o: o.due_date)
    if not sorted_ords or sorted_ords[-1].total_yds > 0:
        return 0

    last = sorted_ords[-1]
    rem_yds = abs(last.total_yds)

    # yards produced past the hard requirements that land in the safety
    # bucket are wanted inventory, not excess
    safety = req.safety_order
    if safety is not None and not last.safety:
        into_safety = max(0, safety.init_yds - max(0, safety.total_yds))
        rem_yds = max(0, rem_yds - into_safety)
    if rem_yds <= 0:
        return 0

    # an item with safety stock but no hard requirements has no weekly use
    rem_weeks = 1
    if req.avg_use > 0:
        rem_weeks = round(rem_yds / req.avg_use)
    return rem_yds * 0.014 * rem_weeks

@logging.logged_func(LOGGER, inv_cost_args, inv_cost_ret)
def excess_inv_cost(order: Order, reqs: list[Req]) -> tuple[float, float]:
    cur_inv, rem_inv = 0, 0
    for req in reqs:
        if order.item == req.item:
            cur_inv += req_cost(req, order.due_date + dt.timedelta(weeks=2))
        else:
            rem_inv += req_cost(req, order.due_date + dt.timedelta(weeks=2))

    return cur_inv, rem_inv

@logging.logged_func(LOGGER, used_cost_args, used_cost_ret)
def used_inv_cost(inv: Inventory, extras: dict[GreigeStyle, list[PortLoad]], dmnd: Demand) -> float:
    needed_grg: dict[GreigeStyle, dict[dt.datetime, float]] = {}
    max_pnum = -1
    max_pdate = dt.datetime.fromtimestamp(0)
    for order in dmnd.itervalues():
        # safety stock has no claim on greige that a hard order may need
        if order.safety: continue
        if order.pnum > max_pnum:
            max_pnum = order.pnum
            max_pdate = order.due_date
        rem_lbs = min(order.init_lbs, order.total_lbs)
        if rem_lbs <= 0: continue
        if order.greige not in needed_grg:
            needed_grg[order.greige] = {}
        if order.due_date not in needed_grg[order.greige]:
            needed_grg[order.greige][order.due_date] = 0
        needed_grg[order.greige][order.due_date] += rem_lbs
    
    avail_grg: dict[GreigeStyle, float] = {}
    def is_new(p: PortLoad):
        r1_new = 'NEW' in p.roll1.roll_id
        r2_new = p.roll2 is not None and 'NEW' in p.roll2.roll_id
        return r1_new or r2_new
    
    for grg in inv:
        if grg not in avail_grg:
            avail_grg[grg] = 0
        for rview in inv[grg].itervalues():
            if 'NEW' in rview.id: continue
            avail_grg[grg] += rview.lbs
    for grg in extras:
        if grg not in avail_grg:
            avail_grg[grg] = 0
        avail_grg[grg] += sum(map(lambda p: p.lbs,
                                  filter(lambda p: not is_new(p), extras[grg])))

    used_cost = 0
    for grg in needed_grg:
        if grg not in avail_grg:
            avail_grg[grg] = 0

        dates = sorted(needed_grg[grg].keys())
        for date in dates:
            rem_needed = max(0, needed_grg[grg][date] - avail_grg[grg])
            avail_grg[grg] -= needed_grg[grg][date]
            days_late = (max_pdate - date).total_seconds() / (3600*24) + 1
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

class Cost(NamedTuple):
    non_jet: float
    jet: float
    hard_late: dict[str, float] # late cost of each hard order not being scheduled

    @property
    def total(self) -> float:
        return self.non_jet + self.jet

@logging.logged_func(LOGGER, cost_args, cost_ret)
def cost(jet: Jet, sched: JetSched, newjob: Job | None, order: Order, dmnd: Demand,
         reqs: list[Req], snap: Snapshot, inv: Inventory, next_avail: dt.datetime,
         ignore_rem: bool = False) -> Cost:
    apply_snapshot(inv, snap)
    prevsched = jet.set_sched(sched)

    cur_late, rem_late, hard_late = late_cost(order, dmnd, next_avail, jet.n_ports,
                                              ignore_rem=ignore_rem)
    cur_inv, rem_inv = excess_inv_cost(order, reqs)
    used_inv = used_inv_cost(inv, prevsched.free_greige(), dmnd)
    strips, not_seq, nb9 = sched_cost(jet)
    ndays = (order.due_date - jet.date_rng.minval).total_seconds() / (3600*24)
    nweeks = max(1, ndays/7 - 2.5)
    over_max = sched_over_max(jet, nweeks)
    not_pref = 0

    all_jobs = list(filter(lambda j: j.shade not in (color.STRIP, color.HEAVYSTRIP),
                           jet.jobs))
    apply_snapshot(inv, None)
    jet.set_sched(prevsched)

    if order.item.can_run_on_jet('Jet-07') and jet.id in ('Jet-09', 'Jet-10'):
        not_pref = order.total_yds * 10
    elif order.item.can_run_on_jet('Jet-08'):
        if jet.id != 'Jet-08' and jet.id in ('Jet-09', 'Jet-10'):
            not_pref = order.total_yds * 10

    non_jet_cost = sum((cur_late, rem_late, cur_inv, rem_inv, used_inv))
    jet_cost = (strips+not_seq+nb9+over_max) / (max(1,len(all_jobs))*jet.n_ports) + not_pref
    # if order.item.id == 'FF LYRICHELHS-41114-63':
    #     print(jet, sched, snap, cur_late, rem_late, cur_inv, rem_inv, used_inv, jet_cost)
    return Cost(non_jet_cost, jet_cost, hard_late)

def cost_all(scheds: dict[Jet, JetSched], order: Order, dmnd: Demand, reqs: list[Req],
             snap: Snapshot, inv: Inventory, next_avail: dt.datetime) -> float:
    apply_snapshot(inv, snap)
    prevscheds: dict[Jet, JetSched] = {}
    for jet in scheds:
        prevscheds[jet] = jet.set_sched(scheds[jet])
    
    cur_late, rem_late, _ = late_cost(order, dmnd, next_avail, -1)
    cur_inv, rem_inv = excess_inv_cost(order, reqs)

    free_grg: dict[GreigeStyle, list[PortLoad]] = {}
    for sched in prevscheds.values():
        cur_free = sched.free_greige()
        for grg in cur_free:
            if grg not in free_grg:
                free_grg[grg] = []
            free_grg[grg] += cur_free[grg]

    used_inv = used_inv_cost(inv, free_grg, dmnd)

    total_jet_cost = 0
    for jet in scheds:
        strips, not_seq, nb9 = sched_cost(jet)
        ndays = (order.due_date - jet.date_rng.minval).total_seconds() / (3600*24)
        nweeks = max(1, ndays/7 - 2.5)
        over_max = sched_over_max(jet, nweeks)
        not_pref = 0

        if order.item.can_run_on_jet('Jet-07') and jet.id != 'Jet-07':
            not_pref += order.total_yds * 10
        elif order.item.can_run_on_jet('Jet-08') and jet.id != 'Jet-08':
            not_pref += order.total_yds * 10

        all_jobs = list(filter(lambda j: j.shade not in (color.STRIP, color.HEAVYSTRIP),
                               jet.jobs))

        total_jet_cost += (strips+not_seq+nb9+over_max) / (len(all_jobs)*jet.n_ports) + not_pref

    apply_snapshot(inv, None)
    for jet in prevscheds:
        jet.set_sched(prevscheds[jet])
    
    return sum((cur_late, rem_late, cur_inv, rem_inv, used_inv)) + total_jet_cost / len(scheds)

def key_sched(s_and_c: tuple[dict[Jet, JetSched], Snapshot | None, float]):
    return s_and_c[-1]

def best_sub_job(snap: Snapshot, jet: Jet, lots: list[DyeLot],
                 order: Order, dmnd: Demand, reqs: list[Req], inv: Inventory,
                 next_avail: dt.datetime) -> tuple[JetSched, float] | None:
    costs: list[tuple[JetSched, float, float]] = []
    cur_fri = order.due_date + dt.timedelta(days=4 - order.due_date.weekday())
    next_fri = max(next_avail, cur_fri + dt.timedelta(weeks=2))

    index = jet.get_start_idx((lots[0],), order.due_date)
    cur_jet_jobs = jet.cur_sched.jobs
    for i in range(index, len(cur_jet_jobs)+1):
        newsched, newjobs = jet.insert(lots, i, order.due_date)
        if newsched is not None:
            newcost = cost(jet, newsched, newjobs[0], order, dmnd, reqs, snap, inv,
                           next_fri).total
            costs.append((newsched, newcost))
    
    if not costs:
        return None
    costs = sorted(costs, key=lambda x: x[1])
    return costs[0]

def best_multi_scheds(multi_lots: dict[Snapshot, dict[Jet, list[DyeLot]]],
                      order: Order, dmnd: Demand, reqs: list[Req], inv: Inventory,
                      next_avail: dt.datetime):
    best_scheds: dict[Snapshot, dict[Jet, JetSched]] = {}

    for snap in multi_lots:
        print(snap)
        best_scheds[snap] = {}
        for jet in multi_lots[snap]:
            if not multi_lots[snap][jet]: continue
            print(jet)
            res = best_sub_job(snap, jet, multi_lots[snap][jet],
                               order, dmnd, reqs, inv, next_avail)
            if res is None:
                del best_scheds[snap]
                break

            sched, _ = res
            best_scheds[snap][jet] = sched
    
    return best_scheds

@logging.logged_func(LOGGER, best_job_args, best_job_ret)
def get_best_job(lots_map: dict[Jet, list[tuple[DyeLot, tuple[DyeLot, ...], Snapshot]]],
                 order: Order, dmnd: Demand, reqs: list[Req], inv: Inventory, jets: list[Jet],
                 next_avail: dt.datetime, check_multi: bool = True) \
                    -> tuple[dict[Jet, JetSched], Snapshot | None, float] | None:
    sched_and_costs: list[tuple[dict[Jet, JetSched], Snapshot | None, float]] = []
    cur_fri = order.due_date + dt.timedelta(days=4 - order.due_date.weekday())
    next_fri = max(next_avail, cur_fri + dt.timedelta(weeks=2))

    # Safety stock is placed wherever it fits, but it may never push a hard
    # order later than it already is: any candidate schedule that raises the
    # late cost of any single hard order is thrown out before costs are
    # compared. (Per order, not in total: a reshuffle that helps one hard
    # order must not pay for delaying another.)
    base_hard_late: dict[str, float] = {}
    if order.safety:
        base_hard_late = hard_late_cost(dmnd, next_fri)

    for jet in lots_map:
        for tup in lots_map[jet]:
            lots = tup[:-1]
            snapshot = tup[-1]
            if order.safety:
                # try every slot, and do not hold the job back to the week
                # before its (nominal) due date
                index = 0
                insert_due = None
            else:
                index = jet.get_start_idx(lots, order.due_date)
                insert_due = order.due_date
            cur_jet_jobs = jet.cur_sched.jobs
            for i in range(index, len(cur_jet_jobs)+1):
                # print(f'      inserting at {i} on jet {jet.id}')
                newsched, newjobs = jet.insert(lots, i, insert_due)
                # if order.item.id == 'FF LYRICHELHS-41114-63':
                #     print(jet, i, end=' ')
                #     if cur_jet_jobs and i > 0 and i < len(cur_jet_jobs):
                #         print(cur_jet_jobs[i-1].color.shade, cur_jet_jobs[i].lots[0].moveable)
                #     else:
                #         print()
                #     print(newsched)
                #     print()
                if newsched is not None:
                    newcost = cost(jet, newsched, newjobs[0], order, dmnd, reqs, snapshot, inv,
                                   next_fri, ignore_rem=True)
                    if order.safety and worsened_hard_orders(base_hard_late, newcost.hard_late):
                        continue
                    sched_and_costs.append(({jet: newsched}, snapshot, newcost.total))
        cur_cost = cost(jet, jet.cur_sched, None, order, dmnd, reqs, None, inv, next_fri).total
        sched_and_costs.append(({ jet: jet.cur_sched }, None, cur_cost))
    
    if check_multi:
        multi_lots = get_multi_lots(order, inv, jets)
        best_scheds = best_multi_scheds(multi_lots, order, dmnd, reqs, inv, next_avail)
        for snap, scheds in best_scheds.items():
            schedcost = cost_all(scheds, order, dmnd, reqs, snap, inv, next_avail)
            sched_and_costs.append((scheds, snap, schedcost))

    sorted_s_and_c = sorted(sched_and_costs, key=key_sched)
    # if order.item.id == 'FF LYRICHELHS-41114-63':
    #     print(sorted_s_and_c)
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
                   jets: list[Jet], next_avail: dt.datetime,
                   check_multi: bool = True) -> tuple[Order, bool]:
    lots_map = get_all_lots(order, dmnd, inv, jets)
    if 'SPACEWALK' in order.item.id:
        print(', '.join(map(lambda j: j.id, lots_map.keys())))
    ret = get_best_job(lots_map, order, dmnd, reqs, inv, jets, next_avail,
                       check_multi=check_multi)
    if ret is None:
        return order, False
    
    best_scheds, best_snap, _ = ret

    apply_snapshot(inv, best_snap, temp=False)
    if best_snap is None:
        return order, False
    
    prev_scheds: dict[Jet, JetSched] = {}
    for jet in best_scheds:
        prev_scheds[jet] = jet.set_sched(best_scheds[jet])
        add_back_free_loads(prev_scheds[jet], inv)

    return order, True

def schedule_dates(dmnd: Demand, reqs: list[Req], inv: Inventory, jets: list[Jet],
                   next_avail: dt.datetime, dates: list[dt.datetime]) -> None:
    for date in dates:
        all_views = list(dmnd[date].itervalues())
        if all(map(lambda o: o.safety, all_views)):
            print(f'Making schedule for safety stock (bucket {date.strftime('%m/%d')})')
        else:
            print(f'Making schedule for orders for {date.strftime('%m/%d')}')

        ultra_lt = list(filter(lambda o: o.color.shade == color.LIGHT0, all_views))
        rem = list(filter(lambda o: o.color.shade != color.LIGHT0, all_views))
        views = sorted(rem, key=lambda o: o.init_yds, reverse=True)
        views += sorted(ultra_lt, key=lambda o: o.init_yds, reverse=True)

        for oview in views:
            print(f'  Making schedule for {oview}')
            order = dmnd.remove(oview)
            checked = True
            min_yds = 150 if order.init_yds > 150 else 80
            prev_yds = math.inf

            while order.total_yds > min_yds:
                if order.total_yds + 100 > prev_yds:
                    break

                prev_yds = order.total_yds
                print(f'    remaining yards: {order.total_yds:.2f}')
                order, cont = schedule_order(order, dmnd, reqs, inv, jets,
                                             next_avail, check_multi=not checked)
                checked = True
                if not cont:
                    print(f'    remaining yards: {order.total_yds:.2f}')
                    break

            dmnd.add(order)

@logging.logged_func(LOGGER, desc_args=make_sched_args, desc_ret=make_sched_ret)
def make_schedule(dmnd: Demand, reqs: list[Req], inv: Inventory, jets: list[Jet],
                  next_avail: dt.datetime) -> None:
    # Safety stock is held out of the demand until every hard requirement has
    # been scheduled, so the hard schedule comes out exactly as it would with
    # no safety stock at all. Only then are the safety orders added and placed
    # wherever they fit without pushing a hard order later (see get_best_job).
    safety_orders: list[Order] = [dmnd.remove(v) for v in list(dmnd.itervalues())
                                  if v.safety]

    schedule_dates(dmnd, reqs, inv, jets, next_avail, sorted(dmnd))
    if not safety_orders:
        return

    hard_dates = set(dmnd)
    for order in safety_orders:
        dmnd.add(order)
    safety_dates = sorted(filter(lambda d: d not in hard_dates, dmnd))

    hard_late_before = hard_late_cost(dmnd, next_avail)
    schedule_dates(dmnd, reqs, inv, jets, next_avail, safety_dates)
    hard_late_after = hard_late_cost(dmnd, next_avail)
    worse = worsened_hard_orders(hard_late_before, hard_late_after)
    print(f'Hard-order late cost before safety stock: {sum(hard_late_before.values()):.2f}, '
          f'after: {sum(hard_late_after.values()):.2f}; '
          f'hard orders made later by safety stock: {len(worse)}')
    for oid in worse:
        print(f'  {oid}: {hard_late_before.get(oid, 0):.2f} -> {hard_late_after[oid]:.2f}')

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
                 reqs: list[Req], lgr: logging.Logger) -> None:
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
    
    lp_ids, lp_data = get_lot_pnums(reqs)
    lp_df = pd.DataFrame(data=lp_data, index=lp_ids)
    lp_df = df_cols_to_string(lp_df, 'order')
    
    new_ids, new_inv = get_new_inv(inv)
    new_inv_df = pd.DataFrame(data=new_inv, index=new_ids)
    
    inv_df = pd.concat([inv_df, new_inv_df])
    inv_df['date_needed'] = inv_df['arrive_date']
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
            else:
                lbs_used += sum(used2['lbs2'])
                min_date = min(min_date, min(used2['start']))

        if lbs_used is not None:
            inv_df.loc[i, 'used'] = lbs_used
            inv_df.loc[i, 'date_needed'] = min_date
    
    late, late_detail, missing = get_late_tables(dmnd)

    safety_ids, safety_data = get_safety_table(reqs)
    safety_df = pd.DataFrame(data=safety_data, index=safety_ids)
    safety_df = df_cols_to_string(safety_df, 'item', 'greige')

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
    lp_df.to_excel(writer, sheet_name='lot_priorities', index_label='lot_id')
    late_df.to_excel(writer, sheet_name='late_orders', float_format='%.2f', index_label='order_id')
    late_df2.to_excel(writer, sheet_name='late_details', float_format='%.2f',
                      index_label='bucket_id')
    missing_df.to_excel(writer, sheet_name='not_scheduled', float_format='%.2f', index_label='order_id')
    safety_df.to_excel(writer, sheet_name='safety_stock', float_format='%.2f',
                       index_label='order_id')

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
    # safety replenishment comes in with the demand (the tab's Safety column)
    reqs, dmnd = load_demand(start, use_lam_sched=True)
    jets = load_jets(start, end)
    print('\rFinished loading data!')

    inv_df, dmnd_df = get_input_tables(inv, dmnd)
    friday_raw = start + dt.timedelta(days=4 - start.weekday())
    friday = dt.datetime(friday_raw.year, friday_raw.month, friday_raw.day)
    make_schedule(dmnd, reqs, inv, jets, friday + dt.timedelta(weeks=4))
    write_output(writer, os.path.join(os.path.dirname(__file__), 'datasrc'),
                 inv_df, dmnd_df, inv, dmnd, jets, reqs, LOGGER)

    writer.close()

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])