#!/usr/bin/env python

import datetime as dt

from app.support import HasID, SuperImmut, FloatRange, DateRange
from app.style.color import STRIP, HEAVYSTRIP
from ..job import Job
from .jetsched import JetSched

class Jet(HasID[str], SuperImmut,
          attrs=('_prefix','id','n_ports','load_rng','date_rng','jobs','sched'),
          priv_attrs=('prefix','id'),
          frozen=('_Jet__prefix','_Jet__id','n_ports','load_rng','date_rng','sched')):
    
    def __init__(self, id: str, n_ports: int, load_min: float, load_max: float, min_date: dt.datetime,
                 max_date: dt.datetime):
        priv = {
            'prefix': 'Jet', 'id': id
        }
        SuperImmut.__init__(self, priv=priv, n_ports=n_ports, load_rng=FloatRange(load_min, load_max),
                            date_rng=DateRange(min_date, max_date), sched=JetSched(min_date, max_date))
        
    @property
    def _prefix(self) -> str:
        return self.__prefix
    
    @property
    def id(self) -> str:
        return self.__id
    
    @property
    def jobs(self) -> list[Job]:
        return self.sched.jobs
    
    def get_start_idx(self, job: Job):
        for i, j in enumerate(self.jobs):
            job.start = j.start
            if job.end + dt.timedelta(hours=16) > job.due_date:
                return max(0, i-1)
            if j.shade in (STRIP, HEAVYSTRIP): continue
            if j.shade < job.shade:
                return max(0, i-1)
        return len(self.jobs)
    
    def insert_job(self, job: Job, idx: int) -> tuple[JetSched, list[Job]]:
        newjobs = self.jobs
        newjobs.insert(idx, job)

        cursched: JetSched = self.sched
        newsched = JetSched(cursched.date_rng.minval, cursched.date_rng.maxval)
        kicked: list[Job] = []

        for job in newjobs:
            if newsched.rem_time < job.cycle_time:
                kicked.append(job)
            else:
                job.start = newsched.last_job_end
                newsched.add_job(job)
        
        return newsched, kicked