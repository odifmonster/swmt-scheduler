#!/usr/bin/env python

from typing import Literal

from app.support.logging import FormattedArgs, FormattedRet
from app.support import FloatRange
from app.style import GreigeStyle
from app.inventory import RollView, Inventory
from app.schedule import Req, Jet, DyeLot, Demand, JetSched

class _NJI:
    jet: Jet
    idx: int
    cost: float

class _RP:
    id: str
    rview: RollView
    lbs: float

class _PLFull:
    roll1: _RP
    roll2: _RP

class _PLReg:
    roll1: _RP
    roll2: None

def make_schedule_args(dmnd: Demand, inv: Inventory, jets: list[Jet]) -> FormattedArgs:
    return { 'desc1': 'Running scheduling algorithm' }

def make_schedule_ret(_: None) -> FormattedRet:
    return {}

def get_best_job_args(req: Req, pnum: int, jets: list[Jet], inv: Inventory, dmnd: Demand) -> FormattedArgs:
    return {
        'desc1': f'Getting best job for P{pnum} of {req.id}',
        'desc2': f'{req.bucket(pnum).yds:.2f} yards needed to make truck',
        'desc3': f'{req.bucket(pnum).total_yds:.2f} yards needed to meet requirement'
    }

def get_best_job_ret(jobinfo: _NJI | None) -> FormattedRet:
    if jobinfo is None:
        return { 'result': 'Best option is not to schedule' }
    return { 'result': f'Best option is to schedule after {jobinfo.idx} job(s) on {jobinfo.jet.id}' }

def get_dyelot_args(req: Req, pnum: int, jet: Jet, inv: Inventory) -> FormattedArgs:
    return {
        'desc1': f'Attempting to load {jet.id} with {req.greige.id} for P{pnum} of {req.id}',
        'desc2': f'{req.bucket(pnum).lbs:.2f} pounds needed to make truck',
        'desc3': f'{req.bucket(pnum).lbs:.2f} pounds needed to meet requirement'
    }

type DyeLotRet = tuple[list[_PLFull | _PLReg], set[RollView], DyeLot | None,
                       Literal['CANNOT RUN', 'NO GREIGE', 'N/A']]
def get_dyelot_ret(ret: DyeLotRet) -> FormattedRet:
    fmtd: FormattedRet = {}
    if ret[2] is None:
        fmtd['result'] = 'Could not load jet'
        if ret[3] == 'CANNOT RUN':
            fmtd['notes1'] = 'Jet cannot run item'
        elif ret[3] == 'NO GREIGE':
            fmtd['notes1'] = 'Insufficient greige in inventory'
            fmtd['notes2'] = f'Could only fill {len(ret[0])} port(s)'
    else:
        fmtd['result'] = 'Can load jet'
        fmtd['notes1'] = f'Will use {ret[2].lbs:.2f} pounds of {ret[2].greige.id}'
        fmtd['notes2'] = f'Will yield {ret[2].yds:.2f} yards of {ret[2].item.id}'
    return fmtd

def get_comb_rolls_args(greige: GreigeStyle, inv: Inventory, extras: list[_RP], tgt_rng: FloatRange) \
    -> FormattedArgs:
    return { 'desc1': f'Combining rolls of {greige.id}' }

def get_comb_rolls_yld(port_load: _PLFull) -> FormattedRet:
    return {
        'result': f'Combined {port_load.roll1.id} and {port_load.roll2.id} into {port_load.roll1.lbs+port_load.roll2.lbs:.2f} lb port load'
    }

def get_normal_rolls_args(greige: GreigeStyle, inv: Inventory, prev_wts: list[float],
                          jet_rng: FloatRange, used: str | None = None) -> FormattedArgs:
    return { 'desc1': f'Getting standard rolls of {greige.id}' }

def get_normal_rolls_yld(port_load: _PLReg) -> FormattedRet:
    return {
        'result': f'{port_load.roll1.lbs:.2f} lbs of {port_load.roll1.id}'
    }

def get_half_loads_args(greige: GreigeStyle, inv: Inventory, prev_wts: list[float],
                        jet_rng: FloatRange, used: str | None = None) -> FormattedArgs:
    return { 'desc1': f'Getting half rolls of {greige.id}' }

def get_half_loads_yld(port_load: _PLReg) -> FormattedRet:
    return {
        'result': f'{port_load.roll1.lbs:.2f} lbs of {port_load.roll1.id}'
    }

def get_odd_loads_args(greige: GreigeStyle, inv: Inventory, prev_wts: list[float],
                       jet_rng: FloatRange, extras: list[_RP]) -> FormattedArgs:
    return { 'desc1': f'Getting port loads from odd-size rolls of {greige.id}' }

def get_odd_loads_yld(port_load: _PLReg) -> FormattedRet:
    return {
        'result': f'{port_load.roll1.lbs:.2f} lbs of {port_load.roll1.id}'
    }

def get_port_loads_args(greige: GreigeStyle, inv: Inventory, jet_rng: FloatRange,
                        used: _PLReg | None = None) -> FormattedArgs:
    fmtr: FormattedArgs =  {
        'desc1': f'Getting available rolls of {greige.id} to load ports'
    }
    if used:
        fmtr['desc2'] = f'Using {used.roll1.lbs:.2f} lbs of {used.roll1.id} in first port'
    
    return fmtr

def get_port_loads_yld(port_load: _PLFull | _PLReg) -> FormattedRet:
    lbs = port_load.roll1.lbs
    if port_load.roll2:
        lbs += port_load.roll2.lbs
    
    return {
        'result': f'{lbs:.2f} lb port load'
    }

def get_jet_loads_args(greige: GreigeStyle, inv: Inventory, jet: Jet) -> FormattedArgs:
    return {
        'desc1': f'Finding rolls of {greige.id} to load in {jet.id}'
    }

def get_jet_loads_ret(loads: list[_PLFull | _PLReg]) -> FormattedRet:
    return {
        'result': f'Found greige for {len(loads)} ports'
    }

def req_cost_args(cur_req: Req, dmnd: Demand) -> FormattedArgs:
    return {
        'desc1': 'Calculating cost of missed shipments and excess inventory'
    }



def req_cost_ret(ret: tuple[float, float]) -> FormattedRet:
    return {
        'result' : f'Found late cost of {ret[0]}, inv_cost of {ret[1]}'
    }   

def strip_cost_args(sched: JetSched, jet: Jet) -> FormattedArgs:
    return {
        'desc1': f'Calculating strip cost for {jet.id}'
    }

def strip_cost_ret(strip_cost: float) -> FormattedRet:
    return{
        'result': f'Found strip cost of {strip_cost}'
    }

def not_seq_cost_args(sched: JetSched, jet: Jet) -> FormattedArgs:
    return{
        'desc1': f'Calcuating non_seq and non_black_9 cost for {jet.id}'
    }

def not_seq_cost_ret(ret: tuple[float, float]) -> FormattedRet:
    return{
        'result': f'Found non_seq cost of {ret[0]}, and non_black_9 cost of {ret[1]}'
    }


