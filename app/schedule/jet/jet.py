#!/usr/bin/env python

from typing import Callable
import datetime as dt

from app.support import HasID, SuperImmut, FloatRange, DateRange
from app.style.color import STRIP, HEAVYSTRIP
from ..req import ReqView
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
                            date_rng=DateRange(min_date, max_date), sched=JetSched(min_date, max_date, 0))
        
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
        curjobs = self.jobs
        finish_time = dt.timedelta(hours=16)

        for i in range(len(curjobs), 0, -1):
            if curjobs[i-1].end + job.cycle_time + finish_time <= job.due_date \
                and curjobs[i-1].shade <= job.shade:
                return i

        return 0
    
    def try_insert_job(self, job: Job, idx: int) -> tuple[JetSched, list[Job]] | None:
        curjobs = self.jobs
        cursched: JetSched = self.sched
        newsched = JetSched(cursched.date_rng.minval, cursched.date_rng.maxval)
        kicked: list[Job] = []

        for i in range(idx):
            if newsched.rem_time < curjobs[i].cycle_time:
                kicked.append(curjobs[i])
            curjobs[i].start = newsched.last_job_end
            newsched.add_job(curjobs[i])
        
        fits = newsched.check_for_strip(job)
        if not fits:
            cursched.set_times()
            return None
        
        job.start = newsched.last_job_end
        newsched.add_job(job)
        
        for j in curjobs[idx:]:
            if j.shade in (STRIP, HEAVYSTRIP):
                continue
            if not fits:
                kicked.append(j)
            
            fits = newsched.check_for_strip(j)
            if fits:
                j.start = newsched.last_job_end
                newsched.add_job(j)
            else:
                kicked.append(j)
        
        return newsched, kicked

    def get_sched_cost(self, newsched: JetSched, kicked: list[Job],
                       cost_func: Callable[[JetSched, 'Jet', set[ReqView]], float]) -> float:
        all_reqs: set[ReqView] = set()

        for job in newsched.jobs:
            for lot in job.lots:
                all_reqs.add(lot.req)
        
        for job in kicked:
            for lot in job.lots:
                all_reqs.add(lot.req)

        cursched: JetSched = self.sched
        cursched.set_times()
        curcost = cost_func(cursched, self, all_reqs)
        newsched.set_times()
        newcost = cost_func(newsched, self, all_reqs)
        cursched.set_times()

        return newcost - curcost
    
    def get_all_options(self, job: Job,
                        cost_func: Callable[[JetSched, 'Jet', set[ReqView]], float]) -> \
                        list[tuple[int, float]]:
        idx = self.get_start_idx(job)
        costs: list[tuple[int, float]] = []

        for i in range(idx, len(self.jobs)+1):
            res = self.try_insert_job(job, i)
            if not res: continue
            newsched, kicked = res
            cost = self.get_sched_cost(newsched, kicked, cost_func)
            costs.append((i, cost))
        
        return costs