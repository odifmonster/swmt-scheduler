#!/usr/bin/env python

import unittest

import datetime as dt, random

from app.style import GreigeStyle, Color, FabricStyle
from app.inventory import AllocRoll
from app.schedule import Job, DyeLot, Req
from app.schedule.jet import JetSched, Jet

def dt_is_close(date: dt.datetime, tgt: dt.datetime):
    return abs(tgt - date) <= dt.timedelta(minutes=2)

def random_str_id() -> str:
    digits = [str(i) for i in range(10)]
    return ''.join([random.choice(digits) for _ in range(8)])

def random_job(start: dt.datetime, fabric: FabricStyle) -> Job:
    req = Req(fabric, dt.datetime.now(), (0,0,0,0))
    roll = AllocRoll(random_str_id(), fabric.greige, 350)
    lot = DyeLot([roll], fabric, req.view(), 1)
    return Job.make_job(start, (lot,))

def make_colors(n: int) -> list[Color]:
    clrs: list[Color] = []
    shades = ['SOLUTION', 'LIGHT', 'MEDIUM', 'BLACK']

    for i in range(n):
        clr = Color(f'COLOR_{i+1:02}', 101+i, random.choice(shades))
        clrs.append(clr)
    
    return clrs

def make_masters(n: int) -> list[str]:
    return [f'MASTER_{i+1:02}' for i in range(n)]

def make_fabrics(n: int, greige: GreigeStyle, masters: list[str],
                 colors: list[Color]) -> list[FabricStyle]:
    fabs: list[FabricStyle] = []

    for i in range(n):
        fab = FabricStyle(f'FABRIC_{i+1:03}', greige, random.choice(masters),
                          random.choice(colors), 2.2 + 0.6*random.random(), ['Jet'])
        fabs.append(fab)
    
    return fabs

class TestJetSched(unittest.TestCase):

    def setUp(self):
        self.greige1 = GreigeStyle('GREIGE1', 330, 370)
        self.clr1 = Color('MD GREY', 100, 'MEDIUM')
        self.fabric1 = FabricStyle('FABRIC1', self.greige1, 'MASTER1', self.clr1,
                                   2.5, ['Jet'])
        
        self.colors = make_colors(10)
        self.masters = make_masters(10)
        self.fabrics = make_fabrics(100, self.greige1, self.masters, self.colors)

    def test_time_calcs(self):
        sched = JetSched(dt.datetime(2025, 8, 22, hour=17), dt.datetime(2025, 9, 1), 0)

        self.assertEqual(sched.last_job_end, dt.datetime(2025, 8, 22, hour=17))

        test_req = Req(self.fabric1, dt.datetime.now(), (0,0,0,0))
        test_roll = AllocRoll('ROLL', self.greige1, 350)
        test_lot = DyeLot([test_roll], self.fabric1, test_req.view(), 1)
        job = Job.make_job(sched.last_job_end, (test_lot,))

        sched.add_job(job)
        self.assertTrue(dt_is_close(sched.last_job_end, dt.datetime(2025, 8, 25)))
    
    def test_sched_strips(self):
        sched = JetSched(dt.datetime(2025, 8, 18), dt.datetime(2025, 8, 22, hour=23, minute=59,
                                                               second=59), 0)
        
        for i in range(6):
            job = random_job(sched.last_job_end, random.choice(self.fabrics))
            sched.add_job(job)
            self.assertEqual(sched.jobs_since_strip, i+1)
        
        sched.add_job(Job.make_strip(False, sched.last_job_end))
        self.assertEqual(sched.jobs_since_strip, 0)

        for i in range(3):
            job = random_job(sched.last_job_end, random.choice(self.fabrics))
            sched.add_job(job)
            self.assertEqual(sched.jobs_since_strip, i+1)

class TestJet(unittest.TestCase):

    def setUp(self):
        self.greige = GreigeStyle('GREIGE', 330, 370)
        self.sol_fab = FabricStyle('FABRIC1', self.greige, 'MASTER1',
                                   Color('SOLUTION COLOR', 100, 'SOLUTION'),
                                   2.5, ['Jet'])
        self.lt_fab = FabricStyle('FABRIC2', self.greige, 'MASTER2',
                                  Color('LIGHT COLOR', 200, 'LIGHT'),
                                  2.5, ['Jet'])
        self.md_fab = FabricStyle('FABRIC3', self.greige, 'MASTER3',
                                  Color('MEDIUM COLOR', 300, 'MEDIUM'),
                                  2.5, ['Jet'])
        self.blk_fab = FabricStyle('FABRIC4', self.greige, 'MASTER4',
                                   Color('BLACK COLOR', 400, 'BLACK'),
                                   2.5, ['Jet'])

    def test_basic_start(self):
        jet = 0

    def test_sequenced_start(self):
        pass

    def test_dated_start(self):
        pass

    def test_combined_start(self):
        pass

if __name__ == '__main__':
    unittest.main()