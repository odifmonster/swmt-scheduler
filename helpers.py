#!/usr/bin/env python

from typing import TypedDict, Literal
import datetime as dt, pandas as pd

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

class OrderTable(TypedDict):
    item: list[str]
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

type LotsCol = Literal['jet', 'job', 'item', 'start', 'end', 'greige', 'color', 'lbs',
                       'yds']

class LotsTable(TypedDict):
    jet: list[str]
    job: list[str]
    item: list[str]
    start: list[dt.datetime]
    end: list[dt.datetime]
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
            case 'greige': return job.greige.id
            case 'color': return job.color.name
            case 'lbs': return lot.lbs
            case 'yds': return lot.yds

type RollsCol = Literal['jet', 'job', 'lot', 'greige', 'roll1', 'lbs1', 'roll2',
                        'lbs2', 'start', 'item', 'color']

class RollsTable(TypedDict):
    jet: list[str]
    job: list[str]
    lot: list[str]
    greige: list[str]
    roll1: list[str]
    lbs1: list[float]
    roll2: list[str]
    lbs2: list[float]
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
            case 'start': return job.start
            case 'item': return lot.item.id
            case 'color': return lot.color.name

class LateTable(TypedDict):
    item: list[str]
    due_date: list[dt.datetime]
    ordered_yds: list[float]
    late_yds: list[float]
    days_late: list[float]

class MissingTable(TypedDict):
    item: list[str]
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

type InvData = tuple[list[str], InvTable]
type OrderData = tuple[list[str], OrderTable]

def get_init_tables(inv: Inventory, dmnd: Demand) -> tuple[InvData, OrderData]:
    roll_ids: list[str] = []
    inv_table = InvTable(greige=[], lbs=[])

    order_ids: list[str] = []
    order_table = OrderTable(item=[], pnum=[], due_date=[], yds=[], lbs=[])

    for rview in inv.itervalues():
        roll_ids.append(rview.id)
        inv_table['greige'].append(rview.item.id)
        inv_table['lbs'].append(rview.lbs)
    
    for order in dmnd.itervalues():
        order_ids.append(order.id)
        order_table['item'].append(order.item.id)
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
    lots_table = LotsTable(jet=[], job=[], item=[], start=[], end=[], greige=[], color=[],
                           lbs=[], yds=[])
    
    rolls_table = RollsTable(jet=[], job=[], lot=[], greige=[], roll1=[], lbs1=[], roll2=[],
                             lbs2=[], start=[], item=[], color=[])
    
    for jet in jets:
        for job in jet.jobs:
            job_ids.append(job.id)
            for job_col in ('jet', 'start', 'end', 'greige', 'color', 'lbs'):
                jobs_table[job_col].append(JobsTable.get_col_info(job_col, jet, job))
            
            for lot in job.lots:
                lot_ids.append(lot.id)
                for lot_col in ('jet', 'job', 'item', 'start', 'end', 'greige', 'color',
                                'lbs', 'yds'):
                    lots_table[lot_col].append(LotsTable.get_col_info(lot_col, jet, job, lot))
                
                for port in lot.ports:
                    for roll_col in ('jet', 'job', 'lot', 'greige', 'roll1', 'lbs1',
                                     'roll2', 'lbs2', 'start', 'item', 'color'):
                        cur_info = RollsTable.get_col_info(roll_col, jet, job, lot, port)
                        rolls_table[roll_col].append(cur_info)
    
    return (job_ids, jobs_table), (lot_ids, lots_table), rolls_table

type LateData = tuple[list[str], LateTable]
type MissingData = tuple[list[str], MissingTable]

def get_late_tables(dmnd: Demand) -> tuple[LateData, MissingData]:
    late_ids: list[str] = []
    late_table = LateTable(item=[], due_date=[], ordered_yds=[], late_yds=[], days_late=[])

    miss_ids: list[str] = []
    miss_table = MissingTable(item=[], due_date=[], ordered_yds=[], yds_not_scheduled=[],
                              lbs_not_scheduled=[])

    for order in dmnd.itervalues():
        if order.yds > 0 and order.total_yds <= 0:
            late_ids.append(order.id)
            late_table['item'].append(order.item.id)
            late_table['due_date'].append(order.due_date)
            late_table['ordered_yds'].append(order.init_yds)
            late_table['late_yds'].append(order.yds)

            late_pairs = order.late_table()
            late_delta = late_pairs[0][1]
            late_table['days_late'].append(late_delta.total_seconds() / (3600 * 24))
        elif order.total_yds > 0:
            miss_ids.append(order.id)

            miss_table['item'].append(order.item.id)
            miss_table['due_date'].append(order.due_date)
            miss_table['ordered_yds'].append(order.init_yds)
            rem_yds = min(order.total_yds, order.init_yds)
            rem_lbs = min(order.total_lbs, order.init_lbs)
            miss_table['yds_not_scheduled'].append(rem_yds)
            miss_table['lbs_not_scheduled'].append(rem_lbs)
    
    return (late_ids, late_table), (miss_ids, miss_table)

def get_logs_table(lgr: Logger) -> tuple[list[int], LogsTable]:
    proc_ids: list[int] = []
    logs_table = LogsTable(caller=[], name=[], desc1=[], desc2=[], desc3=[])

    for process in sorted(lgr.processes, key=lambda p: p.id):
        proc_ids.append(process.id)
        logs_table['caller'].append(process.caller)
        logs_table['name'].append(process.name)
        logs_table['desc1'].append(process.desc1)
        logs_table['desc2'].append(process.desc2)
        logs_table['desc3'].append(process.desc3)
    
    return proc_ids, logs_table

def df_cols_to_string(df: pd.DataFrame, *args: *tuple[str, ...]) -> pd.DataFrame:
    for col in args:
        df[col] = df[col].astype('string')
    return df