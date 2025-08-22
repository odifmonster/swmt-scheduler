#!/usr/bin/env python

import datetime as dt

from app.support import SuperImmut, DateRange
from app.style.color import SOLUTION, LIGHT, MEDIUM, STRIP, HEAVYSTRIP, EMPTY
from ...job import Job

class JetSched(SuperImmut, attrs=('date_rng','last_job_end','rem_time','jobs_since_strip',
                                  'soil_level'),
               priv_attrs=('jobs','init_jss','jss','init_soil','soil'),
               frozen=('_JetSched__init_soil','_JetSched__init_jss','date_rng')):
    
    def __init__(self, min_date: dt.datetime, max_date: dt.datetime, soil_level: int = 0,
                 njobs: int = 0):
        super().__init__(priv={'jobs': [], 'init_jss': njobs, 'jss': njobs, 'init_soil': soil_level,
                               'soil': soil_level},
                         date_rng=DateRange(min_date, max_date))

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
    def soil_level(self):
        return self.__soil
    
    @property
    def jobs(self) -> list[Job]:
        return self.__jobs.copy()
    
    def check_for_strip(self, newjob: Job) -> tuple[Job | None, bool]:
        if newjob.shade in (STRIP, HEAVYSTRIP):
            return None, True
        
        needed_strip = newjob.lots[0].color.get_needed_strip(self.soil_level)
        if not needed_strip is None or self.jobs_since_strip >= 9:
            is_heavy = needed_strip == HEAVYSTRIP
            strip_job = Job.make_strip(is_heavy, self.last_job_end)

            if strip_job.cycle_time + newjob.cycle_time <= self.rem_time:
                return strip_job, True
            return None, False
        
        if newjob.cycle_time > self.rem_time:
            return None, False
        return None, True
    
    def add_job(self, job: Job):
        if job.shade in (STRIP, HEAVYSTRIP):
            self.__jss = 0
            if job.shade == STRIP:
                self.__soil -= 27
            else:
                self.__soil -= 63
            self.__soil = max(0, self.__soil)
        else:
            self.__jss += 1
            if job.shade in (SOLUTION, LIGHT):
                self.__soil += 1
            elif job.shade in (MEDIUM, EMPTY):
                self.__soil += 3
            else:
                self.__soil += 7
        job.start = self.last_job_end
        self.__jobs.append(job)

    def set_times(self) -> None:
        curjobs = self.jobs
        self.clear_jobs()

        for job in curjobs:
            self.add_job(job)
    
    def clear_jobs(self):
        self.__jobs = []
        self.__jss = self.__init_jss
        self.__soil = self.__init_soil