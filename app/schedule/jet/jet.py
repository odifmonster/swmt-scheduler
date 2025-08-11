#!/usr/bin/env python

import datetime

from app.support import HasID, FloatRange, DateRange
from ..job import Job

class _JetBase(HasID[str]):

    def __init__(self, id: str, weekly_turns: float, n_ports: int,
                 port_range: FloatRange, start_date: datetime.datetime):
        self.__id = id
        self.__turns = weekly_turns
        self.__n_ports = n_ports
        self.__port_rng = port_range
        self.__date_rng = DateRange(start_date, start_date + datetime.timedelta(days=10))
        self.__wknd = DateRange(start_date + datetime.timedelta(days=3),
                                start_date + datetime.timedelta(days=5))
        self.__jobs: list[Job] = []

    @property
    def _prefix(self):
        return 'JET'
    
    @property
    def id(self):
        return self.__id
    
    @property
    def n_ports(self):
        return self.__n_ports
    
    @property
    def port_range(self):
        return self.__port_rng
    
    @property
    def avg_cycle(self):
        return datetime.timedelta(days=5) / self.__turns
        
    @property
    def last_job_end(self):
        if not self.__jobs:
            return self.__date_rng.minval
        if self.__wknd.contains(self.__jobs[-1].end):
            return self.__wknd.maxval
        if self.__wknd.is_above(self.__jobs[-1].end) and \
            self.__wknd.minval - self.__jobs[-1].end <= datetime.timedelta(hours=1):
            return self.__wknd.maxval
        return self.__jobs[-1].end
    
    @property
    def rem_time(self):
        lje = self.last_job_end
        if self.__wknd.is_above(lje):
            next_wk = self.__date_rng.maxval - self.__wknd.maxval
            rem_cur_wk = self.__wknd.minval - lje
            return rem_cur_wk + next_wk
        return self.__date_rng.maxval - lje
    
    def _get_nearest_idx(self, job: Job, start: int, end: int) -> int:
        if not self.__jobs:
            return 0
        if end <= start:
            return start
        
        mid = start + int((end-start)/2)
        if job.end <= self.__jobs[mid].end:
            return self._get_nearest_idx(job, start, mid)
        return self._get_nearest_idx(job, mid+1, end)
    
    def __iter__(self):
        return iter(self.__jobs)
        
    def add_job(self, job: Job):
        idx = self._get_nearest_idx(job, 0, len(self.__jobs))
        self.__jobs.insert(idx, job)

    def sort_jobs(self):
        new_jobs = sorted(self.__jobs, key=lambda j: (j.before_date, j.shade))
        self.__jobs = []

        for job in new_jobs:
            job.start = self.last_job_end
            self.add_job(job)

class Jet(_JetBase):
    pass