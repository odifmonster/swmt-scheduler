#!/usr/bin/env python

import datetime as dt

from app.support.logging import *
from app.style import GreigeStyle
from app.materials import Inventory, Snapshot, PortLoad
from app.schedule import Order, OrderView, Req, Demand, DyeLot, JetSched, Jet

__all__ = ['make_sched_args', 'make_sched_ret', 'all_lots_args', 'all_lots_ret',
           'sched_ord_args', 'sched_ord_ret', 'single_lots_args', 'single_lots_ret',
           'gsl_loop_args', 'gsl_loop_ret', 'paired_lots_args', 'paired_lots_ret',
           'gpl_loop_args', 'gpl_loop_ret', 'jload_args', 'jload_ret',
           'best_job_args', 'best_job_ret', 'cost_args', 'cost_ret', 'sc_cost_args',
           'sc_cost_ret', 'late_cost_args', 'late_cost_ret', 'inv_cost_args',
           'inv_cost_ret', 'used_cost_args', 'used_cost_ret', 'order_cost_args',
           'order_cost_ret']

def make_sched_args(dmnd: Demand, reqs: list[Req], inv: Inventory, jets: list[Jet],
                    next_avail: dt.datetime) \
    -> ProcessDesc:
    return {
        'desc1': 'Generating the current schedule'
    }

def make_sched_ret(res: None) -> ProcessDesc:
    return {
        'desc1': 'Finished generating the current schedule'
    }

def sched_ord_args(order: Order, dmnd: Demand, reqs: list[Req], inv: Inventory,
                   jets: list[Jet], next_avail: dt.datetime) -> ProcessDesc:
    return {
        'desc1': f'Attempting to fulfill {order}',
        'desc2': f'due date={order.due_date.strftime('%m/%d')}',
        'desc3': f'yards missing truck={order.yds:.2f}, yards not scheduled={min(order.init_yds,order.total_yds):.2f}'
    }

def sched_ord_ret(res: tuple[Order, bool]) -> ProcessDesc:
    order, _ = res
    return {
        'desc1': f'remaining unscheduled yards={min(order.init_yds,order.total_yds):.2f}'
    }

def all_lots_args(order: Order, dmnd: Demand, inv: Inventory, jets: list[Jet]) -> ProcessDesc:
    return {
        'desc1': f'Getting all possible dyelots to assign to {order}',
        'desc2': f'greige={order.greige}, color={order.color}'
    }

def all_lots_ret(res: dict[Jet, list[tuple[DyeLot, *tuple[DyeLot, ...], Snapshot]]]) -> ProcessDesc:
    return {}

def single_lots_args(order: Order, inv: Inventory, jets: list[Jet]) -> ProcessDesc:
    return {
        'desc1': f'Getting all possible single dyelots to assign to {order}'
    }

def single_lots_ret(res: dict[Jet, tuple[DyeLot, Snapshot]]) -> ProcessDesc:
    return {}

def gsl_loop_args(order: Order, inv: Inventory, jet: Jet) -> ProcessDesc:
    return {
        'desc1': f'Creating dyelot for {jet.id} to assign to {order}'
    }

def gsl_loop_ret(res: tuple[DyeLot, Snapshot] | str) -> ProcessDesc:
    fmtd: ProcessDesc = {}
    if type(res) is str:
        fmtd['desc1'] = 'Failed to create dyelot'
        fmtd['desc2'] = res
    else:
        lot, snap = res
        fmtd['desc1'] = f'lot={lot.id}, inventory snapshot={snap}'
    return fmtd

def paired_lots_args(o1: Order, o2: Order, inv: Inventory, jets: list[Jet]) -> ProcessDesc:
    return {
        'desc1': f'Getting all possible dyelots to assign to {o1} and {o2}'
    }

def paired_lots_ret(res: dict[Jet, tuple[DyeLot, DyeLot, Snapshot]]) -> ProcessDesc:
    return {}

def gpl_loop_args(o1: Order, o2: Order, inv: Inventory, jet: Jet) -> ProcessDesc:
    return {
        'desc1': f'Creating dyelot for {jet.id} to assign to {o1} and {o2}'
    }

def gpl_loop_ret(res: tuple[DyeLot, DyeLot, Snapshot] | str) -> ProcessDesc:
    if type(res) is str:
        return {
            'desc1': 'Failed to create dyelot', 'desc2': res
        }
    lot1, lot2, snap = res
    return {
        'desc1': f'lot1={lot1.id}, lot2={lot2.id}, inventory snapshot={snap}'
    }

def jload_args(inv: Inventory, greige: GreigeStyle, jet: Jet,
               max_date: dt.datetime | None = None, create: bool = False) -> ProcessDesc:
    return {
        'desc1': f'Searching inventory for {greige} to load {jet.id}'
    }

def jload_ret(res: tuple[Snapshot | None, list[PortLoad]]) -> ProcessDesc:
    snap, loads = res
    if snap is None:
        return {
            'desc1': 'Could not fill jet', 'desc2': f'Could only fill {len(loads)} port(s)'
        }
    return {
        'desc1': 'Able to fill jet'
    }

def best_job_args(lots_map: dict[Jet, list[tuple[DyeLot, tuple[DyeLot, ...], Snapshot]]],
                  order: Order, dmnd: Demand, reqs: list[Req], inv: Inventory,
                  next_avail: dt.datetime) -> ProcessDesc:
    return {
        'desc1': f'Finding best job for {order}'
    }

def best_job_ret(res: tuple[Jet, Snapshot | None, JetSched, float] | None) -> ProcessDesc:
    if res is None:
        return { 'desc1': 'Could not find any jobs' }
    jet, snap, sched, cost = res
    if snap is None:
        return {
            'desc1': 'Chose not to schedule any jobs',
            'desc2': f'cost={cost:.2f}'
        }
    return {
        'desc1': f'Best option is {sched} on {jet.id}',
        'desc2': f'cost={cost:.2f}'
    }

def cost_args(jet: Jet, sched: JetSched, order: Order, dmnd: Demand, reqs: list[Req],
              snap: Snapshot, inv: Inventory, next_avail: dt.datetime) -> ProcessDesc:
    if sched == jet.cur_sched:
        return {
            'desc1': f'Getting the total cost for the current schedule of {jet.id}',
            'desc2': f'sched={jet.cur_sched}'
        }
    return {
        'desc1': f'Getting the total cost of {sched} for {jet.id}',
        'desc2': f'inventory snapshot={snap}'
    }

def cost_ret(res: float) -> ProcessDesc:
    return {
        'desc1': f'cost={res:.2f}'
    }

def sc_cost_args(jet: Jet) -> ProcessDesc:
    return {
        'desc1': f'Getting the schedule-related costs of {jet.cur_sched}'
    }

def sc_cost_ret(res: tuple[float, float, float]) -> ProcessDesc:
    strips, not_seq, non_black_9 = res
    return {
        'desc1': f'strip costs={strips:.2f}', 'desc2': f'not sequenced costs={not_seq:.2f}',
        'desc3': f'non-preferred items costs={non_black_9}'
    }

def order_cost_args(order: Order | OrderView, next_avail: dt.datetime) -> ProcessDesc:
    return {
        'desc1': f'Calculating late and not-scheduled costs for {order}'
    }

def order_cost_ret(res: float) -> ProcessDesc:
    return {
        'desc1': f'late cost={res:.2f}'
    }

def late_cost_args(order: Order, dmnd: Demand, next_avail: dt.datetime) -> ProcessDesc:
    return {
        'desc1': 'Getting the cost of late and not-scheduled orders'
    }

def late_cost_ret(res: tuple[float, float]) -> ProcessDesc:
    return {
        'desc1': f'late costs on current order={res[0]:.2f}',
        'desc2': f'late costs on other orders={res[1]:.2f}'
    }

def inv_cost_args(order: Order, reqs: list[Req]) -> ProcessDesc:
    return {
        'desc1': 'Getting the cost of any excess inventory'
    }

def inv_cost_ret(res: tuple[float, float]) -> ProcessDesc:
    return {
        'desc1': f'excess inv costs on current order={res[0]:.2f}',
        'desc2': f'excess inv costs on other orders={res[1]:.2f}'
    }

def used_cost_args(inv: Inventory, extras: dict[GreigeStyle, list[PortLoad]],
                   dmnd: Demand) -> ProcessDesc:
    return {
        'desc1': 'Getting the cost of using up greige inventory'
    }

def used_cost_ret(res: float) -> ProcessDesc:
    return {
        'desc1': f'used up inv costs={res:.2f}'
    }