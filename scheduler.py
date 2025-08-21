#!/usr/bin/env python

from typing import NamedTuple, Unpack
import datetime as dt, pandas as pd, os

from app.style import color
from app.inventory import Inventory, AllocRoll, RollView
from app.schedule import Job, Jet, JetSched, Req, Demand

from loaddata import load_inv, load_demand, load_adaptive_jobs
from getrolls import PortLoad, get_port_loads
from gettables import get_jobs_data, get_rolls_data, get_missing_data

class NewJobInfo(NamedTuple):
    jet: Jet
    idx: int
    port_loads: list[PortLoad]
    cost: tuple[float, float, float, float, float]
    yds_diff: float

def cost_func(sched: JetSched, jet: Jet, cur_req: Req, dmnd: Demand) \
    -> tuple[float, float, float, float, float]:
    late_cost = 0
    inv_cost = 0
    for key in dmnd.fullkeys():
        rview = dmnd[key]
        for yds, tdelta in rview.late_yd_buckets():
            if yds < 200 or tdelta.total_seconds() <= 0: continue

            days_late = tdelta.total_seconds() / (3600*24)
            if 0 < days_late < 4:
                late_cost += (1000 + yds*0.1)
            elif days_late < 5:
                late_cost += (1500 + yds*0.1)
            elif days_late < 6:
                late_cost += (2500 + yds*0.1)
            elif days_late >= 6:
                late_cost += (5000 + yds*0.1)
                
        if rview.bucket(4).yds < 0:
            inv_cost += (abs(rview.bucket(4).yds) * 0.02 * 2)
    
    for yds, tdelta in cur_req.late_yd_buckets():
        if yds < 200 or tdelta.total_seconds() <= 0: continue

        days_late = tdelta.total_seconds() / (3600*24)
        if 0 < days_late < 4:
            late_cost += (1000 + yds*0.1)
        elif days_late < 5:
            late_cost += (1500 + yds*0.1)
        elif days_late < 6:
            late_cost += (2500 + yds*0.1)
        elif days_late >= 6:
            late_cost += (5000 + yds*0.1)
    
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
        
        not_seq_cost += abs(diff) * 0.1
    if jet.id == 'Jet-09' and len(sched.jobs) > 0 and \
        sched.jobs[-1].shade not in (color.STRIP, color.HEAVYSTRIP) \
        and sched.jobs[-1].shade != color.BLACK:
        non_black_9 += 5
    
    return (late_cost, max(0,inv_cost), strip_cost, not_seq_cost, non_black_9)

def get_best_job(req: Req, pnum: int, jets: list[Jet], inv: Inventory, dmnd: Demand) -> NewJobInfo | None:
    newjobs: list[NewJobInfo] = []
    for jet in jets:
        if not req.item.can_run_on_jet(jet.id): continue

        port_loads: list[PortLoad] = []
        loads = get_port_loads(req.greige, inv, jet.load_rng)
        for i, load in enumerate(loads):
            if i == jet.n_ports: break
            port_loads.append(load)
        
        if len(port_loads) < jet.n_ports:
            print(f'not enough inventory for {req.greige} on {jet.id}.')
            if req.greige in inv:
                print(inv[req.greige])
            print()
            continue

        temp_rolls: list[AllocRoll] = []
        used_rolls: set[RollView] = set()

        for load in port_loads:
            use_roll = inv.remove(load.roll1.rview)
            used_rolls.add(use_roll.view())
            aroll = use_roll.use(load.roll1.lbs, temp=True)
            inv.add(use_roll)
            if not load.roll2 is None:
                use_roll = inv.remove(load.roll2.rview)
                aroll = use_roll.use(load.roll2.lbs, temp=True)
                used_rolls.add(use_roll.view())
                inv.add(use_roll)
            temp_rolls.append(aroll)

        lot = req.assign_lot(temp_rolls, pnum)
        job = Job.make_job(dt.datetime.fromtimestamp(0), (lot,))
        yds_diff = abs(job.yds - req.bucket(pnum).yds)
        n = 0
        for idx, cost in jet.get_all_options(job, req, dmnd, cost_func):
            n += 1
            newjobs.append(NewJobInfo(jet, idx, port_loads, cost, yds_diff))
        if n == 0:
            print(f'Could not fit P{pnum} for {req} onto {jet.id}.')

        for rview in used_rolls:
            r = inv.remove(rview)
            r.reset()
            inv.add(r)

        req.unassign_lot(lot.view())
    
    if not newjobs:
        return None
    
    newjobs = sorted(newjobs, key=lambda j: (sum(j.cost), yds_diff))
    # for job in newjobs:
    #     print(job.jet.id, job.idx, req.item, 'cost=('+','.join([f'{x:.2f}' for x in job.cost])+')')
    # print()
    return newjobs[0]

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
    
    res = job_info.jet.try_insert_job(job, job_info.idx)
    if res is None:
        raise RuntimeError('Do not call \'assign_job\' on un-tested jobs.')
    newsched, kicked = res

    for kjob in kicked:
        kjob.start = None

    job_info.jet.sched.clear_jobs()
    for njob in newsched.jobs:
        njob.start = job_info.jet.sched.last_job_end
        job_info.jet.sched.add_job(njob)

def make_schedule(demand: Demand, inv: Inventory, jets: list[Jet]) -> None:
    for i in range(1,5):
        for key in demand.fullkeys():
            reqview = demand[key]
            req = demand.remove(reqview)
            bucket = req.bucket(i)

            while bucket.total_yds >= 200:
                best_job = get_best_job(req, i, jets, inv, demand)
                if best_job is None:
                    break
                assign_job(best_job, req, i, inv)
            
            demand.add(req)

def make_job(req: Req, pnum: int, yds: float) -> Job:
    lbs = yds / req.item.yld
    aroll = AllocRoll('some_roll', req.greige, lbs)
    dlot = req.assign_lot([aroll], pnum)
    last_date = req.bucket(4).date + dt.timedelta(days=1)
    newjob = Job.make_job(last_date, (dlot,))
    return newjob

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