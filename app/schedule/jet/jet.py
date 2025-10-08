#!/usr/bin/env python

from app.support import HasID, SuperImmut, FloatRange, DateRange
from app.support.logging import Logger, HasLogger, logged_meth
from ..dyelot import DyeLot
from .jetsched import JetSched
from .job import Job
from datetime import datetime, timedelta

def insert_args(slf, lots, idx):
    min_date = max(map(lambda l: l.min_date, lots))
    return {
        'desc1': 'Attempting to insert ' + ', '.join([l.id for l in lots]) + \
            f' after {idx} job(s) on {slf.id}',
        'desc2': f'min date={min_date.strftime('%m/%d')}'
    }

def insert_ret(res):
    newsched, newjobs = res
    if newsched is None:
        return {
            'desc1': 'Could not insert lots at given position'
        }
    return {
        'desc1': f'new schedule={newsched}',
        'desc2': 'new jobs=[' + ', '.join([f'Job({job.id})' for job in newjobs]) + ']'
    }

class Jet(HasLogger, HasID[str], SuperImmut,
          attrs=('_logger','_prefix','id','logger','n_ports','load_rng','date_rng',
                 'jobs','n_new_jobs','cur_sched'),
          priv_attrs=('id','init_sched','cur_sched'),
          frozen=('*id','*init_sched','n_ports','load_rng','date_rng')):
    
    _logger = Logger()

    @classmethod
    def set_logger(cls, lgr):
        cls._logger = lgr
    
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
    def logger(self):
        return type(self)._logger
    
    @property
    def jobs(self) -> tuple[Job, ...]:
        if self.__cur_sched is None:
            return self.__init_sched.full_sched
        return self.__init_sched.full_sched + self.__cur_sched.full_sched
    
    @property
    def n_new_jobs(self) -> int:
        return len(self.__cur_sched.jobs)
    
    @property
    def cur_sched(self):
        return self.__cur_sched
    
    def add_adaptive_job(self, job):
        self.__init_sched.add_job(job, force=True)

    def init_new_sched(self):
        self.__cur_sched = JetSched(DateRange(max(self.date_rng.minval,
                                                  self.__init_sched.last_job_end),
                                              self.date_rng.maxval),
                                    prev_sched=self.__init_sched)
    
    def get_start_idx(self, lots: tuple[DyeLot, ...], due_date: datetime):
        curjobs = self.__cur_sched.jobs
        for i, job in enumerate(curjobs):
            tdelta = due_date - job.start
            moveable = all(map(lambda l: l.moveable, job.lots))
            if tdelta.days < 18 and (moveable or i == len(curjobs) - 1 or \
                curjobs[i+1].start - timedelta(hours=4) > job.end):
                return i
        return len(curjobs)
    
    @logged_meth(insert_args, insert_ret)
    def insert(self, lots, idx):
        if self.__cur_sched is None:
            raise RuntimeError('Cannot call \'insert\' method before initializing a new schedule')
        
        newsched = self.__cur_sched.copy()
        cur_reg_jobs = self.__cur_sched.jobs
        cur_jobs = self.__cur_sched.full_sched

        if idx > 0:
            last_job_before = cur_reg_jobs[idx-1]
            for job in cur_jobs:
                moveable = all(map(lambda l: l.moveable, job.lots))
                newsched.add_job(job, force=not moveable)
                if job.id == last_job_before.id:
                    break
        
        newjobs = []
        if type(lots) is list:
            for lot in lots:
                if not newsched.can_add((lot,)):
                    return None, []
                newjobs.append(newsched.add_lots((lot,), idx))
        else:
            if not newsched.can_add(lots):
                return None, []
            newjobs.append(newsched.add_lots(lots, idx))

        rem_jobs = self.__cur_sched.jobs[idx:]
        rem_moveable = list(filter(lambda j: j.lots[0].moveable, rem_jobs))
        rem_frozen = list(filter(lambda j: not j.lots[0].moveable, rem_jobs))

        m_idx = 0
        f_idx = 0
        while m_idx < len(rem_moveable) or f_idx < len(rem_frozen):
            if m_idx == len(rem_moveable):
                add_frz = True
            elif f_idx == len(rem_frozen):
                add_frz = False
            elif rem_frozen[f_idx].start < rem_moveable[m_idx].start:
                add_frz = True
            else:
                nxt_move = rem_moveable[m_idx]
                nxt_move_end = newsched.get_expected_end(tuple(nxt_move.lots))
                if nxt_move_end + timedelta(minutes=1) > rem_frozen[f_idx].start:
                    add_frz = True
                else:
                    add_frz = False
            
            if add_frz:
                curjob = rem_frozen[f_idx]
                f_idx += 1
            else:
                curjob = rem_moveable[m_idx]
                m_idx += 1

            if newsched.can_add(tuple(curjob.lots)):
                newjobs.append(newsched.add_lots(tuple(curjob.lots), -1))
            elif add_frz:
                return None, []
        
        return newsched, newjobs
    
    def set_sched(self, newsched: JetSched):
        temp = self.__cur_sched
        temp.deactivate()
        self.__cur_sched = newsched
        newsched.activate()
        return temp