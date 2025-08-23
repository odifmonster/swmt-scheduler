#!/usr/bin/env python

from typing import Literal

from app.support.logging import ProcessDesc
from app.support import FloatRange
from app.style import GreigeStyle
from app.inventory import Inventory, RollView
from app.schedule import Demand, Jet, Req, DyeLot, JetSched

from schedtypes import NewJobInfo, PortLoad, RollPiece

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
        desc['desc1'] = f'Able to create test dyelot {lot}'
        desc['desc2'] = f'Will use {lot.lbs:.2f} pounds of {lot.greige.id}'
        desc['desc3'] = f'Will yield {lot.yds:.2f} yards of {lot.item.id}'
    
    return desc

def jet_loads_args(greige: GreigeStyle, inv: Inventory, jet: Jet) -> ProcessDesc:
    return {
        'desc1': f'Searching for {greige.id} to load {jet.id}'
    }

def jet_loads_ret(ret: list[PortLoad]) -> ProcessDesc:
    return {
        'desc1': f'Found enough greige for {len(ret)} port(s)'
    }

def grg_starts_args(greige: GreigeStyle, inv: Inventory, jet: Jet) -> ProcessDesc:
    return {
        'desc1': f'Searching for valid rolls of {greige.id} to put in first port of {jet.id}'
    }

def grg_starts_yld(ret: list[PortLoad]) -> ProcessDesc:
    return {
        'desc1': f'Starting with roll {ret[0].roll1.id}',
        'desc2': f'Weight: {ret[0].roll1.lbs:.2f} lbs',
        'desc3': f'Can fill {len(ret)} port(s)'
    }

def port_loads_args(greige: GreigeStyle, inv: Inventory, jet_rng: FloatRange,
                    used: PortLoad | None = None) -> ProcessDesc:
    desc: ProcessDesc =  {
        'desc1': f'Searching for {greige.id} to load ports'
    }
    if used:
        desc['desc2'] = f'Using {used.roll1.lbs:.2f} lbs of {used.roll1.id} in first port'
    return desc

def port_loads_yld(ret: PortLoad) -> ProcessDesc:
    desc: ProcessDesc = {
        'desc1': 'Created port load', 'desc2': f'Used {ret.roll1.lbs:.2f} lbs of {ret.roll1.id}'
    }
    if ret.roll2:
        desc['desc3'] = f'Used {ret.roll2.lbs: .2f} of {ret.roll2.id}'
    return desc

def normal_rolls_args(greige: GreigeStyle, inv: Inventory, prev_wts: list[float],
                      jet_rng: FloatRange, used: str | None = None) -> ProcessDesc:
    return {
        'desc1': f'Searching for normal-sized rolls of {greige.id} to load ports'
    }

def normal_rolls_yld(ret: PortLoad) -> ProcessDesc:
    return {
        'desc1': f'Can load port with {ret.roll1.lbs:.2f} lbs of {ret.roll1.id}'
    }

def half_rolls_args(greige: GreigeStyle, inv: Inventory, prev_wts: list[float],
                      jet_rng: FloatRange, used: str | None = None) -> ProcessDesc:
    return {
        'desc1': f'Searching for half-sized rolls of {greige.id} to load ports'
    }

def half_rolls_yld(ret: PortLoad) -> ProcessDesc:
    return {
        'desc1': f'Can load port with {ret.roll1.lbs:.2f} lbs of {ret.roll1.id}'
    }

def odd_rolls_args(greige: GreigeStyle, inv: Inventory, prev_wts: list[float],
                  jet_rng: FloatRange, extras: list[RollPiece]) -> ProcessDesc:
    return {
        'desc1': f'Searching for odd-sized rolls of {greige.id} to split and load ports'
    }

def odd_rolls_yld(ret: PortLoad) -> ProcessDesc:
    return {
        'desc1': f'Can load port with {ret.roll1.lbs:.2f} lbs of {ret.roll1.id}'
    }

def comb_rolls_args(greige: GreigeStyle, inv: Inventory, extras: list[RollPiece],
                   tgt_rng: FloatRange) -> ProcessDesc:
    return {
        'desc1': f'Looking for partials of {greige.id} to combine and load ports'
    }

def comb_rolls_yld(ret: PortLoad) -> ProcessDesc:
    return {
        'desc1': f'Can combine {ret.roll1.id} and {ret.roll2.id}',
        'desc2': f'Total weight: {ret.roll1.lbs+ret.roll2.lbs:.2f} lbs'
    }

def req_cost_args(cur_req: Req, dmnd: Demand) -> ProcessDesc:
    return {
        'desc1': 'Calculating penalties for late orders and excess inventory',
        'desc2': f'Target item: {cur_req.item.id}'
    }

def req_cost_ret(ret: tuple[float, float, float, float]) -> ProcessDesc:
    cur_late, cur_inv, other_late, other_inv = ret
    return {
        'desc1': f'Late penalties for current item: {cur_late:.2f}',
        'desc3': f'Total penalties on other items: {other_late:.2f}',
        'desc2': f'Inventory penalties for current item: {cur_inv + other_inv:.2f}'
    }

def strip_cost_args(sched: JetSched, jet: Jet) -> ProcessDesc:
    return {
        'desc1': f'Calculating penalties for strip cycles on {jet.id}'
    }

def strip_cost_ret(ret: float) -> ProcessDesc:
    return {
        'desc1': f'Strip penalties: {ret:.2f}'
    }

def not_seq_args(sched: JetSched, jet: Jet) -> ProcessDesc:
    return {
        'desc1': f'Calculating penalties for minor schedule violations on {jet.id}'
    }

def not_seq_ret(ret: tuple[float, float]) -> ProcessDesc:
    return {
        'desc1': f'Not sequenced penalties: {ret[0]}',
        'desc2': f'Other penalties: {ret[1]}'
    }