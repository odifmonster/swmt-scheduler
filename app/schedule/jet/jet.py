#!/usr/bin/env python

import datetime as dt

from app.support import HasID, SuperImmut, FloatRange
from app.style import color
from ..job import Job

class Jet(HasID[str], SuperImmut, attrs=('_prefix','id','n_ports','last_job_end','rem_time',
                                         'jobs_since_strip','port_range','soil_level'),
          priv_attrs=('prefix','id','min_date','max_date','jss','soil_level','jobs'),
          frozen=('_Jet__prefix','_Jet__id','_Jet__min_date','_Jet__max_date')):

    def __init__(self, id: str, n_ports: int, port_min: float, port_max: float,
                 min_date: dt.datetime, max_date: dt.datetime):
        priv = {
            'prefix': 'Jet', 'id': id, 'min_date': min_date, 
            'max_date': max_date, 'jss': 0, 'soil_level': 0, 'jobs': []
        }
        SuperImmut.__init__(self, priv=priv, n_ports=n_ports,
                            port_range=FloatRange(port_min, port_max))
    
    @property
    def _prefix(self):
        return self.__prefix
    
    @property
    def id(self):
        return self.__id
    
    @property
    def last_job_end(self) -> dt.datetime:
        if not self.__jobs:
            return self.__min_date
        lje: dt.datetime = self.__jobs[-1].end
        if lje.weekday() > 4:
            days_til_monday = 7-lje.weekday()
            monday = lje + dt.timedelta(days=days_til_monday)
            lje = dt.datetime(monday.year, monday.month, monday.day)
        return max(lje, self.__min_date)
    
    @property
    def rem_time(self) -> dt.timedelta:
        if self.last_job_end >= self.__max_date:
            return dt.timedelta(days=0)
        return self.__max_date - self.last_job_end
    
    @property
    def jobs_since_strip(self) -> int:
        return self.__jss
    
    @property
    def soil_level(self) -> int:
        return self.__soil_level
    
    @property
    def jobs(self) -> list[Job]:
        return [j for j in self.__jobs]
    
    def add_job(self, job: Job) -> None:
        if self.__jobs and self.__jobs[-1].end > job.start + dt.timedelta(minutes=2):
            raise ValueError('Cannot add job that starts before the last job ends.')
        if job.color.shade == color.BLACK:
            self.__soil_level += 7
        elif job.color.shade in (color.MEDIUM, color.EMPTY):
            self.__soil_level += 3
        elif job.color.shade in (color.LIGHT, color.SOLUTION):
            self.__soil_level += 1
        elif job.color.shade == color.STRIP:
            self.__soil_level -= 27
            self.__soil_level = max(0, self.__soil_level)

        if job.color.shade == color.STRIP:
            self.__jss = 0
        else:
            self.__jss += 1

        self.__jobs.append(job)

    def sort_jobs(self) -> None:
        oldjobs = list(filter(lambda j: j.color.shade != color.STRIP, self.__jobs))
        strips = list(filter(lambda j: j.color.shade == color.STRIP, self.__jobs))
        strips = sorted(strips, key=lambda j: j.max_date)

        self.__jobs: list[Job] = []
        self.__soil_level = 0
        oldjobs = sorted(oldjobs, key=lambda j: (j.max_date, j.color.shade))

        for j in oldjobs:
            if strips and strips[0].start - self.last_job_end <= dt.timedelta(hours=1):
                self.add_job(strips.pop(0))
            j.start = self.last_job_end
            self.add_job(j)
        
        if strips:
            self.add_job(strips.pop())