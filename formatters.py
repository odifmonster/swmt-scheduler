#!/usr/bin/env python

from typing import Literal

from app.support.logging import FormattedArgs, FormattedRet
from app.inventory import RollView
from app.schedule import Req, Jet, DyeLot

from getrolls import PortLoad

class _NJI:
    jet: Jet
    idx: int
    cost: float

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

type DyeLotRet = tuple[list[PortLoad], set[RollView], DyeLot | None,
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