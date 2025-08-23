#!/usr/bin/env python

from typing import Literal

from app.support.logging import ProcessDesc
from app.inventory import Inventory, RollView
from app.schedule import Demand, Jet, Req, DyeLot

from schedtypes import NewJobInfo, PortLoad

def make_sched_args(demand: Demand, inv: Inventory, jets: list[Jet]) -> ProcessDesc:
    return { 'desc1': 'Running schedule algorithm' }

def make_sched_ret(ret: None) -> ProcessDesc:
    return { 'desc1': 'Finished scheduling algorithm' }

def best_job_args(req: Req, pnum: int, jets: list[Jet], inv: Inventory, dmnd: Demand) \
    -> ProcessDesc:
    return {
        'desc1': f'Finding best job for P{pnum} of {req.id}',
        'desc2': f'{req.bucket(pnum).yds:.2f} yds needed to make truck',
        'desc3': f'{req.bucket(pnum).total_yds:.2f} yds needed to meet requirement'
    }

def best_job_ret(ret: NewJobInfo | None) -> ProcessDesc:
    if ret is None:
        return {
            'desc1': 'Will not schedule current demand'
        }
    return {
        'desc1': f'Best option is on {ret.jet.id} after {ret.idx} job(s)'
    }

type DyeLotRet = tuple[list[PortLoad], set[RollView], DyeLot | None,
                       Literal['N/A', 'CANNOT RUN', 'NO GREIGE']]

def dyelot_args(req: Req, pnum: int, jet: Jet, inv: Inventory) -> ProcessDesc:
    return {
        'desc1': f'Trying to create dyelot for {req.item.id} on {jet.id}',
        'desc2': f'Greige style: {req.item.greige.id}'
    }

def dyelot_ret(ret: DyeLotRet) -> ProcessDesc:
    pls, rvs, lot, reason = ret
    desc: ProcessDesc = {}
    if lot is None:
        desc['desc1'] = 'Failed to create dyelot'
        if reason == 'CANNOT RUN':
            desc['desc2'] = 'Jet cannot run item'
        elif reason == 'NO GREIGE':
            desc['desc2'] = 'Not enough greige to load jet'
            desc['desc3'] = f'Could only fill {len(pls)} port(s)'
    else:
        desc['desc1'] = 'Able to create dyelot'
        desc['desc2'] = f'Will use {lot.lbs:.2f} pounds of {lot.greige.id}'
        desc['desc3'] = f'Will yield {lot.yds:.2f} yards of {lot.item.id}'
    
    return desc