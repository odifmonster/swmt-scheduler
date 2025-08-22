#!/usr/bin/env python

from typing import NamedTuple, Unpack, Literal, Generator
import datetime as dt, pandas as pd, os

from app.support import logging, FloatRange
from app.style import color, GreigeStyle
from app.inventory import roll, Inventory, AllocRoll, RollView
from app.schedule import DyeLot, Job, Jet, JetSched, Req, Demand

from loaddata import load_inv, load_demand, load_adaptive_jobs
from formatters import make_schedule_args, make_schedule_ret, get_best_job_args, get_best_job_ret, \
    get_dyelot_args, get_dyelot_ret, get_comb_rolls_args, get_comb_rolls_yld, get_normal_rolls_args, \
    get_normal_rolls_yld, get_half_loads_args, get_half_loads_yld, get_odd_loads_args, \
    get_odd_loads_yld, get_port_loads_args, get_port_loads_yld
from gettables import get_jobs_data, get_rolls_data, get_missing_data, get_process_data

LOGGER = logging.Logger()

class RollPiece(NamedTuple):
    id: str
    rview: RollView
    lbs: float

class PortLoad(NamedTuple):
    roll1: RollPiece
    roll2: RollPiece | None

class SplitRoll(NamedTuple):
    full: list[RollPiece]
    extra: RollPiece

def get_splits(rview: RollView, tgt_rng: FloatRange) -> SplitRoll:
    x = round(rview.lbs / tgt_rng.average())
    if x > 0 and tgt_rng.contains(rview.lbs / x):
        split_wt = rview.lbs / x
        full = [RollPiece(rview.id, rview, split_wt) for _ in range(x)]
        return SplitRoll(full, RollPiece(rview.id, rview, 0))
    
    split_wt = tgt_rng.average()
    nsplits = int(rview.lbs / split_wt)
    full = [RollPiece(rview.id, rview, split_wt) for _ in range(nsplits)]
    return SplitRoll(full, RollPiece(rview.id, rview, rview.lbs - nsplits*split_wt))

@logging.logged_generator(LOGGER, arg_fmtr=get_comb_rolls_args, yld_fmtr=get_comb_rolls_yld)
def get_comb_rolls(greige: GreigeStyle, inv: Inventory, extras: list[RollPiece],
                   tgt_rng: FloatRange) -> Generator[PortLoad | logging.LogGenMsg]:
    extra_ids: set[str] = { piece.id for piece in extras }
    if roll.PARTIAL not in inv[greige]:
        yield logging.LogGenMsg(result=f'No partial rolls of {greige.id} in inventory.')
        return
    
    subgroup = inv[greige, roll.PARTIAL]
    pieces = extras.copy()
    
    for rid in subgroup:
        if rid not in extra_ids:
            pieces.append(RollPiece(rid, subgroup[rid], subgroup[rid].lbs))
    
    used_ids: set[str] = set()

    for i in range(len(pieces)):
        roll1 = pieces[i]
        for j in range(i+1, len(pieces)):
            roll2 = pieces[j]
            if tgt_rng.contains(roll1.lbs + roll2.lbs) and roll1.id not in used_ids and \
                roll2.id not in used_ids:
                used_ids.add(roll1.id)
                used_ids.add(roll2.id)
                yield PortLoad(roll1, roll2)
            elif roll1.id not in used_ids and roll2.id not in used_ids:
                yield logging.LogGenMsg(result=f'Combined {roll1.id} and {roll2.id} out of target range',
                                notes1=f'Combined weight: {roll1.lbs+roll2.lbs:.2f} lbs',
                                notes2=f'Target range: {tgt_rng.minval:.2f} to {tgt_rng.maxval:.2f} lbs')

@logging.logged_generator(LOGGER, arg_fmtr=get_normal_rolls_args, yld_fmtr=get_normal_rolls_yld)
def get_normal_loads(greige: GreigeStyle, inv: Inventory, prev_wts: list[float],
                     jet_rng: FloatRange) -> Generator[PortLoad | logging.LogGenMsg]:
    if roll.NORMAL not in inv[greige]:
        yield logging.LogGenMsg(result=f'No normal rolls of {greige.id} in inventory.')
        return
    
    for rid in inv[greige, roll.NORMAL]:
        rview = inv[greige, roll.NORMAL, rid]
        
        if not prev_wts:
            rng = FloatRange(max(jet_rng.minval, greige.port_range.minval),
                             min(jet_rng.maxval, greige.port_range.maxval))
        else:
            rng = FloatRange(max(max(prev_wts)-20, jet_rng.minval),
                             min(min(prev_wts)+20, jet_rng.maxval))
            
        if not rng.contains(rview.lbs / 2):
            yield logging.LogGenMsg(result=f'{rview.id} weight out of target range',
                            notes1=f'Half roll weight: {rview.lbs/2:.2f}',
                            notes2=f'Target range: {rng.minval:.2f} to {rng.maxval:.2f} lbs')
            continue

        prev_wts.append(rview.lbs / 2)
        yield PortLoad(RollPiece(rview.id, rview, rview.lbs / 2), None)
        yield PortLoad(RollPiece(rview.id, rview, rview.lbs / 2), None)

@logging.logged_generator(LOGGER, arg_fmtr=get_half_loads_args, yld_fmtr=get_half_loads_yld)
def get_half_loads(greige: GreigeStyle, inv: Inventory, prev_wts: list[float],
                   jet_rng: FloatRange) -> Generator[PortLoad | logging.LogGenMsg]:
    if roll.HALF not in inv[greige]:
        yield logging.LogGenMsg(result=f'No half rolls of {greige.id} in inventory.')
        return
    
    for rid in inv[greige, roll.HALF]:
        rview = inv[greige, roll.HALF, rid]

        if not prev_wts:
            rng = FloatRange(max(jet_rng.minval, greige.port_range.minval),
                             min(jet_rng.maxval, greige.port_range.maxval))
        else:
            rng = FloatRange(max(max(prev_wts)-20, jet_rng.minval),
                             min(min(prev_wts)+20, jet_rng.maxval))
            
        if not rng.contains(rview.lbs):
            yield logging.LogGenMsg(result=f'{rview.id} weight out of target range',
                            notes1=f'Roll weight: {rview.lbs/2:.2f}',
                            notes2=f'Target range: {rng.minval:.2f} to {rng.maxval:.2f} lbs')
            continue

        prev_wts.append(rview.lbs)
        yield PortLoad(RollPiece(rview.id, rview, rview.lbs), None)

@logging.logged_generator(LOGGER, arg_fmtr=get_odd_loads_args, yld_fmtr=get_odd_loads_yld)
def get_odd_loads(greige: GreigeStyle, inv: Inventory, prev_wts: list[float],
                  jet_rng: FloatRange, extras: list[RollPiece]) -> Generator[PortLoad | logging.LogGenMsg]:
    if not prev_wts:
        rng = FloatRange(max(jet_rng.minval, greige.port_range.minval),
                         min(jet_rng.maxval, greige.port_range.maxval))
    else:
        rng = FloatRange(max(max(prev_wts)-20, jet_rng.minval),
                         min(min(prev_wts)+20, jet_rng.maxval))
        
    for size in (roll.LARGE, roll.SMALL):
        if size not in inv[greige]:
            yield logging.LogGenMsg(result=f'No {size.lower()} rolls of {greige.id} in inventory.')
            continue

        for rid in inv[greige, size]:
            
            splits = get_splits(inv[greige, size, rid], rng)

            for item in splits.full:
                prev_wts.append(item.lbs)
                yield PortLoad(item, None)

            if splits.extra.lbs > 20:
                extras.append(splits.extra)

@logging.logged_generator(LOGGER, arg_fmtr=get_port_loads_args, yld_fmtr=get_port_loads_yld)
def get_port_loads(greige: GreigeStyle, inv: Inventory, jet_rng: FloatRange) \
    -> Generator[PortLoad | logging.LogGenMsg]:
    if greige not in inv:
        yield logging.LogGenMsg(result=f'No {greige.id} in inventory.')
        return
    
    prev_wts: list[float] = []
    normal = get_normal_loads(greige, inv, prev_wts, jet_rng)
    for load in normal:
        yield load
    half = get_half_loads(greige, inv, prev_wts, jet_rng)
    for load in half:
        yield load
    extras: list[RollPiece] = []
    odd = get_odd_loads(greige, inv, prev_wts, jet_rng, extras)
    for load in odd:
        yield load
    if not prev_wts:
        tgt_rng = FloatRange(max(jet_rng.minval, greige.port_range.minval),
                             min(jet_rng.maxval, greige.port_range.maxval))
    else:
        tgt_rng = FloatRange(max(max(prev_wts)-20, jet_rng.minval),
                             min(min(prev_wts)+20, jet_rng.maxval))
    comb = get_comb_rolls(greige, inv, extras, tgt_rng)
    for load in comb:
        yield load

class NewJobInfo(NamedTuple):
    jet: Jet
    idx: int
    port_loads: list[PortLoad]
    cost: float

def cost_func(sched: JetSched, jet: Jet, cur_req: Req, dmnd: Demand) -> tuple[float, float]:
    late_cost = 0
    inv_cost = 0
    for key in dmnd.fullkeys():
        rview = dmnd[key]
        for yds, tdelta in rview.late_yd_buckets():
            if yds < 200 or tdelta.total_seconds() <= 0: continue

            days_late = tdelta.total_seconds() / (3600*24)
            if 0 < days_late < 4:
                late_cost += (1000 + yds*0.05)
            elif days_late < 5:
                late_cost += (1500 + yds*0.05)
            elif days_late < 6:
                late_cost += (2500 + yds*0.05)
            elif days_late >= 6:
                late_cost += (5000 + yds*0.05)
                
        if rview.bucket(4).yds < 0:
            inv_cost += (abs(rview.bucket(4).yds) * 0.02 * 2)
    
    for yds, tdelta in cur_req.late_yd_buckets():
        if yds < 200 or tdelta.total_seconds() <= 0: continue

        days_late = tdelta.total_seconds() / (3600*24)
        if 0 < days_late < 4:
            late_cost += (1000 + yds*0.05)
        elif days_late < 5:
            late_cost += (1500 + yds*0.05)
        elif days_late < 6:
            late_cost += (2500 + yds*0.05)
        elif days_late >= 6:
            late_cost += (5000 + yds*0.05)
    
    strip_cost = 0
    cost_12_port_hrs = 150
    for job in sched.jobs:
        if job.shade in (color.STRIP, color.HEAVYSTRIP):
            cur_cost = cost_12_port_hrs * (job.cycle_time.total_seconds() / (3600 * 12))
            strip_cost += cur_cost
    
    shade_vals = {
        color.SOLUTION: 0, color.LIGHT: 3, color.MEDIUM: 6, color.BLACK: 9
    }

    not_seq_cost = 0
    non_black_9 = 0
    for job1, job2 in zip(sched.jobs[:-1], sched.jobs[1:]):
        if job1.shade in (color.STRIP, color.HEAVYSTRIP) or \
            job2.shade in (color.STRIP, color.HEAVYSTRIP):
            continue
        if jet.id == 'Jet-09' and job1.shade != color.BLACK:
            non_black_9 += 5

        val1 = shade_vals[job1.shade]
        val2 = shade_vals[job2.shade]
        diff = val2 - val1
        if diff > 0:
            diff /= 2
        
        not_seq_cost += abs(diff)
    if jet.id == 'Jet-09' and len(sched.jobs) > 0 and \
        sched.jobs[-1].shade not in (color.STRIP, color.HEAVYSTRIP) \
        and sched.jobs[-1].shade != color.BLACK:
        non_black_9 += 5
    
    return late_cost*0.9, max(0, inv_cost) + strip_cost + not_seq_cost*1.2 + non_black_9

@logging.logged_func(LOGGER, arg_fmtr=get_dyelot_args, ret_fmtr=get_dyelot_ret)
def get_dyelot(req: Req, pnum: int, jet: Jet, inv: Inventory) \
    -> tuple[list[PortLoad], set[RollView], DyeLot | None, Literal['N/A', 'CANNOT RUN', 'NO GREIGE']]:
    if not req.item.can_run_on_jet(jet.id):
        return [], set(), None, 'CANNOT RUN'
    
    port_loads: list[PortLoad] = []
    loads = get_port_loads(req.greige, inv, jet.load_rng)
    for i, load in enumerate(loads):
        if i == jet.n_ports: break
        port_loads.append(load)
    
    if len(port_loads) < jet.n_ports:
        return port_loads, set(), None, 'NO GREIGE'
    
    temp_rolls: list[AllocRoll] = []
    used_rolls: set[RollView] = set()

    for load in port_loads:
        to_use = inv.remove(load.roll1.rview)
        used_rolls.add(to_use.view())
        aroll = to_use.use(load.roll1.lbs, temp=True)
        inv.add(to_use)
        if load.roll2:
            to_use = inv.remove(load.roll2.rview)
            aroll = to_use.use(load.roll2.lbs, aroll=aroll, temp=True)
            used_rolls.add(to_use.view())
            inv.add(to_use)
        temp_rolls.append(aroll)
    
    return port_loads, used_rolls, req.assign_lot(temp_rolls, pnum), 'N/A'

@logging.logged_func(LOGGER, arg_fmtr=get_best_job_args, ret_fmtr=get_best_job_ret)
def get_best_job(req: Req, pnum: int, jets: list[Jet], inv: Inventory, dmnd: Demand) -> NewJobInfo | None:
    newjobs: list[NewJobInfo] = []
    for jet in jets:
        port_loads, used_rolls, lot, _ = get_dyelot(req, pnum, jet, inv)
        if not lot: continue

        job = Job.make_job(dt.datetime.fromtimestamp(0), (lot,))
        for idx, cost in jet.get_all_options(job, req, dmnd, cost_func):
            newjobs.append(NewJobInfo(jet, idx, port_loads, cost))

        for rview in used_rolls:
            r = inv.remove(rview)
            r.reset()
            inv.add(r)

        req.unassign_lot(lot.view())
    
    if not newjobs:
        return None
    
    newjobs = sorted(newjobs, key=lambda j: j.cost)
    bestjob = newjobs[0]
    
    if bestjob.idx < 0:
        return None
    return bestjob

def assign_job(job_info: NewJobInfo, req: Req, pnum: int, inv: Inventory) -> None:
    arolls: list[AllocRoll] = []

    for load in job_info.port_loads:
        roll1 = inv.remove(load.roll1.rview)
        aroll = roll1.use(load.roll1.lbs)
        if roll1.lbs > 20:
            inv.add(roll1)

        if not load.roll2 is None:
            roll2 = inv.remove(load.roll2.rview)
            aroll = roll2.use(load.roll2.lbs, aroll=aroll)
            if roll2.lbs > 20:
                inv.add(roll2)
        
        arolls.append(aroll)
    
    lot = req.assign_lot(arolls, pnum)
    job = Job.make_job(dt.datetime.fromtimestamp(0), (lot,))
    
    newsched, kicked, scheduled = job_info.jet.try_insert_job(job, job_info.idx)
    if not scheduled:
        raise RuntimeError('Do not call \'assign_job\' on un-tested jobs.')

    for kjob in kicked:
        kjob.start = None

    job_info.jet.sched.clear_jobs()
    for njob in newsched.jobs:
        njob.start = job_info.jet.sched.last_job_end
        job_info.jet.sched.add_job(njob)

@logging.logged_func(LOGGER, arg_fmtr=make_schedule_args, ret_fmtr=make_schedule_ret)
def make_schedule(demand: Demand, inv: Inventory, jets: list[Jet]) -> None:
    for i in range(1,5):
        keys = sorted(demand.fullkeys(), key=lambda k: k[1].shade)
        for key in keys:
            reqview = demand[key]
            req = demand.remove(reqview)
            bucket = req.bucket(i)

            while bucket.total_yds >= 200:
                best_job = get_best_job(req, i, jets, inv, demand)
                if best_job is None:
                    break
                assign_job(best_job, req, i, inv)
            
            demand.add(req)

def df_cols_to_string(df: pd.DataFrame, *args: Unpack[tuple[str, ...]]) -> pd.DataFrame:
    for col in args:
        df[col] = df[col].astype('string')
    return df

def write_to_output(jets: list[Jet], dmnd: Demand) -> None:
    dirpath = os.path.join(os.path.dirname(__file__), 'datasrc')
    writer = pd.ExcelWriter(os.path.join(dirpath, 'output.xlsx'),
                            datetime_format='MM/DD HH:MM:SS')

    job_ids, jobs_table = get_jobs_data(jets)
    jobs_df = pd.DataFrame(data=jobs_table, index=job_ids)
    jobs_df = df_cols_to_string(jobs_df, 'jet', 'item', 'greige', 'color')
    jobs_df.to_excel(writer, sheet_name='jobs', float_format='%.2f', index_label='job_id')

    alloc_ids, rolls_table = get_rolls_data(jets)
    rolls_df = pd.DataFrame(data=rolls_table, index=alloc_ids)
    rolls_df = df_cols_to_string(rolls_df, 'job_id', 'jet', 'greige', 'roll1', 'roll2', 'item',
                                 'color')
    rolls_df.to_excel(writer, sheet_name='roll_allocation', float_format='%.2f')

    missing_table = get_missing_data(dmnd)
    missing_df = pd.DataFrame(data=missing_table)
    missing_df = df_cols_to_string(missing_df, 'item', 'scheduled')
    missing_df.to_excel(writer, sheet_name='late_orders', index=False, float_format='%.2f')

    proc_ids, process_table = get_process_data(LOGGER)
    process_df = pd.DataFrame(data=process_table, index=proc_ids)
    process_df = df_cols_to_string(process_df, 'name', 'desc1', 'desc2', 'desc3', 'result',
                                   'notes1', 'notes2')
    process_df.to_excel(writer, sheet_name='logs')

    writer.close()

def main():
    inv = load_inv()
    dmnd = load_demand(dt.datetime(2025, 8, 22, hour=12))
    jets = load_adaptive_jobs(dt.datetime(2025, 8, 22),
                              dt.datetime(2025, 8, 29, hour=23, minute=59, second=59))
    
    make_schedule(dmnd, inv, jets)
    write_to_output(jets, dmnd)
    
if __name__ == '__main__':
    main()