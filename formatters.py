#!/usr/bin/env python

from typing import Literal

from app.support.logging import FormattedArgs, FormattedRet
from app.style import GreigeStyle
from app.inventory import RollView
from app.schedule import Req, Jet, DyeLot

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

def make_schedule_args(_dmnd, _inv, _jets) -> FormattedArgs:
    return { 'desc1': 'Running scheduling algorithm' }

def make_schedule_ret(_: None) -> FormattedRet:
    return {}

def get_best_job_args(req: Req, pnum: int, _jets: list[Jet], _inv, _dmnd) -> FormattedArgs:
    return {
        'desc1': f'Getting best job for P{pnum} of {req.id}',
        'desc2': f'{req.bucket(pnum).yds:.2f} yards needed to make truck',
        'desc3': f'{req.bucket(pnum).total_yds:.2f} yards needed to meet requirement'
    }

def get_best_job_ret(jobinfo: _NJI | None) -> FormattedRet:
    if jobinfo is None:
        return { 'result': 'Best option is not to schedule' }
    return { 'result': f'Best option is to schedule after {jobinfo.idx} job(s) on {jobinfo.jet.id}' }

def get_dyelot_args(req: Req, pnum: int, jet: Jet, _inv) -> FormattedArgs:
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

def get_comb_rolls_args(greige: GreigeStyle, _inv, _extras, _tgt_rng) -> FormattedArgs:
    return { 'desc1': f'Combining rolls of {greige.id}' }

def get_comb_rolls_yld(port_load: _PLFull) -> FormattedRet:
    return {
        'result': f'Combined {port_load.roll1.id} and {port_load.roll2.id} into {port_load.roll1.lbs+port_load.roll2.lbs:.2f} lb port load'
    }

def get_normal_rolls_args(greige: GreigeStyle, _inv, _prev_wts, _jet_rng) -> FormattedArgs:
    return { 'desc1': f'Getting standard rolls of {greige.id}' }

def get_normal_rolls_yld(port_load: _PLReg) -> FormattedRet:
    return {
        'result': f'{port_load.roll1.lbs:.2f} lbs of {port_load.roll1.id}'
    }

def get_half_loads_args(greige: GreigeStyle, _inv, _prev_wts, _jet_rng) -> FormattedArgs:
    return { 'desc1': f'Getting half rolls of {greige.id}' }

def get_half_loads_yld(port_load: _PLReg) -> FormattedRet:
    return {
        'result': f'{port_load.roll1.lbs:.2f} lbs of {port_load.roll1.id}'
    }

def get_odd_loads_args(greige: GreigeStyle, _inv, _prev_wts, _jet_rng, _extras) -> FormattedArgs:
    return { 'desc1': f'Getting port loads from odd-size rolls of {greige.id}' }

def get_odd_loads_yld(port_load: _PLReg) -> FormattedRet:
    return {
        'result': f'{port_load.roll1.lbs:.2f} lbs of {port_load.roll1.id}'
    }

def get_port_loads_args(greige: GreigeStyle, _inv, _jet_rng) -> FormattedArgs:
    return {
        'desc1': f'Getting available rolls of {greige.id} to load ports'
    }

def get_port_loads_yld(port_load: _PLFull | _PLReg) -> FormattedRet:
    lbs = port_load.roll1.lbs
    if port_load.roll2:
        lbs += port_load.roll2.lbs
    
    return {
        'result': f'{lbs:.2f} lb port load'
    }