#!/usr/bin/env python

from typing import NamedTuple, Generator

from app import style
from app.support import FloatRange
from app.style import GreigeStyle
from app.materials import Inventory, RollAlloc, PortLoad, Snapshot

from loaddata import load_inv, load_demand, load_jets

style.greige.init()

LOGGER = []

class Jet(NamedTuple):
    n_ports: int
    load_rng: FloatRange

def add_back_piece(inv: Inventory, piece: RollAlloc, snapshot: Snapshot) -> None:
    roll = inv.remove(inv.get(piece.roll_id))
    roll.deallocate(piece, snapshot=snapshot)
    inv.add(roll)

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

def get_dyelots(req, inv, jets) -> list[int | tuple[int, int]]:
    """
    Loop through jets:
        If approximate lbs < needed lbs: skip
        
        Load all ports
        If one req:
            Create dyelot and assign
        else:
            Divide ports
            Create two dyelots, assign to corresponding thing
    """
    return [0]

def get_best_job(combs, req, bucket, dmnd, inv, jets) -> int | None:
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

def get_req_pairs(req, pnum, matches) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    for match in matches:
        if req + match <= 8:
            pairs.append((req, match))
    return pairs

def make_schedule(dmnd, inv, jets) -> None:
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
    for pnum in range(1,5):
        for req in dmnd: # dmnd.fullvals()
            bucket = req[pnum]
            while bucket > 10:
                matches = [] # dmnd.get_matches(req)
                pairs = get_req_pairs(bucket, matches)
                job = get_best_job(pairs, bucket, pnum, dmnd, inv, jets)
                if not job:
                    break
                # job.schedule()
                bucket -= 1

def write_output(dmnd, jets, lgr) -> None:
    pass

def main():
    inv = load_inv()
    # dmnd = load_demand()
    # jets = load_jets()

    # make_schedule(dmnd, inv, jets)
    # write_output(dmnd, jets, LOGGER)

    jet1 = Jet(8, FloatRange(300, 400))
    grg = style.greige.get_style('AU5429D')
    print(inv[grg])

    snap1, loads1 = get_jet_loads(inv, grg, jet1)
    for load in loads1:
        print(load)
    
    for rview in inv.itervalues():
        roll = inv.remove(rview)
        roll.apply_snap(snapshot=snap1)
        inv.add(roll)
    
    print(inv[grg])
    
    snap2, loads2 = get_jet_loads(inv, grg, jet1)
    for load in loads2:
        print(load)

    for rview in inv.itervalues():
        roll = inv.remove(rview)
        roll.apply_snap(snapshot=snap2)
        inv.add(roll)

    print(inv[grg])

if __name__ == '__main__':
    main()