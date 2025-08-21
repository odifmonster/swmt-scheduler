#!/usr/bin/env python

from typing import TypedDict
import datetime as dt

from app.style.color import EMPTY, STRIP, HEAVYSTRIP
from app.schedule import Jet, Demand

class JobsData(TypedDict):
    jet: list[str]
    start: list[dt.datetime]
    end: list[dt.datetime]
    item: list[str]
    greige: list[str]
    color: list[str]
    lbs: list[float]
    yds: list[float]

class RollsData(TypedDict):
    job_id: list[str]
    jet: list[str]
    greige: list[str]
    roll1: list[str]
    lbs1: list[float]
    roll2: list[str]
    lbs2: list[float]
    lbs: list[float]
    start: list[dt.datetime]
    item: list[str]
    color: list[str]

class MissingData(TypedDict):
    item: list[str]
    priority: list[int]
    due_date: list[dt.datetime]
    missing_yds: list[float]
    missing_lbs: list[float]
    scheduled: list[str]

def get_jobs_data(jets: list[Jet]) -> tuple[list[str], JobsData]:
    data: JobsData = JobsData(jet=[], start=[], end=[], item=[], greige=[],
                              color=[], lbs=[], yds=[])
    ids: list[str] = []
    
    for jet in jets:
        for job in jet.jobs:
            ids.append(job.id)
            data['jet'].append(jet.id)
            data['start'].append(job.start)
            data['end'].append(job.end)
            if job.shade in (EMPTY, STRIP, HEAVYSTRIP):
                if job.shade == EMPTY:
                    data['item'].append('')
                    data['greige'].append('')
                    data['color'].append('')
                else:
                    data['item'].append('N/A')
                    data['greige'].append('N/A')
                    data['color'].append('N/A')
            else:
                lot = job.lots[0]
                data['item'].append(lot.item.id)
                data['greige'].append(lot.item.greige.id)
                data['color'].append(lot.color.name)

            data['lbs'].append(job.lbs)
            data['yds'].append(job.yds)
    
    return ids, data

def get_rolls_data(jets: list[Jet]) -> tuple[list[str], RollsData]:
    data: RollsData = RollsData(job_id=[], jet=[], greige=[], roll1=[], lbs1=[],
                                roll2=[], lbs2=[], lbs=[], start=[], item=[],
                                color=[])
    ids: list[str] = []

    for jet in jets:
        for job in jet.jobs:
            for lot in job.lots:
                for aroll in lot.rolls:
                    ids.append(f'{aroll.id:06}')
                    data['job_id'].append(job.id)
                    data['jet'].append(jet.id)
                    data['greige'].append(aroll.greige.id)
                    data['roll1'].append(aroll.rolls[0].id)
                    data['lbs1'].append(aroll.rolls[0].lbs)

                    if len(aroll.rolls) == 2:
                        data['roll2'].append(aroll.rolls[1].id)
                        data['lbs2'].append(aroll.rolls[1].lbs)
                    else:
                        data['roll2'].append('')
                        data['lbs2'].append(0)
                    
                    data['lbs'].append(aroll.lbs)
                    data['start'].append(job.start)
                    data['item'].append(lot.item.id)
                    data['color'].append(lot.item.color.name)
    
    return ids, data

def get_missing_data(dmnd: Demand) -> MissingData:
    data: MissingData = MissingData(item=[], priority=[], due_date=[], missing_yds=[], missing_lbs=[],
                                    scheduled=[])
    
    for pnum in range(1, 5):
        for key in dmnd.fullkeys():
            rview = dmnd[key]
            rbucket = rview.bucket(pnum)

            if rbucket.yds > 0:
                data['item'].append(rview.item.id)
                data['priority'].append(pnum)
                data['due_date'].append(rbucket.date)
                data['missing_yds'].append(rbucket.yds)
                data['missing_lbs'].append(rbucket.lbs)
                if rbucket.total_yds <= 0:
                    data['scheduled'].append('TRUE')
                else:
                    data['scheduled'].append('FALSE')
    
    return data