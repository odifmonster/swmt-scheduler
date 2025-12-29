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

def _max_color(clr1, clr2):
    if color.BLACK in (clr1, clr2):
        return color.BLACK
    if color.SOLUTION in (clr1, clr2):
        return color.SOLUTION
    if color.MEDIUM in (clr1, clr2):
        return color.MEDIUM
    if color.LIGHT in (clr1, clr2):
        return color.LIGHT
    if color.LIGHT0 in (clr1, clr2):
        return color.LIGHT0
    return color.EMPTY

class JetSched(HasID[int], SuperImmut,
               attrs=('_prefix','id','soil_level','jobs_since_strip','clr_since_strip',
                      'rem_time','last_job_end','jobs'),
               priv_attrs=('id','init_sched','soil','jss','date_rng','jobs',
                           'max_ss'),
               frozen=('*id','*init_sched','*date_rng')):
    
    def __init__(self, date_rng: DateRange, prev_sched = None):
        init_soil, init_jobs, init_clr = 0, 0, color.EMPTY
        if prev_sched:
            init_soil = prev_sched.soil_level
            init_jobs = prev_sched.jobs_since_strip
            init_clr = prev_sched.clr_since_strip

        globals()['_CTR'] += 1
        SuperImmut.__init__(self, priv={'id': globals()['_CTR'], 'init_sched': prev_sched,
                                        'soil': init_soil, 'jss': init_jobs,
                                        'date_rng': date_rng, 'jobs': [],
                                        'max_ss': init_clr})
    
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
    def clr_since_strip(self):
        return self.__max_ss
    
    @property
    def last_job_end(self):
        lje: dt.datetime = dt.datetime.fromtimestamp(0)
        if not self.__jobs:
            lje = self.__date_rng.minval
        else:
            lje = max(self.__date_rng.minval, self.__jobs[-1].end)

        last_mon = lje - dt.timedelta(days=lje.weekday())
        if (lje.weekday() > 4 and (lje.weekday() > 5 or lje.hour >= 20)) or \
            (last_mon.date() == dt.date(2025, 12, 22) and lje.weekday() > 2):
            return _first_monday_after(lje)
        return lje
    
    @property
    def rem_time(self):
        lje = self.last_job_end
        rem_rng = DateRange(lje, self.__date_rng.maxval)
        first_mon = _first_monday_after(lje)
        wknd_hrs = 24
        if first_mon.date() == dt.date(2025, 12, 29):
            wknd_hrs = 96
        cur_wknd = DateRange(first_mon - dt.timedelta(hours=wknd_hrs), first_mon)
        rem_t = rem_rng.maxval - lje

        while rem_rng.overlaps(cur_wknd):
            rem_t -= dt.timedelta(hours=24)
            if cur_wknd.minval < rem_rng.minval:
                rem_t += (rem_rng.minval - cur_wknd.minval)
            if cur_wknd.maxval > rem_rng.maxval:
                rem_t += (cur_wknd.maxval - rem_rng.maxval)
            
            first_mon += dt.timedelta(days=7)
            wknd_hrs = 24
            if first_mon.date() == dt.date(2025, 12, 29):
                wknd_hrs = 96
            cur_wknd = DateRange(first_mon - dt.timedelta(hours=wknd_hrs),
                                 first_mon)
        
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
        strip = None
        if item.color.shade in (color.LIGHT, color.LIGHT0):
            if self.__max_ss in (color.MEDIUM, color.SOLUTION):
                strip = fabric.get_style('STRIP')
            elif self.__max_ss == color.BLACK:
                strip = fabric.get_style('HEAVYSTRIP')
        if item.color.shade == color.MEDIUM:
            if self.__max_ss == color.SOLUTION:
                strip = fabric.get_style('STRIP')
            elif self.__max_ss == color.BLACK:
                strip = fabric.get_style('HEAVYSTRIP')

        if strip is None and self.jobs_since_strip >= 9:
            strip = fabric.get_style('STRIP')
        
        return strip
    
    def get_cycle_end(self, start: dt.datetime, item: fabric.FabricStyle):
        end = start + item.cycle_time
        wkday = end.weekday()
        cur_mon = end - dt.timedelta(days=wkday)
        if (wkday > 4 and wkday > 5 or end.hour >= 20) or \
            cur_mon.date() == dt.date(2025, 12, 22) and wkday > 2:
            end = _first_monday_after(end)
        return end
    
    def get_expected_end(self, lots: tuple[DyeLot, ...]):
        start = self.last_job_end
        strip = self.get_needed_strip(lots[0].item)
        if strip is not None:
            start = self.get_cycle_end(start, strip)
        return self.get_cycle_end(start, lots[0].item)
    
    def can_add(self, lots: tuple[DyeLot, ...]):
        total_cycle = lots[0].cycle_time - dt.timedelta(hours=4)
        strip = self.get_needed_strip(lots[0].item)

        if not strip is None:
            if lots[0].shade == color.LIGHT0:
                return False
            total_cycle += strip.cycle_time

        if self.jobs_since_strip == 0 and lots[0].shade == color.LIGHT0:
            return False
        
        min_date = max(map(lambda l: l.min_date, lots))
        moveable = all(map(lambda l: l.moveable, lots))
        min_mon = min_date - dt.timedelta(days=min_date.weekday())
        if moveable and (min_date.weekday() > 5 \
            or min_mon.date() == dt.date(2025, 12, 22) and min_date.weekday() > 2):
            min_date = _first_monday_after(min_date)
        if not moveable:
            new_start = min_date
        else:
            new_start = max(min_date, self.last_job_end)
        
        if self.last_job_end - dt.timedelta(minutes=1) > new_start:
            return False
        
        diff = new_start - self.last_job_end
        return total_cycle + diff <= self.rem_time
    
    def add_job(self, job: Job, force = False):
        if not force and job.start + dt.timedelta(minutes=1) < self.last_job_end:
            print(force)
            new_start = job.start.strftime('%m/%d %H:%M')
            cur_end = self.last_job_end.strftime('%m/%d %H:%M')
            raise ValueError(f'Cannot add job with start time {new_start} to schedule with last job ending at {cur_end}')
        
        self.__jobs.append(job)
        if job.shade in (color.STRIP, color.HEAVYSTRIP):
            self.__jss = 0
            self.__max_ss = job.shade
        else:
            self.__max_ss = _max_color(job.shade, self.__max_ss)
            self.__jss += 1

        self.__soil += job.color.soil
        self.__soil = max(self.__soil, 0)

    def add_lots(self, lots: tuple[DyeLot, ...], idx: int):
        strip = self.get_needed_strip(lots[0].item)
        if not strip is None:
            strip_job = Job([DyeLot.new_strip(strip, self.last_job_end)], self.last_job_end)
            self.add_job(strip_job)
        min_date = max(map(lambda l: l.min_date, lots))
        moveable = all(map(lambda l: l.moveable, lots))
        force = False
        min_mon = min_date - dt.timedelta(days=min_date.weekday())
        if min_date.weekday() > 5 or \
            min_mon.date() == dt.date(2025, 12, 22) and min_date.weekday() > 2:
            min_date = _first_monday_after(min_date)
        if not moveable:
            force = True
            new_start = min_date
        else:
            new_start = max(min_date, self.last_job_end)
        new_job = Job(lots, new_start, idx=idx)
        self.add_job(new_job, force=force)
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