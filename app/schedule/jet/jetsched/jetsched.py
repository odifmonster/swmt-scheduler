#!/usr/bin/env python

from typing import Callable
import datetime as dt

from app.support import HasID, SuperImmut, DateRange
from app.style import fabric, color, GreigeStyle
from ..job import Job
from ...dyelot import DyeLot

_CTR = 0

def _first_monday_after(date: dt.datetime):
    days_to_mon = 7 - date.weekday()
    monday = date + dt.timedelta(days=days_to_mon)
    return dt.datetime(year=monday.year, month=monday.month, day=monday.day)

class JetSched(HasID[int], SuperImmut,
               attrs=('_prefix','id','soil_level','jobs_since_strip','rem_time',
                      'last_job_end','jobs'),
               priv_attrs=('id','init_sched','soil','jss','date_rng','jobs'),
               frozen=('*id','*init_sched','*date_rng')):
    
    def __init__(self, date_rng: DateRange, prev_sched = None):
        init_soil, init_jobs = 0, 0
        if prev_sched:
            init_soil = prev_sched.soil_level
            init_jobs = prev_sched.jobs_since_strip

        globals()['_CTR'] += 1
        SuperImmut.__init__(self, priv={'id': globals()['_CTR'], 'init_sched': prev_sched,
                                        'soil': init_soil, 'jss': init_jobs,
                                        'date_rng': date_rng, 'jobs': []})
    
    @property
    def _prefix(self):
        return 'JetSched'
    
    @property
    def id(self):
        return self.__id
    
    @property
    def soil_level(self):
        return self.__soil
    
    @property
    def jobs_since_strip(self):
        return self.__jss
    
    @property
    def last_job_end(self):
        lje: dt.datetime = dt.datetime.fromtimestamp(0)
        if not self.__jobs:
            lje = self.__date_rng.minval
        else:
            lje = self.__jobs[-1].end

        if lje.weekday() > 4 and (lje.weekday() == 6 or lje.hour >= 20):
            return _first_monday_after(lje)
        return lje
    
    @property
    def rem_time(self):
        lje = self.last_job_end
        rem_rng = DateRange(lje, self.__date_rng.maxval)
        first_mon = _first_monday_after(lje)
        cur_wknd = DateRange(first_mon - dt.timedelta(hours=24), first_mon)
        rem_t = rem_rng.maxval - lje

        while rem_rng.overlaps(cur_wknd):
            rem_t -= dt.timedelta(hours=24)
            if cur_wknd.minval < rem_rng.minval:
                rem_t += (rem_rng.minval - cur_wknd.minval)
            if cur_wknd.maxval > rem_rng.maxval:
                rem_t += (cur_wknd.maxval - rem_rng.maxval)
            
            cur_wknd = DateRange(cur_wknd.minval + dt.timedelta(days=7),
                                 cur_wknd.maxval + dt.timedelta(days=7))
        
        return rem_t
    
    @property
    def jobs(self) -> tuple[Job, ...]:
        filt_func: Callable[[Job], bool] = \
            lambda j: j.color.shade not in (color.STRIP, color.HEAVYSTRIP)
        return tuple(filter(filt_func, self.__jobs))
    
    @property
    def full_sched(self) -> tuple[Job, ...]:
        return tuple(self.__jobs)
    
    def copy(self):
        return JetSched(self.__date_rng, prev_sched=self.__init_sched)
    
    def get_needed_strip(self, item: fabric.FabricStyle):
        strip_id = item.get_strip(self.soil_level)
        strip = None if strip_id is None else fabric.get_style(strip_id)
        if strip is None and (self.jobs_since_strip >= 9 or \
            self.full_sched and item.color.shade == fabric.color.LIGHT and \
            self.full_sched[-1].color.shade == fabric.color.BLACK):
            strip = fabric.get_style('STRIP')
        
        return strip
    
    def can_add(self, lots: tuple[DyeLot, ...]):
        total_cycle = lots[0].cycle_time - dt.timedelta(hours=4)
        strip = self.get_needed_strip(lots[0].item)

        if not strip is None:
            total_cycle += strip.cycle_time
        
        return total_cycle <= self.rem_time
    
    def add_job(self, job: Job, force = False):
        if not force and job.start + dt.timedelta(minutes=1) < self.last_job_end:
            new_start = job.start.strftime('%m/%d %H:%M')
            cur_end = self.last_job_end.strftime('%m/%d %H:%M')
            raise ValueError(f'Cannot add job with start time {new_start} to schedule with last job ending at {cur_end}')
        
        self.__jobs.append(job)
        if job.shade in (color.STRIP, color.HEAVYSTRIP):
            self.__jss = 0
        else:
            self.__jss += 1

        self.__soil += job.color.soil
        self.__soil = max(self.__soil, 0)

    def add_lots(self, lots: tuple[DyeLot, ...], idx: int):
        strip = self.get_needed_strip(lots[0].item)
        if not strip is None:
            strip_job = Job([DyeLot.new_strip(strip, self.last_job_end)], self.last_job_end)
            self.add_job(strip_job)
        min_date = max(map(lambda l: l.min_date, lots))
        if min_date.weekday() == 6:
            min_date += dt.timedelta(days=1)
        new_job = Job(lots, max(min_date, self.last_job_end), idx=idx)
        self.add_job(new_job)
        return new_job
    
    def activate(self):
        for job in self.jobs:
            job.activate()
    
    def deactivate(self):
        for job in self.jobs:
            job.deactivate()

    def free_greige(self):
        avail: dict[GreigeStyle, list] = {}
        for job in self.jobs:
            for lot in job.lots:
                if not lot.start is None: continue
                
                if lot.greige not in avail:
                    avail[lot.greige] = []
                avail[lot.greige] += list(lot.ports)
        return avail