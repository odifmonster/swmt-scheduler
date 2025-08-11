#!/usr/bin/env python

import datetime as dt

from app.support import DateRange, SuperView

from app.schedule.jet import Jet

class ShadowedJet(Jet, SuperView[Jet],
                  no_access=['add_job'],
                  overrides=['last_job_end','rem_time'],
                  dunders=['eq','hash'],
                  view_only=['_ShadowedJet__sublink','_ShadowedJet__wknd',
                             '_ShadowedJet__end','_ShadowedJet__shadow_jobs',
                             'set_shadows']):
    
    def __init__(self, link: Jet, start_date: dt.datetime):
        SuperView.__init__(self, link)
        self.__sublink = link
        self.__wknd = DateRange(start_date+dt.timedelta(days=3),
                                start_date+dt.timedelta(days=5))
        self.__end = start_date + dt.timedelta(days=10)
        self.__shadow_jobs = 0
    
    @property
    def last_job_end(self):
        sublnk = self.__sublink
        lje = sublnk.last_job_end + (self.avg_cycle*self.__shadow_jobs)
        if self.__wknd.contains(lje):
            lje = self.__wknd.maxval
        elif sublnk.last_job_end <= self.__wknd.minval and lje >= self.__wknd.maxval:
            lje = lje + dt.timedelta(days=2)
        return lje
    
    @property
    def rem_time(self):
        lje = self.last_job_end
        rem = self.__end - lje
        if lje <= self.__wknd.minval:
            rem = rem - dt.timedelta(days=2)
        return rem
    
    def set_shadows(self, n: int):
        self.__shadow_jobs = n