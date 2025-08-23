#!/usr/bin/env python

from typing import Callable
import datetime as dt

from app.support import HasID, SuperImmut, FloatRange, DateRange
from app.style.color import STRIP, HEAVYSTRIP
from ..req import Req, Demand
from ..job import Job
from .jetsched import JetSched

type CostFunc = Callable[['JetSched', 'Jet', Req, Demand], tuple[float, float]]

class Jet(HasID[str], SuperImmut,
          attrs=('_prefix','id','n_ports','load_rng','date_rng','jobs','new_jobs',
                 'sched'),
          priv_attrs=('prefix','id','init_sched'),
          frozen=('_Jet__prefix','_Jet__id','_Jet__init_sched','_logger','n_ports','load_rng',
                  'date_rng')):

    def __init__(self, id: str, n_ports: int, load_min: float, load_max: float, min_date: dt.datetime,
                 max_date: dt.datetime):
        priv = {
            'prefix': 'Jet', 'id': id, 'init_sched': JetSched(min_date, max_date)
        }
        SuperImmut.__init__(self, priv=priv, n_ports=n_ports, load_rng=FloatRange(load_min, load_max),
                            date_rng=DateRange(min_date, max_date), sched=None)

    @property
    def _prefix(self) -> str:
        return self.__prefix
    
    @property
    def id(self) -> str:
        return self.__id
    
    @property
    def jobs(self) -> list[Job]:
        if self.sched is None:
            return self.__init_sched.jobs
        return self.__init_sched.jobs + self.sched.jobs
    
    @property
    def new_jobs(self) -> list[Job]:
        if self.sched is None:
            return []
        return self.sched.jobs
    
    def add_placeholder(self, job: Job) -> None:
        self.__init_sched.add_job(job)
    
    def init_new_sched(self) -> None:
        self.sched = JetSched(max(self.__init_sched.last_job_end, self.date_rng.minval),
                              self.date_rng.maxval, soil_level=self.__init_sched.soil_level,
                              njobs=self.__init_sched.jobs_since_strip)
    
    def get_start_idx(self, job: Job):
        curjobs = self.new_jobs
        finish_time = dt.timedelta(hours=16)

        for i in range(len(curjobs), 0, -1):
            if curjobs[i-1].end + job.cycle_time + finish_time <= job.due_date \
                and curjobs[i-1].shade <= job.shade:
                return i

        return 0
    
    def try_insert_job(self, job: Job, idx: int) -> tuple[JetSched, list[Job], bool]:
        curjobs = self.new_jobs
        newsched = JetSched(self.sched.date_rng.minval, self.sched.date_rng.maxval,
                            soil_level=self.__init_sched.soil_level,
                            njobs=self.__init_sched.jobs_since_strip)
        kicked: list[Job] = []

        for i in range(idx):
            if newsched.rem_time < curjobs[i].cycle_time:
                kicked.append(curjobs[i])
            newsched.add_job(curjobs[i])
        
        strip, fits = newsched.check_for_strip(job)
        scheduled = fits
        
        if fits:
            if strip:
                newsched.add_job(strip)
            newsched.add_job(job)
        else:
            kicked.append(job)
        
        for j in curjobs[idx:]:
            if j.shade in (STRIP, HEAVYSTRIP):
                continue
            strip, fits = newsched.check_for_strip(j)
            if not fits:
                kicked.append(j)
            else:
                if strip:
                    newsched.add_job(strip)
                newsched.add_job(j)
        
        return newsched, kicked, scheduled

    def get_sched_cost(self, newjob: Job, newsched: JetSched, kicked: list[Job],
                       cur_req: Req, dmnd: Demand, cost_func: CostFunc) -> float:
        newsched.set_times()
        for kjob in kicked:
            kjob.start = None
        newcost = cost_func(newsched, self, cur_req, dmnd)
        newjob.start = None
        self.sched.set_times()

        late_cost, rem_cost = newcost
        return late_cost + 5 * rem_cost / len(newsched.jobs)
    
    def get_all_options(self, job: Job, cur_req: Req, dmnd: Demand, cost_func: CostFunc) -> \
        list[tuple[int, float]]:
        idx = self.get_start_idx(job)
        costs: list[tuple[int, float]] = []
        cur_req = job.lots[0].req

        for i in range(idx, len(self.new_jobs)+1):
            if cur_req.id == 'REQ FF MOLTO-NA-41256-64':
                print(f'Getting cost of inserting on {self.id} after {i} job(s)')
            newsched, kicked, scheduled = self.try_insert_job(job, i)
            cost = self.get_sched_cost(job, newsched, kicked, cur_req, dmnd, cost_func)
            if scheduled:
                idx = i
            else:
                idx = -1
            costs.append((idx, cost))
        
        return costs