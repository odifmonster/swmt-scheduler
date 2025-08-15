#!/usr/bin/env python

from typing import Generator, Callable
import math, datetime as dt

from app.support import DateRange, SuperView

from app.schedule.jet import Jet
from app.schedule.demand import Demand

class ShadowedJet(Jet, SuperView[Jet],
                  no_access=['add_job'],
                  overrides=['last_job_end','rem_time'],
                  dunders=['eq','hash'],
                  view_only=['_ShadowedJet__sublink','_ShadowedJet__wknd',
                             '_ShadowedJet__end','_ShadowedJet__shadow_jobs',
                             'inc_shadows']):
    
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
    
    def inc_shadows(self):
        self.__shadow_jobs = self.__shadow_jobs + 1

def nearest_jet(dmnd: Demand, lbs: float, jets: list[Jet], exceed_total: bool = True) -> int:
    port_range = dmnd.item.greige.port_range
    port_avg = (port_range.minval+port_range.maxval)/2

    best_wt_diff = math.inf
    earliest_date = dt.datetime.now() + dt.timedelta(days=30)
    best_idx = 0
    for i, jet in enumerate(jets):
        if not dmnd.item.can_run_on_jet(jet.id): continue
        diff = jet.n_ports*port_avg - lbs
        jdate = jet.last_job_end
        if abs(diff) < best_wt_diff and (not exceed_total or diff > 0):
            best_wt_diff = abs(diff)
            best_idx = i
        elif abs(diff) == best_wt_diff and jdate < earliest_date:
            earliest_date = jdate
            best_idx = i
    
    return best_idx

def get_single_jets(dmnd: Demand, jets: list[Jet], ignore_due: bool = False) -> Generator[Jet]:
    port_range = dmnd.item.greige.port_range
    port_avg = (port_range.minval+port_range.maxval)/2

    start = nearest_jet(dmnd, dmnd.pounds, jets)
    from_best = jets
    if start > 0:
        from_best = jets[start:] + jets[start-1::-1]
    for jet in from_best:
        if jet.n_ports*port_avg < dmnd.pounds: continue
        if not dmnd.item.can_run_on_jet(jet.id): continue
        if jet.rem_time < jet.avg_cycle or \
            (not ignore_due and jet.last_job_end+dt.timedelta(days=1)>dmnd.due_date):
            continue
        yield jet

def get_multi_jets(start_date: dt.datetime,
                   dmnd: Demand, jets: list[Jet],
                   prev: tuple[Jet, ...] = tuple(),
                   ignore_due: bool = False) -> Generator[tuple[Jet, ...], int]:
    port_range = dmnd.item.greige.port_range
    port_avg = (port_range.minval+port_range.maxval)/2

    total_lbs = sum(map(lambda j: j.n_ports*port_avg, prev))
    if total_lbs >= dmnd.pounds:
        yield prev
        return

    should_exceed = port_avg*8 > dmnd.pounds-total_lbs
    best_idx = nearest_jet(dmnd, dmnd.pounds-total_lbs, jets, exceed_total=should_exceed)
    from_best = jets
    if best_idx > 0:
        from_best = jets[best_idx:] + jets[best_idx-1::-1]

    jet_map = { j.id: (ShadowedJet(j, start_date), j) for j in from_best }
    map(lambda j: jet_map[j.id][0].inc_shadows(), prev)
    max_ports = None

    for sjet, rjet in jet_map.values():
        if max_ports and sjet.n_ports >= max_ports:
            continue
        if not dmnd.item.can_run_on_jet(sjet.id):
            continue
        if sjet.rem_time < sjet.avg_cycle or \
            (not ignore_due and sjet.last_job_end+dt.timedelta(days=1) > dmnd.due_date):
            continue
        
        res = get_multi_jets(start_date, dmnd, jets, prev=(*prev, rjet),
                             ignore_due=ignore_due)
        while True:
            try:
                combo = res.send(max_ports)
                yield combo
            except StopIteration:
                return

def get_partial_jets(dmnd: Demand, jets: list[Jet]) -> Generator[Jet, int]:
    port_range = dmnd.item.greige.port_range
    port_avg = (port_range.minval+port_range.maxval)/2
    
    sub_jets = [jet for jet in jets if dmnd.item.can_run_on_jet(jet.id)]
    max_ports = 10
    while True:
        fltr_jets = filter(lambda j: j.n_ports < max_ports and j.rem_time >= j.avg_cycle, sub_jets)
        sort_jets = sorted(fltr_jets, key=lambda j: abs(j.n_ports*port_avg-dmnd.pounds))
        if len(sort_jets) == 0 or dmnd.pounds <= 0:
            return
        
        max_ports = yield sort_jets[0]