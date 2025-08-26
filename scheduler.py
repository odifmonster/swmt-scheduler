#!/usr/bin/env python

from typing import NamedTuple, Generator
import sys, math, datetime as dt

from app import style
from app.style import GreigeStyle
from app.materials import Inventory, RollAlloc, PortLoad, Snapshot
from app.schedule import DyeLot, Order, OrderView, Req, Demand, Jet, JetSched

from helpers import add_back_piece, apply_snapshot
from loaddata import load_inv, load_demand, load_jets

style.greige.init()
style.fabric.init()

LOGGER = []

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

def get_jet_loads(inv: Inventory, greige: GreigeStyle, jet: Jet) \
    -> tuple[Snapshot | None, list[PortLoad]]:
    snap = Snapshot()
    max_ret: list[PortLoad] = []
    
    for rview in inv.itervalues():
        roll = inv.remove(rview)
        roll.snapshot = snap
        inv.add(roll)

    for start in inv.get_starts(greige):
        ret = try_load_jet(inv, inv.get_port_loads(greige, snap, jet.load_rng, start=start),
                           jet, snap)
        if len(ret) == jet.n_ports:
            return snap, ret
        if len(ret) > len(max_ret):
            max_ret = ret
    
    ret = try_load_jet(inv, inv.get_port_loads(greige, snap, jet.load_rng), jet, snap)
    if len(ret) == jet.n_ports:
        return snap, ret

    return None, ret

def get_paired_lots(o1: Order, o2: Order, inv: Inventory, jets: list[Jet]) \
    -> list[tuple[DyeLot, DyeLot]]:
    lots: list[tuple[DyeLot, DyeLot]] = []
    avg_load = o1.greige.port_rng.average()
    min_o1_ports = math.ceil(o1.lbs / avg_load)
    min_total_ports = math.ceil((o1.lbs+o2.lbs) / avg_load)

    for jet in jets:
        if not o1.item.can_run_on_jet(jet.id): continue
        if min_total_ports > jet.n_ports: continue
        snap, loads = get_jet_loads(inv, o1.greige, jet)
        if snap is None: continue

        ports1 = round((min_o1_ports / min_total_ports) * jet.n_ports)
        lot1 = o1.assign(loads[:ports1])
        lot2 = o2.assign(loads[ports1:])
        lots.append((lot1, lot2))
    
    return lots

def get_single_lots(order: Order, inv: Inventory, jets: list[Jet]) -> list[tuple[DyeLot]]:
    lots: list[tuple[DyeLot]] = []
    
    for jet in jets:
        if not order.item.can_run_on_jet(jet.id): continue
        snap, loads = get_jet_loads(inv, order.greige, jet)
        if snap is None: continue

        lots.append((order.assign(loads),))
    
    return lots

def get_order_pairs(order: Order, dmnd: Demand) -> list[tuple[Order, Order]]:
    to_remove: list[OrderView] = []
    for match in dmnd.get_matches(order):
        if match.lbs <= 0: continue
        if (order.lbs + match.lbs) / order.greige.port_rng.average() <= 8:
            to_remove.append((order, match))

    ret: list[tuple[Order, Order]] = []
    for oview in to_remove:
        o2 = dmnd.remove(oview)
        ret.append((order, o2))
    return ret

def get_all_lots(order: Order, dmnd: Demand, inv: Inventory,
                 jets: list[Jet]) -> list[tuple[DyeLot, ...]]:
    lots: list[tuple[DyeLot, ...]] = []

    lots += get_single_lots(order, inv, jets)

    pairs = get_order_pairs(order, dmnd)
    for o1, o2 in pairs:
        lots += get_paired_lots(o1, o2, inv, jets)
        dmnd.add(o2)

    return lots

def sched_cost(jet: Jet, sched: JetSched) -> float:
    """The cost of not sequencing and of running on non-preferred jets."""
    return 0

def order_cost(order: Order | OrderView) -> float:
    """The cost of late penalties on this order."""
    return 0

def late_cost(order: Order, dmnd: Demand) -> tuple[float, float]:
    """The cost of all late penalties given the current demand."""
    return 0, 0

def req_cost(req: Req) -> float:
    """The cost of any excess inventory produced on this item requirement."""
    return 0

def excess_inv_cost(order: Order, reqs: list[Req]) -> tuple[float, float]:
    """The carrying cost of any excess inventory."""
    return 0, 0

def used_inv_cost(inv: Inventory, extras: dict[GreigeStyle, list[PortLoad]], reqs: list[Req]) -> float:
    """The cost of using up the given greige."""
    return 0

def cost(jet: Jet, sched: JetSched, order: Order, dmnd: Demand, reqs: list[Req],
         snap: Snapshot, inv: Inventory) -> float:
    apply_snapshot(inv, snap)
    prevsched = jet.set_sched(sched)

    cur_late, rem_late = late_cost(order, dmnd)
    cur_inv, rem_inv = excess_inv_cost(order, reqs)
    used_inv = used_inv_cost(inv, prevsched.free_greige(), reqs)
    scost = sched_cost(jet, sched)

    return sum((cur_late, rem_late, cur_inv, rem_inv, used_inv)) + scost / jet.n_ports

def get_best_job(lots: list[tuple[DyeLot, ...]], order: Order, dmnd: Demand,
                 inv: Inventory, jets: list[Jet]) -> int | None:
    """
    Loop through pairs
        Get all dyelots that cover the pair
    
    Get all dyelots that cover the req

    Loop through all dyelots
        Append all jobs and costs
    
    Sort jobs by cost
    Pick the best one and return it
    """
    return 0

def make_schedule(dmnd: Demand, inv: Inventory, jets) -> None:
    """
    greige, color, priority, id
    Loop through priorities
        Loop through reqs
            While demand is remaining and can schedule
                grab all matching items
                make pairs that cover everything and fit on one jet
                get the best job from pairs and requirement

                if there is a best job:
                    schedule it
                else:
                    next req
    """
    dates = sorted(dmnd)
    for date in dates:
        for oview in dmnd[date].itervalues():
            order = dmnd.remove(oview)
            # while order.total_yds > 50:
            #     pairs = get_order_pairs(order, dmnd)
            #     lots = get_all_lots(order, dmnd, inv, jets)

def write_output(dmnd, jets, lgr) -> None:
    pass

def main(start_str: str, p1date_str: str):
    start = dt.datetime.fromisoformat(start_str)
    p1date_raw = dt.datetime.fromisoformat(p1date_str)
    p1date = dt.datetime(p1date_raw.year, p1date_raw.month, p1date_raw.day, hour=8)

    inv = load_inv()
    reqs, dmnd = load_demand(p1date)
    jets = load_jets()

    make_schedule(dmnd, inv, jets)
    write_output(dmnd, jets, LOGGER)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])