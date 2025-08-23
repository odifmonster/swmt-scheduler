#!/usr/bin/env python

from typing import Unpack, Literal, Generator
import datetime as dt, pandas as pd, os

from app.support import FloatRange, logging
from app.style import color, GreigeStyle
from app.inventory import roll, Inventory, AllocRoll, RollView
from app.schedule import DyeLot, Job, Jet, JetSched, Req, Demand, ReqView

from schedtypes import SplitRoll, RollPiece, PortLoad, NewJobInfo
from loaddata import load_inv, load_demand, load_adaptive_jobs
from formatters import make_sched_args, make_sched_ret, best_job_args, best_job_ret, dyelot_args, \
    dyelot_ret, jet_loads_args, jet_loads_ret, grg_starts_args, grg_starts_yld, port_loads_args, \
    port_loads_yld, normal_rolls_args, normal_rolls_yld, half_rolls_args, half_rolls_yld, \
    odd_rolls_args, odd_rolls_yld, comb_rolls_args, comb_rolls_yld, req_cost_args, req_cost_ret, \
    strip_cost_args, strip_cost_ret, not_seq_args, not_seq_ret
from gettables import get_jobs_data, get_rolls_data, get_missing_data, get_logs_data

LOGGER = logging.Logger()
Jet.set_logger(LOGGER)

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

@logging.logged_generator(LOGGER, comb_rolls_args, comb_rolls_yld)
def get_comb_rolls(greige: GreigeStyle, inv: Inventory, extras: list[RollPiece],
                   tgt_rng: FloatRange) -> Generator[PortLoad | logging.FailedYield]:
    extra_ids: set[str] = { piece.id for piece in extras }
    if roll.PARTIAL not in inv[greige]:
        yield logging.FailedYield(desc1=f'No partial rolls of {greige.id} in inventory.')
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
                yield logging.FailedYield(
                    desc1=f'Combination of {roll1.id} and {roll2.id} outside of target range',
                    desc2=f'Total weight: {roll1.lbs+roll2.lbs:.2f} lbs',
                    desc3=f'Target: {tgt_rng.minval:.2f} to {tgt_rng.maxval:.2f} lbs'
                )

@logging.logged_generator(LOGGER, normal_rolls_args, normal_rolls_yld)
def get_normal_loads(greige: GreigeStyle, inv: Inventory, prev_wts: list[float],
                     jet_rng: FloatRange, used: str | None = None) \
                        -> Generator[PortLoad | logging.FailedYield]:
    if roll.NORMAL not in inv[greige]:
        yield logging.FailedYield(desc1=f'No normal-sized rolls of {greige.id} in inventory.')
        return
    
    for rid in inv[greige, roll.NORMAL]:
        if used and rid == used: continue
        rview = inv[greige, roll.NORMAL, rid]
        
        if not prev_wts:
            rng = FloatRange(max(jet_rng.minval, greige.port_range.minval),
                             min(jet_rng.maxval, greige.port_range.maxval))
        else:
            rng = FloatRange(max(max(prev_wts)-20, jet_rng.minval),
                             min(min(prev_wts)+20, jet_rng.maxval))
            
        if not rng.contains(rview.lbs / 2):
            yield logging.FailedYield(desc1=f'{rview.id} weight outside target range',
                                      desc2=f'Weight: {rview.lbs / 2:.2f} lbs',
                                      desc3=f'Target: {rng.minval:.2f} to {rng.maxval:.2f} lbs')
            continue

        prev_wts.append(rview.lbs / 2)
        yield PortLoad(RollPiece(rview.id, rview, rview.lbs / 2), None)
        yield PortLoad(RollPiece(rview.id, rview, rview.lbs / 2), None)

@logging.logged_generator(LOGGER, half_rolls_args, half_rolls_yld)
def get_half_loads(greige: GreigeStyle, inv: Inventory, prev_wts: list[float],
                   jet_rng: FloatRange, used: str | None = None) \
                    -> Generator[PortLoad | logging.FailedYield]:
    if roll.HALF not in inv[greige]:
        yield logging.FailedYield(desc1=f'No half-sized rolls of {greige.id} in inventory.')
        return
    
    for rid in inv[greige, roll.HALF]:
        if used and rid == used: continue
        rview = inv[greige, roll.HALF, rid]

        if not prev_wts:
            rng = FloatRange(max(jet_rng.minval, greige.port_range.minval),
                             min(jet_rng.maxval, greige.port_range.maxval))
        else:
            rng = FloatRange(max(max(prev_wts)-20, jet_rng.minval),
                             min(min(prev_wts)+20, jet_rng.maxval))
            
        if not rng.contains(rview.lbs):
            yield logging.FailedYield(desc1=f'{rview.id} weight outside target range',
                                      desc2=f'Weight: {rview.lbs:.2f} lbs',
                                      desc3=f'Target: {rng.minval:.2f} to {rng.maxval:.2f} lbs')
            continue

        prev_wts.append(rview.lbs)
        yield PortLoad(RollPiece(rview.id, rview, rview.lbs), None)

@logging.logged_generator(LOGGER, odd_rolls_args, odd_rolls_yld)
def get_odd_loads(greige: GreigeStyle, inv: Inventory, prev_wts: list[float],
                  jet_rng: FloatRange, extras: list[RollPiece]) \
                    -> Generator[PortLoad | logging.FailedYield]:
    if not prev_wts:
        rng = FloatRange(max(jet_rng.minval, greige.port_range.minval),
                         min(jet_rng.maxval, greige.port_range.maxval))
    else:
        rng = FloatRange(max(max(prev_wts)-20, jet_rng.minval),
                         min(min(prev_wts)+20, jet_rng.maxval))
        
    for size in (roll.LARGE, roll.SMALL):
        if size not in inv[greige]:
            yield logging.FailedYield(desc1=f'No {size.lower()} rolls of {greige.id} in inventory')
            continue

        for rid in inv[greige, size]:
            
            splits = get_splits(inv[greige, size, rid], rng)

            for item in splits.full:
                prev_wts.append(item.lbs)
                yield PortLoad(item, None)

            if splits.extra.lbs > 20:
                extras.append(splits.extra)

@logging.logged_generator(LOGGER, grg_starts_args, grg_starts_yld)
def get_starts(greige: GreigeStyle, inv: Inventory, jet: Jet) \
    -> Generator[list[PortLoad] | logging.FailedYield]:
    if greige not in inv:
        yield logging.FailedYield(desc1=f'No normal or half rolls of {greige.id} in inventory.')
        return
    
    for size in (roll.NORMAL, roll.HALF):
        if size not in inv[greige]:
            continue

        for rid in inv[greige, size]:
            rview = inv[greige, size, rid]
            r_wt = rview.lbs if size == roll.HALF else rview.lbs / 2
            if not jet.load_rng.contains(r_wt):
                yield logging.FailedYield(desc1=f'{rview.id} outside of target range',
                                          desc2=f'Weight: {r_wt:.2f} lbs',
                                          desc3=f'Target: {jet.load_rng.minval:.2f} to {jet.load_rng.maxval:.2f} lbs')
                continue

            start: list[PortLoad] = []
            if size == roll.NORMAL:
                start.append(PortLoad(RollPiece(rid, rview, r_wt), None))
                start.append(PortLoad(RollPiece(rid, rview, r_wt), None))
            else:
                start.append(PortLoad(RollPiece(rid, rview, r_wt), None))
            
            yield start

@logging.logged_generator(LOGGER, port_loads_args, port_loads_yld)
def get_port_loads(greige: GreigeStyle, inv: Inventory, jet_rng: FloatRange, used: PortLoad | None = None) \
    -> Generator[PortLoad | logging.FailedYield]:
    if greige not in inv:
        yield logging.FailedYield(desc1=f'No {greige.id} in inventory')
        return
    
    prev_wts: list[float] = []
    used_id = None
    if used:
        prev_wts.append(used.roll1.lbs)
        used_id = used.roll1.id

    normal = get_normal_loads(greige, inv, prev_wts, jet_rng, used=used_id)
    for load in normal:
        yield load
    half = get_half_loads(greige, inv, prev_wts, jet_rng, used=used_id)
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

@logging.logged_func(LOGGER, desc_args=jet_loads_args, desc_ret=jet_loads_ret)
def get_jet_loads(greige: GreigeStyle, inv: Inventory, jet: Jet) -> list[PortLoad]:
    starts = get_starts(greige, inv, jet)

    for start in starts:
        loads: list[PortLoad] = []

        for start_load in start:
            loads.append(start_load)
            if len(loads) == jet.n_ports:
                return loads
        
        used = start[0]
        rem_loads = get_port_loads(greige, inv, jet.load_rng, used=used)
        for load in rem_loads:
            loads.append(load)
            if len(loads) == jet.n_ports:
                return loads
    
    loads: list[PortLoad] = []
    all_loads = get_port_loads(greige, inv, jet.load_rng)
    for load in all_loads:
        loads.append(load)
        if len(loads) == jet.n_ports:
            break
    
    return loads

def get_late_cost(req: Req | ReqView) -> float:
    cost = 0
    for i in range(1,4):
        bucket = req.bucket(i)
        late_table = bucket.late_yds

        if not late_table or bucket.yds < 200: continue
        max_late = late_table[0][1]
        days_late = max_late.total_seconds() / (3600 * 24)

        if 0 < days_late < 4:
            cost += 1000
        elif days_late < 5:
            cost += 1500
        elif days_late < 6:
            cost += 2500
        elif days_late < 10:
            cost += 5000
        elif days_late >= 10:
            cost += 10000

        for yds, tdelta in late_table:
            tdays = tdelta.total_seconds() / (3600 * 24)

            if 0 < tdays < 4:
                cost += yds * 0.01
            elif tdays < 5:
                cost += yds * 0.015
            elif tdays < 6:
                cost += yds * 0.025
            elif tdays < 10:
                cost += yds * 0.5
            elif tdays >= 10:
                cost += yds
    
    return cost

@logging.logged_func(LOGGER, req_cost_args, req_cost_ret)
def req_cost(cur_req: Req, dmnd: Demand) -> tuple[float, float, float, float]:
    other_late = 0
    other_inv = 0

    for key in dmnd.fullkeys():
        rview = dmnd[key]
        other_late += get_late_cost(rview)
                
        if rview.bucket(4).yds < 0:
            other_inv += (abs(rview.bucket(4).yds) * 0.02 * 2)
    
    cur_late = get_late_cost(cur_req)
    cur_inv = 0

    if cur_req.bucket(4).yds < 0:
        cur_inv = (abs(cur_req.bucket(4).yds) * 0.02 * 2)
    
    return cur_late, cur_inv, other_late, other_inv

@logging.logged_func(LOGGER, strip_cost_args, strip_cost_ret)
def strip_cost(sched: JetSched, jet: Jet) -> float:
    strip_cost = 0
    cost_12_port_hrs = 150
    for job in sched.jobs:
        if job.shade in (color.STRIP, color.HEAVYSTRIP):
            cur_cost = cost_12_port_hrs * (job.cycle_time.total_seconds() / (3600 * 12)) * jet.n_ports
            strip_cost += cur_cost
    return strip_cost

@logging.logged_func(LOGGER, not_seq_args, not_seq_ret)
def not_seq_cost(sched: JetSched, jet: Jet):
    shade_vals = {
        color.SOLUTION: 0, color.LIGHT: 5, color.MEDIUM: 10, color.BLACK: 20
    }
    not_seq_cost = 0
    non_black_9 = 0
    for job1, job2 in zip(sched.jobs[:-1], sched.jobs[1:]):
        if job1.shade in (color.STRIP, color.HEAVYSTRIP) or \
            job2.shade in (color.STRIP, color.HEAVYSTRIP):
            continue

        val1 = shade_vals[job1.shade]
        val2 = shade_vals[job2.shade]
        diff = val2 - val1
        if diff > 0:
            diff /= 2
        
        not_seq_cost += abs(diff)
    
    if jet.id == 'Jet-09':
        for job in sched.jobs:
            if job.shade not in (color.STRIP, color.HEAVYSTRIP, color.BLACK):
                non_black_9 += 5
    return not_seq_cost, non_black_9

def cost_func(sched: JetSched, jet: Jet, cur_req: Req, dmnd: Demand) -> tuple[float, float]:
    cur_late, cur_inv, other_late, other_inv = req_cost(cur_req, dmnd)
    scost = strip_cost(sched, jet)
    not_seq_cos, non_black_9 = not_seq_cost(sched, jet)
    return cur_late+other_late+cur_inv+other_inv, scost+not_seq_cos*1.2+non_black_9

@logging.logged_func(LOGGER, desc_args=dyelot_args, desc_ret=dyelot_ret)
def get_dyelot(req: Req, pnum: int, jet: Jet, inv: Inventory) \
    -> tuple[list[PortLoad], set[RollView], DyeLot | None, Literal['N/A', 'CANNOT RUN', 'NO GREIGE']]:
    if not req.item.can_run_on_jet(jet.id):
        return [], set(), None, 'CANNOT RUN'
    
    port_loads = get_jet_loads(req.greige, inv, jet)
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

@logging.logged_func(LOGGER, desc_args=best_job_args, desc_ret=best_job_ret)
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

@logging.logged_func(LOGGER, desc_args=make_sched_args, desc_ret=make_sched_ret)
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

    proc_ids, logs_table = get_logs_data(LOGGER)
    logs_df = pd.DataFrame(data=logs_table, index=proc_ids)
    logs_df = df_cols_to_string(logs_df, 'name', 'desc1', 'desc2', 'desc3')
    logs_df.to_excel(writer, sheet_name='logs', index_label='process_id')

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