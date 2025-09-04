#!/usr/bin/env python

from typing import TypedDict, Literal
import re, datetime as dt, pandas as pd

from app.support.logging import Logger
from app.materials import Inventory, Snapshot, RollAlloc, PortLoad
from app.schedule import DyeLot, Demand, Jet, Job

def add_back_piece(inv: Inventory, piece: RollAlloc, snapshot: Snapshot) -> None:
    roll = inv.remove(inv.get(piece.roll_id), remkey=True)
    roll.deallocate(piece, snapshot=snapshot)
    inv.add(roll)

def apply_snapshot(inv: Inventory, snap: Snapshot | None, temp: bool = True) -> None:
    views = list(inv.itervalues())
    for rview in views:
        roll = inv.remove(rview)
        if temp:
            roll.snapshot = snap
        else:
            roll.apply_snap(snap)
        inv.add(roll)

class InvTable(TypedDict):
    greige: list[str]
    lbs: list[float]
    avail_date: list[dt.datetime]

class OrderTable(TypedDict):
    item: list[str]
    greige: list[str]
    pnum: list[int]
    due_date: list[dt.datetime]
    yds: list[float]
    lbs: list[float]

type JobsCol = Literal['jet', 'start', 'end', 'greige', 'color', 'lbs']

class JobsTable(TypedDict):
    jet: list[str]
    start: list[dt.datetime]
    end: list[dt.datetime]
    greige: list[str]
    color: list[str]
    lbs: list[float]

    @classmethod
    def get_col_info(cls, col: JobsCol, jet: Jet, job: Job):
        match col:
            case 'jet': return jet.id
            case 'start': return job.start
            case 'end': return job.end
            case 'greige': return job.greige.id
            case 'color': return job.color.name
            case 'lbs': return sum(map(lambda l: l.lbs, job.lots))

type LotsCol = Literal['jet', 'job', 'item', 'start', 'end', 'min_date', 'greige',
                       'color', 'lbs', 'yds']

class LotsTable(TypedDict):
    jet: list[str]
    job: list[str]
    item: list[str]
    start: list[dt.datetime]
    end: list[dt.datetime]
    min_date: list[dt.datetime]
    greige: list[str]
    color: list[str]
    lbs: list[float]
    yds: list[float]

    @classmethod
    def get_col_info(cls, col: LotsCol, jet: Jet, job: Job, lot: DyeLot):
        match col:
            case 'jet': return jet.id
            case 'job': return job.id
            case 'item': return lot.item.id
            case 'start': return job.start
            case 'end': return job.end
            case 'min_date': return lot.min_date
            case 'greige': return job.greige.id
            case 'color': return job.color.name
            case 'lbs': return lot.lbs
            case 'yds': return lot.yds

type RollsCol = Literal['jet', 'job', 'lot', 'greige', 'roll1', 'lbs1', 'roll2',
                        'lbs2', 'avail_date', 'start', 'item', 'color']

class RollsTable(TypedDict):
    jet: list[str]
    job: list[str]
    lot: list[str]
    greige: list[str]
    roll1: list[str]
    lbs1: list[float]
    roll2: list[str]
    lbs2: list[float]
    avail_date: list[dt.datetime]
    start: list[dt.datetime]
    item: list[str]
    color: list[str]

    @classmethod
    def get_col_info(cls, col: RollsCol, jet: Jet, job: Job, lot: DyeLot, pl: PortLoad):
        match col:
            case 'jet': return jet.id
            case 'job': return job.id
            case 'lot': return lot.id
            case 'greige': return job.greige.id
            case 'roll1': return pl.roll1.roll_id
            case 'lbs1': return pl.roll1.lbs
            case 'roll2':
                if pl.roll2:
                    return pl.roll2.roll_id
                return 'N/A'
            case 'lbs2':
                if pl.roll2:
                    return pl.roll2.lbs
                return 0
            case 'avail_date': return pl.avail_date
            case 'start': return job.start
            case 'item': return lot.item.id
            case 'color': return lot.color.name

class NewInvTable(TypedDict):
    greige: list[str]
    lbs: list[float]
    avail_date: list[dt.datetime]

class LateTable(TypedDict):
    item: list[str]
    due_date: list[dt.datetime]
    ordered_yds: list[float]
    late_yds: list[float]
    days_late: list[float]

class LateTableDetail(TypedDict):
    order: list[str]
    item: list[str]
    due_date: list[dt.datetime]
    ordered_yds: list[float]
    late_yds: list[float]
    cum_late_yds: list[float]
    days_late: list[float]

class MissingTable(TypedDict):
    item: list[str]
    greige: list[str]
    due_date: list[dt.datetime]
    ordered_yds: list[float]
    yds_not_scheduled: list[float]
    lbs_not_scheduled: list[float]

class LogsTable(TypedDict):
    caller: list[int]
    name: list[str]
    desc1: list[str]
    desc2: list[str]
    desc3: list[str]

def df_cols_to_string(df: pd.DataFrame, *args: *tuple[str, ...]) -> pd.DataFrame:
    for col in args:
        df[col] = df[col].astype('string')
    return df

type InvData = tuple[list[str], InvTable]
type OrderData = tuple[list[str], OrderTable]

def get_init_tables(inv: Inventory, dmnd: Demand) -> tuple[InvData, OrderData]:
    roll_ids: list[str] = []
    inv_table = InvTable(greige=[], lbs=[], avail_date=[])

    order_ids: list[str] = []
    order_table = OrderTable(item=[], greige=[], pnum=[], due_date=[], yds=[], lbs=[])

    for rview in inv.itervalues():
        roll_ids.append(rview.id)
        inv_table['greige'].append(rview.item.id)
        inv_table['lbs'].append(rview.lbs)
        inv_table['avail_date'].append(rview.avail_date)
    
    for order in dmnd.itervalues():
        order_ids.append(order.id)
        order_table['item'].append(order.item.id)
        order_table['greige'].append(order.item.greige.id)
        order_table['pnum'].append(order.pnum)
        order_table['due_date'].append(order.due_date)
        order_table['yds'].append(order.yds)
        order_table['lbs'].append(order.lbs)
    
    return (roll_ids, inv_table), (order_ids, order_table)

type JobsData = tuple[list[str], JobsTable]
type LotsData = tuple[list[str], LotsTable]

def get_sched_tables(jets: list[Jet]) -> tuple[JobsData, LotsData, RollsTable]:
    job_ids: list[str] = []
    jobs_table = JobsTable(jet=[], start=[], end=[], greige=[], color=[], lbs=[])

    lot_ids: list[str] = []
    lots_table = LotsTable(jet=[], job=[], item=[], start=[], end=[], min_date=[],
                           greige=[], color=[], lbs=[], yds=[])
    
    rolls_table = RollsTable(jet=[], job=[], lot=[], greige=[], roll1=[], lbs1=[], roll2=[],
                             lbs2=[], avail_date=[], start=[], item=[], color=[])
    
    for jet in jets:
        for job in jet.jobs:
            job_ids.append(job.id)
            for job_col in ('jet', 'start', 'end', 'greige', 'color', 'lbs'):
                jobs_table[job_col].append(JobsTable.get_col_info(job_col, jet, job))
            
            for lot in job.lots:
                lot_ids.append(lot.id)
                for lot_col in ('jet', 'job', 'item', 'start', 'end', 'min_date', 'greige',
                                'color', 'lbs', 'yds'):
                    lots_table[lot_col].append(LotsTable.get_col_info(lot_col, jet, job, lot))
                
                for port in lot.ports:
                    for roll_col in ('jet', 'job', 'lot', 'greige', 'roll1', 'lbs1',
                                     'roll2', 'lbs2', 'avail_date', 'start', 'item',
                                     'color'):
                        cur_info = RollsTable.get_col_info(roll_col, jet, job, lot, port)
                        rolls_table[roll_col].append(cur_info)
    
    return (job_ids, jobs_table), (lot_ids, lots_table), rolls_table

type NewInvData = tuple[list[str], NewInvTable]

def get_new_inv(inv: Inventory) -> NewInvData:
    roll_ids: list[str] = []
    inv_table = NewInvTable(greige=[], lbs=[], avail_date=[])

    for rview in inv.itervalues():
        if 'NEW' not in rview.id: continue

        roll_ids.append(rview.id)
        inv_table['greige'].append(rview.item.id)
        inv_table['lbs'].append(rview.init_wt)
        inv_table['avail_date'].append(rview.avail_date)
    
    return roll_ids, inv_table

type LateData = tuple[list[str], LateTable]
type LateDetailData = tuple[list[str], LateTableDetail]
type MissingData = tuple[list[str], MissingTable]

def get_late_tables(dmnd: Demand) -> tuple[LateData, LateDetailData, MissingData]:
    late_ids: list[str] = []
    late_detail = LateTableDetail(order=[], item=[], due_date=[], ordered_yds=[], late_yds=[],
                                  cum_late_yds=[], days_late=[])
    
    order_ids: list[str] = []
    late_table = LateTable(item=[], due_date=[], ordered_yds=[], late_yds=[], days_late=[])

    miss_ids: list[str] = []
    miss_table = MissingTable(item=[], greige=[], due_date=[], ordered_yds=[], yds_not_scheduled=[],
                              lbs_not_scheduled=[])

    for order in dmnd.itervalues():
        if order.yds > 0 and order.total_yds <= 0:
            cur_fri = order.due_date + dt.timedelta(days=4 - order.due_date.weekday())
            next_fri = cur_fri + dt.timedelta(weeks=2)
            late_pairs = sorted(order.late_table(next_fri), key=lambda x: x[1])
            total_yds = 0

            order_ids.append(order.id)
            late_table['item'].append(order.item.id)
            late_table['due_date'].append(order.due_date)
            late_table['ordered_yds'].append(order.init_yds)
            late_table['late_yds'].append(order.yds)
            late_table['days_late'].append(late_pairs[-1][1].total_seconds() / (3600*24))
            
            for i, pair in enumerate(late_pairs):
                late_ids.append(order.id+f'@{i}')
                late_detail['order'].append(order.id)
                late_detail['item'].append(order.item.id)
                late_detail['due_date'].append(order.due_date)
                late_detail['ordered_yds'].append(order.init_yds)

                late_yds, late_delta = pair
                total_yds += late_yds
                late_detail['late_yds'].append(late_yds)
                late_detail['cum_late_yds'].append(total_yds)
                late_detail['days_late'].append(late_delta.total_seconds() / (3600 * 24))
        elif order.total_yds > 0:
            miss_ids.append(order.id)

            miss_table['item'].append(order.item.id)
            miss_table['greige'].append(order.item.greige.id)
            miss_table['due_date'].append(order.due_date)
            miss_table['ordered_yds'].append(order.init_yds)
            rem_yds = min(order.total_yds, order.init_yds)
            rem_lbs = min(order.total_lbs, order.init_lbs)
            miss_table['yds_not_scheduled'].append(rem_yds)
            miss_table['lbs_not_scheduled'].append(rem_lbs)
    
    return (order_ids, late_table), (late_ids, late_detail), (miss_ids, miss_table)

def get_logs_table(lgr: Logger) -> list[tuple[str, list[int], LogsTable]]:
    tables: list[tuple[str, list[int], LogsTable]] = []

    cur_pnum = 1
    cur_date = None
    date_idx = 0
    cur_ids: list[int] = []
    cur_table = LogsTable(caller=[], name=[], desc1=[], desc2=[], desc3=[])

    for process in sorted(lgr.processes, key=lambda p: p.id):
        if process.name == 'schedule_order':
            x: re.Match = re.match(r'.*Order\(id=(.*)\)', process.desc1)
            order_id: str = x.group(1)
            prefix = order_id[1:3]
            pnum = int(prefix[1:])

            x: re.Match = re.match(r'.*=(.*)', process.desc2)
            day: str = x.group(1)
            
            if pnum > cur_pnum or pnum >= 5 and day != cur_date:
                if cur_pnum >= 5:
                    fname = f'p{cur_pnum}_logs_{date_idx}.tsv'
                    date_idx += 1
                    if pnum > cur_pnum:
                        date_idx = 0
                else:
                    fname = f'p{cur_pnum}_logs.tsv'

                tables.append((fname, cur_ids, cur_table))
                cur_ids: list[int] = []
                cur_table = LogsTable(caller=[], name=[], desc1=[], desc2=[],
                                      desc3=[])
                cur_pnum = pnum
                cur_date = day

        cur_ids.append(process.id)
        cur_table['caller'].append(process.caller)
        cur_table['name'].append(process.name)
        cur_table['desc1'].append(process.desc1)
        cur_table['desc2'].append(process.desc2)
        cur_table['desc3'].append(process.desc3)
    
    if cur_pnum >= 5:
        fname = f'p{cur_pnum}_logs_{date_idx}.tsv'
    else:
        fname = f'p{cur_pnum}_logs.tsv'
    tables.append((fname, cur_ids, cur_table))
    
    return tables