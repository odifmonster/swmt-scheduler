#!/usr/bin/env python

import unittest

import random, datetime as dt

from app.style import color, GreigeStyle, Color, FabricMaster, FabricStyle
from app.inventory import AllocRoll
from app.schedule import Req, DyeLot, Job, Jet

def make_greige_styles(n: int) -> list[GreigeStyle]:
    tgts = [350, 362.5, 375]
    ret: list[GreigeStyle] = []
    for i in range(n):
        tgt = random.choice(tgts)
        ret.append(GreigeStyle(f'GREIGE_{i+1:02}', tgt-20, tgt+20))
    return ret

def make_colors(n: int) -> list[Color]:
    shades = ['SOLUTION', 'LIGHT', 'MEDIUM', 'BLACK']
    ret: list[Color] = []
    for i in range(n):
        ret.append(Color(f'COLOR_{i+1:02}', i*10, random.choice(shades)))
    return ret

def make_masters(n: int) -> list[FabricMaster]:
    return [f'MASTER_{i+1:02}' for i in range(n)]

def make_fabric_styles(n: int, greiges: list[GreigeStyle], masters: list[FabricMaster],
                       colors: list[Color]) -> list[FabricStyle]:
    jets = [f'Jet-{i:02}' for i in (1,2,3,4,7,8,9,10)]
    return [FabricStyle(f'FABRIC_{i+1:02}', random.choice(greiges), random.choice(masters),
                        random.choice(colors), 2.2+0.6*random.random(), jets) for i in range(n)]

class TestDyeLot(unittest.TestCase):
    
    def setUp(self):
        self.greiges = make_greige_styles(10)
        self.colors = make_colors(15)
        self.masters = make_masters(15)
        self.fabrics = make_fabric_styles(100, self.greiges, self.masters, self.colors)
    
    def test_dyelot_qty(self):
        test_req = Req(random.choice(self.fabrics), 9000, dt.datetime(2025, 9, 1))
        test_lot = DyeLot(test_req)
        self.assertEqual(test_lot.lbs, 0)
        self.assertEqual(test_lot.yds, 0)
        test_lot.add_roll(AllocRoll('SOME_ROLL', test_req.greige, 350))
        self.assertEqual(test_lot.lbs, 350)
        self.assertAlmostEqual(test_lot.yds, 350*test_req.item.yld, places=4)

    def test_req_qty(self):
        test_req = Req(random.choice(self.fabrics), 9000, dt.datetime(2025, 9, 1))
        test_lot = DyeLot(test_req)
        test_lot.add_roll(AllocRoll('SOME_ROLL', test_req.greige, 350))
        self.assertAlmostEqual(test_req.yds, 9000-(350*test_req.item.yld), places=4)

    def test_chained_req_qty(self):
        fab = random.choice(self.fabrics)
        req3 = Req(fab, 1500, dt.datetime(2025, 9, 10))
        req2 = Req(fab, 500, dt.datetime(2025, 9, 5), subscriber=req3)
        req1 = Req(fab, 1000, dt.datetime(2025, 9, 1), subscriber=req2)

        test_lot = DyeLot(req1)

        lbs1 = int(1000/(fab.yld*62))*62
        lbs2 = int(1500/(fab.yld*57))*57 - lbs1
        lbs3 = int(3000/(fab.yld*103))*103 - (lbs1+lbs2)

        self.assertEqual(req1.yds, 1000)
        self.assertEqual(req2.yds, 500)
        self.assertEqual(req3.yds, 1500)

        test_lot.add_roll(AllocRoll('SOME_ROLL_1', fab.greige, lbs1))
        self.assertAlmostEqual(1000-lbs1*fab.yld, req1.yds, places=4)
        self.assertEqual(req2.yds, 500)
        self.assertEqual(req3.yds, 1500)

        test_lot.add_roll(AllocRoll('SOME_ROLL_2', fab.greige, lbs2))
        self.assertAlmostEqual(1000-(lbs1+lbs2)*fab.yld, req1.yds, places=4)
        self.assertAlmostEqual(1500-(lbs1+lbs2)*fab.yld, req2.yds, places=4)
        self.assertEqual(req3.yds, 1500)

        test_lot.add_roll(AllocRoll('SOME_ROLL_3', fab.greige, lbs3))
        self.assertAlmostEqual(1000-(lbs1+lbs2+lbs3)*fab.yld, req1.yds, places=4)
        self.assertAlmostEqual(1500-(lbs1+lbs2+lbs3)*fab.yld, req2.yds, places=4)
        self.assertAlmostEqual(3000-(lbs1+lbs2+lbs3)*fab.yld, req3.yds, places=4)

def dt_is_close(date: dt.datetime, tgt: dt.datetime):
    return date > tgt - dt.timedelta(minutes=1) and date < tgt + dt.timedelta(minutes=1)

class TestJob(unittest.TestCase):
    
    def test_strip_errors(self):
        with self.assertRaises(ValueError) as cm1:
            j = Job.make_strip(dt.datetime.now(), id='some_id_1')
        
        self.assertEqual(str(cm1.exception), 'Explicit strip cycle must provide an id and an end time.')

        with self.assertRaises(ValueError) as cm2:
            j = Job.make_strip(dt.datetime.now(), end_time=dt.datetime.now()+dt.timedelta(hours=6))
        
        self.assertEqual(str(cm2.exception), 'Explicit strip cycle must provide an id and an end time.')
    
    def test_make_strip(self):
        start = dt.datetime.now()
        end = start + dt.timedelta(hours=6)
        strip1 = Job.make_strip(start, id='some_strip_1', end_time=end)
        self.assertAlmostEqual(6*3600, strip1.cycle_time.seconds, places=4)
        self.assertTrue(dt_is_close(strip1.end, end))
        self.assertEqual(strip1.color.shade, color.STRIP)

        strip2 = Job.make_strip(start)
        end2 = start + dt.timedelta(hours=7)
        self.assertAlmostEqual(7*3600, strip2.cycle_time.seconds, places=4)
        self.assertTrue(dt_is_close(strip2.end, end2))
        self.assertEqual(strip2.color.shade, color.STRIP)

    def test_make_empty_job(self):
        start1 = dt.datetime.now()
        end1 = start1 + dt.timedelta(hours=7.34)
        job1 = Job.make_empty_job(start1, 'some_job_1', end1)
        self.assertAlmostEqual(7.34*3600, job1.cycle_time.seconds, places=4)
        self.assertTrue(dt_is_close(job1.end, end1))
        self.assertEqual(job1.color.shade, color.EMPTY)

    def test_make_job(self):
        start = dt.datetime.now()
        due_date = start + dt.timedelta(weeks=1)
        ends = [
            start+dt.timedelta(hours=10), start+dt.timedelta(hours=8),
            start+dt.timedelta(hours=8), start+dt.timedelta(hours=6)
        ]

        grg = make_greige_styles(1)[0]
        fab1 = FabricStyle('TEST_FABRIC_1', grg, 'TEST_MASTER',
                           Color('TEST_BLACK', 100, 'BLACK'), 2.5, ['Jet'])
        fab2 = FabricStyle('TEST_FABRIC_2', grg, 'TEST_MASTER',
                           Color('TEST_MEDIUM', 200, 'MEDIUM'), 2.5, ['Jet'])
        fab3 = FabricStyle('TEST_FABRIC_3', grg, 'TEST_MASTER',
                           Color('TEST_LIGHT', 200, 'LIGHT'), 2.5, ['Jet'])
        fab4 = FabricStyle('TEST_FABRIC_4', grg, 'TEST_MASTER',
                           Color('TEST_SOLUTION', 200, 'SOLUTION'), 2.5, ['Jet'])
        
        lot1 = DyeLot(Req(fab1, 1000, due_date))
        job1 = Job.make_job(start, due_date, lots=(lot1,))
        self.assertAlmostEqual(10*3600, job1.cycle_time.seconds, places=4)
        self.assertTrue(dt_is_close(job1.end, ends[0]))
        self.assertEqual(job1.color.shade, color.BLACK)

        lot2 = DyeLot(Req(fab2, 1000, due_date))
        job2 = Job.make_job(start, due_date, lots=(lot2,))
        self.assertAlmostEqual(8*3600, job2.cycle_time.seconds, places=4)
        self.assertTrue(dt_is_close(job2.end, ends[1]))
        self.assertEqual(job2.color.shade, color.MEDIUM)

        lot3 = DyeLot(Req(fab3, 1000, due_date))
        job3 = Job.make_job(start, due_date, lots=(lot3,))
        self.assertAlmostEqual(8*3600, job3.cycle_time.seconds, places=4)
        self.assertTrue(dt_is_close(job3.end, ends[2]))
        self.assertEqual(job3.color.shade, color.LIGHT)

        lot4 = DyeLot(Req(fab4, 1000, due_date))
        job4 = Job.make_job(start, due_date, lots=(lot4,))
        self.assertAlmostEqual(6*3600, job4.cycle_time.seconds, places=4)
        self.assertTrue(dt_is_close(job4.end, ends[3]))
        self.assertEqual(job4.color.shade, color.SOLUTION)

def make_job_with_shade(shade: str, clr_id: int, item_id: str, start: dt.datetime,
                        due_date: dt.datetime) -> Job:
    grg = make_greige_styles(1)[0]
    clr = Color(f'COLOR_{shade}', clr_id, shade)
    fab = FabricStyle(item_id, grg, 'TEST_MASTER', clr, 2.5, ['Jet'])
    lot = DyeLot(Req(fab, 1000, due_date))
    return Job.make_job(start, due_date, (lot,))

class TestJet(unittest.TestCase):

    def setUp(self):
        self.start = dt.datetime(2025, 8, 13)
        self.end = dt.datetime(2025, 8, 23)
        self.jet = Jet('Jet', 4, 300, 400, self.start, self.end)
    
    def test_lje(self):
        self.assertTrue(dt_is_close(self.jet.last_job_end, self.start))

        start1 = dt.datetime(2025, 8, 8)
        end1 = start1 + dt.timedelta(hours=8.62)
        job1 = Job.make_empty_job(start1, 'job1', end1)

        self.jet.add_job(job1)
        self.assertTrue(dt_is_close(self.jet.last_job_end, self.start))

        start2 = dt.datetime(2025, 8, 12, hour=20)
        end2 = start2 + dt.timedelta(hours=7.39)
        job2 = Job.make_empty_job(start2, 'job2', end2)

        self.jet.add_job(job2)
        self.assertTrue(dt_is_close(self.jet.last_job_end, end2))

        start3 = dt.datetime(2025, 8, 15, hour=18)
        end3 = start3 + dt.timedelta(hours=8)
        job3 = Job.make_empty_job(start3, 'job3', end3)

        self.jet.add_job(job3)
        self.assertTrue(dt_is_close(self.jet.last_job_end, dt.datetime(2025, 8, 18)))
    
    def test_jobs_since(self):
        self.assertEqual(self.jet.jobs_since_strip, 0)

        for i in range(5):
            start = self.jet.last_job_end
            end = start + dt.timedelta(hours=8)
            job = Job.make_empty_job(start, f'job{i+1}', end)
            self.jet.add_job(job)
        
        self.assertEqual(self.jet.jobs_since_strip, 5)

        self.jet.add_job(Job.make_strip(self.jet.last_job_end))
        self.assertEqual(self.jet.jobs_since_strip, 0)

        self.jet.add_job(Job.make_empty_job(self.jet.last_job_end, 'job6',
                                            self.jet.last_job_end+dt.timedelta(hours=6)))
        self.assertEqual(self.jet.jobs_since_strip, 1)

    def test_soil_level(self):
        self.assertEqual(self.jet.soil_level, 0)

        due_date1 = self.jet.last_job_end + dt.timedelta(days=2)
        due_date2 = self.jet.last_job_end + dt.timedelta(days=3)
        due_date3 = self.jet.last_job_end + dt.timedelta(days=7)

        self.jet.add_job(make_job_with_shade('BLACK', 100, 'FABRIC1', self.jet.last_job_end,
                                             due_date1))
        self.jet.add_job(make_job_with_shade('BLACK', 101, 'FABRIC2', self.jet.last_job_end,
                                             due_date1))
        self.assertEqual(self.jet.soil_level, 10)

        self.jet.add_job(make_job_with_shade('MEDIUM', 200, 'FABRIC3', self.jet.last_job_end,
                                             due_date2))
        self.jet.add_job(make_job_with_shade('LIGHT', 300, 'FABRIC4', self.jet.last_job_end,
                                             due_date2))
        self.assertEqual(self.jet.soil_level, 14)

        self.jet.add_job(Job.make_strip(self.jet.last_job_end))
        self.assertEqual(self.jet.soil_level, 0)

        for i in range(7):
            self.jet.add_job(make_job_with_shade('BLACK', 102+i, f'FABRIC{i+5}',
                                                 self.jet.last_job_end, due_date3))
        
        self.assertEqual(self.jet.soil_level, 35)
        self.jet.add_job(Job.make_strip(self.jet.last_job_end))
        self.assertEqual(self.jet.soil_level, 10)

        self.jet.sort_jobs()
        self.assertEqual(self.jet.soil_level, 10)

if __name__ == '__main__':
    unittest.main()