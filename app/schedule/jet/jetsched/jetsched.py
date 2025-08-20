#!/usr/bin/env python

import datetime as dt

from app.support import SuperImmut, DateRange
from app.style.color import STRIP, HEAVYSTRIP
from ...job import Job

class JetSched(SuperImmut, attrs=('date_rng','last_job_end','rem_time'),
               priv_attrs=('jobs','jss'), frozen=('date_rng',)):
    
    def __init__(self, min_date: dt.datetime, max_date: dt.datetime):
        super().__init__(priv={'jobs': [], 'jss': 0}, date_rng=DateRange(min_date, max_date))

    @property
    def last_job_end(self) -> dt.datetime:
        if not self.__jobs:
            return self.date_rng.minval
        lje: dt.datetime = self.__jobs[-1].end
        if lje.weekday() > 4:
            days_to_mon = 7 - lje.weekday()
            monday = lje + dt.timedelta(days=days_to_mon)
            lje = dt.datetime(monday.year, monday.month, monday.day)
        return min(self.date_rng.maxval, lje)

    @property
    def rem_time(self) -> dt.timedelta:
        return self.date_rng.maxval - self.last_job_end
    
    @property
    def jobs_since_strip(self):
        return self.__jss
    
    @property
    def jobs(self) -> list[Job]:
        return self.__jobs.copy()
    
    def add_job(self, job: Job):
        if job.shade in (STRIP, HEAVYSTRIP):
            self.__jss = 0
        else:
            self.__jss += 1
        self.__jobs.append(job)