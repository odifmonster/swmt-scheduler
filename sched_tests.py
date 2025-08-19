#!/usr/bin/env python

import unittest

import random, datetime as dt

from app.style import color, GreigeStyle, Color, FabricMaster, FabricStyle
from app.inventory import AllocRoll
from app.schedule import DyeLot, Job

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

    def test_lot_qty(self):
        fab = self.fabrics[0]
        rolls = [AllocRoll(f'roll_{i+1:02}', fab.greige, random.normalvariate(mu=350, sigma=10)) \
                    for i in range(6)]
        lot = DyeLot(dt.datetime(2025, 8, 18), dt.datetime(2025, 8, 18, hour=8),
                     rolls, fab)
        
        self.assertAlmostEqual(sum(map(lambda r: r.lbs, rolls)), lot.lbs, places=4)
        self.assertAlmostEqual(sum(map(lambda r: r.lbs*fab.yld, rolls)), lot.yds, places=4)

    def test_dl_view(self):
        fab = self.fabrics[0]
        rolls = [AllocRoll(f'roll_{i+1:02}', fab.greige, random.normalvariate(mu=350, sigma=10)) \
                    for i in range(6)]
        lot = DyeLot(dt.datetime(2025, 8, 18), dt.datetime(2025, 8, 18, hour=8),
                     rolls, fab)
        
        lot_view = lot.view()

        lot.start = dt.datetime(2025, 8, 17)
        lot.end = dt.datetime(2025, 8, 17, hour=8)

        self.assertEqual(lot_view.start, dt.datetime(2025, 8, 17))
        self.assertEqual(lot_view.end, dt.datetime(2025, 8, 17, hour=8))

        with self.assertRaises(AttributeError) as cm:
            lot_view.end = dt.datetime(2025, 8, 18)

        self.assertEqual(str(cm.exception), '\'end\' is a viewed attribute on another object.')

class TestJob(unittest.TestCase):

    def setUp(self):
        self.greiges = make_greige_styles(10)
        self.colors = make_colors(15)
        self.masters = make_masters(15)
        self.fabrics = make_fabric_styles(100, self.greiges, self.masters, self.colors)

    def test_init_times(self):
        fab = self.fabrics[0]
        if fab.color.shade == color.BLACK:
            cycle_time = dt.timedelta(hours=10)
        elif fab.color.shade == color.SOLUTION:
            cycle_time = dt.timedelta(hours=6)
        else:
            cycle_time = dt.timedelta(hours=8)

        lots: list[DyeLot] = []
        for i in range(3):
            roll = AllocRoll(f'roll_{i+1:02}', fab.greige, 350)
            lot = DyeLot(dt.datetime.fromtimestamp(0), dt.datetime.fromtimestamp(10), [roll],
                         fab)
            lots.append(lot)
        
        start1 = dt.datetime(2025, 8, 18)
        start2 = dt.datetime(2025, 8, 19)
        job = Job.make_job(start1, lots=tuple(lots))

        for lot in lots:
            self.assertEqual(lot.start, start1)
            self.assertEqual(lot.end, start1+cycle_time)

        job.start = start2

        for lot in lots:
            self.assertEqual(lot.start, start2)
            self.assertEqual(lot.end, start2+cycle_time)

# class TestReq(unittest.TestCase):
#     pass

if __name__ == '__main__':
    unittest.main()