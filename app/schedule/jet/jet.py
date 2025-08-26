#!/usr/bin/env python

from app.support import HasID, SuperImmut, FloatRange, DateRange
from ..dyelot import DyeLot
from .jetsched import JetSched
from .job import Job

class Jet(HasID[str], SuperImmut,
          attrs=('_prefix','id','n_ports','load_rng','date_rng','jobs'),
          priv_attrs=('id','init_sched','cur_sched'),
          frozen=('*id','*init_sched','n_ports','load_rng','date_rng')):
    
    def __init__(self, id, n_ports, min_load, max_load, start, end):
        date_rng = DateRange(start, end)
        SuperImmut.__init__(self, priv={'id': id, 'init_sched': JetSched(date_rng),
                                        'cur_sched': None},
                            n_ports=n_ports, load_rng=FloatRange(min_load, max_load),
                            date_rng=date_rng)
    
    @property
    def _prefix(self):
        return 'Jet'
    
    @property
    def id(self):
        return self.__id
    
    @property
    def jobs(self) -> tuple[Job]:
        if self.__cur_sched is None:
            return self.__init_sched.jobs
        return self.__init_sched.jobs + self.__cur_sched.jobs
    
    def add_adaptive_job(self, job):
        self.__init_sched.add_job(job)

    def init_new_sched(self):
        self.__cur_sched = JetSched(DateRange(max(self.date_rng.minval,
                                                  self.__init_sched.last_job_end),
                                              self.date_rng.maxval))
    
    def get_start_idx(self, lots: tuple[DyeLot, ...]):
        # Implement same thing as original get start idx
        return 0
    
    def insert(self, lots, idx):
        if self.__cur_sched is None:
            raise RuntimeError('Cannot call \'insert\' method before initializing a new schedule')
        
        newsched = self.__cur_sched.copy()
        for job in self.__cur_sched.jobs[:idx]:
            newsched.add_job(job)
        
        if not newsched.can_add(lots):
            return None, []
    
        newjobs = []
        newjobs.append(newsched.add_lots(lots))
        for job in self.__cur_sched.jobs[idx:]:
            if newsched.can_add(tuple(job.lots)):
                newjobs.append(newsched.add_lots(tuple(job.lots)))
        
        return newsched, newjobs
    
    def set_sched(self, newsched: JetSched):
        temp = self.__cur_sched
        temp.deactivate()
        self.__cur_sched = newsched
        newsched.activate()
        return temp